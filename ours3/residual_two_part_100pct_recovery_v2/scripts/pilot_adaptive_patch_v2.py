#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = OURS3 / "full_object_cad_recovery_v1"
ROOT = OURS3 / "residual_two_part_100pct_recovery_v2"
GRAPH = OURS3 / "cad_part_graph_gate1"
HF_PATH = OURS3 / "high_fidelity_part_recovery_v2/scripts/pipeline.py"
TARGETS = ("CADPART_008", "CADPART_010")
CONFIGS = (
    {"name": "adaptive_006_m60", "relative_residual": 0.006, "min_faces": 60, "max_patches": 96},
    {"name": "adaptive_004_m50", "relative_residual": 0.004, "min_faces": 50, "max_patches": 128},
    {"name": "adaptive_003_m40", "relative_residual": 0.003, "min_faces": 40, "max_patches": 144},
    {"name": "adaptive_002_m30", "relative_residual": 0.002, "min_faces": 30, "max_patches": 160},
)


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def hfmod():
    spec = importlib.util.spec_from_file_location("hf", HF_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SAMPLE = 16000
    return module


def plane_stats(mesh, face_ids):
    vertices = np.asarray(mesh.vertices)[np.unique(np.asarray(mesh.faces)[face_ids])]
    origin = vertices.mean(axis=0)
    _, _, vh = np.linalg.svd(vertices - origin, full_matrices=False)
    normal = vh[-1]
    residuals = np.abs((vertices - origin) @ normal)
    return vertices, origin, normal, float(np.quantile(residuals, 0.95))


def recursive_partition(mesh, cfg):
    diag = float(np.linalg.norm(mesh.extents))
    groups = [np.arange(len(mesh.faces), dtype=int)]
    while len(groups) < cfg["max_patches"]:
        scored = []
        for index, ids in enumerate(groups):
            if len(ids) < 2 * cfg["min_faces"]:
                continue
            _, _, _, residual = plane_stats(mesh, ids)
            if residual > diag * cfg["relative_residual"]:
                scored.append((residual, index))
        if not scored:
            break
        _, index = max(scored)
        ids = groups[index]
        centers = np.asarray(mesh.triangles_center)[ids]
        centered = centers - centers.mean(axis=0)
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
        projection = centered @ vh[0]
        order = np.argsort(projection, kind="mergesort")
        cut = len(order) // 2
        left = ids[order[:cut]]
        right = ids[order[cut:]]
        if len(left) < cfg["min_faces"] or len(right) < cfg["min_faces"]:
            break
        groups[index:index + 1] = [left, right]
    return groups


def make_plane_face(mesh, face_ids):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Dir, gp_Pln, gp_Pnt

    vertices, origin, normal, residual = plane_stats(mesh, face_ids)
    reference = np.array([1.0, 0.0, 0.0]) if abs(normal[0]) < 0.8 else np.array([0.0, 1.0, 0.0])
    u_axis = np.cross(normal, reference)
    u_axis /= np.linalg.norm(u_axis)
    v_axis = np.cross(normal, u_axis)
    uv = np.column_stack(((vertices - origin) @ u_axis, (vertices - origin) @ v_axis))
    hull = ConvexHull(uv)
    polygon = uv[hull.vertices]
    maker = BRepBuilderAPI_MakePolygon()
    first = None
    for u, v in polygon:
        point = origin + u * u_axis + v * v_axis
        pnt = gp_Pnt(*map(float, point))
        maker.Add(pnt)
        if first is None:
            first = pnt
    maker.Add(first)
    maker.Close()
    face = BRepBuilderAPI_MakeFace(
        gp_Pln(gp_Pnt(*map(float, origin)), gp_Dir(*map(float, normal))),
        maker.Wire(),
        True,
    ).Face()
    return face, residual


def write_compound(path, faces):
    from OCP.BRep import BRep_Builder
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.TopoDS import TopoDS_Compound

    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for face in faces:
        builder.Add(compound, face)
    if compound.IsNull() or not BRepCheck_Analyzer(compound).IsValid():
        raise RuntimeError("invalid analytic surface compound")
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError("STEP write failed")


def s1(metrics):
    return bool(
        metrics.get("brep_valid")
        and metrics.get("symmetric_chamfer_normalized", 99) <= 0.03
        and metrics.get("p95_symmetric", 99) <= 0.07
        and metrics.get("coverage_02", 0) >= 0.80
    )


def main():
    hf = hfmod()
    summary = {"targets": {}, "candidate_configuration_limit": 12}
    for cid in TARGETS:
        source = GRAPH / "cases" / cid / f"{cid}_global.obj"
        mesh = trimesh.load(source, force="mesh", process=False)
        target_results = []
        for cfg in CONFIGS:
            out = ROOT / "metrics" / "adaptive_analytic_patch_v2" / cid / cfg["name"]
            out.mkdir(parents=True, exist_ok=True)
            dump(out / "transform.json", {"CANONICAL_TO_SOURCE": np.eye(4).tolist()})
            groups = recursive_partition(mesh, cfg)
            faces = []
            patch_records = []
            for patch_id, ids in enumerate(groups):
                face, residual = make_plane_face(mesh, ids)
                faces.append(face)
                patch_records.append({
                    "patch_id": patch_id,
                    "source_triangle_count": int(len(ids)),
                    "source_triangle_ids_local": ids.tolist(),
                    "source_area": float(mesh.area_faces[ids].sum()),
                    "plane_p95_residual": residual,
                    "analytic_surface_type": "PLANE",
                })
            write_compound(out / "candidate.step", faces)
            metadata = {
                "backend": "ANALYTIC_SURFACE_BREP_ADAPTIVE_PATCH_V2",
                "configuration": cfg,
                "expected_topology_type": "COMPOUND",
                "patch_count": len(groups),
                "source_triangle_count": len(mesh.faces),
                "assigned_source_triangle_count": sum(len(x) for x in groups),
                "unique_source_triangle_count": len(set(np.concatenate(groups).tolist())),
                "faceted_triangle_brep": False,
                "minimum_source_triangles_per_patch": min(len(x) for x in groups),
                "surface_shift_applied": False,
                "patches": patch_records,
            }
            dump(out / "surface_patch_segmentation.json", metadata)
            candidate = {
                "candidate_id": cfg["name"],
                "backend": "ANALYTIC_SURFACE_BREP_ADAPTIVE_PATCH_V2",
                "directory": str(out),
            }
            metrics = hf.qa_candidate(
                {"source_obj": str(source), "transform": str(out / "transform.json")},
                candidate,
            )
            metrics["surface_brep_s1"] = s1(metrics)
            dump(out / "metrics.json", metrics)
            target_results.append({"configuration": cfg, "patch_count": len(groups), "metrics": metrics})
            print(
                cid,
                cfg["name"],
                len(groups),
                metrics.get("symmetric_chamfer_normalized"),
                metrics.get("p95_symmetric"),
                metrics.get("coverage_02"),
                metrics["surface_brep_s1"],
                flush=True,
            )
        summary["targets"][cid] = target_results
        dump(ROOT / "metrics" / "adaptive_analytic_patch_v2" / "pilot_summary.json", summary)


if __name__ == "__main__":
    main()
