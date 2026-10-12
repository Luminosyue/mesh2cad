"""Generic 2D section boundary recovery: bounded slab, robust filter, alpha/concave hull.

Convex hull is a last-resort fallback. Callers must not inflate contours to close a wire.
"""
from __future__ import annotations

from typing import Any

import numpy as np

import generic_cad_profiles as gp


MAX_SLICE_TO_SPACING = 0.45


def robust_filter_uv(uv: np.ndarray, k: int = 6) -> dict[str, Any]:
    pts = np.unique(np.asarray(uv, dtype=float), axis=0)
    before = int(len(pts))
    if before < 8:
        return {"points": pts, "POINTS_BEFORE_FILTER": before, "POINTS_AFTER_FILTER": before, "OUTLIER_RATIO": 0.0}
    from scipy.spatial import cKDTree

    tree = cKDTree(pts)
    kk = min(max(k, 3), before)
    nn = tree.query(pts, k=kk)[0]
    local_d = nn[:, 1:].mean(axis=1) if nn.ndim == 2 else nn
    med = float(np.median(local_d))
    mad = float(np.median(np.abs(local_d - med)))
    scale = 1.4826 * mad if mad > 1e-12 else max(med, 1e-9)
    keep = local_d <= med + 3.8 * scale
    c = np.median(pts, axis=0)
    rad = np.linalg.norm(pts - c, axis=1)
    r_med = float(np.median(rad))
    r_mad = float(np.median(np.abs(rad - r_med)))
    r_scale = 1.4826 * r_mad if r_mad > 1e-12 else max(r_med, 1e-9)
    keep = keep & (rad <= r_med + 4.2 * r_scale)
    if int(keep.sum()) < max(5, before // 4):
        keep = np.ones(before, dtype=bool)
    after = pts[keep]
    return {
        "points": after,
        "POINTS_BEFORE_FILTER": before,
        "POINTS_AFTER_FILTER": int(len(after)),
        "OUTLIER_RATIO": float(1.0 - len(after) / max(before, 1)),
    }


def _triangle_circumradius(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ab = float(np.linalg.norm(a - b))
    bc = float(np.linalg.norm(b - c))
    ca = float(np.linalg.norm(c - a))
    area2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
    if area2 <= 1e-18:
        return 1e9
    return float(ab * bc * ca / max(area2, 1e-18))


def alpha_shape_boundary(uv: np.ndarray, alpha: float | None = None) -> np.ndarray | None:
    pts = np.unique(np.asarray(uv, dtype=float), axis=0)
    if len(pts) < 4:
        return None
    from scipy.spatial import Delaunay

    try:
        tri = Delaunay(pts)
    except Exception:
        return None
    simplices = np.asarray(tri.simplices, dtype=np.int64)
    if alpha is None:
        edges = []
        for a, b, c in simplices:
            edges.extend(
                [
                    float(np.linalg.norm(pts[a] - pts[b])),
                    float(np.linalg.norm(pts[b] - pts[c])),
                    float(np.linalg.norm(pts[c] - pts[a])),
                ]
            )
        alpha = float(np.median(edges) * 2.4) if edges else 1.0
    kept = []
    for simplex in simplices:
        a, b, c = pts[simplex]
        if _triangle_circumradius(a, b, c) <= alpha:
            kept.append(tuple(sorted((int(simplex[0]), int(simplex[1])))))
            kept.append(tuple(sorted((int(simplex[1]), int(simplex[2])))))
            kept.append(tuple(sorted((int(simplex[2]), int(simplex[0])))))
    if not kept:
        return None
    uniq, counts = np.unique(np.asarray(kept, dtype=np.int64), axis=0, return_counts=True)
    boundary = uniq[counts == 1]
    if len(boundary) < 3:
        return None
    span = float(np.ptp(pts, axis=0).max()) or 1.0
    segs = [(pts[int(i)], pts[int(j)]) for i, j in boundary]
    loops = gp.chain_segments(segs, tol=max(1e-8, span * 1e-4))
    if not loops:
        return None
    return gp.ensure_ccw(loops[0])


def concave_boundary(uv: np.ndarray) -> np.ndarray | None:
    pts = np.asarray(uv, dtype=float)
    if len(pts) < 4:
        return None
    from scipy.spatial import cKDTree

    tree = cKDTree(pts)
    nn = tree.query(pts, k=min(4, len(pts)))[0]
    med = float(np.median(nn[:, 1] if nn.ndim == 2 else nn))
    alpha = max(med * 2.6, float(np.ptp(pts, axis=0).max()) * 0.08)
    return alpha_shape_boundary(pts, alpha=alpha)


def slab_intersection_uv(local: np.ndarray, faces: np.ndarray | None, x: float, half: float) -> np.ndarray:
    local = np.asarray(local, dtype=float)
    hits: list[np.ndarray] = []
    planes = np.linspace(float(x) - half, float(x) + half, 5) if half > 1e-10 else np.array([float(x)])
    if faces is not None and len(faces):
        for xi in planes:
            for loop in gp.mesh_section_loops(local, faces, float(xi)):
                hits.extend(list(loop))
    band = local[np.abs(local[:, 0] - float(x)) <= max(half, 1e-12)]
    if len(band):
        hits.extend(list(band[:, 1:3]))
    if not hits:
        return np.zeros((0, 2))
    return np.unique(np.asarray(hits, dtype=float), axis=0)


def recover_section_boundary(
    local: np.ndarray,
    faces: np.ndarray | None,
    x: float,
    thickness: float = 0.0,
    section_spacing: float | None = None,
) -> dict[str, Any]:
    local = np.asarray(local, dtype=float)
    axial_span = float(np.ptp(local[:, 0])) or 1.0
    spacing = float(section_spacing) if section_spacing and section_spacing > 0 else max(axial_span / 24.0, 1e-6)
    requested = max(float(thickness), 0.0)
    max_half = min(max(requested, 1e-9), MAX_SLICE_TO_SPACING * spacing, 0.04 * axial_span)
    loops = gp.mesh_section_loops(local, faces, float(x))
    method = "MESH_PLANE_LOOP"
    outer = loops[0] if loops else np.zeros((0, 2))
    inners = loops[1:] if len(loops) > 1 else []
    selected = np.zeros((0, 2))
    if len(outer) >= 3:
        selected = np.asarray(outer, dtype=float)
        filt = {"POINTS_BEFORE_FILTER": int(len(selected)), "POINTS_AFTER_FILTER": int(len(selected)), "OUTLIER_RATIO": 0.0, "points": selected}
        half_used = 0.0
        axial_selected = 0.0
    else:
        half_used = max_half
        selected = slab_intersection_uv(local, faces, float(x), half_used)
        if len(selected) < 5:
            half_used = min(MAX_SLICE_TO_SPACING * spacing, 0.04 * axial_span, max(half_used, 1e-9))
            selected = slab_intersection_uv(local, faces, float(x), half_used)
        filt = robust_filter_uv(selected)
        selected = filt["points"]
        alpha_loop = alpha_shape_boundary(selected) if len(selected) >= 4 else None
        concave = None if alpha_loop is not None else concave_boundary(selected)
        if alpha_loop is not None and len(alpha_loop) >= 3:
            outer = alpha_loop
            method = "ALPHA_SHAPE"
        elif concave is not None and len(concave) >= 3:
            outer = concave
            method = "CONCAVE_HULL"
        elif len(selected) >= 3:
            outer = gp.convex_hull_uv(selected)
            method = "CONVEX_HULL_FALLBACK"
        else:
            outer = np.zeros((0, 2))
            method = "UNKNOWN"
        inners = []
        band = local[np.abs(local[:, 0] - float(x)) <= max(half_used, 1e-12)]
        axial_selected = float(np.ptp(band[:, 0])) if len(band) else 0.0
    if len(outer) >= 3:
        outer = gp.ensure_ccw(np.asarray(outer, dtype=float))
    measured_centroid = outer.mean(axis=0) if len(outer) >= 3 else (
        selected.mean(axis=0) if len(selected) else np.zeros(2)
    )
    desc = gp.profile_descriptor(outer, inners)
    desc["section_position"] = float(x)
    desc["measured_section_centroid_2d"] = np.asarray(measured_centroid, dtype=float).tolist()
    if len(outer) >= 3:
        samples = np.asarray(desc.get("boundary_2d") or gp.resample_closed(outer), dtype=float)
        samples = samples - samples.mean(axis=0) + np.asarray(measured_centroid, dtype=float)
        desc["boundary_2d"] = samples.tolist()
        desc["centroid_2d"] = np.asarray(measured_centroid, dtype=float).tolist()
    desc["PROFILE_BOUNDARY_METHOD"] = method
    desc["profile_source_method"] = method
    desc["PROFILE_OUTWARD_OFFSET"] = 0.0
    desc["loop_count"] = int(len(loops)) if loops else (1 if len(outer) >= 3 else 0)
    desc["OUTER_LOOP"] = desc.get("boundary_2d") or []
    desc["INNER_LOOP_EVIDENCE"] = bool(inners)
    desc["POINTS_BEFORE_FILTER"] = int(filt.get("POINTS_BEFORE_FILTER") or 0) if len(outer) >= 3 else int(len(selected))
    desc["POINTS_AFTER_FILTER"] = int(filt.get("POINTS_AFTER_FILTER") or len(outer))
    desc["OUTLIER_RATIO"] = float(filt.get("OUTLIER_RATIO") or 0.0)
    desc["slice_half_thickness"] = float(half_used if len(loops) < 1 or len((loops[0] if loops else [])) < 3 else 0.0)
    desc["SECTION_SELECTED_AXIAL_SPAN"] = float(axial_selected if "axial_selected" in locals() else 0.0)
    desc["SECTION_TARGET_SPACING"] = float(spacing)
    desc["SLICE_SPAN_TO_SECTION_SPACING_RATIO"] = float(
        (desc["SECTION_SELECTED_AXIAL_SPAN"] / spacing) if spacing > 1e-12 else 0.0
    )
    desc["source_point_count"] = int(desc.get("point_count") or 0)
    return desc
