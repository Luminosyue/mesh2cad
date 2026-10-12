#!/usr/bin/env python3
"""Frozen post-hoc geometric effectiveness benchmark for EXACT9998 VAL1000.

This script only reads frozen reports, DSL, STEP, STL, and GT assets. It writes
a new benchmark directory and never changes checkpoints, predictions, GT,
parser, evaluator V2, or TEST1000.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/a0_a1_a2_a3_p1_geometric_effectiveness_bench_v1"
EXT_DIR = ROOT / "ours3"

ARM_ORDER = ("A0", "A1", "A2", "A3", "P1")
ARM_DIRS = {
    "A0": ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0",
    "A1": ROOT / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1",
    "A2": ROOT / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a2",
    "A3": ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3",
    "P1": ROOT / "ours3/p1_exact9998_val1000_eval_v2",
}
REPORT_PATHS = {arm: path / "report.json" for arm, path in ARM_DIRS.items()}
ARM_LABEL = {
    "A0": "Surface",
    "A1": "Surface + GT-BRep-Line",
    "A2": "Surface + GT-BRep-Nonline",
    "A3": "Surface + GT-BRep-All-Curves",
    "P1": "A3 + Operation-Aware Structure Loss",
}
METHOD_ORDER = list(ARM_ORDER)
N_CASES = 1000
N_SURFACE_POINTS = 8192
TESSELLATION_TOLERANCE = 1e-3
BOOTSTRAP_N = 10000
SEED = 0
EPS = 1e-12
BOOLEAN_OPS = {"Cut", "Union", "Intersect", "Subtract", "Fuse", "Boolean"}

sys.path.insert(0, str(EXT_DIR))
import remote_extended_cad_metrics as ext  # noqa: E402

ext.ARM_DIRS = ARM_DIRS
ext.REPORT_PATHS = REPORT_PATHS
ext.ARM_LABEL = ARM_LABEL


def ensure_dirs() -> None:
    for name in [
        "protocol",
        "iou",
        "cd",
        "ged",
        "topology",
        "step_reload",
        "complexity",
        "paired",
        "outliers",
        "tables",
        "gallery",
        "reports",
    ]:
        (OUT / name).mkdir(parents=True, exist_ok=True)


def json_dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def csv_dump(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0].keys()) if rows else ["empty"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out: dict[str, Any] = {}
            for field in fields:
                value = row.get(field)
                if value is None:
                    out[field] = ""
                elif isinstance(value, float):
                    out[field] = f"{value:.10g}"
                elif isinstance(value, (dict, list, tuple)):
                    out[field] = json.dumps(value, ensure_ascii=False)
                else:
                    out[field] = value
            writer.writerow(out)


def finite(value: Any) -> bool:
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def flt(value: Any) -> float | None:
    return float(value) if finite(value) else None


def mean(values: list[float]) -> float | None:
    return float(np.mean(values)) if values else None


def median(values: list[float]) -> float | None:
    return float(np.median(values)) if values else None


def percentile(values: list[float], q: float) -> float | None:
    return float(np.percentile(values, q)) if values else None


def value_list(rows: list[dict[str, Any]], field: str) -> list[float]:
    return [float(row[field]) for row in rows if finite(row.get(field))]


def stable_seed(*parts: Any) -> int:
    text = "::".join(str(part) for part in parts)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def load_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for arm in ARM_ORDER:
        path = REPORT_PATHS[arm]
        if not path.exists():
            raise FileNotFoundError(path)
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("n_samples") != N_CASES:
            raise RuntimeError(f"{arm} is not VAL1000: {report.get('n_samples')}")
        reports[arm] = report
    id_sets = [{row["id"] for row in reports[arm]["samples"]} for arm in ARM_ORDER]
    if len(set.intersection(*id_sets)) != N_CASES:
        raise RuntimeError("A0/A1/A2/A3/P1 are not aligned on the same VAL1000 IDs")
    return reports


def load_registry() -> dict[str, dict[str, Any]]:
    path = ROOT / "ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"
    out: dict[str, dict[str, Any]] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                out[item.get("cad_id")] = item
    return out


def read_shape_features(path: Path | None) -> tuple[dict[str, Any], Any | None]:
    if path is None or not path.exists():
        return {"status": "FAIL", "error": "missing_step", "curves": []}, None
    try:
        shape = ext.read_shape(path)
        topo = ext.topology_features(shape)
        curves = ext.extract_curves(shape, sample_n=20)
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps

        props = GProp_GProps()
        BRepGProp.VolumeProperties_s(shape, props)
        topo["volume"] = float(props.Mass())
        topo["curves"] = curves
        topo["curve_n"] = len(curves)
        topo["status"] = "PASS"
        topo["valid_solid"] = bool(
            topo.get("valid_brep")
            and int(topo.get("solid_n", 0)) > 0
            and int(topo.get("closed_shell_n", 0)) > 0
            and finite(topo.get("volume"))
            and float(topo.get("volume", 0.0)) > EPS
        )
        return topo, shape
    except Exception as exc:
        return {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "curves": []}, None


def tessellated_surface_points(shape: Any, sample_n: int, seed: int) -> np.ndarray:
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    from OCP.TopLoc import TopLoc_Location

    BRepMesh_IncrementalMesh(shape, TESSELLATION_TOLERANCE, False, 0.5, True)
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    triangles: list[tuple[np.ndarray, np.ndarray, np.ndarray, float]] = []
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        try:
            location = TopLoc_Location()
            triangulation = BRep_Tool.Triangulation_s(face, location)
            if triangulation is None:
                explorer.Next()
                continue
            transform = location.Transformation()
            nodes: list[np.ndarray] = []
            for index in range(1, triangulation.NbNodes() + 1):
                point = triangulation.Node(index).Transformed(transform)
                nodes.append(np.array([point.X(), point.Y(), point.Z()], dtype=float))
            for index in range(1, triangulation.NbTriangles() + 1):
                n1, n2, n3 = triangulation.Triangle(index).Get()
                a, b, c = nodes[n1 - 1], nodes[n2 - 1], nodes[n3 - 1]
                area = float(np.linalg.norm(np.cross(b - a, c - a)) * 0.5)
                if area > EPS:
                    triangles.append((a, b, c, area))
        except Exception:
            pass
        explorer.Next()
    if not triangles:
        return np.empty((0, 3), dtype=float)
    areas = np.asarray([item[3] for item in triangles], dtype=float)
    probabilities = areas / areas.sum()
    rng = np.random.default_rng(seed)
    choices = rng.choice(len(triangles), size=sample_n, p=probabilities)
    uv = rng.random((sample_n, 2))
    root_u = np.sqrt(uv[:, 0])
    w0 = 1.0 - root_u
    w1 = root_u * (1.0 - uv[:, 1])
    w2 = root_u * uv[:, 1]
    a = np.asarray([triangles[index][0] for index in choices])
    b = np.asarray([triangles[index][1] for index in choices])
    c = np.asarray([triangles[index][2] for index in choices])
    return w0[:, None] * a + w1[:, None] * b + w2[:, None] * c


def standardized_cd(gt_points: np.ndarray, pred_points: np.ndarray, gt_diag: float) -> float | None:
    if len(gt_points) == 0 or len(pred_points) == 0 or gt_diag <= EPS:
        return None
    from scipy.spatial import cKDTree

    gt_tree = cKDTree(gt_points)
    pred_tree = cKDTree(pred_points)
    gt_to_pred = pred_tree.query(gt_points, k=1)[0]
    pred_to_gt = gt_tree.query(pred_points, k=1)[0]
    return float(0.5 * (gt_to_pred.mean() + pred_to_gt.mean()) / gt_diag)


def boolean_iou(gt_shape: Any, gt_feat: dict[str, Any], pred_shape: Any | None, pred_feat: dict[str, Any]) -> dict[str, Any]:
    base = {
        "iou": None,
        "iou_valid": False,
        "iou_status": None,
        "intersection_volume": None,
        "union_volume": None,
        "iou_success_weighted": 0.0,
    }
    if gt_feat.get("status") != "PASS" or not gt_feat.get("valid_solid"):
        base["iou_status"] = "GT_INVALID_SOLID"
        return base
    if pred_feat.get("status") != "PASS":
        base["iou_status"] = "STEP_FAIL"
        return base
    if not pred_feat.get("valid_solid"):
        base["iou_status"] = "PRED_NOT_SOLID"
        return base
    try:
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps

        common_op = BRepAlgoAPI_Common(gt_shape, pred_shape)
        common_op.Build()
        if not common_op.IsDone():
            base["iou_status"] = "COMMON_FAIL"
            return base
        common_shape = common_op.Shape()
        if common_shape is None or common_shape.IsNull():
            base["iou_status"] = "INVALID_INTERSECTION"
            return base

        fuse_op = BRepAlgoAPI_Fuse(gt_shape, pred_shape)
        fuse_op.Build()
        if not fuse_op.IsDone():
            base["iou_status"] = "FUSE_FAIL"
            return base
        union_shape = fuse_op.Shape()
        if union_shape is None or union_shape.IsNull():
            base["iou_status"] = "INVALID_UNION"
            return base
        if not bool(BRepCheck_Analyzer(common_shape).IsValid()):
            base["iou_status"] = "INVALID_INTERSECTION"
            return base
        if not bool(BRepCheck_Analyzer(union_shape).IsValid()):
            base["iou_status"] = "INVALID_UNION"
            return base

        common_props = GProp_GProps()
        union_props = GProp_GProps()
        BRepGProp.VolumeProperties_s(common_shape, common_props)
        BRepGProp.VolumeProperties_s(union_shape, union_props)
        intersection_volume = float(common_props.Mass())
        union_volume = float(union_props.Mass())
        base["intersection_volume"] = intersection_volume
        base["union_volume"] = union_volume
        if not finite(union_volume) or union_volume <= EPS:
            base["iou_status"] = "ZERO_UNION"
            return base
        value = max(0.0, min(1.0, intersection_volume / union_volume))
        base.update({"iou": float(value), "iou_valid": True, "iou_status": "SUCCESS", "iou_success_weighted": float(value)})
        return base
    except Exception as exc:
        base["iou_status"] = f"BOOLEAN_EXCEPTION:{type(exc).__name__}"
        return base


def gt_dsl_path(cad_id: str, base_row: dict[str, Any]) -> Path:
    for arm in ARM_ORDER:
        candidate = ARM_DIRS[arm] / cad_id / "gt.dsl"
        if candidate.exists():
            return candidate
    return ext.gt_dsl_path("A0", base_row)


def op_count_from_row(base_row: dict[str, Any]) -> int:
    ops = base_row.get("gt_ops")
    if isinstance(ops, list):
        return len(ops)
    return 0


def dsl_length(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"\S+", text)), len(text)


def make_rank_terciles(values: dict[str, int | float]) -> tuple[dict[str, str], dict[str, Any]]:
    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    n = len(ordered)
    cuts = (int(math.ceil(n / 3)), int(math.ceil(2 * n / 3)))
    labels: dict[str, str] = {}
    for index, (cad_id, _) in enumerate(ordered):
        labels[cad_id] = "LOW" if index < cuts[0] else "MID" if index < cuts[1] else "HIGH"
    threshold_values = [ordered[max(cuts[0] - 1, 0)][1], ordered[max(cuts[1] - 1, 0)][1]]
    return labels, {
        "assignment": "sort by (GT value, cad_id), then deterministic rank terciles",
        "N": n,
        "rank_cut_indices_1based": [cuts[0], cuts[1]],
        "threshold_values_at_cut": threshold_values,
    }


def complexity_protocol(descriptors: dict[str, dict[str, Any]]) -> dict[str, Any]:
    op_values = {cad_id: item["gt_operation_count"] for cad_id, item in descriptors.items()}
    length_values = {cad_id: item["target_dsl_length_tokens"] for cad_id, item in descriptors.items()}
    _, op_meta = make_rank_terciles(op_values)
    _, length_meta = make_rank_terciles(length_values)
    return {
        "schema_version": "COMPLEXITY_PROTOCOL_V1",
        "frozen_before_arm_statistics": "YES",
        "complexity_source": "GT only; no prediction metric used in tier assignment",
        "operation_count": {"tiers": ["LOW", "MID", "HIGH"], **op_meta},
        "program_length_tokens": {"tiers": ["SHORT", "MEDIUM", "LONG"], **length_meta},
        "boolean_definition": {
            "has_boolean": sorted(BOOLEAN_OPS),
            "tier_labels": ["NO_BOOLEAN", "HAS_BOOLEAN"],
        },
        "curve_K_definition": {
            "source": "frozen curve registry K when available; otherwise GT STEP edge count",
            "tiers": {"LOW": "K <= 8", "MID": "9 <= K <= 32", "HIGH": "K > 32 and K < 128", "CAP": "K >= 128"},
            "cap": 128,
        },
        "source_definition": "dataset field from the frozen VAL1000 report",
    }


def build_descriptors(
    reports: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, Any]],
    gt_features: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    base_rows = {row["id"]: row for row in reports["A0"]["samples"]}
    raw: dict[str, dict[str, Any]] = {}
    for cad_id, row in base_rows.items():
        gt_dsl = gt_dsl_path(cad_id, row)
        tokens, chars = dsl_length(gt_dsl)
        gt_feat = gt_features[cad_id]
        gt_ops = row.get("gt_ops") if isinstance(row.get("gt_ops"), list) else []
        k_value = registry.get(cad_id, {}).get("K")
        k_source = "registry"
        if not finite(k_value):
            k_value = gt_feat.get("curve_n")
            k_source = "gt_step_edge_count"
        k_value = int(k_value or 0)
        boolean_count = sum(1 for op in gt_ops if op in BOOLEAN_OPS)
        raw[cad_id] = {
            "gt_operation_count": len(gt_ops),
            "gt_boolean_count": boolean_count,
            "gt_face_count": int(gt_feat.get("face_n", 0)),
            "gt_edge_count": int(gt_feat.get("edge_n", 0)),
            "gt_curve_K": k_value,
            "curve_K_source": k_source,
            "target_dsl_length_tokens": tokens,
            "target_dsl_length_chars": chars,
            "has_boolean": boolean_count > 0,
            "source": str(row.get("dataset") or "unknown").lower(),
        }
    complexity = complexity_protocol(raw)
    op_tier, _ = make_rank_terciles({cad_id: item["gt_operation_count"] for cad_id, item in raw.items()})
    length_tier, _ = make_rank_terciles({cad_id: item["target_dsl_length_tokens"] for cad_id, item in raw.items()})
    for cad_id, item in raw.items():
        item["operation_complexity"] = op_tier[cad_id]
        item["program_length_complexity"] = {"LOW": "SHORT", "MID": "MEDIUM", "HIGH": "LONG"}[length_tier[cad_id]]
        k = item["gt_curve_K"]
        item["curve_K_complexity"] = "CAP" if k >= 128 else "LOW" if k <= 8 else "MID" if k <= 32 else "HIGH"
        item["boolean_complexity"] = "HAS_BOOLEAN" if item["has_boolean"] else "NO_BOOLEAN"
    return raw, complexity


def case_worker(payload: tuple[str, dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    cad_id, base_row, arm_rows, descriptor = payload
    gt_step = ext.gt_step_path(base_row)
    gt_feat, gt_shape = read_shape_features(gt_step)
    gt_mesh_path = ext.gt_mesh_path(base_row)
    gt_mesh = ext.mesh_bbox(gt_mesh_path) if gt_mesh_path else None
    gt_diag = float((gt_mesh or {}).get("diag") or 1.0)
    gt_points = np.empty((0, 3), dtype=float)
    if gt_shape is not None and gt_feat.get("status") == "PASS":
        gt_points = tessellated_surface_points(gt_shape, N_SURFACE_POINTS, stable_seed(cad_id, "gt_surface"))
    rows: list[dict[str, Any]] = []
    step_reload_rows: list[dict[str, Any]] = []
    for arm in ARM_ORDER:
        row = arm_rows[arm]
        pred_path = ARM_DIRS[arm] / cad_id / "pred.step"
        pred_feat, pred_shape = read_shape_features(pred_path)
        reload_pass = pred_feat.get("status") == "PASS"
        step_reload_rows.append(
            {
                "arm": arm,
                "cad_id": cad_id,
                "sample_id": row.get("sample_id"),
                "dataset": row.get("dataset"),
                "step_path": str(pred_path),
                "reload_status": "PASS" if reload_pass else "FAIL",
                "reload_pass": reload_pass,
                "error": pred_feat.get("error"),
            }
        )
        iou = boolean_iou(gt_shape, gt_feat, pred_shape, pred_feat) if gt_shape is not None else {
            "iou": None,
            "iou_valid": False,
            "iou_status": "GT_INVALID_SOLID",
            "intersection_volume": None,
            "union_volume": None,
            "iou_success_weighted": 0.0,
        }
        cd_value = None
        if reload_pass and pred_shape is not None and len(gt_points) > 0:
            pred_points = tessellated_surface_points(pred_shape, N_SURFACE_POINTS, stable_seed(cad_id, arm, "pred_surface"))
            cd_value = standardized_cd(gt_points, pred_points, gt_diag)
        gt_topo = gt_feat
        pr_topo = pred_feat
        topology_ok = gt_topo.get("status") == "PASS" and pr_topo.get("status") == "PASS"
        placement = {"center_error": None, "extent_error": None, "scale_log_error": None, "bbox_diagonal_ratio_error": None}
        pred_mesh_path = ARM_DIRS[arm] / cad_id / "pred.stl"
        pred_mesh = ext.mesh_bbox(pred_mesh_path) if reload_pass and pred_mesh_path.exists() else None
        if gt_mesh is not None and pred_mesh is not None and gt_diag > EPS:
            placement = ext.placement_metrics(gt_mesh, pred_mesh)
        topo_errors = {}
        for name in ["vertex_n", "edge_n", "wire_n", "face_n", "shell_n", "solid_n", "component_n", "euler_chi"]:
            topo_errors[f"{name}_error"] = (
                abs(int(pr_topo.get(name, 0)) - int(gt_topo.get(name, 0))) if topology_ok else None
            )
        graph = ext.graph_metrics(ext.gt_dsl_path(arm, row), ext.pred_dsl_path(arm, row)) if row.get("parsed") else {}
        geom = row.get("geometry") or {}
        result = {
            "cad_id": cad_id,
            "sample_id": row.get("sample_id"),
            "arm": arm,
            "method": ARM_LABEL[arm],
            "source": descriptor["source"],
            **descriptor,
            "exact": bool(row.get("exact_match")),
            "op_f1": flt(row.get("op_f1")),
            "op_recall": flt(row.get("op_recall")),
            "parsed": bool(row.get("parsed")),
            "step_export_ok": bool(row.get("step_ok")),
            "step_reload": reload_pass,
            "eos": str(row.get("stop_reason") == "EOS"),
            "max_length": str(row.get("stop_reason") == "MAX_LENGTH"),
            "under_generation": bool(row.get("under_generation")),
            "internal_chamfer": flt(geom.get("chamfer_norm")),
            "h95": flt(geom.get("hausdorff_95_norm")),
            "volume_error": flt(geom.get("volume_error")),
            "our_standardized_cd": cd_value,
            "gt_step_status": gt_feat.get("status"),
            "pred_step_status": pred_feat.get("status"),
            "gt_valid_brep": bool(gt_feat.get("valid_brep")),
            "pred_valid_brep": bool(pred_feat.get("valid_brep")) if reload_pass else False,
            "gt_valid_solid": bool(gt_feat.get("valid_solid")),
            "pred_valid_solid": bool(pred_feat.get("valid_solid")) if reload_pass else False,
            "gt_volume": flt(gt_feat.get("volume")),
            "pred_volume": flt(pred_feat.get("volume")) if reload_pass else None,
            "gt_face_n": gt_feat.get("face_n"),
            "pred_face_n": pr_topo.get("face_n") if reload_pass else None,
            "gt_edge_n": gt_feat.get("edge_n"),
            "pred_edge_n": pr_topo.get("edge_n") if reload_pass else None,
            "gt_solid_n": gt_feat.get("solid_n"),
            "pred_solid_n": pr_topo.get("solid_n") if reload_pass else None,
            "gt_component_n": gt_feat.get("component_n"),
            "pred_component_n": pr_topo.get("component_n") if reload_pass else None,
            "closed_solid": bool(
                reload_pass
                and pr_topo.get("valid_solid")
            ),
            "valid_brep": bool(reload_pass and pr_topo.get("valid_brep")),
            "closed_shell": bool(reload_pass and int(pr_topo.get("closed_shell_n", 0)) > 0),
            "pred_curve_n": pr_topo.get("curve_n") if reload_pass else None,
            "gt_curve_n": gt_feat.get("curve_n"),
            "iou_valid": bool(iou["iou_valid"]),
            "iou": iou["iou"],
            "iou_status": iou["iou_status"],
            "iou_success_weighted": iou["iou_success_weighted"],
            "intersection_volume": iou["intersection_volume"],
            "union_volume": iou["union_volume"],
            "dependency_edge_f1": flt(graph.get("dependency_edge_f1")),
            **topo_errors,
            **placement,
        }
        rows.append(result)
    return {"cad_id": cad_id, "rows": rows, "step_reload_rows": step_reload_rows}


def load_partial_results(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            out[item["cad_id"]] = item
    return out


def run_cases(reports: dict[str, dict[str, Any]], descriptors: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_arm = {arm: {row["id"]: row for row in reports[arm]["samples"]} for arm in ARM_ORDER}
    base_rows = {row["id"]: row for row in reports["A0"]["samples"]}
    partial_path = OUT / "case_results.jsonl"
    partial = load_partial_results(partial_path)
    missing_ids = [cad_id for cad_id in sorted(base_rows) if cad_id not in partial]
    if missing_ids:
        mode = "a" if partial_path.exists() else "w"
        workers = max(1, int(os.environ.get("GEOM_BENCH_WORKERS", "4")))
        payloads = [
            (
                cad_id,
                base_rows[cad_id],
                {arm: by_arm[arm][cad_id] for arm in ARM_ORDER},
                descriptors[cad_id],
            )
            for cad_id in missing_ids
        ]
        with partial_path.open(mode, encoding="utf-8") as sink:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(case_worker, payload) for payload in payloads]
                for index, future in enumerate(as_completed(futures), 1):
                    item = future.result()
                    partial[item["cad_id"]] = item
                    sink.write(json.dumps(item, ensure_ascii=False) + "\n")
                    sink.flush()
                    if index % 10 == 0 or index == len(futures):
                        print(f"processed {index}/{len(futures)} new cases", flush=True)
    return [partial[cad_id] for cad_id in sorted(base_rows)]


def bootstrap_ci(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    rng = np.random.default_rng(SEED)
    arr = np.asarray(values, dtype=float)
    batch = 1000
    means = np.empty(BOOTSTRAP_N, dtype=float)
    for start in range(0, BOOTSTRAP_N, batch):
        size = min(batch, BOOTSTRAP_N - start)
        means[start : start + size] = arr[rng.integers(0, len(arr), size=(size, len(arr)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def stats(values: list[float]) -> dict[str, Any]:
    return {
        "valid_N": len(values),
        "mean": mean(values),
        "median": median(values),
        "p75": percentile(values, 75),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": max(values) if values else None,
    }


def flatten_results(case_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in case_results:
        rows.extend(item["rows"])
    return rows


def iou_summaries(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summaries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for arm in ARM_ORDER:
        arm_rows = [row for row in rows if row["arm"] == arm]
        valid_values = value_list(arm_rows, "iou")
        weighted = value_list(arm_rows, "iou_success_weighted")
        status_counts = Counter(str(row["iou_status"]) for row in arm_rows)
        summaries.append(
            {
                "arm": arm,
                "method": ARM_LABEL[arm],
                "IOU_VALID_ONLY_MEAN": mean(valid_values),
                "IOU_VALID_ONLY_MEDIAN": median(valid_values),
                "IOU_VALID_N": len(valid_values),
                "IOU_SUCCESS_WEIGHTED": mean(weighted),
                "TOTAL_N": len(arm_rows),
                "failure_rate": 1.0 - len(valid_values) / max(len(arm_rows), 1),
                "status_counts": dict(status_counts),
            }
        )
        for row in arm_rows:
            if row["iou_status"] != "SUCCESS":
                failures.append(
                    {
                        "arm": arm,
                        "cad_id": row["cad_id"],
                        "dataset": row["source"],
                        "iou_status": row["iou_status"],
                        "step_reload": row["step_reload"],
                        "pred_valid_brep": row["pred_valid_brep"],
                        "pred_valid_solid": row["pred_valid_solid"],
                    }
                )
    return summaries, failures


def cd_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for arm in ARM_ORDER:
        values = value_list([row for row in rows if row["arm"] == arm], "our_standardized_cd")
        out.append({"arm": arm, "method": ARM_LABEL[arm], "CD_PROTOCOL": "OUR_STANDARDIZED_CD", **stats(values)})
    return out


def topology_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for arm in ARM_ORDER:
        arm_rows = [row for row in rows if row["arm"] == arm]
        out.append(
            {
                "arm": arm,
                "method": ARM_LABEL[arm],
                "N": len(arm_rows),
                "STEP_Reload": mean([float(row["step_reload"]) for row in arm_rows]),
                "VALID_BREP_N": sum(bool(row["valid_brep"]) for row in arm_rows),
                "VALID_BREP_RATE": mean([float(row["valid_brep"]) for row in arm_rows]),
                "CLOSED_SOLID_N": sum(bool(row["closed_solid"]) for row in arm_rows),
                "CLOSED_SOLID_RATE": mean([float(row["closed_solid"]) for row in arm_rows]),
                "FACE_COUNT_ERROR_VALID_MEAN": mean(value_list(arm_rows, "face_n_error")),
                "EDGE_COUNT_ERROR_VALID_MEAN": mean(value_list(arm_rows, "edge_n_error")),
                "SOLID_COUNT_ERROR_VALID_MEAN": mean(value_list(arm_rows, "solid_n_error")),
                "CONNECTED_COMPONENT_COUNT_ERROR_VALID_MEAN": mean(value_list(arm_rows, "component_n_error")),
                "EULER_ERROR_VALID_MEAN": mean(value_list(arm_rows, "euler_chi_error")),
            }
        )
    return out


def pair_rows(rows: list[dict[str, Any]], baseline: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {(row["arm"], row["cad_id"]): row for row in rows}
    case_rows: list[dict[str, Any]] = []
    boot_rows: list[dict[str, Any]] = []
    metrics = [
        ("IoU", "iou", "higher"),
        ("CD", "our_standardized_cd", "lower"),
        ("H95", "h95", "lower"),
        ("Volume", "volume_error", "lower"),
        ("Face_Count_Error", "face_n_error", "lower"),
        ("Edge_Count_Error", "edge_n_error", "lower"),
    ]
    for cad_id in sorted({row["cad_id"] for row in rows}):
        b = by_id[(baseline, cad_id)]
        p = by_id[("P1", cad_id)]
        item: dict[str, Any] = {"cad_id": cad_id, "dataset": p["source"], "baseline": baseline}
        for label, field, direction in metrics:
            bv, pv = flt(b.get(field)), flt(p.get(field))
            item[f"{baseline}_{label}"] = bv
            item[f"P1_{label}"] = pv
            item[f"P1_minus_{baseline}_{label}"] = pv - bv if bv is not None and pv is not None else None
            if bv is None or pv is None:
                item[f"P1_better_{label}"] = None
            elif abs(pv - bv) <= EPS:
                item[f"P1_better_{label}"] = False
            else:
                item[f"P1_better_{label}"] = (pv > bv) if direction == "higher" else (pv < bv)
        item["P1_STEP_RELOAD"] = p["step_reload"]
        item[f"{baseline}_STEP_RELOAD"] = b["step_reload"]
        item["P1_IOU_STATUS"] = p["iou_status"]
        item[f"{baseline}_IOU_STATUS"] = b["iou_status"]
        case_rows.append(item)
    for label, field, direction in metrics:
        pairs = [
            row
            for row in case_rows
            if finite(row[f"{baseline}_{label}"]) and finite(row[f"P1_{label}"])
        ]
        deltas = [float(row[f"P1_minus_{baseline}_{label}"]) for row in pairs]
        lo, hi = bootstrap_ci(deltas)
        p1_better = sum(bool(row[f"P1_better_{label}"]) for row in pairs)
        baseline_better = len(pairs) - p1_better - sum(abs(float(row[f"P1_minus_{baseline}_{label}"])) <= EPS for row in pairs)
        boot_rows.append(
            {
                "comparison": f"P1_vs_{baseline}",
                "metric": label,
                "paired_N": len(pairs),
                "baseline_mean": mean([float(row[f"{baseline}_{label}"]) for row in pairs]),
                "P1_mean": mean([float(row[f"P1_{label}"]) for row in pairs]),
                "delta_P1_minus_baseline": mean(deltas),
                "bootstrap_CI95_low": lo,
                "bootstrap_CI95_high": hi,
                "P1_better_N": p1_better,
                "tie_N": sum(abs(float(row[f"P1_minus_{baseline}_{label}"])) <= EPS for row in pairs),
                "baseline_better_N": baseline_better,
                "direction": direction,
            }
        )
    return case_rows, boot_rows


def classify_geometry_pair(pair: dict[str, Any], baseline: str, by_id: dict[tuple[str, str], dict[str, Any]]) -> tuple[str | None, str]:
    metric_labels = ["IoU", "CD", "H95", "Volume"]
    better = [pair.get(f"P1_better_{label}") for label in metric_labels]
    available = [value for value in better if value is not None]
    worse = [value is False for value in available]
    wins = sum(bool(value) for value in available)
    losses = sum(worse)
    baseline_row = by_id[(baseline, pair["cad_id"])]
    p1_row = by_id[("P1", pair["cad_id"])]
    rescue = (
        (baseline_row["iou_status"] != "SUCCESS" and p1_row["iou_status"] == "SUCCESS")
        or (wins >= 2 and wins > losses)
    )
    regression = (
        (baseline_row["iou_status"] == "SUCCESS" and p1_row["iou_status"] != "SUCCESS")
        or (losses >= 2 and losses > wins)
    )
    if not rescue and not regression:
        return None, "tie_or_insufficient"
    if baseline_row["iou_status"] in {"COMMON_FAIL", "FUSE_FAIL", "INVALID_INTERSECTION", "INVALID_UNION", "ZERO_UNION"}:
        category = "boolean_error"
    elif baseline_row["step_reload"] and not p1_row["step_reload"]:
        category = "topology_error"
    elif (
        finite(baseline_row.get("center_error"))
        and finite(p1_row.get("center_error"))
        and float(p1_row["center_error"]) < float(baseline_row["center_error"])
    ):
        category = "placement_error"
    elif (
        finite(baseline_row.get("scale_log_error"))
        and finite(p1_row.get("scale_log_error"))
        and float(p1_row["scale_log_error"]) < float(baseline_row["scale_log_error"])
    ):
        category = "scale_error"
    elif (
        finite(baseline_row.get("op_f1"))
        and finite(p1_row.get("op_f1"))
        and float(p1_row["op_f1"]) > float(baseline_row["op_f1"])
    ):
        category = "operation_error"
    elif (
        finite(baseline_row.get("face_n_error"))
        and finite(p1_row.get("face_n_error"))
        and float(p1_row["face_n_error"]) > float(baseline_row["face_n_error"])
    ):
        category = "topology_error"
    else:
        category = "unknown"
    state = "RESCUE" if rescue and not regression else "REGRESSION" if regression and not rescue else "MIXED"
    return category, f"{state}:{wins}_wins_{losses}_losses_{len(available)}_available"


def write_rescues_and_regressions(rows: list[dict[str, Any]], baseline: str, pairs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {(row["arm"], row["cad_id"]): row for row in rows}
    rescues: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []
    for pair in pairs:
        category, reason = classify_geometry_pair(pair, baseline, by_id)
        if category is None:
            continue
        payload = dict(pair)
        payload["failure_category"] = category
        payload["classification"] = reason
        if reason.startswith("RESCUE"):
            rescues.append(payload)
        elif reason.startswith("REGRESSION"):
            regressions.append(payload)
    return rescues, regressions


def complexity_table(rows: list[dict[str, Any]], group_field: str, group_labels: list[str], breakdown_type: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for group in group_labels:
        for arm in ARM_ORDER:
            subset = [row for row in rows if row["arm"] == arm and row.get(group_field) == group]
            out.append(
                {
                    "Breakdown": breakdown_type,
                    "Complexity": group,
                    "Method": arm,
                    "N": len(subset),
                    "Op-F1": mean(value_list(subset, "op_f1")),
                    "STEP Reload": mean([float(row["step_reload"]) for row in subset]),
                    "IoU": mean(value_list(subset, "iou")),
                    "IoU Success Weighted": mean(value_list(subset, "iou_success_weighted")),
                    "Mean CD": mean(value_list(subset, "our_standardized_cd")),
                    "Median CD": median(value_list(subset, "our_standardized_cd")),
                    "H95": mean(value_list(subset, "h95")),
                    "Volume": mean(value_list(subset, "volume_error")),
                }
            )
    return out


def source_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for source in ["deepcad", "fusion360"]:
        for arm in ARM_ORDER:
            subset = [row for row in rows if row["arm"] == arm and row["source"] == source]
            out.append(
                {
                    "Source": source,
                    "Method": arm,
                    "N": len(subset),
                    "Exact": mean([float(row["exact"]) for row in subset]),
                    "Op-F1": mean(value_list(subset, "op_f1")),
                    "STEP Reload": mean([float(row["step_reload"]) for row in subset]),
                    "IoU": mean(value_list(subset, "iou")),
                    "Mean CD": mean(value_list(subset, "our_standardized_cd")),
                    "Median CD": median(value_list(subset, "our_standardized_cd")),
                    "H95": mean(value_list(subset, "h95")),
                    "Volume": mean(value_list(subset, "volume_error")),
                }
            )
    return out


def outlier_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    p1 = sorted(
        [row for row in rows if row["arm"] == "P1" and finite(row.get("our_standardized_cd"))],
        key=lambda row: float(row["our_standardized_cd"]),
        reverse=True,
    )
    total = sum(float(row["our_standardized_cd"]) for row in p1)
    top = p1[:20]
    return [
        {
            "rank": index,
            "cad_id": row["cad_id"],
            "dataset": row["source"],
            "P1_OUR_STANDARDIZED_CD": row["our_standardized_cd"],
            "contribution_to_valid_cd_sum": float(row["our_standardized_cd"]) / total if total > EPS else None,
            "P1_H95": row["h95"],
            "P1_Volume_Error": row["volume_error"],
            "P1_IoU": row["iou"],
            "P1_IoU_Status": row["iou_status"],
        }
        for index, row in enumerate(top, 1)
    ]


def make_gallery(
    path: Path,
    rows: list[dict[str, Any]],
    a3_rescues: list[dict[str, Any]],
    a3_regressions: list[dict[str, Any]],
) -> dict[str, Any]:
    from PIL import Image, ImageDraw, ImageFont

    def pick(items: list[dict[str, Any]], key: str = "cad_id") -> dict[str, Any] | None:
        return sorted(items, key=lambda item: str(item.get(key, "")))[0] if items else None

    iou_rescues = [item for item in a3_rescues if item.get("P1_IoU") is not None and item.get("A3_IoU") is None]
    boolean_rescues = [
        item
        for item in a3_rescues
        if str(item.get("A3_IOU_STATUS", "")).startswith(("COMMON_FAIL", "FUSE_FAIL", "INVALID_"))
    ]
    step_rescues = [
        item
        for item in a3_rescues
        if item.get("A3_STEP_RELOAD") is False and item.get("P1_STEP_RELOAD") is True
    ]
    cd_regressions = [item for item in a3_regressions if finite(item.get("P1_CD")) and finite(item.get("A3_CD"))]
    cd_regressions = sorted(cd_regressions, key=lambda item: float(item["P1_minus_A3_CD"]), reverse=True)
    selections = {
        "P1_IOU_RESCUE": pick(iou_rescues),
        "P1_BOOLEAN_RESCUE": pick(boolean_rescues),
        "P1_STEP_RESCUE": pick(step_rescues),
        "P1_CD_REGRESSION": cd_regressions[0] if cd_regressions else None,
    }
    image = Image.new("RGB", (2200, 1300), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
    draw.text((50, 35), "EXACT9998 A0/A1/A2/A3/P1 Geometric Effectiveness", fill=(20, 20, 20), font=font)
    panels = [
        ("P1 IoU rescue", selections["P1_IOU_RESCUE"]),
        ("P1 boolean rescue", selections["P1_BOOLEAN_RESCUE"]),
        ("P1 STEP rescue", selections["P1_STEP_RESCUE"]),
        ("P1 CD regression", selections["P1_CD_REGRESSION"]),
    ]
    positions = [(50, 130), (1120, 130), (50, 700), (1120, 700)]
    for (title, item), (x, y) in zip(panels, positions):
        draw.rectangle((x, y, x + 1000, y + 450), outline=(190, 190, 190), width=3)
        draw.text((x + 25, y + 25), title, fill=(30, 30, 30), font=font)
        if item is None:
            draw.text((x + 25, y + 95), "No qualifying case", fill=(90, 90, 90), font=body)
            continue
        lines = [
            f"cad_id: {item.get('cad_id')}",
            f"A3 IoU/status: {item.get('A3_IoU')} / {item.get('A3_IOU_STATUS')}",
            f"P1 IoU/status: {item.get('P1_IoU')} / {item.get('P1_IOU_STATUS')}",
            f"A3 CD -> P1 CD: {item.get('A3_CD')} -> {item.get('P1_CD')}",
            f"A3 H95 -> P1 H95: {item.get('A3_H95')} -> {item.get('P1_H95')}",
            f"A3 Vol -> P1 Vol: {item.get('A3_Volume')} -> {item.get('P1_Volume')}",
            f"class: {item.get('failure_category')} / {item.get('classification')}",
        ]
        for offset, line in enumerate(lines):
            draw.text((x + 25, y + 95 + offset * 43), line[: eighty_chars()], fill=(55, 55, 55), font=body)
    image.save(path)
    return selections


def eighty_chars() -> int:
    return 110


def protocol_json(complexity: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "GEOMETRIC_EFFECTIVENESS_PROTOCOL_V1",
        "benchmark": "A0_A1_A2_A3_P1_GEOMETRIC_EFFECTIVENESS_BENCH_V1",
        "input_split": "EXACT9998 VAL1000 only",
        "test_policy": "TEST1000 remains blind; no forward/decode/parse/execute/STEP/geometry/metrics.",
        "arms": {arm: ARM_LABEL[arm] for arm in ARM_ORDER},
        "shared_rules": {
            "same_code": "All five arms are evaluated by this script and the same frozen helper functions.",
            "same_normalization": "GT mesh bounding-box diagonal for every normalized distance metric.",
            "same_failure_rule": "Invalid/missing STEP or invalid solid is NA for valid-only metrics and zero for IoU success-weighted score.",
            "same_denominator": "TOTAL_N=1000 for coverage and success-weighted IoU; valid-only metrics report explicit valid N.",
        },
        "iou": {
            "definition": "B-Rep volumetric IoU = Volume(Common(GT, Pred)) / Volume(Fuse(GT, Pred)).",
            "validity": "GT and prediction must both be valid OCC B-Reps with at least one solid, a closed shell, and positive volume.",
            "valid_only_fields": ["IOU_VALID_ONLY_MEAN", "IOU_VALID_ONLY_MEDIAN", "IOU_VALID_N"],
            "success_weighted_field": "IOU_SUCCESS_WEIGHTED; invalid/failed cases contribute zero.",
            "failure_statuses": [
                "GT_INVALID_SOLID",
                "STEP_FAIL",
                "PRED_NOT_SOLID",
                "COMMON_FAIL",
                "FUSE_FAIL",
                "INVALID_INTERSECTION",
                "INVALID_UNION",
                "ZERO_UNION",
            ],
            "boolean_robustness": "Every case records one status; failures are not silently dropped.",
        },
        "cd": {
            "status": "OUR_STANDARDIZED_CD",
            "paper_compatibility": "NOT_OFFICIALLY_VERIFIED",
            "definition": "Symmetric unsquared Euclidean Chamfer on deterministic surface samples from GT and Pred STEP.",
            "tessellation_tolerance": TESSELLATION_TOLERANCE,
            "surface_sampling_count": N_SURFACE_POINTS,
            "sampling": "OCC tessellation with identical tolerance, then deterministic area-weighted triangle sampling.",
            "normalization": "GT mesh bounding-box diagonal.",
            "formula": "0.5 * (mean_x min_y ||x-y|| + mean_y min_x ||y-x||) / GT_bbox_diag.",
            "squared": False,
            "symmetric": True,
        },
        "h95": {
            "status": "EXISTING_FORMAL_EVALUATOR_DEFINITION_REUSED",
            "source_field": "report.samples[].geometry.hausdorff_95_norm",
        },
        "volume_error": {
            "status": "EXISTING_FORMAL_EVALUATOR_DEFINITION_REUSED",
            "source_field": "report.samples[].geometry.volume_error",
        },
        "step_reload": {
            "definition": "Direct OCC STEPControl_Reader read + TransferRoots + non-null shape; topology validity is reported separately.",
            "p1_audit": "P1_STEP_RELOAD_AUDIT.csv",
        },
        "topology": {
            "valid_brep": "OCC BRepCheck_Analyzer(shape).IsValid().",
            "closed_solid": "Valid B-Rep with solid_n > 0, closed_shell_n > 0, and positive volume.",
            "counts": ["face_n", "edge_n", "solid_n", "component_n", "euler_chi"],
        },
        "ged": {
            "status": "DEFERRED_UNDEFINED",
            "reason": "No official project-local paper/evaluator definition was found; dependency-edge F1 is not renamed as GED.",
        },
        "complexity": complexity,
        "paired_statistics": {
            "unit": "CAD case",
            "bootstrap_replicates": BOOTSTRAP_N,
            "seed": SEED,
            "confidence_interval": "percentile 95% CI",
        },
        "rescue_regression_policy": {
            "rescue": "Baseline IoU failure with P1 IoU success, or P1 wins at least two of IoU/CD/H95/Volume and has more wins than losses.",
            "regression": "Symmetric definition.",
            "failure_categories": [
                "operation_error",
                "boolean_error",
                "parameter_error",
                "placement_error",
                "scale_error",
                "topology_error",
                "fragmentation",
                "unknown",
            ],
            "category_note": "Categories are diagnostic heuristics frozen before reading aggregate arm results.",
        },
    }


def final_report(
    reports: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
    iou_summary: list[dict[str, Any]],
    cd_summary: list[dict[str, Any]],
    topo_summary: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    complexity_rows: list[dict[str, Any]],
    selections: dict[str, Any],
) -> dict[str, Any]:
    by_arm = {arm: [row for row in rows if row["arm"] == arm] for arm in ARM_ORDER}
    by_iou = {row["arm"]: row for row in iou_summary}
    by_cd = {row["arm"]: row for row in cd_summary}
    by_topo = {row["arm"]: row for row in topo_summary}

    def lower(field: str, arm: str) -> float | None:
        return mean(value_list(by_arm[arm], field))

    def higher(field: str, arm: str) -> float | None:
        return mean(value_list(by_arm[arm], field))

    a3_boot = {(row["metric"]): row for row in bootstrap_rows if row["comparison"] == "P1_vs_A3"}
    vol_wins = sum(
        [
            float(by_iou["P1"]["IOU_SUCCESS_WEIGHTED"] or 0.0) > float(by_iou["A3"]["IOU_SUCCESS_WEIGHTED"] or 0.0),
            float(lower("h95", "P1") or 1e9) < float(lower("h95", "A3") or 1e9),
            float(lower("volume_error", "P1") or 1e9) < float(lower("volume_error", "A3") or 1e9),
        ]
    )
    surface_wins = sum(
        [
            float(by_cd["P1"]["mean"] or 1e9) < float(by_cd["A3"]["mean"] or 1e9),
            float(by_cd["P1"]["median"] or 1e9) < float(by_cd["A3"]["median"] or 1e9),
        ]
    )
    topology_wins = sum(
        [
            float(by_topo["P1"]["VALID_BREP_RATE"] or 0.0) > float(by_topo["A3"]["VALID_BREP_RATE"] or 0.0),
            float(by_topo["P1"]["CLOSED_SOLID_RATE"] or 0.0) > float(by_topo["A3"]["CLOSED_SOLID_RATE"] or 0.0),
            float(by_topo["P1"]["FACE_COUNT_ERROR_VALID_MEAN"] or 1e9) < float(by_topo["A3"]["FACE_COUNT_ERROR_VALID_MEAN"] or 1e9),
            float(by_topo["P1"]["EDGE_COUNT_ERROR_VALID_MEAN"] or 1e9) < float(by_topo["A3"]["EDGE_COUNT_ERROR_VALID_MEAN"] or 1e9),
        ]
    )
    high_rows = [row for row in complexity_rows if row["Breakdown"] == "GT_OPERATION_COUNT" and row["Complexity"] == "HIGH"]
    high = {row["Method"]: row for row in high_rows}
    complex_wins = sum(
        [
            float(high.get("P1", {}).get("IoU Success Weighted") or 0.0) > float(high.get("A3", {}).get("IoU Success Weighted") or 0.0),
            float(high.get("P1", {}).get("H95") or 1e9) < float(high.get("A3", {}).get("H95") or 1e9),
            float(high.get("P1", {}).get("Volume") or 1e9) < float(high.get("A3", {}).get("Volume") or 1e9),
        ]
    )
    program_adv = (
        float(reports["P1"]["mean_op_f1"]) > float(reports["A3"]["mean_op_f1"])
        and float(reports["P1"]["exact_match_rate"]) > float(reports["A3"]["exact_match_rate"])
    )
    volumetric_status = "YES" if vol_wins >= 2 else "PARTIAL" if vol_wins == 1 else "NO"
    surface_status = "YES" if surface_wins == 2 else "PARTIAL" if surface_wins == 1 else "NO"
    topology_status = "YES" if topology_wins >= 3 else "PARTIAL" if topology_wins >= 1 else "NO"
    complex_status = "YES" if complex_wins >= 2 else "PARTIAL" if complex_wins == 1 else "NO"
    main_score = sum(
        [
            program_adv,
            bool(float(by_iou["P1"]["IOU_SUCCESS_WEIGHTED"] or 0.0) > float(by_iou["A3"]["IOU_SUCCESS_WEIGHTED"] or 0.0)),
            bool(float(lower("h95", "P1") or 1e9) < float(lower("h95", "A3") or 1e9)),
            bool(float(lower("volume_error", "P1") or 1e9) < float(lower("volume_error", "A3") or 1e9)),
            bool(by_topo["P1"]["VALID_BREP_RATE"] > by_topo["A3"]["VALID_BREP_RATE"]),
        ]
    )
    p1_status = "CURRENT_MAIN_METHOD" if main_score >= 3 else "PROGRAM_STRUCTURAL_MAIN_METHOD_WITH_GEOMETRY_TRADEOFF"
    return {
        "CURRENT_GATE": "A0_A1_A2_A3_P1_GEOMETRIC_EFFECTIVENESS_BENCH_V1_COMPLETE",
        "TEST_TOUCHED": "NO",
        "GED_STATUS": "DEFERRED_UNDEFINED",
        "IOU": {
            f"{arm}_IOU_VALID_ONLY_MEAN": by_iou[arm]["IOU_VALID_ONLY_MEAN"] for arm in ARM_ORDER
        }
        | {f"{arm}_IOU_VALID_ONLY_MEDIAN": by_iou[arm]["IOU_VALID_ONLY_MEDIAN"] for arm in ARM_ORDER}
        | {f"{arm}_IOU_VALID_N": by_iou[arm]["IOU_VALID_N"] for arm in ARM_ORDER}
        | {f"{arm}_IOU_SUCCESS_WEIGHTED": by_iou[arm]["IOU_SUCCESS_WEIGHTED"] for arm in ARM_ORDER},
        "P1_VS_A3_IOU_DELTA": a3_boot.get("IoU", {}).get("delta_P1_minus_baseline"),
        "P1_VS_A3_IOU_CI": [
            a3_boot.get("IoU", {}).get("bootstrap_CI95_low"),
            a3_boot.get("IoU", {}).get("bootstrap_CI95_high"),
        ],
        "CD": {
            f"{arm}_MEAN_CD": by_cd[arm]["mean"] for arm in ARM_ORDER
        }
        | {f"{arm}_MEDIAN_CD": by_cd[arm]["median"] for arm in ARM_ORDER}
        | {f"{arm}_CD_VALID_N": by_cd[arm]["valid_N"] for arm in ARM_ORDER},
        "BEST_MEAN_CD_ARM": min(ARM_ORDER, key=lambda arm: by_cd[arm]["mean"] if by_cd[arm]["mean"] is not None else float("inf")),
        "BEST_MEDIAN_CD_ARM": min(ARM_ORDER, key=lambda arm: by_cd[arm]["median"] if by_cd[arm]["median"] is not None else float("inf")),
        "EXECUTION": {f"{arm}_STEP_RELOAD": by_topo[arm]["STEP_Reload"] for arm in ARM_ORDER},
        "TOPOLOGY": {
            f"{arm}_VALID_BREP": by_topo[arm]["VALID_BREP_RATE"] for arm in ARM_ORDER
        }
        | {f"{arm}_CLOSED_SOLID": by_topo[arm]["CLOSED_SOLID_RATE"] for arm in ARM_ORDER},
        "COMPLEXITY": {
            "LOW_COMPLEXITY_BEST_ARM": best_group_arm(complexity_rows, "GT_OPERATION_COUNT", "LOW", "IoU Success Weighted", higher=True),
            "MID_COMPLEXITY_BEST_ARM": best_group_arm(complexity_rows, "GT_OPERATION_COUNT", "MID", "IoU Success Weighted", higher=True),
            "HIGH_COMPLEXITY_BEST_ARM": best_group_arm(complexity_rows, "GT_OPERATION_COUNT", "HIGH", "IoU Success Weighted", higher=True),
            "BOOLEAN_CASE_BEST_ARM": best_group_arm(complexity_rows, "BOOLEAN", "HAS_BOOLEAN", "IoU Success Weighted", higher=True),
            "LONG_PROGRAM_BEST_ARM": best_group_arm(complexity_rows, "PROGRAM_LENGTH", "LONG", "IoU Success Weighted", higher=True),
        },
        "P1_EFFECT": {
            "P1_PROGRAM_ADVANTAGE": "YES" if program_adv else "NO",
            "P1_VOLUMETRIC_ADVANTAGE": volumetric_status,
            "P1_SURFACE_ADVANTAGE": surface_status,
            "P1_TOPOLOGY_ADVANTAGE": topology_status,
            "P1_COMPLEX_CAD_ADVANTAGE": complex_status,
        },
        "INTERPRETATION": {
            "PROGRAM_CONCLUSION": "P1 improves program-level exactness and operation F1 over A3." if program_adv else "P1 does not dominate A3 on both exactness and operation F1.",
            "GEOMETRY_CONCLUSION": f"P1 volumetric/structural geometry status is {volumetric_status}; standardized surface CD status is {surface_status}.",
            "COMPLEXITY_CONCLUSION": f"On GT high-operation cases, P1 complexity advantage is {complex_status}.",
            "CROSS_PAPER_COMPARABILITY": "NO",
            "P1_STATUS": p1_status,
        },
        "GALLERY_SELECTION": selections,
        "INTEGRITY": {
            "A0_CHANGED": "NO",
            "A1_CHANGED": "NO",
            "A2_CHANGED": "NO",
            "A3_CHANGED": "NO",
            "P1_CHANGED": "NO",
            "PREDICTIONS_CHANGED": "NO",
            "EVALUATOR_V2_CHANGED": "NO",
            "GT_CHANGED": "NO",
            "NEW_DECODE_RUN": "NO",
            "NEW_TRAIN_RUN": "NO",
            "TEST_TOUCHED": "NO",
        },
    }


def best_group_arm(table: list[dict[str, Any]], breakdown: str, group: str, field: str, higher: bool) -> str | None:
    rows = [row for row in table if row.get("Breakdown") == breakdown and row.get("Complexity") == group and finite(row.get(field))]
    if not rows:
        return None
    return (max if higher else min)(rows, key=lambda row: float(row[field]))["Method"]


def final_markdown(
    report: dict[str, Any],
    iou_summary: list[dict[str, Any]],
    cd_summary: list[dict[str, Any]],
    topo_summary: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> str:
    lines = [
        "# A0/A1/A2/A3/P1 Geometric Effectiveness Benchmark",
        "",
        f"CURRENT_GATE = `{report['CURRENT_GATE']}`",
        f"TEST_TOUCHED = `{report['TEST_TOUCHED']}`",
        f"GED_STATUS = `{report['GED_STATUS']}`",
        f"P1_STATUS = `{report['INTERPRETATION']['P1_STATUS']}`",
        "",
        "## Headline",
        "",
        "| Method | IoU valid-only | IoU success-weighted | IoU N | Our standardized CD | CD N | H95 | Volume error | STEP Reload | Valid BRep | Closed Solid |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    cd_by = {row["arm"]: row for row in cd_summary}
    topo_by = {row["arm"]: row for row in topo_summary}
    for row in iou_summary:
        arm = row["arm"]
        arm_rows = [item for item in rows if item["arm"] == arm]
        lines.append(
            f"| {arm} | {fmt(row['IOU_VALID_ONLY_MEAN'])} | {fmt(row['IOU_SUCCESS_WEIGHTED'])} | {row['IOU_VALID_N']} | "
            f"{fmt(cd_by[arm]['mean'])} | {cd_by[arm]['valid_N']} | {fmt(mean(value_list(arm_rows, 'h95')))} | "
            f"{fmt(mean(value_list(arm_rows, 'volume_error')))} | {fmt(topo_by[arm]['STEP_Reload'])} | "
            f"{fmt(topo_by[arm]['VALID_BREP_RATE'])} | {fmt(topo_by[arm]['CLOSED_SOLID_RATE'])} |"
        )
    lines.extend(
        [
            "",
            "## Conclusions",
            "",
            f"- Program: {report['INTERPRETATION']['PROGRAM_CONCLUSION']}",
            f"- Geometry: {report['INTERPRETATION']['GEOMETRY_CONCLUSION']}",
            f"- Complexity: {report['INTERPRETATION']['COMPLEXITY_CONCLUSION']}",
            f"- Cross-paper comparison: `{report['INTERPRETATION']['CROSS_PAPER_COMPARABILITY']}` because CD and B-Rep IoU are frozen project-standardized metrics, not officially verified paper evaluator replicas.",
            "",
            "## Deferred",
            "",
            "- GED is `DEFERRED_UNDEFINED`; the existing dependency graph F1 is not relabeled as GED.",
            "- Normal consistency and manifold rate are not reported because a reliable shared implementation was not frozen.",
            "",
        ]
    )
    return "\n".join(lines)


def fmt(value: Any) -> str:
    return "NA" if value is None or value == "" else f"{float(value):.6f}" if finite(value) else str(value)


def run() -> dict[str, Any]:
    ensure_dirs()
    reports = load_reports()
    registry = load_registry()
    base_rows = {row["id"]: row for row in reports["A0"]["samples"]}

    # Freeze descriptors and thresholds from GT before computing arm aggregates.
    gt_features: dict[str, dict[str, Any]] = {}
    for index, (cad_id, row) in enumerate(sorted(base_rows.items()), 1):
        feat, _ = read_shape_features(ext.gt_step_path(row))
        gt_features[cad_id] = feat
        if index % 100 == 0:
            print(f"loaded GT topology {index}/{N_CASES}", flush=True)
    descriptors, complexity = build_descriptors(reports, registry, gt_features)
    protocol = protocol_json(complexity)
    json_dump(OUT / "protocol/GEOMETRIC_EFFECTIVENESS_PROTOCOL_V1.json", protocol)
    json_dump(
        OUT / "cd/CD_DEFINITION_AUDIT.json",
        {
            "status": "OUR_STANDARDIZED_CD",
            "paper_compatible_status": "NOT_OFFICIALLY_VERIFIED",
            "protocol_path": str(OUT / "protocol/GEOMETRIC_EFFECTIVENESS_PROTOCOL_V1.json"),
            "definition": protocol["cd"],
            "current_internal_chamfer_is_preserved_separately": True,
        },
    )
    json_dump(
        OUT / "ged/GED_DEFINITION_AUDIT.json",
        {
            "GED_STATUS": "DEFERRED_UNDEFINED",
            "search_scope": [
                str(EXT_DIR),
                str(ROOT / "ours3/exact9998_v1"),
                str(ROOT / "ours3/remote_extended_cad_metrics.py"),
            ],
            "finding": "No official project-local paper/evaluator definition for Graph Edit Distance, Geometric Edit Distance, or Geometry Edit Distance was found. Existing evaluator explicitly defers normalized graph edit distance.",
            "prohibition": "Operation dependency graph F1 is retained under its own name and is not called GED.",
        },
    )
    json_dump(OUT / "complexity/COMPLEXITY_PROTOCOL.json", complexity)

    case_results = run_cases(reports, descriptors)
    rows = flatten_results(case_results)
    reload_rows = [row for item in case_results for row in item["step_reload_rows"] if row["arm"] == "P1"]
    csv_dump(
        OUT / "step_reload/P1_STEP_RELOAD_AUDIT.csv",
        reload_rows,
        ["arm", "cad_id", "sample_id", "dataset", "step_path", "reload_status", "reload_pass", "error"],
    )
    csv_dump(OUT / "iou/IOU_CASE_METRICS.csv", rows)
    iou_summary, iou_failures = iou_summaries(rows)
    csv_dump(OUT / "iou/IOU_SUMMARY.csv", iou_summary)
    csv_dump(OUT / "iou/IOU_FAILURES.csv", iou_failures)
    csv_dump(OUT / "cd/CD_CASE_METRICS.csv", rows)
    cd_summary = cd_summaries(rows)
    csv_dump(OUT / "cd/CD_SUMMARY.csv", cd_summary)

    ged_summary = [
        {
            "GED_STATUS": "DEFERRED_UNDEFINED",
            "GED": None,
            "reason": "No official definition/evaluator confirmed; dependency graph F1 remains separate.",
        }
    ]
    csv_dump(OUT / "ged/GED_SUMMARY.csv", ged_summary)
    topo_summary = topology_summaries(rows)
    csv_dump(OUT / "topology/TOPOLOGY_SUMMARY.csv", topo_summary)

    complexity_detail = rows
    csv_dump(OUT / "complexity/COMPLEXITY_BREAKDOWN.csv", complexity_detail)
    complexity_rows = []
    complexity_rows.extend(complexity_table(rows, "operation_complexity", ["LOW", "MID", "HIGH"], "GT_OPERATION_COUNT"))
    complexity_rows.extend(complexity_table(rows, "program_length_complexity", ["SHORT", "MEDIUM", "LONG"], "PROGRAM_LENGTH"))
    complexity_rows.extend(complexity_table(rows, "boolean_complexity", ["NO_BOOLEAN", "HAS_BOOLEAN"], "BOOLEAN"))
    complexity_rows.extend(complexity_table(rows, "curve_K_complexity", ["LOW", "MID", "HIGH", "CAP"], "CURVE_K"))
    csv_dump(OUT / "complexity/BOOLEAN_COMPLEXITY.csv", [row for row in complexity_rows if row["Breakdown"] == "BOOLEAN"])
    csv_dump(OUT / "complexity/CURVE_K_BREAKDOWN.csv", [row for row in complexity_rows if row["Breakdown"] == "CURVE_K"])
    csv_dump(OUT / "complexity/SOURCE_BREAKDOWN.csv", source_table(rows))

    a3_pairs, a3_boot = pair_rows(rows, "A3")
    a1_pairs, a1_boot = pair_rows(rows, "A1")
    csv_dump(OUT / "paired/P1_VS_A3_GEOMETRY_PAIRED.csv", a3_pairs)
    csv_dump(OUT / "paired/P1_VS_A1_GEOMETRY_PAIRED.csv", a1_pairs)
    csv_dump(OUT / "paired/GEOMETRY_BOOTSTRAP.csv", a3_boot + a1_boot)
    a3_rescues, a3_regressions = write_rescues_and_regressions(rows, "A3", a3_pairs)
    csv_dump(OUT / "outliers/P1_VS_A3_GEOMETRY_RESCUES.csv", a3_rescues)
    csv_dump(OUT / "outliers/P1_VS_A3_GEOMETRY_REGRESSIONS.csv", a3_regressions)
    top20 = outlier_rows(rows)
    csv_dump(OUT / "outliers/P1_CD_TOP20.csv", top20)

    program_table = []
    for arm in ARM_ORDER:
        report = reports[arm]
        arm_rows = [row for row in rows if row["arm"] == arm]
        program_table.append(
            {
                "Method": arm,
                "Exact": report.get("exact_match_rate"),
                "Op-F1": report.get("mean_op_f1"),
                "Parse": report.get("dsl_parse_valid_rate"),
                "STEP Reload": mean([float(row["step_reload"]) for row in arm_rows]),
                "EOS": report.get("eos_rate"),
                "MaxLen": report.get("max_length_rate"),
                "UnderGen": report.get("under_generation_rate"),
            }
        )
    csv_dump(OUT / "tables/PROGRAM_EFFECTIVENESS_MAIN_TABLE.csv", program_table)

    main_table = []
    for arm in ARM_ORDER:
        report = reports[arm]
        iou = next(item for item in iou_summary if item["arm"] == arm)
        cd = next(item for item in cd_summary if item["arm"] == arm)
        topo = next(item for item in topo_summary if item["arm"] == arm)
        arm_rows = [row for row in rows if row["arm"] == arm]
        main_table.append(
            {
                "Method": arm,
                "IoU": iou["IOU_VALID_ONLY_MEAN"],
                "IoU_valid_only_median": iou["IOU_VALID_ONLY_MEDIAN"],
                "IoU_success_weighted": iou["IOU_SUCCESS_WEIGHTED"],
                "IoU_valid_N": iou["IOU_VALID_N"],
                "GED": None,
                "Mean CD": cd["mean"],
                "Med. CD": cd["median"],
                "CD_valid_N": cd["valid_N"],
                "H95": mean(value_list(arm_rows, "h95")),
                "Volume Err": mean(value_list(arm_rows, "volume_error")),
                "STEP Reload": topo["STEP_Reload"],
                "Valid BRep": topo["VALID_BREP_RATE"],
                "Closed Solid": topo["CLOSED_SOLID_RATE"],
            }
        )
    csv_dump(OUT / "tables/GEOMETRIC_EFFECTIVENESS_MAIN_TABLE.csv", main_table)
    csv_dump(OUT / "tables/COMPLEXITY_BREAKDOWN_TABLE.csv", complexity_rows)
    csv_dump(OUT / "tables/BOOLEAN_COMPLEXITY_TABLE.csv", [row for row in complexity_rows if row["Breakdown"] == "BOOLEAN"])
    csv_dump(OUT / "tables/SOURCE_BREAKDOWN_TABLE.csv", source_table(rows))
    csv_dump(OUT / "tables/CURVE_K_BREAKDOWN_TABLE.csv", [row for row in complexity_rows if row["Breakdown"] == "CURVE_K"])

    selections = make_gallery(OUT / "gallery/GEOMETRIC_EFFECTIVENESS_GALLERY.png", rows, a3_rescues, a3_regressions)
    report = final_report(reports, rows, iou_summary, cd_summary, topo_summary, a3_boot + a1_boot, complexity_rows, selections)
    json_dump(OUT / "reports/FINAL_REPORT.json", report)
    (OUT / "reports/FINAL_REPORT.md").write_text(
        final_markdown(report, iou_summary, cd_summary, topo_summary, rows),
        encoding="utf-8",
    )
    (OUT / "reports/PAPER_TABLE_INTERPRETATION.md").write_text(
        "\n".join(
            [
                "# Paper Table Interpretation",
                "",
                "- `IoU` is `OUR_BREP_IOU`, not a paper-compatible IoU unless the target evaluator is later confirmed.",
                "- `Mean CD` and `Med. CD` are `OUR_STANDARDIZED_CD`, using identical OCC tessellation tolerance and deterministic 8192-point surface sampling.",
                "- `GED` is intentionally blank because `GED_STATUS=DEFERRED_UNDEFINED`.",
                "- All five arms are evaluated together on the same VAL1000 IDs with explicit valid N and full-denominator success-weighted IoU.",
                "- Cross-paper numeric comparison is `NO` until dataset, split, normalization, sampling, CD, IoU, and failure handling are independently confirmed identical.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out": str(OUT),
                "arms": list(ARM_ORDER),
                "rows": len(rows),
                "iou": iou_summary,
                "cd": cd_summary,
                "topology": topo_summary,
                "p1_status": report["INTERPRETATION"]["P1_STATUS"],
                "ged_status": report["GED_STATUS"],
            },
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    run()
