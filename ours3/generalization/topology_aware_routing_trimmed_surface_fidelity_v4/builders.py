from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from generalization.analytic_builder_coverage_v3 import builders as v3_builders


def _world_points(local_points: np.ndarray, frame: dict[str, Any]) -> np.ndarray:
    matrix = np.asarray(frame["local_to_world"], dtype=float)
    homogeneous = np.column_stack((local_points, np.ones(len(local_points))))
    return (matrix @ homogeneous.T).T[:, :3]


def _face(points: np.ndarray) -> Any:
    return v3_builders._face(points)


def _signed_area(points: np.ndarray) -> float:
    return 0.5 * float(
        np.sum(
            points[:, 0] * np.roll(points[:, 1], -1)
            - points[:, 1] * np.roll(points[:, 0], -1)
        )
    )


def _boundary_loops(local_mesh: trimesh.Trimesh) -> list[np.ndarray]:
    """Recover closed source boundary loops without inventing closure."""
    edges = np.asarray(local_mesh.edges_unique, dtype=np.int64)
    inverse = np.asarray(local_mesh.edges_unique_inverse, dtype=np.int64)
    if not len(edges):
        return []
    counts = np.bincount(inverse, minlength=len(edges))
    boundary = edges[counts == 1]
    if not len(boundary):
        return []

    adjacency: dict[int, list[int]] = {}
    for edge_index, (start, end) in enumerate(boundary):
        adjacency.setdefault(int(start), []).append(edge_index)
        adjacency.setdefault(int(end), []).append(edge_index)
    for values in adjacency.values():
        values.sort()

    unused = set(range(len(boundary)))
    loops: list[np.ndarray] = []
    while unused:
        edge_index = min(unused)
        start, current = map(int, boundary[edge_index])
        unused.remove(edge_index)
        vertex_loop = [start, current]
        previous = start
        while current != start:
            choices = [
                candidate
                for candidate in adjacency.get(current, [])
                if candidate in unused
            ]
            if not choices:
                break
            next_edge = choices[0]
            if len(choices) > 1:
                for candidate in choices:
                    a, b = map(int, boundary[candidate])
                    if (b if a == current else a) != previous:
                        next_edge = candidate
                        break
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


def _fit_plane(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    center = np.asarray(points, dtype=float).mean(axis=0)
    _, singular, axes = np.linalg.svd(
        np.asarray(points, dtype=float) - center,
        full_matrices=False,
    )
    u, v, normal = axes[0], axes[1], axes[2]
    if np.dot(np.cross(u, v), normal) < 0:
        v = -v
        normal = -normal
    residual = float(singular[-1] / max(singular[0], 1e-12))
    return center, u, v, residual


def _repair_loop_polygons(
    local_mesh: trimesh.Trimesh,
    loops: list[np.ndarray],
    center: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
) -> list[Any]:
    try:
        from shapely.geometry import Polygon
    except Exception as exc:
        raise ValueError(f"SHAPELY_IMPORT:{exc}") from exc

    vertices = np.asarray(local_mesh.vertices, dtype=float)
    scale = max(float(np.ptp(vertices, axis=0).max()), 1e-8)
    tolerance = max(scale * 1.0e-4, 1.0e-7)
    repaired: list[Any] = []
    for loop in loops:
        points = vertices[loop]
        uv = np.column_stack(((points - center) @ u, (points - center) @ v))
        if len(uv) < 3 or abs(_signed_area(uv)) < 1e-10:
            continue
        polygon = Polygon(uv)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            continue
        polygon = polygon.simplify(tolerance, preserve_topology=True)
        if polygon.geom_type == "MultiPolygon":
            repaired.extend(sorted(polygon.geoms, key=lambda item: item.area, reverse=True)[:8])
        elif polygon.geom_type == "Polygon" and polygon.area > tolerance * tolerance:
            repaired.append(polygon)
    return repaired


def _trimmed_component_faces(
    component: trimesh.Trimesh,
    frame: dict[str, Any],
) -> tuple[list[Any], dict[str, Any]]:
    """Build exact planar trims from component boundaries; never use a hull as final trim."""
    points = np.asarray(component.vertices, dtype=float)
    if len(points) < 3:
        return [], {"outer_loop_count": 0, "inner_loop_count": 0}
    center, u, v, plane_residual = _fit_plane(points)
    loops = _boundary_loops(component)
    if not loops:
        return [], {
            "outer_loop_count": 0,
            "inner_loop_count": 0,
            "plane_residual": plane_residual,
            "boundary_recovery": "NO_CLOSED_LOOP",
        }
    polygons = _repair_loop_polygons(component, loops, center, u, v)
    if not polygons:
        return [], {
            "outer_loop_count": 0,
            "inner_loop_count": 0,
            "plane_residual": plane_residual,
            "boundary_recovery": "EMPTY_AFTER_REPAIR",
        }

    polygons.sort(key=lambda item: float(item.area), reverse=True)
    parents: list[int | None] = [None] * len(polygons)
    for index, polygon in enumerate(polygons):
        representative = polygon.representative_point()
        for candidate in range(index):
            if polygons[candidate].covers(representative):
                parents[index] = candidate
                break

    depths: list[int] = []
    for index in range(len(polygons)):
        depth = 0
        parent = parents[index]
        while parent is not None:
            depth += 1
            parent = parents[parent]
        depths.append(depth)

    def to_world(uv_points: np.ndarray) -> np.ndarray:
        local_points = center + np.outer(uv_points[:, 0], u) + np.outer(uv_points[:, 1], v)
        return _world_points(local_points, frame)

    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace

    faces: list[Any] = []
    outer_count = 0
    inner_count = 0
    for index, polygon in enumerate(polygons):
        if depths[index] % 2:
            continue
        outer_xy = np.asarray(polygon.exterior.coords[:-1], dtype=float)
        if len(outer_xy) < 3:
            continue
        if _signed_area(outer_xy) < 0:
            outer_xy = outer_xy[::-1]
        maker = BRepBuilderAPI_MakeFace(_wire(to_world(outer_xy)), True)
        local_inner_count = 0
        inner_rings = [
            np.asarray(ring.coords[:-1], dtype=float)
            for ring in polygon.interiors
        ]
        inner_rings.extend(
            np.asarray(child.exterior.coords[:-1], dtype=float)
            for child, parent, depth in zip(polygons, parents, depths)
            if parent == index and depth % 2 == 1
        )
        for inner_xy in inner_rings:
            if len(inner_xy) < 3 or abs(_signed_area(inner_xy)) < 1e-10:
                continue
            if _signed_area(inner_xy) > 0:
                inner_xy = inner_xy[::-1]
            maker.Add(_wire(to_world(inner_xy)))
            local_inner_count += 1
        maker.Build()
        if not maker.IsDone():
            continue
        faces.append(maker.Face())
        outer_count += 1
        inner_count += local_inner_count

    return faces, {
        "outer_loop_count": outer_count,
        "inner_loop_count": inner_count,
        "source_loop_count": len(loops),
        "plane_residual": plane_residual,
        "boundary_recovery": "SOURCE_TRIMMED",
    }


def _face_components(
    local_mesh: trimesh.Trimesh,
    face_ids: np.ndarray,
) -> list[np.ndarray]:
    from trimesh.graph import connected_components

    face_ids = np.asarray(face_ids, dtype=np.int64)
    adjacency = np.asarray(local_mesh.face_adjacency, dtype=np.int64)
    if not len(adjacency):
        return [face_ids]
    selected = np.isin(adjacency[:, 0], face_ids) & np.isin(adjacency[:, 1], face_ids)
    components = connected_components(
        adjacency[selected],
        nodes=face_ids,
        min_len=1,
    )
    return [np.asarray(component, dtype=np.int64) for component in components]


def _wire(points: np.ndarray) -> Any:
    return v3_builders._wire(points)


def _shape_counts(shape: Any) -> dict[str, Any]:
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer

    counts = {}
    for label, shape_type in (
        ("EDGE_COUNT", TopAbs_EDGE),
        ("FACE_COUNT", TopAbs_FACE),
        ("SHELL_COUNT", TopAbs_SHELL),
        ("SOLID_COUNT", TopAbs_SOLID),
    ):
        explorer = TopExp_Explorer(shape, shape_type)
        count = 0
        while explorer.More():
            count += 1
            explorer.Next()
        counts[label] = count
    if counts["SOLID_COUNT"]:
        topology_type = "SOLID"
    elif counts["SHELL_COUNT"]:
        topology_type = "OPENSHELL"
    elif counts["FACE_COUNT"]:
        topology_type = "FACESET"
    else:
        topology_type = "UNKNOWN"
    counts["BREP_TOPOLOGY_TYPE"] = topology_type
    return counts


def _plane_polygon(submesh: trimesh.Trimesh) -> tuple[np.ndarray, float]:
    points = np.asarray(submesh.vertices, dtype=float)
    center = points.mean(axis=0)
    _, singular, axes = np.linalg.svd(points - center, full_matrices=False)
    u, v, normal = axes[0], axes[1], axes[2]
    uv = np.column_stack(((points - center) @ u, (points - center) @ v))
    sample_step = max(1, len(uv) // 5000)
    sampled = uv[::sample_step]
    hull = ConvexHull(sampled)
    profile = sampled[hull.vertices]
    local = center + np.outer(profile[:, 0], u) + np.outer(profile[:, 1], v)
    triangle_area = 0.0
    for face in np.asarray(submesh.faces, dtype=np.int64):
        tri = points[face]
        triangle_area += 0.5 * float(np.linalg.norm(np.cross(tri[1] - tri[0], tri[2] - tri[0])))
    hull_area = float(hull.volume)
    convexity_overfill = max(0.0, hull_area / max(triangle_area, 1e-12) - 1.0)
    return local, float(convexity_overfill)


def _normal_patch_submeshes(local_mesh: trimesh.Trimesh) -> list[trimesh.Trimesh]:
    normals = np.asarray(local_mesh.face_normals, dtype=float)
    if not len(normals):
        return []
    quantized = np.round(normals, 1)
    unique, counts = np.unique(quantized, axis=0, return_counts=True)
    order = np.argsort(counts)[::-1]
    minimum_faces = max(2, int(len(normals) * 0.001))
    minimum_area = max(float(local_mesh.area) * 2.5e-4, 1e-5)
    patches: list[trimesh.Trimesh] = []
    assigned = np.zeros(len(normals), dtype=bool)
    for index in order:
        if counts[index] < minimum_faces:
            continue
        reference = unique[index] / max(float(np.linalg.norm(unique[index])), 1e-12)
        # Signed normals are intentional: opposite sides must not share one trim.
        similarity = normals @ reference
        face_ids = np.flatnonzero(similarity >= 0.96)
        face_ids = face_ids[~assigned[face_ids]]
        if len(face_ids) < minimum_faces:
            continue
        assigned[face_ids] = True
        for component_faces in _face_components(local_mesh, face_ids):
            submesh = local_mesh.submesh([component_faces], append=True, repair=False)
            component = submesh
            if float(component.area) >= minimum_area:
                patches.append(component)
    patches.sort(key=lambda item: float(item.area), reverse=True)
    return patches[:96]


def trimmed_planar_face(
    local_mesh: trimesh.Trimesh,
    frame: dict[str, Any],
) -> dict[str, Any]:
    result = v3_builders.planar_face(local_mesh, frame)
    result["parameters"] = {
        **result.get("parameters", {}),
        "builder_type": "TRIMMED_PLANAR_FACE",
        "representation": "TRIMMED_ANALYTIC_PLANAR_FACE",
    }
    return result


def multi_patch_surface(
    local_mesh: trimesh.Trimesh,
    frame: dict[str, Any],
    topology: dict[str, Any],
) -> dict[str, Any]:
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    faces = []
    patch_parameters = []
    patches = _normal_patch_submeshes(local_mesh)
    for patch_index, patch in enumerate(patches):
        patch_faces, trim_info = _trimmed_component_faces(patch, frame)
        for face_index, face in enumerate(patch_faces):
            faces.append(face)
            patch_parameters.append({
                "patch_index": patch_index,
                "face_index": face_index,
                "triangle_count": int(len(patch.faces)),
                "convexity_overfill_ratio": None,
                "representation": "TRIMMED_PLANE_PATCH",
                **trim_info,
            })
    if not faces:
        raise ValueError("MULTI_PATCH_SURFACE_NO_ANALYTIC_PATCH")
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for face in faces:
        builder.Add(compound, face)
    return {
        "shape": compound,
        "parameters": {
            "builder_type": "MULTI_PATCH_SURFACE",
            "representation": "ANALYTIC_PLANAR_FACESET",
            "patch_count": len(faces),
            "source_component_count": len(patches),
            "negative_space_regions_recovered": int(
                sum(item.get("inner_loop_count", 0) for item in patch_parameters)
            ),
            "patches": patch_parameters,
            "topology_class": topology.get("topology_class"),
        },
    }


def _station_wire(
    local_mesh: trimesh.Trimesh,
    station: float,
    axis_index: int = 2,
) -> tuple[Any, float]:
    points = np.asarray(local_mesh.vertices, dtype=float)
    mask = np.abs(points[:, axis_index] - station) <= max(float(np.ptp(points[:, axis_index])) * 0.10, 1e-5)
    if int(mask.sum()) < 30:
        order = np.argsort(np.abs(points[:, axis_index] - station))
        mask = np.zeros(len(points), dtype=bool)
        mask[order[: min(4000, len(points))]] = True
    other = [index for index in range(3) if index != axis_index]
    uv = points[mask][:, other]
    if len(uv) < 3:
        raise ValueError("SECTION_TOO_FEW_POINTS")
    hull = ConvexHull(uv)
    profile = uv[hull.vertices]
    local = np.zeros((len(profile), 3), dtype=float)
    local[:, other] = profile
    local[:, axis_index] = station
    convexity = max(0.0, float(hull.volume) / max(float(np.ptp(uv, axis=0).prod()), 1e-12) - 1.0)
    return _wire(local), convexity


def ruled_surface(
    local_mesh: trimesh.Trimesh,
    frame: dict[str, Any],
    topology: dict[str, Any],
) -> dict[str, Any]:
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

    axis_index = 2
    low, high = np.asarray(local_mesh.vertices).min(axis=0)[axis_index], np.asarray(local_mesh.vertices).max(axis=0)[axis_index]
    first, convexity_first = _station_wire(local_mesh, float(low + 0.08 * (high - low)), axis_index)
    second, convexity_second = _station_wire(local_mesh, float(high - 0.08 * (high - low)), axis_index)
    if max(convexity_first, convexity_second) > 0.12:
        raise ValueError("CONVEXITY_OVERFILL_RULED_PROFILE")
    loft = BRepOffsetAPI_ThruSections(False, True, 1e-5)
    loft.CheckCompatibility(False)
    loft.AddWire(_wire(_world_points(_wire_points(first), frame)))
    loft.AddWire(_wire(_world_points(_wire_points(second), frame)))
    loft.Build()
    if not loft.IsDone():
        raise ValueError("RULED_SURFACE_BUILD_FAILED")
    return {
        "shape": loft.Shape(),
        "parameters": {
            "builder_type": "RULED_SURFACE",
            "representation": "OCC_RULED_SURFACE",
            "topology_class": topology.get("topology_class"),
            "axis_index": axis_index,
            "station_min": float(low),
            "station_max": float(high),
        },
    }


def _wire_points(wire: Any) -> np.ndarray:
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    points = []
    explorer = TopExp_Explorer(wire, TopAbs_VERTEX)
    while explorer.More():
        vertex = TopoDS.Vertex_s(explorer.Current())
        points.append(list(BRep_Tool.Pnt_s(vertex).Coord()))
        explorer.Next()
    return np.asarray(points, dtype=float)


def loft_surface(
    local_mesh: trimesh.Trimesh,
    frame: dict[str, Any],
    topology: dict[str, Any],
) -> dict[str, Any]:
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

    points = np.asarray(local_mesh.vertices, dtype=float)
    low, high = float(points[:, 2].min()), float(points[:, 2].max())
    stations = np.linspace(low + 0.08 * (high - low), high - 0.08 * (high - low), 4)
    wires = []
    convexities = []
    for station in stations:
        wire, convexity = _station_wire(local_mesh, float(station), 2)
        wires.append(_wire(_world_points(_wire_points(wire), frame)))
        convexities.append(convexity)
    if max(convexities) > 0.12:
        raise ValueError("CONVEXITY_OVERFILL_LOFT_PROFILE")
    loft = BRepOffsetAPI_ThruSections(False, False, 1e-5)
    loft.CheckCompatibility(False)
    for wire in wires:
        loft.AddWire(wire)
    loft.Build()
    if not loft.IsDone():
        raise ValueError("LOFT_SURFACE_BUILD_FAILED")
    return {
        "shape": loft.Shape(),
        "parameters": {
            "builder_type": "LOFT_SURFACE",
            "representation": "OCC_LOFT_SURFACE",
            "topology_class": topology.get("topology_class"),
            "station_count": len(stations),
            "stations": stations.tolist(),
            "convexity_overfill": convexities,
        },
    }


def build_family(
    family: str,
    local_mesh: trimesh.Trimesh,
    frame: dict[str, Any],
    topology: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    if family == "TRIMMED_PLANAR_FACE":
        result = trimmed_planar_face(local_mesh, frame)
    elif family == "MULTI_PATCH_SURFACE":
        result = multi_patch_surface(local_mesh, frame, topology)
    elif family == "RULED_SURFACE":
        result = ruled_surface(local_mesh, frame, topology)
    elif family == "LOFT_SURFACE":
        result = loft_surface(local_mesh, frame, topology)
    else:
        raise ValueError("NO_SUPPORTED_BUILDER:" + family)
    occ_valid = v3_builders.validate_shape(result["shape"])
    if occ_valid and not v3_builders.write_step(result["shape"], output):
        raise ValueError("STEP_WRITE_FAILED")
    parameters = {
        **result.get("parameters", {}),
        **_shape_counts(result["shape"]),
    }
    return {
        "valid": occ_valid,
        "step_path": str(output) if occ_valid else None,
        "parameters": parameters,
        "builder_type": family,
    }
