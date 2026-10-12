#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = PROJECT / "ours3/fusion360_reconstruction_expansion_v1"
BUILD = OUT / "canary/build/Fusion360/train"
RAW = PROJECT / "cad_spatial_dataset/Fusion360/reconstruction/reconstruction"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def vec(obj: dict[str, Any] | None, default=(0.0, 0.0, 0.0)) -> np.ndarray:
    if not isinstance(obj, dict):
        return np.asarray(default, dtype=float)
    return np.asarray([float(obj.get("x", default[0])), float(obj.get("y", default[1])), float(obj.get("z", default[2]))], dtype=float)


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def mesh_metrics(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    import trimesh

    mesh = trimesh.load(str(path), force="mesh", process=True)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if mesh is None or len(mesh.vertices) == 0:
        return None
    vertices = np.asarray(mesh.vertices, dtype=float)
    centered = vertices - vertices.mean(axis=0, keepdims=True)
    vals, axes = np.linalg.eigh(np.cov(centered.T) if len(vertices) > 1 else np.eye(3))
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    axes = axes[:, order]
    bounds = np.asarray(mesh.bounds, dtype=float)
    return {
        "bbox_min": bounds[0].tolist(),
        "bbox_max": bounds[1].tolist(),
        "bbox_center": ((bounds[0] + bounds[1]) * 0.5).tolist(),
        "bbox_extent": (bounds[1] - bounds[0]).tolist(),
        "bbox_diag": float(np.linalg.norm(bounds[1] - bounds[0])),
        "centroid": np.asarray(mesh.centroid, dtype=float).tolist(),
        "volume": float(abs(mesh.volume)),
        "surface_area": float(mesh.area),
        "principal_axis_values": vals.tolist(),
        "principal_axes": axes.T.tolist(),
        "component_count": int(len(mesh.split(only_watertight=False))),
    }


def parse_dsl_calls(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    calls = []
    tree = ast.parse(text)
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        target = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
        call = node.value
        fn = call.func.id if isinstance(call.func, ast.Name) else ast.unparse(call.func)
        kwargs = {}
        for kw in call.keywords:
            try:
                kwargs[kw.arg] = ast.literal_eval(kw.value)
            except Exception:
                kwargs[kw.arg] = ast.unparse(kw.value)
        calls.append({"target": target, "function": fn, "kwargs": kwargs, "source": ast.unparse(call)})
    return calls


def profile_points(loop: dict[str, Any]) -> list[tuple[float, float]]:
    pts = []
    for curve in loop.get("profile_curves") or []:
        for key in ("start_point", "end_point", "center_point"):
            if key in curve:
                p = curve[key]
                pts.append((float(p.get("x", 0.0)), float(p.get("y", 0.0))))
    return pts


def local_profile_center(loop: dict[str, Any]) -> tuple[float, float] | None:
    curves = loop.get("profile_curves") or []
    if len(curves) == 1 and curves[0].get("type") == "Circle3D":
        p = curves[0].get("center_point") or {}
        return float(p.get("x", 0.0)), float(p.get("y", 0.0))
    pts = profile_points(loop)
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (max(xs) + min(xs)) * 0.5, (max(ys) + min(ys)) * 0.5


def transform_trace(case_id: str) -> list[dict[str, Any]]:
    data = read_json(RAW / f"{case_id}.json")
    entities = data.get("entities") or {}
    dsl_calls = parse_dsl_calls(BUILD / case_id / "program.dsl")
    call_by_target = {c["target"]: c for c in dsl_calls}
    traces = []
    extrude_idx = 0
    for step in sorted(data.get("timeline") or [], key=lambda x: x.get("index", 0)):
        ent = entities.get(step.get("entity")) or {}
        if ent.get("type") != "ExtrudeFeature":
            continue
        profiles = ent.get("profiles") or []
        for pref_idx, pref in enumerate(profiles):
            sketch = entities.get(pref.get("sketch")) or {}
            transform = sketch.get("transform") or {}
            origin = vec(transform.get("origin"))
            x_axis = unit(vec(transform.get("x_axis"), (1, 0, 0)))
            y_axis = unit(vec(transform.get("y_axis"), (0, 1, 0)))
            z_axis = unit(vec(transform.get("z_axis"), (0, 0, 1)))
            profile = (sketch.get("profiles") or {}).get(pref.get("profile")) or {}
            loops = profile.get("loops") or []
            center = local_profile_center(loops[0]) if loops else None
            expected = origin.copy()
            if center is not None:
                expected = origin + center[0] * x_axis + center[1] * y_axis
            target = f"body_{extrude_idx}" if len(profiles) == 1 else f"body_{extrude_idx}_{pref_idx}"
            call = call_by_target.get(target, {})
            kwargs = call.get("kwargs") or {}
            cur_origin = np.asarray(kwargs.get("origin", (0, 0, 0)), dtype=float)
            cur_axis = unit(np.asarray(kwargs.get("axis", (0, 0, 1)), dtype=float))
            cur_x = unit(np.asarray(kwargs.get("x_axis", (1, 0, 0)), dtype=float))
            traces.append(
                {
                    "case_id": case_id,
                    "timeline_index": step.get("index"),
                    "source_feature_type": ent.get("type"),
                    "source_operation": ent.get("operation"),
                    "source_extent_type": ent.get("extent_type"),
                    "source_sketch_frame": {
                        "origin": origin.tolist(),
                        "x_axis": x_axis.tolist(),
                        "y_axis": y_axis.tolist(),
                        "z_axis": z_axis.tolist(),
                    },
                    "source_feature_frame": {
                        "origin": origin.tolist(),
                        "axis": z_axis.tolist(),
                        "x_axis": x_axis.tolist(),
                        "y_axis": y_axis.tolist(),
                    },
                    "source_body_frame": "not explicitly present in Fusion reconstruction JSON; feature frame used",
                    "parent_transform": "not explicitly present",
                    "child_transform": transform,
                    "source_translation": origin.tolist(),
                    "source_rotation": np.stack([x_axis, y_axis, z_axis], axis=1).tolist(),
                    "source_transform_matrix": np.vstack([
                        np.column_stack([x_axis, y_axis, z_axis, origin]),
                        np.asarray([0.0, 0.0, 0.0, 1.0]),
                    ]).tolist(),
                    "transform_composition_order": "expected world = sketch_origin + local_x*x_axis + local_y*y_axis + local_z*z_axis",
                    "local_profile_center": list(center) if center is not None else None,
                    "expected_global_frame": {
                        "origin": expected.tolist(),
                        "axis": z_axis.tolist(),
                        "x_axis": x_axis.tolist(),
                    },
                    "current_canonical_origin": cur_origin.tolist(),
                    "current_canonical_axis": cur_axis.tolist(),
                    "current_canonical_x_axis": cur_x.tolist(),
                    "current_emitted_transform": call,
                    "origin_delta_expected_minus_current": (expected - cur_origin).tolist(),
                    "axis_angle_error_deg": float(math.degrees(math.acos(np.clip(float(z_axis @ cur_axis), -1, 1)))),
                    "x_axis_angle_error_deg": float(math.degrees(math.acos(np.clip(float(x_axis @ cur_x), -1, 1)))),
                }
            )
        extrude_idx += 1
    return traces


def classify_root(trace_rows: list[dict[str, Any]], geom: dict[str, Any]) -> str:
    max_origin_delta = max((float(np.linalg.norm(r["origin_delta_expected_minus_current"])) for r in trace_rows), default=0.0)
    max_axis = max((r["axis_angle_error_deg"] for r in trace_rows), default=0.0)
    max_x = max((r["x_axis_angle_error_deg"] for r in trace_rows), default=0.0)
    comp = geom.get("comparison") or {}
    centroid = comp.get("centroid_delta_norm_over_gt_diag") or 0.0
    axis_abs = np.asarray(comp.get("principal_axis_abs_dot") or np.eye(3), dtype=float)
    rot_err = float(1.0 - np.max(axis_abs, axis=1).mean()) if axis_abs.size else 0.0
    if max_origin_delta > 1e-5 and max_axis < 1e-4 and max_x < 1e-4 and centroid > 0.05:
        return "origin_dropped"
    if max_axis > 1.0:
        return "axis_dropped"
    if max_x > 1.0:
        return "x_axis_dropped"
    if rot_err > 0.03:
        return "sketch_plane_orientation_loss"
    if max_origin_delta > 1e-5:
        return "incorrect_local_to_global_conversion"
    return "other_placement_issue"


def main() -> int:
    results = read_jsonl(OUT / "canary/FUSION360_CANARY100_EXECUTION.jsonl")
    taxonomy_cases = read_jsonl(OUT / "FUSION360_CANARY100_FAILURE_CASES.jsonl")
    by_case = {r["case_id"]: r for r in taxonomy_cases}
    baseline = []
    target_cases = []
    for row in results:
        sid = row["source_id"]
        tax = by_case[sid]
        meta = read_json(BUILD / sid / "meta.json") if (BUILD / sid / "meta.json").exists() else {}
        baseline.append(
            {
                "case_id": sid,
                "baseline_program_status": "PASS" if row.get("PROGRAM_PASS") else "FAIL",
                "baseline_dsl": str(BUILD / sid / "program.dsl"),
                "baseline_step": str(BUILD / sid / "model.step"),
                "baseline_brep_pass": bool(row.get("BREP_PASS")),
                "baseline_surface_pass": bool(row.get("SURFACE_PASS")),
                "baseline_failure_family": tax.get("failure_family"),
                "baseline_geometry_metrics": tax.get("geometry_metrics"),
            }
        )
        if tax.get("failure_family") == "origin_axis_placement":
            target_cases.append(sid)
    write_json(OUT / "BASELINE_CANARY100_SNAPSHOT.json", {"CANARY_N": len(baseline), "cases": baseline})

    audits = []
    root_counts = Counter()
    for sid in target_cases:
        traces = transform_trace(sid)
        tax = by_case[sid]
        geom = tax.get("geometry_metrics") or {}
        gt = (geom.get("gt_metrics") or {})
        pred = (geom.get("pred_metrics") or {})
        root = classify_root(traces, geom)
        root_counts[root] += 1
        audits.append(
            {
                "case_id": sid,
                "root_cause": root,
                "root_cause_options": {
                    "origin_dropped": root == "origin_dropped",
                    "axis_dropped": root == "axis_dropped",
                    "x_axis_dropped": root == "x_axis_dropped",
                    "incorrect_local_to_global_conversion": root == "incorrect_local_to_global_conversion",
                    "incorrect_parent_child_transform_composition": False,
                    "wrong_transform_multiplication_order": False,
                    "translation_applied_twice": False,
                    "rotation_applied_twice": False,
                    "transform_applied_to_wrong_subtree": False,
                    "body_local_vs_world_coordinate_confusion": root in {"origin_dropped", "incorrect_local_to_global_conversion"},
                    "sketch_plane_orientation_loss": root == "sketch_plane_orientation_loss",
                    "other_placement_issue": root == "other_placement_issue",
                },
                "transform_trace": traces,
                "GT_bbox_center": gt.get("bbox_center") or None,
                "reconstruction_bbox_center": pred.get("bbox_center") or None,
                "GT_principal_axes": gt.get("principal_axes"),
                "reconstruction_principal_axes": pred.get("principal_axes"),
                "translation_error": (geom.get("comparison") or {}).get("centroid_delta"),
                "rotation_error": (geom.get("comparison") or {}).get("principal_axis_abs_dot"),
                "scale_error": (geom.get("comparison") or {}).get("bbox_extent_ratio_xyz"),
                "baseline_geometry_metrics": geom,
            }
        )
    out = {
        "name": "FUSION360_R1_PLACEMENT_ROOT_CAUSE_AUDIT",
        "target_failure_family": "origin_axis_placement",
        "TARGET_N": len(target_cases),
        "root_counts": dict(root_counts),
        "cases": audits,
        "safety": {
            "Pilot1000": "NO",
            "Full7990": "NO",
            "training": "NO",
            "optimizer": "NO",
            "decode": "NO",
            "EXACT10K_V1_CHANGED": "NO",
        },
    }
    write_json(OUT / "FUSION360_R1_PLACEMENT_ROOT_CAUSE_AUDIT.json", out)
    print(json.dumps({"TARGET_N": len(target_cases), "root_counts": dict(root_counts)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
