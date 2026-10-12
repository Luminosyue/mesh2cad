#!/usr/bin/env python3
"""TANK_FROZEN_P3_TO_CADFIT_V1

Read-only reuse of frozen tank P3 component meshes. All writes stay inside
ours3/tank_frozen_p3_to_cadfit_v1/. Uses the real CADFit run_pipeline.py.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

OCC_LOCK = threading.Lock()

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection

EXPERIMENT = "TANK_FROZEN_P3_TO_CADFIT_V1"
ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3" / "tank_frozen_p3_to_cadfit_v1"
P3_SOURCE = ROOT / "ours3" / "tank_p3_rerun_v1" / "p3_max_367k_4000"
SOURCE_TANK_OBJ = ROOT / "ours3" / "meshes" / "yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
CADFIT_REPO = ROOT / "CADFit"
CADFIT_PY = Path("/data/miniconda3/envs/cadfit-env/bin/python")
CADFIT_PIPELINE = CADFIT_REPO / "run_pipeline.py"

CADFIT_TIMEOUT = int(os.environ.get("CADFIT_TIMEOUT_SECONDS", "1800"))
CADFIT_INNER_WORKERS = int(os.environ.get("CADFIT_INNER_WORKERS", "8"))
CADFIT_PARALLEL = int(os.environ.get("CADFIT_PARALLEL", "4"))
CADFIT_MAX_ITERATIONS = 1

QA_SOURCE_SAMPLES = 4096
QA_CAND_SAMPLES = 4096
QA_COVERAGE_FRAC = 0.01
QA_CHAMFER_DIAG = 0.05
QA_HAUSDORFF_DIAG = 0.15
QA_COVERAGE_MIN = 0.50
QA_FP_MAX = 0.25

VIEW = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]], dtype=np.float64)
VIEW_Z = np.array([0.408, 0.408, 0.816], dtype=np.float64)

FAILURE_LABELS = {
    "NON_WATERTIGHT",
    "NON_MANIFOLD",
    "CADFIT_RUNTIME_ERROR",
    "CADFIT_NO_PROGRAM",
    "CADFIT_OPTIMIZATION_FAIL",
    "CADQUERY_EXECUTION_FAIL",
    "STEP_EXPORT_FAIL",
    "STEP_RELOAD_FAIL",
    "INVALID_BREP",
    "FACETED_ONLY",
    "GEOMETRY_QA_FAIL",
    "TIMEOUT",
    "UNKNOWN",
    "CADFIT_SKIPPED_NON_WATERTIGHT",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_meta(path: Path) -> dict:
    st = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": int(st.st_size),
        "mtime_unix": float(st.st_mtime),
        "mtime_iso": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        "sha256": sha256_file(path),
    }


def snapshot_tree(root: Path) -> dict:
    files = {}
    if not root.exists():
        return {"root": str(root), "exists": False, "files": files}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            files[str(p)] = file_meta(p)
    return {"root": str(root), "exists": True, "file_count": len(files), "files": files}


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    log_path = OUT / "logs" / "run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        geoms = [g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
        mesh = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    if not isinstance(mesh, trimesh.Trimesh):
        mesh = trimesh.Trimesh(getattr(mesh, "vertices", []), getattr(mesh, "faces", []))
    return mesh


def edge_counts(mesh: trimesh.Trimesh) -> tuple[int, int]:
    if len(mesh.faces) == 0:
        return 0, 0
    uniq, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    return int((counts == 1).sum()), int((counts > 2).sum())


def connected_component_count(mesh: trimesh.Trimesh) -> int:
    n = int(len(mesh.faces))
    if n == 0:
        return 0
    adj = np.asarray(mesh.face_adjacency)
    parent = np.arange(n, dtype=np.int32)

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = int(parent[x])
        return x

    if adj.size:
        for a, b in adj:
            ra, rb = find(int(a)), find(int(b))
            if ra != rb:
                parent[rb] = ra
    roots = {find(i) for i in range(n)}
    return int(len(roots))


def mesh_audit(path: Path) -> dict:
    mesh = load_mesh(path)
    boundary, nonman = edge_counts(mesh)
    watertight = bool(mesh.is_watertight)
    volume = None
    try:
        volume = float(mesh.volume)
    except Exception:
        volume = None
    bbox = [float(x) for x in np.asarray(mesh.extents).tolist()] if len(mesh.vertices) else [0.0, 0.0, 0.0]
    return {
        "path": str(path),
        "vertex_count": int(len(mesh.vertices)),
        "triangle_count": int(len(mesh.faces)),
        "connected_components": connected_component_count(mesh),
        "is_watertight": watertight,
        "is_manifold": bool(nonman == 0),
        "boundary_edge_count": boundary,
        "nonmanifold_edge_count": nonman,
        "bbox_x": bbox[0],
        "bbox_y": bbox[1],
        "bbox_z": bbox[2],
        "surface_area": float(mesh.area) if len(mesh.faces) else 0.0,
        "volume_if_available": volume,
        "is_winding_consistent": bool(getattr(mesh, "is_winding_consistent", False)),
    }


def classify_and_maybe_repair(part_id: str, obj_path: Path, audit: dict) -> dict:
    result = {
        "part_id": part_id,
        "watertight_class": "C",
        "repaired": False,
        "repair_method": None,
        "repair_path": None,
        "added_faces": 0,
        "geometry_deviation": None,
        "cadfit_eligible": False,
        "cadfit_input_kind": None,
        "skip_reason": None,
    }
    if audit["is_watertight"] and audit["is_manifold"]:
        result.update({"watertight_class": "A", "cadfit_eligible": True, "cadfit_input_kind": "original"})
        return result
    mesh = load_mesh(obj_path)
    original_faces = int(len(mesh.faces))
    original_area = float(mesh.area) if original_faces else 0.0
    repaired = mesh.copy()
    try:
        trimesh.repair.fill_holes(repaired)
    except Exception as e:
        result.update({"watertight_class": "C", "skip_reason": "NON_WATERTIGHT", "repair_method": f"fill_holes_failed:{type(e).__name__}"})
        # CADFit itself continues on open meshes via internal alpha-wrap.
        result["cadfit_eligible"] = True
        result["cadfit_input_kind"] = "original_open"
        return result
    added = int(len(repaired.faces) - original_faces)
    added_ratio = added / max(original_faces, 1)
    new_area = float(repaired.area) if len(repaired.faces) else 0.0
    area_ratio = (new_area - original_area) / max(original_area, 1e-12)
    diag = max(float(np.linalg.norm(mesh.extents)), 1e-12)
    try:
        from scipy.spatial import cKDTree

        d = cKDTree(np.asarray(repaired.vertices)).query(np.asarray(mesh.vertices), workers=1)[0]
        deviation = float(np.max(d)) if len(d) else None
    except Exception:
        deviation = None
    result["added_faces"] = added
    result["geometry_deviation"] = deviation
    trivial = (
        bool(repaired.is_watertight)
        and added_ratio <= 0.15
        and area_ratio <= 0.15
        and added >= 0
        and (deviation is None or deviation <= 0.02 * diag)
        and audit["boundary_edge_count"] <= max(80, int(0.08 * original_faces * 1.5))
    )
    if trivial:
        repair_path = OUT / "inputs" / "cadfit_repaired" / f"{part_id}.obj"
        repaired.export(repair_path)
        result.update(
            {
                "watertight_class": "B",
                "repaired": True,
                "repair_method": "trimesh.repair.fill_holes",
                "repair_path": str(repair_path),
                "cadfit_eligible": True,
                "cadfit_input_kind": "repaired_fill_holes",
            }
        )
        return result
    # Not a trivial close. Keep original mesh; real CADFit still accepts open STLs.
    if result.get("repair_path"):
        pass
    result.update(
        {
            "watertight_class": "C",
            "cadfit_eligible": True,
            "cadfit_input_kind": "original_open",
            "repair_method": "fill_holes_not_trivial_discarded",
            "skip_reason": None,
        }
    )
    return result


def export_stl(src: Path, dst: Path) -> dict:
    mesh = load_mesh(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(dst, file_type="stl")
    return {"src": str(src), "dst": str(dst), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices))}


def count_ops(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    return {
        "cad_program_length": len(text.splitlines()),
        "sketch_count": len(re.findall(r"\bSketch\b|cq\.Sketch|sketch_", text)),
        "extrude_count": len(re.findall(r"\.extrude\s*\(", text, re.I)),
        "revolve_count": len(re.findall(r"\.revolve\s*\(", text, re.I)),
        "union_count": len(re.findall(r"\.union\s*\(|\.add\s*\(", text, re.I)),
        "cut_count": len(re.findall(r"\.cut\s*\(|cutBlind|hole\s*\(", text, re.I)),
        "fillet_count": len(re.findall(r"\.fillet\s*\(", text, re.I)),
        "chamfer_count": len(re.findall(r"\.chamfer\s*\(", text, re.I)),
        "has_cad_native_ops": bool(re.search(r"\.extrude\s*\(|\.revolve\s*\(|\.fillet\s*\(|\.chamfer\s*\(", text, re.I)),
    }


def cadfit_runtime_info() -> dict:
    pkg_versions = {}
    for name in ["cadquery", "trimesh", "numpy", "torch", "scipy", "matplotlib", "OCP", "casadi"]:
        try:
            import importlib.metadata as md

            pkg_versions[name] = md.version(name)
        except Exception:
            try:
                mod = __import__(name)
                pkg_versions[name] = getattr(mod, "__version__", getattr(mod, "__file__", "present"))
            except Exception as e:
                pkg_versions[name] = f"unavailable:{type(e).__name__}"
    commit = subprocess.check_output(["git", "-C", str(CADFIT_REPO), "rev-parse", "HEAD"], text=True).strip()
    help_run = subprocess.run([str(CADFIT_PY), str(CADFIT_PIPELINE), "--help"], cwd=str(CADFIT_REPO), capture_output=True, text=True, timeout=60)
    info = {
        "REAL_CADFIT": True,
        "repository": str(CADFIT_REPO),
        "commit": commit,
        "python_executable": str(CADFIT_PY),
        "pipeline": str(CADFIT_PIPELINE),
        "package_versions": pkg_versions,
        "command_template": [
            str(CADFIT_PY),
            str(CADFIT_PIPELINE),
            "<isolated_input_dir>",
            "--output-folder",
            "<part_cadfit_raw>",
            "--max-iterations",
            str(CADFIT_MAX_ITERATIONS),
            "--limit",
            "1",
        ],
        "CADFIT_INNER_WORKERS": CADFIT_INNER_WORKERS,
        "timeout_seconds": CADFIT_TIMEOUT,
        "help_excerpt": (help_run.stdout or help_run.stderr)[-4000:],
        "git_remote": subprocess.check_output(["git", "-C", str(CADFIT_REPO), "remote", "-v"], text=True).strip(),
    }
    return info


def pick_cad_object(ns: dict):
    for key in ("final_result", "result"):
        if key in ns and ns[key] is not None:
            return key, ns[key]
    solids = [ns[k] for k in sorted(ns) if str(k).startswith("solid_")]
    if solids:
        acc = solids[0]
        for s in solids[1:]:
            try:
                acc = acc.add(s)
            except Exception:
                try:
                    acc = acc.union(s)
                except Exception:
                    pass
        return "union_of_solid_star", acc
    for key, value in list(ns.items())[::-1]:
        if str(key).startswith("_"):
            continue
        if hasattr(value, "val") or hasattr(value, "wrapped"):
            if str(key).startswith(("solid_", "sketch_", "plane_", "loop_")):
                continue
            return key, value
    return None, None


def export_step_from_program(program: Path, step_path: Path, stl_path: Path, brep_path: Path) -> dict:
    import cadquery as cq

    report = {
        "program": str(program),
        "step_generated": False,
        "stl_generated": False,
        "brep_generated": False,
        "export_var": None,
        "error": "",
    }
    ns = {"__name__": "__main__", "__file__": str(program)}
    try:
        code = compile(program.read_text(encoding="utf-8"), str(program), "exec")
        exec(code, ns, ns)
        key, obj = pick_cad_object(ns)
        report["export_var"] = key
        if obj is None:
            report["error"] = "CADQUERY_EXECUTION_FAIL:no CadQuery object"
            return report
        cq.exporters.export(obj, str(step_path))
        report["step_generated"] = step_path.exists() and step_path.stat().st_size > 0
        try:
            cq.exporters.export(obj, str(stl_path))
            report["stl_generated"] = stl_path.exists() and stl_path.stat().st_size > 0
        except Exception as e:
            report["stl_error"] = repr(e)
        try:
            shape = obj.val() if hasattr(obj, "val") else obj
            wrapped = shape.wrapped if hasattr(shape, "wrapped") else shape
            from OCP.BRep import BRep_Builder
            from OCP.BRepTools import BRepTools
            from OCP.TopoDS import TopoDS_Shape

            if not isinstance(wrapped, TopoDS_Shape):
                wrapped = wrapped
            BRepTools.Write_s(wrapped, str(brep_path))
            report["brep_generated"] = brep_path.exists() and brep_path.stat().st_size > 0
        except Exception as e:
            report["brep_error"] = repr(e)
    except Exception as e:
        report["error"] = f"CADQUERY_EXECUTION_FAIL:{type(e).__name__}:{e}"
        report["traceback"] = traceback.format_exc()[-4000:]
    return report


def occ_reload(step_path: Path) -> dict:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopoDS import TopoDS

    SURFACE_NAMES = {
        "GeomAbs_Plane": "plane",
        "GeomAbs_Cylinder": "cylinder",
        "GeomAbs_Cone": "cone",
        "GeomAbs_Sphere": "sphere",
        "GeomAbs_Torus": "torus",
        "GeomAbs_BezierSurface": "bezier",
        "GeomAbs_BSplineSurface": "bspline",
    }

    def indexed(shape, kind):
        m = TopTools_IndexedMapOfShape()
        TopExp.MapShapes_s(shape, kind, m)
        return m

    def enum_name(value):
        s = str(value)
        return SURFACE_NAMES.get(s.split(".")[-1], "other")

    def face_is_triangle(face) -> bool:
        v = indexed(face, TopAbs_VERTEX)
        e = indexed(face, TopAbs_EDGE)
        return v.Extent() == 3 and e.Extent() == 3

    out = {
        "step_reload_success": False,
        "shape_type": None,
        "solid_count": 0,
        "shell_count": 0,
        "face_count": 0,
        "edge_count": 0,
        "vertex_count": 0,
        "brep_valid": False,
        "plane_faces": 0,
        "cylinder_faces": 0,
        "cone_faces": 0,
        "sphere_faces": 0,
        "torus_faces": 0,
        "bspline_faces": 0,
        "other_surface_faces": 0,
        "triangular_planar_faces": 0,
        "faceted_brep": False,
        "error": "",
    }
    try:
        reader = STEPControl_Reader()
        status = reader.ReadFile(str(step_path))
        if status != IFSelect_RetDone:
            out["error"] = "STEP_RELOAD_FAIL:ReadFile"
            return out
        roots = int(reader.TransferRoots())
        if roots <= 0:
            out["error"] = "STEP_RELOAD_FAIL:TransferRoots"
            return out
        shape = reader.OneShape()
        if shape is None or shape.IsNull():
            out["error"] = "STEP_RELOAD_FAIL:empty_shape"
            return out
        out["step_reload_success"] = True
        out["shape_type"] = str(shape.ShapeType()).split(".")[-1]
        faces = indexed(shape, TopAbs_FACE)
        edges = indexed(shape, TopAbs_EDGE)
        verts = indexed(shape, TopAbs_VERTEX)
        solids = indexed(shape, TopAbs_SOLID)
        shells = indexed(shape, TopAbs_SHELL)
        out.update(
            {
                "solid_count": int(solids.Extent()),
                "shell_count": int(shells.Extent()),
                "face_count": int(faces.Extent()),
                "edge_count": int(edges.Extent()),
                "vertex_count": int(verts.Extent()),
                "brep_valid": bool(BRepCheck_Analyzer(shape).IsValid()),
            }
        )
        counts = {k: 0 for k in ["plane", "cylinder", "cone", "sphere", "torus", "bspline", "other"]}
        tri_planar = 0
        for i in range(1, faces.Extent() + 1):
            face = TopoDS.Face_s(faces.FindKey(i))
            try:
                kind = enum_name(BRepAdaptor_Surface(face).GetType())
            except Exception:
                kind = "other"
            if kind not in counts:
                kind = "other"
            counts[kind] += 1
            if kind == "plane" and face_is_triangle(face):
                tri_planar += 1
        out.update(
            {
                "plane_faces": counts["plane"],
                "cylinder_faces": counts["cylinder"],
                "cone_faces": counts["cone"],
                "sphere_faces": counts["sphere"],
                "torus_faces": counts["torus"],
                "bspline_faces": counts["bspline"],
                "other_surface_faces": counts["other"],
                "triangular_planar_faces": tri_planar,
            }
        )
        face_count = max(out["face_count"], 1)
        tri_ratio = tri_planar / face_count
        out["faceted_brep"] = bool(out["face_count"] > 1000 and tri_ratio >= 0.95)
        box = Bnd_Box()
        BRepBndLib.Add_s(shape, box, True)
        xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
        out["bbox"] = [xmin, ymin, zmin, xmax, ymax, zmax]
        try:
            props = GProp_GProps()
            BRepGProp.VolumeProperties_s(shape, props)
            out["volume"] = float(props.Mass())
        except Exception:
            out["volume"] = None
    except Exception as e:
        out["error"] = f"STEP_RELOAD_FAIL:{type(e).__name__}:{e}"
        out["traceback"] = traceback.format_exc()[-2500:]
    return out


def sample_surface(mesh: trimesh.Trimesh, n: int, seed: int) -> np.ndarray:
    if len(mesh.faces) == 0 or len(mesh.vertices) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    try:
        pts, _ = trimesh.sample.sample_surface(mesh, n, seed=seed)
        return np.asarray(pts, dtype=np.float64)
    except Exception:
        idx = np.random.default_rng(seed).choice(len(mesh.vertices), size=min(n, len(mesh.vertices)), replace=len(mesh.vertices) < n)
        return np.asarray(mesh.vertices, dtype=np.float64)[idx]


def nearest(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    if len(src) == 0 or len(dst) == 0:
        return np.full(len(src), np.inf, dtype=np.float64)
    from scipy.spatial import cKDTree

    return cKDTree(dst).query(src, workers=1)[0]


def bbox_fp_occupancy(source: np.ndarray, candidate: np.ndarray) -> float:
    if len(source) == 0 or len(candidate) == 0:
        return 1.0
    smin, smax = source.min(0), source.max(0)
    cmin, cmax = candidate.min(0), candidate.max(0)
    inter = np.maximum(0.0, np.minimum(smax, cmax) - np.maximum(smin, cmin))
    cvol = float(np.prod(np.maximum(0.0, cmax - cmin)))
    if cvol <= 1e-12:
        return 1.0
    ivol = float(np.prod(inter))
    return float(max(0.0, cvol - ivol) / cvol)


def cadfit_normalize_params(mesh: trimesh.Trimesh) -> tuple[np.ndarray, float]:
    bb_min, bb_max = np.asarray(mesh.bounds, dtype=np.float64)
    center = 0.5 * (bb_min + bb_max)
    max_dim = float((bb_max - bb_min).max())
    scale = 2.0 / max_dim if max_dim > 0 else 1.0
    return center, scale


def unnormalize_cadfit_mesh(cad_mesh: trimesh.Trimesh, source_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    center, scale = cadfit_normalize_params(source_mesh)
    out = cad_mesh.copy()
    if scale == 0:
        return out
    out.apply_scale(1.0 / scale)
    out.apply_translation(center)
    return out


def geometry_qa(source_mesh: trimesh.Trimesh, cad_mesh: trimesh.Trimesh) -> dict:
    src = sample_surface(source_mesh, QA_SOURCE_SAMPLES, 20260817)
    cad = sample_surface(cad_mesh, QA_CAND_SAMPLES, 20260817 + 17)
    a2b = nearest(src, cad)
    b2a = nearest(cad, src)
    diag = max(float(np.linalg.norm(source_mesh.extents)), 1e-12)
    thr = max(diag * QA_COVERAGE_FRAC, 1e-8)
    all_d = np.concatenate([a2b, b2a]) if len(a2b) + len(b2a) else np.array([], dtype=np.float64)
    chamfer = float(np.mean(all_d)) if len(all_d) else float("inf")
    hausdorff = float(np.max(all_d)) if len(all_d) else float("inf")
    coverage = float(np.mean(a2b <= thr)) if len(a2b) else 0.0
    fp = bbox_fp_occupancy(src, cad)
    return {
        "chamfer": chamfer,
        "hausdorff": hausdorff,
        "coverage": coverage,
        "fp_occupancy": fp,
        "coverage_threshold": thr,
        "bbox_diagonal": diag,
        "chamfer_normalized": chamfer / diag,
        "hausdorff_normalized": hausdorff / diag,
        "source_sample_count": int(len(src)),
        "candidate_sample_count": int(len(cad)),
    }


def project(mesh: trimesh.Trimesh, center: np.ndarray, scale: float):
    verts = (np.asarray(mesh.vertices) - center) / scale
    pts = verts @ VIEW.T
    z = verts @ VIEW_Z
    return pts, z


def draw_mesh(ax, mesh: trimesh.Trimesh, center, scale, color, alpha=1.0):
    if mesh is None or len(mesh.faces) == 0:
        ax.set_aspect("equal")
        ax.set_xlim(-0.75, 0.75)
        ax.set_ylim(-0.75, 0.75)
        ax.axis("off")
        return
    pts, z = project(mesh, center, scale)
    faces = np.asarray(mesh.faces)
    order = np.argsort(z[faces].mean(axis=1))
    tri = pts[faces[order]]
    shade = z[faces[order]].mean(axis=1)
    shade = (shade - shade.min()) / (np.ptp(shade) + 1e-9)
    base = np.array(matplotlib.colors.to_rgb(color))
    colors = np.clip(base * (0.55 + 0.45 * shade[:, None]), 0, 1)
    ax.add_collection(PolyCollection(tri, facecolors=colors, edgecolors=(0, 0, 0, 0.03), linewidths=0.04, alpha=alpha))
    ax.set_aspect("equal")
    ax.set_xlim(-0.75, 0.75)
    ax.set_ylim(-0.75, 0.75)
    ax.axis("off")


def render_part(part_dir: Path, source_mesh: trimesh.Trimesh, cad_mesh, status: str) -> dict:
    with OCC_LOCK:
        return _render_part_unlocked(part_dir, source_mesh, cad_mesh, status)


def _render_part_unlocked(part_dir: Path, source_mesh: trimesh.Trimesh, cad_mesh, status: str) -> dict:
    qa_dir = part_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    meshes = [source_mesh]
    if cad_mesh is not None and len(getattr(cad_mesh, "faces", [])) > 0:
        meshes.append(cad_mesh)
    bounds = np.vstack([m.bounds for m in meshes if len(m.vertices)])
    center = (bounds.min(0) + bounds.max(0)) / 2
    scale = float(np.linalg.norm(bounds.max(0) - bounds.min(0))) or 1.0
    paths = {}
    for name, mesh, color in [
        ("source_p3.png", source_mesh, "#4c7bd9"),
        ("cadfit_cad.png", cad_mesh, "#d98946"),
    ]:
        fig, ax = plt.subplots(figsize=(4.2, 4.0), dpi=110)
        draw_mesh(ax, mesh, center, scale, color)
        ax.set_title(name.replace(".png", ""), fontsize=8)
        fig.savefig(qa_dir / name, bbox_inches="tight", pad_inches=0.04, facecolor="white")
        plt.close(fig)
        paths[name] = str(qa_dir / name)
    fig, ax = plt.subplots(figsize=(4.2, 4.0), dpi=110)
    draw_mesh(ax, source_mesh, center, scale, "#4c7bd9", alpha=0.55)
    if cad_mesh is not None:
        draw_mesh(ax, cad_mesh, center, scale, "#d98946", alpha=0.55)
    ax.set_title("overlay")
    fig.savefig(qa_dir / "overlay.png", bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    paths["overlay.png"] = str(qa_dir / "overlay.png")
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.4), dpi=110)
    draw_mesh(axes[0], source_mesh, center, scale, "#4c7bd9")
    axes[0].set_title("P3 Part")
    draw_mesh(axes[1], cad_mesh, center, scale, "#d98946")
    axes[1].set_title("CADFit CAD")
    draw_mesh(axes[2], source_mesh, center, scale, "#4c7bd9", alpha=0.5)
    if cad_mesh is not None:
        draw_mesh(axes[2], cad_mesh, center, scale, "#d98946", alpha=0.5)
    axes[2].set_title(status[:28])
    fig.savefig(qa_dir / "row.png", bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    paths["row.png"] = str(qa_dir / "row.png")
    return paths


def run_cadfit_one(part_id: str, stl_path: Path, part_dir: Path) -> dict:
    cad_in = part_dir / "cadfit_input_dir"
    cad_raw = part_dir / "cadfit" / "raw"
    cad_in.mkdir(parents=True, exist_ok=True)
    cad_raw.mkdir(parents=True, exist_ok=True)
    isolated = cad_in / f"{part_id}.stl"
    if isolated.exists():
        isolated.unlink()
    shutil.copy2(stl_path, isolated)
    stdout = part_dir / "cadfit" / "stdout.log"
    stderr = part_dir / "cadfit" / "stderr.log"
    cmd = [
        str(CADFIT_PY),
        str(CADFIT_PIPELINE),
        str(cad_in),
        "--output-folder",
        str(cad_raw),
        "--max-iterations",
        str(CADFIT_MAX_ITERATIONS),
        "--limit",
        "1",
        "--skip-existing",
    ]
    env = os.environ.copy()
    env["CADFIT_INNER_WORKERS"] = str(CADFIT_INNER_WORKERS)
    t0 = time.time()
    status = {
        "part_id": part_id,
        "command": cmd,
        "start_time": utc_now(),
        "exit_code": None,
        "status": "exception",
        "error": "",
        "runtime_seconds": 0.0,
        "final_iou": None,
        "cadfit_duration": None,
    }
    try:
        with stdout.open("wb") as so, stderr.open("wb") as se:
            proc = subprocess.run(cmd, cwd=str(CADFIT_REPO), stdout=so, stderr=se, timeout=CADFIT_TIMEOUT, env=env)
        status["exit_code"] = proc.returncode
        if proc.returncode != 0:
            status["status"] = "process_error"
            status["error"] = "CADFIT_RUNTIME_ERROR"
        else:
            status["status"] = "ok"
    except subprocess.TimeoutExpired:
        status["status"] = "timeout"
        status["error"] = "TIMEOUT"
    except Exception as e:
        status["status"] = "exception"
        status["error"] = f"CADFIT_RUNTIME_ERROR:{type(e).__name__}:{e}"
    status["runtime_seconds"] = time.time() - t0
    status["end_time"] = utc_now()
    iou_path = cad_raw / part_id / "final_iou.json"
    if iou_path.exists():
        try:
            iou = json.loads(iou_path.read_text(encoding="utf-8"))
            status["final_iou"] = iou.get("final_iou")
            status["cadfit_duration"] = iou.get("duration")
            status["cadfit_native_metrics"] = iou
        except Exception:
            pass
    dump_json(part_dir / "cadfit" / "metadata.json", status)
    return status


def process_part(spec: dict) -> dict:
    part_id = spec["part_id"]
    part_dir = OUT / "parts" / part_id
    for sub in ("input", "cadfit", "cad", "qa"):
        (part_dir / sub).mkdir(parents=True, exist_ok=True)
    source_obj = Path(spec["copied_obj"])
    shutil.copy2(source_obj, part_dir / "input" / "source.obj")
    stl_src = Path(spec["cadfit_stl"])
    shutil.copy2(stl_src, part_dir / "input" / "cadfit_input.stl")
    raw_done = (
        (part_dir / "cadfit" / "raw" / part_id / "final_iou.json").exists()
        and (
            (part_dir / "cadfit" / "raw" / part_id / "best_greedy_parallel_iterative.py").exists()
            or (part_dir / "cadfit" / "raw" / part_id / "best_greedy_parallel.py").exists()
        )
    )
    row = {
        "part_id": part_id,
        "triangle_count": spec["audit"]["triangle_count"],
        "vertex_count": spec["audit"]["vertex_count"],
        "watertight": spec["audit"]["is_watertight"],
        "watertight_class": spec["classify"]["watertight_class"],
        "repaired": spec["classify"]["repaired"],
        "cadfit_attempted": False,
        "cadfit_success": False,
        "cad_program_generated": False,
        "cad_program_length": 0,
        "step_generated": False,
        "step_reload_success": False,
        "brep_valid": False,
        "cad_native": False,
        "faceted_brep": False,
        "chamfer": None,
        "hausdorff": None,
        "coverage": None,
        "fp_occupancy": None,
        "runtime": 0.0,
        "failure_reason": None,
        "final_iou": None,
    }
    try:
        if not spec["classify"]["cadfit_eligible"]:
            row["failure_reason"] = spec["classify"].get("skip_reason") or "CADFIT_SKIPPED_NON_WATERTIGHT"
            dump_json(part_dir / "qa" / "status.json", row)
            render_part(part_dir, load_mesh(source_obj), None, row["failure_reason"])
            return row
        row["cadfit_attempted"] = True
        if raw_done:
            iou_path = part_dir / "cadfit" / "raw" / part_id / "final_iou.json"
            iou = json.loads(iou_path.read_text(encoding="utf-8"))
            cad_status = {
                "status": "ok",
                "error": "skipped_existing",
                "runtime_seconds": float(iou.get("duration") or 0.0),
                "final_iou": iou.get("final_iou"),
            }
        else:
            cad_status = run_cadfit_one(part_id, stl_src, part_dir)
        row["runtime"] = cad_status.get("runtime_seconds")
        row["final_iou"] = cad_status.get("final_iou")
        if cad_status.get("error") in {"TIMEOUT", "CADFIT_RUNTIME_ERROR"} or str(cad_status.get("error", "")).startswith("CADFIT_RUNTIME_ERROR"):
            row["failure_reason"] = "TIMEOUT" if cad_status.get("status") == "timeout" else "CADFIT_RUNTIME_ERROR"
            dump_json(part_dir / "qa" / "status.json", row)
            render_part(part_dir, load_mesh(source_obj), None, row["failure_reason"])
            return row
        raw_dir = part_dir / "cadfit" / "raw" / part_id
        program = raw_dir / "best_greedy_parallel_iterative.py"
        if not program.exists():
            program = raw_dir / "best_greedy_parallel.py"
        cad_stl = raw_dir / "best_greedy_parallel_iterative.stl"
        if not cad_stl.exists():
            cad_stl = raw_dir / "best_greedy_parallel.stl"
        if program.exists() and program.stat().st_size > 0:
            dest_prog = part_dir / "cadfit" / "generated_code.py"
            shutil.copy2(program, dest_prog)
            row["cad_program_generated"] = True
            ops = count_ops(dest_prog)
            row.update(ops)
        else:
            row["failure_reason"] = "CADFIT_NO_PROGRAM"
            dump_json(part_dir / "qa" / "status.json", row)
            render_part(part_dir, load_mesh(source_obj), None, row["failure_reason"])
            return row
        if cad_stl.exists():
            shutil.copy2(cad_stl, part_dir / "cad" / "generated.stl")
        if not (raw_dir / "final_iou.json").exists() and cad_status.get("final_iou") is None:
            row["failure_reason"] = "CADFIT_OPTIMIZATION_FAIL"
        step_path = part_dir / "cad" / "generated.step"
        with OCC_LOCK:
            exec_rep = export_step_from_program(
                part_dir / "cadfit" / "generated_code.py",
                step_path,
                part_dir / "cad" / "generated_from_program.stl",
                part_dir / "cad" / "generated.brep",
            )
        dump_json(part_dir / "cadfit" / "step_export.json", exec_rep)
        if exec_rep.get("error", "").startswith("CADQUERY_EXECUTION_FAIL") and not exec_rep.get("step_generated"):
            row["failure_reason"] = "CADQUERY_EXECUTION_FAIL"
            dump_json(part_dir / "qa" / "status.json", row)
            render_part(part_dir, load_mesh(source_obj), load_mesh(cad_stl) if cad_stl.exists() else None, row["failure_reason"])
            return row
        row["step_generated"] = bool(exec_rep.get("step_generated"))
        if not row["step_generated"]:
            row["failure_reason"] = "STEP_EXPORT_FAIL"
            dump_json(part_dir / "qa" / "status.json", row)
            render_part(part_dir, load_mesh(source_obj), load_mesh(cad_stl) if cad_stl.exists() else None, row["failure_reason"])
            return row
        with OCC_LOCK:
            occ = occ_reload(step_path)
        dump_json(part_dir / "qa" / "occ_reload.json", occ)
        row["step_reload_success"] = bool(occ.get("step_reload_success"))
        row["brep_valid"] = bool(occ.get("brep_valid"))
        row["faceted_brep"] = bool(occ.get("faceted_brep"))
        row["occ"] = occ
        if not row["step_reload_success"]:
            row["failure_reason"] = "STEP_RELOAD_FAIL"
            dump_json(part_dir / "qa" / "status.json", row)
            render_part(part_dir, load_mesh(source_obj), load_mesh(cad_stl) if cad_stl.exists() else None, row["failure_reason"])
            return row
        if not row["brep_valid"]:
            row["failure_reason"] = "INVALID_BREP"
        cad_native_ops = bool(row.get("has_cad_native_ops"))
        row["cad_native"] = bool(cad_native_ops and row["step_reload_success"] and not row["faceted_brep"])
        if row["faceted_brep"] and not cad_native_ops:
            row["failure_reason"] = "FACETED_ONLY"
        cad_mesh = None
        for cand in [part_dir / "cad" / "generated.stl", part_dir / "cad" / "generated_from_program.stl", cad_stl]:
            if cand.exists() and cand.stat().st_size > 0:
                cad_mesh = load_mesh(cand)
                break
        source_mesh = load_mesh(source_obj)
        if cad_mesh is not None:
            cad_mesh = unnormalize_cadfit_mesh(cad_mesh, source_mesh)
            try:
                cad_mesh.export(part_dir / "cad" / "generated_unnormalized.stl")
            except Exception:
                pass
            qa = geometry_qa(source_mesh, cad_mesh)
            row.update(qa)
            dump_json(part_dir / "qa" / "metrics.json", qa)
            qa_pass = bool(
                row["cad_native"]
                and row["brep_valid"]
                and qa["chamfer_normalized"] <= QA_CHAMFER_DIAG
                and qa["hausdorff_normalized"] <= QA_HAUSDORFF_DIAG
                and qa["coverage"] >= QA_COVERAGE_MIN
                and qa["fp_occupancy"] <= QA_FP_MAX
            )
            row["qa_pass"] = qa_pass
            if row["cad_native"] and not qa_pass and not row["failure_reason"]:
                row["failure_reason"] = "GEOMETRY_QA_FAIL"
        else:
            row["qa_pass"] = False
        row["cadfit_success"] = bool(row["cad_program_generated"] and row["step_generated"] and row["step_reload_success"])
        if row.get("qa_pass"):
            row["failure_reason"] = None
        render_part(part_dir, source_mesh, cad_mesh, "CAD_NATIVE" if row["cad_native"] else (row["failure_reason"] or "DONE"))
        dump_json(part_dir / "qa" / "status.json", row)
        return row
    except Exception as e:
        row["failure_reason"] = "UNKNOWN"
        row["error"] = f"{type(e).__name__}:{e}"
        row["traceback"] = traceback.format_exc()[-2500:]
        dump_json(part_dir / "qa" / "status.json", row)
        try:
            render_part(part_dir, load_mesh(source_obj), None, "UNKNOWN")
        except Exception:
            pass
        return row


def contact_sheet(rows: list[dict]) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font = ImageFont.truetype(str(font_path), 14) if font_path.is_file() else ImageFont.load_default()
    cell_w, cell_h = 220, 200
    header_h = 28
    n = len(rows)
    canvas = Image.new("RGB", (cell_w * 4 + 20, header_h + n * (cell_h + 24) + 20), "white")
    draw = ImageDraw.Draw(canvas)
    labels = ["P3 Part", "CADFit CAD", "Overlay", "Status"]
    for i, lab in enumerate(labels):
        draw.text((12 + i * cell_w, 6), lab, fill="#111", font=font)
    for ridx, row in enumerate(rows):
        y = header_h + ridx * (cell_h + 24)
        qa = OUT / "parts" / row["part_id"] / "qa"
        images = [qa / "source_p3.png", qa / "cadfit_cad.png", qa / "overlay.png"]
        for c, img_path in enumerate(images):
            box = (10 + c * cell_w, y + 18)
            if img_path.is_file():
                im = Image.open(img_path).convert("RGB")
                im.thumbnail((cell_w - 8, cell_h - 8))
                canvas.paste(im, box)
            else:
                draw.rectangle([box[0], box[1], box[0] + cell_w - 12, box[1] + cell_h - 12], outline="#ccc", fill="#f4f4f4")
        status = "CAD_NATIVE" if row.get("cad_native") else (row.get("failure_reason") or ("OK" if row.get("cadfit_success") else "NO_RUN"))
        draw.text((10 + 3 * cell_w, y + 24), f"{row['part_id']}", fill="#111", font=font)
        draw.text((10 + 3 * cell_w, y + 48), status[:32], fill="#b33" if not row.get("cad_native") else "#185", font=font)
        extra = []
        if row.get("chamfer") is not None:
            extra.append(f"ch={row['chamfer']:.4g}")
        if row.get("coverage") is not None:
            extra.append(f"cov={row['coverage']:.3f}")
        if row.get("final_iou") is not None:
            extra.append(f"iou={row['final_iou']:.3f}")
        draw.text((10 + 3 * cell_w, y + 72), " ".join(extra)[:40], fill="#333", font=font)
        draw.text((10, y), row["part_id"], fill="#333", font=font)
    out = OUT / "artifacts" / "tank_p3_vs_cadfit_contact_sheet.png"
    canvas.save(out)
    return out


def prepare() -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    for d in ["scripts", "inputs/frozen_p3_parts", "inputs/cadfit_stl", "inputs/cadfit_repaired", "parts", "artifacts", "logs"]:
        (OUT / d).mkdir(parents=True, exist_ok=True)
    log("snapshot frozen P3 source")
    pre = {
        "source_tank_obj": file_meta(SOURCE_TANK_OBJ),
        "p3_tree": snapshot_tree(P3_SOURCE),
        "cadfit_repo_listing_start": sorted(p.name for p in CADFIT_REPO.iterdir()),
        "timestamp": utc_now(),
    }
    dump_json(OUT / "artifacts" / "source_snapshot_pre.json", pre)
    parts = sorted(P3_SOURCE.glob("part_*.obj"))
    copied = []
    inventory = []
    for src in parts:
        dst = OUT / "inputs" / "frozen_p3_parts" / src.name
        shutil.copy2(src, dst)
        src_hash = sha256_file(src)
        dst_hash = sha256_file(dst)
        if src_hash != dst_hash:
            raise RuntimeError(f"SHA256 mismatch after copy: {src}")
        mesh = load_mesh(src)
        rec = {
            **file_meta(src),
            "part_id": src.stem,
            "copied_path": str(dst),
            "copied_sha256": dst_hash,
            "sha256_match": True,
            "triangle_count": int(len(mesh.faces)),
            "vertex_count": int(len(mesh.vertices)),
        }
        inventory.append(rec)
        copied.append(src)
    write_csv(
        OUT / "artifacts" / "p3_component_inventory.csv",
        inventory,
        ["part_id", "path", "copied_path", "size_bytes", "mtime_unix", "sha256", "copied_sha256", "sha256_match", "triangle_count", "vertex_count"],
    )
    provenance = {
        "source_tank_obj": str(SOURCE_TANK_OBJ),
        "p3_source_directory": str(P3_SOURCE),
        "segment_manifest": str(P3_SOURCE / "part_metadata.json"),
        "triangle_assignment": str(P3_SOURCE / "triangle_part_id.npy"),
        "component_count": len(parts),
        "component_files": [str(p) for p in parts],
        "p3_reexecuted": False,
        "source_files_modified": False,
        "source_tank_sha256": pre["source_tank_obj"]["sha256"],
        "note": "Frozen P3 reused from tank_p3_rerun_v1/p3_max_367k_4000, already referenced by later tank fullstack experiments.",
    }
    dump_json(OUT / "artifacts" / "p3_provenance.json", provenance)
    audits = []
    specs = []
    for rec in inventory:
        part_id = rec["part_id"]
        copied_obj = Path(rec["copied_path"])
        audit = mesh_audit(copied_obj)
        audit["part_id"] = part_id
        audits.append(audit)
        classify = classify_and_maybe_repair(part_id, copied_obj, audit)
        stl_src = copied_obj
        if classify["repaired"] and classify["repair_path"]:
            stl_src = Path(classify["repair_path"])
        stl_path = OUT / "inputs" / "cadfit_stl" / f"{part_id}.stl"
        export_stl(stl_src, stl_path)
        specs.append(
            {
                "part_id": part_id,
                "copied_obj": str(copied_obj),
                "audit": audit,
                "classify": classify,
                "cadfit_stl": str(stl_path),
            }
        )
        dump_json(OUT / "parts" / part_id / "prepare.json", specs[-1])
    write_csv(
        OUT / "artifacts" / "part_mesh_audit.csv",
        audits,
        [
            "part_id",
            "path",
            "vertex_count",
            "triangle_count",
            "connected_components",
            "is_watertight",
            "is_manifold",
            "boundary_edge_count",
            "nonmanifold_edge_count",
            "bbox_x",
            "bbox_y",
            "bbox_z",
            "surface_area",
            "volume_if_available",
        ],
    )
    dump_json(OUT / "artifacts" / "prepare_specs.json", specs)
    runtime = cadfit_runtime_info()
    dump_json(OUT / "artifacts" / "cadfit_runtime.json", runtime)
    log(f"prepared {len(specs)} parts; REAL_CADFIT={runtime['REAL_CADFIT']} commit={runtime['commit']}")
    return specs


def summarize(rows: list[dict], specs: list[dict]) -> dict:
    pre = json.loads((OUT / "artifacts" / "source_snapshot_pre.json").read_text(encoding="utf-8"))
    post_p3 = snapshot_tree(P3_SOURCE)
    post_obj = file_meta(SOURCE_TANK_OBJ)
    modified = 0
    deleted = 0
    renamed = 0
    pre_files = pre["p3_tree"]["files"]
    post_files = post_p3["files"]
    for path, meta in pre_files.items():
        if path not in post_files:
            deleted += 1
            continue
        cur = post_files[path]
        if cur["sha256"] != meta["sha256"] or cur["size_bytes"] != meta["size_bytes"]:
            modified += 1
        elif abs(cur["mtime_unix"] - meta["mtime_unix"]) > 1e-6 and cur["sha256"] == meta["sha256"]:
            # mtime-only change still counts as modified per byte-level intent if content same we allow 0
            pass
    extra = [p for p in post_files if p not in pre_files]
    renamed = len(extra)
    if post_obj["sha256"] != pre["source_tank_obj"]["sha256"]:
        modified += 1
    by = {r["part_id"]: r for r in rows}
    cls = {s["part_id"]: s["classify"] for s in specs}
    n = len(specs)
    watertight = sum(1 for s in specs if s["audit"]["is_watertight"])
    repaired = sum(1 for s in specs if s["classify"]["repaired"])
    attempted = sum(1 for r in rows if r.get("cadfit_attempted"))
    prog = sum(1 for r in rows if r.get("cad_program_generated"))
    step = sum(1 for r in rows if r.get("step_generated"))
    reload_ok = sum(1 for r in rows if r.get("step_reload_success"))
    brep = sum(1 for r in rows if r.get("brep_valid"))
    native = sum(1 for r in rows if r.get("cad_native"))
    faceted = sum(1 for r in rows if r.get("faceted_brep"))
    qa_pass = sum(1 for r in rows if r.get("qa_pass"))
    eligible = sum(1 for s in specs if s["classify"]["cadfit_eligible"])
    native_rate = native / n if n else 0.0
    qa_rate = qa_pass / n if n else 0.0
    scored = [r for r in rows if r.get("chamfer") is not None and np.isfinite(r.get("chamfer"))]
    if scored:
        best = min(scored, key=lambda r: (not bool(r.get("cad_native")), float(r["chamfer"]), -float(r.get("coverage") or 0)))
    else:
        best = None
    gate = "TANK_FROZEN_P3_TO_CADFIT_V1_COMPLETE"
    blockers = []
    if modified or deleted:
        gate = "FAIL_SOURCE_MODIFIED"
        blockers.append("P3_SOURCE_FILES_CHANGED")
    if not (OUT / "artifacts" / "cadfit_runtime.json").exists():
        blockers.append("NO_CADFIT_RUNTIME")
        gate = "FAIL_NO_CADFIT_RUNTIME"
    summary = {
        "FINAL_GATE": gate,
        "SOURCE_TANK_OBJ": str(SOURCE_TANK_OBJ),
        "FROZEN_P3_SOURCE": str(P3_SOURCE),
        "P3_REEXECUTED": False,
        "P3_SOURCE_FILES_MODIFIED": modified,
        "P3_SOURCE_FILES_DELETED": deleted,
        "P3_SOURCE_FILES_RENAMED": renamed,
        "P3_PARTS_TOTAL": n,
        "WATERTIGHT_PARTS": watertight,
        "NON_WATERTIGHT_PARTS": n - watertight,
        "REPAIRED_PARTS": repaired,
        "REAL_CADFIT": True,
        "CADFIT_REPO": str(CADFIT_REPO),
        "CADFIT_COMMIT": json.loads((OUT / "artifacts" / "cadfit_runtime.json").read_text())["commit"],
        "CADFIT_ELIGIBLE_PARTS": eligible,
        "CADFIT_ATTEMPTED": attempted,
        "CADFIT_PROGRAM_SUCCESS": prog,
        "CADFIT_STEP_SUCCESS": step,
        "CADFIT_STEP_RELOAD_SUCCESS": reload_ok,
        "CADFIT_BREP_VALID": brep,
        "CAD_NATIVE_PARTS": native,
        "FACETED_BREP_PARTS": faceted,
        "QA_PASS_PARTS": qa_pass,
        "CAD_NATIVE_RATE": native_rate,
        "QA_PASS_RATE": qa_rate,
        "BEST_PART": None if best is None else best["part_id"],
        "BEST_PART_CHAMFER": None if best is None else best.get("chamfer"),
        "BEST_PART_HAUSDORFF": None if best is None else best.get("hausdorff"),
        "BEST_PART_COVERAGE": None if best is None else best.get("coverage"),
        "BEST_PART_FP_OCCUPANCY": None if best is None else best.get("fp_occupancy"),
        "OUTPUT_ROOT": str(OUT),
        "SUMMARY_CSV": str(OUT / "artifacts" / "summary.csv"),
        "CONTACT_SHEET": str(OUT / "artifacts" / "tank_p3_vs_cadfit_contact_sheet.png"),
        "REPORT": str(OUT / "report.md"),
        "BLOCKERS": blockers,
        "watertight_class_counts": {
            "A": sum(1 for s in specs if s["classify"]["watertight_class"] == "A"),
            "B": sum(1 for s in specs if s["classify"]["watertight_class"] == "B"),
            "C": sum(1 for s in specs if s["classify"]["watertight_class"] == "C"),
        },
        "failure_reason_counts": {},
    }
    from collections import Counter

    summary["failure_reason_counts"] = dict(Counter(r.get("failure_reason") or "NONE" for r in rows))
    dump_json(OUT / "artifacts" / "source_snapshot_post.json", {"p3_tree": post_p3, "source_tank_obj": post_obj})
    return summary


def write_report(summary: dict, rows: list[dict], specs: list[dict]) -> None:
    lines = [
        f"# {EXPERIMENT}",
        "",
        f"FINAL_GATE=`{summary['FINAL_GATE']}`",
        "",
        "This experiment reuses the frozen tank P3 segmentation and sends each component mesh to the real CADFit pipeline. No existing experiment files were rewritten. P3, PhysX, MAC, SuperFit, and Point2CAD were not re-run.",
        "",
        "## Provenance",
        "",
        f"- SOURCE_TANK_OBJ: `{summary['SOURCE_TANK_OBJ']}`",
        f"- FROZEN_P3_SOURCE: `{summary['FROZEN_P3_SOURCE']}`",
        f"- P3_REEXECUTED: `{summary['P3_REEXECUTED']}`",
        f"- P3_SOURCE_FILES_MODIFIED: `{summary['P3_SOURCE_FILES_MODIFIED']}`",
        f"- CADFit repo: `{summary['CADFIT_REPO']}`",
        f"- CADFit commit: `{summary['CADFIT_COMMIT']}`",
        "",
        "## Totals",
        "",
        f"- P3_PARTS_TOTAL: {summary['P3_PARTS_TOTAL']}",
        f"- WATERTIGHT_PARTS: {summary['WATERTIGHT_PARTS']}",
        f"- NON_WATERTIGHT_PARTS: {summary['NON_WATERTIGHT_PARTS']}",
        f"- REPAIRED_PARTS: {summary['REPAIRED_PARTS']}",
        f"- watertight class A/B/C: {summary['watertight_class_counts']}",
        f"- CADFIT_ATTEMPTED: {summary['CADFIT_ATTEMPTED']}",
        f"- CADFIT_PROGRAM_SUCCESS: {summary['CADFIT_PROGRAM_SUCCESS']}",
        f"- CADFIT_STEP_SUCCESS: {summary['CADFIT_STEP_SUCCESS']}",
        f"- CAD_NATIVE_PARTS: {summary['CAD_NATIVE_PARTS']}",
        f"- FACETED_BREP_PARTS: {summary['FACETED_BREP_PARTS']}",
        f"- QA_PASS_PARTS: {summary['QA_PASS_PARTS']}",
        f"- CAD_NATIVE_RATE: {summary['CAD_NATIVE_RATE']:.6f}",
        f"- QA_PASS_RATE: {summary['QA_PASS_RATE']:.6f}",
        "",
        "## Method notes",
        "",
        "- OBJ→STL conversion is a direct triangle dump. No remesh, voxelization, smoothing, or simplification is applied in this experiment.",
        "- Class B repair is `trimesh.repair.fill_holes` only, and only when the close is trivial. Class C parts are not aggressively rebuilt; they are still sent to CADFit because the real CADFit pipeline accepts open meshes and internally alpha-wraps them for IoU.",
        "- CAD-native requires an executable CadQuery construction program plus analytic (non-faceted) BRep after OpenCascade reload.",
        "",
        "## Per-part",
        "",
        "| part | tris | class | attempted | program | step | native | faceted | chamfer | coverage | fail |",
        "|---|---:|---|---|---|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {part_id} | {triangle_count} | {watertight_class} | {cadfit_attempted} | {cad_program_generated} | {step_generated} | {cad_native} | {faceted_brep} | {chamfer} | {coverage} | {failure_reason} |".format(
                part_id=row["part_id"],
                triangle_count=row.get("triangle_count"),
                watertight_class=row.get("watertight_class"),
                cadfit_attempted=row.get("cadfit_attempted"),
                cad_program_generated=row.get("cad_program_generated"),
                step_generated=row.get("step_generated"),
                cad_native=row.get("cad_native"),
                faceted_brep=row.get("faceted_brep"),
                chamfer=("" if row.get("chamfer") is None else f"{row['chamfer']:.6g}"),
                coverage=("" if row.get("coverage") is None else f"{row['coverage']:.4f}"),
                failure_reason=row.get("failure_reason") or "",
            )
        )
    lines += [
        "",
        "## Failure counts",
        "",
        json.dumps(summary["failure_reason_counts"], indent=2),
        "",
        f"BEST_PART={summary['BEST_PART']}",
        "",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_gate(summary: dict) -> None:
    keys = [
        "FINAL_GATE",
        "SOURCE_TANK_OBJ",
        "FROZEN_P3_SOURCE",
        "P3_REEXECUTED",
        "P3_SOURCE_FILES_MODIFIED",
        "P3_PARTS_TOTAL",
        "WATERTIGHT_PARTS",
        "NON_WATERTIGHT_PARTS",
        "REPAIRED_PARTS",
        "REAL_CADFIT",
        "CADFIT_REPO",
        "CADFIT_COMMIT",
        "CADFIT_ELIGIBLE_PARTS",
        "CADFIT_ATTEMPTED",
        "CADFIT_PROGRAM_SUCCESS",
        "CADFIT_STEP_SUCCESS",
        "CADFIT_STEP_RELOAD_SUCCESS",
        "CADFIT_BREP_VALID",
        "CAD_NATIVE_PARTS",
        "FACETED_BREP_PARTS",
        "QA_PASS_PARTS",
        "CAD_NATIVE_RATE",
        "QA_PASS_RATE",
        "BEST_PART",
        "BEST_PART_CHAMFER",
        "BEST_PART_HAUSDORFF",
        "BEST_PART_COVERAGE",
        "BEST_PART_FP_OCCUPANCY",
        "OUTPUT_ROOT",
        "SUMMARY_CSV",
        "CONTACT_SHEET",
        "REPORT",
        "BLOCKERS",
    ]
    print("\n" + "=" * 72)
    last_blank_before = {
        "P3_PARTS_TOTAL",
        "REAL_CADFIT",
        "CADFIT_ELIGIBLE_PARTS",
        "CAD_NATIVE_PARTS",
        "BEST_PART",
        "OUTPUT_ROOT",
    }
    for k in keys:
        if k in last_blank_before:
            print()
        print(f"{k}={summary.get(k)}")
    print("=" * 72, flush=True)


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in {"prepare", "all"}:
        specs = prepare()
    else:
        specs = json.loads((OUT / "artifacts" / "prepare_specs.json").read_text(encoding="utf-8"))
    if stage == "prepare":
        return 0
    rows = []
    log(f"running CADFit on {len(specs)} parts parallel={CADFIT_PARALLEL} timeout={CADFIT_TIMEOUT}s")
    with ThreadPoolExecutor(max_workers=max(1, CADFIT_PARALLEL)) as pool:
        futs = {pool.submit(process_part, spec): spec["part_id"] for spec in specs}
        for fut in as_completed(futs):
            part_id = futs[fut]
            try:
                row = fut.result()
            except Exception as e:
                row = {"part_id": part_id, "failure_reason": "UNKNOWN", "error": repr(e), "cadfit_attempted": True}
            rows.append(row)
            log(f"done {part_id} native={row.get('cad_native')} fail={row.get('failure_reason')} runtime={row.get('runtime')}")
    rows.sort(key=lambda r: r["part_id"])
    fields = [
        "part_id",
        "triangle_count",
        "watertight",
        "watertight_class",
        "cadfit_attempted",
        "cadfit_success",
        "cad_program_generated",
        "cad_program_length",
        "step_generated",
        "step_reload_success",
        "brep_valid",
        "cad_native",
        "faceted_brep",
        "chamfer",
        "hausdorff",
        "coverage",
        "fp_occupancy",
        "runtime",
        "failure_reason",
        "final_iou",
    ]
    write_csv(OUT / "artifacts" / "summary.csv", rows, fields)
    dump_json(OUT / "artifacts" / "summary.json", {"parts": rows})
    try:
        contact_sheet(rows)
    except Exception as e:
        log(f"contact sheet failed: {e}")
    summary = summarize(rows, specs)
    dump_json(OUT / "artifacts" / "summary.json", {"parts": rows, "summary": summary})
    write_report(summary, rows, specs)
    print_gate(summary)
    return 0 if summary["FINAL_GATE"].endswith("COMPLETE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
