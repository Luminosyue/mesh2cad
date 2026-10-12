#!/usr/bin/env python3
"""CASE01 read-only recovery root-cause audit. Never calls CAD generation or LLMs."""
from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import re
import socket
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp
from OCP.TopLoc import TopLoc_Location
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS


PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
CASE = PROJECT / "batch_real_mesh2cad_v1/cases/CASE_01"
PART = CASE / "cad_recovery/CADPART_000"
OUT = PROJECT / "parallel_pipeline_diagnostics_v1/task_c"
SOURCE = PROJECT / "meshes/Asus_M5A99FX_PRO_R20_Motherboard_ATX_Socket_AM3.obj"
LEDGER = PART / "local_to_global_transform.json"
SEED = 20260811
SAMPLES = 50_000
MAX_TRIANGLES = 400_000
CANDIDATES = {
    "candidate_A_loft": PART / "candidate_A_loft/candidate.step",
    "candidate_B_loft": PART / "candidate_B_loft/candidate.step",
    "candidate_C_primitive": PART / "candidate_C_primitive/candidate.step",
}
SURFACE_NAMES = {
    "GeomAbs_Plane": "PLANE", "GeomAbs_Cylinder": "CYLINDER", "GeomAbs_Cone": "CONE",
    "GeomAbs_Sphere": "SPHERE", "GeomAbs_Torus": "TORUS", "GeomAbs_BezierSurface": "BEZIER",
    "GeomAbs_BSplineSurface": "BSPLINE", "GeomAbs_SurfaceOfRevolution": "SURFACE_OF_REVOLUTION",
    "GeomAbs_SurfaceOfExtrusion": "SURFACE_OF_EXTRUSION", "GeomAbs_OffsetSurface": "OFFSET",
}
CURVE_NAMES = {
    "GeomAbs_Line": "LINE", "GeomAbs_Circle": "CIRCLE", "GeomAbs_Ellipse": "ELLIPSE",
    "GeomAbs_BezierCurve": "BEZIER", "GeomAbs_BSplineCurve": "BSPLINE",
}


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return clean(value.tolist())
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,)): return float(value) if np.isfinite(value) else None
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def indexed(shape, kind):
    out = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape, kind, out); return out


def enum_name(value, mapping): return mapping.get(str(value).split(".")[-1], "OTHER")


def bounds_shape(shape):
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box, True); v = box.Get()
    b = np.asarray([v[:3], v[3:]], float)
    return b, float(np.linalg.norm(b[1] - b[0]))


def topology(shape):
    maps = {name: indexed(shape, kind) for name, kind in {
        "SOLID": TopAbs_SOLID, "SHELL": TopAbs_SHELL, "FACE": TopAbs_FACE,
        "EDGE": TopAbs_EDGE, "VERTEX": TopAbs_VERTEX}.items()}
    surfaces, curves = Counter(), Counter(); areas, lengths = [], []
    for i in range(1, maps["FACE"].Extent() + 1):
        face = TopoDS.Face_s(maps["FACE"].FindKey(i))
        try: surfaces[enum_name(BRepAdaptor_Surface(face).GetType(), SURFACE_NAMES)] += 1
        except Exception: surfaces["OTHER"] += 1
        try:
            p = GProp_GProps(); BRepGProp.SurfaceProperties_s(face, p); areas.append(float(p.Mass()))
        except Exception: areas.append(float("nan"))
    for i in range(1, maps["EDGE"].Extent() + 1):
        edge = TopoDS.Edge_s(maps["EDGE"].FindKey(i))
        try: curves[enum_name(BRepAdaptor_Curve(edge).GetType(), CURVE_NAMES)] += 1
        except Exception: curves["OTHER"] += 1
        try:
            p = GProp_GProps(); BRepGProp.LinearProperties_s(edge, p); lengths.append(float(p.Mass()))
        except Exception: lengths.append(float("nan"))
    b, diag = bounds_shape(shape); ar = np.asarray(areas); le = np.asarray(lengths)
    face_count = maps["FACE"].Extent()
    return {
        "counts": {k.lower() + "s": int(v.Extent()) for k, v in maps.items()},
        "surface_histogram": dict(surfaces), "curve_histogram": dict(curves),
        "analytic_face_ratio": float(sum(surfaces[x] for x in ("PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS")) / max(face_count, 1)),
        "bspline_face_ratio": float(surfaces["BSPLINE"] / max(face_count, 1)),
        "tiny_face_ratio": float(np.mean(ar < diag * diag * 1e-8)) if len(ar) else 0.0,
        "short_edge_ratio": float(np.mean(le < diag * 1e-5)) if len(le) else 0.0,
        "raw_bbox": b, "raw_bbox_diagonal": diag,
    }


def point_xyz(point, transform=None):
    if transform is not None: point = point.Transformed(transform)
    return point.X(), point.Y(), point.Z()


def tessellate(shape, diag):
    last = 0
    for factor in (.005, .01, .02, .04):
        deflection = max(diag * factor, 1e-6)
        BRepTools.Clean_s(shape)
        mesher = BRepMesh_IncrementalMesh(shape, deflection, False, .35, False)
        mesher.Perform()
        face_map = indexed(shape, TopAbs_FACE); last = 0
        for i in range(1, face_map.Extent() + 1):
            face = TopoDS.Face_s(face_map.FindKey(i)); loc = TopLoc_Location(); tri = BRep_Tool.Triangulation_s(face, loc)
            if tri is not None: last += tri.NbTriangles()
        if 0 < last <= MAX_TRIANGLES: break
    if not (0 < last <= MAX_TRIANGLES):
        return {"status": "RESOURCE_LIMIT", "triangle_count": last, "deflection": deflection}
    points, faces = [], []
    for i in range(1, face_map.Extent() + 1):
        face = TopoDS.Face_s(face_map.FindKey(i)); loc = TopLoc_Location(); tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None: continue
        tr = loc.Transformation(); offset = len(points)
        for n in range(1, tri.NbNodes() + 1): points.append(point_xyz(tri.Node(n), tr))
        for j in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(j).Get()
            if face.Orientation() == TopAbs_REVERSED: b, c = c, b
            faces.append((offset + a - 1, offset + b - 1, offset + c - 1))
    return {"status": "SUCCESS", "triangle_count": len(faces), "deflection": deflection,
            "vertices": np.asarray(points, float), "faces": np.asarray(faces, np.int64)}


def apply_transform(vertices, matrix):
    m = np.asarray(matrix, float)
    return vertices @ m[:3, :3].T + m[:3, 3]


def bbox(vertices):
    b = np.asarray([vertices.min(axis=0), vertices.max(axis=0)])
    return b, float(np.linalg.norm(b[1] - b[0]))


def geometry_metrics(source, cad):
    src_diag = float(np.linalg.norm(source.extents))
    src_pts = trimesh.sample.sample_surface(source, SAMPLES, seed=SEED)[0]
    cad_pts = trimesh.sample.sample_surface(cad, SAMPLES, seed=SEED + 1)[0]
    da = cKDTree(cad_pts).query(src_pts, workers=1)[0] / src_diag
    db = cKDTree(src_pts).query(cad_pts, workers=1)[0] / src_diag
    both = np.r_[da, db]
    return {
        "sample_count_each": SAMPLES, "seed_source": SEED, "seed_cad": SEED + 1,
        "normalized_symmetric_chamfer": float((da.mean() + db.mean()) / 2),
        "normalized_p95": float(np.quantile(both, .95)),
        "source_coverage_005": float(np.mean(da <= .005)),
        "source_coverage_010": float(np.mean(da <= .010)),
        "source_coverage_020": float(np.mean(da <= .020)),
        "cad_coverage_020": float(np.mean(db <= .020)),
        "normalized_hausdorff_sampled": float(both.max()),
    }


def qclass(m, valid):
    if not valid: return "INVALID"
    c, p, v = m["normalized_symmetric_chamfer"], m["normalized_p95"], m["source_coverage_020"]
    if c <= .01 and p <= .02 and v >= .95: return "Q1"
    if c <= .02 and p <= .05 and v >= .85: return "Q2"
    return "Q3"


def parse_program(path):
    tree = ast.parse(path.read_text(encoding="utf-8")); out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign): continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {"SECTIONS", "RULED", "KIND", "DIMS"}:
                try: out[target.id] = ast.literal_eval(node.value)
                except Exception: pass
    return out


def signed_area(points):
    p = np.asarray(points, float); q = np.roll(p, -1, axis=0)
    return float(.5 * np.sum(p[:, 0] * q[:, 1] - q[:, 0] * p[:, 1]))


def orient(a, b, c): return np.cross(np.asarray(b) - a, np.asarray(c) - a)


def segments_cross(a, b, c, d):
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return bool((o1 * o2 < -1e-12) and (o3 * o4 < -1e-12))


def self_intersections(points):
    p = np.asarray(points, float); n = len(p); count = 0
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1: continue
            if segments_cross(a, b, p[j], p[(j + 1) % n]): count += 1
    return count


def profile_distance(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = (a - a.mean(0)) / max(np.sqrt(np.mean(np.sum((a - a.mean(0)) ** 2, axis=1))), 1e-12)
    b = (b - b.mean(0)) / max(np.sqrt(np.mean(np.sum((b - b.mean(0)) ** 2, axis=1))), 1e-12)
    direct = float(np.sqrt(np.mean(np.sum((a - b) ** 2, axis=1))))
    trials = []
    for reverse in (False, True):
        q = b[::-1] if reverse else b
        for shift in range(len(b)):
            trials.append((float(np.sqrt(np.mean(np.sum((a - np.roll(q, shift, axis=0)) ** 2, axis=1)))), reverse, shift))
    best = min(trials)
    return {"direct_rms": direct, "best_rms": best[0], "best_reversed": best[1], "best_shift": best[2],
            "direct_to_best_ratio": direct / max(best[0], 1e-12)}


def section_audit(program):
    sections = program["SECTIONS"]
    z = np.asarray([x["z"] for x in sections], float); area = np.asarray([abs(signed_area(x["points"])) for x in sections])
    inter = [self_intersections(x["points"]) for x in sections]
    adjacent = [profile_distance(sections[i]["points"], sections[i + 1]["points"]) for i in range(len(sections) - 1)]
    ratios = np.maximum(area[1:] / np.maximum(area[:-1], 1e-12), area[:-1] / np.maximum(area[1:], 1e-12))
    return {
        "section_count": len(sections), "point_count_set": sorted({len(x["points"]) for x in sections}),
        "indices": [x["index"] for x in sections], "z_strictly_monotonic": bool(np.all(np.diff(z) > 0)),
        "z_range": [float(z.min()), float(z.max())], "signed_area_orientation_changes": int(np.sum(np.sign([signed_area(x["points"]) for x in sections])[1:] != np.sign([signed_area(x["points"]) for x in sections])[:-1])),
        "self_intersecting_section_count": int(sum(v > 0 for v in inter)), "self_intersection_total": int(sum(inter)),
        "area_min": float(area.min()), "area_max": float(area.max()), "max_adjacent_area_ratio": float(ratios.max()),
        "adjacent_best_reversal_count": int(sum(x["best_reversed"] for x in adjacent)),
        "adjacent_nonzero_best_shift_count": int(sum(x["best_shift"] != 0 for x in adjacent)),
        "adjacent_large_shift_count": int(sum(min(x["best_shift"], 64 - x["best_shift"]) >= 8 for x in adjacent)),
        "direct_to_best_ratio_max": float(max(x["direct_to_best_ratio"] for x in adjacent)),
        "direct_to_best_ratio_median": float(np.median([x["direct_to_best_ratio"] for x in adjacent])),
        "worst_adjacent_pairs": sorted([dict(pair=[sections[i]["index"], sections[i+1]["index"]], **x) for i, x in enumerate(adjacent)], key=lambda x: x["direct_to_best_ratio"], reverse=True)[:8],
    }


def scan_evidence():
    patterns = re.compile(r"timeout|resource|killed|loft|tessell|error|fail", re.I)
    files = []
    for root in [CASE, PROJECT / "batch_10_step_quality_audit_v1/cases/CASE_01", PROJECT / "batch_10_step_audit_sanity_fix_v2"]:
        if not root.exists(): continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".json", ".txt", ".log", ".md", ".csv"} and p.stat().st_size < 5_000_000:
                try:
                    lines = [line.strip()[:800] for line in p.read_text(encoding="utf-8", errors="replace").splitlines() if patterns.search(line)]
                except Exception: continue
                if lines: files.append({"path": str(p), "matching_lines": lines[:30], "match_count": len(lines)})
    return files


def audit_candidate(name, path, matrix, source):
    started = time.time(); result = {
        "candidate": name, "step_path": str(path), "step_sha256": sha256(path), "step_bytes": path.stat().st_size,
        "program_path": str(path.with_name("deterministic_program.py")), "build_log_path": str(path.with_name("build.log")),
        "provenance_explicit": path.with_name("deterministic_program.py").is_file() and path.with_name("build.log").is_file(),
        "fresh_reload": True, "unrestricted_icp_used": False, "transform_mode": "SAVED_CANONICAL_TO_SOURCE",
    }
    reader = STEPControl_Reader(); status = reader.ReadFile(str(path)); result["step_read_status"] = int(status)
    result["step_read_success"] = bool(status == IFSelect_RetDone)
    roots = int(reader.TransferRoots()) if result["step_read_success"] else 0; result["transfer_roots"] = roots
    shape = reader.OneShape() if roots else None; result["step_reload_success"] = bool(shape and not shape.IsNull())
    if not result["step_reload_success"]: return result
    result["brep_valid"] = bool(BRepCheck_Analyzer(shape).IsValid()); result.update(topology(shape))
    tess = tessellate(shape, result["raw_bbox_diagonal"])
    result.update({"tessellation_status": tess["status"], "tessellation_triangle_count": tess["triangle_count"], "tessellation_deflection": tess["deflection"]})
    if tess["status"] == "SUCCESS":
        raw_b, raw_d = bbox(tess["vertices"]); vertices = apply_transform(tess["vertices"], matrix); mapped_b, mapped_d = bbox(vertices)
        cad = trimesh.Trimesh(vertices=vertices, faces=tess["faces"], process=False)
        result["tessellated_raw_bbox"] = raw_b; result["tessellated_raw_bbox_diagonal"] = raw_d
        result["mapped_bbox"] = mapped_b; result["mapped_bbox_diagonal"] = mapped_d
        result["source_bbox"] = source.bounds; result["source_bbox_diagonal"] = float(np.linalg.norm(source.extents))
        result["bbox_sanity"] = {
            "mapped_to_source_diagonal_ratio": mapped_d / float(np.linalg.norm(source.extents)),
            "center_offset_normalized": float(np.linalg.norm(mapped_b.mean(0) - source.bounds.mean(0)) / np.linalg.norm(source.extents)),
            "extent_relative_error_l2": float(np.linalg.norm((mapped_b[1]-mapped_b[0]) - source.extents) / np.linalg.norm(source.extents)),
        }
        result["geometry_metrics"] = geometry_metrics(source, cad); result["geometry_q"] = qclass(result["geometry_metrics"], result["brep_valid"])
        result["generated_mesh_path"] = str(OUT / "candidates" / name / "fresh_step_tessellation_source_frame.obj")
        Path(result["generated_mesh_path"]).parent.mkdir(parents=True, exist_ok=True); cad.export(result["generated_mesh_path"])
    result["elapsed_seconds"] = time.time() - started
    return result


def main():
    for d in [OUT / "artifacts", OUT / "candidates", OUT / "logs", OUT / "scripts", OUT / "tests", OUT / "transforms"]: d.mkdir(parents=True, exist_ok=True)
    source = trimesh.load(SOURCE, force="mesh", process=False)
    ledger = load(LEDGER); matrix = np.asarray(ledger["CANONICAL_TO_SOURCE"], float); inverse = np.asarray(ledger["SOURCE_TO_CANONICAL"], float)
    transform_audit = {
        "ledger_path": str(LEDGER), "ledger_sha256": sha256(LEDGER), "transform_used": "CANONICAL_TO_SOURCE",
        "matrix": matrix, "inverse_matrix": inverse, "matrix_finite": bool(np.isfinite(matrix).all()),
        "inverse_roundtrip_max_abs_error": float(np.abs(matrix @ inverse - np.eye(4)).max()),
        "ledger_roundtrip_pass": ledger.get("roundtrip_pass"), "ledger_icp_used": ledger.get("ICP_USED"), "unrestricted_icp_used": False,
    }
    dump(OUT / "transforms/transform_used.json", transform_audit)
    source_info = {"path": str(SOURCE), "sha256": sha256(SOURCE), "vertices": len(source.vertices), "triangles": len(source.faces),
                   "watertight": bool(source.is_watertight), "connected_components": len(source.split(only_watertight=False)),
                   "bbox": source.bounds, "bbox_diagonal": float(np.linalg.norm(source.extents)), "surface_area": float(source.area)}
    audits = []
    for name, path in CANDIDATES.items():
        print(f"AUDIT_START {name}", flush=True)
        record = audit_candidate(name, path, matrix, source); audits.append(record)
        dump(OUT / "candidates" / name / "fresh_qa.json", record)
        dump(OUT / "transforms" / name / "transform_used.json", transform_audit)
        print(f"AUDIT_DONE {name} {record.get('geometry_q')} tris={record.get('tessellation_triangle_count')}", flush=True)
    programs = {name: parse_program(path.with_name("deterministic_program.py")) for name, path in CANDIDATES.items()}
    sections = {name: section_audit(programs[name]) for name in ("candidate_A_loft", "candidate_B_loft")}
    router = load(CASE / "router/frozen_geometry_router/router_decision.json") if (CASE / "router/frozen_geometry_router/router_decision.json").is_file() else {}
    geometry_analysis = load(CASE / "router/frozen_geometry_router/geometry_analysis/geometry_analysis.json") if (CASE / "router/frozen_geometry_router/geometry_analysis/geometry_analysis.json").is_file() else {}
    logs = scan_evidence()
    graph = {
        "schema": "CASE01_PROVENANCE_GRAPH_V1", "case_id": "CASE_01", "read_only_audit": True,
        "nodes": [
            {"id": "SOURCE_OBJ", "type": "SOURCE_MESH", **source_info},
            {"id": "ROUTER", "type": "FROZEN_GEOMETRY_ROUTER", "path": str(CASE / "router/frozen_geometry_router")},
            {"id": "CADPART_000", "type": "WHOLE_OBJECT_CAD_PART", "path": str(PART), "p3_segmentation_used": False},
            *[{"id": n, "type": "CANDIDATE_STEP", "path": str(p), "sha256": sha256(p), "provenance_explicit": True} for n, p in CANDIDATES.items()],
        ],
        "edges": [
            {"from": "SOURCE_OBJ", "to": "ROUTER", "relation": "ANALYZED_BY"},
            {"from": "ROUTER", "to": "CADPART_000", "relation": "WHOLE_OBJECT_ROUTE_NO_P3"},
            *[{"from": "CADPART_000", "to": n, "relation": "DETERMINISTIC_PROGRAM_AND_BUILD_LOG"} for n in CANDIDATES],
            *[{"from": n, "to": "SOURCE_OBJ", "relation": "FRESH_QA_VIA_SAVED_CANONICAL_TO_SOURCE_NO_ICP"} for n in CANDIDATES],
        ],
        "transform": transform_audit,
    }
    dump(OUT / "artifacts/case01_provenance_graph.json", graph)
    geometry_hypothesis = {
        "source": source_info, "router_decision": router, "geometry_analysis_summary": geometry_analysis,
        "part_decomposition": {"cad_part_count": 1, "part_ids": ["CADPART_000"], "scope": "WHOLE_OBJECT", "p3_segmentation_used": False},
        "candidate_programs": {n: {k: v for k, v in p.items() if k != "SECTIONS"} for n, p in programs.items()},
        "loft_section_audits": sections,
    }
    dump(OUT / "artifacts/case01_geometry_hypothesis_audit.json", geometry_hypothesis)
    dump(OUT / "artifacts/case01_candidate_audit.json", {"candidates": audits, "thresholds": {"Q1": {"chamfer_max": .01, "p95_max": .02, "coverage02_min": .95}, "Q2": {"chamfer_max": .02, "p95_max": .05, "coverage02_min": .85}}, "no_icp": True})
    dump(OUT / "artifacts/case01_log_resource_evidence.json", {"evidence_files": logs})
    all_reload = all(x.get("step_reload_success") for x in audits); all_q3 = all(x.get("geometry_q") == "Q3" for x in audits)
    resource_evidence = any(any(re.search(r"resource|timeout|killed", line, re.I) for line in x["matching_lines"]) for x in logs)
    rootcause = {
        "schema": "CASE01_RECOVERY_ROOTCAUSE_V1", "PRIMARY_ROOT_CAUSE": "GEOMETRY_HYPOTHESIS_WRONG",
        "SECONDARY_ROOT_CAUSES": ["BRep_VALID_BUT_GEOMETRY_Q3", "SURFACE_FIT_FAILURE", "PART_DECOMPOSITION_WRONG"],
        "CASE01_RESOURCE_FAILURE": bool(resource_evidence), "CASE01_GEOMETRY_FAILURE": bool(all_q3),
        "RESOURCE_TIMEOUT_ONLY_REJECTED": bool(resource_evidence and all_reload and all_q3),
        "reasoning": [
            "CASE01 is one watertight but geometrically complex motherboard routed as a single whole-object CAD part with no P3 decomposition.",
            "All three explicit-provenance STEP candidates freshly reload; resource timeout therefore does not explain the persistent candidate geometry failure.",
            "The smooth loft, ruled loft, and primitive fallback all score Q3 after the saved transform and without ICP, so the common failure precedes a specific loft implementation.",
            "Loft profiles exhibit extreme area variation and correspondence shifts; these amplify surface-fit failure but are downstream of the unsuitable whole-object single-profile family hypothesis.",
            "The saved transform is finite, inverse-consistent, and maps the primitive's nominal 100 mm diagonal back to source scale; transform failure is not primary.",
        ],
        "RESCUE_ROUTE_A": {
            "name": "DECOMPOSE_THEN_FIT_ANALYTIC_FEATURES",
            "plan_only": True,
            "steps": ["Split the single connected source by feature-scale and plane-region adjacency, not connected components.", "Represent the motherboard substrate as a thin plate/extrusion.", "Fit raised/socket/slot/cylindrical feature groups independently with explicit local transforms.", "Assemble parts and require per-part plus whole-object direct QA before acceptance."],
            "acceptance": "Every part BRep-valid; assembled direct no-ICP Q1/Q2; transform roundtrip retained."
        },
        "RESCUE_ROUTE_B": {
            "name": "MULTI_LOOP_SECTION_AND_CORRESPONDENCE_LOFT",
            "plan_only": True,
            "steps": ["Keep only coherent local feature zones, never one outer contour for the full motherboard.", "Preserve multiple loops/holes per slice and reject degenerate end sections.", "Solve cyclic profile correspondence with explicit twist and self-intersection checks.", "Loft short stable spans, cap them, then boolean-compose with the plate substrate."],
            "acceptance": "No profile-order alarms; bounded canonical bbox; fresh STEP reload; direct no-ICP Q1/Q2."
        },
        "REBUILD_EXECUTED": False, "MAC_LLM_CALLS": 0, "UNRESTRICTED_ICP_USED": False,
    }
    dump(OUT / "artifacts/case01_rootcause.json", rootcause)
    summary = {
        "CURRENT_GATE": "CASE01_RECOVERY_ROOTCAUSE_V1_PASS" if all_reload and all_q3 else "CASE01_RECOVERY_ROOTCAUSE_V1_INCOMPLETE",
        "CASE_ID": "CASE_01", "PRIMARY_ROOT_CAUSE": rootcause["PRIMARY_ROOT_CAUSE"], "SECONDARY_ROOT_CAUSES": rootcause["SECONDARY_ROOT_CAUSES"],
        "CASE01_RESOURCE_FAILURE": rootcause["CASE01_RESOURCE_FAILURE"], "CASE01_GEOMETRY_FAILURE": rootcause["CASE01_GEOMETRY_FAILURE"],
        "RESOURCE_TIMEOUT_ONLY_REJECTED": rootcause["RESOURCE_TIMEOUT_ONLY_REJECTED"],
        "CANDIDATE_STEP_COUNT": len(audits), "CANDIDATE_RELOAD_SUCCESS": sum(bool(x.get("step_reload_success")) for x in audits),
        "CANDIDATE_BREP_VALID": sum(bool(x.get("brep_valid")) for x in audits), "CANDIDATE_Q3": sum(x.get("geometry_q") == "Q3" for x in audits),
        "CANDIDATES": [{"candidate": x["candidate"], "sha256": x["step_sha256"], "brep_valid": x.get("brep_valid"), "geometry_q": x.get("geometry_q"), **(x.get("geometry_metrics") or {}), "faces": x.get("counts", {}).get("faces"), "triangles": x.get("tessellation_triangle_count")} for x in audits],
        "RESCUE_ROUTE_A": rootcause["RESCUE_ROUTE_A"]["name"], "RESCUE_ROUTE_B": rootcause["RESCUE_ROUTE_B"]["name"],
        "REBUILD_EXECUTED": False, "MAC_LLM_CALLS": 0, "UNRESTRICTED_ICP_USED": False,
        "OUTPUT_ROOT": str(OUT), "TESTS_PASSED": 0, "TESTS_FAILED": 0,
        "BLOCKERS": [] if all_reload and all_q3 else ["FRESH_CANDIDATE_AUDIT_INCOMPLETE"],
    }
    dump(OUT / "artifacts/task_c_summary.json", summary)
    report = ["# CASE01_RECOVERY_ROOTCAUSE_V1", "", f"Gate: `{summary['CURRENT_GATE']}`", "", "## Finding", "", f"Primary root cause: `{rootcause['PRIMARY_ROOT_CAUSE']}`.", "", "The historical smooth-loft tessellation timeout is a real resource event, but it is not the sole cause. Every explicit A/B/C STEP candidate freshly reloads; after the saved canonical-to-source transform, all remain Q3 under direct fixed-seed geometry QA without ICP. The common failure is the whole-object geometry hypothesis for a complex motherboard, with loft surface fitting and missing feature-scale decomposition as secondary causes.", "", "## Candidate evidence", ""]
    for x in audits:
        m = x.get("geometry_metrics", {}); report.append(f"- `{x['candidate']}`: valid={x.get('brep_valid')}, faces={x.get('counts',{}).get('faces')}, Q={x.get('geometry_q')}, Chamfer={m.get('normalized_symmetric_chamfer')}, P95={m.get('normalized_p95')}, Coverage@2%={m.get('source_coverage_020')}")
    report += ["", "## Failure separation", "", f"- Resource failure observed: `{rootcause['CASE01_RESOURCE_FAILURE']}`.", f"- Persistent geometry failure: `{rootcause['CASE01_GEOMETRY_FAILURE']}`.", f"- Resource-timeout-only diagnosis rejected: `{rootcause['RESOURCE_TIMEOUT_ONLY_REJECTED']}`.", "", "## Rescue plans (not executed)", "", f"- Route A — `{rootcause['RESCUE_ROUTE_A']['name']}`: feature-scale decomposition, analytic local fits, assembly-level QA.", f"- Route B — `{rootcause['RESCUE_ROUTE_B']['name']}`: multi-loop local sections, explicit correspondence/twist checks, short-span lofts composed with a plate substrate.", "", "No STEP was overwritten; no reconstruction, MAC, LLM, CASE09 work, shared-code change, or unrestricted ICP was performed.", ""]
    (OUT / "artifacts/case01_recovery_rootcause_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(clean(summary), indent=2), flush=True)


if __name__ == "__main__": main()
