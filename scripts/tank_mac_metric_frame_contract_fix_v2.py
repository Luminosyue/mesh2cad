#!/usr/bin/env python3
"""TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2 — bind MAC HOW to measured geometry."""
from __future__ import annotations

import ast
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import generic_cad_runtime as rt  # noqa: E402
import tank_mac_transform_contract_fix_v1 as v1  # noqa: E402

FROZEN_P3 = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
V4 = ROOT / "ours3/tank_p3_45_component_pipeline_a_multibackend_repair_v4"
V5 = ROOT / "ours3/tank_p3_45_component_pipeline_a_fullrun_v5"
OUT = ROOT / "ours3/tank_mac_metric_frame_contract_fix_v2"
SOURCE_OBJ = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"


def ensure_dirs() -> Path:
    for sub in (
        "00_audit",
        "01_frame_contract",
        "02_metric_contract",
        "03_component_000/source",
        "03_component_000/original_mac",
        "03_component_000/generated_code_audit",
        "03_component_000/canonical",
        "03_component_000/runtime_binding",
        "03_component_000/fixed_local",
        "03_component_000/fixed_global",
        "03_component_000/qa",
        "03_component_000/visuals",
        "04_generic_runtime",
        "05_v5_integration",
        "artifacts",
    ):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    return OUT


def stage_stats(vertices: np.ndarray) -> dict[str, Any]:
    s = rt.mesh_stats(vertices)
    return {"bbox": [s["bbox_min"], s["bbox_max"]], "centroid": s["centroid"], "extents": s["extent"], "sorted_extents": s["sorted_extent"], "axis": None, "bbox_diagonal": s["bbox_diagonal"]}


def run() -> dict[str, Any]:
    ensure_dirs()
    source_part = FROZEN_P3 / "part_000.obj"
    v4c = V4 / "03_components/P3_COMPONENT_000"
    measured_path = v4c / "01_prepare/measured_spec.json"
    mac_code = v4c / "06_mac/generated_code.py"
    mac_step = v4c / "06_mac/generated.step"
    mac_stl = v4c / "06_mac/generated.stl"
    proxy = v4c / "05_dual_modal/dual_modal/proxy.obj"
    tokens = v4c / "05_dual_modal/dual_modal/canonical_obj_tokens.txt"

    mesh = rt.load_mesh(source_part)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    measured = rt.load_json(measured_path, {}) or {}
    contract = rt.build_frame_contract(vertices, measured)
    local = contract.global_to_local(vertices)
    geom = rt.measured_geometry_contract(mesh, measured, contract)
    rt.dump_json(OUT / "03_component_000/canonical/measured_geometry_contract.json", geom)
    rt.dump_json(OUT / "01_frame_contract/frame_contract.json", contract.to_json())

    shutil.copy2(source_part, OUT / "03_component_000/source/source_part.obj")
    if proxy.is_file():
        shutil.copy2(proxy, OUT / "03_component_000/source/proxy.obj")
    if tokens.is_file():
        shutil.copy2(tokens, OUT / "03_component_000/source/canonical_obj_tokens.txt")
    shutil.copy2(measured_path, OUT / "03_component_000/source/measured_spec.json")
    shutil.copy2(mac_code, OUT / "03_component_000/original_mac/original_generated_code.py")
    shutil.copy2(mac_code, OUT / "03_component_000/original_mac/generated_code.py")
    shutil.copy2(mac_step, OUT / "03_component_000/original_mac/generated.step")
    shutil.copy2(mac_stl, OUT / "03_component_000/original_mac/generated.stl")

    code_text = mac_code.read_text(encoding="utf-8")
    audit_rows = rt.audit_generated_code_numerics(code_text)
    rt.write_csv(OUT / "artifacts/component_000_generated_code_numeric_audit.csv", audit_rows)
    rt.dump_json(OUT / "03_component_000/generated_code_audit/numeric_audit.json", {"rows": audit_rows})

    original_mac = rt.load_mesh(mac_stl)
    orig_v = np.asarray(original_mac.vertices, dtype=float)
    orig_f = np.asarray(original_mac.faces, dtype=np.int64)
    source_major = float(geom["principal_extents"][0])
    mac_literals = [row["literal_value"] for row in audit_rows if abs(row["literal_value"] - 848.5129577095579) < 1e-4 or abs(row["literal_value"] - 848) < 0.6]
    mac_literal_length = float(mac_literals[0]) if mac_literals else float(np.ptp(orig_v, axis=0).max())
    hallucination = bool(abs(mac_literal_length / max(source_major, 1e-12) - 1000.0) < 5.0)
    unit_or_frame = bool(not hallucination and abs(mac_literal_length - source_major) > 1.0)

    probe = rt.cadquery_compat_probe(0.85, 0.025)
    rt.dump_json(OUT / "02_metric_contract/cadquery_compat_probe.json", probe)
    unit_contract = {
        "source_numeric_unit": rt.SOURCE_NUMERIC_UNIT,
        "internal_geometry_unit": rt.INTERNAL_GEOMETRY_UNIT,
        "cad_runtime_unit": rt.CAD_RUNTIME_UNIT,
        "step_unit": rt.STEP_EXPORT_UNIT,
        "mac_canonical_unit_diagnostic": rt.MAC_CANONICAL_UNIT,
        "unit_scale_source_to_runtime": 1.0,
        "unit_scale_runtime_to_step": 1.0,
        "unit_conversion_application_count": 0,
        "MAC_METRIC_HALLUCINATION": hallucination,
        "UNIT_OR_FRAME_MEASUREMENT_BUG": unit_or_frame,
        "SOURCE_MAJOR_EXTENT": source_major,
        "MAC_LITERAL_LENGTH": mac_literal_length,
    }
    rt.dump_json(OUT / "02_metric_contract/unit_contract.json", unit_contract)

    roundtrip = rt.roundtrip_errors(vertices, contract)
    n = min(len(vertices), 20000)
    rng = np.random.default_rng(1)
    sample_idx = rng.choice(len(vertices), n, replace=False)
    sampled = vertices[sample_idx]
    roundtrip_s = rt.roundtrip_errors(sampled, contract)
    canonical_full = contract.apply(local, contract.T_CANONICAL_FROM_LOCAL)
    recovered_full = contract.local_to_global(contract.apply(canonical_full, contract.T_LOCAL_FROM_CANONICAL))
    v1.render_meshes([(vertices, faces, (0.45, 0.55, 0.7), "src")], OUT / "artifacts/source_global.png", "source GLOBAL", vertices)
    v1.render_meshes([(local, faces, (0.45, 0.55, 0.7), "src")], OUT / "artifacts/source_local.png", "source LOCAL", local)
    v1.render_meshes([(canonical_full, faces, (0.45, 0.55, 0.7), "src")], OUT / "artifacts/source_canonical.png", "source CANONICAL", canonical_full)
    v1.render_meshes([(recovered_full, faces, (0.85, 0.4, 0.1), "rt")], OUT / "artifacts/canonical_inverse_global.png", "canonical inverse GLOBAL", recovered_full)
    v1.render_meshes(
        [(vertices, faces, (0.3, 0.5, 0.85), "src"), (recovered_full, faces, (0.85, 0.4, 0.1), "rt")],
        OUT / "artifacts/source_vs_roundtrip.png",
        f"roundtrip max_norm={roundtrip_s['ROUNDTRIP_MAX_ERROR_NORMALIZED']:.2e}",
        vertices,
    )
    if not roundtrip_s["ROUNDTRIP_PASS"]:
        summary_fail = {
            "CURRENT_GATE": "TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_FRAME_FAIL",
            "NEXT_PRIMARY_BLOCKER": "COORDINATE_AND_UNIT_CONTRACT",
            "ROUNDTRIP_PASS": False,
            "ROUNDTRIP_MAX_ERROR_NORMALIZED": roundtrip_s["ROUNDTRIP_MAX_ERROR_NORMALIZED"],
            "MAC_API_REEXECUTED": False,
            "P3_REEXECUTED": False,
        }
        rt.dump_json(OUT / "artifacts/final_summary.json", summary_fail)
        for k, v in summary_fail.items():
            print(f"{k}={v}", flush=True)
        return summary_fail

    shutil.copy2(ROOT / "scripts/generic_cad_runtime.py", OUT / "04_generic_runtime/generic_cad_runtime.py")
    (OUT / "03_component_000/runtime_binding/parameterized_generated_code.py").write_text(rt.parameterized_generated_code(), encoding="utf-8")

    hypothesis = {"builder_family": "EXTRUSION", "profile_type": "ELLIPSE", "mac_literals_ignored": True}
    params = rt.bind_parameters(geom, hypothesis)
    rt.dump_json(OUT / "03_component_000/runtime_binding/runtime_geometry_parameters.json", {"builder_family": params.builder_family, "provenance": params.provenance, **{k: getattr(params, k) for k in ("length", "radius", "radius_y", "radius_z", "x_min", "x_max")}})
    rt.dump_json(OUT / "artifacts/component_000_metric_provenance.json", params.provenance)
    gate = rt.primitive_precondition(geom, params.builder_family)

    # Diagnostic stages A-D use independent constructions, never bbox-fit.
    local_step = OUT / "03_component_000/fixed_local/generated_local_fixed.step"
    built = rt.build_ellipse_extrusion_local(params, local_step)
    local_mesh = rt.tessellate_step(local_step, OUT / "03_component_000/fixed_local/generated_local_fixed.stl") if built["step_success"] else None
    local_v = np.asarray(local_mesh.vertices, dtype=float) if local_mesh is not None else np.zeros((0, 3))
    local_f = np.asarray(local_mesh.faces, dtype=np.int64) if local_mesh is not None else np.zeros((0, 3), dtype=np.int64)
    local_sanity = rt.local_metric_sanity(local, local_v) if len(local_v) else {"LOCAL_METRIC_SANITY_PASS": False}

    global_step = OUT / "03_component_000/fixed_global/generated_global_fixed.step"
    transform_count = 0
    step_ok = False
    if built["step_success"]:
        step_ok = rt.transform_step(local_step, global_step, contract.T_GLOBAL_FROM_LOCAL)
        transform_count = 1
    global_mesh = rt.tessellate_step(global_step, OUT / "03_component_000/fixed_global/generated_global_fixed.stl") if step_ok else None
    global_v = np.asarray(global_mesh.vertices, dtype=float) if global_mesh is not None else np.zeros((0, 3))
    global_f = np.asarray(global_mesh.faces, dtype=np.int64) if global_mesh is not None else np.zeros((0, 3), dtype=np.int64)

    pre = rt.pre_export_sanity(vertices, global_v, transform_count) if len(global_v) else {"PRE_EXPORT_SANITY_PASS": False, "CANDIDATE_VALID_FOR_RANKING": False, "GLOBAL_TRANSFORM_APPLICATION_COUNT": transform_count}

    src_s = rt.mesh_stats(vertices)
    orig_s = rt.mesh_stats(orig_v)
    fix_s = rt.mesh_stats(global_v) if len(global_v) else orig_s
    orig_ratio = rt.extent_ratios(src_s["extent"], orig_s["extent"])
    fix_ratio = rt.extent_ratios(src_s["extent"], fix_s["extent"]) if len(global_v) else orig_ratio
    bugs_before = rt.classify_extent_bug(orig_ratio["XYZ_EXTENT_RATIO"], orig_ratio["SORTED_EXTENT_RATIO"])
    centroid_before = float(np.linalg.norm(np.asarray(orig_s["centroid"]) - np.asarray(src_s["centroid"])))
    centroid_after = float(np.linalg.norm(np.asarray(fix_s["centroid"]) - np.asarray(src_s["centroid"]))) if len(global_v) else centroid_before
    axis_before = v1.axis_angle_degrees(v1.principal_axis(vertices), v1.principal_axis(orig_v))
    axis_after = v1.axis_angle_degrees(v1.principal_axis(vertices), v1.principal_axis(global_v)) if len(global_v) else axis_before

    transform_pass = bool(pre.get("PRE_EXPORT_SANITY_PASS") and pre.get("bbox_center_error_normalized", 1) <= 0.15 and abs(np.log10(max(fix_ratio["SORTED_EXTENT_RATIO"][2], 1e-12))) < 0.15)
    geom_metrics = {"chamfer": None, "coverage": None, "hausdorff": None}
    geom_pass = False
    geom_status = "BLOCKED_BY_TRANSFORM"
    if transform_pass and len(global_v):
        geom_metrics = rt.nearest_metrics(rt.sample_mesh(mesh), global_v)
        geom_pass = bool(geom_metrics["chamfer"] <= 0.05 and geom_metrics["coverage"] >= 0.80 and geom_metrics["hausdorff"] < 0.12)
        geom_status = "PASS" if geom_pass else "FAIL"
        rt.dump_json(OUT / "03_component_000/qa/geometry_qa.json", geom_metrics)
    else:
        rt.dump_json(OUT / "03_component_000/qa/geometry_qa.json", {"GEOMETRY_QA_STATUS": geom_status})

    sections = rt.analyze_cross_sections(local, faces=faces)
    breaks = rt.detect_change_points(sections)
    primitive_correct = bool(len(breaks) == 0 and geom.get("cylindricality_score", 0) >= 0.6)

    # Four diagnostic stages
    stages = {
        "A_ORIGINAL_MAC": stage_stats(orig_v),
        "B_UNIT_FIXED_ONLY": stage_stats(orig_v / 1000.0),
        "C_UNIT_PLUS_AXIS_FIXED": stage_stats(contract.local_to_global(orig_v / 1000.0)),
        "D_FINAL_RUNTIME_BOUND": stage_stats(global_v) if len(global_v) else stage_stats(orig_v),
    }
    rt.dump_json(OUT / "00_audit/before_after_stages.json", stages)

    v1.render_meshes([(vertices, faces, (0.45, 0.55, 0.7), "source")], OUT / "artifacts/component_000_source.png", "P3_COMPONENT_000 source", vertices)
    v1.render_meshes([(orig_v, orig_f, (0.85, 0.45, 0.15), "mac")], OUT / "artifacts/component_000_original_mac.png", "original MAC", orig_v)
    if len(local_v):
        v1.render_meshes([(local, faces, (0.45, 0.55, 0.7), "src"), (local_v, local_f, (0.85, 0.45, 0.15), "cad")], OUT / "artifacts/component_000_metric_fixed_local.png", "local runtime-bound CAD", local)
    if len(global_v):
        v1.render_meshes([(global_v, global_f, (0.85, 0.45, 0.15), "cad")], OUT / "artifacts/component_000_final_global.png", "final SOURCE_GLOBAL CAD", global_v)
        v1.render_meshes([(vertices, faces, (0.35, 0.55, 0.85), "src"), (orig_v, orig_f, (0.85, 0.35, 0.1), "mac")], OUT / "artifacts/component_000_source_vs_original.png", "source vs original MAC", vertices)
        v1.render_meshes([(vertices, faces, (0.35, 0.55, 0.85), "src"), (global_v, global_f, (0.85, 0.45, 0.15), "fix")], OUT / "artifacts/component_000_source_vs_fixed.png", f"SOURCE vs MAC_FIXED centroid_err={centroid_after:.4f} extent={fix_ratio['XYZ_EXTENT_RATIO']}", vertices)

    mac_metric_left = any(item["source"] == "MAC_LITERAL" for item in params.provenance.values())
    v5_text = (ROOT / "scripts/tank_p3_45_component_pipeline_a_fullrun_v5.py").read_text(encoding="utf-8")
    v5_integrated = "mac_runtime_bind_to_source_global" in v5_text and "PARAMETER_BINDING_REEXECUTED" in v5_text

    if mac_metric_left:
        gate_name, blocker = "TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_METRIC_BINDING_FAIL", "MAC_METRIC_PARAMETER_BINDING"
    elif not roundtrip_s["ROUNDTRIP_PASS"]:
        gate_name, blocker = "TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_FRAME_FAIL", "COORDINATE_AND_UNIT_CONTRACT"
    elif transform_pass and not geom_pass:
        gate_name, blocker = "TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_TRANSFORM_PASS_GEOMETRY_FAIL", "MAC_PRIMITIVE_AND_CONSTRUCTION_HYPOTHESIS"
    elif transform_pass and geom_pass:
        gate_name, blocker = "TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_PASS", "BATCH_MAC_RUNTIME_REEXECUTION"
    else:
        gate_name, blocker = "TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_FRAME_FAIL", "COORDINATE_AND_UNIT_CONTRACT"

    summary = {
        "CURRENT_GATE": gate_name,
        "NEXT_PRIMARY_BLOCKER": blocker,
        "P3_REEXECUTED": False,
        "MAC_API_REEXECUTED": False,
        "MAC_RUNTIME_REEXECUTED": True,
        "COMPONENT": "P3_COMPONENT_000",
        "SOURCE_BBOX": [src_s["bbox_min"], src_s["bbox_max"]],
        "SOURCE_CENTROID": src_s["centroid"],
        "SOURCE_EXTENTS": src_s["extent"],
        "ORIGINAL_MAC_BBOX": [orig_s["bbox_min"], orig_s["bbox_max"]],
        "ORIGINAL_MAC_CENTROID": orig_s["centroid"],
        "ORIGINAL_MAC_EXTENTS": orig_s["extent"],
        "SOURCE_MAJOR_EXTENT": source_major,
        "ORIGINAL_MAC_LENGTH": mac_literal_length,
        "RUNTIME_BOUND_LENGTH": params.length,
        "CAD_LOCAL_LENGTH": float(np.ptp(local_v[:, 0])) if len(local_v) else None,
        "CAD_GLOBAL_LENGTH": float(np.max(fix_s["extent"])) if len(global_v) else None,
        "MAC_METRIC_HALLUCINATION": hallucination,
        "UNIT_OR_FRAME_MEASUREMENT_BUG": unit_or_frame,
        "SOURCE_UNIT": rt.SOURCE_NUMERIC_UNIT,
        "INTERNAL_UNIT": rt.INTERNAL_GEOMETRY_UNIT,
        "CAD_RUNTIME_UNIT": rt.CAD_RUNTIME_UNIT,
        "STEP_UNIT": rt.STEP_EXPORT_UNIT,
        "UNIT_CONVERSION_APPLICATION_COUNT": 0,
        "SOURCE_FRAME": "SOURCE_GLOBAL",
        "LOCAL_FRAME": "COMPONENT_LOCAL",
        "MAC_FRAME": "MAC_CANONICAL_MM_TOKENS",
        "FINAL_STEP_FRAME": "SOURCE_GLOBAL",
        "DOUBLE_TRANSFORM_DETECTED": transform_count != 1,
        "MISSING_TRANSFORM_DETECTED": transform_count == 0,
        **bugs_before,
        "BUILD123D_AVAILABLE": False,
        "COMPAT_RUNTIME_USED": True,
        "COMPAT_LENGTH_RATIO": probe.get("COMPAT_LENGTH_RATIO"),
        "COMPAT_RADIUS_RATIO": probe.get("COMPAT_RADIUS_RATIO"),
        "ROUNDTRIP_MAX_ERROR_NORMALIZED": roundtrip_s["ROUNDTRIP_MAX_ERROR_NORMALIZED"],
        "ROUNDTRIP_PASS": roundtrip_s["ROUNDTRIP_PASS"],
        "ORIGINAL_EXTENT_RATIO_XYZ": orig_ratio["XYZ_EXTENT_RATIO"],
        "FIXED_EXTENT_RATIO_XYZ": fix_ratio["XYZ_EXTENT_RATIO"],
        "ORIGINAL_SORTED_EXTENT_RATIO": orig_ratio["SORTED_EXTENT_RATIO"],
        "FIXED_SORTED_EXTENT_RATIO": fix_ratio["SORTED_EXTENT_RATIO"],
        "ORIGINAL_CENTROID_ERROR": centroid_before,
        "FIXED_CENTROID_ERROR": centroid_after,
        "ORIGINAL_AXIS_ERROR": axis_before,
        "FIXED_AXIS_ERROR": axis_after,
        "LOCAL_METRIC_SANITY_PASS": local_sanity.get("LOCAL_METRIC_SANITY_PASS"),
        "PRE_EXPORT_SANITY_PASS": pre.get("PRE_EXPORT_SANITY_PASS"),
        "TRANSFORM_QA_PASS": transform_pass,
        "MAC_PRIMITIVE_HYPOTHESIS_CORRECT": primitive_correct,
        "STRUCTURAL_BREAK_COUNT": len(breaks),
        "CHAMFER": geom_metrics.get("chamfer"),
        "COVERAGE": geom_metrics.get("coverage"),
        "HAUSDORFF": geom_metrics.get("hausdorff"),
        "GEOMETRY_QA_PASS": geom_pass,
        "GEOMETRY_QA_STATUS": geom_status,
        "FINAL_TRANSFORM_USES_ICP": False,
        "FINAL_TRANSFORM_USES_BBOX_FIT": False,
        "FINAL_TRANSFORM_USES_ANISOTROPIC_SCALE": False,
        "GENERATED_LOCAL_FIXED_STEP": str(local_step),
        "GENERATED_GLOBAL_FIXED_STEP": str(global_step),
        "GENERATED_GLOBAL_FIXED_STEP_RELOAD": bool(global_mesh is not None),
        "GENERIC_RUNTIME_INTEGRATED_INTO_V5": v5_integrated,
        "MAC_LITERAL_REMAINS_IN_FINAL_METRICS": mac_metric_left,
        "COMPAT_PROBE": probe,
        "PRIMITIVE_PRECONDITION": gate,
        "source_part_obj_frame": "SOURCE_GLOBAL",
        "MAC_INPUT_FRAME": "SOURCE_GLOBAL_TOKENS_PLUS_MM_SCALED_EXTENTS",
        "RUNTIME_MEASURE_FRAME": "COMPONENT_LOCAL",
        "CAD_BUILD_FRAME": "COMPONENT_LOCAL",
        "PCA_RECOMPUTED_AT_RUNTIME": not contract.pca_reused,
        "GLOBAL_TRANSFORM_APPLICATION_COUNT": transform_count,
        "CASE_SPECIFIC_COMPONENT_ID_IN_GENERIC_RUNTIME": "component_id" in Path(ROOT / "scripts/generic_cad_runtime.py").read_text(encoding="utf-8").split("def bind_parameters")[0],
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
    }
    rt.dump_json(OUT / "03_component_000/qa/transform_qa.json", {"TRANSFORM_QA_PASS": transform_pass, **pre, **fix_ratio})
    tests_passed, tests_failed = 0, 0
    try:
        import subprocess

        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(ROOT / "tests/test_mac_metric_frame_contract_v2.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        tail = (proc.stdout or "") + (proc.stderr or "")
        import re as _re

        m = _re.search(r"(\d+) passed", tail)
        tests_passed = int(m.group(1)) if m else int(proc.returncode == 0)
        f = _re.search(r"(\d+) failed", tail)
        tests_failed = int(f.group(1)) if f else (0 if proc.returncode == 0 else 1)
        summary["PYTEST_OUTPUT_TAIL"] = tail[-1200:]
    except Exception as exc:
        tests_failed = 1
        summary["PYTEST_OUTPUT_TAIL"] = str(exc)
    summary["TESTS_PASSED"] = tests_passed
    summary["TESTS_FAILED"] = tests_failed
    rt.dump_json(OUT / "artifacts/final_summary.json", summary)
    lines = ["# TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2", "", f"CURRENT_GATE={gate_name}", f"NEXT_PRIMARY_BLOCKER={blocker}", "", "```text"]
    lines.extend(f"{k}={v}" for k, v in summary.items())
    lines.append("```")
    (OUT / "artifacts/TANK_MAC_METRIC_FRAME_CONTRACT_FIX_V2_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for k, v in summary.items():
        print(f"{k}={v}", flush=True)
    return summary


def mac_runtime_bind_to_source_global(source_part: Path, measured_spec_path: Path, output_dir: Path, hypothesis: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generic V5 entry: no component-id branch. Rebind measurements and place once."""
    mesh = rt.load_mesh(source_part)
    vertices = np.asarray(mesh.vertices, dtype=float)
    measured = rt.load_json(measured_spec_path, {}) or {}
    contract = rt.build_frame_contract(vertices, measured)
    geom = rt.measured_geometry_contract(mesh, measured, contract)
    local = contract.global_to_local(vertices)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    sections = rt.analyze_cross_sections(local, faces=faces)
    breaks = rt.detect_change_points(sections)
    hyp = hypothesis or {"builder_family": "EXTRUSION"}
    route = rt.route_builder(str(hyp.get("builder_family") or hyp.get("visual_builder_suggestion") or "EXTRUSION"), sections, breaks, geom)
    params = rt.bind_parameters(geom, hyp)
    output_dir.mkdir(parents=True, exist_ok=True)
    built = rt.execute_resolved_builder(local, route, sections, breaks, params, output_dir, faces=np.asarray(mesh.faces, dtype=np.int64))
    local_step = output_dir / "generated_local_fixed.step"
    if built.get("step_success") and built.get("step_path"):
        src = Path(str(built["step_path"]))
        if src.is_file() and src.resolve() != local_step.resolve():
            shutil.copy2(src, local_step)
    global_step = output_dir / "generated_global_fixed.step"
    ok = rt.transform_step(local_step, global_step, contract.T_GLOBAL_FROM_LOCAL) if built.get("step_success") and local_step.is_file() else False
    stl_path = output_dir / "generated_global_fixed.stl"
    if ok:
        rt.tessellate_step(global_step, stl_path)
    return {
        "step_ok": ok,
        "generated_local_step": local_step,
        "generated_global_step": global_step,
        "generated_global_stl": stl_path,
        "contract": contract,
        "params": params,
        "route": route,
        "GLOBAL_TRANSFORM_APPLICATION_COUNT": 1 if ok else 0,
        "MAC_API_REEXECUTED": False,
        "MAC_RUNTIME_REEXECUTED": True,
        "PARAMETER_BINDING_REEXECUTED": True,
        "FINAL_TRANSFORM_USES_ICP": False,
        "FINAL_TRANSFORM_USES_BBOX_FIT": False,
        "FINAL_TRANSFORM_USES_ANISOTROPIC_SCALE": False,
    }


if __name__ == "__main__":
    run()
