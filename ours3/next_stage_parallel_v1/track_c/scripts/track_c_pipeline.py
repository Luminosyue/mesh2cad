from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
GATE1 = OURS3 / "mac_pipeline"
TRACK = OURS3 / "next_stage_parallel_v1" / "track_c"
PREPARED_MAC = ROOT / "Multi-Agent-CAD"
OFFICIAL_MAC = OURS3 / "external" / "Multi-Agent-CAD"
CANONICAL_DIAGONAL_MM = 100.0
SAMPLE_COUNT = 50_000
SAMPLE_SEED = 20260810
AB_CLASSES = {"A_PROGRAM_CAD_FRIENDLY", "B_PROGRAM_CAD_POSSIBLE"}
QUALITY_THRESHOLDS = {
    "Q1_STRONG_PAIR": {
        "chamfer_max": 0.01,
        "p95_max": 0.02,
        "coverage_02_min": 0.95,
    },
    "Q2_USABLE_PAIR": {
        "chamfer_max": 0.02,
        "p95_max": 0.05,
        "coverage_02_min": 0.85,
    },
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=json_default) + "\n", encoding="utf-8")


def json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    return str(value)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_audit(repo: Path) -> dict:
    def run(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

    status = run("status", "--short")
    return {
        "path": str(repo),
        "commit": run("rev-parse", "HEAD"),
        "branch": run("branch", "--show-current"),
        "dirty": bool(status),
        "status_paths": [line[3:] for line in status.splitlines() if len(line) > 3],
    }


def scale_spec(original: dict, source: dict) -> dict:
    mesh_diag = float(source["bbox_diagonal"])
    mesh_to_cad = CANONICAL_DIAGONAL_MM / mesh_diag
    cad_to_mesh = 1.0 / mesh_to_cad
    scaled = json.loads(json.dumps(original))

    bbox = scaled["object_geometry"]["bbox"]
    for key in ("min", "max", "extents"):
        bbox[key] = [float(v) * mesh_to_cad for v in bbox[key]]
    scaled["object_geometry"]["normalized_bbox_extents"] = [
        float(v) * CANONICAL_DIAGONAL_MM
        for v in scaled["object_geometry"]["normalized_bbox_extents"]
    ]

    parameters = scaled.get("base_feature", {}).get("parameters", {})
    if "estimated_depth" in parameters:
        units = parameters.get("units")
        factor = CANONICAL_DIAGONAL_MM if units == "normalized_bbox_diagonal" else mesh_to_cad
        parameters["estimated_depth"] = float(parameters["estimated_depth"]) * factor
        parameters["units"] = "mm"

    for candidate in scaled.get("symmetry", {}).get("mirror_plane_candidates", []):
        if "offset" in candidate:
            candidate["offset"] = float(candidate["offset"]) * mesh_to_cad
            candidate["offset_units"] = "mm"

    scaled["DRAFT_ONLY"] = False
    scaled["NOT_EXECUTED_BY_MAC"] = False
    scaled["UNIT_KNOWN"] = True
    scaled["source"]["unit_known"] = False
    scaled["canonicalization"] = {
        "canonical_bbox_diagonal_mm": CANONICAL_DIAGONAL_MM,
        "source_bbox_diagonal_mesh_units": mesh_diag,
        "mesh_to_cad_scale": mesh_to_cad,
        "cad_to_mesh_scale": cad_to_mesh,
        "physical_unit_inferred": False,
        "directions_scaled": False,
        "rule": "cad_mm = mesh_coordinate * mesh_to_cad_scale",
    }
    scaled["provenance"] = {
        "geometry_analyzer": "GATE1_V0",
        "prompt_variant": "GEOMETRY_ONLY",
        "prompt_human_edited": False,
        "physx_used": False,
        "p3_used": False,
        "step_gt_used": False,
        "abc_data_used": False,
        "source_has_step_gt": False,
        "cad_generator": "MULTI_AGENT_CAD",
    }
    return scaled


def mac_prompt(case_id: str, original_prompt: str, spec: dict) -> str:
    bbox = spec["object_geometry"]["bbox"]
    base = spec["base_feature"]
    return f"""PROMPT_VARIANT=GEOMETRY_ONLY
PHYSX_USED=false
P3_USED=false
PROMPT_HUMAN_EDITED=false
PHYSICAL_UNIT_INFERRED=false
CANONICAL_BBOX_DIAGONAL_MM={CANONICAL_DIAGONAL_MM:.1f}

Generate one CAD attempt in millimeters using only the supplied Gate1 V0 geometry evidence.
Do not infer object identity, function, materials, assembly, or missing semantic features.
Use the canonical coordinate frame directly; do not apply ICP or any learned registration.
The target bounding box is min={bbox['min']} mm, max={bbox['max']} mm, extents={bbox['extents']} mm.
The only dominant feature hypothesis is {base['type']} with parameters {json.dumps(base['parameters'], sort_keys=True)}.
Construct the simplest single-solid CAD model consistent with those hard dimensions and feature type.
Center and orient the result so its bounding box matches the stated min/max coordinates.

Original Gate1 prompt (unmodified provenance; its unknown-unit instruction is superseded only by the deterministic canonical scale above):
---BEGIN GATE1 PROMPT---
{original_prompt.rstrip()}
---END GATE1 PROMPT---

Canonical geometry-only spec JSON:
{json.dumps(spec, indent=2, sort_keys=True)}
"""


def prepare() -> dict:
    for name in ("artifacts", "logs", "tests", "scripts", "cases", "configs"):
        (TRACK / name).mkdir(parents=True, exist_ok=True)

    summary_path = GATE1 / "artifacts" / "mac_gate1_10case_summary.csv"
    with summary_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    selected = [r for r in rows if r["CADABILITY_CLASS"] in AB_CLASSES]
    selected.sort(key=lambda r: (0 if r["CADABILITY_CLASS"].startswith("A_") else 1, r["CASE"]))
    if len(selected) != 4:
        raise RuntimeError(f"Expected exactly 4 original A/B whole-object cases, found {len(selected)}")
    if sum(r["CADABILITY_CLASS"].startswith("A_") for r in selected) != 1:
        raise RuntimeError("Expected exactly one A pilot")

    cases = []
    for row in selected:
        case_id = row["CASE"]
        g1_case = GATE1 / "cases" / case_id
        source = read_json(g1_case / "source.json")
        original_spec_path = g1_case / "cad_spec" / "cad_spec_v0.json"
        original_prompt_path = g1_case / "cad_spec" / "cad_prompt_v0.txt"
        original_spec = read_json(original_spec_path)
        original_prompt = original_prompt_path.read_text(encoding="utf-8")
        case_dir = TRACK / "cases" / case_id
        out_dir = case_dir / "mac_output_geometry_only"
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original_spec_path, case_dir / "cad_spec_v0_gate1_unchanged.json")
        shutil.copy2(original_prompt_path, case_dir / "cad_prompt_v0_gate1_unchanged.txt")
        scaled = scale_spec(original_spec, source)
        scaled["provenance"]["gate1_spec_sha256"] = sha256(original_spec_path)
        scaled["provenance"]["gate1_prompt_sha256"] = sha256(original_prompt_path)
        write_json(case_dir / "cad_spec_geometry_only_mac.json", scaled)
        prompt = mac_prompt(case_id, original_prompt, scaled)
        (out_dir / "input_prompt.txt").write_text(prompt, encoding="utf-8")
        write_json(case_dir / "provenance.json", {
            **scaled["provenance"],
            "case_id": case_id,
            "source_obj": source["source_obj"],
            "source_obj_sha256": sha256(Path(source["source_obj"])),
            "gate1_summary_row": row,
            "canonicalization": scaled["canonicalization"],
            "mac_commit": git_audit(PREPARED_MAC)["commit"],
        })
        cases.append({
            "case_id": case_id,
            "cadability_class": row["CADABILITY_CLASS"],
            "cadability_score": float(row["CADABILITY_SCORE"]),
            "source_obj": source["source_obj"],
            "case_dir": str(case_dir),
            "mac_output_dir": str(out_dir),
            "mesh_to_cad_scale": scaled["canonicalization"]["mesh_to_cad_scale"],
            "cad_to_mesh_scale": scaled["canonicalization"]["cad_to_mesh_scale"],
        })

    manifest = {
        "track": "MAC_GATE_2_GEOMETRY_BASELINE",
        "input_cases": len(cases),
        "selection_source": str(summary_path),
        "selection_rule": sorted(AB_CLASSES),
        "whole_object_only": True,
        "cases": cases,
        "canonical_bbox_diagonal_mm": CANONICAL_DIAGONAL_MM,
        "sample_count": SAMPLE_COUNT,
        "sample_seed": SAMPLE_SEED,
        "quality_thresholds": QUALITY_THRESHOLDS,
        "prohibitions": {
            "geometry_analyzer_rerun": False,
            "physx_used": False,
            "p3_used": False,
            "step_gt_used": False,
            "abc_data_used": False,
            "icp_used_for_main_metric": False,
            "assembly_started": False,
        },
    }
    write_json(TRACK / "artifacts" / "track_c_manifest.json", manifest)
    write_json(TRACK / "artifacts" / "mac_repo_audit.json", {
        "official_checkout": git_audit(OFFICIAL_MAC),
        "prepared_server_checkout": git_audit(PREPARED_MAC),
        "provider_config_source": str(PREPARED_MAC / "multi_agent_cad" / "config.py"),
        "provider_secret_logged": False,
    })
    print(json.dumps({"selected": [c["case_id"] for c in cases], "pilot": cases[0]["case_id"]}))
    return manifest


def run_case(case_id: str) -> int:
    manifest = read_json(TRACK / "artifacts" / "track_c_manifest.json")
    case = next((c for c in manifest["cases"] if c["case_id"] == case_id), None)
    if case is None:
        raise RuntimeError(f"Case {case_id} is not in frozen A/B manifest")
    case_dir = Path(case["case_dir"])
    out_dir = Path(case["mac_output_dir"])
    prompt = (out_dir / "input_prompt.txt").read_text(encoding="utf-8")
    os.chdir(out_dir)
    sys.path.insert(0, str(PREPARED_MAC))

    from multi_agent_cad import nodes, token_tracker
    from multi_agent_cad.graph import build_graph, get_default_initial_state

    nodes._CACHE_DIR = out_dir / "pipeline_cache"
    nodes._CACHE_DIR.mkdir(parents=True, exist_ok=True)
    token_tracker.tracker.reset()
    state = get_default_initial_state(workflow_id="original")
    state["user_request"] = prompt
    state["force_refresh"] = True
    accumulated = dict(state)
    result = {
        "case_id": case_id,
        "attempted": True,
        "run_success": False,
        "cad_attempt_generated": False,
        "step_generated": False,
        "stl_generated": False,
        "error_class": None,
        "error_message": None,
        "started_unix": time.time(),
    }
    try:
        app = build_graph()
        for event in app.stream(state, {"recursion_limit": 50}):
            for _, node_output in event.items():
                accumulated.update(node_output)
        result["run_success"] = accumulated.get("error_type") in (None, "none")
    except Exception as exc:
        result["error_class"] = type(exc).__name__
        result["error_message"] = str(exc)[:2000]
        (out_dir / "traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")

    def dump_value(value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, dict):
            return {str(k): dump_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [dump_value(v) for v in value]
        return value

    for field, filename in (("cad_brief", "cad_brief.json"), ("architect_plan", "architect_plan.json"), ("qa_report", "mac_qa.json")):
        if accumulated.get(field) is not None:
            write_json(out_dir / filename, dump_value(accumulated[field]))
    write_json(out_dir / "final_state.json", dump_value(accumulated))

    code_files = sorted(out_dir.glob("temp_design*.py"), key=lambda p: p.stat().st_mtime)
    step_files = sorted(out_dir.glob("temp_output*.step"), key=lambda p: p.stat().st_mtime)
    stl_files = sorted(out_dir.glob("temp_output*.stl"), key=lambda p: p.stat().st_mtime)
    result["cad_attempt_generated"] = bool(code_files or step_files or stl_files)
    result["step_generated"] = bool(step_files)
    result["stl_generated"] = bool(stl_files)
    if code_files:
        shutil.copy2(code_files[-1], out_dir / "generated_code.py")
    if step_files:
        shutil.copy2(step_files[-1], out_dir / "generated.step")
    if stl_files:
        shutil.copy2(stl_files[-1], out_dir / "generated.stl")
    usage = token_tracker.tracker.summary()
    write_json(out_dir / "usage.json", usage)
    result["llm_calls"] = int(usage["n_calls"])
    result["total_tokens"] = int(usage["total_tokens"])
    result["finished_unix"] = time.time()
    result["elapsed_seconds"] = round(result["finished_unix"] - result["started_unix"], 3)
    write_json(out_dir / "mac_run_result.json", result)
    print(json.dumps(result))
    return 0 if result["cad_attempt_generated"] else 3


def topology_counts(shape: Any) -> dict:
    from OCP.TopAbs import (
        TopAbs_EDGE,
        TopAbs_FACE,
        TopAbs_SHELL,
        TopAbs_SOLID,
        TopAbs_VERTEX,
    )
    from OCP.TopExp import TopExp_Explorer

    def count(kind: Any) -> int:
        exp = TopExp_Explorer(shape, kind)
        n = 0
        while exp.More():
            n += 1
            exp.Next()
        return n

    return {
        "solid_count": count(TopAbs_SOLID),
        "shell_count": count(TopAbs_SHELL),
        "face_count": count(TopAbs_FACE),
        "edge_count": count(TopAbs_EDGE),
        "vertex_count": count(TopAbs_VERTEX),
    }


def write_obj(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Deterministic STEP retessellation\n")
        for v in vertices:
            f.write(f"v {v[0]:.12g} {v[1]:.12g} {v[2]:.12g}\n")
        for tri in faces:
            f.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")


def qa_case(case_id: str) -> int:
    import trimesh
    from build123d import import_step
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from scipy.spatial import cKDTree

    manifest = read_json(TRACK / "artifacts" / "track_c_manifest.json")
    case = next(c for c in manifest["cases"] if c["case_id"] == case_id)
    out_dir = Path(case["mac_output_dir"])
    step_path = out_dir / "generated.step"
    qa = {
        "case_id": case_id,
        "step_reload_success": False,
        "brep_valid": False,
        "geometry_metrics_computed": False,
        "sample_count_per_surface": SAMPLE_COUNT,
        "sample_seed": SAMPLE_SEED,
        "icp_used": False,
        "quality_class": "Q3_REJECT",
        "error_class": None,
        "error_message": None,
    }
    try:
        reader = STEPControl_Reader()
        status = reader.ReadFile(str(step_path))
        if status != IFSelect_RetDone:
            raise RuntimeError(f"STEPControl_Reader status={status}")
        reader.TransferRoots()
        shape = reader.OneShape()
        qa["step_reload_success"] = not shape.IsNull()
        qa["brep_valid"] = bool(BRepCheck_Analyzer(shape).IsValid())
        qa.update(topology_counts(shape))

        bshape = import_step(step_path)
        verts, tris = bshape.tessellate(tolerance=0.05, angular_tolerance=0.1)
        vertices_mm = np.asarray([[v.X, v.Y, v.Z] for v in verts], dtype=np.float64)
        faces = np.asarray(tris, dtype=np.int64)
        vertices_mesh = vertices_mm * float(case["cad_to_mesh_scale"])
        retess_obj = out_dir / "generated_from_step.obj"
        write_obj(retess_obj, vertices_mesh, faces)

        source = trimesh.load(case["source_obj"], force="mesh", process=False)
        generated = trimesh.Trimesh(vertices=vertices_mesh, faces=faces, process=False)
        src_pts, src_face = trimesh.sample.sample_surface(source, SAMPLE_COUNT, seed=SAMPLE_SEED)
        cad_pts, cad_face = trimesh.sample.sample_surface(generated, SAMPLE_COUNT, seed=SAMPLE_SEED + 1)
        src_normals = source.face_normals[src_face]
        cad_normals = generated.face_normals[cad_face]
        cad_tree = cKDTree(cad_pts)
        src_tree = cKDTree(src_pts)
        s2c, s2c_idx = cad_tree.query(src_pts, k=1, workers=-1)
        c2s, c2s_idx = src_tree.query(cad_pts, k=1, workers=-1)
        source_diag = float(np.linalg.norm(source.bounds[1] - source.bounds[0]))
        s2c_n = s2c / source_diag
        c2s_n = c2s / source_diag
        sym = np.concatenate([s2c_n, c2s_n])
        normal_sc = np.abs(np.sum(src_normals * cad_normals[s2c_idx], axis=1))
        normal_cs = np.abs(np.sum(cad_normals * src_normals[c2s_idx], axis=1))
        src_ext = source.bounds[1] - source.bounds[0]
        cad_ext = generated.bounds[1] - generated.bounds[0]
        src_ctr = source.bounds.mean(axis=0)
        cad_ctr = generated.bounds.mean(axis=0)
        metrics = {
            "symmetric_chamfer_normalized": float((s2c_n.mean() + c2s_n.mean()) / 2.0),
            "source_to_cad_mean": float(s2c_n.mean()),
            "cad_to_source_mean": float(c2s_n.mean()),
            "p95_symmetric": float(np.quantile(sym, 0.95)),
            "hausdorff_approx": float(sym.max()),
            "coverage_005": float((s2c_n <= 0.005).mean()),
            "coverage_01": float((s2c_n <= 0.01).mean()),
            "coverage_02": float((s2c_n <= 0.02).mean()),
            "cad_to_source_coverage_01": float((c2s_n <= 0.01).mean()),
            "normal_consistency": float((normal_sc.mean() + normal_cs.mean()) / 2.0),
            "bbox_extent_linf_error": float(np.max(np.abs(cad_ext - src_ext)) / source_diag),
            "bbox_center_error": float(np.linalg.norm(cad_ctr - src_ctr) / source_diag),
            "source_bbox_diagonal": source_diag,
            "generated_bbox_diagonal_mesh_units": float(np.linalg.norm(cad_ext)),
        }
        qa.update(metrics)
        qa["geometry_metrics_computed"] = True
        if qa["brep_valid"] and metrics["symmetric_chamfer_normalized"] <= 0.01 and metrics["p95_symmetric"] <= 0.02 and metrics["coverage_02"] >= 0.95:
            qa["quality_class"] = "Q1_STRONG_PAIR"
        elif qa["brep_valid"] and metrics["symmetric_chamfer_normalized"] <= 0.02 and metrics["p95_symmetric"] <= 0.05 and metrics["coverage_02"] >= 0.85:
            qa["quality_class"] = "Q2_USABLE_PAIR"
    except Exception as exc:
        qa["error_class"] = type(exc).__name__
        qa["error_message"] = str(exc)[:2000]
        (out_dir / "qa_traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
    write_json(out_dir / "independent_geometry_qa.json", qa)
    print(json.dumps(qa))
    return 0 if qa["geometry_metrics_computed"] else 4


def finalize() -> dict:
    manifest = read_json(TRACK / "artifacts" / "track_c_manifest.json")
    smoke = read_json(TRACK / "artifacts" / "provider_smoke.json")
    results = []
    for case in manifest["cases"]:
        out = Path(case["mac_output_dir"])
        run = read_json(out / "mac_run_result.json") if (out / "mac_run_result.json").exists() else {"attempted": False, "run_success": False, "step_generated": False, "llm_calls": 0, "total_tokens": 0}
        qa = read_json(out / "independent_geometry_qa.json") if (out / "independent_geometry_qa.json").exists() else {"step_reload_success": False, "brep_valid": False, "geometry_metrics_computed": False, "quality_class": "Q3_REJECT"}
        results.append({"case_id": case["case_id"], "cadability_class": case["cadability_class"], "run": run, "qa": qa})
    counts = {
        "mac_attempted": sum(bool(r["run"].get("attempted")) for r in results),
        "mac_run_success": sum(bool(r["run"].get("run_success")) for r in results),
        "mac_step_success": sum(bool(r["run"].get("step_generated")) for r in results),
        "step_reload_success": sum(bool(r["qa"].get("step_reload_success")) for r in results),
        "brep_valid_count": sum(bool(r["qa"].get("brep_valid")) for r in results),
        "geometry_metrics_computed": sum(bool(r["qa"].get("geometry_metrics_computed")) for r in results),
        "q1_strong_pair": sum(r["qa"].get("quality_class") == "Q1_STRONG_PAIR" for r in results),
        "q2_usable_pair": sum(r["qa"].get("quality_class") == "Q2_USABLE_PAIR" for r in results),
        "q3_reject": sum(r["qa"].get("quality_class") == "Q3_REJECT" for r in results),
        "llm_calls": int(smoke.get("llm_calls", 0)) + sum(int(r["run"].get("llm_calls", 0)) for r in results),
        "total_tokens": int(smoke.get("total_tokens", 0)) + sum(int(r["run"].get("total_tokens", 0)) for r in results),
    }
    blockers = []
    if not smoke.get("connectivity_smoke_success"):
        blockers.append("LLM_PROVIDER_CONNECTIVITY_FAILED")
        status = "BLOCKED"
    elif not (counts["mac_attempted"] >= 1 and counts["mac_step_success"] >= 1 and counts["step_reload_success"] >= 1 and counts["geometry_metrics_computed"] >= 1):
        blockers.append("MAC_GATE_2_MINIMUM_SUCCESS_CRITERIA_NOT_MET")
        status = "FAIL"
    else:
        status = "PASS"
    pytest_log = TRACK / "logs" / "pytest.log"
    pytest_text = pytest_log.read_text(encoding="utf-8", errors="replace") if pytest_log.exists() else ""
    passed_match = re.search(r"(\d+) passed", pytest_text)
    failed_match = re.search(r"(\d+) failed", pytest_text)
    tests_passed = int(passed_match.group(1)) if passed_match else 0
    tests_failed = int(failed_match.group(1)) if failed_match else 0
    summary = {
        "TRACK_C": "MAC_GATE_2_GEOMETRY_BASELINE",
        "TRACK_C_STATUS": status,
        "MAC_INPUT_CASES": 4,
        "LLM_PROVIDER_READY": bool(smoke.get("connectivity_smoke_success")),
        "MAC_ATTEMPTED": counts["mac_attempted"],
        "MAC_RUN_SUCCESS": counts["mac_run_success"],
        "MAC_STEP_SUCCESS": counts["mac_step_success"],
        "STEP_RELOAD_SUCCESS": counts["step_reload_success"],
        "BREP_VALID_COUNT": counts["brep_valid_count"],
        "GEOMETRY_METRICS_COMPUTED": counts["geometry_metrics_computed"],
        "Q1_STRONG_PAIR": counts["q1_strong_pair"],
        "Q2_USABLE_PAIR": counts["q2_usable_pair"],
        "Q3_REJECT": counts["q3_reject"],
        "GEOMETRY_ONLY_PSEUDO_PAIR_FEASIBLE": (counts["q1_strong_pair"] + counts["q2_usable_pair"]) >= 1,
        "LLM_CALLS": counts["llm_calls"],
        "TOTAL_TOKENS": counts["total_tokens"],
        "TESTS_PASSED": tests_passed,
        "TESTS_FAILED": tests_failed,
        "PHYSX_USED_IN_MAC_BASELINE": False,
        "P3_INFERENCE_RERUN": False,
        "ASSEMBLY_STARTED": False,
        "STEP_GT_USED": False,
        "ABC_DATA_USED": False,
        "BLOCKERS": blockers,
        "CASES": results,
    }
    write_json(TRACK / "artifacts" / "track_c_summary.json", summary)
    lines = [
        "# Track C — MAC Gate 2 Geometry Baseline",
        "",
        f"Status: **{status}**",
        "",
        "## Scope and provenance",
        "",
        "Four original Gate1 whole-object A/B cases were selected automatically. Gate1 analysis was not rerun. PhysX, P3, STEP GT, ABC GT, ICP, and assembly were not used.",
        "",
        f"Canonical bbox diagonal: {CANONICAL_DIAGONAL_MM:.1f} mm. Metric sample count: {SAMPLE_COUNT} per surface, seed: {SAMPLE_SEED}.",
        "",
        "## Results",
        "",
        "| Case | Gate1 class | STEP | Reload | BREP | Metrics | Quality | Chamfer | P95 | Coverage .02 |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for r in results:
        qa = r["qa"]
        lines.append(
            f"| {r['case_id']} | {r['cadability_class']} | {r['run'].get('step_generated', False)} | {qa.get('step_reload_success', False)} | {qa.get('brep_valid', False)} | {qa.get('geometry_metrics_computed', False)} | {qa.get('quality_class')} | {qa.get('symmetric_chamfer_normalized', '')} | {qa.get('p95_symmetric', '')} | {qa.get('coverage_02', '')} |"
        )
    lines += ["", "## Fixed quality thresholds", "", "Q1: valid BREP, Chamfer <= 0.01, P95 <= 0.02, Coverage_02 >= 0.95. Q2: valid BREP, Chamfer <= 0.02, P95 <= 0.05, Coverage_02 >= 0.85. Otherwise Q3.", "", "## Machine-readable summary", "", f"`{TRACK / 'artifacts' / 'track_c_summary.json'}`", ""]
    (TRACK / "artifacts" / "track_c_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    p_run = sub.add_parser("run-case")
    p_run.add_argument("case_id")
    p_qa = sub.add_parser("qa-case")
    p_qa.add_argument("case_id")
    sub.add_parser("finalize")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
        return 0
    if args.command == "run-case":
        return run_case(args.case_id)
    if args.command == "qa-case":
        return qa_case(args.case_id)
    if args.command == "finalize":
        finalize()
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
