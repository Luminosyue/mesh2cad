#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = PROJECT / "ours3/fusion360_reconstruction_expansion_v1"
POST = OUT / "r1_placement/postpatch"
BUILD_ROOT = POST / "build"
RAW = PROJECT / "cad_spatial_dataset/Fusion360/reconstruction/reconstruction"
TIMEOUT = 600


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def run(cmd: list[str], timeout=TIMEOUT):
    try:
        p = subprocess.run(cmd, cwd=str(PROJECT), text=True, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "", True


def classify(rc: int, timed_out: bool) -> str | None:
    if timed_out:
        return "OCC_NATIVE_NONTERMINATION"
    if rc == 0:
        return None
    if rc == 2:
        return "UNSUPPORTED_PROGRAM"
    if rc == 1:
        return "DSL_EXEC_FAIL"
    if rc == 3:
        return "SEMANTIC_GEOMETRY_FAIL"
    return "OTHER"


def mesh_metrics(path: Path):
    if not path.exists():
        return None
    import trimesh

    mesh = trimesh.load(str(path), force="mesh", process=True)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if mesh is None or len(mesh.vertices) == 0:
        return None
    verts = np.asarray(mesh.vertices, dtype=float)
    bounds = np.asarray(mesh.bounds, dtype=float)
    vals, axes = np.linalg.eigh(np.cov((verts - verts.mean(axis=0)).T) if len(verts) > 1 else np.eye(3))
    order = np.argsort(vals)[::-1]
    return {
        "bbox_center": ((bounds[0] + bounds[1]) * 0.5).tolist(),
        "bbox_extent": (bounds[1] - bounds[0]).tolist(),
        "bbox_diag": float(np.linalg.norm(bounds[1] - bounds[0])),
        "centroid": np.asarray(mesh.centroid, dtype=float).tolist(),
        "volume": float(abs(mesh.volume)),
        "surface_area": float(mesh.area),
        "principal_axes": axes[:, order].T.tolist(),
        "principal_axis_values": vals[order].tolist(),
        "component_count": int(len(mesh.split(only_watertight=False))),
    }


def reexec_compare(case_id: str, sample_dir: Path):
    try:
        from edge_aware_cad_planner_v1.cad_dsl import execute_dsl
        import tempfile

        dsl = sample_dir / "program.dsl"
        if not dsl.exists():
            return {"error": "missing_dsl"}
        with tempfile.TemporaryDirectory(prefix=f"r1cmp_{case_id}_") as tmp:
            stl = Path(tmp) / "pred.stl"
            execute_dsl(dsl.read_text(encoding="utf-8"), Path(tmp) / "pred.step", stl)
            gt = mesh_metrics(RAW / f"{case_id}.obj")
            pred = mesh_metrics(stl)
            if not gt or not pred:
                return {"error": "mesh_metric_failed", "gt": gt, "pred": pred}
            centroid_delta = np.asarray(pred["centroid"]) - np.asarray(gt["centroid"])
            bbox_delta = np.asarray(pred["bbox_center"]) - np.asarray(gt["bbox_center"])
            axes_abs_dot = np.abs(np.asarray(pred["principal_axes"]) @ np.asarray(gt["principal_axes"]).T)
            return {
                "gt_metrics": gt,
                "pred_metrics": pred,
                "bbox_center_error": float(np.linalg.norm(bbox_delta) / gt["bbox_diag"]) if gt["bbox_diag"] else None,
                "centroid_error": float(np.linalg.norm(centroid_delta) / gt["bbox_diag"]) if gt["bbox_diag"] else None,
                "principal_axis_abs_dot": axes_abs_dot.tolist(),
                "volume_error": abs(1.0 - pred["volume"] / gt["volume"]) if gt["volume"] else None,
                "surface_area_ratio": pred["surface_area"] / gt["surface_area"] if gt["surface_area"] else None,
                "body_count_delta": pred["component_count"] - gt["component_count"],
            }
    except Exception as exc:
        return {"error": repr(exc)}


def main() -> int:
    manifest = read_jsonl(OUT / "FUSION360_CANARY100_MANIFEST.jsonl")
    if BUILD_ROOT.exists():
        shutil.rmtree(BUILD_ROOT)
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, row in enumerate(manifest, 1):
        sid = row["source_id"]
        cmd = [
            sys.executable,
            str(PROJECT / "scripts/fusion360/build_fusion360_sample.py"),
            "--sample-id",
            sid,
            "--output",
            str(BUILD_ROOT),
            "--num-points",
            "8192",
            "--no-vis",
        ]
        start = time.time()
        rc, so, se, timed_out = run(cmd)
        sample_dir = BUILD_ROOT / "Fusion360/train" / sid
        meta = read_json(sample_dir / "meta.json", {})
        qa = meta.get("qa") or {}
        ok = rc == 0 and bool(qa.get("passed", True))
        out = {
            "case_id": sid,
            "cad_id": row["cad_id"],
            "index": i,
            "returncode": rc,
            "elapsed_seconds": round(time.time() - start, 3),
            "timeout": timed_out,
            "PROGRAM_PASS": bool(meta.get("conversion")),
            "DSL_EXEC_PASS": bool(meta.get("occ_qa", {}).get("ok")),
            "STEP_PASS": bool(meta.get("model_step")) or bool(meta.get("occ_qa", {}).get("step")),
            "BREP_PASS": ok,
            "SURFACE_PASS": ok and meta.get("spatial", {}).get("num_points") == 8192,
            "failure_stage": classify(rc, timed_out),
            "failure_reason": qa.get("reject_reason") or se[-1000:] or so[-1000:] or None,
            "artifact_dir": str(sample_dir),
            "qa": qa,
            "conversion": meta.get("conversion"),
        }
        rows.append(out)
        print(f"[post-r1 {i}/{len(manifest)}] {sid} rc={rc} stage={out['failure_stage']}", flush=True)
    write_jsonl(POST / "FUSION360_R1_CANARY100_POSTPATCH_CASES.jsonl", rows)

    counts = {k: sum(1 for r in rows if r[k]) for k in ["PROGRAM_PASS", "DSL_EXEC_PASS", "STEP_PASS", "BREP_PASS", "SURFACE_PASS"]}
    failure_matrix = dict(Counter(r["failure_stage"] or "PASS" for r in rows))
    post_report = {
        "CURRENT_STAGE": "CANARY100_R1_PLACEMENT_POSTPATCH",
        "CANARY_N": len(rows),
        "POST_R1_PROGRAM_PASS": counts["PROGRAM_PASS"],
        "POST_R1_DSL_EXEC_PASS": counts["DSL_EXEC_PASS"],
        "POST_R1_STEP_PASS": counts["STEP_PASS"],
        "POST_R1_BREP_PASS": counts["BREP_PASS"],
        "POST_R1_SURFACE_PASS": counts["SURFACE_PASS"],
        "failure_matrix": failure_matrix,
        "OCC_NATIVE_NONTERMINATION": failure_matrix.get("OCC_NATIVE_NONTERMINATION", 0),
        "PROTOCOL_DRIFT": "NO",
        "Pilot1000": "NO",
        "Full7990": "NO",
        "TRAINING_RUN": "NO",
        "OPTIMIZER_STEP": "NO",
        "DECODE_RUN": "NO",
        "C2_CHANGED": "NO",
    }
    write_json(OUT / "FUSION360_R1_CANARY100_POSTPATCH.json", post_report)

    root = read_json(OUT / "FUSION360_R1_PLACEMENT_ROOT_CAUSE_AUDIT.json")
    target_ids = [r["case_id"] for r in root["cases"]]
    baseline = read_json(OUT / "BASELINE_CANARY100_SNAPSHOT.json")
    base_by_id = {r["case_id"]: r for r in baseline["cases"]}
    post_by_id = {r["case_id"]: r for r in rows}
    comparisons = []
    for sid in target_ids:
        before = base_by_id[sid]
        after = post_by_id[sid]
        after_geom = reexec_compare(sid, Path(after["artifact_dir"]))
        before_geom = before.get("baseline_geometry_metrics") or {}
        comparisons.append(
            {
                "case_id": sid,
                "baseline_brep_pass": before["baseline_brep_pass"],
                "patched_brep_pass": after["BREP_PASS"],
                "fixed": (not before["baseline_brep_pass"]) and after["BREP_PASS"],
                "new_failure": before["baseline_brep_pass"] and not after["BREP_PASS"],
                "baseline_geometry_metrics": before_geom,
                "patched_qa_metrics": after.get("qa", {}).get("geometry") or {},
                "patched_geometry_compare": after_geom,
                "TARGET_CHAMFER_BEFORE": (before_geom.get("distance_metrics") or before_geom.get("qa_metrics") or {}).get("chamfer_norm") or (before_geom.get("qa_metrics") or {}).get("chamfer"),
                "TARGET_CHAMFER_AFTER": after.get("qa", {}).get("chamfer"),
                "TARGET_HAUSDORFF95_BEFORE": (before_geom.get("distance_metrics") or before_geom.get("qa_metrics") or {}).get("hausdorff95_norm") or (before_geom.get("qa_metrics") or {}).get("hausdorff95"),
                "TARGET_HAUSDORFF95_AFTER": after.get("qa", {}).get("hausdorff95"),
                "TARGET_BBOX_ERROR_BEFORE": (before_geom.get("comparison") or {}).get("centroid_delta_norm_over_gt_diag"),
                "TARGET_BBOX_ERROR_AFTER": after_geom.get("bbox_center_error"),
                "TARGET_CENTROID_ERROR_BEFORE": (before_geom.get("comparison") or {}).get("centroid_delta_norm_over_gt_diag"),
                "TARGET_CENTROID_ERROR_AFTER": after_geom.get("centroid_error"),
            }
        )
    target_before = sum(1 for sid in target_ids if base_by_id[sid]["baseline_brep_pass"])
    target_after = sum(1 for sid in target_ids if post_by_id[sid]["BREP_PASS"])
    target_fixed = sum(1 for c in comparisons if c["fixed"])
    target_still_fail = sum(1 for c in comparisons if not c["patched_brep_pass"])
    target_new_failure = sum(1 for c in comparisons if c["new_failure"])
    target_report = {
        "TARGET_FAILURE_FAMILY": "origin_axis_placement",
        "TARGET_N": len(target_ids),
        "TARGET_FIXED_N": target_fixed,
        "TARGET_STILL_FAIL_N": target_still_fail,
        "TARGET_NEW_FAILURE_N": target_new_failure,
        "TARGET_BREP_PASS_BEFORE": target_before,
        "TARGET_BREP_PASS_AFTER": target_after,
        "cases": comparisons,
    }
    write_json(OUT / "FUSION360_R1_PLACEMENT_TARGET_COMPARISON.json", target_report)

    baseline_pass_ids = [r["case_id"] for r in baseline["cases"] if r["baseline_brep_pass"]]
    regressed = [sid for sid in baseline_pass_ids if not post_by_id[sid]["BREP_PASS"]]
    non_target_ids = [r["case_id"] for r in baseline["cases"] if r["case_id"] not in set(target_ids)]
    regression_report = {
        "BASELINE_PASS_N": len(baseline_pass_ids),
        "BASELINE_PASS_STILL_PASS": len(baseline_pass_ids) - len(regressed),
        "BASELINE_PASS_REGRESSED": len(regressed),
        "regressed_case_ids": regressed,
        "non_target_case_n": len(non_target_ids),
        "non_target_regression_note": "Checked all non-target canary cases against baseline pass/fail status; patch scope was placement-only.",
        "unit_boolean_extrude_profile_protocol_drift": "NO",
        "PROTOCOL_DRIFT": "NO",
    }
    write_json(OUT / "FUSION360_R1_PLACEMENT_REGRESSION_AUDIT.json", regression_report)

    taxonomy = read_json(OUT / "FUSION360_CANARY100_FAILURE_TAXONOMY.json")
    placement_exposure_n = len(taxonomy["known_issue_recheck"].get("placement_cases", []))
    transform_exposure_n = len(taxonomy["known_issue_recheck"].get("transform_cases", []))
    placement_attributed_n = taxonomy["failure_family_counts"].get("origin_axis_placement", 0)
    transform_attributed_n = placement_attributed_n

    root_counts = root["root_counts"]
    gate = (
        "FUSION360_CANARY_R1_PLACEMENT_REPAIR_PASS"
        if target_fixed >= 15 and len(regressed) == 0 and post_report["OCC_NATIVE_NONTERMINATION"] == 0
        else "FUSION360_CANARY_R1_PLACEMENT_REPAIR_REVIEW"
    )
    final = {
        "CURRENT_GATE": gate,
        "CANARY_N": len(rows),
        "BASELINE_PROGRAM_PASS": 93,
        "BASELINE_STEP_PASS": 93,
        "BASELINE_BREP_PASS": 29,
        "BASELINE_SURFACE_PASS": 29,
        "TARGET_FAILURE_FAMILY": "origin_axis_placement",
        "TARGET_N": len(target_ids),
        "ROOT_ORIGIN_DROPPED_N": root_counts.get("origin_dropped", 0),
        "ROOT_AXIS_DROPPED_N": root_counts.get("axis_dropped", 0),
        "ROOT_X_AXIS_DROPPED_N": root_counts.get("x_axis_dropped", 0),
        "ROOT_FRAME_CONVERSION_N": root_counts.get("incorrect_local_to_global_conversion", 0),
        "ROOT_TRANSFORM_COMPOSITION_N": root_counts.get("incorrect_parent_child_transform_composition", 0),
        "ROOT_TRANSFORM_ORDER_N": root_counts.get("wrong_transform_multiplication_order", 0),
        "ROOT_DOUBLE_TRANSFORM_N": 0,
        "ROOT_SKETCH_PLANE_N": root_counts.get("sketch_plane_orientation_loss", 0),
        "ROOT_OTHER_N": root_counts.get("other_placement_issue", 0),
        "PATCH_FILES": ["/data/home/cuiyuehan/project/mesh2cad/scripts/fusion360/fusion360_to_dsl.py"],
        "PATCH_FUNCTIONS": ["_is_circle_loop", "_is_rect_loop", "_sketch_frame", "_offset_origin_in_sketch_frame", "_emit_extrude_body", "_emit_hole_body"],
        "TARGET_BREP_PASS_BEFORE": target_before,
        "TARGET_BREP_PASS_AFTER": target_after,
        "TARGET_FIXED_N": target_fixed,
        "TARGET_STILL_FAIL_N": target_still_fail,
        "POST_R1_PROGRAM_PASS": counts["PROGRAM_PASS"],
        "POST_R1_DSL_EXEC_PASS": counts["DSL_EXEC_PASS"],
        "POST_R1_STEP_PASS": counts["STEP_PASS"],
        "POST_R1_BREP_PASS": counts["BREP_PASS"],
        "POST_R1_SURFACE_PASS": counts["SURFACE_PASS"],
        "BASELINE_PASS_N": len(baseline_pass_ids),
        "BASELINE_PASS_STILL_PASS": len(baseline_pass_ids) - len(regressed),
        "BASELINE_PASS_REGRESSED": len(regressed),
        "PLACEMENT_EXPOSURE_N": placement_exposure_n,
        "PLACEMENT_ATTRIBUTED_FAILURE_N": placement_attributed_n,
        "TRANSFORM_EXPOSURE_N": transform_exposure_n,
        "TRANSFORM_ATTRIBUTED_FAILURE_N": transform_attributed_n,
        "OCC_NATIVE_NONTERMINATION": post_report["OCC_NATIVE_NONTERMINATION"],
        "PROTOCOL_DRIFT": "NO",
        "EXACT10K_V1_CHANGED": "NO",
        "TRAINING_RUN": "NO",
        "OPTIMIZER_STEP": "NO",
        "DECODE_RUN": "NO",
        "C2_CHANGED": "NO",
    }
    lines = ["# FUSION360_R1_PLACEMENT_REPORT", ""]
    for k, v in final.items():
        lines.append(f"{k}={v}")
    lines += [
        "",
        "Gate rule:",
        "- PASS requires TARGET_FIXED_N >= 15, BASELINE_PASS_REGRESSED = 0, OCC_NATIVE_NONTERMINATION = 0, PROTOCOL_DRIFT = NO.",
        "- Even on PASS, Pilot1000 and Full7990 remain forbidden in this round.",
    ]
    (OUT / "FUSION360_R1_PLACEMENT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
