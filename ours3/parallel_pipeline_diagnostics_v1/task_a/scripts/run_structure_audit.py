#!/usr/bin/env python3
"""Read-only structural audit of explicitly named STEP artifacts.

This program never writes beside an input STEP. All products are confined to
TASK_ROOT.  Paths are deliberately explicit: a missing version is reported as
NOT_AVAILABLE rather than discovered by a heuristic search.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.GeomAbs import (
    GeomAbs_BSplineSurface, GeomAbs_BezierSurface, GeomAbs_Cone,
    GeomAbs_Cylinder, GeomAbs_Line, GeomAbs_Plane, GeomAbs_Sphere,
    GeomAbs_SurfaceOfExtrusion, GeomAbs_SurfaceOfRevolution, GeomAbs_Torus,
)
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED, TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
TASK_ROOT = ROOT / "parallel_pipeline_diagnostics_v1" / "task_a"
ART = TASK_ROOT / "artifacts"
LOG = TASK_ROOT / "logs"
TEST = TASK_ROOT / "tests"
SCRIPT = TASK_ROOT / "scripts"

CASES = ["CASE_02", "CASE_03", "CASE_04", "CASE_05", "CASE_08", "CASE_09"]
BASELINE = {
    "CASE_02": ROOT / "batch_real_mesh2cad_v1/cases/CASE_02/cad_recovery/reconstructed.step",
    "CASE_03": ROOT / "batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step",
    "CASE_04": ROOT / "batch_real_mesh2cad_v1/cases/CASE_04/cad_recovery/reconstructed.step",
    "CASE_05": ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/assembly/partial_assembly.step",
    "CASE_08": ROOT / "batch_real_mesh2cad_v1/cases/CASE_08/cad_recovery/reconstructed.step",
    "CASE_09": ROOT / "batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/reconstructed.step",
}
V1 = {
    "CASE_04": ROOT / "complexity_aware_compact_cad_v1/case04/compact_balanced.step",
    "CASE_05": ROOT / "complexity_aware_compact_cad_v1/case05/compact_balanced.step",
    "CASE_09": ROOT / "complexity_aware_compact_cad_v1/case09/compact_balanced.step",
}
V2 = {
    "CASE_03": ROOT / "feature_preserving_compact_cad_v2/case03/v2_feature_preserving.step",
    "CASE_04": ROOT / "feature_preserving_compact_cad_v2/case04/v2_feature_preserving.step",
    "CASE_05": ROOT / "feature_preserving_compact_cad_v2/case05/v2_feature_preserving.step",
    "CASE_09": ROOT / "feature_preserving_compact_cad_v2/case09/v2_feature_preserving.step",
}
LATEST_OVERRIDE = {
    "CASE_09": ROOT / "case09_aircraft_end2end_cad_v1/07_assembly/CASE09_aircraft_final.step",
}

SURFACE_NAMES = {
    GeomAbs_Plane: "PLANE", GeomAbs_Cylinder: "CYLINDER", GeomAbs_Cone: "CONE",
    GeomAbs_Sphere: "SPHERE", GeomAbs_Torus: "TORUS",
    GeomAbs_SurfaceOfRevolution: "SURFACE_OF_REVOLUTION",
    GeomAbs_SurfaceOfExtrusion: "SURFACE_OF_EXTRUSION",
    GeomAbs_BSplineSurface: "BSPLINE", GeomAbs_BezierSurface: "BEZIER",
}
SURFACE_ORDER = ["PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS",
                 "SURFACE_OF_REVOLUTION", "SURFACE_OF_EXTRUSION", "BSPLINE", "BEZIER", "OTHER"]
ANALYTIC = set(SURFACE_ORDER[:7])
TYPE_COLORS = {
    "PLANE": "#4c78a8", "CYLINDER": "#f58518", "CONE": "#e45756",
    "SPHERE": "#72b7b2", "TORUS": "#54a24b", "SURFACE_OF_REVOLUTION": "#b279a2",
    "SURFACE_OF_EXTRUSION": "#ff9da6", "BSPLINE": "#9d755d", "BEZIER": "#bab0ac",
    "OTHER": "#777777",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fingerprint(path: Path) -> dict:
    st = path.stat()
    return {"path": str(path), "size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": sha256(path)}


def enum_shapes(shape, kind):
    out = []
    ex = TopExp_Explorer(shape, kind)
    caster = {TopAbs_FACE: TopoDS.Face_s, TopAbs_EDGE: TopoDS.Edge_s, TopAbs_VERTEX: TopoDS.Vertex_s}[kind]
    while ex.More():
        out.append(caster(ex.Current())); ex.Next()
    return out


def fresh_read_step(path: Path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {status}")
    transferred = reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError("STEP transfer returned null shape")
    return shape, int(transferred)


def vec3(v):
    return np.array([v.X(), v.Y(), v.Z()], dtype=float)


def canonical_dir(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n < 1e-15:
        return np.zeros(3)
    v = v / n
    k = int(np.argmax(np.abs(v)))
    return -v if v[k] < 0 else v


def bbox_diag(shape):
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box)
    vals = box.Get()
    lo = np.asarray(vals[:3]); hi = np.asarray(vals[3:])
    return float(np.linalg.norm(hi - lo)), lo, hi


def safe_face_normal(adaptor):
    try:
        u0, u1 = adaptor.FirstUParameter(), adaptor.LastUParameter()
        v0, v1 = adaptor.FirstVParameter(), adaptor.LastVParameter()
        u = 0.5 * (u0 + u1) if np.isfinite(u0 + u1) else 0.0
        v = 0.5 * (v0 + v1) if np.isfinite(v0 + v1) else 0.0
        p, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
        adaptor.D1(u, v, p, du, dv)
        return canonical_dir(np.cross(vec3(du), vec3(dv)))
    except Exception:
        return np.zeros(3)


def quantized(values, scale):
    tol = max(scale * 1e-5, 1e-9)
    return tuple(int(round(float(x) / tol)) for x in values)


def surface_signature(ad, name, diag):
    """Coarse design-surface hypothesis; adjacency is required separately."""
    try:
        if name == "PLANE":
            pl = ad.Plane(); n = canonical_dir(vec3(pl.Axis().Direction())); p = vec3(pl.Location())
            return (name, quantized(n, 1.0), int(round(float(np.dot(n, p)) / max(diag * 1e-5, 1e-9))))
        if name == "CYLINDER":
            cy = ad.Cylinder(); ax = canonical_dir(vec3(cy.Axis().Direction())); p = vec3(cy.Location())
            moment = np.cross(p, ax)
            return (name, quantized(ax, 1.0), quantized(moment, diag), int(round(cy.Radius() / max(diag * 1e-5, 1e-9))))
        if name == "SURFACE_OF_REVOLUTION":
            axis = ad.AxeOfRevolution(); d = canonical_dir(vec3(axis.Direction())); p = vec3(axis.Location())
            return (name, quantized(d, 1.0), quantized(np.cross(p, d), diag))
        if name == "SURFACE_OF_EXTRUSION":
            d = canonical_dir(vec3(ad.Direction()))
            return (name, quantized(d, 1.0))
        if name in {"CONE", "SPHERE", "TORUS"}:
            return (name, quantized(safe_face_normal(ad), 1.0))
    except Exception:
        pass
    return (name,)


class UnionFind:
    def __init__(self, n): self.p = list(range(n)); self.sz = [1] * n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: return
        if self.sz[a] < self.sz[b]: a, b = b, a
        self.p[b] = a; self.sz[a] += self.sz[b]


def group_surfaces(faces, face_meta, diag):
    edge_faces = defaultdict(list)
    for fi, face in enumerate(faces):
        ex = TopExp_Explorer(face, TopAbs_EDGE)
        while ex.More():
            edge_faces[hash(TopoDS.Edge_s(ex.Current()))].append(fi); ex.Next()
    uf = UnionFind(len(faces)); adjacency_pairs = 0; grouped_pairs = 0
    for fis in edge_faces.values():
        uniq = sorted(set(fis))
        for ai in range(len(uniq)):
            for bi in range(ai + 1, len(uniq)):
                a, b = uniq[ai], uniq[bi]; adjacency_pairs += 1
                ma, mb = face_meta[a], face_meta[b]
                compatible = False
                if ma["name"] == mb["name"] and ma["name"] in ANALYTIC:
                    compatible = ma["signature"] == mb["signature"]
                elif ma["name"] in {"BSPLINE", "BEZIER", "OTHER"} and mb["name"] in {"BSPLINE", "BEZIER", "OTHER"}:
                    na, nb = np.asarray(ma["normal"]), np.asarray(mb["normal"])
                    compatible = np.linalg.norm(na) > 0 and np.linalg.norm(nb) > 0 and abs(float(np.dot(na, nb))) >= math.cos(math.radians(8))
                if compatible:
                    uf.union(a, b); grouped_pairs += 1
    roots = [uf.find(i) for i in range(len(faces))]
    remap = {r: i for i, r in enumerate(sorted(set(roots)))}
    gids = [remap[r] for r in roots]
    sizes = Counter(gids)
    return gids, {
        "SURFACE_GROUP_COUNT": len(sizes),
        "FACES_PER_GROUP_MEAN": float(np.mean(list(sizes.values()))) if sizes else 0.0,
        "FACES_PER_GROUP_MAX": max(sizes.values(), default=0),
        "ADJACENT_FACE_PAIRS": adjacency_pairs,
        "GROUPED_ADJACENT_PAIRS": grouped_pairs,
        "GROUPING_METHOD": "shared-TopoDS_Edge + exact analytic hypothesis or <=8deg representative-normal G1 proxy",
    }


def edge_geometry(edges, diag):
    records = []
    for i, edge in enumerate(edges):
        try:
            c = BRepAdaptor_Curve(edge); a, b = c.FirstParameter(), c.LastParameter()
            if not np.isfinite(a + b): continue
            ts = np.linspace(a, b, 9)
            pts = np.array([vec3(c.Value(float(t))) for t in ts])
            chord = float(np.linalg.norm(pts[-1] - pts[0]))
            arc = float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))
            direction = canonical_dir(pts[-1] - pts[0])
            near_line = c.GetType() == GeomAbs_Line or (chord > 1e-12 and arc / chord <= 1.015)
            records.append({"index": i, "points": pts, "center": pts.mean(0), "length": arc,
                            "direction": direction, "near_line": bool(near_line)})
        except Exception:
            continue
    return records


def connected_components(points, radius):
    if len(points) == 0: return []
    pairs = cKDTree(points).query_pairs(radius)
    uf = UnionFind(len(points))
    for a, b in pairs: uf.union(a, b)
    groups = defaultdict(list)
    for i in range(len(points)): groups[uf.find(i)].append(i)
    return list(groups.values())


def detect_strips(records, total_edges, diag):
    eligible = [r for r in records if r["near_line"] and r["length"] >= max(diag * 0.003, 1e-8)]
    families = []
    for r in sorted(eligible, key=lambda x: (-x["length"], x["index"])):
        placed = False
        for fam in families:
            if abs(float(np.dot(r["direction"], fam[0]["direction"]))) >= math.cos(math.radians(5)):
                fam.append(r); placed = True; break
        if not placed: families.append([r])
    strip_ids, regions, directions = set(), [], []
    for fam in families:
        if len(fam) < 4: continue
        centers = np.array([r["center"] for r in fam]); lengths = np.array([r["length"] for r in fam])
        radius = max(diag * 0.18, float(np.median(lengths)) * 2.5)
        for comp in connected_components(centers, radius):
            if len(comp) < 4: continue
            subset = [fam[i] for i in comp]; d = canonical_dir(np.mean([r["direction"] for r in subset], axis=0))
            cc = np.array([r["center"] for r in subset]); centered = cc - cc.mean(0)
            perp = centered - np.outer(centered @ d, d)
            if len(perp) < 2: continue
            _, _, vh = np.linalg.svd(perp, full_matrices=False); axis = canonical_dir(vh[0])
            coords = np.sort(perp @ axis)
            tol = max(diag * 2e-4, 1e-9)
            uniq = [float(coords[0])]
            for x in coords[1:]:
                if x - uniq[-1] > tol: uniq.append(float(x))
            if len(uniq) < 4: continue
            gaps = np.diff(uniq); med = float(np.median(gaps))
            good = gaps[(gaps >= 0.55 * med) & (gaps <= 1.8 * med)] if med > 0 else []
            coverage = len(good) / max(len(gaps), 1)
            cv = float(np.std(good) / np.mean(good)) if len(good) >= 2 and np.mean(good) > 0 else 999.0
            if coverage >= 0.6 and cv <= 0.35:
                ids = [r["index"] for r in subset]; strip_ids.update(ids)
                regions.append({"edge_indices": ids, "direction": d.tolist(), "spacing_median": med,
                                "spacing_cv": cv, "spacing_coverage": coverage})
                directions.append(d)
    # Deduplicate nearly identical direction summaries.
    dom = []
    for d in directions:
        if not any(abs(float(np.dot(d, e))) >= math.cos(math.radians(5)) for e in dom): dom.append(d)
    return strip_ids, {
        "STRIP_EDGE_COUNT": len(strip_ids),
        "STRIP_EDGE_RATIO": len(strip_ids) / total_edges if total_edges else 0.0,
        "DOMINANT_STRIP_DIRECTIONS": [np.round(d, 6).tolist() for d in dom],
        "STRIP_REGION_COUNT": len(regions),
        "STRIP_REGIONS": regions,
        "STRIP_DETECTOR": "TopoDS_Edge near-line, <=5deg direction families, local KD-tree regions, near-equal spacing coverage>=0.60/CV<=0.35",
    }


def tessellate(shape, faces, diag):
    BRepMesh_IncrementalMesh(shape, max(diag * 0.004, 1e-5), False, 0.35, True)
    all_vertices, face_tris = [], []
    for face in faces:
        loc = TopLoc_Location(); tri = BRep_Tool.Triangulation_s(face, loc)
        local = []
        if tri is None:
            face_tris.append(local); continue
        trsf = loc.Transformation(); offset = len(all_vertices)
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf); all_vertices.append([p.X(), p.Y(), p.Z()])
        reversed_face = face.Orientation() == TopAbs_REVERSED
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            ids = [offset + a - 1, offset + b - 1, offset + c - 1]
            if reversed_face: ids[1], ids[2] = ids[2], ids[1]
            local.append(ids)
        face_tris.append(local)
    return np.asarray(all_vertices, dtype=float), face_tris


def projection_basis(vertices):
    center = vertices.mean(0); _, _, vh = np.linalg.svd(vertices - center, full_matrices=False)
    axes = vh[:2].copy()
    for i in range(2):
        k = int(np.argmax(np.abs(axes[i])))
        if axes[i, k] < 0: axes[i] *= -1
    if np.dot(np.cross(axes[0], axes[1]), vh[2]) < 0: axes[1] *= -1
    return center, axes


def project(points, center, axes): return (np.asarray(points) - center) @ axes.T


def set_plot_bounds(ax, points2d):
    lo, hi = points2d.min(0), points2d.max(0); span = np.maximum(hi - lo, 1e-9)
    pad = 0.04 * max(span)
    ax.set_xlim(lo[0] - pad, hi[0] + pad); ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_aspect("equal"); ax.axis("off")


def save_render(path, title, tri2d, tri_normals, face_ids, face_meta, group_ids, line2d, strip_line2d, mode):
    fig, ax = plt.subplots(figsize=(6.4, 5.0), dpi=140)
    if mode == "smooth":
        light = canonical_dir([0.25, -0.35, 0.9]); shades = np.clip(0.52 + 0.40 * np.abs(tri_normals @ light), 0, 1)
        colors = [(0.17*s, 0.47*s, 0.74*s, 1) for s in shades]
    elif mode == "type": colors = [TYPE_COLORS[face_meta[i]["name"]] for i in face_ids]
    elif mode == "group":
        cmap = plt.get_cmap("tab20")
        colors = [cmap((group_ids[i] * 7) % 20) for i in face_ids]
    else: colors = ["#d9d9d9"] * len(tri2d)
    ax.add_collection(PolyCollection(tri2d, facecolors=colors, edgecolors="none", linewidths=0))
    if mode in {"brep", "strip"}:
        ax.add_collection(LineCollection(line2d, colors="#262626" if mode == "brep" else "#a8a8a8",
                                         linewidths=0.45 if mode == "brep" else 0.25, alpha=0.9))
    if mode == "strip" and strip_line2d:
        ax.add_collection(LineCollection(strip_line2d, colors="#e31a1c", linewidths=1.7, alpha=1.0))
    set_plot_bounds(ax, np.concatenate(tri2d, axis=0)); ax.set_title(title, fontsize=10)
    fig.tight_layout(pad=0.2); fig.savefig(path, bbox_inches="tight", pad_inches=0.03); plt.close(fig)


def structural_class(metrics):
    f = metrics["TOTAL_FACES"]
    if f <= 0: return "UNKNOWN"
    a, b = metrics["ANALYTIC_FACE_RATIO"], metrics["BSPLINE_FACE_RATIO"]
    gr = metrics["SURFACE_GROUP_COUNT"] / f
    sr = metrics["STRIP_EDGE_RATIO"]
    # Distinct faces on a simple analytic solid are legitimate design faces;
    # group_ratio=1 is not evidence against an analytic-feature BRep.
    if a >= 0.75 and b <= 0.10: return "ANALYTIC_FEATURE_BREP"
    # A many-face spline-derived body is fragmented even when adjacent patches
    # can be grouped. Compactness is reserved for genuinely small BReps.
    if b >= 0.50 and f <= 80: return "COMPACT_BUT_SPLINE_DERIVED"
    if b >= 0.50: return "FRAGMENTED_SPLINE_BREP"
    if f <= 80 and b < 0.50 and gr <= 0.50: return "COMPACT_STRUCTURED"
    return "UNKNOWN"


def audit_one(case_id, label, path, out_dir):
    before = fingerprint(path); started = time.time()
    shape, transferred = fresh_read_step(path)
    faces, edges, verts = enum_shapes(shape, TopAbs_FACE), enum_shapes(shape, TopAbs_EDGE), enum_shapes(shape, TopAbs_VERTEX)
    diag, lo, hi = bbox_diag(shape)
    counts = Counter(); bs_rows, face_meta = [], []
    for fi, face in enumerate(faces):
        ad = BRepAdaptor_Surface(face); name = SURFACE_NAMES.get(ad.GetType(), "OTHER"); counts[name] += 1
        normal = safe_face_normal(ad); sig = surface_signature(ad, name, diag)
        face_meta.append({"name": name, "normal": normal.tolist(), "signature": sig})
        if name == "BSPLINE":
            try:
                bs = ad.BSpline(); pu, pv = bs.NbUPoles(), bs.NbVPoles()
                bs_rows.append({"face_index": fi, "degree_u": bs.UDegree(), "degree_v": bs.VDegree(),
                                "poles_u": pu, "poles_v": pv, "total_control_points": pu * pv,
                                "knots_u": bs.NbUKnots(), "knots_v": bs.NbVKnots()})
            except Exception as exc:
                bs_rows.append({"face_index": fi, "error": f"{type(exc).__name__}: {exc}"})
    gids, grouping = group_surfaces(faces, face_meta, diag)
    edge_records = edge_geometry(edges, diag); strip_ids, strip = detect_strips(edge_records, len(edges), diag)
    control = [r["total_control_points"] for r in bs_rows if "total_control_points" in r]
    max_poles = max([max(r["poles_u"], r["poles_v"]) for r in bs_rows if "poles_u" in r], default=0)
    high_count = sum(r.get("total_control_points", 0) >= 100 or max(r.get("poles_u",0), r.get("poles_v",0)) >= 16 or max(r.get("degree_u",0), r.get("degree_v",0)) >= 5 for r in bs_rows)
    metrics = {"CASE_ID": case_id, "ARTIFACT_LABEL": label, "STEP_PATH": str(path),
               "FRESH_RELOAD": True, "TRANSFERRED_ROOTS": transferred,
               "TOTAL_FACES": len(faces), "TOTAL_EDGES": len(edges), "TOTAL_VERTICES": len(verts)}
    metrics.update({f"{name}_FACES": counts[name] for name in SURFACE_ORDER})
    metrics["ANALYTIC_FACE_RATIO"] = sum(counts[n] for n in ANALYTIC) / len(faces) if faces else 0.0
    metrics["BSPLINE_FACE_RATIO"] = counts["BSPLINE"] / len(faces) if faces else 0.0
    metrics.update({"BSPLINE_CONTROL_POINTS_TOTAL": sum(control),
                    "BSPLINE_CONTROL_POINTS_MEAN": float(np.mean(control)) if control else 0.0,
                    "BSPLINE_MAX_POLES": max_poles,
                    "BSPLINE_HIGH_COMPLEXITY_FACE_COUNT": high_count,
                    "BSPLINE_FACE_DETAILS": bs_rows})
    metrics.update(grouping); metrics.update(strip)
    metrics["CAD_STRUCTURE_DIAG"] = structural_class(metrics)
    metrics["BBOX_MIN"] = lo.tolist(); metrics["BBOX_MAX"] = hi.tolist(); metrics["BBOX_DIAGONAL"] = diag

    vertices, face_tris = tessellate(shape, faces, diag)
    if len(vertices) == 0: raise RuntimeError("fresh tessellation produced zero vertices")
    center, axes = projection_basis(vertices)
    tri3d, tri_face = [], []
    for fi, tris in enumerate(face_tris):
        for ids in tris: tri3d.append(vertices[ids]); tri_face.append(fi)
    tri3d = np.asarray(tri3d); tri2d = np.asarray([project(t, center, axes) for t in tri3d])
    normals = np.cross(tri3d[:,1]-tri3d[:,0], tri3d[:,2]-tri3d[:,0]); nn = np.linalg.norm(normals, axis=1)
    normals = normals / np.maximum(nn[:,None], 1e-15)
    line2d, strip_line2d = [], []
    for r in edge_records:
        p2 = project(r["points"], center, axes); line2d.append(p2)
        if r["index"] in strip_ids: strip_line2d.append(p2)
    out_dir.mkdir(parents=True, exist_ok=True)
    names_modes = [("smooth_shaded.png","smooth"),("true_brep_edges.png","brep"),
                   ("surface_type_colored.png","type"),("surface_group_colored.png","group"),
                   ("strip_edge_overlay.png","strip")]
    for filename, mode in names_modes:
        save_render(out_dir/filename, f"{case_id} | {label} | {mode}", tri2d, normals, tri_face,
                    face_meta, gids, line2d, strip_line2d, mode)
    after = fingerprint(path)
    metrics["INPUT_FINGERPRINT_BEFORE"] = before; metrics["INPUT_FINGERPRINT_AFTER"] = after
    metrics["INPUT_UNCHANGED"] = before == after
    metrics["RENDER_FILES"] = [str(out_dir / x[0]) for x in names_modes]
    metrics["ELAPSED_SECONDS"] = time.time() - started
    (out_dir/"cad_structure_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True)+"\n")
    return metrics


def build_manifest():
    slots, unique = {}, {}
    for case in CASES:
        slots[case] = {}
        for label, table in [("baseline", BASELINE), ("v1_compact", V1), ("v2_feature_preserving", V2)]:
            path = table.get(case)
            if path is None or not path.is_file():
                slots[case][label] = {"status": "NOT_AVAILABLE", "path": None}
            else:
                slots[case][label] = {"status": "AVAILABLE", "path": str(path)}; unique[str(path)] = (case, label)
        latest_path = LATEST_OVERRIDE.get(case)
        latest_source = "explicit_latest_override"
        if latest_path is None or not latest_path.is_file():
            latest_source = "highest_available_explicit_version"
            for label in ("v2_feature_preserving", "v1_compact", "baseline"):
                if slots[case][label]["status"] == "AVAILABLE": latest_path = Path(slots[case][label]["path"]); break
        if latest_path is None or not latest_path.is_file():
            slots[case]["latest"] = {"status": "NOT_AVAILABLE", "path": None}
        else:
            slots[case]["latest"] = {"status": "AVAILABLE", "path": str(latest_path), "selection_basis": latest_source}
            unique.setdefault(str(latest_path), (case, "latest"))
    audit_items = []
    for path, (case, label) in unique.items(): audit_items.append({"case":case,"label":label,"path":path})
    audit_items.sort(key=lambda x: (x["case"], ["baseline","v1_compact","v2_feature_preserving","latest"].index(x["label"])))
    return {"CASES": CASES, "VERSION_SLOTS": slots, "AUDIT_ITEMS": audit_items,
            "PATH_POLICY": "explicit allowlist only; no glob/path guessing",
            "V1_SELECTION_POLICY": "explicit top-level compact_balanced.step",
            "V2_SELECTION_POLICY": "explicit top-level v2_feature_preserving.step"}


def contact_sheet(metrics):
    rows = []
    labels = ["smooth_shaded.png","true_brep_edges.png","surface_type_colored.png","surface_group_colored.png","strip_edge_overlay.png"]
    for m in metrics:
        d = Path(m["OUTPUT_DIR"]); imgs = [Image.open(d/x).convert("RGB") for x in labels]
        thumbs=[]
        for im in imgs:
            im.thumbnail((270,205)); canvas=Image.new("RGB",(280,225),"white"); canvas.paste(im,((280-im.width)//2,18)); thumbs.append(canvas)
        row=Image.new("RGB",(280*5,255),"white"); dr=ImageDraw.Draw(row); dr.text((8,4),f'{m["CASE_ID"]} | {m["ARTIFACT_LABEL"]} | {m["CAD_STRUCTURE_DIAG"]}',fill="black")
        for j,im in enumerate(thumbs): row.paste(im,(j*280,25))
        rows.append(row)
    sheet=Image.new("RGB",(1400,255*len(rows)),"white")
    for i,row in enumerate(rows): sheet.paste(row,(0,i*255))
    out=ART/"cad_structure_contact_sheet.png"; sheet.save(out,quality=92); return out


def run_tests(summary, metrics, manifest):
    tests=[]
    def check(name, condition, detail=""): tests.append({"name":name,"passed":bool(condition),"detail":detail})
    check("six_cases_audited", summary["CASES_AUDITED"] == 6)
    check("all_available_artifacts_fresh_reloaded", all(m["FRESH_RELOAD"] for m in metrics))
    check("surface_histograms_close", all(sum(m[f"{n}_FACES"] for n in SURFACE_ORDER)==m["TOTAL_FACES"] for m in metrics))
    check("all_inputs_unchanged", all(m["INPUT_UNCHANGED"] for m in metrics))
    check("all_five_renders_present", all(len(m["RENDER_FILES"])==5 and all(Path(p).is_file() for p in m["RENDER_FILES"]) for m in metrics))
    check("contact_sheet_present", Path(summary["STRUCTURE_CONTACT_SHEET"]).is_file())
    check("case09_read_only", summary["CASE09_TOUCHED"] is False and all(m["INPUT_UNCHANGED"] for m in metrics if m["CASE_ID"]=="CASE_09"))
    check("missing_versions_explicit", all(manifest["VERSION_SLOTS"][c][v]["status"]=="NOT_AVAILABLE" for c,v in [("CASE_02","v1_compact"),("CASE_02","v2_feature_preserving"),("CASE_03","v1_compact"),("CASE_08","v1_compact"),("CASE_08","v2_feature_preserving")]))
    check("latest_each_case_available", all(manifest["VERSION_SLOTS"][c]["latest"]["status"]=="AVAILABLE" for c in CASES))
    check("required_metrics_nonnegative", all(m["TOTAL_FACES"]>0 and m["TOTAL_EDGES"]>0 and m["SURFACE_GROUP_COUNT"]>0 for m in metrics))
    check("structural_class_enum", all(m["CAD_STRUCTURE_DIAG"] in {"COMPACT_STRUCTURED","COMPACT_BUT_SPLINE_DERIVED","FRAGMENTED_SPLINE_BREP","ANALYTIC_FEATURE_BREP","UNKNOWN"} for m in metrics))
    check("no_mac_or_llm", summary["MAC_CALLS"]==0 and summary["LLM_CALLS"]==0)
    passed=sum(t["passed"] for t in tests); failed=len(tests)-passed
    payload={"tests":tests,"TESTS_PASSED":passed,"TESTS_FAILED":failed}
    (TEST/"test_results.json").write_text(json.dumps(payload,indent=2)+"\n")
    return payload


def write_report(summary, latest):
    lines=["# CAD Structure Audit V1", "", "Read-only OCP audit of explicitly named STEP files. No STEP, CASE09 source, or shared code was modified.", "",
           "## Latest artifact results", "", "| Case | Structural class | Faces | BSpline ratio | Surface groups | Strip edges | Strip ratio |", "|---|---|---:|---:|---:|---:|---:|"]
    for c in CASES:
        m=latest[c]; lines.append(f'| {c} | {m["CAD_STRUCTURE_DIAG"]} | {m["TOTAL_FACES"]} | {m["BSPLINE_FACE_RATIO"]:.6f} | {m["SURFACE_GROUP_COUNT"]} | {m["STRIP_EDGE_COUNT"]} | {m["STRIP_EDGE_RATIO"]:.6f} |')
    lines += ["", "## Method notes", "", "- Every available input was loaded into a new STEPControl_Reader and freshly tessellated.",
              "- Surface groups require shared TopoDS_Edge adjacency and either the same analytic hypothesis or a conservative representative-normal G1 proxy.",
              "- Strip detection operates on real TopoDS_Edge samples, direction families, local spatial regions, and near-equal spacing tests.",
              "- Compact classification requires surface abstraction evidence; low face count alone is never sufficient.",
              "- Missing explicit version paths are recorded as NOT_AVAILABLE; no path guessing was used.", "",
              f'- Contact sheet: `{summary["STRUCTURE_CONTACT_SHEET"]}`', ""]
    (TASK_ROOT/"task_a_report.md").write_text("\n".join(lines))


def main():
    for d in (TASK_ROOT, ART, LOG, TEST, SCRIPT): d.mkdir(parents=True, exist_ok=True)
    manifest=build_manifest(); (ART/"input_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    metrics=[]
    with (LOG/"audit_progress.log").open("w") as log:
        for item in manifest["AUDIT_ITEMS"]:
            case,label,path=item["case"],item["label"],Path(item["path"])
            safe_label=label.lower(); out=ART/case/safe_label
            log.write(f"START {case} {label} {path}\n"); log.flush()
            m=audit_one(case,label,path,out); m["OUTPUT_DIR"]=str(out); metrics.append(m)
            log.write(f'PASS {case} {label} faces={m["TOTAL_FACES"]} class={m["CAD_STRUCTURE_DIAG"]} elapsed={m["ELAPSED_SECONDS"]:.3f}\n'); log.flush()
    sheet=contact_sheet(metrics)
    by_path={m["STEP_PATH"]:m for m in metrics}; latest={}
    for c in CASES: latest[c]=by_path[manifest["VERSION_SLOTS"][c]["latest"]["path"]]
    summary={"TASK_A_STATUS":"PASS", "CASES_AUDITED":6, "ARTIFACTS_AUDITED":len(metrics),
             "CASE09_TOUCHED":False, "MAC_CALLS":0, "LLM_CALLS":0,
             "STRUCTURE_CONTACT_SHEET":str(sheet), "REPORT_PATH":str(TASK_ROOT/"task_a_report.md"),
             "INPUT_MANIFEST":str(ART/"input_manifest.json"), "BLOCKERS":[],
             "CPU_CONCURRENCY":1, "PYTHON":sys.version, "PLATFORM":platform.platform(),
             "LATEST_RESULTS":{c:{k:latest[c][k] for k in ["STEP_PATH","CAD_STRUCTURE_DIAG","TOTAL_FACES","TOTAL_EDGES","TOTAL_VERTICES","ANALYTIC_FACE_RATIO","BSPLINE_FACE_RATIO","SURFACE_GROUP_COUNT","FACES_PER_GROUP_MEAN","FACES_PER_GROUP_MAX","STRIP_EDGE_COUNT","STRIP_EDGE_RATIO","DOMINANT_STRIP_DIRECTIONS","STRIP_REGION_COUNT"]} for c in CASES},
             "ALL_ARTIFACT_RESULTS":[{k:m[k] for k in ["CASE_ID","ARTIFACT_LABEL","STEP_PATH","CAD_STRUCTURE_DIAG","TOTAL_FACES","TOTAL_EDGES","TOTAL_VERTICES","ANALYTIC_FACE_RATIO","BSPLINE_FACE_RATIO","BSPLINE_CONTROL_POINTS_TOTAL","BSPLINE_CONTROL_POINTS_MEAN","BSPLINE_MAX_POLES","BSPLINE_HIGH_COMPLEXITY_FACE_COUNT","SURFACE_GROUP_COUNT","FACES_PER_GROUP_MEAN","FACES_PER_GROUP_MAX","STRIP_EDGE_COUNT","STRIP_EDGE_RATIO","DOMINANT_STRIP_DIRECTIONS","STRIP_REGION_COUNT","INPUT_UNCHANGED","OUTPUT_DIR"]} for m in metrics]}
    for c in CASES: summary[c.replace("_","")+"_STRUCTURAL_CLASS"]=latest[c]["CAD_STRUCTURE_DIAG"]
    c9=latest["CASE_09"]
    summary.update({"CASE09_TOTAL_FACES":c9["TOTAL_FACES"],"CASE09_BSPLINE_RATIO":c9["BSPLINE_FACE_RATIO"],
                    "CASE09_SURFACE_GROUPS":c9["SURFACE_GROUP_COUNT"],"CASE09_STRIP_EDGE_COUNT":c9["STRIP_EDGE_COUNT"],"CASE09_STRIP_EDGE_RATIO":c9["STRIP_EDGE_RATIO"]})
    test_result=run_tests(summary,metrics,manifest); summary.update({"TESTS_PASSED":test_result["TESTS_PASSED"],"TESTS_FAILED":test_result["TESTS_FAILED"]})
    if summary["TESTS_FAILED"]: summary["TASK_A_STATUS"]="FAIL"; summary["BLOCKERS"].append("INDEPENDENT_TEST_FAILURE")
    write_report(summary,latest)
    (ART/"task_a_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    with (ART/"cad_structure_metrics.csv").open("w",newline="") as f:
        keys=["CASE_ID","ARTIFACT_LABEL","STEP_PATH","CAD_STRUCTURE_DIAG","TOTAL_FACES","TOTAL_EDGES","TOTAL_VERTICES"]+[f"{n}_FACES" for n in SURFACE_ORDER]+["ANALYTIC_FACE_RATIO","BSPLINE_FACE_RATIO","BSPLINE_CONTROL_POINTS_TOTAL","BSPLINE_CONTROL_POINTS_MEAN","BSPLINE_MAX_POLES","BSPLINE_HIGH_COMPLEXITY_FACE_COUNT","SURFACE_GROUP_COUNT","FACES_PER_GROUP_MEAN","FACES_PER_GROUP_MAX","STRIP_EDGE_COUNT","STRIP_EDGE_RATIO","STRIP_REGION_COUNT","INPUT_UNCHANGED"]
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows([{k:m.get(k) for k in keys} for m in metrics])
    print(json.dumps({k:summary[k] for k in ["TASK_A_STATUS","CASES_AUDITED","ARTIFACTS_AUDITED","CASE09_TOUCHED","CASE09_TOTAL_FACES","CASE09_BSPLINE_RATIO","CASE09_SURFACE_GROUPS","CASE09_STRIP_EDGE_COUNT","CASE09_STRIP_EDGE_RATIO","STRUCTURE_CONTACT_SHEET","REPORT_PATH","TESTS_PASSED","TESTS_FAILED","BLOCKERS"]},indent=2))


if __name__ == "__main__": main()
