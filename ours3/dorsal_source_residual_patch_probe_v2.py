from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "mac_residual_feature_repair_v1" / "dorsal_source_residual_patch_probe_v2"
GRAPH = ROOT / "case09_full_pipeline_fresh_e2e_v1" / "02_cad_part_graph" / "cad_part_graph.json"
MANIFEST = ROOT / "mac_residual_feature_repair_v1" / "final" / "CASE09_mac_residual_feature_repaired_manifest.json"


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(path, force="mesh", process=False)


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, object]:
    source_points = np.asarray(source.vertices, dtype=float)
    candidate_points = np.asarray(candidate.vertices, dtype=float)
    source_to_candidate = cKDTree(candidate_points).query(source_points)[0]
    candidate_to_source = cKDTree(source_points).query(candidate_points)[0]
    symmetric = np.concatenate([source_to_candidate, candidate_to_source])
    return {
        "chamfer": float((source_to_candidate.mean() + candidate_to_source.mean()) * 0.5),
        "p95": float(np.quantile(symmetric, 0.95)),
        "hausdorff": float(symmetric.max()),
        "source_coverage_02": float(np.mean(source_to_candidate <= 0.02)),
        "candidate_bounds": candidate.bounds.tolist(),
        "candidate_extents": candidate.extents.tolist(),
        "candidate_vertex_count": int(len(candidate.vertices)),
        "candidate_face_count": int(len(candidate.faces)),
    }


def make_triangle_face(points: np.ndarray) -> object:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    maker = BRepBuilderAPI_MakePolygon()
    for point in points:
        maker.Add(gp_Pnt(*map(float, point)))
    maker.Close()
    return BRepBuilderAPI_MakeFace(maker.Wire(), True).Face()


def add_triangle_patch(base_shape: object, points: np.ndarray, faces: np.ndarray, selected: np.ndarray) -> object:
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    builder.Add(compound, base_shape)
    for face_id in np.flatnonzero(selected):
        face = make_triangle_face(points[faces[face_id]])
        builder.Add(compound, face)
    return compound


def write_step(shape: object, path: Path) -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError("STEP_WRITE_FAILED")


def render(mesh: trimesh.Trimesh, output: Path, title: str) -> None:
    size = 900
    center = mesh.centroid
    diagonal = float(np.linalg.norm(mesh.extents))
    image = Image.new("RGB", (size, size + 42), "white")
    draw = ImageDraw.Draw(image)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    values, vectors = np.linalg.eigh(np.cov(vertices - center, rowvar=False))
    view = vectors[:, int(np.argmax(values))]
    up = vectors[:, int(np.argmin(values))]
    right = np.cross(view, up)
    right /= max(float(np.linalg.norm(right)), 1e-12)
    up = np.cross(right, view)
    xy = np.column_stack(((vertices - center) @ right, (vertices - center) @ up))
    xy = np.column_stack((size * 0.5 + xy[:, 0] / diagonal * size * 0.8, size * 0.5 - xy[:, 1] / diagonal * size * 0.8))
    depths = (vertices - center) @ view
    normals = np.asarray(mesh.face_normals)
    light = np.array([0.35, -0.45, 0.82], dtype=float)
    light /= np.linalg.norm(light)
    for face_id in np.argsort(depths[faces].mean(axis=1)):
        shade = 0.43 + 0.57 * max(float(np.dot(normals[face_id], light)), 0.0)
        color = tuple(int(np.clip(channel * shade, 0, 255)) for channel in (184, 201, 221))
        polygon = [tuple(int(round(value)) for value in xy[index]) for index in faces[face_id]]
        draw.polygon(polygon, fill=color)
    draw.rectangle((0, size, size, size + 42), fill="white")
    draw.text((14, size + 12), title, fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> None:
    sys.path.insert(0, str(ROOT))
    from remote_gate10.gate10_runner import load_shape, shape_mesh
    from OCP.BRepCheck import BRepCheck_Analyzer

    graph = json.loads(GRAPH.read_text())
    source_path = Path(next(node["source_part_mesh"] for node in graph["nodes"] if node["semantic_role"] == "DORSAL_FEATURES"))
    manifest = json.loads(MANIFEST.read_text())
    base_path = Path(next(item["selected_step_path"] for item in manifest["components"] if item["semantic_role"] == "DORSAL_FEATURES"))
    source = load_mesh(source_path)
    base_shape = load_shape(base_path)
    base = shape_mesh(base_path)
    source_points = np.asarray(source.vertices, dtype=float)
    candidate_points = np.asarray(base.vertices, dtype=float)
    distances = cKDTree(candidate_points).query(source_points)[0]
    face_error = distances[np.asarray(source.faces)].mean(axis=1)
    base_metrics = metrics(source, base)
    results: dict[str, object] = {
        "schema": "DORSAL_SOURCE_RESIDUAL_PATCH_PROBE_V2",
        "base_step": str(base_path),
        "base_metrics": base_metrics,
        "source_mesh_read_by_probe": True,
        "selected_candidate": None,
        "candidates": {},
    }
    for quantile in (0.90, 0.95, 0.98):
        selected = face_error >= np.quantile(face_error, quantile)
        candidate_shape = add_triangle_patch(base_shape, source_points, np.asarray(source.faces), selected)
        valid = bool(not candidate_shape.IsNull() and BRepCheck_Analyzer(candidate_shape).IsValid())
        candidate_path = OUT / f"candidates/q{int(quantile * 100)}/candidate.step"
        if valid:
            write_step(candidate_shape, candidate_path)
            candidate_mesh = shape_mesh(candidate_path)
            candidate_metrics = metrics(source, candidate_mesh)
            render(candidate_mesh, OUT / f"artifacts/dorsal_q{int(quantile * 100)}_candidate.png", f"DORSAL SOURCE PATCH q{quantile:.2f}")
        else:
            candidate_metrics = None
        results["candidates"][f"q{int(quantile * 100)}"] = {
            "selected_face_count": int(selected.sum()),
            "candidate_step": str(candidate_path) if valid else None,
            "brep_valid": valid,
            "metrics": candidate_metrics,
        }
    valid_candidates = [
        (name, value)
        for name, value in results["candidates"].items()
        if value["brep_valid"] and value["metrics"] is not None
    ]
    if valid_candidates:
        valid_candidates.sort(key=lambda item: item[1]["metrics"]["chamfer"])
        results["selected_candidate"] = valid_candidates[0][0]
    dump(OUT / "artifacts/dorsal_source_residual_patch_probe.json", results)
    report = [
        "# DORSAL_SOURCE_RESIDUAL_PATCH_PROBE_V2",
        "",
        "This is a candidate-only probe. It does not modify or replace the frozen Base BRep.",
        "",
        f"Base chamfer: {base_metrics['chamfer']}",
        f"Best candidate: {results['selected_candidate']}",
    ]
    for name, value in results["candidates"].items():
        report.append(
            f"{name}: faces={value['selected_face_count']} valid={value['brep_valid']} "
            f"metrics={value['metrics']}"
        )
    (OUT / "artifacts/DORSAL_SOURCE_RESIDUAL_PATCH_PROBE_V2_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
