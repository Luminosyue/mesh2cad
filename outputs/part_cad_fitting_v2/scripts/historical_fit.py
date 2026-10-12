import math
from typing import Any
import numpy as np
from fit_logic import basis_for_axis

def polygon_area(points: np.ndarray) -> float:
    p = np.asarray(points, float)
    return 0.5 * float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - p[:, 1] * np.roll(p[:, 0], -1)))

def resample_loop(points: np.ndarray, n: int = 48) -> np.ndarray:
    p = np.asarray(points, float)
    if len(p) > 1 and np.linalg.norm(p[0] - p[-1]) < 1e-10:
        p = p[:-1]
    if len(p) < 3:
        raise ValueError("loop has fewer than 3 vertices")
    if polygon_area(p) < 0:
        p = p[::-1]
    q = np.vstack([p, p[:1]])
    seg = np.linalg.norm(np.diff(q, axis=0), axis=1)
    total = float(seg.sum())
    if total <= 1e-15:
        raise ValueError("zero perimeter loop")
    s = np.r_[0.0, np.cumsum(seg)]
    targets = np.linspace(0.0, total, n, endpoint=False)
    out = []
    for target in targets:
        i = min(int(np.searchsorted(s, target, side="right") - 1), len(seg) - 1)
        alpha = 0.0 if seg[i] == 0 else (target - s[i]) / seg[i]
        out.append(q[i] * (1.0 - alpha) + q[i + 1] * alpha)
    return np.asarray(out)

def align_loop(points: np.ndarray, previous: np.ndarray | None) -> np.ndarray:
    if previous is None:
        return points
    options = []
    for base in (points, points[::-1]):
        for k in range(len(points)):
            options.append(np.roll(base, k, axis=0))
    return min(options, key=lambda x: float(np.mean(np.sum((x - previous) ** 2, axis=1))))

def section_loft_profile(mesh, axis: np.ndarray, ruled: bool, section_count: int = 32, points_per_loop: int = 40) -> dict[str, Any]:
    from scipy.optimize import linear_sum_assignment
    from shapely.geometry import Point, Polygon

    v = np.asarray(mesh.vertices, float)
    center = np.asarray(mesh.bounds).mean(axis=0)
    B = basis_for_axis(axis)
    local = (v - center) @ B
    zmin, zmax = float(local[:, 2].min()), float(local[:, 2].max())
    span = zmax - zmin
    if span <= 1e-12:
        raise ValueError("zero loft span")
    tracks: dict[str, list[dict[str, Any]]] = {"outer": [], "hole": []}
    zs = np.linspace(zmin + 0.0015 * span, zmax - 0.0015 * span, section_count)
    cross_span = float(max(np.ptp(local[:, 0]), np.ptp(local[:, 1]), 1e-12))
    for section_index, z in enumerate(zs):
        sec = mesh.section(plane_origin=center + B[:, 2] * z, plane_normal=B[:, 2])
        loops = []
        if sec is not None:
            for d in sec.discrete:
                pts = (np.asarray(d) - center) @ B
                p2 = pts[:, :2]
                if len(p2) >= 4 and abs(polygon_area(p2)) > 1e-14:
                    loops.append(p2)
        if not loops:
            continue
        poly_rows = []
        for q in loops:
            try:
                poly = Polygon(q)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                if poly.is_empty or poly.geom_type != "Polygon":
                    continue
                poly_rows.append({"raw": q, "poly": poly, "area": float(abs(poly.area)), "center": np.asarray(poly.centroid.coords[0])})
            except Exception:
                continue
        poly_rows.sort(key=lambda x: -x["area"])
        classified = {"outer": [], "hole": []}
        for i, item in enumerate(poly_rows):
            point = Point(item["center"])
            depth = sum(1 for prior in poly_rows[:i] if prior["poly"].contains(point))
            typ = "hole" if depth % 2 else "outer"
            sampled = resample_loop(item["raw"], points_per_loop)
            classified[typ].append({"points": sampled, "center": sampled.mean(axis=0), "area": item["area"]})
        for typ in ("outer", "hole"):
            current = classified[typ]
            active_ids = [i for i, t in enumerate(tracks[typ]) if section_index - t["last_index"] <= 3]
            pairs = []
            if active_ids and current:
                cost = np.zeros((len(active_ids), len(current)), float)
                for ai, tid in enumerate(active_ids):
                    t = tracks[typ][tid]
                    for ci, item in enumerate(current):
                        dc = np.linalg.norm(t["last_center"] - item["center"]) / cross_span
                        da = abs(math.log(max(item["area"], 1e-15) / max(t["last_area"], 1e-15)))
                        cost[ai, ci] = dc + 0.12 * da
                rr, cc = linear_sum_assignment(cost)
                pairs = [(active_ids[int(a)], int(c)) for a, c in zip(rr, cc) if cost[a, c] <= 0.32]
            used = set()
            for tid, ci in pairs:
                item = current[ci]
                p = align_loop(item["points"], tracks[typ][tid]["last_points"])
                gp = center + p[:, 0, None] * B[:, 0] + p[:, 1, None] * B[:, 1] + z * B[:, 2]
                tracks[typ][tid]["sections"].append(gp.tolist())
                tracks[typ][tid].update({"last_index": section_index, "last_center": item["center"], "last_area": item["area"], "last_points": p})
                used.add(ci)
            for ci, item in enumerate(current):
                if ci in used:
                    continue
                p = item["points"]
                gp = center + p[:, 0, None] * B[:, 0] + p[:, 1, None] * B[:, 1] + z * B[:, 2]
                tracks[typ].append({"sections": [gp.tolist()], "last_index": section_index, "last_center": item["center"], "last_area": item["area"], "last_points": p})
    outer_rows = sorted((t for t in tracks["outer"] if len(t["sections"]) >= 4), key=lambda t: (-len(t["sections"]), -float(t["last_area"])))[:4]
    hole_rows = sorted((t for t in tracks["hole"] if len(t["sections"]) >= 4), key=lambda t: (-len(t["sections"]), -float(t["last_area"])))[:4]
    outer_tracks = [t["sections"] for t in outer_rows]
    hole_tracks = [t["sections"] for t in hole_rows]
    if not outer_tracks:
        raise ValueError("no loft outer track with >=4 sections")
    entities = points_per_loop * sum(len(t) for t in outer_tracks + hole_tracks)
    return {
        "kind": "multi_loft", "center": center.tolist(), "basis": B.tolist(), "axis": B[:, 2].tolist(),
        "zmin": zmin, "zmax": zmax, "outer_tracks": outer_tracks, "hole_tracks": hole_tracks,
        "ruled": ruled, "sketch_entity_count": entities,
    }

def primitive_profile(mesh, axis: np.ndarray, kind: str) -> dict[str, Any]:
    v = np.asarray(mesh.vertices, float)
    center = np.asarray(mesh.bounds).mean(axis=0)
    B = basis_for_axis(axis)
    local = (v - center) @ B
    mins, maxs = local.min(axis=0), local.max(axis=0)
    ext = maxs - mins
    if kind == "box":
        return {"kind": "box", "center": center.tolist(), "basis": B.tolist(), "mins": mins.tolist(), "maxs": maxs.tolist(), "sketch_entity_count": 4}
    radial = np.linalg.norm(local[:, :2] - 0.5 * (mins[:2] + maxs[:2]), axis=1)
    radius = float(np.quantile(radial, 0.99))
    return {"kind": "cylinder", "center": center.tolist(), "basis": B.tolist(), "zmin": float(mins[2]), "zmax": float(maxs[2]), "radius": radius, "sketch_entity_count": 1}