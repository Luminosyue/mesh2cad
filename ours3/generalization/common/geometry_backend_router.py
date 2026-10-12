from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import ConvexHull, cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V6_RUNTIME = ROOT / "case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py"
RESTORE = ROOT / "v6_geometry_backend_restore"


def classify_geometry(mesh: trimesh.Trimesh) -> dict[str, Any]:
    points = np.asarray(mesh.vertices, dtype=float)
    _, values, axes = np.linalg.svd(points - points.mean(axis=0), full_matrices=False)
    ratios = np.sort(np.maximum(values, 1e-12))[::-1]
    planar = float(ratios[2] / ratios[0])
    profile_constancy = float(1.0 - np.std(np.linalg.norm(points - points.mean(axis=0), axis=1)) / max(np.mean(np.linalg.norm(points - points.mean(axis=0), axis=1)), 1e-12))
    components = len(mesh.split(only_watertight=False))
    if planar < 0.06:
        geometry_class = "PLANAR"
    elif planar < 0.16 and profile_constancy > 0.55:
        geometry_class = "PRISMATIC"
    elif profile_constancy > 0.78 and ratios[1] / ratios[0] < 0.45:
        geometry_class = "REVOLUTIONAL"
    elif planar < 0.22 and ratios[1] / ratios[0] > 0.42:
        geometry_class = "PROFILE_EXTRUSION"
    elif components > 1:
        geometry_class = "MIXED"
    elif profile_constancy > 0.62:
        geometry_class = "LOFTABLE"
    else:
        geometry_class = "FREEFORM"
    return {
        "geometry_class": geometry_class,
        "planarity": planar,
        "principal_extent_ratios": (ratios / ratios[0]).tolist(),
        "profile_constancy": profile_constancy,
        "components": components,
        "analytic_eligible": geometry_class in {"PLANAR", "PRISMATIC", "PROFILE_EXTRUSION", "REVOLUTIONAL"},
        "v6_eligible": True,
    }


def _runtime():
    spec = importlib.util.spec_from_file_location("generic_v6_runtime", V6_RUNTIME)
    if spec is None or spec.loader is None:
        raise RuntimeError("V6_RUNTIME_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_step(shape: Any, path: Path) -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError("STEP_WRITE_FAILED")


def _analytic_prism(mesh: trimesh.Trimesh) -> Any:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Pnt, gp_Vec

    points = np.asarray(mesh.vertices, dtype=float)
    center = points.mean(axis=0)
    _, _, axes = np.linalg.svd(points - center, full_matrices=False)
    normal = axes[-1]
    if float(np.dot(normal, np.asarray(mesh.face_normals).mean(axis=0))) < 0:
        normal *= -1
    u, v = axes[0], axes[1]
    uv = np.column_stack(((points - center) @ u, (points - center) @ v))
    hull = ConvexHull(uv)
    low = float(np.min((points - center) @ normal))
    high = float(np.max((points - center) @ normal))
    polygon = BRepBuilderAPI_MakePolygon()
    first = None
    for x, y in uv[hull.vertices]:
        point = center + x * u + y * v + low * normal
        gp = gp_Pnt(*map(float, point))
        polygon.Add(gp)
        first = first or gp
    polygon.Add(first)
    polygon.Close()
    face = BRepBuilderAPI_MakeFace(polygon.Wire(), True).Face()
    vector = gp_Vec(*map(float, (high - low) * normal))
    return BRepPrimAPI_MakePrism(face, vector, True).Shape()


def build_analytic(mesh_path: Path, output: Path) -> dict[str, Any]:
    from OCP.BRepCheck import BRepCheck_Analyzer

    mesh = trimesh.load(mesh_path, force="mesh", process=False)
    shape = _analytic_prism(mesh)
    valid = bool(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())
    if valid:
        _write_step(shape, output)
    return {"valid": valid, "representation": "ANALYTIC_PRISM", "step": str(output) if valid else None}


def representation_for(geometry_class: str) -> str:
    return {
        "PLANAR": "PROFILE_EXTRUSION",
        "PRISMATIC": "PROFILE_EXTRUSION",
        "PROFILE_EXTRUSION": "GLOBAL_UPPER_LOWER_SKINS",
        "REVOLUTIONAL": "PERIODIC_GLOBAL_BSPLINE",
        "LOFTABLE": "GLOBAL_LOFT",
        "FREEFORM": "SEMANTIC_FREEFORM_SKINS",
        "MIXED": "HYBRID_ANALYTIC_FREEFORM",
        "REPEATED": "GLOBAL_LOFT",
        "UNKNOWN": "GLOBAL_LOFT",
    }.get(geometry_class, "GLOBAL_LOFT")


def build_v6(mesh_path: Path, output: Path, geometry_class: str) -> dict[str, Any]:
    runtime = _runtime()
    representation = representation_for(geometry_class)
    runtime.build_candidate(str(mesh_path), representation, str(output), 14, 12, 0.001)
    return {"valid": output.is_file(), "representation": representation, "step": str(output)}


def mesh_distance_metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, float]:
    source_points = np.asarray(source.vertices, dtype=float)
    candidate_points = np.asarray(candidate.vertices, dtype=float)
    a = cKDTree(candidate_points).query(source_points)[0]
    b = cKDTree(source_points).query(candidate_points)[0]
    values = np.concatenate([a, b])
    return {
        "chamfer": float((a.mean() + b.mean()) * 0.5),
        "hausdorff": float(values.max()),
        "source_coverage": float(np.mean(a <= 0.02)),
    }
