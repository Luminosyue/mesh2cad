"""Canonical profile extraction and correspondence alignment."""
from __future__ import annotations

from typing import Any

import numpy as np
import trimesh
from scipy.spatial import ConvexHull


def resample_closed(points, count: int) -> np.ndarray:
    pts = np.asarray(points, float)
    if len(pts) > 1 and np.linalg.norm(pts[0] - pts[-1]) < 1e-9:
        pts = pts[:-1]
    closed = np.vstack([pts, pts[0]])
    lengths = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    dist = np.r_[0, np.cumsum(lengths)]
    if dist[-1] < 1e-10:
        raise RuntimeError("degenerate profile")
    out = []
    for t in np.linspace(0, dist[-1], count, endpoint=False):
        i = min(np.searchsorted(dist, t, side="right") - 1, len(pts) - 1)
        a = (t - dist[i]) / max(lengths[i], 1e-12)
        out.append(closed[i] * (1 - a) + closed[i + 1] * a)
    return np.asarray(out)


def resample_open(points, count: int) -> np.ndarray:
    pts = np.asarray(points, float)
    if len(pts) < 2:
        raise RuntimeError("open profile too short")
    lengths = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    dist = np.r_[0, np.cumsum(lengths)]
    if dist[-1] < 1e-10:
        raise RuntimeError("degenerate open profile")
    out = []
    for t in np.linspace(0, dist[-1], count, endpoint=True):
        i = min(np.searchsorted(dist, t, side="right") - 1, len(pts) - 2)
        a = (t - dist[i]) / max(lengths[i], 1e-12)
        out.append(pts[i] * (1 - a) + pts[i + 1] * a)
    return np.asarray(out)


def _section(mesh, ai: int, coordinate: float, count: int) -> tuple[np.ndarray, bool]:
    origin = np.zeros(3)
    origin[ai] = coordinate
    normal = np.zeros(3)
    normal[ai] = 1
    plane = [i for i in range(3) if i != ai]
    section = mesh.section(plane_origin=origin, plane_normal=normal)
    loops = [] if section is None else [np.asarray(x, float) for x in section.discrete if len(x) >= 2]
    if loops:
        loop = max(loops, key=lambda x: np.linalg.norm(np.diff(x, axis=0), axis=1).sum())
        closed = np.linalg.norm(loop[0] - loop[-1]) < 1e-6 or len(loop) >= 4
        uv = resample_closed(loop[:, plane], count) if closed else resample_open(loop[:, plane], count)
        return uv, bool(closed)
    vertices = np.asarray(mesh.vertices, float)
    order = np.argsort(abs(vertices[:, ai] - coordinate))
    k = min(len(vertices), max(count * 12, len(vertices) // 250))
    cloud = np.unique(np.round(vertices[order[:k]][:, plane], 9), axis=0)
    if len(cloud) < 3:
        raise RuntimeError("insufficient section")
    uv = resample_closed(cloud[ConvexHull(cloud).vertices], count)
    return uv, True


def cyclic_align(prev: np.ndarray, raw: np.ndarray) -> tuple[np.ndarray, int, str]:
    best = None
    cost = 1e99
    shift = 0
    orient = "FORWARD"
    for name, candidate in (("FORWARD", raw), ("REVERSED", raw[::-1])):
        for k in range(len(raw)):
            rolled = np.roll(candidate, k, axis=0)
            value = float(np.mean(np.sum((rolled - prev) ** 2, axis=1)))
            if value < cost:
                cost = value
                best = rolled
                shift = k
                orient = name
    return best, shift, orient


def open_align(prev: np.ndarray, raw: np.ndarray) -> tuple[np.ndarray, str]:
    fwd = raw
    rev = raw[::-1]
    if float(np.mean(np.sum((fwd - prev) ** 2, axis=1))) <= float(np.mean(np.sum((rev - prev) ** 2, axis=1))):
        return fwd, "FORWARD"
    return rev, "REVERSED"


def extract_profiles(mesh: trimesh.Trimesh, sections: int = 10, count: int = 10) -> dict[str, Any]:
    ai = int(np.argmax(mesh.extents))
    lo, hi = mesh.bounds[:, ai]
    rows = []
    coords = []
    closed_flags = []
    for fraction in np.linspace(0.003, 0.997, sections):
        coordinate = float(lo + (hi - lo) * fraction)
        uv, closed = _section(mesh, ai, coordinate, count)
        area = 0.5 * np.sum(uv[:, 0] * np.roll(uv[:, 1], -1) - uv[:, 1] * np.roll(uv[:, 0], -1))
        if closed and area < 0:
            uv = uv[::-1]
        if closed:
            uv = np.roll(uv, -int(np.argmax(uv[:, 0] + 1e-4 * uv[:, 1])), axis=0)
        rows.append(uv)
        coords.append(coordinate)
        closed_flags.append(closed)
    aligned = [rows[0]]
    shifts = [0]
    orients = ["CANONICAL"]
    closed = bool(closed_flags[0])
    for raw, flag in zip(rows[1:], closed_flags[1:]):
        closed = closed and flag
        if closed:
            best, shift, orient = cyclic_align(aligned[-1], raw)
        else:
            best, orient = open_align(aligned[-1], raw)
            shift = 0
        aligned.append(best)
        shifts.append(shift)
        orients.append(orient)
    plane = [i for i in range(3) if i != ai]
    xyz = []
    for coordinate, uv in zip(coords, aligned):
        pts = np.zeros((len(uv), 3))
        pts[:, ai] = coordinate
        pts[:, plane] = uv
        xyz.append(pts)
    stacked = np.vstack(xyz) if xyz else np.zeros((0, 3))
    lo3, hi3 = (stacked.min(0), stacked.max(0)) if len(stacked) else (np.zeros(3), np.zeros(3))
    return {
        "axis_index": ai,
        "stations": coords,
        "profiles_uv": aligned,
        "profiles_xyz": xyz,
        "closed": closed,
        "cyclic_shifts": shifts,
        "orientations": orients,
        "bbox_min": lo3.tolist(),
        "bbox_max": hi3.tolist(),
        "bbox_diag": float(np.linalg.norm(hi3 - lo3)),
        "PROFILE_SUPPORT_BBOX": {"bbox_min": lo3.tolist(), "bbox_max": hi3.tolist(), "bbox_diag": float(np.linalg.norm(hi3 - lo3))},
    }
