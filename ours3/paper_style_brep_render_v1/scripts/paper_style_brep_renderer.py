#!/usr/bin/env python3
"""Paper-style mesh | split | true-BRep renderer for frozen Mesh2CAD results."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from PIL import Image, ImageDraw, ImageFont

from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GCPnts import GCPnts_AbscissaPoint
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import (
    TopAbs_COMPOUND,
    TopAbs_COMPSOLID,
    TopAbs_EDGE,
    TopAbs_FACE,
    TopAbs_REVERSED,
    TopAbs_SOLID,
    TopAbs_VERTEX,
)
from OCP.TopExp import TopExp
from OCP.TopLoc import TopLoc_Location
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS, TopoDS_Iterator


OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUTPUT_ROOT = OURS3 / "paper_style_brep_render_v1"
PALETTE = [
    "#9ecae1", "#f3b37a", "#e99b9b", "#79c7b8", "#efd66f", "#9fcf8f",
    "#b9a3d7", "#e8a6c5", "#85b6d9", "#d7b878", "#90c9ce", "#c5a5a1",
    "#a9c48c", "#b2abd2", "#efc39a", "#89b6a5", "#d9a4b2", "#a7b9d7",
    "#c6c77d", "#d7a97f", "#8dc4b7", "#c3abd8", "#e5b4a7", "#9eb9cf",
    "#b8cc9a", "#d8b2cb", "#a9c7c9", "#d7c49d",
]
CAMERA_DIRECTION = np.asarray([1.35, -1.55, 1.05], dtype=float)
CAMERA_DIRECTION /= np.linalg.norm(CAMERA_DIRECTION)
CAMERA_UP = np.asarray([0.0, 0.0, 1.0], dtype=float)


CASE_CONFIG = {
    "case05": {
        "case_id": "CASE_05",
        "prefix": "CASE05",
        "source_obj": OURS3 / "meshes/ASSORTED_VEGETABLE_SET.obj",
        "split_labels": OURS3 / "batch_real_mesh2cad_v1/cases/CASE_05/p3/triangle_part_id.npy",
        "step": OURS3 / "case05_residual_part003_recovery_v3/assembly/CASE_05_full_cad_assembly_v3.step",
        "split_type": "P3_PARTS",
        "recovered_holes": None,
    },
    "real03": {
        "case_id": "REAL_03",
        "prefix": "REAL03",
        "source_provenance": OURS3 / "fusion_pipeline/cases/REAL_03/source.json",
        "split_labels": OURS3 / "fusion_pipeline/cases/REAL_03/segmentation/triangle_part_id.npy",
        "step": OURS3 / "negative_feature_topology_recovery_v1/assembly/REAL_03_full_cad_assembly_feature_fixed.step",
        "split_type": "P3_PARTS",
        "recovered_holes": 10,
    },
}


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return clean(value.tolist())
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,)): return float(value)
    if isinstance(value, (np.bool_,)): return bool(value)
    return value


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_source(config):
    if "source_obj" in config: return Path(config["source_obj"]), None
    provenance = json.loads(Path(config["source_provenance"]).read_text(encoding="utf-8"))
    return Path(provenance["source_obj"]), str(config["source_provenance"])


def load_source_mesh(path: Path):
    mesh = trimesh.load(path, force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise RuntimeError(f"invalid source mesh: {path}")
    return mesh


def load_split_labels(path: Path, face_count: int):
    labels = np.load(path)
    if labels.ndim != 1 or len(labels) != face_count:
        raise RuntimeError(f"split label count mismatch: {path} {labels.shape} != {face_count}")
    return labels.astype(np.int32)


def fresh_read_step(path: Path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {path}")
    roots = reader.TransferRoots()
    shape = reader.OneShape()
    if roots <= 0 or shape.IsNull():
        raise RuntimeError(f"STEP transfer failed: {path}")
    return shape, int(roots)


def shape_bounds(shape):
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, True)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    bounds = np.asarray([[xmin, ymin, zmin], [xmax, ymax, zmax]], dtype=float)
    if not np.isfinite(bounds).all(): raise RuntimeError("invalid STEP bounds")
    return bounds


def indexed_shapes(shape, kind):
    mapping = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, mapping)
    return mapping


def direct_children(shape):
    values = []
    iterator = TopoDS_Iterator(shape)
    while iterator.More():
        values.append(iterator.Value())
        iterator.Next()
    return values


def assembly_components(shape):
    current = shape
    while current.ShapeType() in (TopAbs_COMPOUND, TopAbs_COMPSOLID):
        children = direct_children(current)
        if len(children) > 1: return children
        if len(children) != 1: break
        current = children[0]
    solids = indexed_shapes(shape, TopAbs_SOLID)
    if solids.Extent() > 1:
        return [solids.FindKey(i) for i in range(1, solids.Extent() + 1)]
    return [shape]


def point_tuple(point, transform=None):
    if transform is not None: point = point.Transformed(transform)
    return point.X(), point.Y(), point.Z()


SURFACE_TYPE_NAMES = {
    "GeomAbs_Plane": "Plane", "GeomAbs_Cylinder": "Cylinder", "GeomAbs_Cone": "Cone",
    "GeomAbs_Sphere": "Sphere", "GeomAbs_Torus": "Torus",
    "GeomAbs_BezierSurface": "BezierSurface", "GeomAbs_BSplineSurface": "BSplineSurface",
    "GeomAbs_SurfaceOfRevolution": "SurfaceOfRevolution", "GeomAbs_SurfaceOfExtrusion": "SurfaceOfExtrusion",
    "GeomAbs_OffsetSurface": "OffsetSurface", "GeomAbs_OtherSurface": "Other",
}
CURVE_TYPE_NAMES = {
    "GeomAbs_Line": "Line", "GeomAbs_Circle": "Circle", "GeomAbs_Ellipse": "Ellipse",
    "GeomAbs_Hyperbola": "Hyperbola", "GeomAbs_Parabola": "Parabola",
    "GeomAbs_BezierCurve": "BezierCurve", "GeomAbs_BSplineCurve": "BSplineCurve",
    "GeomAbs_OffsetCurve": "OffsetCurve", "GeomAbs_OtherCurve": "Other",
}


def enum_name(value, mapping):
    raw = str(value).split(".")[-1]
    return mapping.get(raw, raw.replace("GeomAbs_", ""))


def triangulate_component(shape, component_id, deflection, angular_deflection):
    BRepMesh_IncrementalMesh(shape, deflection, False, angular_deflection, True).Perform()
    face_map = indexed_shapes(shape, TopAbs_FACE)
    vertices, triangles, face_records = [], [], []
    for face_index in range(1, face_map.Extent() + 1):
        face = TopoDS.Face_s(face_map.FindKey(face_index))
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)
        surface_type = enum_name(BRepAdaptor_Surface(face).GetType(), SURFACE_TYPE_NAMES)
        if triangulation is None:
            face_records.append({"FACE_ID": face_index, "COMPONENT_ID": component_id, "SURFACE_TYPE": surface_type, "TESSELLATION_TRIANGLE_COUNT": 0})
            continue
        transform = location.Transformation()
        offset = len(vertices)
        for node_index in range(1, triangulation.NbNodes() + 1):
            vertices.append(point_tuple(triangulation.Node(node_index), transform))
        count = 0
        for triangle_index in range(1, triangulation.NbTriangles() + 1):
            a, b, c = triangulation.Triangle(triangle_index).Get()
            if face.Orientation() == TopAbs_REVERSED: b, c = c, b
            triangles.append((offset + a - 1, offset + b - 1, offset + c - 1))
            count += 1
        face_records.append({"FACE_ID": face_index, "COMPONENT_ID": component_id, "SURFACE_TYPE": surface_type, "TESSELLATION_TRIANGLE_COUNT": count})
    return np.asarray(vertices, dtype=np.float64), np.asarray(triangles, dtype=np.int64), face_records


def sample_curve(edge, bbox_diag):
    adaptor = BRepAdaptor_Curve(edge)
    first, last = float(adaptor.FirstParameter()), float(adaptor.LastParameter())
    if not np.isfinite(first) or not np.isfinite(last) or last <= first: return None
    curve_type = enum_name(adaptor.GetType(), CURVE_TYPE_NAMES)
    try: length = float(GCPnts_AbscissaPoint.Length_s(adaptor, first, last))
    except Exception: length = bbox_diag * 0.01
    if not np.isfinite(length) or length <= bbox_diag * 1e-10: return None
    target = max(bbox_diag * 0.004, 1e-8)
    base = max(2, int(math.ceil(length / target)) + 1)
    if curve_type == "Line": base = 2
    elif curve_type in ("Circle", "Ellipse"): base = max(base, 64)
    elif curve_type in ("BSplineCurve", "BezierCurve", "Other", "OffsetCurve"): base = max(base, 32)
    base = min(base, 96)
    parameters = np.linspace(first, last, base)
    points = np.asarray([point_tuple(adaptor.Value(float(u))) for u in parameters], dtype=float)
    # One curvature-refinement pass inserts midpoints where chord sag exceeds tolerance.
    refined = [points[0]]
    inserted = 0
    sag_tolerance = bbox_diag * 0.00025
    for i in range(base - 1):
        mid_u = float((parameters[i] + parameters[i + 1]) * 0.5)
        mid = np.asarray(point_tuple(adaptor.Value(mid_u)))
        sag = np.linalg.norm(mid - (points[i] + points[i + 1]) * 0.5)
        if sag > sag_tolerance and len(refined) < 192:
            refined.append(mid); inserted += 1
        refined.append(points[i + 1])
    points = np.asarray(refined, dtype=float)
    closed = bool(np.linalg.norm(points[0] - points[-1]) <= max(bbox_diag * 1e-6, 1e-9))
    return points, curve_type, length, inserted, closed


def extract_topology(shape, bbox_diag):
    face_map = indexed_shapes(shape, TopAbs_FACE)
    edge_map = indexed_shapes(shape, TopAbs_EDGE)
    vertex_map = indexed_shapes(shape, TopAbs_VERTEX)
    edge_points, edge_cells, edge_records = [], [], []
    cursor = 0
    for edge_index in range(1, edge_map.Extent() + 1):
        edge = TopoDS.Edge_s(edge_map.FindKey(edge_index))
        try: sampled = sample_curve(edge, bbox_diag)
        except Exception as exc:
            sampled = None
            error = type(exc).__name__
        else: error = None
        if sampled is None:
            edge_records.append({"EDGE_ID": edge_index, "EDGE_CURVE_TYPE": "DegenerateOrUnavailable", "RENDERED": False, "SAMPLE_COUNT": 0, "ERROR": error})
            continue
        points, curve_type, length, inserted, closed = sampled
        edge_points.extend(points.tolist())
        edge_cells.append(np.arange(cursor, cursor + len(points), dtype=np.int64))
        cursor += len(points)
        edge_records.append({"EDGE_ID": edge_index, "EDGE_CURVE_TYPE": curve_type, "RENDERED": True, "SAMPLE_COUNT": len(points), "CURVE_LENGTH": length, "CURVATURE_REFINEMENT_POINTS": inserted, "CLOSED": closed})
    vertices, vertex_records = [], []
    for vertex_index in range(1, vertex_map.Extent() + 1):
        vertex = TopoDS.Vertex_s(vertex_map.FindKey(vertex_index))
        point = point_tuple(BRep_Tool.Pnt_s(vertex))
        vertices.append(point)
        vertex_records.append({"VERTEX_ID": vertex_index, "XYZ": point})
    return {
        "face_count": face_map.Extent(), "edge_count": edge_map.Extent(), "vertex_count": vertex_map.Extent(),
        "edge_points": np.asarray(edge_points, dtype=np.float64), "edge_cells": edge_cells,
        "vertices": np.asarray(vertices, dtype=np.float64), "edge_records": edge_records,
        "vertex_records": vertex_records,
    }


def polydata(points, faces):
    cells = np.column_stack((np.full(len(faces), 3, dtype=np.int64), faces)).ravel()
    return pv.PolyData(points, cells)


def line_polydata(points, cells):
    encoded = []
    for cell in cells: encoded.extend([len(cell), *cell.tolist()])
    result = pv.PolyData(points)
    result.lines = np.asarray(encoded, dtype=np.int64)
    return result


def configure_plotter(center, diag, window=(1000, 1000), background="white"):
    plotter = pv.Plotter(off_screen=True, window_size=window)
    plotter.set_background(background)
    plotter.camera.parallel_projection = True
    plotter.camera_position = [tuple(center + CAMERA_DIRECTION * diag * 3.0), tuple(center), tuple(CAMERA_UP)]
    plotter.camera.parallel_scale = diag * 0.61
    plotter.enable_anti_aliasing("fxaa")
    return plotter


def finish_plotter(plotter, output):
    plotter.reset_camera_clipping_range()
    # VTK 9.3/Xvfb can segfault in the explicit return_img=False code path on
    # large actors; the default screenshot path is stable and still writes PNG.
    plotter.screenshot(str(output))
    plotter.close()


def render_mesh_panel(mesh, center, diag, output):
    plotter = configure_plotter(center, diag)
    data = polydata(np.asarray(mesh.vertices), np.asarray(mesh.faces))
    plotter.add_mesh(data, color="#e5e1d7", show_edges=False, smooth_shading=False,
                     ambient=0.38, diffuse=0.72, specular=0.06)
    # VTK's show_edges path can exhaust the Xvfb OpenGL context on 300k+ face
    # meshes.  Draw a deterministic representative set of the actual OBJ
    # triangle edges as a separate depth-tested actor instead.
    unique_edges = np.asarray(mesh.edges_unique, dtype=np.int64)
    display_count = min(len(unique_edges), 120000)
    selected = unique_edges[np.linspace(0, len(unique_edges)-1, display_count, dtype=np.int64)]
    wire = pv.PolyData(np.asarray(mesh.vertices))
    wire.lines = np.column_stack((np.full(display_count, 2, dtype=np.int64), selected)).ravel()
    plotter.add_mesh(wire, color="#72777d", line_width=0.3, opacity=0.32,
                     render_lines_as_tubes=False, ambient=1.0, diffuse=0.0)
    finish_plotter(plotter, output)


def render_split_panel(mesh, labels, center, diag, output, explode=0.04):
    plotter = configure_plotter(center, diag)
    vertices, faces = np.asarray(mesh.vertices), np.asarray(mesh.faces)
    for color_index, label in enumerate(sorted(np.unique(labels))):
        part_faces = faces[labels == label]
        used, inverse = np.unique(part_faces.ravel(), return_inverse=True)
        local_faces = inverse.reshape((-1, 3))
        local_vertices = vertices[used].copy()
        centroid = local_vertices.mean(axis=0)
        direction = centroid - center
        norm = np.linalg.norm(direction)
        if norm > 1e-12: local_vertices += direction / norm * diag * explode
        plotter.add_mesh(polydata(local_vertices, local_faces), color=PALETTE[color_index % len(PALETTE)],
                         smooth_shading=True, show_edges=False, ambient=0.38, diffuse=0.74,
                         specular=0.10, specular_power=24)
    finish_plotter(plotter, output)


def render_brep(surface_points, surface_faces, face_components, edge_data, vertex_points,
                center, diag, output, part_colored=False, wireframe=False):
    plotter = configure_plotter(center, diag)
    if not wireframe:
        if part_colored:
            for color_index, component in enumerate(sorted(np.unique(face_components))):
                selected = surface_faces[face_components == component]
                used, inverse = np.unique(selected.ravel(), return_inverse=True)
                plotter.add_mesh(polydata(surface_points[used], inverse.reshape((-1, 3))),
                                 color=PALETTE[color_index % len(PALETTE)], smooth_shading=True,
                                 show_edges=False, ambient=0.34, diffuse=0.72, specular=0.22, specular_power=32)
        else:
            plotter.add_mesh(polydata(surface_points, surface_faces), color="#aec7e8", smooth_shading=True,
                             show_edges=False, ambient=0.34, diffuse=0.72, specular=0.22, specular_power=32)
    if len(edge_data.points):
        plotter.add_mesh(edge_data, color="#263750", line_width=1.15 if not wireframe else 1.35,
                         render_lines_as_tubes=False, ambient=1.0, diffuse=0.0)
    if len(vertex_points):
        plotter.add_mesh(pv.PolyData(vertex_points), color="#1f6fd1", point_size=3.2 if not wireframe else 4.2,
                         render_points_as_spheres=True, ambient=1.0, diffuse=0.0)
    finish_plotter(plotter, output)


def find_font(size):
    candidates = [
        "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/times.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for path in candidates:
        if Path(path).is_file(): return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def compose(images, labels, caption, output, width_each=1100):
    panel_height = 1100; top = 74; bottom = 112
    canvas = Image.new("RGB", (width_each * len(images), top + panel_height + bottom), "white")
    draw = ImageDraw.Draw(canvas)
    label_font = find_font(32); caption_font = find_font(23)
    for index, (path, label) in enumerate(zip(images, labels)):
        image = Image.open(path).convert("RGB").resize((width_each, panel_height), Image.Resampling.LANCZOS)
        canvas.paste(image, (index * width_each, top))
        box = draw.textbbox((0, 0), label, font=label_font)
        x = index * width_each + (width_each - (box[2] - box[0])) // 2
        draw.text((x, 22), label, fill="#24262b", font=label_font)
    box = draw.textbbox((0, 0), caption, font=caption_font)
    draw.text(((canvas.width - (box[2] - box[0])) // 2, top + panel_height + 38), caption, fill="#42464d", font=caption_font)
    canvas.save(output, dpi=(300, 300))
    canvas.save(output.with_suffix(".pdf"), "PDF", resolution=300.0)


def faceted_audit(face_records, source_face_count):
    counts = np.asarray([x["TESSELLATION_TRIANGLE_COUNT"] for x in face_records], dtype=float)
    types = Counter(x["SURFACE_TYPE"] for x in face_records)
    face_count = len(face_records)
    planar_fraction = types.get("Plane", 0) / max(face_count, 1)
    median_triangles = float(np.median(counts)) if len(counts) else 0.0
    wrapped = bool(face_count > max(1000, int(source_face_count * 0.25)) and planar_fraction > 0.95 and median_triangles <= 4)
    analytic = sum(types.get(name, 0) for name in ("Plane", "Cylinder", "Cone", "Sphere", "Torus", "SurfaceOfRevolution", "SurfaceOfExtrusion"))
    return {
        "FACETED_MESH_WRAPPED_AS_BREP": wrapped,
        "PLANAR_FACE_FRACTION": planar_fraction,
        "MEDIAN_TESSELLATION_TRIANGLES_PER_FACE": median_triangles,
        "ANALYTIC_FACE_COUNT": analytic,
        "BSPLINE_FACE_COUNT": types.get("BSplineSurface", 0),
        "LOFT_FACE_COUNT_IF_AVAILABLE": types.get("BSplineSurface", 0),
        "FACE_TYPE_COUNTS": dict(types),
        "FACETED_AUDIT_RULE": "face_count > max(1000, 0.25*source_triangle_count) and planar_fraction > 0.95 and median_face_tessellation_triangles <= 4",
    }


def process_case(case_key):
    config = CASE_CONFIG[case_key]
    out = OUTPUT_ROOT / case_key
    metrics_dir = out / "metrics"
    out.mkdir(parents=True, exist_ok=True); metrics_dir.mkdir(parents=True, exist_ok=True)
    source_path, provenance_path = resolve_source(config)
    source = load_source_mesh(source_path)
    labels = load_split_labels(Path(config["split_labels"]), len(source.faces))
    shape, root_count = fresh_read_step(Path(config["step"]))
    step_bounds = shape_bounds(shape); step_diag = float(np.linalg.norm(step_bounds[1] - step_bounds[0]))
    source_bounds = np.asarray(source.bounds); source_diag = float(np.linalg.norm(source_bounds[1] - source_bounds[0]))
    shared_bounds = np.asarray([np.minimum(source_bounds[0], step_bounds[0]), np.maximum(source_bounds[1], step_bounds[1])])
    center = shared_bounds.mean(axis=0); shared_diag = float(np.linalg.norm(shared_bounds[1] - shared_bounds[0]))
    deflection = max(step_diag * 0.001, 1e-6); angular = 0.12
    components = assembly_components(shape)
    point_chunks, face_chunks, component_chunks, face_records = [], [], [], []
    offset = 0
    for component_id, component in enumerate(components):
        points, faces, records = triangulate_component(component, component_id, deflection, angular)
        if len(faces):
            point_chunks.append(points); face_chunks.append(faces + offset)
            component_chunks.append(np.full(len(faces), component_id, dtype=np.int32)); offset += len(points)
        for record in records: record["GLOBAL_FACE_ID"] = len(face_records) + 1; face_records.append(record)
    surface_points = np.vstack(point_chunks); surface_faces = np.vstack(face_chunks); face_components = np.concatenate(component_chunks)
    topology = extract_topology(shape, step_diag)
    topology_audit = faceted_audit(face_records, len(source.faces))
    edge_type_counts = Counter(x["EDGE_CURVE_TYPE"] for x in topology["edge_records"])
    rendered_edges = sum(x["RENDERED"] for x in topology["edge_records"])
    closed_edges = sum(x.get("CLOSED", False) for x in topology["edge_records"])
    curved_samples = [x["SAMPLE_COUNT"] for x in topology["edge_records"] if x["RENDERED"] and x["EDGE_CURVE_TYPE"] != "Line"]
    brep_topology = {
        "CASE_ID": config["case_id"], "STEP_PATH": str(config["step"]), "STEP_FRESH_RELOAD_SUCCESS": True,
        "STEP_TRANSFERRED_ROOT_COUNT": root_count, "ASSEMBLY_COMPONENT_COUNT": len(components),
        "BREP_FACE_COUNT": topology["face_count"], "BREP_EDGE_COUNT": topology["edge_count"],
        "BREP_VERTEX_COUNT": topology["vertex_count"], "RENDERED_BREP_EDGE_COUNT": rendered_edges,
        "UNRENDERED_DEGENERATE_EDGE_COUNT": topology["edge_count"] - rendered_edges,
        "DUPLICATE_EDGE_HANDLING": "TopTools_IndexedMapOfShape identity deduplication",
        "EDGE_RENDER_COUNT_EXPLANATION": "one polyline per unique non-degenerate TopoDS_Edge; degenerate/unavailable edges are audited but not drawable",
        "EDGE_CURVE_TYPE_COUNTS": dict(edge_type_counts), "CLOSED_BREP_EDGE_COUNT": closed_edges,
        "CURVED_EDGE_MIN_SAMPLE_COUNT": min(curved_samples) if curved_samples else 0,
        "CURVED_EDGE_SAMPLING": "curve-length base density plus midpoint chord-sag curvature refinement",
        "TESSELLATION_LINEAR_DEFLECTION": deflection, "TESSELLATION_ANGULAR_DEFLECTION": angular,
        "FACES": face_records, "EDGES": topology["edge_records"], "VERTICES": topology["vertex_records"],
        **topology_audit,
    }
    dump(metrics_dir / "brep_topology.json", brep_topology)
    np.savez_compressed(metrics_dir / "brep_render_cache.npz", surface_points=surface_points,
                        surface_faces=surface_faces, face_components=face_components,
                        edge_points=topology["edge_points"], vertices=topology["vertices"])

    render_input = {
        "CASE_KEY": case_key, "CASE_ID": config["case_id"], "PREFIX": config["prefix"],
        "SOURCE_OBJ": str(source_path), "SOURCE_OBJ_PROVENANCE_PATH": provenance_path,
        "SPLIT_LABELS": str(config["split_labels"]), "SPLIT_VISUALIZATION_TYPE": config["split_type"],
        "STEP_PATH": str(config["step"]), "CENTER": center.tolist(), "SHARED_DIAG": shared_diag,
        "SHARED_WORLD_BOUNDS": shared_bounds.tolist(), "SOURCE_TRIANGLE_COUNT": len(source.faces),
        "SOURCE_EDGE_COUNT": int(len(source.edges_unique)), "SPLIT_REGION_COUNT": int(len(np.unique(labels))),
        "BREP_TESSELLATION_TRIANGLE_COUNT": len(surface_faces), "ASSEMBLY_COMPONENT_COUNT": len(components),
        "RECOVERED_HOLE_COUNT": config["recovered_holes"],
    }
    dump(metrics_dir / "render_input.json", render_input)

    # OCP and VTK/OpenGL are deliberately isolated in different processes.  On
    # this server their shared native dependencies can segfault when a large
    # STEP transfer graph and a VTK render context coexist in one interpreter.
    del shape, components
    gc.collect()
    helper = Path(__file__).with_name("paper_style_render_cached.py")
    command = ["xvfb-run", "-a", "-s", "-screen 0 1920x1200x24", sys.executable, str(helper), "--case", case_key]
    subprocess.run(command, check=True, cwd=str(OUTPUT_ROOT))
    return json.loads((out / "render_metadata.json").read_text(encoding="utf-8"))


def finalize(results):
    summary = {
        "CURRENT_GATE": "PAPER_STYLE_BREP_RENDERER_V1_PASS" if all(not x["FACETED_MESH_WRAPPED_AS_BREP"] for x in results.values()) else "PAPER_STYLE_BREP_RENDERER_V1_FAIL",
        "RENDER_BACKEND": "OCP_7_8_PLUS_PYVISTA_0_48_XVFB_OFFSCREEN", "OUTPUT_ROOT": str(OUTPUT_ROOT),
        "cases": results, "TESTS_PASSED": 0, "TESTS_FAILED": 0,
        "BLOCKERS": [] if all(not x["FACETED_MESH_WRAPPED_AS_BREP"] for x in results.values()) else ["FACETED_MESH_WRAPPED_AS_BREP"],
    }
    dump(OUTPUT_ROOT / "artifacts/summary.json", summary)
    lines = ["# PAPER_STYLE_BREP_RENDERER_V1", "", "## Outcome", "", f"- Gate: `{summary['CURRENT_GATE']}`", f"- Backend: `{summary['RENDER_BACKEND']}`", "", "## Provenance", "", "- Mesh panels use source OBJ triangle faces and edges.", "- Split panels use frozen P3 triangle labels with a 0.04 bbox-diagonal explosion.", "- BRep panels use only freshly reloaded STEP topology: independently tessellated faces, unique TopoDS edges, and TopoDS vertices.", "- No CAD recovery, P3, PhysX, MAC, or LLM was rerun; STEP geometry was not modified.", ""]
    for key, metadata in results.items():
        lines += [f"## {metadata['CASE_ID']}", "", f"- Faces / edges / vertices: `{metadata['BREP_FACE_COUNT']} / {metadata['BREP_EDGE_COUNT']} / {metadata['BREP_VERTEX_COUNT']}`", f"- Faceted wrapped audit: `{metadata['FACETED_MESH_WRAPPED_AS_BREP']}`", f"- Comparison: `{OUTPUT_ROOT/key/'comparison_figure.png'}`", ""]
    (OUTPUT_ROOT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=("case05", "real03", "all"), default="all")
    args = parser.parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    keys = list(CASE_CONFIG) if args.case == "all" else [args.case]
    results = {}
    for key in keys:
        print(f"START_CASE={key}", flush=True)
        results[key] = process_case(key)
        print(f"DONE_CASE={key}", flush=True)
    if args.case == "all": print(json.dumps(clean(finalize(results)), indent=2), flush=True)


if __name__ == "__main__": main()
