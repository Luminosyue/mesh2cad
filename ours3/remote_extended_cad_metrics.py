#!/usr/bin/env python3
"""EXACT9998 VAL1000 A0-A3 extended CAD metric audit.

Read-only post-hoc audit. It writes a new output directory and does not modify
checkpoints, predictions, evaluator V2, GT assets, or TEST.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/exact9998_val1000_a0_a1_a2_a3_extended_cad_metrics_v1"
CORE = ROOT / "ours3/a0_a1_a2_a3_core_ablation_finalization_v1"
ARM_DIRS = {
    "A0": ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0",
    "A1": ROOT / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1",
    "A2": ROOT / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a2",
    "A3": ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3",
}
REPORT_PATHS = {arm: path / "report.json" for arm, path in ARM_DIRS.items()}
ARM_LABEL = {
    "A0": "Surface",
    "A1": "Surface + GT-BRep-Line",
    "A2": "Surface + GT-BRep-Nonline",
    "A3": "Surface + GT-BRep-All-Curves",
}
CURVE_TYPES = ["LINE", "CIRCLE", "ELLIPSE", "BSPLINE", "BEZIER", "OTHER"]
PAIRWISE = [("A1", "A3"), ("A0", "A3"), ("A1", "A0"), ("A2", "A0")]
BOOTSTRAP_N = 5000
SEED = 0

sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "SpatialLM")]


def ensure_dirs() -> None:
    for name in [
        "protocol",
        "curve",
        "closure",
        "surface",
        "topology",
        "placement",
        "parameters",
        "graph",
        "common_valid",
        "stats",
        "tables",
        "gallery",
        "reports",
    ]:
        (OUT / name).mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = sorted({key for row in rows for key in row}) if rows else ["empty"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {}
            for field in fields:
                value = row.get(field)
                if value is None:
                    out[field] = ""
                elif isinstance(value, float):
                    out[field] = f"{value:.10g}"
                elif isinstance(value, (list, tuple, dict)):
                    out[field] = json.dumps(value, ensure_ascii=False)
                else:
                    out[field] = value
            writer.writerow(out)


def finite(value: Any) -> bool:
    try:
        return value is not None and math.isfinite(float(value))
    except Exception:
        return False


def flt(value: Any) -> float | None:
    return float(value) if finite(value) else None


def mean(values: list[float]) -> float | None:
    return float(np.mean(values)) if values else None


def median(values: list[float]) -> float | None:
    return float(np.median(values)) if values else None


def percentile(values: list[float], q: float) -> float | None:
    return float(np.percentile(values, q)) if values else None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def protocol() -> dict[str, Any]:
    metrics = {
        "curve": {
            "definition": "Extract B-Rep edges from GT/pred STEP with OCP; classify primitive curve type; sample each curve uniformly in adaptor parameter space; match GT to prediction with Hungarian assignment using geometry-only cost.",
            "denominator": "Pred valid BRep for continuous prediction-side metrics; GT curve support for recall/count metrics; all 1000 for coverage.",
            "matching_rule": "Hungarian one-to-one. Cost = symmetric sampled point distance/GT bbox diag + endpoint-set distance for open curves + relative length difference. Curve type is not used in matching.",
            "threshold": "No arm-tuned threshold. Headline reports continuous assignment metrics and matched-pair type accuracy. Thresholded type F1 is diagnostic under the same frozen assignment.",
            "direction": "lower better for geometry/count/endpoint errors; higher better for accuracy/F1.",
            "failure_treatment": "Invalid or missing prediction STEP produces NA quality values and coverage failure, not zero.",
            "tier": "TIER_B for curve matching/type F1 because topology edge tessellation can differ across equivalent B-Reps; count/error metrics are diagnostic."
        },
        "wire_closure": {
            "definition": "Traverse OCP wires; count wires and Closed() state; report predicted closed-wire rate and count errors.",
            "denominator": "Valid BRep cases for continuous closure quality; 1000 for coverage rates.",
            "direction": "lower better for count/open errors; higher better for closed-wire rate.",
            "tier": "TIER_A for counts; TIER_B for closure interpretation."
        },
        "surface": {
            "definition": "STEP surface area via OCP BRepGProp.SurfaceProperties_s. Normal consistency is deferred unless a shared reliable normal tessellation is available.",
            "denominator": "Pred valid BRep with computable GT/pred area.",
            "direction": "lower better for area error. Normal consistency higher better but marked UNRELIABLE_DEFERRED.",
            "tier": "TIER_A for surface area; TIER_C/deferred for normal consistency."
        },
        "topology": {
            "definition": "OCP TopExp counts vertices, edges, wires, faces, shells, solids; Euler chi=V-E+F. Valid BRep uses BRepCheck_Analyzer.IsValid().",
            "denominator": "1000 for exact-count and validity rates; valid pred BRep for mean count errors.",
            "direction": "lower better for count/Euler/component errors; higher better for exact/valid/closed rates.",
            "tier": "TIER_A for count and valid-BRep rates; TIER_B for Euler diagnostic."
        },
        "placement_scale": {
            "definition": "Use GT mesh and prediction STL bounding boxes/centroids. Center error is bbox-center distance/GT bbox diagonal; extent error is L2 extent difference/GT bbox diagonal; scale log error is abs(log(pred_diag/GT_diag)); bbox diagonal ratio error is abs(pred_diag/GT_diag - 1).",
            "denominator": "Geometry-valid cases, with pairwise and all-four-valid subsets also reported.",
            "direction": "lower better.",
            "tier": "TIER_A diagnostic geometry metric."
        },
        "parameters": {
            "definition": "Parse canonical DSL AST; align same operation type by occurrence order within type; compare numeric fields. Position fields normalized by GT bbox diagonal; direction fields by angular error in degrees.",
            "denominator": "Aligned operation-field pairs; report coverage.",
            "direction": "lower better.",
            "tier": "TIER_B because occurrence-order alignment is diagnostic when duplicated same-type ops exist."
        },
        "dependency_graph": {
            "definition": "Parse canonical DSL assignment text; nodes are operation assignments excluding result aliases; edges are variable references into operation calls. Compare typed dependency-edge multisets.",
            "denominator": "Parse-valid DSL cases; graph alignment coverage reports cases with at least one comparable GT node.",
            "direction": "higher better for precision/recall/F1; lower better for count error.",
            "tier": "TIER_A for typed dependency F1 from canonical DSL text; GED deferred."
        },
        "statistics": {
            "continuous": "Paired bootstrap 95% CI with CAD case as bootstrap unit.",
            "binary": "McNemar exact two-sided test for binary indicators.",
            "no_metric_shopping": "All frozen metrics are emitted even when unfavorable to any arm."
        }
    }
    return {
        "schema_version": "EXTENDED_CAD_METRIC_PROTOCOL_V1",
        "frozen_before_arm_statistics": "YES",
        "input_split": "EXACT9998 VAL1000 only",
        "test_policy": "TEST1000 remains blind: no forward/loss/decode/parse/execute/STEP/geometry/metrics.",
        "normal_consistency_status": "UNRELIABLE_DEFERRED",
        "manifold_status": "NOT_IMPLEMENTED_RELIABLY",
        "graph_edit_distance_status": "DEFERRED",
        "metrics": metrics,
    }


def load_reports() -> dict[str, dict[str, Any]]:
    reports = {}
    for arm, path in REPORT_PATHS.items():
        reports[arm] = json.loads(path.read_text(encoding="utf-8"))
    ids = [{row["id"] for row in report["samples"]} for report in reports.values()]
    if len(set.intersection(*ids)) != 1000:
        raise RuntimeError("A0-A3 VAL1000 IDs are not aligned")
    return reports


def load_step_reload() -> dict[str, dict[str, dict[str, Any]]]:
    result = {}
    for arm in ARM_DIRS:
        path = CORE / f"step_reload/{arm}_STEP_RELOAD_AUDIT.csv"
        rows = {}
        with path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                row["reload_pass"] = row["reload_pass"] == "True"
                row["export_pass"] = row["export_pass"] == "True"
                rows[row["cad_id"]] = row
        result[arm] = rows
    return result


def load_registry() -> dict[str, dict[str, Any]]:
    path = ROOT / "ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                out[item.get("cad_id")] = item
    return out


def gt_base(row: dict[str, Any]) -> Path:
    surf = Path(row["surface_npy"])
    return surf.parent


def gt_mesh_path(row: dict[str, Any]) -> Path | None:
    base = gt_base(row)
    for name in ["model.obj", "mesh.obj", "model.stl", "mesh.stl"]:
        path = base / name
        if path.exists():
            return path
    sid = row["sample_id"]
    for path in [
        ROOT / "cad_spatial_dataset/DeepCAD/train" / sid / "model.obj",
        ROOT / "cad_spatial_dataset/Fusion360/geometry_pack_v1" / sid / "mesh.obj",
    ]:
        if path.exists():
            return path
    return None


def gt_step_path(row: dict[str, Any]) -> Path | None:
    base = gt_base(row)
    for name in ["model.step", "mesh.step"]:
        path = base / name
        if path.exists():
            return path
    sid = row["sample_id"]
    dataset = row.get("dataset")
    if dataset == "fusion360":
        path = ROOT / "cad_spatial_dataset/Fusion360/reconstruction/reconstruction" / f"{sid}.step"
        if path.exists():
            return path
    path = ROOT / "cad_spatial_dataset/DeepCAD/train" / sid / "model.step"
    return path if path.exists() else None


def pred_step_path(arm: str, row: dict[str, Any]) -> Path:
    return ARM_DIRS[arm] / row["id"] / "pred.step"


def pred_stl_path(arm: str, row: dict[str, Any]) -> Path | None:
    path = ARM_DIRS[arm] / row["id"] / "pred.stl"
    return path if path.exists() else None


def pred_dsl_path(arm: str, row: dict[str, Any]) -> Path:
    d = ARM_DIRS[arm] / row["id"]
    for name in ["pred_canonical.dsl", "pred.dsl"]:
        path = d / name
        if path.exists():
            return path
    return d / "pred.dsl"


def gt_dsl_path(arm: str, row: dict[str, Any]) -> Path:
    d = ARM_DIRS[arm] / row["id"]
    path = d / "gt.dsl"
    if path.exists():
        return path
    base = gt_base(row)
    for name in ["program_canonical.dsl", "program.dsl", "cad_target.dsl"]:
        p = base / name
        if p.exists():
            return p
    return path


def load_mesh(path: Path):
    import trimesh

    mesh = trimesh.load(str(path), force="mesh")
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def mesh_bbox(path: Path) -> dict[str, Any] | None:
    try:
        mesh = load_mesh(path)
        bounds = np.asarray(mesh.bounds, dtype=float)
        extent = bounds[1] - bounds[0]
        center = (bounds[0] + bounds[1]) / 2.0
        diag = float(np.linalg.norm(extent))
        return {
            "bbox_min": bounds[0],
            "bbox_max": bounds[1],
            "extent": extent,
            "center": center,
            "diag": diag,
            "area": float(mesh.area),
            "volume": float(abs(mesh.volume)) if getattr(mesh, "is_volume", False) else None,
        }
    except Exception:
        return None


def read_shape(path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP read status {status}")
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape is None or shape.IsNull():
        raise RuntimeError("empty STEP shape")
    return shape


def count_shape(shape, topabs_type, cast=None) -> tuple[int, int]:
    from OCP.TopExp import TopExp_Explorer

    ex = TopExp_Explorer(shape, topabs_type)
    n = closed = 0
    while ex.More():
        item = ex.Current()
        if cast is not None:
            item = cast(item)
        n += 1
        try:
            closed += int(bool(item.Closed()))
        except Exception:
            pass
        ex.Next()
    return n, closed


def surface_area(shape) -> float | None:
    try:
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps

        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(shape, props)
        return float(props.Mass())
    except Exception:
        return None


def edge_length(edge) -> float | None:
    try:
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps

        props = GProp_GProps()
        BRepGProp.LinearProperties_s(edge, props)
        return float(props.Mass())
    except Exception:
        return None


def map_curve_type(curve_type: Any) -> tuple[str, str]:
    raw = str(curve_type).split(".")[-1]
    tail = raw.replace("GeomAbs_", "").upper()
    if "LINE" in tail:
        return "LINE", raw
    if "CIRCLE" in tail:
        return "CIRCLE", raw
    if "ELLIPSE" in tail:
        return "ELLIPSE", raw
    if "BSPLINE" in tail or "B_SPLINE" in tail:
        return "BSPLINE", raw
    if "BEZIER" in tail:
        return "BEZIER", raw
    return "OTHER", raw


def point_tuple(pnt) -> list[float]:
    return [float(pnt.X()), float(pnt.Y()), float(pnt.Z())]


def extract_curves(shape, sample_n: int = 20) -> list[dict[str, Any]]:
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    curves = []
    ex = TopExp_Explorer(shape, TopAbs_EDGE)
    idx = 0
    while ex.More():
        edge = TopoDS.Edge_s(ex.Current())
        try:
            curve = BRepAdaptor_Curve(edge)
            first = float(curve.FirstParameter())
            last = float(curve.LastParameter())
            ctype, raw = map_curve_type(curve.GetType())
            params = np.linspace(first, last, sample_n)
            pts = np.asarray([point_tuple(curve.Value(float(t))) for t in params], dtype=float)
            closed = bool(edge.Closed())
            curves.append(
                {
                    "index": idx,
                    "type": ctype,
                    "raw_type": raw,
                    "length": edge_length(edge),
                    "points": pts,
                    "start": pts[0],
                    "end": pts[-1],
                    "closed": closed,
                    "endpoint_applicable": (not closed) and ctype not in {"CIRCLE", "ELLIPSE"},
                }
            )
        except Exception as exc:
            curves.append(
                {
                    "index": idx,
                    "type": "OTHER",
                    "raw_type": f"EXTRACT_ERROR:{type(exc).__name__}",
                    "length": None,
                    "points": np.zeros((0, 3), dtype=float),
                    "start": None,
                    "end": None,
                    "closed": False,
                    "endpoint_applicable": False,
                }
            )
        idx += 1
        ex.Next()
    return curves


def topology_features(shape) -> dict[str, Any]:
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX, TopAbs_WIRE
    from OCP.TopoDS import TopoDS

    vertex_n, _ = count_shape(shape, TopAbs_VERTEX)
    edge_n, _ = count_shape(shape, TopAbs_EDGE)
    wire_n, closed_wire_n = count_shape(shape, TopAbs_WIRE, TopoDS.Wire_s)
    face_n, _ = count_shape(shape, TopAbs_FACE)
    shell_n, closed_shell_n = count_shape(shape, TopAbs_SHELL, TopoDS.Shell_s)
    solid_n, closed_solid_n = count_shape(shape, TopAbs_SOLID, TopoDS.Solid_s)
    component_n = solid_n if solid_n > 0 else shell_n if shell_n > 0 else (1 if face_n or edge_n else 0)
    try:
        valid = bool(BRepCheck_Analyzer(shape).IsValid())
    except Exception:
        valid = False
    return {
        "valid_brep": valid,
        "vertex_n": vertex_n,
        "edge_n": edge_n,
        "wire_n": wire_n,
        "closed_wire_n": closed_wire_n,
        "face_n": face_n,
        "shell_n": shell_n,
        "closed_shell_n": closed_shell_n,
        "solid_n": solid_n,
        "closed_solid_n": closed_solid_n,
        "component_n": component_n,
        "euler_chi": vertex_n - edge_n + face_n,
        "surface_area": surface_area(shape),
    }


def step_features(path: Path) -> dict[str, Any]:
    try:
        shape = read_shape(path)
        topo = topology_features(shape)
        curves = extract_curves(shape)
        topo["curve_n"] = len(curves)
        topo["curves"] = curves
        topo["status"] = "PASS"
        return topo
    except Exception as exc:
        return {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "curves": []}


def curve_distance(a: dict[str, Any], b: dict[str, Any], diag: float) -> tuple[float, float | None, float | None]:
    diag = max(float(diag), 1e-12)
    pa = np.asarray(a["points"], dtype=float)
    pb = np.asarray(b["points"], dtype=float)
    if len(pa) == 0 or len(pb) == 0:
        sym = 1e6
    else:
        # Curves use a small fixed sample count; direct distances avoid building
        # thousands of tiny KD-trees during the all-pairs Hungarian cost pass.
        dist = np.linalg.norm(pa[:, None, :] - pb[None, :, :], axis=2)
        dab = dist.min(axis=1)
        dba = dist.min(axis=0)
        sym = float((dab.mean() + dba.mean()) / 2.0 / diag)
    la, lb = flt(a.get("length")), flt(b.get("length"))
    len_err = abs(lb - la) / max(abs(la), 1e-12) if la is not None and lb is not None else None
    endpoint_err = None
    if a.get("endpoint_applicable") and b.get("endpoint_applicable") and a.get("start") is not None and b.get("start") is not None:
        a0, a1 = np.asarray(a["start"], float), np.asarray(a["end"], float)
        b0, b1 = np.asarray(b["start"], float), np.asarray(b["end"], float)
        endpoint_err = float(min(np.linalg.norm(a0 - b0) + np.linalg.norm(a1 - b1), np.linalg.norm(a0 - b1) + np.linalg.norm(a1 - b0)) / 2.0 / diag)
    return sym, endpoint_err, len_err


def match_curves(gt: list[dict[str, Any]], pred: list[dict[str, Any]], diag: float) -> dict[str, Any]:
    if not gt or not pred:
        return {
            "pairs": [],
            "matched_n": 0,
            "unmatched_gt_n": len(gt),
            "unmatched_pred_n": len(pred),
            "unmatched_gt_indices": list(range(len(gt))),
            "unmatched_pred_indices": list(range(len(pred))),
        }
    costs = np.zeros((len(gt), len(pred)), dtype=float)
    detail = {}
    for i, gc in enumerate(gt):
        for j, pc in enumerate(pred):
            sym, ep, le = curve_distance(gc, pc, diag)
            cost = sym + (ep if ep is not None else 0.0) + min(le if le is not None else 0.0, 10.0) * 0.05
            costs[i, j] = cost
            detail[(i, j)] = (sym, ep, le, cost)
    gi, pj = linear_sum_assignment(costs)
    pairs = []
    for i, j in zip(gi, pj):
        sym, ep, le, cost = detail[(int(i), int(j))]
        pairs.append(
            {
                "gt_index": int(i),
                "pred_index": int(j),
                "gt_type": gt[int(i)]["type"],
                "pred_type": pred[int(j)]["type"],
                "geometry_error": sym,
                "endpoint_error": ep,
                "length_relative_error": le,
                "matching_cost": cost,
                "type_correct": gt[int(i)]["type"] == pred[int(j)]["type"],
            }
        )
    matched_gt = {p["gt_index"] for p in pairs}
    matched_pred = {p["pred_index"] for p in pairs}
    return {
        "pairs": pairs,
        "matched_n": len(pairs),
        "unmatched_gt_n": max(len(gt) - len(pairs), 0),
        "unmatched_pred_n": max(len(pred) - len(pairs), 0),
        "unmatched_gt_indices": [i for i in range(len(gt)) if i not in matched_gt],
        "unmatched_pred_indices": [i for i in range(len(pred)) if i not in matched_pred],
    }


ASSIGN_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*\((.*)\)\s*$")


def parse_assignments(path: Path) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    if not path.exists():
        return [], []
    text = path.read_text(encoding="utf-8", errors="replace")
    nodes = []
    var_to_op = {}
    references: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = ASSIGN_RE.match(line)
        if not m:
            continue
        var, op, args = m.group(1), m.group(2), m.group(3)
        if var != "result":
            nodes.append({"var": var, "op": op, "line": line})
        refs = re.findall(r"\b[A-Za-z_]\w*\b", args)
        for ref in refs:
            if ref in var_to_op:
                references.append((ref, var))
        var_to_op[var] = op
    typed_edges = [(var_to_op.get(src, "UNK"), var_to_op.get(dst, "UNK")) for src, dst in references if src in var_to_op and dst in var_to_op]
    return nodes, typed_edges


def graph_metrics(gt_path: Path, pred_path: Path) -> dict[str, Any]:
    gt_nodes, gt_edges = parse_assignments(gt_path)
    pr_nodes, pr_edges = parse_assignments(pred_path)
    gt_counter = Counter(gt_edges)
    pr_counter = Counter(pr_edges)
    tp = sum((gt_counter & pr_counter).values())
    pred_n = sum(pr_counter.values())
    gt_n = sum(gt_counter.values())
    prec = tp / pred_n if pred_n else (1.0 if gt_n == 0 else 0.0)
    rec = tp / gt_n if gt_n else (1.0 if pred_n == 0 else 0.0)
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "gt_node_n": len(gt_nodes),
        "pred_node_n": len(pr_nodes),
        "gt_edge_n": gt_n,
        "pred_edge_n": pred_n,
        "node_count_error": abs(len(pr_nodes) - len(gt_nodes)),
        "dependency_edge_precision": prec,
        "dependency_edge_recall": rec,
        "dependency_edge_f1": f1,
        "graph_alignment_coverage": 1.0 if gt_nodes else None,
        "normalized_graph_edit_distance": None,
        "ged_status": "DEFERRED",
    }


def literal_kwargs(line: str) -> dict[str, Any]:
    m = ASSIGN_RE.match(line)
    if not m:
        return {}
    try:
        expr = ast.parse(f"f({m.group(3)})", mode="eval").body
        return {kw.arg: ast.literal_eval(kw.value) for kw in expr.keywords if kw.arg is not None}
    except Exception:
        return {}


def ast_ops_with_params(path: Path) -> list[dict[str, Any]]:
    nodes, _ = parse_assignments(path)
    out = []
    for node in nodes:
        params = literal_kwargs(node["line"])
        out.append({"op": node["op"], "params": params})
    return out


def norm_vec(value: Any) -> np.ndarray | None:
    try:
        arr = np.asarray(value, dtype=float).reshape(-1)
        return arr if arr.size > 0 else None
    except Exception:
        return None


def param_errors(gt_path: Path, pred_path: Path, diag: float) -> list[dict[str, Any]]:
    gt_ops = ast_ops_with_params(gt_path)
    pr_ops = ast_ops_with_params(pred_path)
    by_gt: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_pr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in gt_ops:
        by_gt[item["op"]].append(item)
    for item in pr_ops:
        by_pr[item["op"]].append(item)
    rows = []
    for op, gitems in by_gt.items():
        pitems = by_pr.get(op, [])
        for idx, gitem in enumerate(gitems[: len(pitems)]):
            pitem = pitems[idx]
            for field, gv in gitem["params"].items():
                if field not in pitem["params"]:
                    continue
                pv = pitem["params"][field]
                ga, pa = norm_vec(gv), norm_vec(pv)
                if ga is None or pa is None or ga.shape != pa.shape:
                    continue
                if field in {"axis", "direction", "x_axis"} and ga.size == pa.size:
                    ng, npv = np.linalg.norm(ga), np.linalg.norm(pa)
                    if ng > 1e-12 and npv > 1e-12:
                        cos = float(np.clip(np.dot(ga, pa) / ng / npv, -1.0, 1.0))
                        err = math.degrees(math.acos(cos))
                        unit = "degrees"
                    else:
                        continue
                elif field in {"origin", "translation", "center"} or ga.size in {2, 3}:
                    err = float(np.linalg.norm(ga - pa) / max(diag, 1e-12))
                    unit = "relative_gt_bbox_diag"
                else:
                    err = float(np.mean(np.abs(ga - pa)))
                    unit = "absolute"
                rows.append({"operation": op, "field": field, "error": err, "unit": unit})
    return rows


def placement_metrics(gt_mesh: dict[str, Any] | None, pred_mesh: dict[str, Any] | None) -> dict[str, Any]:
    if not gt_mesh or not pred_mesh or gt_mesh["diag"] <= 1e-12:
        return {
            "center_error": None,
            "extent_error": None,
            "scale_log_error": None,
            "bbox_diagonal_ratio_error": None,
        }
    gt_diag = max(gt_mesh["diag"], 1e-12)
    pred_diag = max(pred_mesh["diag"], 1e-12)
    return {
        "center_error": float(np.linalg.norm(pred_mesh["center"] - gt_mesh["center"]) / gt_diag),
        "extent_error": float(np.linalg.norm(pred_mesh["extent"] - gt_mesh["extent"]) / gt_diag),
        "scale_log_error": float(abs(math.log(pred_diag / gt_diag))),
        "bbox_diagonal_ratio_error": float(abs(pred_diag / gt_diag - 1.0)),
    }


def profile_closure(path: Path) -> dict[str, Any]:
    ops = ast_ops_with_params(path)
    applicable = executable = closed = 0
    for op in ops:
        if op["op"] != "ExtrudePolygon":
            continue
        applicable += 1
        pts = op["params"].get("points")
        if isinstance(pts, (list, tuple)) and len(pts) >= 3:
            executable += 1
            unique = {tuple(np.asarray(p, dtype=float).round(8).tolist()) for p in pts}
            if len(unique) >= 3:
                closed += 1
    return {
        "profile_applicable_n": applicable,
        "profile_executable_n": executable,
        "profile_closed_n": closed,
        "profile_closure_rate": closed / applicable if applicable else None,
    }


def summarize(values: list[float]) -> dict[str, Any]:
    return {"N": len(values), "mean": mean(values), "median": median(values), "p90": percentile(values, 90)}


def aggregate_case_metrics(case_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm = defaultdict(list)
    for row in case_rows:
        by_arm[row["arm"]].append(row)
    return {arm: rows for arm, rows in by_arm.items()}


def bootstrap_ci(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    arr = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED)
    means = []
    for _ in range(BOOTSTRAP_N):
        means.append(float(arr[rng.integers(0, len(arr), size=len(arr))].mean()))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def binary_mcnemar(pairs: list[tuple[bool, bool]]) -> dict[str, Any]:
    both = sum(a and b for a, b in pairs)
    a_only = sum(a and not b for a, b in pairs)
    b_only = sum((not a) and b for a, b in pairs)
    neither = sum((not a) and (not b) for a, b in pairs)
    discord = a_only + b_only
    try:
        from scipy.stats import binomtest

        p = float(binomtest(min(a_only, b_only), n=discord, p=0.5).pvalue) if discord else 1.0
    except Exception:
        p = None
    return {"both_pass": both, "arm1_only": a_only, "arm2_only": b_only, "both_fail": neither, "discordant": discord, "mcnemar_exact_two_sided_p": p}


def run() -> dict[str, Any]:
    ensure_dirs()
    proto = protocol()
    write_json(OUT / "protocol/EXTENDED_CAD_METRIC_PROTOCOL_V1.json", proto)
    write_json(OUT / "curve/CURVE_MATCH_PROTOCOL.json", proto["metrics"]["curve"])
    write_json(
        OUT / "curve/CURVE_MATCH_CALIBRATION.json",
        {
            "status": "CONTINUOUS_ASSIGNMENT_HEADLINE_NO_THRESHOLD",
            "thresholded_precision_recall_f1": "EXPLORATORY_NOT_HEADLINE",
            "calibration_data_used": "GT self-match/deterministic extraction only; no A0-A3 performance used.",
        },
    )
    reports = load_reports()
    reloads = load_step_reload()
    registry = load_registry()
    hashes_before = {arm: sha256(REPORT_PATHS[arm]) for arm in ARM_DIRS}
    base_rows = reports["A0"]["samples"]
    by_arm_rows = {arm: {row["id"]: row for row in report["samples"]} for arm, report in reports.items()}
    all_four_ids = set()
    all_four_path = CORE / "common_valid/ALL_FOUR_VALID_GEOMETRY.csv"
    with all_four_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["cad_id"] and row["cad_id"] != "__SUMMARY__":
                all_four_ids.add(row["cad_id"])

    gt_step_cache: dict[str, dict[str, Any]] = {}
    gt_mesh_cache: dict[str, dict[str, Any] | None] = {}
    gt_diag_cache: dict[str, float] = {}
    case_rows: list[dict[str, Any]] = []
    curve_pair_rows: list[dict[str, Any]] = []
    param_rows: list[dict[str, Any]] = []
    graph_rows: list[dict[str, Any]] = []
    closure_rows: list[dict[str, Any]] = []
    surface_rows: list[dict[str, Any]] = []
    topology_rows: list[dict[str, Any]] = []
    placement_rows: list[dict[str, Any]] = []

    for idx, base_row in enumerate(base_rows, 1):
        cad_id = base_row["id"]
        gt_step = gt_step_path(base_row)
        gt_mesh_p = gt_mesh_path(base_row)
        gt_mesh = mesh_bbox(gt_mesh_p) if gt_mesh_p else None
        gt_mesh_cache[cad_id] = gt_mesh
        diag = (gt_mesh or {}).get("diag") or 1.0
        gt_diag_cache[cad_id] = diag
        gt_feat = step_features(gt_step) if gt_step and gt_step.exists() else {"status": "FAIL", "curves": []}
        gt_step_cache[cad_id] = gt_feat

        for arm in ("A0", "A1", "A2", "A3"):
            row = by_arm_rows[arm][cad_id]
            pred_valid = bool(reloads[arm][cad_id]["reload_pass"])
            pred_feat = step_features(pred_step_path(arm, row)) if pred_valid else {"status": "FAIL", "curves": []}
            pred_mesh_p = pred_stl_path(arm, row)
            pred_mesh = mesh_bbox(pred_mesh_p) if pred_mesh_p and pred_valid else None
            placement = placement_metrics(gt_mesh, pred_mesh)

            gt_curves = gt_feat.get("curves", [])
            pred_curves = pred_feat.get("curves", [])
            cmatch = match_curves(gt_curves, pred_curves, diag) if pred_valid and gt_feat.get("status") == "PASS" else {"pairs": [], "matched_n": 0, "unmatched_gt_n": len(gt_curves), "unmatched_pred_n": len(pred_curves)}
            geom_errors = [p["geometry_error"] for p in cmatch["pairs"] if finite(p["geometry_error"])]
            endpoint_errors = [p["endpoint_error"] for p in cmatch["pairs"] if finite(p["endpoint_error"])]
            length_errors = [p["length_relative_error"] for p in cmatch["pairs"] if finite(p["length_relative_error"])]
            type_acc = mean([float(p["type_correct"]) for p in cmatch["pairs"]]) if cmatch["pairs"] else None
            count_abs = abs(len(pred_curves) - len(gt_curves)) if pred_valid and gt_feat.get("status") == "PASS" else None
            count_rel = count_abs / max(len(gt_curves), 1) if count_abs is not None else None
            gt_topo = gt_feat
            pr_topo = pred_feat
            area_err = None
            if finite(gt_topo.get("surface_area")) and finite(pr_topo.get("surface_area")) and gt_topo["surface_area"] > 1e-12:
                area_err = abs(pr_topo["surface_area"] - gt_topo["surface_area"]) / gt_topo["surface_area"]

            gd = graph_metrics(gt_dsl_path(arm, row), pred_dsl_path(arm, row)) if row.get("parsed") else {
                "gt_node_n": None, "pred_node_n": None, "gt_edge_n": None, "pred_edge_n": None,
                "node_count_error": None, "dependency_edge_precision": None, "dependency_edge_recall": None,
                "dependency_edge_f1": None, "graph_alignment_coverage": None,
                "normalized_graph_edit_distance": None, "ged_status": "DEFERRED",
            }
            graph_rows.append({"cad_id": cad_id, "arm": arm, **gd})
            for prow in param_errors(gt_dsl_path(arm, row), pred_dsl_path(arm, row), diag) if row.get("parsed") else []:
                param_rows.append({"cad_id": cad_id, "arm": arm, **prow})
            gt_profile = profile_closure(gt_dsl_path(arm, row))
            pr_profile = profile_closure(pred_dsl_path(arm, row)) if row.get("parsed") else {"profile_applicable_n": 0, "profile_executable_n": 0, "profile_closed_n": 0, "profile_closure_rate": None}

            topo_errors = {}
            for name in ["vertex_n", "edge_n", "wire_n", "face_n", "shell_n", "solid_n", "component_n", "euler_chi"]:
                topo_errors[f"{name}_error"] = abs(pr_topo.get(name, 0) - gt_topo.get(name, 0)) if pred_valid and gt_feat.get("status") == "PASS" else None

            case = {
                "cad_id": cad_id,
                "source": row.get("dataset"),
                "K": registry.get(cad_id, {}).get("K"),
                "arm": arm,
                "Op-F1": row.get("op_f1"),
                "Parse": bool(row.get("parsed")),
                "STEP_Reload": pred_valid,
                "Chamfer": (row.get("geometry") or {}).get("chamfer_norm"),
                "H95": (row.get("geometry") or {}).get("hausdorff_95_norm"),
                "Volume_Error": (row.get("geometry") or {}).get("volume_error"),
                "GT_curve_N": len(gt_curves),
                "Pred_curve_N": len(pred_curves) if pred_valid else None,
                "curve_count_error": count_abs,
                "curve_count_relative_error": count_rel,
                "matched_curve_N": cmatch["matched_n"],
                "unmatched_gt_curve_N": cmatch["unmatched_gt_n"],
                "unmatched_pred_curve_N": cmatch["unmatched_pred_n"],
                "curve_geometry_error": mean(geom_errors),
                "curve_geometry_error_median": median(geom_errors),
                "curve_geometry_error_p90": percentile(geom_errors, 90),
                "curve_type_accuracy": type_acc,
                "curve_length_relative_error": mean(length_errors),
                "endpoint_error": mean(endpoint_errors),
                "endpoint_applicable_N": len(endpoint_errors),
                "GT_wire_N": gt_topo.get("wire_n"),
                "Pred_wire_N": pr_topo.get("wire_n") if pred_valid else None,
                "wire_count_error": topo_errors.get("wire_n_error"),
                "GT_closed_wire_N": gt_topo.get("closed_wire_n"),
                "Pred_closed_wire_N": pr_topo.get("closed_wire_n") if pred_valid else None,
                "closed_wire_count_error": (abs(pr_topo.get("closed_wire_n", 0) - gt_topo.get("closed_wire_n", 0)) if pred_valid else None),
                "pred_closed_wire_rate": (pr_topo.get("closed_wire_n", 0) / pr_topo.get("wire_n", 1) if pred_valid and pr_topo.get("wire_n", 0) else None),
                "open_wire_count": (pr_topo.get("wire_n", 0) - pr_topo.get("closed_wire_n", 0) if pred_valid else None),
                "surface_area_relative_error": area_err,
                "normal_consistency": None,
                "normal_consistency_status": "UNRELIABLE_DEFERRED",
                "valid_brep": bool(pr_topo.get("valid_brep")) if pred_valid else False,
                "closed_shell": bool(pr_topo.get("closed_shell_n", 0) > 0) if pred_valid else False,
                "closed_solid": bool(pr_topo.get("closed_solid_n", 0) > 0) if pred_valid else False,
                "face_count_error": topo_errors.get("face_n_error"),
                "edge_count_error": topo_errors.get("edge_n_error"),
                "solid_count_error": topo_errors.get("solid_n_error"),
                "component_count_error": topo_errors.get("component_n_error"),
                "euler_error": topo_errors.get("euler_chi_error"),
                "dependency_graph_F1": gd.get("dependency_edge_f1"),
                "dependency_edge_precision": gd.get("dependency_edge_precision"),
                "dependency_edge_recall": gd.get("dependency_edge_recall"),
                "graph_alignment_coverage": gd.get("graph_alignment_coverage"),
                "profile_applicable_n": pr_profile["profile_applicable_n"],
                "profile_executable_n": pr_profile["profile_executable_n"],
                "profile_closed_n": pr_profile["profile_closed_n"],
                "profile_closure_rate": pr_profile["profile_closure_rate"],
                **placement,
                **topo_errors,
            }
            case_rows.append(case)
            closure_rows.append(case)
            surface_rows.append(case)
            topology_rows.append(case)
            placement_rows.append(case)
            for pair in cmatch["pairs"]:
                curve_pair_rows.append({"cad_id": cad_id, "arm": arm, "pair_status": "MATCHED", **pair})
            for gi in cmatch.get("unmatched_gt_indices", []):
                gt_curve = gt_curves[gi]
                curve_pair_rows.append(
                    {
                        "cad_id": cad_id,
                        "arm": arm,
                        "pair_status": "MISSING",
                        "gt_index": gi,
                        "pred_index": None,
                        "gt_type": gt_curve["type"],
                        "pred_type": "MISSING",
                        "geometry_error": None,
                        "endpoint_error": None,
                        "length_relative_error": None,
                        "matching_cost": None,
                        "type_correct": False,
                    }
                )
            for pi in cmatch.get("unmatched_pred_indices", []):
                pred_curve = pred_curves[pi]
                curve_pair_rows.append(
                    {
                        "cad_id": cad_id,
                        "arm": arm,
                        "pair_status": "SPURIOUS",
                        "gt_index": None,
                        "pred_index": pi,
                        "gt_type": "SPURIOUS",
                        "pred_type": pred_curve["type"],
                        "geometry_error": None,
                        "endpoint_error": None,
                        "length_relative_error": None,
                        "matching_cost": None,
                        "type_correct": False,
                    }
                )
        if idx % 25 == 0:
            print(f"processed {idx}/1000", flush=True)

    write_csv(OUT / "curve/CURVE_CASE_METRICS.csv", case_rows)
    write_csv(OUT / "closure/WIRE_CLOSURE_METRICS.csv", closure_rows)
    write_csv(OUT / "closure/PROFILE_CLOSURE_METRICS.csv", closure_rows)
    write_csv(OUT / "surface/SURFACE_EXTENDED_METRICS.csv", surface_rows)
    write_csv(OUT / "topology/BREP_TOPOLOGY_CASE_METRICS.csv", topology_rows)
    write_csv(OUT / "placement/PLACEMENT_SCALE_EXTENDED.csv", placement_rows)
    write_csv(OUT / "graph/DEPENDENCY_GRAPH_METRICS.csv", graph_rows)
    write_csv(OUT / "tables/EXTENDED_CASE_LEVEL_METRICS.csv", case_rows)

    # Curve type metrics and confusion matrices.
    type_metric_rows = []
    for arm in ("A0", "A1", "A2", "A3"):
        pairs = [p for p in curve_pair_rows if p["arm"] == arm and p.get("pair_status") == "MATCHED"]
        all_curve_rows = [p for p in curve_pair_rows if p["arm"] == arm]
        confusion = {gt: Counter() for gt in CURVE_TYPES + ["SPURIOUS"]}
        spurious = Counter()
        for p in all_curve_rows:
            confusion[p["gt_type"]][p["pred_type"]] += 1
        # Add unmatched/missing and spurious from per-case feature data is unavailable by type here;
        # use matched-pair type metrics as frozen diagnostic.
        gt_support = Counter(p["gt_type"] for p in pairs)
        pred_support = Counter(p["pred_type"] for p in pairs)
        f1s = []
        for ctype in CURVE_TYPES:
            tp = confusion[ctype][ctype]
            prec = tp / pred_support[ctype] if pred_support[ctype] else None
            rec = tp / gt_support[ctype] if gt_support[ctype] else None
            f1 = 2 * prec * rec / (prec + rec) if prec is not None and rec is not None and (prec + rec) else None
            if f1 is not None:
                f1s.append(f1)
            type_metric_rows.append({"arm": arm, "curve_type": ctype, "support": gt_support[ctype], "precision": prec, "recall": rec, "f1": f1})
        type_metric_rows.append({
            "arm": arm, "curve_type": "MACRO", "support": sum(gt_support.values()),
            "precision": None, "recall": None, "f1": mean(f1s)
        })
        conf_rows = []
        for gt in CURVE_TYPES + ["SPURIOUS"]:
            row = {"GT_curve_type": gt}
            for pr in CURVE_TYPES:
                row[pr] = confusion[gt][pr]
            row["MISSING"] = confusion[gt]["MISSING"]
            conf_rows.append(row)
        write_csv(OUT / f"curve/CURVE_TYPE_CONFUSION_{arm}.csv", conf_rows, ["GT_curve_type"] + CURVE_TYPES + ["MISSING"])
    write_csv(OUT / "curve/CURVE_TYPE_METRICS.csv", type_metric_rows, ["arm", "curve_type", "support", "precision", "recall", "f1"])

    # Parameter summary.
    param_summary = []
    for (arm, op, field), rows in defaultdict(list, {k: [] for k in []}).items():
        pass
    grouped: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in param_rows:
        grouped[(row["arm"], row["operation"], row["field"], row["unit"])].append(row["error"])
    for (arm, op, field, unit), vals in sorted(grouped.items()):
        param_summary.append({"arm": arm, "operation": op, "parameter_field": field, "unit": unit, "N": len(vals), "mean": mean(vals), "median": median(vals)})
    write_csv(OUT / "parameters/PARAMETER_ERROR_SUMMARY.csv", param_summary, ["arm", "operation", "parameter_field", "unit", "N", "mean", "median"])
    write_csv(OUT / "tables/PARAMETER_ERROR_SUMMARY.csv", param_summary, ["arm", "operation", "parameter_field", "unit", "N", "mean", "median"])

    by_arm = aggregate_case_metrics(case_rows)

    def vals(arm: str, field: str) -> list[float]:
        return [float(r[field]) for r in by_arm[arm] if finite(r.get(field))]

    coverage_rows = []
    for arm in ("A0", "A1", "A2", "A3"):
        rows = by_arm[arm]
        coverage_rows.append({
            "arm": arm,
            "input": ARM_LABEL[arm],
            "Parse": reports[arm]["dsl_parse_valid_rate"],
            "STEP_Export": reports[arm]["step_valid_rate"],
            "STEP_Reload": sum(bool(reloads[arm][r["cad_id"]]["reload_pass"]) for r in rows) / 1000,
            "Valid_BRep": sum(bool(r["valid_brep"]) for r in rows) / 1000,
            "Closed_Shell": sum(bool(r["closed_shell"]) for r in rows) / 1000,
            "Closed_Solid": sum(bool(r["closed_solid"]) for r in rows) / 1000,
            "Geometry_Valid": sum(finite(r.get("Chamfer")) and finite(r.get("H95")) for r in rows) / 1000,
        })
    write_csv(OUT / "tables/EXTENDED_CAD_COVERAGE_TABLE.csv", coverage_rows)

    curve_table = []
    for arm in ("A0", "A1", "A2", "A3"):
        macro = next((r["f1"] for r in type_metric_rows if r["arm"] == arm and r["curve_type"] == "MACRO"), None)
        line_f1 = next((r["f1"] for r in type_metric_rows if r["arm"] == arm and r["curve_type"] == "LINE"), None)
        circ_f1 = next((r["f1"] for r in type_metric_rows if r["arm"] == arm and r["curve_type"] == "CIRCLE"), None)
        ell_f1 = next((r["f1"] for r in type_metric_rows if r["arm"] == arm and r["curve_type"] == "ELLIPSE"), None)
        bsp_f1 = next((r["f1"] for r in type_metric_rows if r["arm"] == arm and r["curve_type"] == "BSPLINE"), None)
        curve_table.append({
            "arm": arm,
            "GT_Curve_N_aggregate": sum(r["GT_curve_N"] for r in by_arm[arm] if r.get("GT_curve_N") is not None),
            "Pred_Curve_Count_Error": mean(vals(arm, "curve_count_error")),
            "Matched_Curve_Geometry_Error": mean(vals(arm, "curve_geometry_error")),
            "Curve_Type_Accuracy": mean(vals(arm, "curve_type_accuracy")),
            "Curve_Type_Macro_F1": macro,
            "LINE_F1": line_f1,
            "CIRCLE_F1": circ_f1,
            "ELLIPSE_F1": ell_f1,
            "BSPLINE_F1": bsp_f1,
            "Endpoint_Error": mean(vals(arm, "endpoint_error")),
            "Closed_Wire_Rate": mean(vals(arm, "pred_closed_wire_rate")),
            "denominator_N": len(vals(arm, "curve_geometry_error")),
        })
    write_csv(OUT / "tables/CURVE_RECONSTRUCTION_TABLE.csv", curve_table)

    surface_table = []
    for arm in ("A0", "A1", "A2", "A3"):
        surface_table.append({
            "arm": arm,
            "Chamfer": reports[arm]["mean_chamfer_norm"],
            "H95": reports[arm]["mean_hausdorff_95_norm"],
            "Surface_Area_Relative_Error": mean(vals(arm, "surface_area_relative_error")),
            "Surface_Area_Error_N": len(vals(arm, "surface_area_relative_error")),
            "Normal_Consistency": None,
            "Normal_Consistency_Status": "UNRELIABLE_DEFERRED",
            "Center_Error": mean(vals(arm, "center_error")),
            "Extent_Error": mean(vals(arm, "extent_error")),
            "Scale_Log_Error": mean(vals(arm, "scale_log_error")),
            "Volume_Error": reports[arm]["mean_volume_error"],
            "denominator_N": len(vals(arm, "center_error")),
        })
    write_csv(OUT / "tables/SURFACE_GEOMETRY_TABLE.csv", surface_table)

    topo_table = []
    for arm in ("A0", "A1", "A2", "A3"):
        topo_table.append({
            "arm": arm,
            "Vertex_Count_Error": mean(vals(arm, "vertex_n_error")),
            "Edge_Count_Error": mean(vals(arm, "edge_n_error")),
            "Face_Count_Error": mean(vals(arm, "face_n_error")),
            "Wire_Count_Error": mean(vals(arm, "wire_n_error")),
            "Solid_Count_Error": mean(vals(arm, "solid_n_error")),
            "Connected_Component_Error": mean(vals(arm, "component_n_error")),
            "Euler_Error": mean(vals(arm, "euler_chi_error")),
            "Closed_Solid_Rate": coverage_rows[["A0", "A1", "A2", "A3"].index(arm)]["Closed_Solid"],
            "Valid_BRep_Rate": coverage_rows[["A0", "A1", "A2", "A3"].index(arm)]["Valid_BRep"],
            "denominator_N": len(vals(arm, "face_count_error")),
        })
    write_csv(OUT / "tables/BREP_TOPOLOGY_TABLE.csv", topo_table)

    program_table = []
    for arm in ("A0", "A1", "A2", "A3"):
        program_table.append({
            "arm": arm,
            "Exact": reports[arm]["exact_match_rate"],
            "Op-F1": reports[arm]["mean_op_f1"],
            "Op_Recall": reports[arm]["mean_op_recall"],
            "Dependency_Edge_Precision": mean(vals(arm, "dependency_edge_precision")),
            "Dependency_Edge_Recall": mean(vals(arm, "dependency_edge_recall")),
            "Dependency_Edge_F1": mean(vals(arm, "dependency_graph_F1")),
            "Graph_Alignment_Coverage": mean(vals(arm, "graph_alignment_coverage")),
            "GED_Status": "DEFERRED",
        })
    write_csv(OUT / "tables/PROGRAM_STRUCTURE_EXTENDED_TABLE.csv", program_table)

    all_four_rows = [r for r in case_rows if r["cad_id"] in all_four_ids]
    write_csv(OUT / "common_valid/ALL_FOUR_VALID_EXTENDED_METRICS.csv", all_four_rows)

    paired_rows = []
    bootstrap_rows = []
    binary_rows = []
    for arm1, arm2 in PAIRWISE:
        ids = sorted({r["cad_id"] for r in by_arm[arm1]} & {r["cad_id"] for r in by_arm[arm2]})
        idx1 = {r["cad_id"]: r for r in by_arm[arm1]}
        idx2 = {r["cad_id"]: r for r in by_arm[arm2]}
        for field, direction in [
            ("surface_area_relative_error", "lower"),
            ("face_count_error", "lower"),
            ("edge_count_error", "lower"),
            ("center_error", "lower"),
            ("extent_error", "lower"),
            ("curve_geometry_error", "lower"),
            ("dependency_graph_F1", "higher"),
        ]:
            deltas = []
            n = 0
            for cad_id in ids:
                a, b = flt(idx1[cad_id].get(field)), flt(idx2[cad_id].get(field))
                if a is None or b is None:
                    continue
                n += 1
                deltas.append(a - b)
            lo, hi = bootstrap_ci(deltas)
            row = {
                "comparison": f"{arm1}_vs_{arm2}",
                "metric": field,
                "paired_N": n,
                "arm1_mean": mean([flt(idx1[c].get(field)) for c in ids if flt(idx1[c].get(field)) is not None and flt(idx2[c].get(field)) is not None]),
                "arm2_mean": mean([flt(idx2[c].get(field)) for c in ids if flt(idx1[c].get(field)) is not None and flt(idx2[c].get(field)) is not None]),
                "mean_delta_arm1_minus_arm2": mean(deltas),
                "bootstrap_ci95_low": lo,
                "bootstrap_ci95_high": hi,
                "direction": direction,
            }
            paired_rows.append(row)
            bootstrap_rows.append(row)
        for field in ["valid_brep", "closed_shell", "closed_solid"]:
            m = binary_mcnemar([(bool(idx1[c].get(field)), bool(idx2[c].get(field))) for c in ids])
            binary_rows.append({"comparison": f"{arm1}_vs_{arm2}", "metric": field, **m})
    write_csv(OUT / "common_valid/PAIRWISE_EXTENDED_METRICS.csv", paired_rows)
    write_csv(OUT / "stats/EXTENDED_PAIRED_BOOTSTRAP.csv", bootstrap_rows)
    write_csv(OUT / "stats/EXTENDED_BINARY_MCNEMAR.csv", binary_rows)

    # Source/K/complexity breakdown is included in FINAL_REPORT as compact summaries.
    def best_lower(table: list[dict[str, Any]], field: str) -> str | None:
        vals2 = [(row["arm"], flt(row.get(field))) for row in table]
        vals2 = [(a, v) for a, v in vals2 if v is not None]
        if not vals2:
            return None
        best = min(v for _, v in vals2)
        winners = [a for a, v in vals2 if abs(v - best) <= 1e-12]
        return winners[0] if len(winners) == 1 else "TIE_" + "_".join(winners)

    def best_higher(table: list[dict[str, Any]], field: str) -> str | None:
        vals2 = [(row["arm"], flt(row.get(field))) for row in table]
        vals2 = [(a, v) for a, v in vals2 if v is not None]
        if not vals2:
            return None
        best = max(v for _, v in vals2)
        winners = [a for a, v in vals2 if abs(v - best) <= 1e-12]
        return winners[0] if len(winners) == 1 else "TIE_" + "_".join(winners)

    # Simple PIL gallery.
    make_gallery(curve_table, surface_table, topo_table, program_table, case_rows)

    rec_md = benchmark_recommendations()
    (OUT / "reports/RECOMMENDED_CURVECAD_BENCH_METRICS.md").write_text(rec_md, encoding="utf-8")

    final = {
        "CURRENT_GATE": "EXACT9998_VAL1000_A0_A1_A2_A3_EXTENDED_CAD_METRICS_V1",
        "TEST_TOUCHED": "NO",
        "P1_UNAFFECTED": "YES",
        "NORMAL_CONSISTENCY_STATUS": "UNRELIABLE_DEFERRED",
        "MANIFOLD_STATUS": "NOT_IMPLEMENTED_RELIABLY",
        "CURVE": {
            "CURVE_MATCH_PROTOCOL_STATUS": "FROZEN_CONTINUOUS_ASSIGNMENT",
            **{f"{arm}_CURVE_TYPE_MACRO_F1": next((r["f1"] for r in type_metric_rows if r["arm"] == arm and r["curve_type"] == "MACRO"), None) for arm in ARM_DIRS},
            **{f"{arm}_CURVE_GEOMETRY_ERROR": next((r["Matched_Curve_Geometry_Error"] for r in curve_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            "BEST_CURVE_ARM": best_lower(curve_table, "Matched_Curve_Geometry_Error"),
        },
        "CLOSURE": {
            **{f"{arm}_CLOSED_WIRE_RATE": next((r["Closed_Wire_Rate"] for r in curve_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            "BEST_CLOSURE_ARM": best_higher(curve_table, "Closed_Wire_Rate"),
        },
        "SURFACE": {
            **{f"{arm}_SURFACE_AREA_ERROR": next((r["Surface_Area_Relative_Error"] for r in surface_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            "BEST_SURFACE_ARM": best_lower(surface_table, "Surface_Area_Relative_Error"),
        },
        "TOPOLOGY": {
            **{f"{arm}_FACE_COUNT_ERROR": next((r["Face_Count_Error"] for r in topo_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            **{f"{arm}_EDGE_COUNT_ERROR": next((r["Edge_Count_Error"] for r in topo_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            **{f"{arm}_CLOSED_SOLID_RATE": next((r["Closed_Solid_Rate"] for r in topo_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            "BEST_TOPOLOGY_ARM": best_lower(topo_table, "Face_Count_Error"),
        },
        "GRAPH": {
            **{f"{arm}_DEP_GRAPH_F1": next((r["Dependency_Edge_F1"] for r in program_table if r["arm"] == arm), None) for arm in ARM_DIRS},
            "BEST_GRAPH_ARM": best_higher(program_table, "Dependency_Edge_F1"),
        },
        "ALL_FOUR_VALID": all_four_summary(all_four_rows),
        "A3": {},
        "BENCHMARK": {
            "TIER_A_METRICS": ["Exact", "Op-F1", "Parse", "STEP Reload", "Chamfer", "H95", "Surface Area Error", "B-Rep count errors", "Dependency Edge F1"],
            "TIER_B_METRICS": ["Curve geometry/type under assignment", "Euler error", "Parameter errors", "Closure interpretation"],
            "TIER_C_METRICS": ["Normal Consistency", "Manifold Rate", "Graph Edit Distance"],
            "RECOMMENDED_HEADLINE_METRICS": ["Op-F1", "STEP Reload", "Chamfer/H95 with geometry coverage", "Face/Edge/Solid count error", "Dependency Edge F1"],
        },
        "INTERPRETATION": {},
        "tables": {
            "coverage": coverage_rows,
            "curve": curve_table,
            "surface": surface_table,
            "topology": topo_table,
            "program": program_table,
        },
        "integrity": {
            "A0_CHANGED": "NO", "A1_CHANGED": "NO", "A2_CHANGED": "NO", "A3_CHANGED": "NO",
            "P1_CHANGED": "NO", "PREDICTIONS_CHANGED": "NO", "EVALUATOR_V2_CHANGED": "NO",
            "GT_CHANGED": "NO", "EXACT9998_CHANGED": "NO", "TEST_TOUCHED": "NO",
            "NEW_DECODE_RUN": "NO", "NEW_TRAIN_RUN": "NO",
            "report_sha256_before": hashes_before,
            "report_sha256_after": {arm: sha256(REPORT_PATHS[arm]) for arm in ARM_DIRS},
        },
    }
    a3_flags = a3_advantage(final)
    final["A3"] = a3_flags
    final["INTERPRETATION"] = interpretation(final)
    write_json(OUT / "reports/FINAL_REPORT.json", final)
    (OUT / "reports/FINAL_REPORT.md").write_text(final_markdown(final), encoding="utf-8")
    print(json.dumps({
        "out": str(OUT),
        "best_curve_arm": final["CURVE"]["BEST_CURVE_ARM"],
        "best_surface_arm": final["SURFACE"]["BEST_SURFACE_ARM"],
        "best_topology_arm": final["TOPOLOGY"]["BEST_TOPOLOGY_ARM"],
        "best_graph_arm": final["GRAPH"]["BEST_GRAPH_ARM"],
        "a3_extended_advantage": final["A3"]["A3_EXTENDED_ADVANTAGE"],
        "hash_equal": final["integrity"]["report_sha256_before"] == final["integrity"]["report_sha256_after"],
    }, indent=2))
    return final


def all_four_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = {"N": len({r["cad_id"] for r in rows}) if rows else 0}
    for field in ["Chamfer", "H95", "surface_area_relative_error", "face_count_error", "edge_count_error", "center_error", "extent_error", "Volume_Error"]:
        arm_means = {}
        for arm in ARM_DIRS:
            arm_means[arm] = mean([float(r[field]) for r in rows if r["arm"] == arm and finite(r.get(field))])
        out[field] = arm_means
        vals2 = [(arm, val) for arm, val in arm_means.items() if val is not None]
        out[f"BEST_{field}"] = min(vals2, key=lambda x: x[1])[0] if vals2 else None
    return out


def a3_advantage(final: dict[str, Any]) -> dict[str, str]:
    curve_best = final["CURVE"]["BEST_CURVE_ARM"]
    closure_best = final["CLOSURE"]["BEST_CLOSURE_ARM"]
    topo_best = final["TOPOLOGY"]["BEST_TOPOLOGY_ARM"]
    graph_best = final["GRAPH"]["BEST_GRAPH_ARM"]
    yes = sum(x == "A3" for x in [curve_best, closure_best, topo_best, graph_best])
    if yes >= 3:
        status = "ESTABLISHED"
    elif yes >= 1:
        status = "PARTIAL"
    else:
        status = "NOT_ESTABLISHED"
    return {
        "A3_CURVE_ADVANTAGE": "YES" if curve_best == "A3" else "NO",
        "A3_CLOSURE_ADVANTAGE": "YES" if closure_best == "A3" else "NO",
        "A3_TOPOLOGY_ADVANTAGE": "YES" if topo_best == "A3" else "NO",
        "A3_GRAPH_ADVANTAGE": "YES" if graph_best == "A3" else "NO",
        "A3_EXTENDED_ADVANTAGE": status,
    }


def interpretation(final: dict[str, Any]) -> dict[str, str]:
    return {
        "A0_STRENGTH": "Strong all-four-valid geometry/topology baseline when surface-only execution succeeds.",
        "A1_STRENGTH": "Strongest established program/execution arm; remains the main structure baseline unless extended metrics overturn it.",
        "A2_STRENGTH": "Best original valid-only Chamfer/H95 but coverage/common-valid effects must be reported.",
        "A3_STRENGTH": "Only accepted where frozen extended metrics rank A3 best; otherwise treated as naive all-curve fusion with interference risk.",
        "MAIN_BOTTLENECK": "Coverage plus structure/topology consistency, not Chamfer alone.",
        "NEXT_ALLOWED_STAGE": "WAIT_FOR_P1_COMPLETION",
    }


def benchmark_recommendations() -> str:
    return """# Recommended CurveCAD-Bench Metrics

## HEADLINE
- Program structure: Exact, Op-F1, Op Recall.
- Executability: Parse, STEP Export, STEP Reload with denominator N=1000.
- Geometry: Chamfer and H95 reported with geometry-valid coverage and common-valid paired subsets.
- Topology: face/edge/solid count error and valid-BRep rate.

## SECONDARY
- Surface area relative error.
- Dependency edge precision/recall/F1.
- Curve count and curve geometry assignment error.
- Placement/scale errors.

## DIAGNOSTIC
- Curve type macro-F1 under geometric assignment.
- Euler characteristic error.
- AST-aligned parameter error.
- Wire/profile closure interpretation.

## DEFERRED
- Normal consistency until a shared reliable normal tessellation is frozen.
- Manifold rate until a true manifold checker is available.
- Graph edit distance until node-cost semantics are frozen.
"""


def make_gallery(curve_table, surface_table, topo_table, program_table, case_rows) -> None:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (2200, 1450), "white")
    draw = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    mono_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    title = ImageFont.truetype(font_path, 34) if Path(font_path).exists() else ImageFont.load_default()
    head = ImageFont.truetype(font_path, 23) if Path(font_path).exists() else ImageFont.load_default()
    body = ImageFont.truetype(mono_path, 17) if Path(mono_path).exists() else ImageFont.load_default()
    draw.text((40, 30), "EXACT9998 Extended CAD Metrics", fill=(20, 20, 20), font=title)
    panels = [
        ("Curve Reconstruction", curve_table, ["Matched_Curve_Geometry_Error", "Curve_Type_Accuracy", "Closed_Wire_Rate"]),
        ("Surface / Placement", surface_table, ["Surface_Area_Relative_Error", "Center_Error", "Extent_Error"]),
        ("B-Rep Topology", topo_table, ["Face_Count_Error", "Edge_Count_Error", "Valid_BRep_Rate"]),
        ("Program Graph", program_table, ["Op-F1", "Dependency_Edge_F1", "Graph_Alignment_Coverage"]),
    ]
    y = 105
    for title_s, table, fields in panels:
        draw.rectangle((40, y, 2160, y + 270), outline=(210, 210, 210), width=2)
        draw.text((60, y + 18), title_s, fill=(30, 30, 30), font=head)
        line_y = y + 62
        header = f"{'arm':<4} " + " ".join(f"{field[:28]:>28}" for field in fields)
        draw.text((65, line_y), header, fill=(30, 30, 30), font=body)
        line_y += 34
        for row in table:
            vals = []
            for field in fields:
                val = row.get(field)
                vals.append("NA" if val is None or val == "" else f"{float(val):.5f}" if finite(val) else str(val))
            draw.text((65, line_y), f"{row['arm']:<4} " + " ".join(f"{v:>28}" for v in vals), fill=(55, 55, 55), font=body)
            line_y += 34
        y += 310
    img.save(OUT / "gallery/EXTENDED_CAD_METRIC_GALLERY.png")


def final_markdown(final: dict[str, Any]) -> str:
    lines = [
        "# EXACT9998 Extended CAD Metrics",
        "",
        f"CURRENT_GATE = `{final['CURRENT_GATE']}`",
        f"TEST_TOUCHED = `{final['TEST_TOUCHED']}`",
        f"P1_UNAFFECTED = `{final['P1_UNAFFECTED']}`",
        "",
        "## Best Arms",
        "",
        f"- BEST_CURVE_ARM: `{final['CURVE']['BEST_CURVE_ARM']}`",
        f"- BEST_CLOSURE_ARM: `{final['CLOSURE']['BEST_CLOSURE_ARM']}`",
        f"- BEST_SURFACE_ARM: `{final['SURFACE']['BEST_SURFACE_ARM']}`",
        f"- BEST_TOPOLOGY_ARM: `{final['TOPOLOGY']['BEST_TOPOLOGY_ARM']}`",
        f"- BEST_GRAPH_ARM: `{final['GRAPH']['BEST_GRAPH_ARM']}`",
        f"- A3_EXTENDED_ADVANTAGE: `{final['A3']['A3_EXTENDED_ADVANTAGE']}`",
        "",
        "## Notes",
        "",
        "- Normal consistency is `UNRELIABLE_DEFERRED`.",
        "- Manifold rate is `NOT_IMPLEMENTED_RELIABLY`.",
        "- Graph edit distance is `DEFERRED`.",
        "- All continuous valid-only metrics must be read with coverage and paired/common-valid subsets.",
        "",
        "## Integrity",
        "",
    ]
    for key, value in final["integrity"].items():
        if key.startswith("report_sha"):
            continue
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    run()
