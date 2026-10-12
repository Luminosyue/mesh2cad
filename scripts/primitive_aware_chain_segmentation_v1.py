from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from dora_fitted_curve_dataset_v1 import circlefit, ellipsefit, linefit, splinefit


@dataclass(frozen=True)
class Segment:
    start_index: int
    end_index: int
    point_count: int
    arclength: float
    primitive_type: str
    normalized_residual: float
    fit: dict


COMPLEXITY = {"LINE": 0.0, "ARC": 0.8, "CIRCLE": 0.8, "ELLIPSE": 1.2, "BSPLINE": 2.2}


def _unit(v):
    v = np.asarray(v, float)
    return v / max(float(np.linalg.norm(v)), 1e-12)


def _arc(points):
    d = np.linalg.norm(np.diff(points, axis=0), axis=1)
    return np.r_[0.0, np.cumsum(d)]


def geometric_profile(points, object_diag):
    """Deterministic local signals; no GT or BRep information is used."""
    p = np.asarray(points, float)
    s = _arc(p)
    w = max(2, min(4, (len(p) - 1) // 8))
    tang = np.zeros_like(p)
    for i in range(len(p)):
        tang[i] = _unit(p[min(len(p) - 1, i + w)] - p[max(0, i - w)])
    turn = np.zeros(len(p))
    turn[1:] = np.arccos(np.clip(np.sum(tang[1:] * tang[:-1], axis=1), -1, 1))
    line_res = np.zeros(len(p)); plane_res = np.zeros(len(p))
    for i in range(len(p)):
        lo, hi = max(0, i - w), min(len(p), i + w + 1); q = p[lo:hi]; c = q.mean(0)
        _, sv, vh = np.linalg.svd(q - c, full_matrices=False)
        line_res[i] = np.sqrt(np.mean((q - (c + (q-c) @ vh[0][:, None] * vh[0])).sum(1)**2)) / max(object_diag, 1e-12)
        plane_res[i] = float(sv[-1] / max(object_diag, 1e-12)) if len(sv) >= 3 else 0.0
    curv = turn / np.maximum(np.gradient(s), 1e-9)
    return {"arclength": s, "tangent": tang, "turning_angle": turn,
            "line_residual": np.nan_to_num(line_res), "planarity_residual": np.nan_to_num(plane_res),
            "curvature_proxy": np.nan_to_num(curv)}


def candidate_change_points(points, profile, object_diag, min_points=4, max_candidates=24):
    n = len(points); score = np.zeros(n)
    turn = profile["turning_angle"]; curv = profile["curvature_proxy"]
    for i in range(2, n - 2):
        left = max(0, i - 3); right = min(n, i + 4)
        score[i] = turn[i] + abs(np.median(curv[i:right]) - np.median(curv[left:i])) * max(object_diag, 1e-12)
    raw = [i for i in range(min_points, n - min_points) if score[i] > 0.08]
    raw.sort(key=lambda i: (-score[i], i))
    kept = []
    for i in raw:
        if all(abs(i-j) >= min_points for j in kept): kept.append(i)
        if len(kept) >= max_candidates: break
    return sorted(kept), len(raw) - len(kept)


def _fit(points, closed, diag):
    f = linefit(points)
    if f["rms"] / diag > 5e-3 and len(points) >= 4: f = circlefit(points, closed)
    if (f is None or f["rms"] / diag > 5e-3) and len(points) >= 6: f = ellipsefit(points, closed)
    if f is None or f["rms"] / diag > 5e-3: f = splinefit(points, closed, diag)
    if f is None: return None
    return f


def _cost(f, diag, split_count):
    return (f["rms"] / max(diag, 1e-12)) ** 2 + COMPLEXITY.get(f["type"], 2.2) * 0.001 + split_count * 0.002


def segment_chain_primitives(points, closed, object_diag, min_points=4, min_arclength_rel=1e-3,
                             max_candidates=24):
    """Return a conservative deterministic segmentation selected by model cost."""
    p = np.asarray(points, float); n = len(p); profile = geometric_profile(p, object_diag)
    candidates, truncated = candidate_change_points(p, profile, object_diag, min_points, max_candidates)
    boundaries = [0] + candidates + [n - 1]
    arc = profile["arclength"]
    cache = {}
    def fit(a, b):
        key = (a, b)
        if key not in cache:
            q = p[a:b+1]; valid = len(q) >= min_points and arc[b] - arc[a] >= min_arclength_rel * object_diag
            cache[key] = _fit(q, False, object_diag) if valid else None
        return cache[key]
    # Dynamic programming over candidate boundaries. H0 is retained explicitly.
    best = {0: (0.0, [])}
    for bi in range(1, len(boundaries)):
        end = boundaries[bi]; options = []
        for ai in range(bi):
            start = boundaries[ai]; f = fit(start, end)
            if f is not None and start in best:
                options.append((best[start][0] + _cost(f, object_diag, bi-1), best[start][1] + [(start, end, f)]))
        if options: best[end] = min(options, key=lambda x: (x[0], len(x[1]), x[1]))
    whole = fit(0, n-1)
    if n - 1 in best:
        chosen = best[n - 1]
    elif whole is not None:
        chosen = (_cost(whole, object_diag, 0), [(0, n-1, whole)])
    else:
        chosen = (float('inf'), [])
    if whole is not None and chosen[0] >= _cost(whole, object_diag, 0) * 0.98:
        chosen = (_cost(whole, object_diag, 0), [(0, n-1, whole)])
    segments = []
    for start, end, f in chosen[1]:
        segments.append(Segment(start, end, end-start+1, float(arc[end]-arc[start]), f["type"],
                                float(f["rms"] / max(object_diag, 1e-12)), f))
    return {"segments": segments, "profile": profile, "candidates": candidates,
            "candidate_count_raw": len(candidates) + truncated, "candidate_count_kept": len(candidates),
            "candidate_count_truncated": truncated, "whole_chain_fit": whole}
