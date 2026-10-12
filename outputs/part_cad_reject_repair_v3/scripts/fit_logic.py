"""Pure fitting/occupancy utilities copied from historical pipeline; no historical module imported.
Voxel occupancy is approximate majority-axis scan-fill, not exact volumetric IoU.
"""

from typing import Any

import numpy as np

def normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n <= 1e-15:
        raise ValueError("zero vector")
    return np.asarray(v, float) / n

def basis_for_axis(axis: np.ndarray) -> np.ndarray:
    z = normalize(axis)
    ref = np.array([1.0, 0.0, 0.0]) if abs(z[0]) < 0.8 else np.array([0.0, 1.0, 0.0])
    x = normalize(np.cross(ref, z))
    y = normalize(np.cross(z, x))
    return np.column_stack([x, y, z])

def candidate_axes(mesh) -> list[np.ndarray]:
    v = np.asarray(mesh.vertices, float)
    center = v.mean(axis=0)
    _, _, vh = np.linalg.svd(v - center, full_matrices=False)
    raw = [np.eye(3)[i] for i in range(3)] + [vh[i] for i in range(3)]
    areas = np.asarray(mesh.area_faces)
    normals = np.asarray(mesh.face_normals)
    scored = []
    for a in raw:
        a = normalize(a)
        if a[np.argmax(np.abs(a))] < 0:
            a = -a
        if any(abs(float(np.dot(a, b))) > 0.995 for _, b in scored):
            continue
        dot = np.abs(normals @ a)
        cap = float(areas[dot > 0.94].sum() / max(areas.sum(), 1e-15))
        side = float(areas[dot < 0.16].sum() / max(areas.sum(), 1e-15))
        local = (v - center) @ basis_for_axis(a)
        ext = np.ptp(local, axis=0)
        compact = float(min(ext[0], ext[1]) / max(max(ext[0], ext[1]), 1e-15))
        score = 1.8 * min(cap * 2.0, 1.0) + side + 0.15 * compact
        scored.append((score, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored]

def projected_profile(mesh, axis: np.ndarray, max_entities: int = 192) -> dict[str, Any]:
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    v = np.asarray(mesh.vertices, float)
    center = np.asarray(mesh.bounds).mean(axis=0)
    B = basis_for_axis(axis)
    local = (v - center) @ B
    triangles = local[np.asarray(mesh.faces), :2]
    polys = []
    for tri in triangles:
        p = Polygon(tri)
        if p.is_valid and p.area > 1e-18:
            polys.append(p)
    if not polys:
        raise ValueError("no valid projected triangles")
    geom = unary_union(polys)
    if not geom.is_valid:
        geom = geom.buffer(0)
    if geom.is_empty:
        raise ValueError("empty projected union")
    # Edge-on triangles have zero projected area and can otherwise make a
    # profile miss a true extreme.  Affinely match the retained silhouette to
    # the exact projected bounds (no independent CAD/source normalization; the
    # resulting profile is still constructed directly in the source frame).
    gb = np.asarray(geom.bounds, float)
    exact_min = local[:, :2].min(axis=0)
    exact_max = local[:, :2].max(axis=0)
    gspan = np.maximum(gb[2:] - gb[:2], 1e-15)
    exact_span = exact_max - exact_min
    from shapely.affinity import affine_transform
    sx, sy = exact_span / gspan
    geom = affine_transform(geom, [sx, 0.0, 0.0, sy, exact_min[0] - sx * gb[0], exact_min[1] - sy * gb[1]])
    span = float(max(np.ptp(local[:, 0]), np.ptp(local[:, 1])))
    tol = max(span * 2e-4, 1e-10)
    for _ in range(9):
        simp = geom.simplify(tol, preserve_topology=True)
        geoms = list(simp.geoms) if simp.geom_type == "MultiPolygon" else [simp]
        entities = sum(len(g.exterior.coords) - 1 + sum(len(h.coords) - 1 for h in g.interiors) for g in geoms)
        if entities <= max_entities:
            geom = simp
            break
        tol *= 1.7
    geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    min_area = max(float(geom.area) * 1e-6, 1e-18)
    profiles = []
    for g in geoms:
        if g.area < min_area:
            continue
        outer = np.asarray(g.exterior.coords[:-1], float)
        holes = [np.asarray(h.coords[:-1], float) for h in g.interiors if Polygon(h).area >= min_area]
        profiles.append({"outer": outer.tolist(), "holes": [h.tolist() for h in holes]})
    if not profiles:
        raise ValueError("no retained profile polygons")
    return {
        "kind": "extrusion", "center": center.tolist(), "basis": B.tolist(), "axis": B[:, 2].tolist(),
        "zmin": float(local[:, 2].min()), "zmax": float(local[:, 2].max()), "profiles": profiles,
        "simplify_tolerance": tol, "sketch_entity_count": entities,
    }

def _scan_fill(surface: np.ndarray, axis: int) -> np.ndarray:
    moved = np.moveaxis(surface, axis, 0)
    n = moved.shape[0]
    any_hit = moved.any(axis=0)
    first = np.argmax(moved, axis=0)
    last = n - 1 - np.argmax(moved[::-1], axis=0)
    idx = np.arange(n, dtype=np.int32).reshape((n,) + (1,) * (moved.ndim - 1))
    filled = (idx >= first[None, ...]) & (idx <= last[None, ...]) & any_hit[None, ...]
    return np.moveaxis(filled, 0, axis)

def voxel_occupancy(mesh, bmin: np.ndarray, pitch: float, shape: tuple[int, int, int]) -> np.ndarray:
    """Uniform non-watertight-tolerant occupancy on one explicitly shared grid.

    Surface triangles are rasterized after the same world-to-grid transform.
    Interior is the majority vote of X/Y/Z scan fills, unioned with the exact
    surface and a final 3-D hole fill.  This treats open sheets conservatively
    (one-voxel occupancy) while filling volumes supported along >=2 axes.
    """
    from scipy.ndimage import binary_fill_holes

    work = mesh.copy()
    work.vertices = (np.asarray(work.vertices, float) - bmin) / pitch
    vox = work.voxelized(pitch=1.0, method="subdivide")
    pts = np.asarray(vox.points)
    if not len(pts):
        raise ValueError("empty surface voxelization")
    ids = np.round(pts).astype(np.int64)
    keep = np.all((ids >= 0) & (ids < np.asarray(shape)), axis=1)
    ids = ids[keep]
    surface = np.zeros(shape, dtype=bool)
    surface[ids[:, 0], ids[:, 1], ids[:, 2]] = True
    fills = [_scan_fill(surface, axis=i) for i in range(3)]
    majority = (fills[0].astype(np.uint8) + fills[1].astype(np.uint8) + fills[2].astype(np.uint8)) >= 2
    return binary_fill_holes(surface | majority)
