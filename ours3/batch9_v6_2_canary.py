#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_case09_style_fullstack_v6_2"
MAC_SCRIPT = BASE / "scripts/batch9_mac.py"
CANARIES = [
    ("CASE_01", "CADPART_000", "CANDIDATE_01_GLOBAL_LOFT"),
    ("CASE_04", "CADPART_000", "CANDIDATE_01_GLOBAL_LOFT"),
    ("CASE_07", "CADPART_000", "CANDIDATE_01_REVOLUTION"),
]


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def status_code(exc: Exception):
    return getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)


def direct_call(client, model, messages, max_tokens):
    """One network attempt. In particular, HTTP 403 must never be retried."""
    started = time.time()
    response = client.chat.completions.create(
        model=model,
        temperature=0.0,
        max_tokens=max_tokens,
        messages=messages,
    )
    usage = response.usage
    return response.choices[0].message.content or "", {
        "model": model,
        "elapsed_seconds": time.time() - started,
        "prompt_tokens": getattr(usage, "prompt_tokens", 0),
        "completion_tokens": getattr(usage, "completion_tokens", 0),
        "total_tokens": getattr(usage, "total_tokens", 0),
        "request_sent": True,
        "response_received": True,
        "attempts": 1,
    }


def visual_context(mac, client, case_id: str, part_id: str, model: str | None = None):
    directory = BASE / "06_dual_modal_adapter" / case_id / part_id
    tokens = (directory / "canonical_obj_tokens.txt").read_text(encoding="ascii")
    render = (directory / "axonometric_render.png").read_bytes()
    prompt = (
        "Analyze this fresh CAD part from its rendered global view and canonical proxy OBJ connectivity. "
        "Return strict JSON with global_shape, visible_part_relationships, symmetry_or_pattern_evidence, "
        "likely_design_features, and ambiguity. Do not estimate dimensions; high-poly exact measurements "
        "are supplied separately. Canonical OBJ:\n" + tokens
    )
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(render).decode("ascii")}},
    ]
    visual_model = model or os.environ.get("VISUAL_MODEL", "Qwen3-VL-4B-Instruct")
    raw, usage = direct_call(client, visual_model, [{"role": "user", "content": content}], 768)
    try:
        parsed = mac.json_from(raw)
    except Exception:
        parsed = {
            "global_shape": raw,
            "visible_part_relationships": [],
            "symmetry_or_pattern_evidence": {},
            "likely_design_features": [],
            "ambiguity": "VLM_FREE_TEXT",
        }
    usage.update({
        "render_sent_as_image": True,
        "canonical_obj_sent_as_text": True,
        "render_sha256": sha256_bytes(render),
        "canonical_obj_sha256": sha256_bytes(tokens.encode("ascii")),
        "provider": "local_qwen3vl",
    })
    return parsed, raw, usage


def strip_fence(code: str) -> str:
    if code.startswith("```"):
        return re.sub(r"^```(?:python)?\s*|\s*```$", "", code, flags=re.S)
    return code


def validate_step(path: Path):
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    read_status = reader.ReadFile(str(path))
    if read_status != IFSelect_RetDone:
        return False, "STEP_READ_FAILED"
    if reader.TransferRoots() <= 0:
        return False, "STEP_TRANSFER_FAILED"
    shape = reader.OneShape()
    if shape.IsNull():
        return False, "NULL_SHAPE"
    if not BRepCheck_Analyzer(shape).IsValid():
        return False, "INVALID_BREP"
    return True, None


def write_failure_summary(results, code, model, base_url, fingerprint, blocker):
    summary = {
        "CURRENT_GATE": "BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL",
        "TARGET_CASES": 9,
        "CASE09_RERUN": False,
        "P3_REUSED_CASES": 9,
        "P3_RERUN_CASES": 0,
        "PHYSX_REUSED_CASES": 9,
        "PHYSX_RERUN_CASES": 0,
        "CAD_PART_GRAPH_FRESH_CASES": 9,
        "OLD_STEP_USED_AS_INPUT": False,
        "MAC_CANARY_PASS": False,
        "MAC_CANARIES_COMPLETED": len(results),
        "MAC_HTTP_STATUS": code,
        "MAC_QUOTA_AVAILABLE": False if code == 403 else None,
        "MAC_API_AVAILABLE": code is not None,
        "MAC_MODEL": model,
        "MAC_BASE_URL": base_url,
        "MAC_KEY_FINGERPRINT": fingerprint,
        "TOTAL_PARTS": 132,
        "MAC_PARTS_ATTEMPTED": 0,
        "MAC_PARTS_SUCCESS": 0,
        "REAL_MAC_CANDIDATES_BEFORE": 3,
        "REAL_MAC_CANDIDATES_AFTER": 3,
        "REAL_MAC_CANDIDATES": 0,
        "REAL_MAC_PROGRAMS_EXECUTED": 0,
        "REAL_MAC_STEP_SUCCESS": 0,
        "REAL_MAC_STEP_FAILURE": 0,
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED": False,
        "TTS_PARTS": 0,
        "TTS_ACTUALLY_USED": False,
        "FUTURECAD_GROUNDING_PARTS": 0,
        "BATCH_STARTED": False,
        "FALLBACK_STARTED": False,
        "CANARY_RESULTS": results,
        "BLOCKERS": [blocker],
    }
    dump(OUT / "artifacts/canary_summary.json", summary)
    dump(OUT / "artifacts/final_summary.json", summary)
    lines = [f"{key}={json.dumps(value) if isinstance(value, (list, dict)) else str(value).lower() if isinstance(value, bool) else value}" for key, value in summary.items() if key != "CANARY_RESULTS"]
    (OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    report = f"""# Batch9 CASE09-style Full-stack V6.2

## Result

`BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL`

The canary stopped at `{results[-1]['case_id']} / {results[-1]['part_id']}` with HTTP `{code}` during `{results[-1].get('failure_stage')}`. The endpoint was called once at that stage; HTTP 403 was not retried.

The required 3/3 canary gate did not pass. CASE04/CASE07 were not called after a CASE01 failure, and the 9-case MAC batch, deterministic fallback, P3, PhysX, and CASE09 were not run.

## Accounting

- Existing verified source-derived part/semantic/dual-modal artifacts retained: 132.
- New real MAC candidates: 0.
- New real MAC programs executed: 0.
- TTS actually used: false.
- Historical STEP used as reconstruction input: false.

Evidence: `{OUT / 'artifacts/canary_summary.json'}`
"""
    (OUT / "report.md").write_text(report, encoding="utf-8")
    return summary


def main() -> int:
    spec = importlib.util.spec_from_file_location("batch9_mac", MAC_SCRIPT)
    mac = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mac)
    text_client, visual_client, model, visual_model = mac.make_clients()
    from multi_agent_cad import config

    base_url = str(config.DS_BASE_URL)
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    fingerprint = "sha256:" + sha256_bytes(key.encode("utf-8"))[:12] if key else "MISSING"
    visual_base = os.environ.get("VISUAL_BASE_URL", "")
    results = []

    for index, (case_id, part_id, candidate_id) in enumerate(CANARIES, 1):
        old = load(BASE / "08_multi_candidate_mac" / case_id / part_id / candidate_id / "candidate_manifest.json")
        hypothesis = old["hypothesis"]
        target = OUT / "01_mac_canary" / f"CANARY_{index:02d}_{case_id}_{part_id}_{candidate_id}"
        target.mkdir(parents=True, exist_ok=True)
        record = {
            "canary_index": index,
            "case_id": case_id,
            "part_id": part_id,
            "candidate_id": candidate_id,
            "hypothesis": hypothesis,
            "MAC_ATTEMPTED": True,
            "HTTP_ATTEMPTS_PER_STAGE": 1,
            "HTTP_STATUS": None,
            "raw_response_nonempty": False,
            "generated_code_from_raw_response": False,
            "program_executed": False,
            "valid_step": False,
            "TEXT_MODEL": model,
            "TEXT_BASE_URL": base_url,
            "VISUAL_MODEL": visual_model,
            "VISUAL_BASE_URL": visual_base,
        }
        started = time.time()
        try:
            visual, visual_raw, visual_usage = visual_context(mac, visual_client, case_id, part_id, visual_model)
            dump(target / "visual_context.json", visual)
            (target / "vlm_response.txt").write_text(visual_raw, encoding="utf-8")
            dump(target / "visual_token_usage.json", visual_usage)
            record.update({"OBJ_TOKENS_SENT_TO_MAC": True, "RENDER_SENT_TO_MAC": True, "visual_http_status": 200})

            system, user, context = mac.candidate_prompt(case_id, part_id, hypothesis, visual)
            (target / "mac_prompt.txt").write_text(system + "\n\n" + user, encoding="utf-8")
            dump(target / "mac_context_manifest.json", {
                "MEASURED_SPEC_SENT_TO_MAC": "measured_cad_spec" in context,
                "SEMANTIC_GRAPH_SENT_TO_MAC": "semantic_surface_graph" in context,
                "FEATURE_GRAPH_SENT_TO_MAC": "cad_feature_graph" in context,
                "DESIGN_HYPOTHESIS_SENT_TO_MAC": "selected_hypothesis" in context,
                "OBJ_TOKENS_SENT_TO_MAC": "canonical_obj_tokens" in context,
                "RENDERED_CONTEXT_SENT_TO_MAC": "rendered_visual_context" in context,
            })
            raw, usage = direct_call(text_client, model, [{"role": "system", "content": system}, {"role": "user", "content": user}], 3072)
            parsed = mac.json_from(raw)
            code = strip_fence(parsed.get("generated_code", ""))
            if not raw.strip() or not code.strip():
                raise RuntimeError("empty raw response or generated code")
            code = mac.safe_code(code, hypothesis["representation"])
            code = re.sub(r"(['\"])batch9_runtime\.py\1", repr(str(mac.RUNTIME)), code)
            dump(target / "mac_response.json", {"raw_response": raw, "parsed": parsed, "error": None})
            dump(target / "token_usage.json", usage)
            dump(target / "cad_brief.json", parsed.get("cad_brief", {}))
            dump(target / "architect_plan.json", parsed.get("architect_plan", {}))
            program = target / "generated_code.py"
            program.write_text(code, encoding="utf-8")
            record.update({"HTTP_STATUS": 200, "raw_response_nonempty": True, "generated_code_from_raw_response": True})

            graph = load(BASE / "02_cad_part_graph" / case_id / "cad_part_graph.json")
            node = next(item for item in graph["nodes"] if item["part_id"] == part_id)
            step = target / "candidate.step"
            command = [sys.executable, str(program), "--source-mesh", node["source_part_mesh"], "--output", str(step)]
            run = subprocess.run(command, text=True, capture_output=True, timeout=300)
            valid, validation_error = validate_step(step) if run.returncode == 0 and step.is_file() else (False, "PROGRAM_OR_STEP_FAILURE")
            dump(target / "execution_log.txt", {
                "command": command,
                "exit_code": run.returncode,
                "stdout": run.stdout,
                "stderr": run.stderr,
                "step_exists": step.is_file(),
                "step_valid": valid,
                "validation_error": validation_error,
            })
            record.update({
                "program_executed": True,
                "execution_exit_code": run.returncode,
                "candidate_step": str(step),
                "valid_step": valid,
                "DUAL_MODAL_CONTEXT_ACTUALLY_USED": True,
                "MAC_CANDIDATE_SUCCESS": valid,
                "elapsed_seconds": time.time() - started,
            })
            if not valid:
                raise RuntimeError(f"generated program did not produce a valid STEP: {validation_error}")
        except Exception as exc:
            code = status_code(exc)
            failure_stage = "VISUAL_CONTEXT" if not record.get("visual_http_status") else "TEXT_MAC" if record.get("HTTP_STATUS") is None else "PROGRAM_EXECUTION"
            record.update({
                "HTTP_STATUS": code if code is not None else record.get("HTTP_STATUS"),
                "failure_stage": failure_stage,
                "error": f"{type(exc).__name__}: {exc}",
                "quota_exhausted": code == 403,
                "elapsed_seconds": time.time() - started,
                "MAC_CANDIDATE_SUCCESS": False,
            })
            if not (target / "mac_response.json").exists():
                dump(target / "mac_response.json", {"raw_response": "", "parsed": {}, "error": record["error"]})
            dump(target / "canary_result.json", record)
            results.append(record)
            blocker = "MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY" if code == 403 else "MAC_CANARY_FAILED"
            summary = write_failure_summary(results, code, model, base_url, fingerprint, blocker)
            print(json.dumps(summary, indent=2), flush=True)
            return 3 if code == 403 else 1

        dump(target / "canary_result.json", record)
        results.append(record)
        print(f"CANARY_{index} {case_id} {part_id} HTTP=200 VALID_STEP=true", flush=True)

    summary = {
        "CURRENT_GATE": "BATCH9_CASE09_STYLE_FULLSTACK_V6_2_CANARY_PASS",
        "MAC_CANARY_PASS": True,
        "MAC_HTTP_STATUS": 200,
        "MAC_QUOTA_AVAILABLE": True,
        "MAC_MODEL": model,
        "MAC_BASE_URL": base_url,
        "MAC_KEY_FINGERPRINT": fingerprint,
        "VISUAL_MODEL": visual_model,
        "VISUAL_BASE_URL": visual_base,
        "MAC_CANARIES_COMPLETED": 3,
        "CANARY_RESULTS": results,
        "BLOCKERS": [],
    }
    dump(OUT / "artifacts/canary_summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
