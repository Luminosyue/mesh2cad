"""2D section profiles, correspondence, and inner-loop evidence.

Sections store a full contour, not a scalar radius. MAC never writes the
final metric profile; this module measures it from COMPONENT_LOCAL geometry.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np


PROFILE_SAMPLE_COUNT = 32


def polygon_area(pts: np.ndarray) -> float:
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 3:
        return 0.0
    closed = np.vstack([pts, pts[0]])
    return float(0.5 * np.abs(np.sum(closed[:-1, 0] * closed[1:, 1] - closed[1:, 0] * closed[:-1, 1])))


def polygon_perimeter(pts: np.ndarray) -> float:
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 2:
        return 0.0
    closed = np.vstack([pts, pts[0]])
    return float(np.sum(np.linalg.norm(np.diff(closed, axis=0), axis=1)))


def signed_area(pts: np.ndarray) -> float:
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 3:
        return 0.0
    closed = np.vstack([pts, pts[0]])
    return float(0.5 * np.sum(closed[:-1, 0] * closed[1:, 1] - closed[1:, 0] * closed[:-1, 1]))


def ensure_ccw(pts: np.ndarray) -> np.ndarray:
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 3:
        return pts
    if signed_area(pts) < 0:
        return pts[::-1].copy()
    return pts


def convex_hull_uv(uv: np.ndarray) -> np.ndarray:
    uv = np.unique(np.asarray(uv, dtype=float), axis=0)
    if len(uv) < 3:
        return uv
    from scipy.spatial import ConvexHull

    hull = ConvexHull(uv)
    return ensure_ccw(uv[hull.vertices])


def rectangularity(pts: np.ndarray) -> float:
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 4:
        return 0.0
    ext = np.ptp(pts, axis=0)
    box_area = float(max(ext[0], 1e-12) * max(ext[1], 1e-12))
    return float(np.clip(polygon_area(pts) / box_area, 0.0, 1.0))


def circularity(pts: np.ndarray) -> float:
    area = polygon_area(pts)
    peri = polygon_perimeter(pts)
    return float(4.0 * math.pi * area / max(peri * peri, 1e-12))


def classify_profile(pts: np.ndarray) -> str:
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 3:
        return "UNKNOWN"
    circ = circularity(pts)
    rect = rectangularity(pts)
    ext = np.ptp(pts, axis=0)
    aspect = float(max(ext) / max(min(ext), 1e-12))
    hull = convex_hull_uv(pts)
    corners = int(len(hull))
    if circ >= 0.90 and aspect <= 1.18:
        return "CIRCLE"
    if circ >= 0.80 and aspect > 1.18:
        return "ELLIPSE"
    if rect >= 0.82 and aspect >= 1.15 and 4 <= corners <= 6:
        return "RECTANGLE"
    if corners == 3 or (corners <= 4 and rect < 0.75 and aspect >= 1.2 and circ < 0.75):
        return "TRIANGLE" if corners == 3 else "SIMPLE_POLYGON"
    if 4 <= corners <= 8 and circ < 0.85:
        return "SIMPLE_POLYGON"
    if circ < 0.75:
        return "GENERAL_POLYGON"
    return "GENERAL_POLYGON"


def resample_closed(points: np.ndarray, count: int = PROFILE_SAMPLE_COUNT) -> np.ndarray:
    points = ensure_ccw(np.asarray(points, dtype=float))
    if len(points) < 3:
        return points
    closed = np.vstack([points, points[0]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(s[-1]) or 1.0
    samples = np.linspace(0.0, total, count, endpoint=False)
    out = []
    for t in samples:
        k = int(np.searchsorted(s, t, side="right") - 1)
        k = min(max(k, 0), len(closed) - 2)
        span = s[k + 1] - s[k] if s[k + 1] > s[k] else 1.0
        a = (t - s[k]) / span
        out.append((1 - a) * closed[k] + a * closed[k + 1])
    return np.asarray(out, dtype=float)


def cyclic_align(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    """Order-only correspondence. Matching may center/scale; metric inverse is mandatory."""
    import generic_cad_profile_metric_calibration as pmc

    return pmc.cyclic_align_metric(reference, candidate)


def align_profile_sequence(profiles: list[np.ndarray]) -> dict[str, Any]:
    import generic_cad_profile_metric_calibration as pmc

    return pmc.align_profile_sequence_metric(profiles)


def _key_uv(p: np.ndarray, scale: float) -> tuple[int, int]:
    return (int(round(float(p[0]) / scale)), int(round(float(p[1]) / scale)))


def chain_segments(segments: list[tuple[np.ndarray, np.ndarray]], tol: float) -> list[np.ndarray]:
    if not segments:
        return []
    scale = max(tol, 1e-8)
    unused = []
    for a, b in segments:
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        if np.linalg.norm(a - b) < scale:
            continue
        unused.append((a, b))
    loops: list[np.ndarray] = []
    while unused:
        start_a, start_b = unused.pop()
        poly = [start_a, start_b]
        closed = False
        progressed = True
        while progressed and not closed:
            progressed = False
            head = poly[-1]
            for i, (a, b) in enumerate(unused):
                if np.linalg.norm(a - head) <= 4 * scale:
                    poly.append(b)
                    unused.pop(i)
                    progressed = True
                    break
                if np.linalg.norm(b - head) <= 4 * scale:
                    poly.append(a)
                    unused.pop(i)
                    progressed = True
                    break
            if len(poly) >= 4 and np.linalg.norm(poly[-1] - poly[0]) <= 6 * scale:
                closed = True
        pts = np.asarray(poly, dtype=float)
        if closed and len(pts) >= 4:
            if np.linalg.norm(pts[0] - pts[-1]) < 8 * scale:
                pts = pts[:-1]
            loops.append(ensure_ccw(pts))
    loops.sort(key=polygon_area, reverse=True)
    return loops


def mesh_section_loops(local: np.ndarray, faces: np.ndarray | None, x: float) -> list[np.ndarray]:
    """Intersect the mesh with plane x=const and reconstruct 2D closed loops."""
    local = np.asarray(local, dtype=float)
    if faces is None or len(faces) == 0:
        return []
    faces = np.asarray(faces, dtype=np.int64)
    segments: list[tuple[np.ndarray, np.ndarray]] = []
    span = float(np.ptp(local[:, 1:3])) or 1.0
    for tri in faces:
        pts = local[tri]
        hits: list[np.ndarray] = []
        for i in range(3):
            a = pts[i]
            b = pts[(i + 1) % 3]
            da = a[0] - x
            db = b[0] - x
            if da * db > 0 and abs(da) > 1e-12 and abs(db) > 1e-12:
                continue
            denom = a[0] - b[0]
            if abs(denom) <= 1e-14:
                if abs(da) <= 1e-10:
                    hits.append(a[1:3].copy())
                continue
            t = da / (da - db)
            if -1e-6 <= t <= 1.0 + 1e-6:
                p = a + t * (b - a)
                hits.append(p[1:3].copy())
        if len(hits) == 2:
            segments.append((hits[0], hits[1]))
        elif len(hits) > 2:
            uniq = []
            for h in hits:
                if not uniq or min(np.linalg.norm(h - u) for u in uniq) > 1e-10:
                    uniq.append(h)
            if len(uniq) >= 2:
                segments.append((uniq[0], uniq[1]))
    loops = chain_segments(segments, tol=max(1e-6, span * 1e-4))
    return [lp for lp in loops if len(lp) >= 3 and polygon_area(lp) > 1e-16]


def profile_descriptor(uv: np.ndarray, inner_loops: list[np.ndarray] | None = None) -> dict[str, Any]:
    uv = np.asarray(uv, dtype=float)
    if len(uv) < 3:
        return {
            "profile_type": "UNKNOWN",
            "point_count": int(len(uv)),
            "area": 0.0,
            "perimeter": 0.0,
            "width": 0.0,
            "height": 0.0,
            "aspect_ratio": 1.0,
            "circularity": 0.0,
            "rectangularity": 0.0,
            "centroid_2d": [0.0, 0.0],
            "boundary_2d": [],
            "convex_hull": [],
            "corner_evidence": 0,
            "inner_loop_evidence": bool(inner_loops),
            "inner_loop_count": len(inner_loops or []),
        }
    hull = convex_hull_uv(uv)
    ext = np.ptp(uv, axis=0)
    centroid = uv.mean(axis=0)
    samples = resample_closed(uv, PROFILE_SAMPLE_COUNT)
    return {
        "profile_type": classify_profile(uv),
        "point_count": int(len(uv)),
        "area": polygon_area(uv),
        "perimeter": polygon_perimeter(uv),
        "width": float(ext[0]),
        "height": float(ext[1]),
        "aspect_ratio": float(max(ext) / max(min(ext), 1e-12)),
        "circularity": circularity(uv),
        "rectangularity": rectangularity(uv),
        "centroid_2d": centroid.tolist(),
        "boundary_2d": samples.tolist(),
        "convex_hull": hull.tolist(),
        "corner_evidence": int(len(hull)),
        "inner_loop_evidence": bool(inner_loops),
        "inner_loop_count": int(len(inner_loops or [])),
        "inner_loops_2d": [resample_closed(lp, PROFILE_SAMPLE_COUNT).tolist() for lp in (inner_loops or [])[:4]],
    }


def extract_section_profile(
    local: np.ndarray,
    faces: np.ndarray | None,
    x: float,
    thickness: float = 0.0,
    section_spacing: float | None = None,
) -> dict[str, Any]:
    from generic_cad_section_boundary import recover_section_boundary

    return recover_section_boundary(local, faces, x, thickness=thickness, section_spacing=section_spacing)


def circle_samples(center: np.ndarray, radius: float, count: int = PROFILE_SAMPLE_COUNT) -> np.ndarray:
    ang = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    return np.stack([center[0] + radius * np.cos(ang), center[1] + radius * np.sin(ang)], axis=1)


def interpolate_profiles(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    import generic_cad_transition_calibration as tc

    packed = tc.transition_profiles(a, b, count=2)
    start, end = packed["profiles"][0], packed["profiles"][-1]
    uv = (1.0 - t) * start + t * end
    return tc.clamp_to_envelope(uv, start, end)
