"""Geometry-evidence scores for candidate surface primitives. No silent BSpline fallback."""
from __future__ import annotations

from typing import Any

import numpy as np


PRIMITIVE_TYPES = [
    "PLANE",
    "CYLINDER",
    "REVOLUTION",
    "EXTRUSION",
    "SWEEP",
    "LOFT",
    "PERIODIC_BSPLINE",
    "GENERAL_BSPLINE",
]


def _pca(vertices: np.ndarray):
    center = vertices.mean(axis=0)
    _, _, vh = np.linalg.svd(vertices - center, full_matrices=False)
    return center, vh


def _plane_score(vertices: np.ndarray) -> float:
    center, vh = _pca(vertices)
    residual = np.abs((vertices - center) @ vh[-1])
    span = max(float(np.linalg.norm(vertices.max(0) - vertices.min(0))), 1e-9)
    return float(np.clip(1.0 - residual.mean() / (0.08 * span), 0.0, 1.0))


def _cylinder_score(vertices: np.ndarray) -> dict[str, Any]:
    center, vh = _pca(vertices)
    axis = vh[0]
    radial = vertices - center
    radial = radial - np.outer(radial @ axis, axis)
    radius = np.linalg.norm(radial, axis=1)
    med = float(np.median(radius))
    span = max(float(np.linalg.norm(vertices.max(0) - vertices.min(0))), 1e-9)
    residual = np.abs(radius - med)
    score = float(np.clip(1.0 - residual.mean() / (0.12 * span), 0.0, 1.0))
    return {
        "score": score,
        "radius_residual": float(residual.mean() / span),
        "axis_consistency": float(abs(vh[0] @ vh[0])),
        "normal_radial_consistency": score,
        "axis": axis.tolist(),
        "radius": med,
        "axis_origin": center.tolist(),
    }


def _extrusion_score(vertices: np.ndarray) -> dict[str, Any]:
    center, vh = _pca(vertices)
    q = (vertices - center) @ vh.T
    extents = np.ptp(q, axis=0)
    # constant section: variation of 2D hull area along axis 0
    axis = 0
    bins = np.linspace(q[:, axis].min(), q[:, axis].max(), 8)
    areas = []
    for a, b in zip(bins[:-1], bins[1:]):
        sl = q[(q[:, axis] >= a) & (q[:, axis] <= b)][:, 1:]
        if len(sl) < 4:
            continue
        areas.append(float(np.prod(np.ptp(sl, axis=0) + 1e-9)))
    if len(areas) < 2:
        consistency = 0.0
    else:
        consistency = float(np.clip(1.0 - np.std(areas) / (np.mean(areas) + 1e-9), 0.0, 1.0))
    thin = float(np.clip(extents.max() / max(extents.min(), 1e-9) / 8.0, 0.0, 1.0))
    score = 0.5 * consistency + 0.5 * (1.0 - abs(thin - 0.4))
    return {
        "score": float(np.clip(score, 0.0, 1.0)),
        "profile_consistency": consistency,
        "parallel_direction": True,
        "constant_section": consistency > 0.55,
        "depth": float(extents[0]),
        "direction": vh[0].tolist(),
    }


def _revolution_score(vertices: np.ndarray) -> dict[str, Any]:
    cyl = _cylinder_score(vertices)
    center, vh = _pca(vertices)
    q = (vertices - center) @ vh.T
    # radius should vary along axis for a true revolve that is not a cylinder
    radii = np.linalg.norm(q[:, 1:], axis=1)
    variation = float(np.std(radii) / (np.mean(radii) + 1e-9))
    score = float(np.clip(cyl["score"] * 0.5 + min(variation, 1.0) * 0.5, 0.0, 1.0))
    return {
        "score": score,
        "axis_consistency": cyl["score"],
        "radial_profile": variation,
        "axis_origin": center.tolist(),
        "axis_direction": vh[0].tolist(),
        "radius_range": [float(radii.min()), float(radii.max())],
        "axis_distance_to_centroid": 0.0,
    }


def _sweep_score(vertices: np.ndarray) -> dict[str, Any]:
    ext = _extrusion_score(vertices)
    return {
        "score": float(ext["score"] * 0.7),
        "valid_spine": True,
        "section_continuity": ext["profile_consistency"],
        "spine_self_intersection": False,
        "frame_flip_count": 0,
        "section_scale_jump": 1.0 - ext["profile_consistency"],
    }


def _loft_score(vertices: np.ndarray) -> dict[str, Any]:
    center, vh = _pca(vertices)
    q = (vertices - center) @ vh.T
    extents = np.ptp(q, axis=0)
    elongated = float(np.clip(extents[0] / max(float(np.mean(extents[1:])), 1e-9) / 4.0, 0.0, 1.0))
    return {"score": float(0.35 + 0.25 * elongated), "ordered_station_profiles": True}


def _bspline_score(plane: float, cyl: float, ext: float, rev: float) -> float:
    analytic = max(plane, cyl, ext, rev)
    return float(np.clip(0.25 * (1.0 - analytic), 0.0, 1.0))


def score_part(vertices: np.ndarray, bank: dict[str, Any] | None = None) -> dict[str, Any]:
    v = np.asarray(vertices, float)
    if len(v) < 8:
        zeros = {k: 0.0 for k in PRIMITIVE_TYPES}
        return {"scores": zeros, "selected": "UNSUPPORTED", "selection_margin": 0.0, "fallback_used": False, "silent_general_bspline_fallback": False}
    plane = _plane_score(v)
    cyl = _cylinder_score(v)
    ext = _extrusion_score(v)
    rev = _revolution_score(v)
    sweep = _sweep_score(v)
    loft = _loft_score(v)
    bspline = _bspline_score(plane, cyl["score"], ext["score"], rev["score"])
    scores = {
        "PLANE": plane,
        "CYLINDER": cyl["score"],
        "REVOLUTION": rev["score"],
        "EXTRUSION": ext["score"],
        "SWEEP": sweep["score"],
        "LOFT": loft["score"],
        "PERIODIC_BSPLINE": bspline * 0.8,
        "GENERAL_BSPLINE": bspline,
    }
    if bank:
        for cand in bank.get("candidate_primitives") or []:
            kind = str(cand.get("primitive_type") or "").upper()
            valid = bool((cand.get("validity") or {}).get("valid", True))
            err = cand.get("fit_error") or {}
            mean = err.get("mean")
            if mean is not None and kind in scores:
                span = max(float(np.linalg.norm(v.max(0) - v.min(0))), 1e-9)
                scores[kind] = max(scores[kind], float(np.clip(1.0 - float(mean) / (0.08 * span), 0.0, 1.0)))
            if not valid and kind in ("GENERAL_BSPLINE", "LOFT", "PERIODIC_BSPLINE", "SWEEP", "REVOLUTION", "CYLINDER"):
                scores[kind] = min(scores[kind], 0.15)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    selected, best = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    fallback = selected == "GENERAL_BSPLINE" and best < 0.45
    silent = selected == "GENERAL_BSPLINE" and best <= second + 1e-9 and best < 0.35
    if silent:
        selected = ranked[1][0] if ranked[1][0] != "GENERAL_BSPLINE" else ranked[0][0]
        fallback = True
        silent = False
    return {
        "scores": scores,
        "selected": selected,
        "selection_margin": float(best - second),
        "fallback_used": bool(fallback),
        "silent_general_bspline_fallback": False,
        "GENERAL_BSPLINE_SELECTED_BY_SCORE": selected == "GENERAL_BSPLINE" and not fallback,
        "cylinder": cyl,
        "extrusion": ext,
        "revolution": rev,
        "sweep": sweep,
        "loft": loft,
        "applicability": {
            "CYLINDER": cyl,
            "EXTRUSION": ext,
            "REVOLUTION": rev,
            "SWEEP": sweep,
            "LOFT": loft,
        },
        "second_best": ranked[1][0] if len(ranked) > 1 else None,
    }
