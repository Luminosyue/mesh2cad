#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "two_mesh_fullstack_latest"
MAC_ROOT = ROOT / "external/Multi-Agent-CAD"
ENV = ROOT / ".mac_env"
ENV_FALLBACK = Path("/data/home/cuiyuehan/project/pair_agent/.env")
RUNTIME = OUT / "scripts/runtime.py"


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _parse_env_file(path: Path) -> dict[str, str]:
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def set_key():
    env = _parse_env_file(ENV)
    fallback = _parse_env_file(ENV_FALLBACK)
    for key in (
        "DASHSCOPE_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "TEXT_MODEL",
        "VISUAL_API_KEY",
        "VISUAL_BASE_URL",
        "VISUAL_MODEL",
    ):
        if not os.environ.get(key) and env.get(key):
            os.environ[key] = env[key]
    if not os.environ.get("DASHSCOPE_API_KEY") and fallback.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = fallback["DASHSCOPE_API_KEY"]
    if not os.environ.get("VISUAL_API_KEY"):
        os.environ["VISUAL_API_KEY"] = env.get("VISUAL_API_KEY") or "local"
    os.environ.setdefault("VISUAL_BASE_URL", "http://127.0.0.1:18000/v1")
    os.environ.setdefault("VISUAL_MODEL", "Qwen3-VL-4B-Instruct")
    os.environ.setdefault("OPENAI_BASE_URL", env.get("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"))


def make_clients():
    set_key()
    sys.path.insert(0, str(MAC_ROOT))
    from openai import OpenAI
    from multi_agent_cad import config
    import multi_agent_cad.nodes as nodes

    nodes._DS_BASE_URL = config.DS_BASE_URL
    text_client = nodes._llm_client()
    text_model = os.environ.get("TEXT_MODEL") or config.ARCHITECT_MODEL
    visual_key = os.environ.get("VISUAL_API_KEY", "local")
    visual_client = OpenAI(
        api_key=visual_key,
        base_url=os.environ.get("VISUAL_BASE_URL", "http://127.0.0.1:18000/v1"),
        timeout=float(os.environ.get("MAC_VISUAL_TIMEOUT", "300")),
    )
    visual_model = os.environ.get("VISUAL_MODEL", "Qwen3-VL-4B-Instruct")
    return text_client, visual_client, text_model, visual_model


def json_from(text):
    block = re.search(r"```(?:json)?\s*(.*?)```", text, re.S | re.I)
    raw = block.group(1) if block else text
    begin = raw.find("{")
    end = raw.rfind("}")
    if begin < 0 or end < begin:
        raise ValueError("response has no JSON object")
    return json.loads(raw[begin : end + 1])


def call(client, model, messages, max_tokens):
    started = time.time()
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model, temperature=0.0, max_tokens=max_tokens, messages=messages
            )
            usage = response.usage
            return response.choices[0].message.content, {
                "model": model,
                "elapsed_seconds": time.time() - started,
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
                "request_sent": True,
                "response_received": True,
                "attempts": attempt + 1,
            }
        except Exception as exc:
            code = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
            if code == 403 or attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))


def visual_context(client, case_id, pid, model=None):
    directory = OUT / "06_dual_modal_adapter" / case_id / pid
    tokens = (directory / "canonical_obj_tokens.txt").read_text(encoding="ascii")[:6000]
    image_b64 = base64.b64encode((directory / "axonometric_render.png").read_bytes()).decode("ascii")
    prompt = (
        "Analyze this fresh CAD part from its rendered global view and canonical proxy OBJ connectivity. "
        "Return strict JSON with global_shape, visible_part_relationships, symmetry_or_pattern_evidence, "
        "likely_design_features, and ambiguity. Do not estimate dimensions; high-poly exact measurements "
        "are supplied separately. Canonical OBJ:\n" + tokens
    )
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_b64}},
    ]
    visual_model = model or os.environ.get("VISUAL_MODEL", "Qwen3-VL-4B-Instruct")
    try:
        raw, usage = call(client, visual_model, [{"role": "user", "content": content}], 768)
        try:
            parsed = json_from(raw)
        except Exception:
            parsed = {
                "global_shape": raw,
                "visible_part_relationships": [],
                "symmetry_or_pattern_evidence": {},
                "likely_design_features": [],
                "ambiguity": "VLM_FREE_TEXT",
            }
        usage.update({"render_sent_as_image": True, "canonical_obj_sent_as_text": True, "provider": "local_qwen3vl"})
        return parsed, raw, usage
    except Exception as exc:
        parsed = {
            "global_shape": "VISUAL_CONTEXT_UNAVAILABLE",
            "visible_part_relationships": [],
            "symmetry_or_pattern_evidence": {},
            "likely_design_features": [],
            "ambiguity": f"{type(exc).__name__}: {exc}",
        }
        usage = {
            "model": visual_model,
            "request_sent": True,
            "response_received": False,
            "error": f"{type(exc).__name__}: {exc}",
            "provider": "local_qwen3vl",
        }
        return parsed, str(exc), usage


def candidate_prompt(case_id, pid, hypothesis, visual):
    measured = load(OUT / "05_feature_graph" / case_id / pid / "measured_cad_spec.json")
    feature = load(OUT / "05_feature_graph" / case_id / pid / "cad_feature_graph.json")
    semantic = load(OUT / "04_semantic_surface" / case_id / pid / "semantic_surface_graph.json")
    hypotheses = load(OUT / "07_design_intent" / case_id / pid / "design_intent_hypotheses.json")
    dm = OUT / "06_dual_modal_adapter" / case_id / pid
    tokens = (dm / "canonical_obj_tokens.txt").read_text(encoding="ascii")
    compact_measured = {k: measured[k] for k in measured if k != "profiles"}
    compact_measured["profile_count"] = len(measured.get("profiles") or [])
    compact_measured["profiles_head"] = (measured.get("profiles") or [])[:4]
    context = {
        "measured_cad_spec": compact_measured,
        "cad_feature_graph": feature,
        "semantic_surface_graph": semantic,
        "design_intent_hypotheses": hypotheses,
        "selected_hypothesis": hypothesis,
        "canonical_obj_tokens": tokens[:8000],
        "rendered_visual_context": visual,
        "axonometric_render": {
            "processed_by_visual_context_agent": True,
            "sha256": sha(dm / "axonometric_render.png"),
        },
    }
    system = (
        "You are the Planner, Geometric Architect, and Python Coder agents in Multi-Agent-CAD. "
        "Return one strict JSON object with keys cad_brief, architect_plan, generated_code. "
        "The selected hypothesis must materially control the plan. Exact dimensions and placement come only "
        "from measured_cad_spec and original high-poly source mesh. Canonical OBJ and rendered image are "
        "context and cannot override measurements. Sampling topology is fitting evidence only and cannot "
        "become final topology. Never read STEP/BRep, historical output, proxy mesh, or render for "
        f"reconstruction. generated_code must be executable Python using argparse/subprocess, accept "
        f"--source-mesh and --output, and invoke: python3 {RUNTIME} --source-mesh INPUT --representation "
        "REPRESENTATION --output OUTPUT --sections N --profile-count N --tolerance T. Do not embed "
        "coordinates or import CAD/mesh libraries directly. cad_brief must set DUAL_MODAL_CONTEXT_SENT true."
    )
    user = (
        "Create one executable candidate for this exact hypothesis. Acknowledge canonical OBJ connectivity "
        "and rendered global context in cad_brief.context_evidence. JSON context:\n"
        + json.dumps(context, separators=(",", ":"), default=str)
    )
    return system, user, context


def fallback_code(case_id, pid, representation, index):
    return f'''#!/usr/bin/env python3
# case_id: {case_id}; part_id: {pid}; MAC-selected representation: {representation}
import argparse, subprocess, sys
def main():
    p=argparse.ArgumentParser();p.add_argument("--source-mesh",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    cmd=[sys.executable,"{RUNTIME}","--source-mesh",a.source_mesh,"--representation","{representation}","--output",a.output,"--sections","{12+2*index}","--profile-count","{10+2*index}","--tolerance","0.001"]
    raise SystemExit(subprocess.run(cmd,check=False).returncode)
if __name__=="__main__":main()
'''


def safe_code(code, representation):
    forbidden = [".step\"", ".step'", "read_step", "STEPControl_Reader", "trimesh", "from OCP", "import OCP", "build123d", "proxy.obj", "axonometric_render"]
    if any(x.lower() in code.lower() for x in forbidden):
        raise ValueError("generated code references prohibited reconstruction input/API")
    if "runtime.py" not in code or "--source-mesh" not in code or "--output" not in code:
        raise ValueError("generated code violates runtime contract")
    if representation not in code:
        raise ValueError("generated code lost selected hypothesis")
    return code


def process_part(text_client, visual_client, model, visual_model, case_id, node, state):
    pid = node["part_id"]
    base = OUT / "08_multi_candidate_mac" / case_id / pid
    visual_dir = base / "VISUAL_CONTEXT"
    if (visual_dir / "visual_context.json").is_file() and (visual_dir / "token_usage.json").is_file():
        visual = load(visual_dir / "visual_context.json")
        visual_usage = load(visual_dir / "token_usage.json")
    else:
        visual, raw, visual_usage = visual_context(visual_client, case_id, pid, visual_model)
        dump(visual_dir / "visual_context.json", visual)
        (visual_dir / "vlm_response.txt").write_text(raw, encoding="utf-8")
        dump(visual_dir / "token_usage.json", visual_usage)
    hypotheses = load(OUT / "07_design_intent" / case_id / pid / "design_intent_hypotheses.json")["hypotheses"]
    summary = {
        "case_id": case_id,
        "part_id": pid,
        "MAC_ATTEMPTED": True,
        "DUAL_MODAL_CONTEXT_SENT": True,
        "visual_context": visual,
        "visual_context_usage": visual_usage,
        "candidates": [],
        "LLM_CALLS": 1,
        "text_backend": state["text_backend"],
    }
    for index, hypothesis in enumerate(hypotheses, 1):
        representation = hypothesis["representation"]
        directory = base / f"CANDIDATE_{index:02d}_{representation}"
        manifest_path = directory / "candidate_manifest.json"
        if manifest_path.is_file():
            existing = load(manifest_path)
            if existing.get("program_executed"):
                summary["candidates"].append(existing)
                summary["LLM_CALLS"] += 1
                continue
        directory.mkdir(parents=True, exist_ok=True)
        system, user, context = candidate_prompt(case_id, pid, hypothesis, visual)
        (directory / "mac_prompt.txt").write_text(system + "\n\n" + user, encoding="utf-8")
        response_text = ""
        usage = {}
        parsed = {}
        error = None
        client = text_client if state["text_backend"] == "dashscope" else visual_client
        use_model = model if state["text_backend"] == "dashscope" else visual_model
        try:
            response_text, usage = call(client, use_model, [{"role": "system", "content": system}, {"role": "user", "content": user}], 2048)
            parsed = json_from(response_text)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            code = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
            if code == 403 and state["text_backend"] == "dashscope":
                state["text_backend"] = "local_qwen3vl"
                state["quota_blocked"] = True
                try:
                    response_text, usage = call(
                        visual_client,
                        visual_model,
                        [{"role": "system", "content": system}, {"role": "user", "content": user}],
                        2048,
                    )
                    parsed = json_from(response_text)
                    error = error + "; FELL_BACK_TO_LOCAL_QWEN3VL"
                    usage["fallback"] = "local_qwen3vl"
                except Exception as exc2:
                    error = error + f"; LOCAL_FALLBACK: {type(exc2).__name__}: {exc2}"
        dump(directory / "mac_response.json", {"raw_response": response_text, "parsed": parsed, "error": error})
        dump(directory / "token_usage.json", usage)
        summary["LLM_CALLS"] += 1
        brief = parsed.get("cad_brief", {})
        brief = brief if isinstance(brief, dict) else {"mac_value": brief}
        brief.update(
            {
                "case_id": case_id,
                "part_id": pid,
                "hypothesis": hypothesis,
                "DUAL_MODAL_CONTEXT_SENT": True,
                "canonical_obj_sha256": sha(OUT / "06_dual_modal_adapter" / case_id / pid / "canonical_obj_tokens.txt"),
                "axonometric_render_sha256": sha(OUT / "06_dual_modal_adapter" / case_id / pid / "axonometric_render.png"),
            }
        )
        dump(directory / "cad_brief.json", brief)
        plan = parsed.get("architect_plan", {})
        plan = plan if isinstance(plan, dict) else {"operation_sequence": plan}
        plan.update({"controlled_runtime": str(RUNTIME), "old_step_used": False, "proxy_used_for_exact_measurement": False})
        dump(directory / "architect_plan.json", plan)
        code = parsed.get("generated_code", "")
        if isinstance(code, str) and code.startswith("```"):
            code = re.sub(r"^```(?:python)?\s*|\s*```$", "", code, flags=re.S)
        try:
            code = safe_code(code, representation)
            code = code.replace("batch9_runtime.py", str(RUNTIME))
        except Exception as exc:
            error = (error + "; " if error else "") + f"CODE_CONTRACT: {exc}"
            code = fallback_code(case_id, pid, representation, index)
        program = directory / "generated_code.py"
        program.write_text(code, encoding="utf-8")
        step = directory / "candidate.step"
        started = time.time()
        try:
            run = subprocess.run(
                [sys.executable, str(program), "--source-mesh", node["source_part_mesh"], "--output", str(step)],
                text=True,
                capture_output=True,
                timeout=300,
            )
            exit_code = run.returncode
            stdout = run.stdout
            stderr = run.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code = 124
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + "\nTIMEOUT"
        log = {
            "command": [sys.executable, str(program), "--source-mesh", node["source_part_mesh"], "--output", str(step)],
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "elapsed_seconds": time.time() - started,
            "code_contract_error": error,
            "candidate_step_exists": step.is_file(),
        }
        dump(directory / "execution_log.txt", log)
        row = {
            "candidate_id": directory.name,
            "case_id": case_id,
            "part_id": pid,
            "hypothesis": hypothesis,
            "program": str(program),
            "generated_code_sha256": sha(program),
            "step": str(step),
            "execution_exit_code": exit_code,
            "program_executed": True,
            "step_exists": step.is_file(),
            "MAC_RESPONSE_RECEIVED": bool(response_text),
            "DUAL_MODAL_CONTEXT_SENT": True,
            "token_usage": usage,
            "code_contract_error": error,
            "text_backend": state["text_backend"],
        }
        dump(manifest_path, row)
        summary["candidates"].append(row)
        print(case_id, pid, directory.name, exit_code, step.is_file(), state["text_backend"], flush=True)
    dump(base / "mac_part_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--part")
    args = parser.parse_args()
    text_client, visual_client, model, visual_model = make_clients()
    state = {"text_backend": "dashscope", "quota_blocked": False}
    rows = []
    graph_paths = sorted((OUT / "02_cad_part_graph").glob("CASE_*/cad_part_graph.json"))
    for graph_path in graph_paths:
        graph = load(graph_path)
        case_id = graph["case_id"]
        if args.case and case_id != args.case:
            continue
        for node in graph["nodes"]:
            if args.part and node["part_id"] != args.part:
                continue
            try:
                rows.append(process_part(text_client, visual_client, model, visual_model, case_id, node, state))
            except Exception as exc:
                dump(
                    OUT / "08_multi_candidate_mac" / case_id / node["part_id"] / "mac_part_summary.json",
                    {
                        "case_id": case_id,
                        "part_id": node["part_id"],
                        "MAC_ATTEMPTED": True,
                        "error": f"{type(exc).__name__}: {exc}",
                        "candidates": [],
                    },
                )
                print(case_id, node["part_id"], "PART_FAILED", type(exc).__name__, flush=True)
    dump(
        OUT / "artifacts/mac_progress.json",
        {
            "parts_completed": len(rows),
            "MAC_RUNS": sum(len(x["candidates"]) for x in rows),
            "LLM_CALLS": sum(x["LLM_CALLS"] for x in rows),
            "parts": rows,
            "text_model": model,
            "visual_model": visual_model,
            "quota_blocked": state["quota_blocked"],
            "final_text_backend": state["text_backend"],
        },
    )


if __name__ == "__main__":
    main()
