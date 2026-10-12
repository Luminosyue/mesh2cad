"""Loft / skin profile correspondence and loft-domain preflight."""
from __future__ import annotations

from typing import Any

import numpy as np


def _segment_intersection(a0, a1, b0, b1) -> bool:
    a0, a1, b0, b1 = map(lambda x: np.asarray(x, float), (a0, a1, b0, b1))
    da = a1 - a0
    db = b1 - b0
    cross = da[0] * db[1] - da[1] * db[0]
    if abs(cross) < 1e-12:
        return False
    t = ((b0[0] - a0[0]) * db[1] - (b0[1] - a0[1]) * db[0]) / cross
    u = ((b0[0] - a0[0]) * da[1] - (b0[1] - a0[1]) * da[0]) / cross
    return 0.02 < t < 0.98 and 0.02 < u < 0.98


def profile_correspondence(profiles_uv: list[np.ndarray], stations: list[float], part_diag: float) -> dict[str, Any]:
    rows = [np.asarray(p, float) for p in profiles_uv]
    n = len(rows)
    if n == 0:
        return {
            "PROFILE_COUNT": 0,
            "PROFILE_POINT_COUNT": 0,
            "PROFILE_ORDER_VALID": False,
            "LOFT_PREFLIGHT_PASS": False,
        }
    count = int(len(rows[0]))
    centroids = np.asarray([row.mean(axis=0) for row in rows], float)
    scales = np.asarray([np.linalg.norm(row - c, axis=1).mean() for row, c in zip(rows, centroids)], float)
    jumps = np.linalg.norm(np.diff(centroids, axis=0), axis=1) if n > 1 else np.asarray([0.0])
    scale_jumps = np.abs(np.diff(scales)) / np.maximum(scales[:-1], 1e-9) if n > 1 else np.asarray([0.0])
    stations_arr = np.asarray(stations, float)
    monotonic = bool(n < 2 or np.all(np.diff(stations_arr) > 0) or np.all(np.diff(stations_arr) < 0))
    flips = 0
    crossings = 0
    self_hits = 0
    for i, row in enumerate(rows):
        closed = np.vstack([row, row[:1]])
        for a in range(len(row)):
            for b in range(a + 2, len(row) - (0 if a else 1)):
                if _segment_intersection(closed[a], closed[a + 1], closed[b], closed[b + 1]):
                    self_hits += 1
        if i == 0:
            continue
        prev = rows[i - 1]
        area = 0.5 * np.sum(row[:, 0] * np.roll(row[:, 1], -1) - row[:, 1] * np.roll(row[:, 0], -1))
        prev_area = 0.5 * np.sum(prev[:, 0] * np.roll(prev[:, 1], -1) - prev[:, 1] * np.roll(prev[:, 0], -1))
        if area * prev_area < 0:
            flips += 1
        for k in range(count):
            a0, a1 = prev[k], prev[(k + 1) % count]
            b0, b1 = row[k], row[(k + 1) % count]
            # correspondence crossing: consecutive correspondences invert in 2D
        # pair crossing: chords between corresponding points
        for k in range(count):
            for m in range(k + 1, count):
                if _segment_intersection(prev[k], row[k], prev[m], row[m]):
                    crossings += 1
    part = max(float(part_diag), 1e-12)
    max_centroid = float(jumps.max()) if jumps.size else 0.0
    max_scale = float(scale_jumps.max()) if scale_jumps.size else 0.0
    return {
        "PROFILE_COUNT": n,
        "PROFILE_POINT_COUNT": count,
        "PROFILE_ORDER_VALID": monotonic,
        "PROFILE_ORIENTATION_CONSISTENT": flips == 0,
        "PROFILE_FLIP_COUNT": int(flips),
        "PROFILE_SELF_INTERSECTION_COUNT": int(self_hits),
        "PROFILE_PAIR_CROSSING_COUNT": int(crossings),
        "STATION_MONOTONICITY": monotonic,
        "MAX_PROFILE_SCALE_JUMP": max_scale,
        "MAX_PROFILE_CENTROID_JUMP": max_centroid / part,
        "STATION_REVERSAL": not monotonic,
    }


def loft_preflight(corr: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    loft_cfg = cfg["loft_preflight"]
    fail = (
        float(corr.get("MAX_PROFILE_CENTROID_JUMP") or 0.0) > loft_cfg["max_centroid_jump_ratio"]
        or float(corr.get("MAX_PROFILE_SCALE_JUMP") or 0.0) > loft_cfg["max_scale_jump_ratio"]
        or int(corr.get("PROFILE_FLIP_COUNT") or 0) > 0
        or int(corr.get("PROFILE_PAIR_CROSSING_COUNT") or 0) > loft_cfg["max_crossing_pairs"]
        or bool(corr.get("STATION_REVERSAL"))
    )
    return {**corr, "LOFT_PREFLIGHT_PASS": (not fail) and int(corr.get("PROFILE_COUNT") or 0) >= 2}


def output_to_profile_ratio(output_diag: float, profile_bbox_diag: float) -> float:
    return float(output_diag) / max(float(profile_bbox_diag), 1e-12)
