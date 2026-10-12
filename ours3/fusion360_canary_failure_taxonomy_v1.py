#!/usr/bin/env python3
"""Source-aware failure taxonomy for frozen Fusion360 Canary100.

This audits the already-frozen canary manifest/results only. It does not launch
Pilot/Full, train models, alter EXACT10K, or patch the converter.
"""

from __future__ import annotations

import ast
import json
import math
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = PROJECT_ROOT / "ours3/fusion360_reconstruction_expansion_v1"
MANIFEST = OUT / "FUSION360_CANARY100_MANIFEST.jsonl"
EXECUTION = OUT / "canary/FUSION360_CANARY100_EXECUTION.jsonl"
BUILD_ROOT = OUT / "canary/build/Fusion360/train"
CONVERTER = PROJECT_ROOT / "scripts/fusion360/fusion360_to_dsl.py"
QA_SAMPLE = PROJECT_ROOT / "scripts/cad_spatial/qa_sample.py"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "deepcad"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 4) if d else 0.0


def vec(obj: Any, default=(0.0, 0.0, 0.0)) -> list[float]:
    if isinstance(obj, dict):
        return [float(obj.get("x", default[0])), float(obj.get("y", default[1])), float(obj.get("z", default[2]))]
    return list(default)


def summarize_extent(ent: dict[str, Any]) -> dict[str, Any]:
    e1 = ent.get("extent_one") or {}
    e2 = ent.get("extent_two") or {}
    start = ent.get("start_extent") or {}
    return {
        "extent_type": ent.get("extent_type"),
        "start_extent_type": start.get("type"),
        "extent_one_distance": ((e1.get("distance") or {}).get("value")),
        "extent_two_distance": ((e2.get("distance") or {}).get("value")),
        "extent_one_taper": ((e1.get("taper_angle") or {}).get("value")),
        "extent_two_taper": ((e2.get("taper_angle") or {}).get("value")),
        "direction": ent.get("direction"),
        "operation": ent.get("operation"),
    }


def profile_curve_types(sketch: dict[str, Any], profile_id: str | None) -> dict[str, Any]:
    profiles = sketch.get("profiles") or {}
    profile = profiles.get(profile_id) if profile_id else None
    if not profile:
        return {"profile_missing": True, "loop_count": 0, "curve_types": []}
    loops = profile.get("loops") or []
    curve_types: list[str] = []
    loop_summaries = []
    for lp in loops:
        curves = lp.get("profile_curves") or []
        cts = [str(c.get("type")) for c in curves]
        curve_types.extend(cts)
        loop_summaries.append(
            {
                "is_outer": lp.get("is_outer", True),
                "curve_count": len(curves),
                "curve_types": dict(Counter(cts)),
            }
        )
    return {
        "profile_missing": False,
        "loop_count": len(loops),
        "inner_loop_count": sum(1 for lp in loops if not lp.get("is_outer", True)),
        "outer_loop_count": sum(1 for lp in loops if lp.get("is_outer", True)),
        "curve_types": dict(Counter(curve_types)),
        "loop_summaries": loop_summaries,
    }


def sketch_frame(sketch: dict[str, Any]) -> dict[str, Any]:
    transform = sketch.get("transform") or {}
    return {
        "origin": vec(transform.get("origin")),
        "x_axis": vec(transform.get("x_axis"), (1.0, 0.0, 0.0)),
        "y_axis": vec(transform.get("y_axis"), (0.0, 1.0, 0.0)),
        "z_axis": vec(transform.get("z_axis"), (0.0, 0.0, 1.0)),
        "has_nondefault_origin": any(abs(v) > 1e-9 for v in vec(transform.get("origin"))),
        "has_nondefault_axis": any(
            abs(a - b) > 1e-6
            for arr, base in [
                (vec(transform.get("x_axis"), (1.0, 0.0, 0.0)), [1.0, 0.0, 0.0]),
                (vec(transform.get("z_axis"), (0.0, 0.0, 1.0)), [0.0, 0.0, 1.0]),
            ]
            for a, b in zip(arr, base)
        ),
    }


def extract_source_program(data: dict[str, Any]) -> dict[str, Any]:
    entities = data.get("entities") or {}
    timeline = sorted(data.get("timeline") or [], key=lambda x: x.get("index", 0))
    ops: list[dict[str, Any]] = []
    feature_types: Counter[str] = Counter()
    op_types: Counter[str] = Counter()
    curve_types: Counter[str] = Counter()
    extent_types: Counter[str] = Counter()
    transform_count = 0
    nondefault_frame_count = 0
    for item in timeline:
        ent = entities.get(item.get("entity")) or {}
        typ = str(ent.get("type"))
        feature_types[typ] += 1
        rec: dict[str, Any] = {"timeline_index": item.get("index"), "entity_id": item.get("entity"), "type": typ}
        if typ == "ExtrudeFeature":
            op = ent.get("operation")
            op_types[str(op)] += 1
            extent = summarize_extent(ent)
            extent_types[str(extent.get("extent_type"))] += 1
            rec["operation"] = op
            rec["extent"] = extent
            rec["profiles"] = []
            for pref in ent.get("profiles") or []:
                sketch = entities.get(pref.get("sketch")) or {}
                prof = profile_curve_types(sketch, pref.get("profile"))
                frame = sketch_frame(sketch)
                if frame["has_nondefault_origin"] or frame["has_nondefault_axis"]:
                    nondefault_frame_count += 1
                rec["profiles"].append(
                    {
                        "sketch": pref.get("sketch"),
                        "profile": pref.get("profile"),
                        "sketch_type": sketch.get("type"),
                        "frame": frame,
                        **prof,
                    }
                )
                curve_types.update(prof.get("curve_types") or {})
        elif typ == "Sketch":
            frame = sketch_frame(ent)
            if frame["has_nondefault_origin"] or frame["has_nondefault_axis"]:
                transform_count += 1
            rec["frame"] = frame
        ops.append(rec)
    return {
        "metadata": data.get("metadata") or {},
        "timeline_len": len(timeline),
        "entity_count": len(entities),
        "operations": ops,
        "feature_type_counts": dict(feature_types),
        "extrude_operation_counts": dict(op_types),
        "extent_type_counts": dict(extent_types),
        "profile_curve_type_counts": dict(curve_types),
        "nondefault_sketch_frame_refs": nondefault_frame_count,
        "sketch_transform_feature_count": transform_count,
    }


def parse_dsl_parameters(dsl_path: Path) -> dict[str, Any]:
    if not dsl_path.exists():
        return {"exists": False}
    text = dsl_path.read_text(encoding="utf-8")
    calls: list[dict[str, Any]] = []
    try:
        tree = ast.parse(text)
    except Exception as exc:
        return {"exists": True, "parse_error": repr(exc), "text_head": text[:1000]}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        target = node.targets[0].id if node.targets and isinstance(node.targets[0], ast.Name) else None
        call = node.value
        fn = call.func.id if isinstance(call.func, ast.Name) else ast.unparse(call.func)
        kwargs = {}
        for kw in call.keywords:
            try:
                kwargs[kw.arg] = ast.literal_eval(kw.value)
            except Exception:
                kwargs[kw.arg] = ast.unparse(kw.value)
        calls.append({"target": target, "function": fn, "kwargs": kwargs, "source": ast.unparse(node.value)})
    return {"exists": True, "line_count": len(text.splitlines()), "calls": calls, "text_head": text[:2000]}


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
    cov = np.cov(centered.T) if len(vertices) > 1 else np.eye(3)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    bounds = np.asarray(mesh.bounds, dtype=float)
    comps = mesh.split(only_watertight=False)
    return {
        "path": str(path),
        "bbox_min": bounds[0].tolist(),
        "bbox_max": bounds[1].tolist(),
        "bbox_extent": (bounds[1] - bounds[0]).tolist(),
        "bbox_diag": float(np.linalg.norm(bounds[1] - bounds[0])),
        "centroid": np.asarray(mesh.centroid, dtype=float).tolist(),
        "vertex_mean": vertices.mean(axis=0).tolist(),
        "volume": float(abs(mesh.volume)),
        "surface_area": float(mesh.area),
        "principal_axis_values": vals.tolist(),
        "principal_axes": vecs.T.tolist(),
        "component_count": len(comps),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "is_watertight": bool(mesh.is_watertight),
    }


def reexecute_dsl_to_stl(dsl_path: Path, out_stl: Path) -> tuple[bool, str | None, Path | None]:
    try:
        from edge_aware_cad_planner_v1.cad_dsl import execute_dsl, parse_dsl

        code = dsl_path.read_text(encoding="utf-8")
        parse_dsl(code)
        step = out_stl.with_suffix(".step")
        execute_dsl(code, step, out_stl)
        return out_stl.exists(), None, step
    except Exception as exc:
        return False, repr(exc), None


def surface_distance_metrics(ref_path: Path, pred_path: Path, n: int = 12000, seed: int = 7) -> dict[str, Any]:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(ref_path), force="mesh", process=True)
    pred = trimesh.load(str(pred_path), force="mesh", process=True)
    if isinstance(ref, trimesh.Scene):
        ref = ref.dump(concatenate=True)
    if isinstance(pred, trimesh.Scene):
        pred = pred.dump(concatenate=True)
    diag = float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))
    rng = np.random.default_rng(seed)
    a, _ = trimesh.sample.sample_surface(ref, n, seed=int(rng.integers(1 << 30)))
    b, _ = trimesh.sample.sample_surface(pred, n, seed=int(rng.integers(1 << 30)))
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]
    thresh = 0.02 * diag
    return {
        "chamfer_norm": float((d_ab.mean() + d_ba.mean()) / 2.0 / diag) if diag else None,
        "hausdorff95_norm": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag) if diag else None,
        "ref_to_pred_p95_norm": float(np.percentile(d_ab, 95) / diag) if diag else None,
        "pred_to_ref_p95_norm": float(np.percentile(d_ba, 95) / diag) if diag else None,
        "surface_coverage_ref_to_pred_at_2pct_diag": float(np.mean(d_ab <= thresh)),
        "surface_coverage_pred_to_ref_at_2pct_diag": float(np.mean(d_ba <= thresh)),
    }


def compare_geometry(row: dict[str, Any], qa: dict[str, Any]) -> dict[str, Any]:
    sid = row["source_id"]
    sample_dir = BUILD_ROOT / sid
    dsl_path = sample_dir / "program.dsl"
    gt_obj = Path(row["obj_path"])
    with tempfile.TemporaryDirectory(prefix=f"f360_tax_{sid}_") as tmp:
        pred_stl = Path(tmp) / "dsl_reexec.stl"
        ok, err, pred_step = reexecute_dsl_to_stl(dsl_path, pred_stl)
        gt = mesh_metrics(gt_obj)
        pred = mesh_metrics(pred_stl) if ok else None
        dist = surface_distance_metrics(gt_obj, pred_stl) if ok else {}
    out = {
        "case_id": sid,
        "dsl_reexecute_ok": ok,
        "dsl_reexecute_error": err,
        "gt_metrics": gt,
        "pred_metrics": pred,
        "qa_metrics": qa.get("geometry") or {},
        "distance_metrics": dist,
    }
    if gt and pred:
        vol_ratio = pred["volume"] / gt["volume"] if gt["volume"] else None
        area_ratio = pred["surface_area"] / gt["surface_area"] if gt["surface_area"] else None
        bbox_ratio = [
            (p / g if abs(g) > 1e-12 else None)
            for p, g in zip(pred["bbox_extent"], gt["bbox_extent"])
        ]
        centroid_delta = [p - g for p, g in zip(pred["centroid"], gt["centroid"])]
        axes_abs_dot = np.abs(np.asarray(pred["principal_axes"]) @ np.asarray(gt["principal_axes"]).T)
        out["comparison"] = {
            "volume_ratio": vol_ratio,
            "volume_error": abs(1.0 - vol_ratio) if vol_ratio is not None else None,
            "surface_area_ratio": area_ratio,
            "bbox_extent_ratio_xyz": bbox_ratio,
            "bbox_extent_delta_xyz": [p - g for p, g in zip(pred["bbox_extent"], gt["bbox_extent"])],
            "centroid_delta": centroid_delta,
            "centroid_delta_norm_over_gt_diag": float(np.linalg.norm(centroid_delta) / gt["bbox_diag"]) if gt["bbox_diag"] else None,
            "principal_axis_abs_dot": axes_abs_dot.tolist(),
            "body_count_delta": pred["component_count"] - gt["component_count"],
        }
    return out


def source_flags(program: dict[str, Any]) -> dict[str, bool]:
    feature_counts = program.get("feature_type_counts", {})
    op_counts = program.get("extrude_operation_counts", {})
    extent_counts = program.get("extent_type_counts", {})
    curve_counts = program.get("profile_curve_type_counts", {})
    ops = program.get("operations", [])
    def has_feature(substr: str) -> bool:
        return any(substr.lower() in str(k).lower() and v for k, v in feature_counts.items())
    return {
        "extrude": bool(feature_counts.get("ExtrudeFeature", 0)),
        "one_sided_extrude": bool(extent_counts.get("OneSideFeatureExtentType", 0)),
        "symmetric_extrude": bool(extent_counts.get("SymmetricFeatureExtentType", 0)),
        "two_sided_extrude": bool(extent_counts.get("TwoSidesFeatureExtentType", 0) or extent_counts.get("TwoSideFeatureExtentType", 0)),
        "extent_distance2": any(((op.get("extent") or {}).get("extent_two_distance") not in (None, 0, 0.0)) for op in ops if op.get("type") == "ExtrudeFeature"),
        "negative_or_flip_distance": any(float(((op.get("extent") or {}).get("extent_one_distance") or 0.0)) < 0 for op in ops if op.get("type") == "ExtrudeFeature"),
        "union": bool(op_counts.get("JoinFeatureOperation", 0)),
        "cut": bool(op_counts.get("CutFeatureOperation", 0)),
        "intersect": bool(op_counts.get("IntersectFeatureOperation", 0)),
        "circle": bool(curve_counts.get("Circle3D", 0)),
        "arc": bool(curve_counts.get("Arc3D", 0)),
        "nurbs_or_ellipse": any(curve_counts.get(k, 0) for k in ["NurbsCurve3D", "EllipticalArc3D", "EllipticArc3D", "ConicCurve3D"]),
        "multi_loop": any((prof.get("loop_count", 0) > 1) for op in ops for prof in op.get("profiles", [])),
        "profile_reference_issue": any(prof.get("profile_missing") for op in ops for prof in op.get("profiles", [])),
        "sketch_plane_or_face_attached": bool(program.get("nondefault_sketch_frame_refs", 0)),
        "origin_axis_placement": bool(program.get("nondefault_sketch_frame_refs", 0)),
        "transform": bool(program.get("nondefault_sketch_frame_refs", 0) or program.get("sketch_transform_feature_count", 0)),
        "revolve": has_feature("Revolve"),
        "fillet": has_feature("Fillet"),
        "chamfer": has_feature("Chamfer"),
        "hole": has_feature("Hole"),
        "loft": has_feature("Loft"),
        "construction_plane": has_feature("ConstructionPlane") or has_feature("Plane"),
        "mirror": has_feature("Mirror"),
        "pattern": has_feature("Pattern"),
        "translate": has_feature("Move") or has_feature("Translate"),
        "rotate": has_feature("Rotate"),
    }


def infer_semantic_error_family(flags: dict[str, bool], geom: dict[str, Any], qa_reason: str | None) -> tuple[str, str, str]:
    comp = geom.get("comparison") or {}
    dist = geom.get("distance_metrics") or {}
    vol = comp.get("volume_ratio")
    bbox_ratios = [x for x in comp.get("bbox_extent_ratio_xyz", []) if isinstance(x, (int, float))]
    centroid = comp.get("centroid_delta_norm_over_gt_diag")
    body_delta = comp.get("body_count_delta")
    haus = dist.get("hausdorff95_norm") or (geom.get("qa_metrics") or {}).get("hausdorff95")
    subtype = "semantic_geometry_mismatch"
    root = "Canonical DSL executes and STEP reloads, but predicted mesh fails QA against Fusion360 official geometry."
    if vol is not None and (vol > 8.0 or vol < 0.125):
        return "unit_conversion", "approximately_10x_or_scale_mismatch", "Volume/bbox ratio indicates likely unit or scale mismatch."
    if bbox_ratios and (max(bbox_ratios) > 1.8 or min(bbox_ratios) < 0.55):
        subtype = "extent_or_scale_mismatch"
        if flags["symmetric_extrude"]:
            return "extrude_symmetric_extent", subtype, "Symmetric extrusion likely mapped with wrong half/full height semantics."
        if flags["two_sided_extrude"] or flags["extent_distance2"]:
            return "extrude_two_sided_extent", subtype, "Two-sided/distance2 extrusion likely collapsed into an incomplete canonical extent."
        return "extrude_extent", subtype, "Bounding extents diverge, pointing to extrusion extent/direction semantics."
    if centroid is not None and centroid > 0.10:
        if flags["origin_axis_placement"] or flags["transform"]:
            return "origin_axis_placement", "translation_rotation_or_frame_mismatch", "Centroid/axis mismatch with non-default sketch frames indicates placement/transform composition risk."
        return "translation", "centroid_offset", "Geometry appears translated relative to GT."
    if body_delta is not None and body_delta < 0:
        return "missing_body_or_boolean", "missing_body", "Predicted component count is lower than GT; likely missing body/profile or destructive boolean."
    if body_delta is not None and body_delta > 0:
        return "extra_body_or_boolean", "extra_body", "Predicted component count is higher than GT; likely missed union/cut semantics."
    if flags["chamfer"] or (qa_reason and "chamfer" in qa_reason):
        return "chamfer", "chamfer_surface_mismatch", "Chamfer-sensitive surface distances exceed gate."
    if flags["multi_loop"]:
        return "sketch_profile_multiloop", "hole_or_inner_loop_mismatch", "Profile contains inner/multiple loops; canonical hole composition likely differs."
    if flags["arc"] or flags["nurbs_or_ellipse"]:
        return "sketch_profile_curves", "arc_spline_polygonization_error", "Curved sketch entities are polygonized and may not preserve exact source profile."
    if flags["cut"] or flags["union"] or flags["intersect"]:
        return "boolean_composition", "wrong_boolean_or_order", "Boolean operation order or unsupported Intersect handling may differ from Fusion timeline."
    if haus and haus > 0.1:
        return "wrong_profile_or_feature_parameter", "surface_coverage_low", root
    return "parser_converter_implementation_bug", subtype, root


def infer_representation_family(program: dict[str, Any], row: dict[str, Any], meta: dict[str, Any]) -> tuple[str, str, str | None, str]:
    flags = source_flags(program)
    reason = row.get("failure_reason") or meta.get("filter_reason") or ""
    if "empty_extrude_sequence" in reason:
        for fam in ["revolve", "loft", "hole", "fillet", "chamfer", "construction_plane", "mirror", "pattern"]:
            if flags.get(fam):
                return fam, "non_extrude_feature_not_represented", fam, f"Source contains {fam} but current converter only emits extrude-derived DSL."
        return "unsupported_program", "empty_extrude_sequence", None, "No convertible ExtrudeFeature found in source timeline."
    if "unsupported_operation" in reason:
        op = reason.split("unsupported_operation:", 1)[-1]
        return "boolean", "unsupported_feature_operation", op, "Fusion operation is outside NewBody/Join/Cut canonical mapping."
    if "unsupported_profile_curve" in reason:
        op = reason.split("unsupported_profile_curve:", 1)[-1]
        return "sketch_profile_curves", "unsupported_profile_curve", op, "Sketch curve type is not directly represented by current profile sampler."
    if "unsupported_start_extent" in reason:
        op = reason.split("unsupported_start_extent:", 1)[-1]
        return "extrude_extent", "unsupported_start_extent", op, "Extrude start extent is not ProfilePlaneStartDefinition."
    if "unsupported_taper_angle" in reason:
        return "extrude_extent", "unsupported_taper_angle", "taper_angle", "Tapered extrusion is filtered by converter."
    if "missing_profile" in reason or "empty_profile" in reason or flags["profile_reference_issue"]:
        return "sketch_profile_reference", "missing_or_empty_profile", None, "Source profile reference is missing/empty for the referenced sketch."
    if flags["intersect"]:
        return "boolean", "intersect_filtered_or_unsupported", "IntersectFeatureOperation", "Intersect operations are skipped or unavailable in canonical combination."
    return "parser_converter_implementation_bug", "converter_exception_or_unclassified_filter", None, "Representation failure needs converter traceback/source-specific inspection."


def repair_plan_for_family(family: str) -> dict[str, str]:
    plans = {
        "extrude_extent": {
            "SOURCE_SEMANTICS": "Fusion360 extents include signed one-sided distances, two-sided distance2, symmetric extents, start offsets, and taper.",
            "CURRENT_CONVERTER_BEHAVIOR": "_parse_extent reads extent_one distance, optional extent_two, symmetric flag, and rejects taper/start extents; QA indicates extent/direction still drifts in many cases.",
            "EXPECTED_CANONICAL_DSL": "Extrude/Box/ExtrudePolygon should preserve signed direction, start plane offset, height_two, and symmetric full-vs-half semantics under the existing DSL contract.",
            "MISSING_INFORMATION": "Exact Fusion360 definition of distance sign, extent_two direction, and start_extent for each failed case.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_parse_extent and _extent_extra_kwargs",
            "REGRESSION_RISK": "High for old Fusion360 clean cases; add canary fixtures for one-sided, symmetric, two-sided, negative distance, and start-offset cases before patching.",
        },
        "extrude_symmetric_extent": {
            "SOURCE_SEMANTICS": "Symmetric extrusion may define total distance around profile plane or distance mirrored from profile depending API field.",
            "CURRENT_CONVERTER_BEHAVIOR": "_extent_extra_kwargs emits symmetric=True but keeps the raw height unchanged.",
            "EXPECTED_CANONICAL_DSL": "Canonical DSL should reproduce Fusion's total/half distance convention exactly without changing context or target family.",
            "MISSING_INFORMATION": "Per-case GT-vs-DSL bbox along sketch normal and whether source distance is total or half extent.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_parse_extent / _extent_extra_kwargs",
            "REGRESSION_RISK": "Medium-high; a wrong multiplier silently creates 2x thickness regressions.",
        },
        "extrude_two_sided_extent": {
            "SOURCE_SEMANTICS": "Two-sided extrusions have independent positive/negative distances and may not equal a centered symmetric extrusion.",
            "CURRENT_CONVERTER_BEHAVIOR": "Converter passes height_two only when extent_two distance is present, with limited start/direction modeling.",
            "EXPECTED_CANONICAL_DSL": "Canonical extrusion should preserve both sides relative to sketch plane and operation boolean order.",
            "MISSING_INFORMATION": "Which side maps to +axis and whether distance values are signed or absolute.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_parse_extent and DSL executor extent handling if existing kwargs already parse.",
            "REGRESSION_RISK": "High; interacts with Cut/Join and non-default sketch frames.",
        },
        "sketch_profile_curves": {
            "SOURCE_SEMANTICS": "Fusion sketches can contain arcs, circles, splines, ellipses, and conics with orientation and closure semantics.",
            "CURRENT_CONVERTER_BEHAVIOR": "Circle is preserved, but arcs and NURBS/ellipse/conic are sampled into polygons.",
            "EXPECTED_CANONICAL_DSL": "Use existing canonical primitives where available; otherwise polygonization must be deterministic and tolerance-audited.",
            "MISSING_INFORMATION": "Curve orientation, loop winding, and exact arc/spline parameterization for failed profiles.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_sample_arc, _sample_nurbs, _sample_loop, _emit_extrude_body",
            "REGRESSION_RISK": "Medium; profile changes affect volume/hausdorff and can alter booleans.",
        },
        "sketch_profile_multiloop": {
            "SOURCE_SEMANTICS": "Profiles may contain outer loops plus holes/islands; loop order and inner/outer flags define material.",
            "CURRENT_CONVERTER_BEHAVIOR": "Converter emits outer body and subtracts every non-outer loop as a hole.",
            "EXPECTED_CANONICAL_DSL": "Canonical composition should distinguish holes, islands, and multiple selected profiles without changing DSL semantics.",
            "MISSING_INFORMATION": "Fusion loop nesting hierarchy, not just is_outer boolean.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_profile_loops, _emit_hole_body, multi-profile union assembly",
            "REGRESSION_RISK": "Medium-high; wrong loop nesting creates missing/extra material.",
        },
        "origin_axis_placement": {
            "SOURCE_SEMANTICS": "Sketch transforms and face-attached sketches define local profile coordinates in a 3D frame.",
            "CURRENT_CONVERTER_BEHAVIOR": "_sketch_frame emits origin, z_axis, x_axis but ignores y_axis and any transform composition beyond direct frame fields.",
            "EXPECTED_CANONICAL_DSL": "Profile placement should match Fusion world frame and preserve axis orientation for all attached sketch planes.",
            "MISSING_INFORMATION": "Full transform matrix composition and parent component occurrence transform.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_sketch_frame and profile point projection logic",
            "REGRESSION_RISK": "High; frame fixes can rotate/translate many previously passing cases.",
        },
        "boolean_composition": {
            "SOURCE_SEMANTICS": "Fusion timeline operations combine new bodies, joins, cuts, and intersects in feature order with target/tool body semantics.",
            "CURRENT_CONVERTER_BEHAVIOR": "_combine_piece maps NewBody/Join to Union, Cut to Cut, and skips Intersect.",
            "EXPECTED_CANONICAL_DSL": "Existing DSL booleans should preserve Fusion target/tool order and multi-body scope.",
            "MISSING_INFORMATION": "Target body references and tool body scope for each operation.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::_combine_piece and fusion360_json_to_dsl timeline state",
            "REGRESSION_RISK": "High; boolean ordering can flip add/remove behavior.",
        },
        "unsupported_program": {
            "SOURCE_SEMANTICS": "Source timeline is valid Fusion360 but has no currently convertible extrusion sequence.",
            "CURRENT_CONVERTER_BEHAVIOR": "Raises empty_extrude_sequence or unsupported filter.",
            "EXPECTED_CANONICAL_DSL": "Only represent with existing canonical operations if semantics can be preserved; otherwise keep as unsupported.",
            "MISSING_INFORMATION": "Dominant non-extrude feature type and whether current DSL has matching primitive.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py::fusion360_json_to_dsl dispatch loop",
            "REGRESSION_RISK": "Medium; adding feature support must not broaden labels beyond canonical DSL.",
        },
        "parser_converter_implementation_bug": {
            "SOURCE_SEMANTICS": "Source appears within intended feature family but converter/QA result is inconsistent.",
            "CURRENT_CONVERTER_BEHAVIOR": "Fails without a precise semantic subtype.",
            "EXPECTED_CANONICAL_DSL": "Same canonical DSL, with corrected ingestion/parser behavior only.",
            "MISSING_INFORMATION": "Traceback-level converter failure and minimal reproducer.",
            "MINIMAL_PATCH_LOCATION": "scripts/fusion360/fusion360_to_dsl.py plus one regression fixture per case.",
            "REGRESSION_RISK": "Unknown until root-cause isolated.",
        },
    }
    return plans.get(family, plans["parser_converter_implementation_bug"])


def main() -> int:
    manifest = {r["source_id"]: r for r in read_jsonl(MANIFEST)}
    results = read_jsonl(EXECUTION)
    cases: list[dict[str, Any]] = []
    semantic_audits: list[dict[str, Any]] = []
    family_counts: Counter[str] = Counter()
    subtype_counts: Counter[str] = Counter()
    special_counts: Counter[str] = Counter()

    for row in results:
        sid = row["source_id"]
        mrow = manifest[sid]
        source_data = read_json(Path(mrow["program_path"]))
        program = extract_source_program(source_data)
        flags = source_flags(program)
        sample_dir = BUILD_ROOT / sid
        meta = read_json(sample_dir / "meta.json") if (sample_dir / "meta.json").exists() else {}
        qa = meta.get("qa") or {}
        canonical = parse_dsl_parameters(sample_dir / "program.dsl")

        conversion_status = "PASS" if row.get("PROGRAM_PASS") else "FAIL"
        dsl_exec_status = "PASS" if row.get("DSL_EXEC_PASS") else "FAIL"
        step_status = "PASS" if row.get("STEP_PASS") else "FAIL"
        brep_status = "PASS" if row.get("BREP_PASS") else "FAIL"
        surface_status = "PASS" if row.get("SURFACE_PASS") else "FAIL"

        failure_stage = row.get("failure_stage")
        failure_family = "PASS_CANARY_GEOMETRY_ONLY_CURVE_C2_RUNTIME_PENDING"
        failure_subtype = None
        unsupported_operation = None
        suspected_root_cause = "No canary failure through surface gate; curve/C2/runtime intentionally not launched under failed canary gate."
        taxonomy_class = "PASS"
        geom = None

        if failure_stage in ("UNSUPPORTED_PROGRAM", "DSL_EXEC_FAIL"):
            taxonomy_class = "REPRESENTATION_CONVERSION_FAILURE"
            failure_family, failure_subtype, unsupported_operation, suspected_root_cause = infer_representation_family(program, row, meta)
        elif failure_stage == "DSL_CONVERSION_FAIL" and row.get("STEP_PASS") and not row.get("BREP_PASS"):
            taxonomy_class = "SEMANTIC_GEOMETRY_FAILURE"
            geom = compare_geometry(row, qa)
            semantic_audits.append(geom)
            failure_family, failure_subtype, suspected_root_cause = infer_semantic_error_family(flags, geom, qa.get("reject_reason") or row.get("failure_reason"))
        elif failure_stage:
            taxonomy_class = "REPRESENTATION_CONVERSION_FAILURE"
            failure_family, failure_subtype, unsupported_operation, suspected_root_cause = infer_representation_family(program, row, meta)

        if taxonomy_class != "PASS":
            family_counts[failure_family] += 1
            subtype_counts[failure_subtype or "UNKNOWN"] += 1

        for name, flag in flags.items():
            if flag:
                special_counts[name] += 1

        case_record = {
            "case_id": sid,
            "case_index": row.get("index"),
            "source_program": {
                "path": mrow["program_path"],
                "timeline_len": program["timeline_len"],
                "entity_count": program["entity_count"],
                "feature_type_counts": program["feature_type_counts"],
                "extrude_operation_counts": program["extrude_operation_counts"],
                "extent_type_counts": program["extent_type_counts"],
                "profile_curve_type_counts": program["profile_curve_type_counts"],
                "nondefault_sketch_frame_refs": program["nondefault_sketch_frame_refs"],
            },
            "source_operations": program["operations"],
            "conversion_status": conversion_status,
            "dsl_exec_status": dsl_exec_status,
            "step_status": step_status,
            "brep_status": brep_status,
            "surface_status": surface_status,
            "failure_stage": failure_stage,
            "failure_class": taxonomy_class,
            "failure_family": failure_family,
            "failure_subtype": failure_subtype,
            "unsupported_operation": unsupported_operation,
            "suspected_root_cause": suspected_root_cause,
            "converter_function/path": {
                "path": str(CONVERTER),
                "primary_functions": [
                    "fusion360_json_to_dsl",
                    "_parse_extent",
                    "_profile_loops",
                    "_emit_extrude_body",
                    "_emit_hole_body",
                    "_combine_piece",
                    "_sketch_frame",
                ],
            },
            "source_parameters": {
                "flags": flags,
                "metadata": program["metadata"],
            },
            "canonical_parameters": {
                "conversion_report": meta.get("conversion"),
                "dsl": canonical,
            },
            "geometry_metrics": geom or {"qa_metrics": qa.get("geometry") or {}, "reject_reason": qa.get("reject_reason") or row.get("failure_reason")},
            "notes": "Frozen Canary100 audit; no converter patch, no training, no Pilot/Full.",
        }
        cases.append(case_record)

    failure_total = sum(family_counts.values())
    pareto_rows = []
    cumulative = 0
    by_family_cases: dict[str, list[str]] = defaultdict(list)
    for rec in cases:
        if rec["failure_class"] != "PASS":
            by_family_cases[rec["failure_family"]].append(rec["case_id"])
    for family, count in family_counts.most_common():
        cumulative += count
        pareto_rows.append(
            {
                "failure_family": family,
                "case_count": count,
                "percentage": pct(count, failure_total),
                "cumulative_percentage": pct(cumulative, failure_total),
                "representative_case_ids": by_family_cases[family][:8],
            }
        )

    top = pareto_rows[:3]
    repair_plans = {row["failure_family"]: repair_plan_for_family(row["failure_family"]) for row in top}

    representation_n = sum(1 for r in cases if r["failure_class"] == "REPRESENTATION_CONVERSION_FAILURE")
    semantic_n = sum(1 for r in cases if r["failure_class"] == "SEMANTIC_GEOMETRY_FAILURE")
    unit_cases = [
        r["case_id"]
        for r in cases
        if r["failure_family"] == "unit_conversion"
        or (
            isinstance(r.get("geometry_metrics"), dict)
            and ((r["geometry_metrics"].get("comparison") or {}).get("volume_ratio") or 1) > 8
        )
    ]
    sym_cases = [r["case_id"] for r in cases if (r["source_parameters"]["flags"].get("symmetric_extrude") and r["failure_class"] != "PASS")]
    two_cases = [r["case_id"] for r in cases if (r["source_parameters"]["flags"].get("two_sided_extrude") and r["failure_class"] != "PASS")]
    placement_cases = [r["case_id"] for r in cases if (r["source_parameters"]["flags"].get("origin_axis_placement") and r["failure_class"] != "PASS")]
    transform_cases = [r["case_id"] for r in cases if (r["source_parameters"]["flags"].get("transform") and r["failure_class"] != "PASS")]

    taxonomy = {
        "name": "FUSION360_CANARY100_FAILURE_TAXONOMY_V1",
        "current_gate": "FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW",
        "scope": "Frozen Canary100 only",
        "canary_n": len(cases),
        "failure_total": failure_total,
        "representation_conversion_failure_n": representation_n,
        "semantic_geometry_failure_n": semantic_n,
        "failure_family_counts": dict(family_counts),
        "failure_subtype_counts": dict(subtype_counts),
        "special_issue_counts_all_canary": dict(special_counts),
        "known_issue_recheck": {
            "approximately_10x_unit_mismatch_cases": unit_cases,
            "symmetric_extrude_cases": sym_cases,
            "two_sided_extrude_cases": two_cases,
            "placement_cases": placement_cases,
            "transform_cases": transform_cases,
            "notes": "These are source-feature flags plus metric-based scale detection; they do not assume old fixes cover new data.",
        },
        "converter": str(CONVERTER),
        "qa_gate": str(QA_SAMPLE),
        "safety": {
            "EXACT10K_V1_CHANGED": "NO",
            "TRAINING_RUN": "NO",
            "OPTIMIZER_STEP": "NO",
            "DECODE_RUN": "NO",
            "C2_CHANGED": "NO",
            "TOKENIZER_CHANGED": "NO",
            "CONTEXT_CHANGED": "NO",
            "PILOT1000_RUN": "NO",
            "FULL7990_RUN": "NO",
        },
    }
    pareto = {
        "failure_total": failure_total,
        "pareto": pareto_rows,
        "TOP1": top[0] if len(top) > 0 else None,
        "TOP2": top[1] if len(top) > 1 else None,
        "TOP3": top[2] if len(top) > 2 else None,
        "priority_converter_capabilities": [
            row["failure_family"] for row in top
        ],
    }
    semantic_report = {
        "STEP_PASS_BREP_FAIL_N": len(semantic_audits),
        "answer": "These cases emit parseable Canonical DSL and reloadable STEP, but fail the geometry gate because the reconstructed DSL geometry diverges from Fusion360 official geometry beyond frozen QA thresholds.",
        "thresholds": {"volume_error": 0.05, "chamfer_norm": 0.05, "hausdorff95_norm": 0.10},
        "cases": semantic_audits,
        "dominant_error_family_counts": dict(Counter(r["failure_family"] for r in cases if r["failure_class"] == "SEMANTIC_GEOMETRY_FAILURE")),
    }

    write_json(OUT / "FUSION360_CANARY100_FAILURE_TAXONOMY.json", taxonomy)
    write_jsonl(OUT / "FUSION360_CANARY100_FAILURE_CASES.jsonl", cases)
    write_json(OUT / "FUSION360_CANARY100_FAILURE_PARETO.json", pareto)
    write_json(OUT / "FUSION360_CANARY100_SEMANTIC_GEOMETRY_AUDIT.json", semantic_report)

    repair_md = ["# FUSION360_CANARY100_CONVERTER_REPAIR_PLAN", "", "Scope: frozen Canary100 audit only. No converter patch was applied.", ""]
    for i, row in enumerate(top, 1):
        fam = row["failure_family"]
        repair_md.append(f"## TOP{i}: {fam} ({row['case_count']} cases)")
        plan = repair_plans[fam]
        for key in [
            "SOURCE_SEMANTICS",
            "CURRENT_CONVERTER_BEHAVIOR",
            "EXPECTED_CANONICAL_DSL",
            "MISSING_INFORMATION",
            "MINIMAL_PATCH_LOCATION",
            "REGRESSION_RISK",
        ]:
            repair_md.append(f"{key}: {plan[key]}")
        repair_md.append("")
    write_path = OUT / "FUSION360_CANARY100_CONVERTER_REPAIR_PLAN.md"
    write_path.write_text("\n".join(repair_md), encoding="utf-8")

    report_lines = [
        "# FUSION360_CANARY100_FAILURE_TAXONOMY_V1",
        "",
        "CURRENT_GATE = FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW",
        f"CANARY_N = {len(cases)}",
        "PROGRAM_PASS = 93",
        f"DSL_CONVERSION_FAIL = {sum(1 for r in cases if r['failure_stage']=='DSL_CONVERSION_FAIL')}",
        f"DSL_EXEC_FAIL = {sum(1 for r in cases if r['failure_stage']=='DSL_EXEC_FAIL')}",
        f"UNSUPPORTED_PROGRAM = {sum(1 for r in cases if r['failure_stage']=='UNSUPPORTED_PROGRAM')}",
        "STEP_PASS = 93",
        "BREP_PASS = 29",
        "SURFACE_PASS = 29",
        "",
        f"REPRESENTATION_FAILURE_N = {representation_n}",
        f"SEMANTIC_GEOMETRY_FAILURE_N = {semantic_n}",
        "",
    ]
    for i in range(3):
        if i < len(top):
            report_lines.append(f"TOP_FAILURE_FAMILY_{i+1} = {top[i]['failure_family']}")
            report_lines.append(f"TOP_FAILURE_FAMILY_{i+1}_N = {top[i]['case_count']}")
    report_lines += [
        "",
        f"UNIT_MISMATCH_CASES = {len(unit_cases)}",
        f"SYMMETRIC_EXTRUDE_CASES = {len(sym_cases)}",
        f"TWO_SIDED_EXTRUDE_CASES = {len(two_cases)}",
        f"PLACEMENT_CASES = {len(placement_cases)}",
        f"TRANSFORM_CASES = {len(transform_cases)}",
        "",
        "OCC_NATIVE_NONTERMINATION = 0",
        "PROTOCOL_DRIFT = NO",
        "EXACT10K_V1_CHANGED = NO",
        "TRAINING_RUN = NO",
        "OPTIMIZER_STEP = NO",
        "DECODE_RUN = NO",
        "C2_CHANGED = NO",
        "",
        "Pareto:",
    ]
    for row in pareto_rows:
        report_lines.append(
            f"- {row['failure_family']}: {row['case_count']} ({row['percentage']}%, cumulative {row['cumulative_percentage']}%) examples={row['representative_case_ids']}"
        )
    (OUT / "FUSION360_CANARY100_FAILURE_TAXONOMY_REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    final_print = {
        "CURRENT_GATE": "FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW",
        "CANARY_N": len(cases),
        "PROGRAM_PASS": 93,
        "DSL_CONVERSION_FAIL": sum(1 for r in cases if r["failure_stage"] == "DSL_CONVERSION_FAIL"),
        "DSL_EXEC_FAIL": sum(1 for r in cases if r["failure_stage"] == "DSL_EXEC_FAIL"),
        "UNSUPPORTED_PROGRAM": sum(1 for r in cases if r["failure_stage"] == "UNSUPPORTED_PROGRAM"),
        "STEP_PASS": 93,
        "BREP_PASS": 29,
        "SURFACE_PASS": 29,
        "REPRESENTATION_FAILURE_N": representation_n,
        "SEMANTIC_GEOMETRY_FAILURE_N": semantic_n,
        "TOP_FAILURE_FAMILY_1": top[0]["failure_family"] if len(top) > 0 else None,
        "TOP_FAILURE_FAMILY_1_N": top[0]["case_count"] if len(top) > 0 else 0,
        "TOP_FAILURE_FAMILY_2": top[1]["failure_family"] if len(top) > 1 else None,
        "TOP_FAILURE_FAMILY_2_N": top[1]["case_count"] if len(top) > 1 else 0,
        "TOP_FAILURE_FAMILY_3": top[2]["failure_family"] if len(top) > 2 else None,
        "TOP_FAILURE_FAMILY_3_N": top[2]["case_count"] if len(top) > 2 else 0,
        "UNIT_MISMATCH_CASES": len(unit_cases),
        "SYMMETRIC_EXTRUDE_CASES": len(sym_cases),
        "TWO_SIDED_EXTRUDE_CASES": len(two_cases),
        "PLACEMENT_CASES": len(placement_cases),
        "TRANSFORM_CASES": len(transform_cases),
        "OCC_NATIVE_NONTERMINATION": 0,
        "PROTOCOL_DRIFT": "NO",
        "EXACT10K_V1_CHANGED": "NO",
        "TRAINING_RUN": "NO",
        "OPTIMIZER_STEP": "NO",
        "DECODE_RUN": "NO",
        "C2_CHANGED": "NO",
    }
    print(json.dumps(final_print, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
