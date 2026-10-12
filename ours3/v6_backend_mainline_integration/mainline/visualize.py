from __future__ import annotations

from pathlib import Path
import sys
import importlib.util
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_fill_holes
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
sys.path.insert(0, str(ROOT / "v6_geometry_backend_restore"))


def shape_mesh(shape: Any) -> trimesh.Trimesh:
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    BRepMesh_IncrementalMesh(shape, 0.003, False, 0.30, True).Perform()
    vertices = []
    faces = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)
        if triangulation is not None:
            base = len(vertices)
            transform = location.Transformation()
            for index in range(1, triangulation.NbNodes() + 1):
                point = triangulation.Node(index).Transformed(transform)
                vertices.append([point.X(), point.Y(), point.Z()])
            for index in range(1, triangulation.NbTriangles() + 1):
                a, b, c = triangulation.Triangle(index).Get()
                faces.append([base + a - 1, base + b - 1, base + c - 1])
        explorer.Next()
    return trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(faces), process=False)


def step_mesh(path: str | Path) -> trimesh.Trimesh:
    from backends.v6_backend_safety_wrapper import reload_shape
    return shape_mesh(reload_shape(Path(path)))


def render_step_image(path: str | Path, edges: bool = False) -> Image.Image:
    restore_runner = ROOT / "v6_geometry_backend_restore/run_restore.py"
    spec = importlib.util.spec_from_file_location("v6_restore_render", restore_runner)
    if spec is None or spec.loader is None:
        raise RuntimeError("RESTORE_RENDER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_artifact(Path(path), edges).resize((295, 210))


def transformed_mesh(mesh: trimesh.Trimesh, matrix: list[list[float]]) -> trimesh.Trimesh:
    result = mesh.copy()
    result.apply_transform(np.asarray(matrix, float))
    return result


def combine(meshes: list[trimesh.Trimesh]) -> trimesh.Trimesh:
    return trimesh.util.concatenate([mesh for mesh in meshes if len(mesh.vertices)])


def _projection(points: np.ndarray, view: int) -> np.ndarray:
    if view == 0:
        return points[:, [0, 1]]
    if view == 1:
        return points[:, [0, 2]]
    if view == 2:
        return points[:, [1, 2]]
    direction = np.asarray([1.35, -1.55, 1.05], float)
    direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, direction); up /= np.linalg.norm(up)
    return np.column_stack((points @ right, points @ up))


def _mask(points: np.ndarray, source_points: np.ndarray, view: int) -> np.ndarray:
    projected_source = _projection(source_points, view)
    projected = _projection(points, view)
    low = projected_source.min(axis=0)
    high = projected_source.max(axis=0)
    scale = np.maximum(high - low, 1e-9)
    indices = ((projected - low) / scale * 383).astype(int).clip(0, 383)
    mask = np.zeros((384, 384), dtype=bool)
    mask[indices[:, 1], indices[:, 0]] = True
    return binary_fill_holes(binary_dilation(mask, iterations=3))


def fidelity(source: trimesh.Trimesh, candidate: trimesh.Trimesh, count: int = 16000) -> dict[str, Any]:
    source_points, _ = trimesh.sample.sample_surface(source, count, seed=310)
    candidate_points, _ = trimesh.sample.sample_surface(candidate, count, seed=311)
    source_to_cad = cKDTree(candidate_points).query(source_points)[0]
    cad_to_source = cKDTree(source_points).query(candidate_points)[0]
    ious = []
    for view in range(4):
        left = _mask(source_points, source_points, view)
        right = _mask(candidate_points, source_points, view)
        ious.append(float(np.logical_and(left, right).sum() / max(np.logical_or(left, right).sum(), 1)))
    return {
        "silhouette_iou_4view": float(np.mean(ious)),
        "silhouette_iou_views": ious,
        "chamfer": float((source_to_cad.mean() + cad_to_source.mean()) * 0.5),
        "hausdorff": float(max(source_to_cad.max(), cad_to_source.max())),
        "source_coverage_02": float(np.mean(source_to_cad <= 0.02)),
    }


def render_mesh(mesh: trimesh.Trimesh, size: tuple[int, int] = (300, 210), edges: bool = False) -> Image.Image:
    image = Image.new("RGB", size, "white")
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        return image
    vertices = np.asarray(mesh.vertices, float)
    faces = np.asarray(mesh.faces, int)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    diagonal = max(float(np.linalg.norm(vertices.max(axis=0) - vertices.min(axis=0))), 1e-9)
    direction = np.asarray([1.35, -1.55, 1.05]); direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, direction); up /= np.linalg.norm(up)
    projected = np.column_stack(((vertices - center) @ right, (vertices - center) @ up)) / diagonal
    xy = np.column_stack((size[0] * 0.5 + projected[:, 0] * size[0] * 0.82, size[1] * 0.5 - projected[:, 1] * size[1] * 0.82))
    depth = (vertices - center) @ direction
    draw = ImageDraw.Draw(image)
    for face_index in np.argsort(depth[faces].mean(axis=1)):
        polygon = [tuple(xy[int(index)]) for index in faces[face_index]]
        draw.polygon(polygon, fill=(215, 227, 238))
        if edges:
            draw.line(polygon + [polygon[0]], fill=(42, 63, 82), width=1)
    return image


def contact_sheet(rows: list[dict[str, Any]], output: Path, edges: bool = False) -> None:
    columns = ("SOURCE", "CURRENT", "V6_MAINLINE_FRESH", "HYBRID", "FINAL_SELECTED")
    cell = (305, 240)
    canvas = Image.new("RGB", (len(columns) * cell[0], len(rows) * cell[1] + 28), "white")
    draw = ImageDraw.Draw(canvas)
    for index, title in enumerate(columns):
        draw.text((index * cell[0] + 8, 7), title, fill="black")
    for row_index, row in enumerate(rows):
        y = 28 + row_index * cell[1]
        for column_index, key in enumerate(("source", "current", "v6", "hybrid", "selected")):
            path = row.get(key)
            if path:
                if str(path).lower().endswith(".obj"):
                    mesh = trimesh.load(path, force="mesh", process=False)
                    image = render_mesh(mesh, (295, 210), edges)
                else:
                    image = render_step_image(path, edges) if edges else render_mesh(step_mesh(path), (295, 210), False)
                canvas.paste(image, (column_index * cell[0] + 5, y + 18))
            else:
                draw.text((column_index * cell[0] + 120, y + 100), "N/A", fill=(120, 120, 120))
        draw.text((7, y + 3), f"{row['part_id']} {row['role']}", fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def whole_comparison(source: trimesh.Trimesh, current: trimesh.Trimesh, integrated: trimesh.Trimesh, output: Path, current_step: Path | None = None, integrated_step: Path | None = None) -> None:
    canvas = Image.new("RGB", (1200, 280), "white")
    draw = ImageDraw.Draw(canvas)
    for index, (title, mesh) in enumerate((("SOURCE", source), ("OLD CURRENT ASSEMBLY", current), ("V6-INTEGRATED PREVIEW", integrated), ("V6-INTEGRATED TRUE EDGES", integrated))):
        draw.text((index * 300 + 8, 8), title, fill="black")
        if index == 1 and current_step is not None:
            image = render_step_image(current_step, True)
        elif index == 3 and integrated_step is not None:
            image = render_step_image(integrated_step, True)
        else:
            image = render_mesh(mesh, (290, 240), False)
        canvas.paste(image.resize((290, 240)), (index * 300 + 5, 30))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
