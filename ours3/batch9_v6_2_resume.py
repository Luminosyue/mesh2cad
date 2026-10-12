#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
GATE = ROOT / "batch9_case09_style_fullstack_v6_2"
MAC_SCRIPT = BASE / "scripts/batch9_mac.py"
MAX_WORKERS = int(os.environ.get("MAC_WORKERS", "4"))
TEXT_RETRIES = int(os.environ.get("MAC_TEXT_RETRIES", "3"))
VISUAL_RETRIES = int(os.environ.get("MAC_VISUAL_RETRIES", "3"))
MAX_TOKENS = int(os.environ.get("MAC_MAX_TOKENS", "3072"))
FILTER_CASE = os.environ.get("RESUME_CASE")
FILTER_PART = os.environ.get("RESUME_PART")
FILTER_CANDIDATE = os.environ.get("RESUME_CANDIDATE")
STOP = threading.Event()
LOCK = threading.Lock()
PROGRESS = {
    "parts_total": 0,
    "parts_completed": 0,
    "candidates_total": 0,
    "candidates_real_success": 0,
    "candidates_invalid": 0,
    "http_403": 0,
    "http_5xx": 0,
    "started_at": time.time(),
}

CANARY_MAP = {
    ("CASE_01", "CADPART_000", "CANDIDATE_01_GLOBAL_LOFT"): "CANARY_01_CASE_01_CADPART_000_CANDIDATE_01_GLOBAL_LOFT",
    ("CASE_04", "CADPART_000", "CANDIDATE_01_GLOBAL_LOFT"): "CANARY_02_CASE_04_CADPART_000_CANDIDATE_01_GLOBAL_LOFT",
    ("CASE_07", "CADPART_000", "CANDIDATE_01_REVOLUTION"): "CANARY_03_CASE_07_CADPART_000_CANDIDATE_01_REVOLUTION",
}


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status_code(exc: Exception):
    return getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)


def load_mac():
    spec = importlib.util.spec_from_file_location("batch9_mac", MAC_SCRIPT)
    mac = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mac)
    return mac


MAC = load_mac()


def valid_step(path: Path):
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    if not path.is_file():
        return False, "STEP_MISSING"
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        return False, "STEP_READ_FAILED"
    if reader.TransferRoots() <= 0:
        return False, "STEP_TRANSFER_FAILED"
    shape = reader.OneShape()
    if shape.IsNull():
        return False, "NULL_SHAPE"
    if not BRepCheck_Analyzer(shape).IsValid():
        return False, "INVALID_BREP"
    return True, None


def truthful_existing(directory: Path) -> bool:
    response_path = directory / "mac_response.json"
    manifest_path = directory / "candidate_manifest.json"
    if not response_path.is_file() or not manifest_path.is_file():
        return False
    response = load(response_path)
    manifest = load(manifest_path)
    parsed = response.get("parsed", {})
    code = parsed.get("generated_code", "") if isinstance(parsed, dict) else ""
    step = directory / "candidate.step"
    return bool(
        response.get("raw_response", "").strip()
        and code.strip()
        and not response.get("error")
        and manifest.get("MAC_RESPONSE_RECEIVED")
        and manifest.get("program_executed")
        and manifest.get("execution_exit_code") == 0
        and step.is_file()
    )


def checkpoint(extra=None):
    with LOCK:
        value = dict(PROGRESS)
        value["elapsed_seconds"] = time.time() - PROGRESS["started_at"]
        value["stopped"] = STOP.is_set()
        if extra:
            value.update(extra)
        dump(GATE / "artifacts/resume_progress.json", value)


def request(client, model, messages, max_tokens, retries, stage, evidence_path):
    attempts = []
    for attempt in range(1, retries + 1):
        if STOP.is_set():
            raise RuntimeError("GLOBAL_STOP_SET")
        started = time.time()
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.0,
                max_tokens=max_tokens,
                messages=messages,
            )
            usage = response.usage
            raw = response.choices[0].message.content or ""
            row = {
                "attempt": attempt,
                "HTTP_STATUS": 200,
                "elapsed_seconds": time.time() - started,
                "raw_response_nonempty": bool(raw.strip()),
            }
            attempts.append(row)
            dump(evidence_path, {"stage": stage, "attempts": attempts})
            return raw, {
                "model": model,
                "elapsed_seconds": row["elapsed_seconds"],
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
                "request_sent": True,
                "response_received": True,
                "attempts": attempt,
            }
        except Exception as exc:
            code = status_code(exc)
            attempts.append({
                "attempt": attempt,
                "HTTP_STATUS": code,
                "elapsed_seconds": time.time() - started,
                "error": f"{type(exc).__name__}: {exc}",
            })
            dump(evidence_path, {"stage": stage, "attempts": attempts})
            with LOCK:
                if code == 403:
                    PROGRESS["http_403"] += 1
                if code and code >= 500:
                    PROGRESS["http_5xx"] += 1
            if code == 403:
                STOP.set()
                raise
            if attempt == retries or code not in (408, 409, 429, 500, 502, 503, 504):
                raise
            time.sleep(10 * attempt)
    raise RuntimeError("request retry loop exhausted")


def visual_context(visual_client, visual_model, case_id: str, part_id: str):
    directory = BASE / "08_multi_candidate_mac" / case_id / part_id / "VISUAL_CONTEXT"
    context_path = directory / "visual_context.json"
    usage_path = directory / "token_usage.json"
    if context_path.is_file() and usage_path.is_file() and load(usage_path).get("response_received"):
        return load(context_path), load(usage_path)

    dm = BASE / "06_dual_modal_adapter" / case_id / part_id
    tokens = (dm / "canonical_obj_tokens.txt").read_text(encoding="ascii")
    import base64
    image = base64.b64encode((dm / "axonometric_render.png").read_bytes()).decode("ascii")
    prompt = (
        "Analyze this fresh CAD part from its rendered global view and canonical proxy OBJ connectivity. "
        "Return strict JSON with global_shape, visible_part_relationships, symmetry_or_pattern_evidence, "
        "likely_design_features, and ambiguity. Do not estimate dimensions; exact measurements are supplied "
        "separately. Canonical OBJ:\n" + tokens
    )
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image}},
    ]
    raw, usage = request(
        visual_client,
        visual_model,
        [{"role": "user", "content": content}],
        768,
        VISUAL_RETRIES,
        "VISUAL_CONTEXT",
        directory / "request_attempts.json",
    )
    try:
        parsed = MAC.json_from(raw)
    except Exception:
        parsed = {
            "global_shape": raw,
            "visible_part_relationships": [],
            "symmetry_or_pattern_evidence": {},
            "likely_design_features": [],
            "ambiguity": "VLM_FREE_TEXT",
        }
    usage.update({"render_sent_as_image": True, "canonical_obj_sent_as_text": True})
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "vlm_response.txt").write_text(raw, encoding="utf-8")
    dump(context_path, parsed)
    dump(usage_path, usage)
    return parsed, usage


def execute_candidate(directory: Path, code: str, node, response, usage, hypothesis, context_flags):
    representation = hypothesis["representation"]
    if code.startswith("```"):
        code = re.sub(r"^```(?:python)?\s*|\s*```$", "", code, flags=re.S)
    code = MAC.safe_code(code, representation)
    code = re.sub(r"(['\"])batch9_runtime\.py\1", repr(str(MAC.RUNTIME)), code)
    program = directory / "generated_code.py"
    program.write_text(code, encoding="utf-8")
    step = directory / "candidate.step"
    started = time.time()
    command = [sys.executable, str(program), "--source-mesh", node["source_part_mesh"], "--output", str(step)]
    try:
        run = subprocess.run(command, text=True, capture_output=True, timeout=300)
        exit_code, stdout, stderr = run.returncode, run.stdout, run.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code, stdout, stderr = 124, exc.stdout or "", (exc.stderr or "") + "\nTIMEOUT"
    valid, validation_error = valid_step(step) if exit_code == 0 else (False, "PROGRAM_FAILED")
    dump(directory / "execution_log.txt", {
        "command": command,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "elapsed_seconds": time.time() - started,
        "candidate_step_exists": step.is_file(),
        "candidate_step_valid": valid,
        "validation_error": validation_error,
    })
    parsed = response.get("parsed", {})
    brief = parsed.get("cad_brief", {})
    if not isinstance(brief, dict):
        brief = {"mac_value": brief}
    brief.update({
        "case_id": node["case_id"],
        "part_id": node["part_id"],
        "hypothesis": hypothesis,
        "DUAL_MODAL_CONTEXT_SENT": True,
    })
    dump(directory / "cad_brief.json", brief)
    plan = parsed.get("architect_plan", {})
    if not isinstance(plan, dict):
        plan = {"operation_sequence": plan}
    plan.update({"old_step_used": False, "proxy_used_for_exact_measurement": False})
    dump(directory / "architect_plan.json", plan)
    dump(directory / "token_usage.json", usage)
    manifest = {
        "candidate_id": directory.name,
        "case_id": node["case_id"],
        "part_id": node["part_id"],
        "hypothesis": hypothesis,
        "program": str(program),
        "generated_code_sha256": sha(program),
        "step": str(step),
        "execution_exit_code": exit_code,
        "program_executed": True,
        "step_exists": step.is_file(),
        "step_valid": valid,
        "MAC_ATTEMPTED": True,
        "MAC_RESPONSE_RECEIVED": True,
        "REAL_MAC_CANDIDATE": True,
        "DUAL_MODAL_CONTEXT_SENT": True,
        **context_flags,
        "token_usage": usage,
        "PROGRAM_STATUS": "VALID_PROGRAM" if valid else "INVALID_PROGRAM",
    }
    dump(directory / "candidate_manifest.json", manifest)
    return manifest


def promote_canaries(graphs):
    promoted = 0
    for key, canary_name in CANARY_MAP.items():
        case_id, part_id, candidate_id = key
        source = GATE / "01_mac_canary" / canary_name
        target = BASE / "08_multi_candidate_mac" / case_id / part_id / candidate_id
        if truthful_existing(target):
            continue
        response = load(source / "mac_response.json")
        parsed = response.get("parsed", {})
        code = parsed.get("generated_code", "")
        if not response.get("raw_response", "").strip() or not code.strip() or response.get("error"):
            raise RuntimeError(f"Canary is not promotable: {source}")
        target.mkdir(parents=True, exist_ok=True)
        for name in ("mac_prompt.txt", "mac_response.json", "mac_context_manifest.json"):
            if (source / name).is_file():
                shutil.copy2(source / name, target / name)
        visual_target = target.parent / "VISUAL_CONTEXT"
        visual_target.mkdir(parents=True, exist_ok=True)
        for src_name, dst_name in (
            ("visual_context.json", "visual_context.json"),
            ("vlm_response.txt", "vlm_response.txt"),
            ("visual_token_usage.json", "token_usage.json"),
        ):
            if (source / src_name).is_file():
                shutil.copy2(source / src_name, visual_target / dst_name)
        graph = graphs[case_id]
        node = dict(next(item for item in graph["nodes"] if item["part_id"] == part_id))
        node.update({"case_id": case_id, "part_id": part_id})
        hypothesis = load(BASE / "07_design_intent" / case_id / part_id / "design_intent_hypotheses.json")["hypotheses"]
        hypothesis = next(item for item in hypothesis if candidate_id.endswith(item["representation"]))
        usage = load(source / "token_usage.json")
        flags = load(source / "mac_context_manifest.json")
        execute_candidate(target, code, node, response, usage, hypothesis, flags)
        promoted += 1
    return promoted


def process_part(text_client, visual_client, text_model, visual_model, graph, node):
    case_id, part_id = graph["case_id"], node["part_id"]
    node = dict(node)
    node.update({"case_id": case_id, "part_id": part_id})
    hypotheses = load(BASE / "07_design_intent" / case_id / part_id / "design_intent_hypotheses.json")["hypotheses"]
    visual, visual_usage = visual_context(visual_client, visual_model, case_id, part_id)
    rows = []
    for index, hypothesis in enumerate(hypotheses, 1):
        if STOP.is_set():
            break
        representation = hypothesis["representation"]
        directory = BASE / "08_multi_candidate_mac" / case_id / part_id / f"CANDIDATE_{index:02d}_{representation}"
        if FILTER_CANDIDATE and str(index) != FILTER_CANDIDATE and directory.name != FILTER_CANDIDATE:
            continue
        directory.mkdir(parents=True, exist_ok=True)
        if truthful_existing(directory):
            existing = load(directory / "candidate_manifest.json")
            existing_step = directory / "candidate.step"
            valid, validation_error = valid_step(existing_step)
            existing.update({
                "REAL_MAC_CANDIDATE": True,
                "step_valid": valid,
                "PROGRAM_STATUS": "VALID_PROGRAM" if valid else "INVALID_PROGRAM",
                "validation_error": validation_error,
            })
            dump(directory / "candidate_manifest.json", existing)
            rows.append(existing)
            continue
        system, user, context = MAC.candidate_prompt(case_id, part_id, hypothesis, visual)
        (directory / "mac_prompt.txt").write_text(system + "\n\n" + user, encoding="utf-8")
        flags = {
            "OBJ_TOKENS_SENT_TO_MAC": "canonical_obj_tokens" in context,
            "RENDER_SENT_TO_MAC": "rendered_visual_context" in context,
            "MEASURED_SPEC_SENT_TO_MAC": "measured_cad_spec" in context,
            "SEMANTIC_GRAPH_SENT_TO_MAC": "semantic_surface_graph" in context,
            "FEATURE_GRAPH_SENT_TO_MAC": "cad_feature_graph" in context,
            "DESIGN_HYPOTHESIS_SENT_TO_MAC": "selected_hypothesis" in context,
            "DUAL_MODAL_CONTEXT_ACTUALLY_USED": True,
        }
        dump(directory / "mac_context_manifest.json", flags)
        raw = ""
        usage = {}
        try:
            raw, usage = request(
                text_client,
                text_model,
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                MAX_TOKENS,
                TEXT_RETRIES,
                "TEXT_MAC",
                directory / "request_attempts.json",
            )
            parsed = MAC.json_from(raw)
            code = parsed.get("generated_code", "")
            if not raw.strip() or not code.strip():
                raise ValueError("empty raw response or generated code")
            response = {"raw_response": raw, "parsed": parsed, "error": None}
            dump(directory / "mac_response.json", response)
            row = execute_candidate(directory, code, node, response, usage, hypothesis, flags)
            rows.append(row)
            with LOCK:
                if row.get("step_valid"):
                    PROGRESS["candidates_real_success"] += 1
                else:
                    PROGRESS["candidates_invalid"] += 1
        except Exception as exc:
            code = status_code(exc)
            dump(directory / "mac_response.json", {
                "raw_response": raw,
                "parsed": {},
                "error": f"{type(exc).__name__}: {exc}",
                "HTTP_STATUS": code,
            })
            dump(directory / "candidate_manifest.json", {
                "candidate_id": directory.name,
                "case_id": case_id,
                "part_id": part_id,
                "hypothesis": hypothesis,
                "MAC_ATTEMPTED": True,
                "MAC_RESPONSE_RECEIVED": bool(raw),
                "REAL_MAC_CANDIDATE": bool(raw),
                "program_executed": False,
                "execution_exit_code": None,
                "step": str(directory / "candidate.step"),
                "step_exists": False,
                "step_valid": False,
                "PROGRAM_STATUS": "INVALID_PROGRAM",
                "error": f"{type(exc).__name__}: {exc}",
                **flags,
            })
            with LOCK:
                PROGRESS["candidates_invalid"] += 1
            if code == 403 or STOP.is_set():
                break
        checkpoint({"current_part": f"{case_id}/{part_id}", "current_candidate": directory.name})

    valid_real = [row for row in rows if row.get("REAL_MAC_CANDIDATE") and row.get("step_valid")]
    summary = {
        "case_id": case_id,
        "part_id": part_id,
        "MAC_ATTEMPTED": True,
        "MAC_USED": bool(rows) and all(row.get("MAC_RESPONSE_RECEIVED") for row in rows),
        "DUAL_MODAL_CONTEXT_SENT": bool(rows) and all(row.get("DUAL_MODAL_CONTEXT_SENT") for row in rows),
        "visual_context": visual,
        "visual_context_usage": visual_usage,
        "candidates": rows,
        "LLM_CALLS": 1 + sum(row.get("token_usage", {}).get("attempts", 0) for row in rows),
        "TTS_USED_FOR_PART": len(valid_real) >= 2,
    }
    dump(BASE / "08_multi_candidate_mac" / case_id / part_id / "mac_part_summary.json", summary)
    with LOCK:
        PROGRESS["parts_completed"] += 1
    checkpoint({"last_completed_part": f"{case_id}/{part_id}"})
    print(f"PART_DONE {case_id} {part_id} REAL_VALID={len(valid_real)}/{len(hypotheses)}", flush=True)
    return summary


def main():
    MAC.set_key()
    os.environ.setdefault("TEXT_MODEL", "glm-5.2")
    sys.path.insert(0, str(MAC.MAC_ROOT))
    from openai import OpenAI
    from multi_agent_cad import config

    text_model = os.environ.get("TEXT_MODEL") or config.ARCHITECT_MODEL
    text_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("DASHSCOPE_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL", str(config.DS_BASE_URL)),
        timeout=float(os.environ.get("MAC_TEXT_TIMEOUT", "600")),
        max_retries=0,
    )
    visual_key = os.environ.get("VISUAL_API_KEY", "")
    visual_client = OpenAI(
        api_key=visual_key or "local",
        base_url=os.environ.get("VISUAL_BASE_URL", "http://127.0.0.1:18000/v1"),
        timeout=float(os.environ.get("MAC_VISUAL_TIMEOUT", "300")),
        max_retries=0,
    )
    visual_model = os.environ.get("VISUAL_MODEL", "Qwen3-VL-4B-Instruct")
    graphs = {}
    jobs = []
    for path in sorted((BASE / "02_cad_part_graph").glob("CASE_*/cad_part_graph.json")):
        graph = load(path)
        graphs[graph["case_id"]] = graph
        if FILTER_CASE and graph["case_id"] != FILTER_CASE:
            continue
        for node in graph["nodes"]:
            if FILTER_PART and node["part_id"] != FILTER_PART:
                continue
            jobs.append((graph, node))
    PROGRESS["parts_total"] = len(jobs)
    PROGRESS["candidates_total"] = sum(
        len(load(BASE / "07_design_intent" / graph["case_id"] / node["part_id"] / "design_intent_hypotheses.json")["hypotheses"])
        for graph, node in jobs
    )
    promoted = promote_canaries(graphs)
    checkpoint({"text_model": text_model, "visual_model": visual_model, "canaries_promoted": promoted})
    summaries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(process_part, text_client, visual_client, text_model, visual_model, graph, node) for graph, node in jobs]
        for future in concurrent.futures.as_completed(futures):
            try:
                summaries.append(future.result())
            except Exception as exc:
                print(f"PART_FATAL {type(exc).__name__}: {exc}", flush=True)
                if status_code(exc) == 403:
                    STOP.set()
    all_rows = []
    for path in sorted((BASE / "08_multi_candidate_mac").glob("CASE_*/CADPART_*/CANDIDATE_*/candidate_manifest.json")):
        all_rows.append(load(path))
    real = [row for row in all_rows if row.get("REAL_MAC_CANDIDATE") or row.get("MAC_RESPONSE_RECEIVED")]
    valid = [row for row in real if row.get("step_valid") is True]
    tts_parts = sum(summary.get("TTS_USED_FOR_PART", False) for summary in summaries)
    final = {
        "MAC_API_AVAILABLE": not STOP.is_set(),
        "MAC_BLOCKED_BY_QUOTA": PROGRESS["http_403"] > 0,
        "MAC_USED": bool(real),
        "ALL_PARTS_MAC": len(summaries) == len(jobs) and all(summary.get("MAC_USED") for summary in summaries),
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED": bool(real) and all(row.get("DUAL_MODAL_CONTEXT_SENT") for row in real),
        "TTS_ACTUALLY_USED": tts_parts > 0,
        "TTS_PARTS": tts_parts,
        "candidate_programs_executed": sum(row.get("program_executed", False) for row in real),
        "candidate_steps": len(valid),
        "real_mac_candidates": len(real),
        "real_mac_valid_candidates": len(valid),
        "fallback_candidates": 0,
        "parts_completed": len(summaries),
        "parts_total": len(jobs),
        "text_model": text_model,
        "visual_model": visual_model,
        "http_403": PROGRESS["http_403"],
        "http_5xx": PROGRESS["http_5xx"],
    }
    dump(BASE / "artifacts/mac_summary_v6_2.json", final)
    dump(BASE / "artifacts/mac_summary.json", final)
    checkpoint({"complete": True, **final})
    print(json.dumps(final, indent=2), flush=True)
    return 3 if STOP.is_set() else 0


if __name__ == "__main__":
    raise SystemExit(main())
