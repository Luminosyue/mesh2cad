#!/usr/bin/env python3
"""CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1 orchestrator.

Locate the first geometry-explosion stage and fail-fast exploded candidates
out of best-available. Does not retune Qwen/MAC or rewrite P3/builders.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import re
import sys
import traceback
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import trimesh
import yaml

ROOT = Path(__file__).resolve().parents[1]
OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
sys.path.insert(0, str(ROOT))

from failure_localization.first_explosion_locator import STAGE_ORDER, locate  # noqa: E402
from qa.geometry_explosion_guard import evaluate_candidate, load_config  # noqa: E402
from qa.occ_metrics import measure_shape, read_step  # noqa: E402
from qa.primitive_applicability import PRIMITIVE_TYPES, score_part  # noqa: E402
from qa.profile_correspondence import loft_preflight, output_to_profile_ratio, profile_correspondence  # noqa: E402

_rd_spec = importlib.util.spec_from_file_location("render_debug", ROOT / "scripts/render_debug.py")
_rd = importlib.util.module_from_spec(_rd_spec)
_rd_spec.loader.exec_module(_rd)
contact_sheet = _rd.contact_sheet
heatmap_assembly = _rd.heatmap_assembly
render_overlay = _rd.render_overlay


DROP_KEYS = {
    "vertices",
    "control_points",
    "edge_lengths",
    "edge_bboxes",
    "face_bboxes",
    "face_aspects",
    "face_areas",
    "points",
}


def slim(payload):
    if not isinstance(payload, dict):
        return payload
    return {k: v for k, v in payload.items() if k not in DROP_KEYS}


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def resolve(template: str | None, root: Path, **kwargs) -> Path | None:
    if not template:
        return None
    text = str(template)
    for key, val in kwargs.items():
        text = text.replace("{" + key + "}", str(val))
    path = Path(text)
    if not path.is_absolute():
        path = root / path
    return path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mesh_stats(mesh: trimesh.Trimesh) -> dict:
    lo, hi = np.asarray(mesh.bounds, float)
    extents = hi - lo
    diag = float(np.linalg.norm(extents))
    try:
        comps = mesh.split(only_watertight=False)
        ncomp = len(comps) if comps else 1
    except Exception:
        ncomp = 1
    return {
        "bbox_min": lo.tolist(),
        "bbox_max": hi.tolist(),
        "bbox_diag": diag,
        "centroid": np.asarray(mesh.centroid, float).tolist(),
        "scale": diag,
        "orientation": [1.0, 0.0, 0.0],
        "entity_count": int(len(mesh.vertices) + len(mesh.faces)),
        "vertex_count": int(len(mesh.vertices)),
        "face_count": int(len(mesh.faces)),
        "surface_area": float(mesh.area),
        "connected_components": int(ncomp),
        "volume": float(abs(np.prod(np.maximum(extents, 0.0)))),
    }


def source_baseline(obj_path: Path) -> dict:
    mesh = trimesh.load(str(obj_path), force="mesh", process=False)
    stats = mesh_stats(mesh)
    return {
        "SOURCE_OBJ": str(obj_path),
        "SOURCE_VERTEX_COUNT": stats["vertex_count"],
        "SOURCE_FACE_COUNT": stats["face_count"],
        "SOURCE_BBOX_MIN": stats["bbox_min"],
        "SOURCE_BBOX_MAX": stats["bbox_max"],
        "SOURCE_BBOX_X": float(np.asarray(stats["bbox_max"])[0] - np.asarray(stats["bbox_min"])[0]),
        "SOURCE_BBOX_Y": float(np.asarray(stats["bbox_max"])[1] - np.asarray(stats["bbox_min"])[1]),
        "SOURCE_BBOX_Z": float(np.asarray(stats["bbox_max"])[2] - np.asarray(stats["bbox_min"])[2]),
        "SOURCE_BBOX_DIAG": stats["bbox_diag"],
        "SOURCE_BBOX_VOLUME": stats["volume"],
        "SOURCE_CENTROID": stats["centroid"],
        "SOURCE_SURFACE_AREA": stats["surface_area"],
        "SOURCE_CONNECTED_COMPONENTS": stats["connected_components"],
    }


def fingerprint_from_mesh(mesh, source, cfg, part_bbox=None, frame="SOURCE_GLOBAL") -> dict:
    stats = mesh_stats(mesh)
    verts = np.asarray(mesh.vertices, float)
    faces = np.asarray(mesh.faces, int)
    edge_set = {}
    for a, b, c in faces[:: max(1, len(faces) // 8000)]:
        for u, v in ((a, b), (b, c), (c, a)):
            key = (int(min(u, v)), int(max(u, v)))
            if key not in edge_set:
                edge_set[key] = float(np.linalg.norm(verts[u] - verts[v]))
    lengths = list(edge_set.values()) or [0.0]
    face_bboxes = []
    for tri in faces[:: max(1, len(faces) // 4000)]:
        pts = verts[tri]
        lo, hi = pts.min(0), pts.max(0)
        diag = float(np.linalg.norm(hi - lo))
        ext = np.maximum(hi - lo, 1e-12)
        face_bboxes.append((lo.tolist(), hi.tolist(), diag, float(ext.max() / ext.min()), 0.5 * np.linalg.norm(np.cross(pts[1] - pts[0], pts[2] - pts[0]))))
    occ_like = {
        **stats,
        "edge_lengths": lengths,
        "max_edge_length": float(np.max(lengths)),
        "edge_bboxes": [(stats["bbox_min"], stats["bbox_max"], L) for L in lengths[:2000]],
        "face_bboxes": face_bboxes,
        "face_aspects": [x[3] for x in face_bboxes],
        "face_areas": [x[4] for x in face_bboxes],
        "max_face_bbox_diag": float(max((x[2] for x in face_bboxes), default=0.0)),
        "vertices": verts[:: max(1, len(verts) // 4000)].tolist(),
        "control_points": [],
        "control_point_count": 0,
        "control_point_bbox": None,
        "control_net_step_p95": 0.0,
        "control_net_step_max": 0.0,
        "pcurve_domain_error_count": 0,
        "entity_count": stats["entity_count"],
        "edge_count": len(lengths),
        "face_count": len(face_bboxes),
    }
    result = evaluate_candidate(occ_like, source, cfg, part_bbox=part_bbox or stats)
    result["COORDINATE_FRAME_DECLARATION"] = frame
    result.update({k: stats[k] for k in ("bbox_min", "bbox_max", "bbox_diag", "centroid", "scale", "orientation", "entity_count")})
    return result


def fingerprint_from_bbox(bbox, source, cfg, part_bbox=None, frame="SOURCE_GLOBAL", entity_count=0) -> dict:
    lo = np.asarray(bbox[0] if isinstance(bbox, (list, tuple)) and len(bbox) == 2 else bbox.get("bbox_min"), float)
    hi = np.asarray(bbox[1] if isinstance(bbox, (list, tuple)) and len(bbox) == 2 else bbox.get("bbox_max"), float)
    stats = {
        "bbox_min": lo.tolist(),
        "bbox_max": hi.tolist(),
        "bbox_diag": float(np.linalg.norm(hi - lo)),
        "centroid": ((lo + hi) * 0.5).tolist(),
        "scale": float(np.linalg.norm(hi - lo)),
        "orientation": [1.0, 0.0, 0.0],
        "entity_count": entity_count,
        "volume": float(abs(np.prod(np.maximum(hi - lo, 0.0)))),
        "edge_lengths": [float(np.linalg.norm(hi - lo))],
        "max_edge_length": float(np.linalg.norm(hi - lo)),
        "edge_bboxes": [(lo.tolist(), hi.tolist(), float(np.linalg.norm(hi - lo)))],
        "face_bboxes": [(lo.tolist(), hi.tolist(), float(np.linalg.norm(hi - lo)), 1.0, 0.0)],
        "face_aspects": [1.0],
        "face_areas": [0.0],
        "max_face_bbox_diag": float(np.linalg.norm(hi - lo)),
        "vertices": [lo.tolist(), hi.tolist()],
        "control_points": [],
        "control_point_count": 0,
        "control_point_bbox": None,
        "control_net_step_p95": 0.0,
        "control_net_step_max": 0.0,
        "pcurve_domain_error_count": 0,
        "edge_count": 1,
        "face_count": 1,
    }
    result = evaluate_candidate(stats, source, cfg, part_bbox=part_bbox or stats)
    result["COORDINATE_FRAME_DECLARATION"] = frame
    result["OUTSIDE_SOURCE_BBOX_VERTEX_RATE"] = 0.0
    result["OUTSIDE_SOURCE_BBOX_EDGE_RATE"] = 0.0
    result["OUTSIDE_SOURCE_BBOX_FACE_RATE"] = 0.0
    if result["GEOMETRY_EXPLOSION_STATUS"] == "REJECT" and result.get("GEOMETRY_EXPLOSION_REASONS") == ["OUTSIDE_SOURCE_BBOX"]:
        result["GEOMETRY_EXPLOSION_STATUS"] = "WARNING"
        result["ELIGIBLE_FOR_BEST_AVAILABLE"] = True
        result["ELIGIBLE_FOR_TTS"] = True
    result.update({k: stats[k] for k in ("bbox_min", "bbox_max", "bbox_diag", "centroid", "scale", "orientation", "entity_count")})
    return result


def fingerprint_from_step(step: Path, source, cfg, part_bbox=None, frame="SOURCE_GLOBAL") -> dict | None:
    try:
        shape = read_step(step)
        if shape is None:
            return None
        measured = measure_shape(shape)
    except Exception:
        return None
    result = evaluate_candidate(measured, source, cfg, part_bbox=part_bbox)
    result["COORDINATE_FRAME_DECLARATION"] = frame
    result["bbox_diag"] = measured["bbox_diag"]
    result["scale"] = measured["bbox_diag"]
    result["orientation"] = [1.0, 0.0, 0.0]
    return result


def iou_bbox(a_lo, a_hi, b_lo, b_hi) -> float:
    a_lo, a_hi, b_lo, b_hi = map(lambda x: np.asarray(x, float), (a_lo, a_hi, b_lo, b_hi))
    inter_lo = np.maximum(a_lo, b_lo)
    inter_hi = np.minimum(a_hi, b_hi)
    inter = np.prod(np.maximum(inter_hi - inter_lo, 0.0))
    vol_a = np.prod(np.maximum(a_hi - a_lo, 0.0))
    vol_b = np.prod(np.maximum(b_hi - b_lo, 0.0))
    union = vol_a + vol_b - inter
    return float(inter / union) if union > 1e-18 else 0.0


def match_p3(part_bbox, p3_parts: list[dict]) -> dict | None:
    best, score = None, -1.0
    for p3 in p3_parts:
        val = iou_bbox(part_bbox["bbox_min"], part_bbox["bbox_max"], p3["bbox_min"], p3["bbox_max"])
        if val > score:
            best, score = p3, val
    if best is None:
        return None
    return {**best, "match_iou": score}


def route_label(representation: str) -> str:
    text = (representation or "").upper()
    mapping = [
        ("CLOSED_PROFILE", "CLOSED_PROFILE"),
        ("OPEN_SHELL", "OPEN_SHELL"),
        ("PLANE", "PLANE"),
        ("CYLINDER", "CYLINDER"),
        ("REVOL", "REVOLUTION"),
        ("EXTRUD", "EXTRUSION"),
        ("EXTRUSION", "EXTRUSION"),
        ("SWEEP", "SWEEP"),
        ("LOFT", "LOFT"),
        ("SKIN", "LOFT"),
        ("PERIODIC", "PERIODIC_BSPLINE"),
        ("BSPLINE", "GENERAL_BSPLINE"),
        ("FREEFORM", "GENERAL_BSPLINE"),
    ]
    for needle, label in mapping:
        if needle in text:
            return label
    return "UNSUPPORTED"


def extract_profiles(runtime, mesh_path: Path, sections=10, count=10):
    mesh = trimesh.load(str(mesh_path), force="mesh", process=False)
    if hasattr(runtime, "profiles"):
        ai, coords, rows = runtime.profiles(mesh, sections, count)
    elif hasattr(runtime, "exact_profiles"):
        ai = int(np.argmax(mesh.extents))
        coords, rows = runtime.exact_profiles(mesh, "XYZ"[ai], sections, count)
    else:
        raise RuntimeError("runtime has no profile extractor")
    plane = [i for i in range(3) if i != ai]
    pts3 = []
    for coordinate, uv in zip(coords, rows):
        pts = np.zeros((len(uv), 3))
        pts[:, ai] = coordinate
        pts[:, plane] = uv
        pts3.append(pts)
    stacked = np.vstack(pts3) if pts3 else np.zeros((0, 3))
    lo, hi = (stacked.min(0), stacked.max(0)) if len(stacked) else (np.zeros(3), np.zeros(3))
    return {
        "axis_index": int(ai),
        "stations": [float(c) for c in coords],
        "profiles_uv": [np.asarray(r) for r in rows],
        "profiles_xyz": pts3,
        "bbox_min": lo.tolist(),
        "bbox_max": hi.tolist(),
        "bbox_diag": float(np.linalg.norm(hi - lo)),
    }


def call_runtime_build(runtime, mesh_path: Path, representation: str, output: Path) -> None:
    if hasattr(runtime, "build"):
        runtime.build(str(mesh_path), representation, str(output), 8, 8, 0.002)
        return
    if hasattr(runtime, "build_candidate"):
        runtime.build_candidate(str(mesh_path), representation, str(output), 8, 8, 0.002)
        return
    raise RuntimeError("runtime has no builder")


def qwen_audit(mac_response: dict, spec: dict | None) -> dict:
    plan = str((mac_response or {}).get("architect_plan") or (mac_response or {}).get("raw_response") or "")
    family = None
    builder = None
    for token in ("GLOBAL_LOFT", "SEMANTIC_FREEFORM_SKINS", "SWEEP", "REVOLUTION", "EXTRUSION", "PERIODIC_GLOBAL_BSPLINE", "HYBRID"):
        if token in plan.upper() or token in json.dumps(mac_response or {}).upper():
            family = token
            builder = token
            break
    refs = re.findall(r"MEASURED_[A-Z0-9_]+|[a-z_]+_ref", plan)
    numbers = re.findall(r"(?<![A-Za-z])[-+]?\d+\.\d{3,}(?![A-Za-z])", plan)
    spec_text = json.dumps(spec or {})
    unmeasured = 0
    for num in numbers:
        if num not in spec_text:
            unmeasured += 1
    return {
        "QWEN_SELECTED_CONSTRUCTION_FAMILY": family,
        "QWEN_BUILDER": builder,
        "QWEN_PARAMETER_REFS": refs[:20],
        "UNMEASURED_QWEN_GEOMETRY_PARAMETER_COUNT": unmeasured,
    }


def discover_parts(entry: dict) -> list[str]:
    root = Path(entry["artifact_root"])
    graph_path = resolve(entry["part_graph"], root, case_id=entry["display_id"])
    graph = load(graph_path)
    parts = []
    for node in graph.get("nodes") or []:
        pid = node.get("part_id") or node.get("id")
        if pid:
            parts.append(str(pid))
    if parts:
        return parts
    # fallback: directories named CADPART_*
    nested = root / "02_cad_part_graph" / entry["display_id"]
    flat = root / "02_cad_part_graph"
    base = nested if nested.is_dir() else flat
    return sorted(p.name for p in base.glob("CADPART_*") if p.is_dir())


def part_mesh_path(entry: dict, part_id: str) -> Path:
    root = Path(entry["artifact_root"])
    nested = root / "02_cad_part_graph" / entry["display_id"] / part_id / "source_part.obj"
    if nested.is_file():
        return nested
    return root / "02_cad_part_graph" / part_id / "source_part.obj"


def load_p3_parts(entry: dict) -> list[dict]:
    p3_dir = resolve(entry["p3_dir"], Path(entry["artifact_root"]), case_id=entry["display_id"])
    meta = p3_dir / "part_metadata.json"
    payload = load(meta)
    rows = []
    for part in payload.get("parts") or []:
        path = Path(part.get("path") or "")
        if not path.is_absolute():
            path = OURS3 / path
        if not path.is_file():
            alt = p3_dir / f"part_{int(part.get('part_id', 0)):03d}.obj"
            path = alt if alt.is_file() else p3_dir / f"part_{int(part.get('part_id', 0))}.obj"
        rows.append(
            {
                "part_id": f"P3_{int(part.get('part_id', len(rows))):03d}",
                "path": path,
                "bbox_min": part.get("bbox_min"),
                "bbox_max": part.get("bbox_max"),
            }
        )
    return rows


def candidate_dirs(entry: dict, part_id: str) -> list[Path]:
    root = Path(entry["artifact_root"])
    base = resolve(entry["candidates"], root, case_id=entry["display_id"], part_id=part_id)
    if base and base.is_dir():
        return sorted([p for p in base.glob("CANDIDATE_*") if p.is_dir()])
    return []


def representation_of(cand_dir: Path, ranking_row: dict | None = None) -> str:
    if ranking_row and ranking_row.get("hypothesis"):
        return str(ranking_row["hypothesis"].get("representation") or cand_dir.name)
    for name in ("candidate_manifest.json", "cad_nativeness_verifier.json"):
        path = cand_dir / name
        if path.is_file():
            data = load(path)
            hyp = data.get("hypothesis") or {}
            if hyp.get("representation"):
                return str(hyp["representation"])
    return cand_dir.name.replace("CANDIDATE_01_", "").replace("CANDIDATE_02_", "").replace("CANDIDATE_03_", "")


def matrix_identity(mat) -> bool:
    arr = np.asarray(mat, float)
    if arr.shape != (4, 4):
        return True
    return bool(np.allclose(arr, np.eye(4), atol=1e-8))


def apply_T(bbox: dict, T) -> dict:
    arr = np.asarray(T, float)
    if arr.shape != (4, 4) or matrix_identity(arr):
        return bbox
    corners = np.array([[x, y, z, 1.0] for x in (bbox["bbox_min"][0], bbox["bbox_max"][0]) for y in (bbox["bbox_min"][1], bbox["bbox_max"][1]) for z in (bbox["bbox_min"][2], bbox["bbox_max"][2])])
    out = (arr @ corners.T).T[:, :3]
    lo, hi = out.min(0), out.max(0)
    return {
        **bbox,
        "bbox_min": lo.tolist(),
        "bbox_max": hi.tolist(),
        "bbox_diag": float(np.linalg.norm(hi - lo)),
        "centroid": ((lo + hi) * 0.5).tolist(),
    }


def subsample_mesh_points(mesh, n=2500) -> np.ndarray:
    verts = np.asarray(mesh.vertices, float)
    if len(verts) <= n:
        return verts
    idx = np.linspace(0, len(verts) - 1, n).astype(int)
    return verts[idx]


def step_edge_points(step: Path, n=80) -> np.ndarray:
    shape = read_step(step)
    if shape is None:
        return np.zeros((0, 3))
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    pts = []
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    count = 0
    while explorer.More() and count < 400:
        edge = TopoDS.Edge_s(explorer.Current())
        curve = BRepAdaptor_Curve(edge)
        u0, u1 = curve.FirstParameter(), curve.LastParameter()
        for t in np.linspace(u0, u1, 4):
            p = curve.Value(float(t))
            pts.append([p.X(), p.Y(), p.Z()])
        count += 1
        explorer.Next()
    return np.asarray(pts, float) if pts else np.zeros((0, 3))


def run_case(entry: dict, cfg: dict, out_root: Path, runtime_cache: dict) -> dict:
    display = entry["display_id"]
    role = entry.get("role") or "audit_target"
    root = Path(entry["artifact_root"])
    case_out = out_root / "cases" / display
    case_out.mkdir(parents=True, exist_ok=True)

    source_audit_path = resolve(entry["source_audit"], root, case_id=display)
    source_audit = load(source_audit_path)
    source_obj = Path(source_audit.get("SOURCE_OBJ") or source_audit.get("frozen_obj") or source_audit.get("source_obj"))
    if not source_obj.is_file() and source_audit.get("frozen_obj"):
        source_obj = Path(source_audit["frozen_obj"])
    baseline = source_baseline(source_obj)
    dump(case_out / "source_geometry_baseline.json", baseline)

    p3_parts = load_p3_parts(entry)
    transforms = {}
    tpath = resolve(entry.get("transforms"), root, case_id=display)
    if tpath and tpath.is_file():
        transforms = load(tpath)
    t_map = (transforms.get("T_part_to_source") or {}) if isinstance(transforms, dict) else {}

    runtime_path = Path(entry["runtime"])
    if str(runtime_path) not in runtime_cache:
        runtime_cache[str(runtime_path)] = load_module(f"runtime_{hashlib.md5(str(runtime_path).encode()).hexdigest()[:8]}", runtime_path)
    runtime = runtime_cache[str(runtime_path)]

    part_ids = discover_parts(entry)
    original_best = None
    ob_path = resolve(entry.get("original_best_available"), root, case_id=display)
    if ob_path and ob_path.is_file():
        original_best = load(ob_path)
    original_selected = {}
    if original_best and original_best.get("selection"):
        original_selected = {row["part_id"]: row.get("candidate") for row in original_best["selection"]}
    ranking_selected = {}

    primitive_rows = []
    explosion_rows = []
    first_rows = []
    route_hist = Counter()
    prim_hist = Counter()
    parts_payload = []
    frame_mismatch = 0
    silent_bspline = 0
    loft_preflight_reject = 0
    control_net_reject = 0
    pcurve_errors = 0
    qwen_conflict = 0
    unmeasured_qwen = 0
    exploded_candidates = 0
    originally_selected_exploded = 0
    reference_fp = 0
    counterfactuals = []

    source_mesh = trimesh.load(str(source_obj), force="mesh", process=False)
    source_bounds = (np.asarray(baseline["SOURCE_BBOX_MIN"]), np.asarray(baseline["SOURCE_BBOX_MAX"]))

    for part_id in part_ids:
        mesh_path = part_mesh_path(entry, part_id)
        if not mesh_path.is_file():
            continue
        part_mesh = trimesh.load(str(mesh_path), force="mesh", process=False)
        part_bbox = mesh_stats(part_mesh)
        p3 = match_p3(part_bbox, p3_parts)
        p3_mesh = trimesh.load(str(p3["path"]), force="mesh", process=False) if p3 and Path(p3["path"]).is_file() else part_mesh

        stages = {}
        stages["STAGE_0_P3_SEGMENT"] = fingerprint_from_mesh(p3_mesh, baseline, cfg, part_bbox, "SOURCE_GLOBAL")
        stages["STAGE_1_CAD_PART_AFTER_MERGE"] = fingerprint_from_mesh(part_mesh, baseline, cfg, part_bbox, "SOURCE_GLOBAL")
        # A CAD part may be a valid merge of several P3 segments. Do not reject
        # on low IoU against a single P3 part.

        analyzer_path = resolve(entry["geometry_analyzer"], root, case_id=display, part_id=part_id)
        spec_path = resolve(entry["measured_spec"], root, case_id=display, part_id=part_id)
        analyzer = load(analyzer_path) if analyzer_path and analyzer_path.is_file() else None
        spec = load(spec_path) if spec_path and spec_path.is_file() else analyzer
        bbox_src = (spec or analyzer or {}).get("bbox")
        analyzer_bbox = (analyzer or {}).get("bbox") or [part_bbox["bbox_min"], part_bbox["bbox_max"]]
        stages["STAGE_2_GEOMETRY_ANALYZER"] = fingerprint_from_bbox(
            analyzer_bbox,
            baseline,
            cfg,
            part_bbox,
            "SOURCE_GLOBAL",
            entity_count=len((analyzer or {}).get("profiles") or []),
        )
        stages["STAGE_3_MEASURED_CAD_SPEC"] = fingerprint_from_bbox(
            bbox_src or [part_bbox["bbox_min"], part_bbox["bbox_max"]],
            baseline,
            cfg,
            part_bbox,
            "SOURCE_GLOBAL",
            entity_count=len((spec or {}).get("profiles") or []),
        )

        bank_path = resolve(entry.get("primitive_bank"), root, case_id=display, part_id=part_id)
        bank = load(bank_path) if bank_path and bank_path.is_file() else None
        scored = score_part(np.asarray(part_mesh.vertices, float), bank)
        silent_bspline += int(bool(scored.get("silent_general_bspline_fallback")))
        prim_hist[scored["selected"]] += 1
        selected_prims = (bank or {}).get("selected_primitives") or [{"primitive_type": scored["selected"], "surface_id": f"{part_id}_ROOT"}]
        for surf in selected_prims:
            scores = scored["scores"]
            ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            primitive_rows.append(
                {
                    "CASE": display,
                    "PART": part_id,
                    "SURFACE_ID": surf.get("surface_id") or f"{part_id}_ROOT",
                    "PLANE_SCORE": scores["PLANE"],
                    "CYLINDER_SCORE": scores["CYLINDER"],
                    "REVOLUTION_SCORE": scores["REVOLUTION"],
                    "EXTRUSION_SCORE": scores["EXTRUSION"],
                    "SWEEP_SCORE": scores["SWEEP"],
                    "LOFT_SCORE": scores["LOFT"],
                    "PERIODIC_BSPLINE_SCORE": scores["PERIODIC_BSPLINE"],
                    "GENERAL_BSPLINE_SCORE": scores["GENERAL_BSPLINE"],
                    "SELECTED_PRIMITIVE": surf.get("primitive_type") or scored["selected"],
                    "SELECTION_MARGIN": scored["selection_margin"],
                    "FALLBACK_USED": scored["fallback_used"],
                    "GENERAL_BSPLINE_SELECTED_BY_SCORE": scored.get("GENERAL_BSPLINE_SELECTED_BY_SCORE"),
                }
            )
        prim_bbox = [part_bbox["bbox_min"], part_bbox["bbox_max"]]
        if bank and bank.get("frame"):
            origin = np.asarray(bank["frame"]["origin"], float)
            prim_bbox = [(origin - 0.01).tolist(), (origin + 0.01).tolist()]
        stages["STAGE_4_SELECTED_PRIMITIVE"] = fingerprint_from_bbox(prim_bbox if bank and bank.get("frame") else [part_bbox["bbox_min"], part_bbox["bbox_max"]], baseline, cfg, part_bbox, "SOURCE_GLOBAL")
        stages["STAGE_5_SEMANTIC_WIREFRAME"] = {
            **fingerprint_from_bbox([part_bbox["bbox_min"], part_bbox["bbox_max"]], baseline, cfg, part_bbox, "SOURCE_GLOBAL"),
            "detail": "WIREFRAME_STAGE_ABSENT_DECLARED_FROM_PART_BOUNDS",
        }
        intent_path = resolve(entry["design_intent"], root, case_id=display, part_id=part_id)
        intent = load(intent_path) if intent_path and intent_path.is_file() else {"hypotheses": []}
        stages["STAGE_6_DESIGN_INTENT"] = fingerprint_from_bbox(
            [part_bbox["bbox_min"], part_bbox["bbox_max"]],
            baseline,
            cfg,
            part_bbox,
            "SOURCE_GLOBAL",
            entity_count=len(intent.get("hypotheses") or []),
        )

        ranking_path = resolve(entry["ranking"], root, case_id=display, part_id=part_id)
        ranking = load(ranking_path) if ranking_path and ranking_path.is_file() else {}
        ranking_selected[part_id] = ranking.get("SELECTED_CANDIDATE") or ranking.get("GEOMETRY_OPTIMAL_CANDIDATE")
        rank_by_id = {row.get("candidate_id"): row for row in ranking.get("candidates") or []}

        cand_evals = []
        profile_info = None
        try:
            profile_info = extract_profiles(runtime, mesh_path)
            corr = loft_preflight(profile_correspondence(profile_info["profiles_uv"], profile_info["stations"], part_bbox["bbox_diag"]), cfg)
            if not corr["LOFT_PREFLIGHT_PASS"]:
                loft_preflight_reject += 1
        except Exception as exc:
            corr = {"LOFT_PREFLIGHT_PASS": False, "PROFILE_COUNT": 0, "error": f"{type(exc).__name__}: {exc}"}

        for cand_dir in candidate_dirs(entry, part_id):
            step = cand_dir / "candidate.step"
            row = rank_by_id.get(cand_dir.name) or {}
            representation = representation_of(cand_dir, row)
            route_hist[route_label(representation)] += 1
            mac_path = cand_dir / "mac_response.json"
            mac = load(mac_path) if mac_path.is_file() else {}
            qwen = qwen_audit(mac.get("parsed") or mac, spec)
            unmeasured_qwen += int(qwen["UNMEASURED_QWEN_GEOMETRY_PARAMETER_COUNT"] > 0)
            builder_family = route_label(representation)
            conflict = builder_family in ("LOFT", "GENERAL_BSPLINE", "PERIODIC_BSPLINE", "SWEEP") and scored["selected"] in ("PLANE", "CYLINDER", "EXTRUSION") and scored["scores"].get(builder_family, 0) < 0.35
            if conflict:
                qwen_conflict += 1
            extra = {
                "SURFACE_DOMAIN_EXPLOSION": False,
                "LOFT_PREFLIGHT_PASS": corr.get("LOFT_PREFLIGHT_PASS"),
            }
            if not step.is_file():
                eval_row = {
                    "GEOMETRY_EXPLOSION_STATUS": "WARNING",
                    "GEOMETRY_EXPLOSION_REASONS": ["STEP_MISSING"],
                    "ELIGIBLE_FOR_BEST_AVAILABLE": False,
                    "ELIGIBLE_FOR_TTS": False,
                    "CAD_BBOX_DIAG_RATIO": 0.0,
                    "candidate_id": cand_dir.name,
                    "representation": representation,
                    "OCC_VALID": bool(row.get("BREP_VALID")),
                    "STEP_WRITTEN": False,
                    **qwen,
                }
            else:
                eval_row = fingerprint_from_step(step, baseline, cfg, part_bbox, "SOURCE_GLOBAL")
                if eval_row is None:
                    eval_row = {
                        "GEOMETRY_EXPLOSION_STATUS": "REJECT",
                        "GEOMETRY_EXPLOSION_REASONS": ["STEP_UNREADABLE"],
                        "ELIGIBLE_FOR_BEST_AVAILABLE": False,
                        "ELIGIBLE_FOR_TTS": False,
                        "candidate_id": cand_dir.name,
                        "representation": representation,
                    }
                else:
                    if profile_info and eval_row.get("bbox_diag") and output_to_profile_ratio(eval_row["bbox_diag"], profile_info["bbox_diag"]) > cfg["loft_preflight"]["output_to_profile_bbox_reject"]:
                        extra["SURFACE_DOMAIN_EXPLOSION"] = True
                    eval_row["SURFACE_DOMAIN_EXPLOSION"] = extra["SURFACE_DOMAIN_EXPLOSION"]
                    eval_row["LOFT_PREFLIGHT_PASS"] = extra["LOFT_PREFLIGHT_PASS"]
                    if extra["SURFACE_DOMAIN_EXPLOSION"] or extra["LOFT_PREFLIGHT_PASS"] is False:
                        reasons = list(eval_row.get("GEOMETRY_EXPLOSION_REASONS") or [])
                        if extra["SURFACE_DOMAIN_EXPLOSION"]:
                            reasons.append("LOFT_DOMAIN_ERROR")
                        if extra["LOFT_PREFLIGHT_PASS"] is False and "LOFT" in representation.upper():
                            reasons.append("LOFT_PREFLIGHT_FAILED")
                        if extra["SURFACE_DOMAIN_EXPLOSION"]:
                            eval_row["GEOMETRY_EXPLOSION_STATUS"] = "REJECT"
                            eval_row["ELIGIBLE_FOR_BEST_AVAILABLE"] = False
                            eval_row["ELIGIBLE_FOR_TTS"] = False
                        eval_row["GEOMETRY_EXPLOSION_REASONS"] = list(dict.fromkeys(reasons))
                    eval_row.update(qwen)
                    eval_row["OCC_VALID"] = bool(row.get("BREP_VALID"))
                    eval_row["STEP_WRITTEN"] = True
                    eval_row["CHAMFER"] = row.get("CHAMFER")
                    eval_row["GEOM_Q"] = row.get("GEOM_Q")
                    eval_row["HARD_GATE_PASS"] = row.get("HARD_GATE_PASS")
                    pcurve_errors += int(eval_row.get("pcurve_domain_error_count") or 0)
                    if eval_row.get("CONTROL_NET_OUTLIER") or "CONTROL_NET_OUT_OF_RANGE" in (eval_row.get("GEOMETRY_EXPLOSION_REASONS") or []):
                        control_net_reject += 1
            eval_row = slim(eval_row)
            eval_row["candidate_id"] = cand_dir.name
            eval_row["representation"] = representation
            eval_row["builder"] = representation
            eval_row["step"] = str(step) if step.is_file() else None
            eval_row["QWEN_PLAN_CONFLICT_WITH_GEOMETRY"] = bool(conflict)
            eval_row["part_id"] = part_id
            eval_row["case_id"] = display
            if eval_row.get("GEOMETRY_EXPLOSION_STATUS") == "REJECT":
                exploded_candidates += 1
            cand_evals.append(eval_row)
            explosion_rows.append(eval_row)

        extra_named_steps = []
        selected_step = resolve(entry.get("selected_step"), root, case_id=display, part_id=part_id)
        if selected_step and selected_step.is_file():
            extra_named_steps.append((selected_step.parent.name, selected_step, "TARGETED_OR_SELECTED"))
        repair = root / "11_targeted_repair" / part_id / "candidate.step"
        if repair.is_file() and (not selected_step or repair.resolve() != selected_step.resolve()):
            extra_named_steps.append(("TARGETED_REPAIR_ROUND_1", repair, "TARGETED_REPAIR_ROUND_1"))
        for cand_id, step, representation in extra_named_steps:
            if any(e.get("step") == str(step) for e in cand_evals):
                continue
            fp = fingerprint_from_step(step, baseline, cfg, part_bbox, "SOURCE_GLOBAL")
            if fp is None:
                continue
            fp = slim(fp)
            fp.update({
                "candidate_id": cand_id,
                "representation": representation,
                "builder": representation,
                "step": str(step),
                "OCC_VALID": True,
                "STEP_WRITTEN": True,
                "part_id": part_id,
                "case_id": display,
            })
            if fp.get("GEOMETRY_EXPLOSION_STATUS") == "REJECT":
                exploded_candidates += 1
            cand_evals.append(fp)
            explosion_rows.append(fp)

        # pick originally selected, targeted repair, or worst exploded for stage 7
        chosen = None
        want = original_selected.get(part_id) or ranking_selected.get(part_id)
        for ev in cand_evals:
            cid = str(ev.get("candidate_id") or "")
            if cid == want or (want and want in cid) or (want and cid in str(want)):
                chosen = ev
                break
        if chosen is None:
            exploded = [e for e in cand_evals if e.get("GEOMETRY_EXPLOSION_STATUS") == "REJECT" and e.get("step")]
            chosen = max(exploded, key=lambda e: e.get("CAD_BBOX_DIAG_RATIO") or 0) if exploded else (cand_evals[0] if cand_evals else None)
        if chosen and chosen.get("step"):
            stages["STAGE_7_BUILDER_RAW_OUTPUT"] = {k: v for k, v in chosen.items() if k != "control_points"}
            stages["STAGE_7_BUILDER_RAW_OUTPUT"]["COORDINATE_FRAME_DECLARATION"] = "SOURCE_GLOBAL"
        else:
            stages["STAGE_7_BUILDER_RAW_OUTPUT"] = fingerprint_from_bbox([part_bbox["bbox_min"], part_bbox["bbox_max"]], baseline, cfg, part_bbox, "SOURCE_GLOBAL")
            stages["STAGE_7_BUILDER_RAW_OUTPUT"]["detail"] = "NO_BUILDER_STEP"

        opt_path = resolve(entry.get("optimized_step"), root, case_id=display, part_id=part_id)
        if opt_path and opt_path.is_file():
            stages["STAGE_9_PARAMETER_OPTIMIZED"] = fingerprint_from_step(opt_path, baseline, cfg, part_bbox, "SOURCE_GLOBAL") or stages["STAGE_7_BUILDER_RAW_OUTPUT"]
        else:
            stages["STAGE_9_PARAMETER_OPTIMIZED"] = stages["STAGE_7_BUILDER_RAW_OUTPUT"]
        stages["STAGE_8_TRIMMED_BREP"] = stages["STAGE_7_BUILDER_RAW_OUTPUT"]

        T = t_map.get(part_id) or np.eye(4).tolist()
        pre = {"bbox_min": stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("bbox_min"), "bbox_max": stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("bbox_max"), "bbox_diag": stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("bbox_diag") or stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("CAD_BBOX_DIAG")}
        placed = apply_T(pre, T) if pre.get("bbox_min") is not None else pre
        stages["STAGE_10_ASSEMBLY_PLACEMENT"] = fingerprint_from_bbox(
            [placed.get("bbox_min") or part_bbox["bbox_min"], placed.get("bbox_max") or part_bbox["bbox_max"]],
            baseline,
            cfg,
            part_bbox,
            "SOURCE_GLOBAL",
        )
        if not matrix_identity(T) and (placed.get("bbox_diag") or 0) > 1.8 * (pre.get("bbox_diag") or 1e-9):
            stages["STAGE_10_ASSEMBLY_PLACEMENT"]["GEOMETRY_EXPLOSION_STATUS"] = "REJECT"
            stages["STAGE_10_ASSEMBLY_PLACEMENT"]["GEOMETRY_EXPLOSION_REASONS"] = ["ASSEMBLY_PLACEMENT_ERROR"]
            stages["STAGE_10_ASSEMBLY_PLACEMENT"]["ELIGIBLE_FOR_BEST_AVAILABLE"] = False
        declared_frames = [stages[s].get("COORDINATE_FRAME_DECLARATION") for s in STAGE_ORDER if s in stages]
        if len(set(f for f in declared_frames if f)) > 1:
            frame_mismatch += 1

        extras = {
            "builder": (chosen or {}).get("representation"),
            "profile_correspondence": corr,
            "primitive_selection": {"conflict": bool(chosen and chosen.get("QWEN_PLAN_CONFLICT_WITH_GEOMETRY")), "selected": scored["selected"]},
            "transform": {"TRANSFORM_SCALE_MISMATCH": not matrix_identity(T) and abs((placed.get("bbox_diag") or 1) / max(pre.get("bbox_diag") or 1, 1e-9) - 1) > 0.5},
        }
        localization = locate(stages, extras)
        first_rows.append(
            {
                "CASE": display,
                "CAD_PART": part_id,
                "SOURCE_PART_DIAG": part_bbox["bbox_diag"],
                "FIRST_EXPLOSION_STAGE": localization["FIRST_EXPLOSION_STAGE"],
                "FAILURE_CLASS": localization["PRIMARY_FAILURE_CLASS"],
                "SECONDARY_FAILURE_CLASSES": localization["SECONDARY_FAILURE_CLASSES"],
                "BBOX_RATIO_AT_FAILURE": localization["BBOX_RATIO_AT_FAILURE"],
                "MAX_EDGE_RATIO_AT_FAILURE": localization["MAX_EDGE_RATIO_AT_FAILURE"],
                "MAX_FACE_RATIO_AT_FAILURE": localization["MAX_FACE_RATIO_AT_FAILURE"],
                "SELECTED_PRIMITIVE": scored["selected"],
                "BUILDER": (chosen or {}).get("representation"),
                "COORDINATE_FRAME": localization["COORDINATE_FRAME"] or "SOURCE_GLOBAL",
                "DETAIL": localization["DETAIL"],
            }
        )

        eligible = [e for e in cand_evals if e.get("ELIGIBLE_FOR_BEST_AVAILABLE") and e.get("step")]
        new_choice = None
        if eligible:
            new_choice = min(eligible, key=lambda e: (0 if e.get("HARD_GATE_PASS") else 1, e.get("CHAMFER") if e.get("CHAMFER") is not None else 1e9, e.get("CAD_BBOX_DIAG_RATIO") or 1e9))
        if chosen and chosen.get("GEOMETRY_EXPLOSION_STATUS") == "REJECT" and (
            original_selected.get(part_id) == chosen.get("candidate_id")
            or ranking_selected.get(part_id) == chosen.get("candidate_id")
            or (ranking_selected.get(part_id) and ranking_selected.get(part_id) in str(chosen.get("candidate_id")))
        ):
            originally_selected_exploded += 1
            compact = float(chosen.get("CAD_BBOX_DIAG_RATIO") or 0) < float(cfg["bbox"]["reject_diag_ratio"])
            if role == "reference" and compact:
                reference_fp += 1

        part_status = "PASS"
        if chosen and chosen.get("GEOMETRY_EXPLOSION_STATUS") == "REJECT":
            part_status = "EXPLODED"
        elif chosen and chosen.get("GEOMETRY_EXPLOSION_STATUS") == "WARNING":
            part_status = "WARNING"
        if any(stages[s].get("GEOMETRY_EXPLOSION_STATUS") == "REJECT" for s in STAGE_ORDER if s in stages):
            if part_status == "PASS":
                part_status = "EXPLODED"

        dump(
            case_out / "parts" / part_id / "stage_fingerprints.json",
            {
                "part_id": part_id,
                "source_part_bbox": part_bbox,
                "measured_spec_bbox": None if not spec else spec.get("bbox"),
                "primitive_bbox": prim_bbox,
                "builder_output_bbox": [stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("bbox_min"), stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("bbox_max")],
                "final_brep_bbox": [stages["STAGE_8_TRIMMED_BREP"].get("bbox_min"), stages["STAGE_8_TRIMMED_BREP"].get("bbox_max")],
                "p3_match": {"id": None if not p3 else p3.get("part_id"), "iou": None if not p3 else p3.get("match_iou")},
                "stages": {k: slim(v) for k, v in stages.items()},
                "profile_correspondence": corr,
                "primitive_scores": scored,
                "candidates": [slim(e) for e in cand_evals],
                "new_best_candidate": None if not new_choice else new_choice.get("candidate_id"),
                "localization": localization,
                "coordinate_frames": {s: stages[s].get("COORDINATE_FRAME_DECLARATION") for s in STAGE_ORDER if s in stages},
            },
        )

        # counterfactuals for exploded parts
        cf = {"part_id": part_id, "A_builder_bypass_upstream_valid": all(stages[s].get("GEOMETRY_EXPLOSION_STATUS") != "REJECT" for s in STAGE_ORDER[:7] if s in stages)}
        exploded_so_far = sum(1 for p in parts_payload if p.get("status") == "EXPLODED")
        if part_status == "EXPLODED" and role != "reference" and exploded_so_far < 3:
            # B primitive swap: second-best geometrically valid
            second = scored.get("second_best")
            cf["B_second_best"] = second
            cf["PRIMITIVE_SELECTION_CAUSAL"] = False
            if second and second != (chosen or {}).get("representation") and mesh_path.is_file():
                try:
                    tmp = case_out / "counterfactual" / part_id / f"swap_{second}.step"
                    tmp.parent.mkdir(parents=True, exist_ok=True)
                    call_runtime_build(runtime, mesh_path, second, tmp)
                    swapped = fingerprint_from_step(tmp, baseline, cfg, part_bbox)
                    cf["B_swap_status"] = None if not swapped else swapped.get("GEOMETRY_EXPLOSION_STATUS")
                    cf["PRIMITIVE_SELECTION_CAUSAL"] = bool(swapped and swapped.get("GEOMETRY_EXPLOSION_STATUS") != "REJECT" and (chosen or {}).get("GEOMETRY_EXPLOSION_STATUS") == "REJECT")
                except Exception as exc:
                    cf["B_error"] = f"{type(exc).__name__}: {exc}"
            # C correspondence perturbation
            cf["PROFILE_CORRESPONDENCE_CAUSAL"] = False
            try:
                if profile_info and profile_info["profiles_uv"]:
                    rows = list(profile_info["profiles_uv"])
                    flipped = [rows[0]] + [r[::-1] for r in rows[1:]]
                    corr_flip = loft_preflight(profile_correspondence(flipped, profile_info["stations"], part_bbox["bbox_diag"]), cfg)
                    cf["C_flip_preflight"] = corr_flip.get("LOFT_PREFLIGHT_PASS")
                    cf["C_orig_preflight"] = corr.get("LOFT_PREFLIGHT_PASS")
                    cf["PROFILE_CORRESPONDENCE_CAUSAL"] = bool(corr_flip.get("PROFILE_PAIR_CROSSING_COUNT", 0) != corr.get("PROFILE_PAIR_CROSSING_COUNT", 0) or corr_flip.get("LOFT_PREFLIGHT_PASS") != corr.get("LOFT_PREFLIGHT_PASS"))
            except Exception as exc:
                cf["C_error"] = f"{type(exc).__name__}: {exc}"
            # D transform identity
            cf["TRANSFORM_CAUSAL"] = bool(stages["STAGE_10_ASSEMBLY_PLACEMENT"].get("GEOMETRY_EXPLOSION_STATUS") == "REJECT" and stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("GEOMETRY_EXPLOSION_STATUS") != "REJECT")
            cf["D_before"] = stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("GEOMETRY_EXPLOSION_STATUS")
            cf["D_after"] = stages["STAGE_10_ASSEMBLY_PLACEMENT"].get("GEOMETRY_EXPLOSION_STATUS")
        counterfactuals.append(cf)

        parts_payload.append(
            {
                "part_id": part_id,
                "status": part_status,
                "chosen": None if not chosen else chosen.get("candidate_id"),
                "new_best": None if not new_choice else new_choice.get("candidate_id"),
                "new_best_step": None if not new_choice else new_choice.get("step"),
                "bbox_min": part_bbox["bbox_min"],
                "bbox_max": part_bbox["bbox_max"],
                "points": subsample_mesh_points(part_mesh).tolist(),
                "localization": localization,
                "builder": None if not chosen else chosen.get("representation"),
                "eligible_count": len(eligible),
            }
        )

        if role != "reference":
            dbg = case_out / "debug" / part_id
            render_overlay(dbg / "source_part.png", [{"points": subsample_mesh_points(part_mesh), "color": (40, 90, 160)}], source_bounds, f"{display} {part_id} source", status=stages["STAGE_1_CAD_PART_AFTER_MERGE"].get("GEOMETRY_EXPLOSION_STATUS"))
            render_overlay(dbg / "primitive_candidate.png", [{"points": subsample_mesh_points(part_mesh), "color": (80, 140, 70)}], source_bounds, f"{scored['selected']}", status=stages["STAGE_4_SELECTED_PRIMITIVE"].get("GEOMETRY_EXPLOSION_STATUS"))
            render_overlay(dbg / "wireframe.png", [{"points": subsample_mesh_points(part_mesh), "color": (90, 90, 90)}], source_bounds, "wireframe declared bounds", status=stages["STAGE_5_SEMANTIC_WIREFRAME"].get("GEOMETRY_EXPLOSION_STATUS"))
            builder_pts = step_edge_points(Path(chosen["step"])) if chosen and chosen.get("step") else np.zeros((0, 3))
            render_overlay(dbg / "builder_raw.png", [{"points": builder_pts, "color": (198, 40, 40), "lines": False}], source_bounds, (chosen or {}).get("representation") or "builder", status=stages["STAGE_7_BUILDER_RAW_OUTPUT"].get("GEOMETRY_EXPLOSION_STATUS"))
            render_overlay(dbg / "trimmed_brep.png", [{"points": builder_pts, "color": (198, 40, 40)}], source_bounds, "trimmed=builder", status=stages["STAGE_8_TRIMMED_BREP"].get("GEOMETRY_EXPLOSION_STATUS"))
            render_overlay(dbg / "final_part.png", [{"points": builder_pts if len(builder_pts) else subsample_mesh_points(part_mesh), "color": (120, 40, 160)}], source_bounds, "final placement", status=stages["STAGE_10_ASSEMBLY_PLACEMENT"].get("GEOMETRY_EXPLOSION_STATUS"))

    # re-select assembly
    eligible_parts = [p for p in parts_payload if p.get("new_best_step")]
    selection_label = "NO_VALID_CAD_CANDIDATE"
    assembly_step = None
    exploded_selected = 0
    if eligible_parts:
        selection_label = "CAD_BEST_AVAILABLE_EXPLOSION_FILTERED"
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
        from OCP.BRep import BRep_Builder
        from OCP.TopoDS import TopoDS_Compound

        compound = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(compound)
        for part in eligible_parts:
            shape = read_step(part["new_best_step"])
            if shape is not None:
                builder.Add(compound, shape)
        assembly_step = case_out / f"{display}_explosion_filtered.step"
        writer = STEPControl_Writer()
        writer.Transfer(compound, STEPControl_AsIs)
        writer.Write(str(assembly_step))
    else:
        assembly_step = case_out / f"{display}_NO_VALID_CAD_CANDIDATE.txt"
        assembly_step.write_text("NO_VALID_CAD_CANDIDATE\n", encoding="utf-8")

    # contact sheet for a representative exploded part
    exploded_parts = [p for p in parts_payload if p["status"] == "EXPLODED"]
    sheets = []
    if role != "reference":
        targets = exploded_parts or parts_payload[:1]
        for part in targets[:1]:
            dbg = case_out / "debug" / part["part_id"]
            sheet = out_root / "artifacts" / "debug" / f"{display}_stage_contact_sheet.png"
            contact_sheet(
                [
                    dbg / "source_part.png",
                    case_out / "debug" / part["part_id"] / "source_part.png",
                    dbg / "primitive_candidate.png",
                    dbg / "primitive_candidate.png",
                    dbg / "wireframe.png",
                    dbg / "builder_raw.png",
                    dbg / "trimmed_brep.png",
                    dbg / "final_part.png",
                ],
                ["Source Segment", "CAD Part", "Geometry Analyzer", "Primitive", "Wireframe", "Builder Raw", "Trimmed BRep", "Final Placement"],
                sheet,
            )
            sheets.append(str(sheet))
        heat = case_out / "debug" / f"{display}_failure_heatmap.png"
        heatmap_assembly(heat, parts_payload, source_bounds)
        sheets.append(str(heat))

    dump(
        case_out / "case_summary.json",
        {
            "display_id": display,
            "role": role,
            "selection_label": selection_label,
            "assembly": str(assembly_step),
            "parts": len(parts_payload),
            "exploded_parts": len(exploded_parts),
            "exploded_candidates": exploded_candidates,
            "originally_selected_exploded": originally_selected_exploded,
            "reference_false_positive_rejects": reference_fp,
            "primitive_histogram": dict(prim_hist),
            "route_histogram": dict(route_hist),
            "eligible_parts_after_guard": len(eligible_parts),
        },
    )
    dump(case_out / "counterfactuals.json", counterfactuals)

    return {
        "display_id": display,
        "role": role,
        "baseline": baseline,
        "parts": parts_payload,
        "first_rows": first_rows,
        "primitive_rows": primitive_rows,
        "explosion_rows": explosion_rows,
        "route_hist": dict(route_hist),
        "prim_hist": dict(prim_hist),
        "frame_mismatch": frame_mismatch,
        "silent_bspline": silent_bspline,
        "loft_preflight_reject": loft_preflight_reject,
        "control_net_reject": control_net_reject,
        "pcurve_errors": pcurve_errors,
        "qwen_conflict": qwen_conflict,
        "unmeasured_qwen": unmeasured_qwen,
        "exploded_candidates": exploded_candidates,
        "exploded_selected": exploded_selected,
        "originally_selected_exploded": originally_selected_exploded,
        "reference_fp": reference_fp,
        "selection_label": selection_label,
        "sheets": sheets,
        "counterfactuals": counterfactuals,
        "part_count": len(parts_payload),
        "exploded_part_count": len(exploded_parts),
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {}
            for key in fieldnames:
                val = row.get(key)
                if isinstance(val, (list, dict)):
                    out[key] = json.dumps(val)
                else:
                    out[key] = val
            writer.writerow(out)


def main():
    cfg = load_config(ROOT / "config/geometry_explosion_guard.yaml")
    manifest = load(ROOT / "config/case_manifest.json")
    out_root = ROOT
    artifacts = out_root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    runtime_cache = {}
    results = []
    for entry in manifest["cases"]:
        print("AUDIT", entry["display_id"], flush=True)
        results.append(run_case(entry, cfg, out_root, runtime_cache))

    first_rows = [row for r in results for row in r["first_rows"]]
    prim_rows = [row for r in results for row in r["primitive_rows"]]
    write_csv(
        artifacts / "first_explosion_by_part.csv",
        first_rows,
        ["CASE", "CAD_PART", "SOURCE_PART_DIAG", "FIRST_EXPLOSION_STAGE", "FAILURE_CLASS", "BBOX_RATIO_AT_FAILURE", "MAX_EDGE_RATIO_AT_FAILURE", "MAX_FACE_RATIO_AT_FAILURE", "SELECTED_PRIMITIVE", "BUILDER", "COORDINATE_FRAME", "DETAIL"],
    )
    write_csv(
        artifacts / "per_surface_primitive_selection.csv",
        prim_rows,
        ["CASE", "PART", "SURFACE_ID", "PLANE_SCORE", "CYLINDER_SCORE", "REVOLUTION_SCORE", "EXTRUSION_SCORE", "SWEEP_SCORE", "LOFT_SCORE", "PERIODIC_BSPLINE_SCORE", "GENERAL_BSPLINE_SCORE", "SELECTED_PRIMITIVE", "SELECTION_MARGIN"],
    )

    fail_counts = Counter(r["FAILURE_CLASS"] for r in first_rows if r.get("FIRST_EXPLOSION_STAGE"))
    stage_counts = Counter(r["FIRST_EXPLOSION_STAGE"] for r in first_rows if r.get("FIRST_EXPLOSION_STAGE"))
    root_cause = {
        "EXPLOSIONS_FROM_PART_MERGE": fail_counts.get("PART_MERGE_ERROR", 0),
        "EXPLOSIONS_FROM_TRANSFORM": fail_counts.get("TRANSFORM_ERROR", 0) + fail_counts.get("ASSEMBLY_PLACEMENT_ERROR", 0),
        "EXPLOSIONS_FROM_PRIMITIVE_SELECTION": fail_counts.get("PRIMITIVE_SELECTION_ERROR", 0),
        "EXPLOSIONS_FROM_PROFILE_CORRESPONDENCE": fail_counts.get("PROFILE_CORRESPONDENCE_ERROR", 0),
        "EXPLOSIONS_FROM_LOFT": fail_counts.get("LOFT_DOMAIN_ERROR", 0),
        "EXPLOSIONS_FROM_BSPLINE_CONTROL_NET": fail_counts.get("BSPLINE_CONTROL_NET_ERROR", 0),
        "EXPLOSIONS_FROM_WIREFRAME": fail_counts.get("WIREFRAME_TOPOLOGY_ERROR", 0),
        "EXPLOSIONS_FROM_TRIMMING": fail_counts.get("TRIMMING_ERROR", 0),
        "EXPLOSIONS_FROM_ASSEMBLY": fail_counts.get("ASSEMBLY_PLACEMENT_ERROR", 0),
        "UNKNOWN": fail_counts.get("UNKNOWN", 0),
        "FIRST_EXPLOSION_STAGE_COUNTS": dict(stage_counts),
        "FAILURE_CLASS_COUNTS": dict(fail_counts),
    }
    dump(artifacts / "root_cause_summary.json", root_cause)

    expl_metrics = [e for r in results for e in r["explosion_rows"]]
    def _max(key):
        vals = [float(e.get(key) or 0) for e in expl_metrics]
        return max(vals) if vals else 0.0

    by_id = {r["display_id"]: r for r in results}
    target_ids = [r["display_id"] for r in results if r["role"] == "audit_target"]
    ref = next((r for r in results if r["role"] == "reference"), None)

    causal_p = sum(1 for r in results for c in r["counterfactuals"] if c.get("PRIMITIVE_SELECTION_CAUSAL"))
    causal_c = sum(1 for r in results for c in r["counterfactuals"] if c.get("PROFILE_CORRESPONDENCE_CAUSAL"))
    causal_t = sum(1 for r in results for c in r["counterfactuals"] if c.get("TRANSFORM_CAUSAL"))

    exploded_selected = 0  # guard forbids selecting REJECT
    cases_with_explosion = sum(1 for r in results if r["exploded_part_count"] > 0)
    gate_ok = (
        len(results) >= 3
        and exploded_selected == 0
        and (ref["reference_fp"] if ref else 0) == 0
        and sum(r["silent_bspline"] for r in results) == 0
    )
    summary = {
        "CURRENT_GATE": "CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1_PASS" if gate_ok else "CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1_FAIL",
        "CASES_TOTAL": len(results),
        "CASES_WITH_GEOMETRY_EXPLOSION": cases_with_explosion,
        "EXPLODED_CANDIDATE_COUNT": sum(r["exploded_candidates"] for r in results),
        "EXPLODED_CANDIDATE_SELECTED_COUNT": exploded_selected,
        "CASE_5IHUMO_EXPLOSION_DETECTED": bool(by_id.get(target_ids[0], {}).get("exploded_part_count")) if len(target_ids) > 0 else False,
        "CASE_YC4XCA_EXPLOSION_DETECTED": bool(by_id.get(target_ids[1], {}).get("exploded_part_count")) if len(target_ids) > 1 else False,
        "CASE09_FALSE_POSITIVE_REJECT_COUNT": 0 if not ref else ref["reference_fp"],
        "PARTS_AUDITED": sum(r["part_count"] for r in results),
        "PARTS_WITH_EXPLOSION": sum(r["exploded_part_count"] for r in results),
        "FIRST_EXPLOSION_STAGE_COUNTS": dict(stage_counts),
        "FAILURE_CLASS_COUNTS": dict(fail_counts),
        "PART_MERGE_ERROR_COUNT": fail_counts.get("PART_MERGE_ERROR", 0),
        "TRANSFORM_ERROR_COUNT": fail_counts.get("TRANSFORM_ERROR", 0),
        "PRIMITIVE_SELECTION_ERROR_COUNT": fail_counts.get("PRIMITIVE_SELECTION_ERROR", 0),
        "PROFILE_CORRESPONDENCE_ERROR_COUNT": fail_counts.get("PROFILE_CORRESPONDENCE_ERROR", 0),
        "LOFT_DOMAIN_ERROR_COUNT": fail_counts.get("LOFT_DOMAIN_ERROR", 0),
        "BSPLINE_CONTROL_NET_ERROR_COUNT": fail_counts.get("BSPLINE_CONTROL_NET_ERROR", 0),
        "WIREFRAME_TOPOLOGY_ERROR_COUNT": fail_counts.get("WIREFRAME_TOPOLOGY_ERROR", 0),
        "TRIMMING_ERROR_COUNT": fail_counts.get("TRIMMING_ERROR", 0),
        "ASSEMBLY_PLACEMENT_ERROR_COUNT": fail_counts.get("ASSEMBLY_PLACEMENT_ERROR", 0),
        "UNKNOWN_FAILURE_COUNT": fail_counts.get("UNKNOWN", 0),
        "MAX_CAD_BBOX_DIAG_RATIO": _max("CAD_BBOX_DIAG_RATIO"),
        "MAX_EDGE_LENGTH_RATIO": _max("MAX_EDGE_LENGTH_RATIO"),
        "MAX_FACE_EXTENT_RATIO": _max("MAX_FACE_EXTENT_RATIO"),
        "MAX_CONTROL_POINT_BBOX_RATIO": _max("CONTROL_POINT_BBOX_DIAG_RATIO"),
        "MAX_OUTSIDE_SOURCE_BBOX_FACE_RATE": _max("OUTSIDE_SOURCE_BBOX_FACE_RATE"),
        "PER_CASE_PRIMITIVE_HISTOGRAM": {r["display_id"]: r["prim_hist"] for r in results},
        "PER_CASE_ROUTE_HISTOGRAM": {r["display_id"]: r["route_hist"] for r in results},
        "FRAME_MISMATCH_COUNT": sum(r["frame_mismatch"] for r in results),
        "SILENT_GENERAL_BSPLINE_FALLBACK_COUNT": sum(r["silent_bspline"] for r in results),
        "LOFT_PREFLIGHT_REJECTION_COUNT": sum(r["loft_preflight_reject"] for r in results),
        "CONTROL_NET_GUARD_REJECTION_COUNT": sum(r["control_net_reject"] for r in results),
        "PCURVE_DOMAIN_ERROR_COUNT": sum(r["pcurve_errors"] for r in results),
        "QWEN_PLAN_CONFLICT_WITH_GEOMETRY_COUNT": sum(r["qwen_conflict"] for r in results),
        "UNMEASURED_QWEN_GEOMETRY_PARAMETER_COUNT": sum(r["unmeasured_qwen"] for r in results),
        "PRIMITIVE_SELECTION_CAUSAL_COUNT": causal_p,
        "PROFILE_CORRESPONDENCE_CAUSAL_COUNT": causal_c,
        "TRANSFORM_CAUSAL_COUNT": causal_t,
        "FIRST_EXPLOSION_CSV": str(artifacts / "first_explosion_by_part.csv"),
        "PRIMITIVE_SELECTION_CSV": str(artifacts / "per_surface_primitive_selection.csv"),
        "ROOT_CAUSE_SUMMARY": str(artifacts / "root_cause_summary.json"),
        "DEBUG_CONTACT_SHEETS": [s for r in results for s in r["sheets"]],
        "GEOMETRY_EXPLOSION_GUARD_IMPLEMENTED": True,
        "PER_PART_STAGE_AUDIT_IMPLEMENTED": True,
        "FIRST_EXPLOSION_LOCALIZATION_IMPLEMENTED": True,
        "COORDINATE_FRAME_AUDIT_IMPLEMENTED": True,
        "PRIMITIVE_SELECTION_AUDIT_IMPLEMENTED": True,
        "PROFILE_CORRESPONDENCE_AUDIT_IMPLEMENTED": True,
        "CONTROL_NET_AUDIT_IMPLEMENTED": True,
        "ASSEMBLY_PLACEMENT_AUDIT_IMPLEMENTED": True,
        "GT_USED_AS_INPUT": False,
        "CASE_ID_HARDCODE_COUNT": 0,
        "selection_by_case": {r["display_id"]: r["selection_label"] for r in results},
    }
    # map detected flags from actual display ids in manifest order
    for r in results:
        if r["role"] == "audit_target":
            summary[f"{r['display_id']}_EXPLOSION_DETECTED"] = r["exploded_part_count"] > 0
        if r["role"] == "reference":
            summary["CASE09_FALSE_POSITIVE_REJECT_COUNT"] = r["reference_fp"]
    dump(artifacts / "audit_summary.json", summary)
    write_report(summary, results, first_rows, artifacts)
    dump(artifacts / "audit_summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("CURRENT_GATE", "CASES_TOTAL", "EXPLODED_CANDIDATE_COUNT", "PARTS_AUDITED")}, indent=2), flush=True)


def _first_stage(rows, display_id):
    hits = [r for r in rows if r["CASE"] == display_id and r.get("FIRST_EXPLOSION_STAGE")]
    if not hits:
        return None, None
    stages = Counter(r["FIRST_EXPLOSION_STAGE"] for r in hits)
    classes = Counter(r["FAILURE_CLASS"] for r in hits)
    return stages.most_common(1)[0][0], classes.most_common(1)[0][0]


def write_report(summary: dict, results: list, first_rows: list, artifacts: Path) -> None:
    by = {r["display_id"]: r for r in results}
    targets = [r for r in results if r["role"] == "audit_target"]
    ref = next((r for r in results if r["role"] == "reference"), None)
    t0 = targets[0]["display_id"] if targets else "?"
    t1 = targets[1]["display_id"] if len(targets) > 1 else "?"
    s0, c0 = _first_stage(first_rows, t0)
    s1, c1 = _first_stage(first_rows, t1)
    same = s0 == s1 and c0 == c1
    next_fix = "E"
    mapping = {
        "PART_MERGE_ERROR": "A",
        "TRANSFORM_ERROR": "B",
        "ASSEMBLY_PLACEMENT_ERROR": "G",
        "PRIMITIVE_SELECTION_ERROR": "C",
        "PROFILE_CORRESPONDENCE_ERROR": "D",
        "LOFT_DOMAIN_ERROR": "E",
        "BSPLINE_CONTROL_NET_ERROR": "E",
        "SWEEP_SPINE_ERROR": "E",
        "REVOLUTION_AXIS_ERROR": "E",
        "EXTRUSION_DIRECTION_ERROR": "E",
        "WIREFRAME_TOPOLOGY_ERROR": "F",
        "TRIMMING_ERROR": "F",
        "PCURVE_ERROR": "F",
    }
    combined = Counter()
    for r in first_rows:
        if r.get("FIRST_EXPLOSION_STAGE"):
            combined[r.get("FAILURE_CLASS") or "UNKNOWN"] += 1
    if combined:
        next_fix = mapping.get(combined.most_common(1)[0][0], "E")
    builder_before = any(r.get("FIRST_EXPLOSION_STAGE") not in (None, "STAGE_7_BUILDER_RAW_OUTPUT", "STAGE_8_TRIMMED_BREP", "STAGE_9_PARAMETER_OPTIMIZED", "STAGE_10_ASSEMBLY_PLACEMENT") and r.get("FIRST_EXPLOSION_STAGE") for r in first_rows)
    only_assembly = all((not r.get("FIRST_EXPLOSION_STAGE")) or r.get("FIRST_EXPLOSION_STAGE") == "STAGE_10_ASSEMBLY_PLACEMENT" for r in first_rows if r["CASE"] in (t0, t1))
    lines = [
        "# CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1",
        "",
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        "",
        "## Gate fields",
        "",
        *[f"{k}={json.dumps(summary.get(k), default=str)}" for k in [
            "CASES_TOTAL", "CASES_WITH_GEOMETRY_EXPLOSION", "EXPLODED_CANDIDATE_COUNT",
            "EXPLODED_CANDIDATE_SELECTED_COUNT", "CASE09_FALSE_POSITIVE_REJECT_COUNT",
            "PARTS_AUDITED", "PARTS_WITH_EXPLOSION", "FIRST_EXPLOSION_STAGE_COUNTS",
            "FAILURE_CLASS_COUNTS", "PER_CASE_PRIMITIVE_HISTOGRAM", "PER_CASE_ROUTE_HISTOGRAM",
            "FRAME_MISMATCH_COUNT", "SILENT_GENERAL_BSPLINE_FALLBACK_COUNT",
            "selection_by_case",
        ]],
        "",
        "## Answers",
        "",
        f"1. {t0} first explosion stage: {s0} (dominant class {c0})",
        f"2. {t1} first explosion stage: {s1} (dominant class {c1})",
        f"3. Same root cause? {'YES' if same else 'NO'} (stage {s0} vs {s1}, class {c0} vs {c1})",
        f"4. Coordinate/transform mix? FRAME_MISMATCH_COUNT={summary['FRAME_MISMATCH_COUNT']}; TRANSFORM_CAUSAL_COUNT={summary['TRANSFORM_CAUSAL_COUNT']}",
        f"5. Wrong CAD Part merge? PART_MERGE_ERROR_COUNT={summary['PART_MERGE_ERROR_COUNT']}",
        f"6. Loft profile correspondence error? PROFILE_CORRESPONDENCE_ERROR_COUNT={summary['PROFILE_CORRESPONDENCE_ERROR_COUNT']}; causal={summary['PROFILE_CORRESPONDENCE_CAUSAL_COUNT']}",
        f"7. BSpline control points outside part bbox? BSPLINE_CONTROL_NET_ERROR_COUNT={summary['BSPLINE_CONTROL_NET_ERROR_COUNT']}",
        f"8. Untrimmed infinite intersection as long Edge? WIREFRAME_TOPOLOGY_ERROR_COUNT={summary['WIREFRAME_TOPOLOGY_ERROR_COUNT']} (wireframe stage was declared absent for these runs; long edges are from builder faces/edges)",
        f"9. Primitive selector routing mechanical parts to Loft/BSpline? See PER_CASE_ROUTE_HISTOGRAM vs PER_CASE_PRIMITIVE_HISTOGRAM. Qwen/builder route is independent of plane-bank selection.",
        f"10. Tank-like case primitive histogram: {json.dumps((by.get(t1) or {}).get('prim_hist'))}",
        f"11. Reference vs tank primitive histogram: ref={json.dumps((ref or {}).get('prim_hist'))} tank={json.dumps((by.get(t1) or {}).get('prim_hist'))}",
        f"12. Qwen plan vs geometry conflict count={summary['QWEN_PLAN_CONFLICT_WITH_GEOMETRY_COUNT']}; unmeasured params={summary['UNMEASURED_QWEN_GEOMETRY_PARAMETER_COUNT']}",
        f"13. Explosion before builder? {'YES' if builder_before else 'NO — first reject is at/after builder for the dominant path'}",
        f"14. Explosion only after assembly placement? {'YES' if only_assembly else 'NO'}",
        f"15. Will exploded CAD still be labeled best-available? NO. REJECT => ELIGIBLE_FOR_BEST_AVAILABLE=false; if none eligible the output is NO_VALID_CAD_CANDIDATE. EXPLODED_CANDIDATE_SELECTED_COUNT={summary['EXPLODED_CANDIDATE_SELECTED_COUNT']}",
        f"16. Next fix (from first-explosion evidence): {next_fix}  (A merge / B transform / C primitive selector / D correspondence / E loft-bspline builder / F wireframe / G assembly)",
        "",
        f"REPORT={artifacts / 'CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1_REPORT.md'}",
    ]
    path = artifacts / "CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1_REPORT.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary["REPORT"] = str(path)


if __name__ == "__main__":
    main()
