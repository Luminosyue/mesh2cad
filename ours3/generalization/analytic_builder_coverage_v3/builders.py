from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import ConvexHull


def _world_points(local_points: np.ndarray, frame: dict[str, Any]) -> np.ndarray:
    matrix = np.asarray(frame["local_to_world"], dtype=float)
    homogeneous = np.column_stack((local_points, np.ones(len(local_points))))
    return (matrix @ homogeneous.T).T[:, :3]


def _wire(points: np.ndarray) -> Any:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    polygon = BRepBuilderAPI_MakePolygon()
    first = None
    for point in points:
        gp_point = gp_Pnt(*map(float, point))
        polygon.Add(gp_point)
        if first is None:
            first = gp_point
    if first is None:
        raise ValueError("PROFILE_EMPTY")
    polygon.Add(first)
    polygon.Close()
    return polygon.Wire()


def _face(points: np.ndarray) -> Any:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace

    return BRepBuilderAPI_MakeFace(_wire(points), True).Face()


def _signed_area(points: np.ndarray) -> float:
    return 0.5 * float(
        np.sum(
            points[:, 0] * np.roll(points[:, 1], -1)
            - points[:, 1] * np.roll(points[:, 0], -1)
        )
    )


def _boundary_loops(local_mesh: trimesh.Trimesh) -> list[np.ndarray]:
    """Recover deterministic polygon loops from the source triangle boundary."""
    edges = np.asarray(local_mesh.edges_unique, dtype=np.int64)
    inverse = np.asarray(local_mesh.edges_unique_inverse, dtype=np.int64)
    if len(edges) == 0:
        return []
    counts = np.bincount(inverse, minlength=len(edges))
    boundary = edges[counts == 1]
    if len(boundary) == 0:
        return []

    adjacency: dict[int, list[int]] = {}
    for edge_index, (start, end) in enumerate(boundary):
        a, b = int(start), int(end)
        adjacency.setdefault(a, []).append(edge_index)
        adjacency.setdefault(b, []).append(edge_index)
    for values in adjacency.values():
        values.sort()

    unused = set(range(len(boundary)))
    loops: list[np.ndarray] = []
    while unused:
        first_edge = min(unused)
        start, current = map(int, boundary[first_edge])
        unused.remove(first_edge)
        vertex_loop = [start, current]
        previous = start
        while current != start:
            candidates = [
                edge_index
                for edge_index in adjacency.get(current, [])
                if edge_index in unused
            ]
            if not candidates:
                break
            next_edge = candidates[0]
            unused.remove(next_edge)
            a, b = map(int, boundary[next_edge])
            next_vertex = b if a == current else a
            if next_vertex == previous and len(candidates) > 1:
                next_edge = candidates[1]
                unused.add(candidates[0])
                unused.remove(next_edge)
                a, b = map(int, boundary[next_edge])
                next_vertex = b if a == current else a
            vertex_loop.append(next_vertex)
            previous, current = current, next_vertex
            if len(vertex_loop) > len(boundary) + 2:
                break
        if current == start and len(vertex_loop) >= 4:
            loops.append(np.asarray(vertex_loop[:-1], dtype=np.int64))
    return loops


def _project_loop(
    local_mesh: trimesh.Trimesh,
    indices: np.ndarray,
) -> np.ndarray:
    vertices = np.asarray(local_mesh.vertices, dtype=float)
    points = vertices[indices]
    plane_z = float(np.median(vertices[:, 2]))
    return np.column_stack((points[:, :2], np.full(len(points), plane_z)))


def planar_face(local_mesh: trimesh.Trimesh, frame: dict[str, Any]) -> dict[str, Any]:
    loops = _boundary_loops(local_mesh)
    if not loops:
        raise ValueError("PROFILE_RECOVERY_FAILURE:NO_BOUNDARY_LOOP")
    projected = [_project_loop(local_mesh, loop) for loop in loops]
    try:
        from shapely.geometry import Polygon
    except Exception as exc:
        raise ValueError(f"PROFILE_RECOVERY_FAILURE:SHAPELY_IMPORT:{exc}") from exc

    repaired: list[Any] = []
    for loop in projected:
        xy = loop[:, :2]
        scale = max(float(np.ptp(xy, axis=0).max()), 1e-8)
        polygon = Polygon(xy)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            continue
        polygon = polygon.simplify(max(scale * 2.5e-4, 1e-7), preserve_topology=True)
        if polygon.geom_type == "MultiPolygon":
            repaired.extend(sorted(polygon.geoms, key=lambda item: item.area, reverse=True)[:4])
        elif polygon.geom_type == "Polygon":
            repaired.append(polygon)
    if not repaired:
        raise ValueError("PROFILE_RECOVERY_FAILURE:EMPTY_REPAIRED_PROFILE")

    outer_polygon = max(repaired, key=lambda item: item.area)
    outer_xy = np.asarray(outer_polygon.exterior.coords[:-1], dtype=float)
    outer = np.column_stack((
        outer_xy,
        np.full(len(outer_xy), float(np.median(np.asarray(local_mesh.vertices)[:, 2]))),
    ))
    if abs(_signed_area(outer[:, :2])) < 1e-10:
        raise ValueError("PROFILE_RECOVERY_FAILURE:DEGENERATE_OUTER_LOOP")
    outer_area = _signed_area(outer[:, :2])
    if outer_area < 0:
        outer = outer[::-1]

    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace

    maker = BRepBuilderAPI_MakeFace(_wire(_world_points(outer, frame)), True)
    inner_profiles = []
    for polygon in repaired:
        if polygon is outer_polygon:
            continue
        representative = polygon.representative_point()
        if not outer_polygon.contains(representative):
            continue
        inner_xy = np.asarray(polygon.exterior.coords[:-1], dtype=float)
        inner = np.column_stack((
            inner_xy,
            np.full(len(inner_xy), float(np.median(np.asarray(local_mesh.vertices)[:, 2]))),
        ))
        if abs(_signed_area(inner[:, :2])) < 1e-10:
            continue
        if _signed_area(inner[:, :2]) > 0:
            inner = inner[::-1]
        maker.Add(_wire(_world_points(inner, frame)))
        inner_profiles.append(inner[:, :2].tolist())
        for interior in polygon.interiors:
            hole_xy = np.asarray(interior.coords[:-1], dtype=float)
            hole = np.column_stack((
                hole_xy,
                np.full(len(hole_xy), float(np.median(np.asarray(local_mesh.vertices)[:, 2]))),
            ))
            if _signed_area(hole[:, :2]) > 0:
                hole = hole[::-1]
            maker.Add(_wire(_world_points(hole, frame)))
            inner_profiles.append(hole[:, :2].tolist())
    maker.Build()
    if not maker.IsDone():
        raise ValueError("PROFILE_RECOVERY_FAILURE:OCC_FACE_BUILD")
    return {
        "shape": maker.Face(),
        "parameters": {
            "axis": frame["axis_z"],
            "outer_profile": outer[:, :2].tolist(),
            "inner_profiles": inner_profiles,
            "boundary_loop_count": len(loops),
            "profile_fit_error": float(np.std(np.asarray(local_mesh.vertices)[:, 2])),
            "builder_type": "PLANAR_FACE",
            "representation": "ANALYTIC_PLANAR_FACE",
        },
    }


def _profile(local_mesh: trimesh.Trimesh, station_mask: np.ndarray | None = None) -> np.ndarray:
    points = np.asarray(local_mesh.vertices, dtype=float)
    if station_mask is not None:
        points = points[station_mask]
    if len(points) < 3:
        raise ValueError("PROFILE_TOO_FEW_POINTS")
    uv = points[:, :2]
    step = max(1, len(uv) // 3000)
    sampled = uv[::step]
    if len(sampled) < 3:
        sampled = uv
    hull = ConvexHull(sampled)
    profile = sampled[hull.vertices]
    area = 0.5 * float(np.sum(profile[:, 0] * np.roll(profile[:, 1], -1) - profile[:, 1] * np.roll(profile[:, 0], -1)))
    if area < 0:
        profile = profile[::-1]
    return profile


def _profile_at_station(local_mesh: trimesh.Trimesh, frame: dict[str, Any], station: float) -> np.ndarray:
    vertices = np.asarray(local_mesh.vertices, dtype=float)
    extent = max(float(np.ptp(vertices[:, 2])), 1e-12)
    mask = np.abs(vertices[:, 2] - station) <= max(extent * 0.12, 1e-5)
    if int(mask.sum()) < 20:
        order = np.argsort(np.abs(vertices[:, 2] - station))
        mask = np.zeros(len(vertices), dtype=bool)
        mask[order[: min(len(vertices), 5000)]] = True
    profile = _profile(local_mesh, mask)
    return np.column_stack((profile, np.full(len(profile), station)))


def profile_extrusion(local_mesh: trimesh.Trimesh, frame: dict[str, Any]) -> dict[str, Any]:
    vertices = np.asarray(local_mesh.vertices, dtype=float)
    low, high = float(vertices[:, 2].min()), float(vertices[:, 2].max())
    if high - low <= 1e-8:
        raise ValueError("PROFILE_EXTRUSION_ZERO_EXTENT")
    profile = _profile(local_mesh)
    local_polygon = np.column_stack((profile, np.full(len(profile), low)))
    world_polygon = _world_points(local_polygon, frame)
    origin = np.asarray(frame["origin"], dtype=float)
    axis = np.asarray(frame["axis_z"], dtype=float)
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Vec

    shape = BRepPrimAPI_MakePrism(
        _face(world_polygon),
        gp_Vec(*map(float, axis * (high - low))),
        True,
    ).Shape()
    return {
        "shape": shape,
        "parameters": {
            "axis": axis.tolist(),
            "station_min": low,
            "station_max": high,
            "outer_profile": profile.tolist(),
            "inner_profiles": [],
            "profile_fit_error": 0.0,
            "builder_type": "PROFILE_EXTRUSION",
        },
    }


def tapered_extrusion(local_mesh: trimesh.Trimesh, frame: dict[str, Any]) -> dict[str, Any]:
    vertices = np.asarray(local_mesh.vertices, dtype=float)
    low, high = float(vertices[:, 2].min()), float(vertices[:, 2].max())
    if high - low <= 1e-8:
        raise ValueError("TAPERED_EXTRUSION_ZERO_EXTENT")
    start = _profile_at_station(local_mesh, frame, low + 0.10 * (high - low))
    end = _profile_at_station(local_mesh, frame, high - 0.10 * (high - low))
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

    loft = BRepOffsetAPI_ThruSections(True, False, 1e-5)
    loft.CheckCompatibility(False)
    loft.SetMaxDegree(5)
    loft.AddWire(_wire(_world_points(start, frame)))
    loft.AddWire(_wire(_world_points(end, frame)))
    loft.Build()
    if not loft.IsDone():
        raise ValueError("TAPERED_EXTRUSION_BUILD_FAILED")
    return {
        "shape": loft.Shape(),
        "parameters": {
            "axis": frame["axis_z"],
            "station_start": low,
            "station_end": high,
            "profile_start": start[:, :2].tolist(),
            "profile_end": end[:, :2].tolist(),
            "builder_type": "TAPERED_EXTRUSION",
        },
    }


def revolution(local_mesh: trimesh.Trimesh, frame: dict[str, Any]) -> dict[str, Any]:
    vertices = np.asarray(local_mesh.vertices, dtype=float)
    low, high = float(vertices[:, 2].min()), float(vertices[:, 2].max())
    if high - low <= 1e-8:
        raise ValueError("REVOLUTION_ZERO_EXTENT")
    radial = np.linalg.norm(vertices[:, :2], axis=1)
    bins = np.linspace(low, high, 18)
    profile = []
    for left, right in zip(bins[:-1], bins[1:]):
        values = radial[(vertices[:, 2] >= left) & (vertices[:, 2] <= right)]
        if len(values):
            profile.append((float(np.percentile(values, 90)), float((left + right) * 0.5)))
    if len(profile) < 3:
        raise ValueError("REVOLUTION_PROFILE_RECOVERY_FAILURE")
    local_profile = np.asarray([(0.0, low), *[(radius, station) for radius, station in profile], (0.0, high)], dtype=float)
    local_polygon = np.column_stack((local_profile[:, 0], np.zeros(len(local_profile)), local_profile[:, 1]))
    world_polygon = _world_points(local_polygon, frame)
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
    from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt

    origin = np.asarray(frame["origin"], dtype=float)
    axis = np.asarray(frame["axis_z"], dtype=float)
    shape = BRepPrimAPI_MakeRevol(
        _face(world_polygon),
        gp_Ax1(gp_Pnt(*map(float, origin)), gp_Dir(*map(float, axis))),
        2.0 * math.pi,
        True,
    ).Shape()
    return {
        "shape": shape,
        "parameters": {
            "axis": axis.tolist(),
            "generatrix_profile": local_profile.tolist(),
            "builder_type": "REVOLUTION",
        },
    }


def box_prism(local_mesh: trimesh.Trimesh, frame: dict[str, Any]) -> dict[str, Any]:
    vertices = np.asarray(local_mesh.vertices, dtype=float)
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    corners = np.asarray([
        [low[0], low[1], low[2]],
        [high[0], low[1], low[2]],
        [high[0], high[1], low[2]],
        [low[0], high[1], low[2]],
    ])
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Vec

    shape = BRepPrimAPI_MakePrism(
        _face(_world_points(corners, frame)),
        gp_Vec(*map(float, np.asarray(frame["axis_z"]) * (high[2] - low[2]))),
        True,
    ).Shape()
    return {
        "shape": shape,
        "parameters": {
            "bbox_min": low.tolist(),
            "bbox_max": high.tolist(),
            "builder_type": "BOX_PRISM",
        },
    }


def boolean_cut(base: Any, cutter: Any) -> dict[str, Any]:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut

    result = BRepAlgoAPI_Cut(base, cutter).Shape()
    return {"shape": result, "parameters": {"boolean_operation": "cut", "builder_type": "BOOLEAN_CUT"}}


def boolean_union(shapes: list[Any]) -> dict[str, Any]:
    if not 1 < len(shapes) <= 4:
        raise ValueError("BOOLEAN_UNION_COMPONENT_LIMIT")
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

    result = shapes[0]
    for shape in shapes[1:]:
        result = BRepAlgoAPI_Fuse(result, shape).Shape()
    return {"shape": result, "parameters": {"boolean_operation": "union", "component_count": len(shapes), "builder_type": "BOOLEAN_UNION"}}


def validate_shape(shape: Any) -> bool:
    from OCP.BRepCheck import BRepCheck_Analyzer

    return bool(shape is not None and not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())


def write_step(shape: Any, path: Path) -> bool:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    return bool(writer.Write(str(path)) == IFSelect_RetDone)


def build_family(
    family: str,
    local_mesh: trimesh.Trimesh,
    frame: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    if family == "PLANAR_FACE":
        result = planar_face(local_mesh, frame)
    elif family == "PROFILE_EXTRUSION":
        result = profile_extrusion(local_mesh, frame)
    elif family == "TAPERED_EXTRUSION":
        result = tapered_extrusion(local_mesh, frame)
    elif family == "REVOLUTION":
        result = revolution(local_mesh, frame)
    elif family == "BOX_PRISM":
        result = box_prism(local_mesh, frame)
    else:
        raise ValueError("NO_SUPPORTED_BUILDER:" + family)
    occ_valid = validate_shape(result["shape"])
    if occ_valid and not write_step(result["shape"], output):
        raise ValueError("STEP_WRITE_FAILED")
    return {
        "valid": occ_valid,
        "step_path": str(output) if occ_valid else None,
        "parameters": result["parameters"],
        "builder_type": family,
    }
