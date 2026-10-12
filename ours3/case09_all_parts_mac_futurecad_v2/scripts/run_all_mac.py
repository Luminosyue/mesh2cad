from __future__ import annotations

import ast
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "case09_all_parts_mac_futurecad_v2"
MAC_ROOT = ROOT / "external/Multi-Agent-CAD"
RUNTIME = OUT / "scripts/case09_v2_runtime.py"
PART_IDS = [f"CADPART_{i:03d}" for i in range(8)]
EXPECTED_BUILDERS = {
    "CADPART_000": "build_global_loft_part",
    "CADPART_001": "build_profile_loft_part",
    "CADPART_002": "build_profile_loft_part",
    "CADPART_003": "build_profile_loft_part",
    "CADPART_004": "build_profile_loft_part",
    "CADPART_005": "build_profile_loft_part",
    "CADPART_006": "build_patterned_blade_part",
    "CADPART_007": "build_dorsal_feature_part",
}
PART_TASKS = {
    "CADPART_000": "Compare LOFT, SWEEP, REVOLUTION, and hybrid LOFT plus local feature. Select the measured-compatible hypothesis. Prefer few longitudinal design surfaces and prohibit transverse strip construction.",
    "CADPART_001": "Use measured root-to-tip profiles, span, twist evidence, leading and trailing boundaries. Prefer one global LOFT/SWEEP representation; prohibit N-1 independent strip faces.",
    "CADPART_002": "Use measured right-wing profiles. Consider but do not force mirror symmetry; preserve measured right-side differences and source-frame transform.",
    "CADPART_003": "Choose PROFILE+EXTRUDE, LOFT, or SWEEP from measured horizontal-tail evidence. Preserve source-frame profile boundaries.",
    "CADPART_004": "Choose PROFILE+EXTRUDE, LOFT, or SWEEP from measured horizontal-tail evidence. Preserve source-frame profile boundaries.",
    "CADPART_005": "Compare profile extrusion and measured profile loft. The explicit repair evidence favors loft if extrusion fails geometry QA.",
    "CADPART_006": "Recover blade feature semantics plus a two-instance rotational pattern. Do not invent a hub when no high-confidence measured hub region exists; preserve both measured blade instances without forcing symmetry.",
    "CADPART_007": "Organize the two measured dorsal regions as profile loft features and a semantic feature group; use pattern/mirror only if supported by measurements.",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_key():
    path = Path("/data/home/cuiyuehan/project/pair_agent/.env")
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip().startswith("DASHSCOPE_API_KEY="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                os.environ["DASHSCOPE_API_KEY"] = value
            return


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("response has no JSON object")
    return json.loads(match.group(0))


def extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.S | re.I)
    code = match.group(1) if match else text
    starts = [x for x in (code.find("import "), code.find("from ")) if x >= 0]
    if not starts:
        raise ValueError("response has no Python program")
    return code[min(starts):].strip() + "\n"


def count_shape(shape, kind):
    explorer = TopExp_Explorer(shape, kind); count = 0
    while explorer.More():
        count += 1; explorer.Next()
    return count


def audit_step(path: Path):
    reader = STEPControl_Reader(); status = reader.ReadFile(str(path))
    roots = reader.TransferRoots() if status == IFSelect_RetDone else 0
    shape = reader.OneShape() if roots else None
    valid = bool(shape and not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())
    return {
        "STEP_RELOAD": status == IFSelect_RetDone and roots > 0,
        "BREP_VALID": valid,
        "TRANSFER_ROOTS": roots,
        "FACES": count_shape(shape, TopAbs_FACE) if valid else 0,
        "EDGES": count_shape(shape, TopAbs_EDGE) if valid else 0,
    }


def code_contract(code: str, expected_builder: str):
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as exc:
        errors.append(f"SYNTAX_ERROR:{exc}")
    lowered = code.lower()
    for forbidden in (".obj", ".stl", "trimesh", "old_step", "reconstructed.step", "edges()[", "faces()["):
        if forbidden in lowered:
            errors.append("FORBIDDEN_TOKEN:" + forbidden)
    if expected_builder not in code:
        errors.append("EXPECTED_SEMANTIC_BUILDER_MISSING:" + expected_builder)
    if "--spec" not in code or "--output" not in code:
        errors.append("CLI_CONTRACT_MISSING")
    if "case09_v2_runtime" not in code:
        errors.append("MEASURED_RUNTIME_IMPORT_MISSING")
    fixed_index = re.search(r"(?:edges|faces|Edges|Faces)\s*\(\s*\)\s*\[\s*\d+\s*\]", code)
    if fixed_index:
        errors.append("FIXED_TOPOLOGY_INDEX_DEPENDENCY")
    return errors


def make_client():
    sys.path.insert(0, str(MAC_ROOT))
    from multi_agent_cad import config
    import multi_agent_cad.nodes as nodes
    nodes._DS_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    return nodes._llm_client(), config


def call_llm(client, model, role, system, user, max_tokens, records, raw_responses):
    last = None
    for transport_attempt in range(1, 4):
        started = time.time()
        try:
            response = client.chat.completions.create(
                model=model, temperature=0.0, max_tokens=max_tokens,
                extra_body={"enable_thinking": False},
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            content = response.choices[0].message.content
            usage = response.usage
            record = {
                "role": role, "request_sent": True, "response_received": True,
                "transport_attempt": transport_attempt, "model": model,
                "elapsed_sec": time.time() - started,
                "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }
            records.append(record); raw_responses.append({"role": role, "content": content, "usage": record})
            return content
        except Exception as exc:
            last = exc
            records.append({"role": role, "request_sent": True, "response_received": False, "transport_attempt": transport_attempt, "error": f"{type(exc).__name__}: {exc}", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
            time.sleep(2 * transport_attempt)
    raise RuntimeError(f"provider call failed after retries: {last}")


def execute_program(program: Path, spec: Path, step: Path):
    env = dict(os.environ); env["PYTHONPATH"] = str(OUT / "scripts") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, str(program), "--spec", str(spec), "--output", str(step)],
        cwd=str(program.parent), env=env, text=True, capture_output=True, timeout=180,
    )
    return result


def run_part(part_id: str):
    client, config = make_client()
    part_spec = OUT / "01_part_specs" / part_id
    run_dir = OUT / "02_mac_runs" / part_id
    run_dir.mkdir(parents=True, exist_ok=True)
    feature = load(part_spec / "cad_feature_graph.json")
    measured = load(part_spec / "measured_cad_spec.json")
    constraints = load(part_spec / "geometry_constraints.json")
    payload = {"cad_feature_graph": feature, "measured_cad_spec": measured, "geometry_constraints": constraints}
    payload_text = json.dumps(payload, ensure_ascii=False)
    prompts = []; calls = []; responses = []

    planner_system = (
        "You are the Spec Planner agent inside Multi-Agent-CAD. Return strict JSON only. "
        "Your only geometry sources are cad_feature_graph, measured_cad_spec, and geometry_constraints. "
        "Never request or infer dimensions from raw OBJ, mesh, STL, GLB, or previous STEP. Preserve every measured value."
    )
    planner_user = (
        f"Create a CADBrief for {part_id}. Part-specific task: {PART_TASKS[part_id]}\n"
        "The brief must include part_id, semantic_label, candidate_hypotheses, selected_hypothesis, "
        "measured_invariants, feature_semantics, prohibited_inputs, acceptance_checks, and grounding_required.\nPAYLOAD:\n"
        + payload_text
    )
    prompts.append({"role": "planner", "system": planner_system, "user": planner_user})
    planner_raw = call_llm(client, config.SPEC_PLANNER_MODEL, "planner", planner_system, planner_user, 3500, calls, responses)
    cad_brief = extract_json(planner_raw); dump(run_dir / "cad_brief.json", cad_brief)

    architect_system = (
        "You are the Geometric Architect agent inside Multi-Agent-CAD. Return strict JSON only. "
        "Translate the CADBrief into an executable, measured-data-preserving plan using only the supported runtime operations. "
        "Do not use fixed transient Face/Edge indices. Do not invent dimensions."
    )
    architect_user = (
        f"Design the ArchitectPlan for {part_id}. Required runtime builder: {EXPECTED_BUILDERS[part_id]}. "
        "Compare the part-specific hypotheses, explain rejection of unsupported ones, define operation_sequence, "
        "runtime_builder, validation_steps, feature_semantics, placement_policy=SOURCE_MEASURED_TRANSFORM, "
        "and grounding_required.\nCAD_BRIEF:\n" + json.dumps(cad_brief, ensure_ascii=False)
        + "\nMEASURED_PAYLOAD:\n" + payload_text
    )
    prompts.append({"role": "architect", "system": architect_system, "user": architect_user})
    architect_raw = call_llm(client, config.ARCHITECT_MODEL, "architect", architect_system, architect_user, 3500, calls, responses)
    architect = extract_json(architect_raw); dump(run_dir / "architect_plan.json", architect)

    candidate_results = []
    for index in range(3):
        candidate = run_dir / f"candidate_{index:02d}"; candidate.mkdir(parents=True, exist_ok=True)
        expected = EXPECTED_BUILDERS[part_id]
        coder_system = (
            "You are the Python Coder agent inside Multi-Agent-CAD. Return only one complete Python code block. "
            "The code must use argparse --spec/--output, import load_measured_spec, validate_shape, export_step, "
            "write_program_provenance and the required semantic builder from case09_v2_runtime, load measured JSON at runtime, "
            "call the semantic builder explicitly, validate, export STEP, and write provenance. Never embed coordinates, "
            "read raw meshes/old STEP, or select topology by numeric Face/Edge index."
        )
        coder_user = (
            f"Generate program candidate {index} for {part_id}. Required builder: {expected}. "
            f"Set CANDIDATE_ID='candidate_{index:02d}' and FINAL_OPS to the plan's feature operations. "
            "Candidate variations may change validation/code organization but must preserve the exact plan and measurements.\n"
            "ARCHITECT_PLAN:\n" + json.dumps(architect, ensure_ascii=False)
        )
        prompts.append({"role": f"coder_candidate_{index}", "system": coder_system, "user": coder_user})
        raw = call_llm(client, config.CODER_MODEL, f"coder_candidate_{index}", coder_system, coder_user, 3000, calls, responses)
        code = extract_code(raw); program = candidate / "generated_code.py"; program.write_text(code, encoding="utf-8")
        step = candidate / "candidate.step"; repair_rounds = 0; logs = []
        while True:
            contract_errors = code_contract(code, expected)
            if contract_errors:
                result_code = 2; stdout = ""; stderr = "\n".join(contract_errors)
            else:
                result = execute_program(program, part_spec / "measured_cad_spec.json", step)
                result_code, stdout, stderr = result.returncode, result.stdout, result.stderr
            logs.append({"round": repair_rounds, "exit_code": result_code, "stdout": stdout, "stderr": stderr})
            if result_code == 0 and step.is_file() and step.stat().st_size > 0:
                break
            if repair_rounds >= 3:
                break
            repair_rounds += 1
            repair_system = coder_system + " Repair the prior program using the concrete execution/contract error."
            repair_user = (
                f"Repair candidate {index}, round {repair_rounds}. Keep required builder {expected}.\n"
                "ERROR:\n" + stderr[-8000:] + "\nCURRENT_PROGRAM:\n" + code
            )
            prompts.append({"role": f"coder_candidate_{index}_repair_{repair_rounds}", "system": repair_system, "user": repair_user})
            raw = call_llm(client, config.CODER_MODEL, f"coder_candidate_{index}_repair_{repair_rounds}", repair_system, repair_user, 3000, calls, responses)
            code = extract_code(raw); program.write_text(code, encoding="utf-8")
        audit = audit_step(step) if step.is_file() else {"STEP_RELOAD": False, "BREP_VALID": False, "TRANSFER_ROOTS": 0, "FACES": 0, "EDGES": 0}
        semantic_pass = not code_contract(code, expected)
        candidate_result = {
            "candidate": index, "program": str(program), "step": str(step),
            "repair_rounds": repair_rounds, "execution_success": result_code == 0,
            "semantic_program_pass": semantic_pass, **audit,
            "program_operation_count": code.count("build_") + code.count("export_step("),
            "code_bytes": len(code.encode("utf-8")),
        }
        candidate_results.append(candidate_result)
        dump(candidate / "candidate_qa.json", candidate_result)
        (candidate / "execution_log.txt").write_text(json.dumps(logs, indent=2) + "\n", encoding="utf-8")
        if not (candidate_result["execution_success"] and candidate_result["BREP_VALID"] and semantic_pass):
            dump(candidate / "repair_feedback.json", {"candidate": index, "rounds": repair_rounds, "errors": logs[-1] if logs else None})

    accepted = [row for row in candidate_results if row["execution_success"] and row["BREP_VALID"] and row["semantic_program_pass"]]
    selected = min(accepted, key=lambda row: (row["FACES"], row["EDGES"], row["code_bytes"])) if accepted else None
    if selected:
        selected_dir = run_dir / f"candidate_{selected['candidate']:02d}"
        shutil.copy2(selected_dir / "generated_code.py", run_dir / "generated_code.py")
        shutil.copy2(selected_dir / "candidate.step", run_dir / "selected.step")
    (run_dir / "mac_prompt.txt").write_text("\n\n".join(f"=== {x['role']} SYSTEM ===\n{x['system']}\n=== USER ===\n{x['user']}" for x in prompts), encoding="utf-8")
    dump(run_dir / "mac_response.json", responses)
    dump(run_dir / "token_usage.json", {
        "LLM_CALLS": len([x for x in calls if x.get("response_received")]),
        "TOTAL_REQUEST_ATTEMPTS": len(calls),
        "TOTAL_INPUT_TOKENS": sum(x.get("prompt_tokens", 0) for x in calls),
        "TOTAL_OUTPUT_TOKENS": sum(x.get("completion_tokens", 0) for x in calls),
        "TOTAL_TOKENS": sum(x.get("total_tokens", 0) for x in calls),
        "calls": calls,
    })
    (run_dir / "execution_log.txt").write_text(json.dumps(candidate_results, indent=2) + "\n", encoding="utf-8")
    summary = {
        "part_id": part_id, "label": measured["semantic_label"], "MAC_USED": True,
        "MAC_RUNS": 1, "LLM_CALLS": len([x for x in calls if x.get("response_received")]),
        "MAC_CANDIDATES": 3, "MAX_MAC_REPAIR_ROUNDS": 3,
        "selected_candidate": selected["candidate"] if selected else None,
        "MAC_RESULT": "SUCCESS" if selected else "MAC_PROGRAM_FAILURE",
        "DEBUG_FALLBACK_RESULT": "NOT_RUN", "candidates": candidate_results,
    }
    dump(run_dir / "mac_run_summary.json", summary)
    return summary


def main():
    load_key()
    if not os.environ.get("DASHSCOPE_API_KEY"):
        raise RuntimeError("DASHSCOPE_API_KEY unavailable")
    if not RUNTIME.is_file():
        raise RuntimeError(f"runtime missing: {RUNTIME}")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        future_map = {pool.submit(run_part, part_id): part_id for part_id in PART_IDS}
        for future in concurrent.futures.as_completed(future_map):
            part_id = future_map[future]
            try:
                row = future.result(); results.append(row)
                print("MAC_PART_DONE", part_id, row["MAC_RESULT"], "LLM_CALLS", row["LLM_CALLS"], flush=True)
            except Exception as exc:
                row = {"part_id": part_id, "MAC_USED": True, "MAC_RUNS": 1, "LLM_CALLS": 0, "MAC_RESULT": "MAC_PROGRAM_FAILURE", "error": f"{type(exc).__name__}: {exc}"}
                dump(OUT / "02_mac_runs" / part_id / "mac_run_summary.json", row); results.append(row)
                print("MAC_PART_FAILED", part_id, row["error"], flush=True)
    results.sort(key=lambda row: row["part_id"])
    aggregate = {
        "MAC_API_AVAILABLE": True, "API_PROVIDER": "DASHSCOPE_CN_OPENAI_COMPATIBLE",
        "MODEL": "qwen3.7-max", "MAC_PARTS_ATTEMPTED": len(results),
        "MAC_PARTS_SUCCESS": sum(row.get("MAC_RESULT") == "SUCCESS" for row in results),
        "MAC_PART_RATIO": sum(row.get("MAC_RESULT") == "SUCCESS" for row in results) / 8,
        "ALL_PARTS_MAC": all(row.get("LLM_CALLS", 0) > 0 for row in results),
        "MAC_RUNS": sum(row.get("MAC_RUNS", 0) for row in results),
        "LLM_CALLS": sum(row.get("LLM_CALLS", 0) for row in results),
        "TOTAL_INPUT_TOKENS": sum(load(OUT / "02_mac_runs" / row["part_id"] / "token_usage.json").get("TOTAL_INPUT_TOKENS", 0) for row in results if (OUT / "02_mac_runs" / row["part_id"] / "token_usage.json").is_file()),
        "TOTAL_OUTPUT_TOKENS": sum(load(OUT / "02_mac_runs" / row["part_id"] / "token_usage.json").get("TOTAL_OUTPUT_TOKENS", 0) for row in results if (OUT / "02_mac_runs" / row["part_id"] / "token_usage.json").is_file()),
        "parts": results,
    }
    dump(OUT / "metrics/mac_aggregate.json", aggregate)
    print(json.dumps(aggregate, indent=2), flush=True)
    return 0 if aggregate["MAC_PARTS_SUCCESS"] == 8 and aggregate["ALL_PARTS_MAC"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
