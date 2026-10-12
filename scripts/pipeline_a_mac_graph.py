#!/usr/bin/env python3
"""Invoke original Multi-Agent-CAD graph to generate build123d CAD per component."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MAC_REPO = ROOT / "Multi-Agent-CAD"
MAC_ENV_FILE = ROOT / "ours3/.mac_env"
EXTERNAL_MAC = ROOT / "ours3/external/Multi-Agent-CAD"
MAC_PYTHON = Path(os.environ.get("MAC_PYTHON", "/data/miniconda3/envs/multi_agent_cad/bin/python"))
JOB_SCRIPT = ROOT / "scripts/run_mac_graph_job.py"

sys.path.insert(0, str(ROOT / "scripts"))
import dual_modal_qwen3vl as qwen3vl  # noqa: E402
import generic_cad_runtime as generic_runtime  # noqa: E402


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str, ensure_ascii=False) + "\n", encoding="utf-8")


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def mac_job_env() -> dict[str, str]:
    env = os.environ.copy()
    conda_lib = str((MAC_PYTHON.parent.parent / "lib").resolve())
    existing = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = conda_lib if not existing else f"{conda_lib}:{existing}"
    pythonpath = [
        str((MAC_REPO / "packages/cadpy/src").resolve()),
        str(MAC_REPO.resolve()),
        str((ROOT / "scripts").resolve()),
        env.get("PYTHONPATH", ""),
    ]
    env["PYTHONPATH"] = os.pathsep.join(item for item in pythonpath if item)
    return env


def invoke_mac_graph_job(mac_dir: Path) -> dict[str, Any]:
    if not MAC_PYTHON.is_file():
        return {"error_type": "FATAL", "execution_log": [f"MAC_PYTHON_MISSING:{MAC_PYTHON}"]}
    log_path = mac_dir / "mac_graph_job.log"
    cmd = [
        str(MAC_PYTHON),
        "-u",
        str(JOB_SCRIPT),
        "--request",
        str((mac_dir / "mac_request.json").resolve()),
        "--mac-dir",
        str(mac_dir.resolve()),
    ]
    timeout_s = int(os.environ.get("MAC_GRAPH_TIMEOUT_SECONDS", "1800"))
    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n=== MAC graph start {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_handle.flush()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(mac_dir),
                env=mac_job_env(),
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired:
            log_handle.write(f"\nMAC graph timeout after {timeout_s}s\n")
            log_handle.flush()
            return {"error_type": "FATAL", "execution_log": [f"MAC_GRAPH_TIMEOUT:{timeout_s}"]}
        log_handle.write(f"\n=== MAC graph exit {proc.returncode} ===\n")
        log_handle.flush()
    returncode = proc.returncode
    result_path = mac_dir / "mac_graph_result.json"
    if result_path.is_file():
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    else:
        payload = {}
    if returncode != 0:
        payload.setdefault("error_type", "FATAL")
        logs = list(payload.get("execution_log") or [])
        logs.append(f"MAC graph job exit {returncode}")
        payload["execution_log"] = logs
    return payload


def component_request_text(part: dict[str, Any], spec: dict[str, Any], visual_parsed: dict[str, Any] | None) -> str:
    scores = spec.get("scores") if isinstance(spec.get("scores"), dict) else {}
    bbox = spec.get("bbox")
    extents = spec.get("principal_extents") or spec.get("dimensions")
    centroid = spec.get("centroid")
    source_part = part.get("source_obj") or part.get("source_part_obj")
    visual_shape = None
    visual_family = None
    if isinstance(visual_parsed, dict):
        visual_shape = visual_parsed.get("global_shape")
        visual_family = visual_parsed.get("likely_builder_family")
    lines = [
        f"Reconstruct component {part.get('component_id')} as CAD-native B-Rep using build123d.",
        "Do not tessellate or dump the source triangle mesh. Build with sketch/extrude/revolve/loft/boolean primitives.",
        "Use the measured numbers below as-is. Do not convert meters to millimeters and do not invent sizes.",
        f"Component id: {part.get('component_id')}",
        f"P3 label: {part.get('p3_label')}",
        f"Triangle count: {part.get('triangle_count')}",
        f"Source mesh path (evidence only): {source_part}",
        f"BBox: {json.dumps(bbox)}",
        f"Centroid: {json.dumps(centroid)}",
        f"Principal extents: {json.dumps(extents)}",
        f"Planarity: {scores.get('planarity_score') or spec.get('planar_score')}",
        f"Cylindricality: {scores.get('cylindricality_score') or spec.get('cylindrical_score')}",
        f"Loft score: {scores.get('loft_score')}",
        f"Revolution score: {scores.get('revolution_score')}",
        f"Freeform score: {scores.get('freeform_score')}",
        f"Qwen3-VL global_shape: {visual_shape}",
        f"Qwen3-VL likely_builder_family: {visual_family}",
        "The generated solid/shell must occupy the same bbox/centroid as the source mesh.",
        "Return executable build123d and let the autonomous skill loop repair failures.",
    ]
    if visual_parsed:
        lines.append("Qwen3-VL visual JSON (images were sent to local Qwen3-VL-4B-Instruct):")
        lines.append(json.dumps(visual_parsed, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def generate_component_cad(part: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    mac_dir = component_dir / "06_mac"
    cache_dir = mac_dir / "pipeline_cache"
    cand_dir = component_dir / "07_candidates" / "mac_candidate_01"
    mac_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cand_dir.mkdir(parents=True, exist_ok=True)
    for key, value in load_env_file(MAC_ENV_FILE).items():
        os.environ.setdefault(key, value)
    visual_parsed = qwen3vl.visual_json_for_mac(component_dir)
    if visual_parsed is not None:
        qwen3vl.mark_visual_entered_mac(component_dir, True)
    request_text = component_request_text(part, spec, visual_parsed)
    dump_json(
        mac_dir / "mac_request.json",
        {
            "component_id": part.get("component_id"),
            "mac_repo": str(MAC_REPO),
            "user_request": request_text,
            "visual_parsed": visual_parsed,
            "visual_model": qwen3vl.visual_model() if visual_parsed is not None else None,
        },
    )
    started = time.time()
    try:
        result = invoke_mac_graph_job(mac_dir)
    except Exception as exc:
        result = {
            "error_type": "FATAL",
            "execution_log": [f"MAC graph failed: {type(exc).__name__}: {exc}"],
        }
        dump_json(mac_dir / "mac_graph_result.json", result)
    if not (mac_dir / "mac_graph_result.json").is_file():
        dump_json(mac_dir / "mac_graph_result.json", {key: result.get(key) for key in result if key != "current_python_code"})

    step_path = Path(str(result.get("current_step_path") or ""))
    if not step_path.is_file():
        local_step = mac_dir / step_path.name if step_path.name else mac_dir / "generated.step"
        if local_step.is_file():
            step_path = local_step
        else:
            found = sorted(mac_dir.glob("*.step")) + sorted(mac_dir.glob("temp_*.step"))
            step_path = found[0] if found else step_path
    stl_path = Path(str(result.get("current_stl_path") or ""))
    if not stl_path.is_file():
        local_stl = mac_dir / stl_path.name if stl_path.name else mac_dir / "generated.stl"
        if local_stl.is_file():
            stl_path = local_stl
    code_path = Path(str(result.get("current_python_code_path") or ""))
    if not code_path.is_file():
        mac_written = mac_dir / "generated_code.py"
        if mac_written.is_file():
            code_path = mac_written
        else:
            for fallback in sorted(mac_dir.glob("temp_design*.py")):
                code_path = fallback
                break
    generated_code = cand_dir / "generated_code.py"
    generated_step = cand_dir / "generated.step"
    generated_stl = cand_dir / "generated.stl"
    mac_code = mac_dir / "generated_code.py"
    mac_step = mac_dir / "generated.step"
    mac_stl = mac_dir / "generated.stl"
    if code_path.is_file():
        shutil.copy2(code_path, generated_code)
        shutil.copy2(code_path, mac_code)
    elif result.get("current_python_code"):
        generated_code.write_text(str(result["current_python_code"]), encoding="utf-8")
        shutil.copy2(generated_code, mac_code)
    if step_path.is_file():
        shutil.copy2(step_path, generated_step)
        shutil.copy2(step_path, mac_step)
    if stl_path.is_file():
        shutil.copy2(stl_path, generated_stl)
        shutil.copy2(stl_path, mac_stl)
    if result.get("cad_brief") is not None:
        dump_json(cand_dir / "cad_brief.json", result.get("cad_brief"))
        dump_json(mac_dir / "cad_brief.json", result.get("cad_brief"))
    if result.get("architect_plan") is not None:
        dump_json(cand_dir / "architect_plan.json", result.get("architect_plan"))
        dump_json(mac_dir / "architect_plan.json", result.get("architect_plan"))

    aligned_step = cand_dir / "generated_aligned.step"
    alignment = None
    if generated_step.is_file() and part.get("mesh") is not None:
        try:
            import tank_p3_point2cad_component_local_qa_v2 as local_qa

            qa_mesh = generic_runtime.load_mesh(generated_stl) if generated_stl.is_file() else None
            if qa_mesh is None:
                import build_a_robot_fresh_generalization_v1 as robot_v1

                qa_mesh = robot_v1.tessellate_step(str(generated_step), cand_dir / "mac_tessellate.stl")
            if qa_mesh is not None:
                probe = local_qa.local_component_qa(
                    part,
                    qa_mesh,
                    {"backend": "MAC_GENERATED_CAD", "cad_native": True, "shell": True, "solid": False},
                    cand_dir / "alignment_qa",
                )
                matrix = probe.get("candidate_to_source_transform")
                if probe.get("alignment_applied") and matrix and not local_qa.transform_is_identity(matrix):
                    if generic_runtime.transform_step(generated_step, aligned_step, __import__("numpy").asarray(matrix, dtype=float)):
                        shutil.copy2(aligned_step, generated_step)
                        shutil.copy2(aligned_step, mac_step)
                        alignment = {"applied": True, "matrix": matrix}
        except Exception as exc:
            alignment = {"applied": False, "error": f"{type(exc).__name__}:{exc}"}

    step_ok = generated_step.is_file() and generated_step.stat().st_size > 0
    payload = {
        "component_id": part.get("component_id"),
        "candidate_id": "MAC_CANDIDATE_01",
        "backend": "MAC_GENERATED_CAD",
        "mac_hypothesis_id": "MAC_CANDIDATE_01",
        "representation": "MAC_BUILD123D_STEP",
        "topology_class": "MAC_GENERATED_BREP",
        "cad_native": bool(step_ok),
        "MAC_REPO": str(MAC_REPO.resolve()),
        "MAC_PYTHON": str(MAC_PYTHON),
        "MAC_GRAPH_USED": True,
        "ACTUAL_EXECUTED_BUILDER": "MULTI_AGENT_CAD_GRAPH",
        "generated_code_path": str(generated_code.resolve()) if generated_code.is_file() else None,
        "step_path": str(generated_step.resolve()) if step_ok else None,
        "stl_path": str(generated_stl.resolve()) if generated_stl.is_file() else None,
        "runtime_measurements_path": None,
        "runtime_success": step_ok,
        "step_success": step_ok,
        "exit_code": 0 if step_ok else 1,
        "alignment": alignment,
        "visual_entered_mac_prompt": visual_parsed is not None,
        "visual_model": qwen3vl.visual_model() if visual_parsed is not None else None,
        "mac_result": {
            "error_type": result.get("error_type"),
            "execution_log": result.get("execution_log", []),
            "iteration_count": result.get("iteration_count"),
        },
        "runtime_seconds": time.time() - started,
        "failure_reason": None if step_ok else (result.get("error_type") or "MAC_GRAPH_NO_STEP"),
    }
    dump_json(cand_dir / "candidate_manifest.json", payload)
    dump_json(mac_dir / "mac_candidate_manifest.json", payload)
    return payload
