"""Preserve section extent and centroid through resampling and correspondence.

Diagnostic centering/scaling for matching is always inverted before the
profile is used as a loft input.
"""
from __future__ import annotations

from typing import Any

import numpy as np

import generic_cad_profiles as gp


def extent_uv(uv: np.ndarray) -> tuple[float, float]:
    uv = np.asarray(uv, dtype=float)
    if len(uv) == 0:
        return 0.0, 0.0
    ext = np.ptp(uv, axis=0)
    return float(ext[0]), float(ext[1])


def resampling_extent_drift(uv: np.ndarray, count: int | None = None) -> dict[str, float]:
    uv = np.asarray(uv, dtype=float)
    if len(uv) < 3:
        return {"RESAMPLING_EXTENT_DRIFT": 0.0, "width_ratio": 1.0, "height_ratio": 1.0, "area_ratio": 1.0}
    samples = gp.resample_closed(uv, count or gp.PROFILE_SAMPLE_COUNT)
    w0, h0 = extent_uv(uv)
    w1, h1 = extent_uv(samples)
    a0 = max(gp.polygon_area(uv), 1e-16)
    a1 = gp.polygon_area(samples)
    wr = w1 / max(w0, 1e-12)
    hr = h1 / max(h0, 1e-12)
    return {
        "RESAMPLING_EXTENT_DRIFT": float(max(abs(wr - 1.0), abs(hr - 1.0))),
        "width_ratio": float(wr),
        "height_ratio": float(hr),
        "area_ratio": float(a1 / a0),
        "centroid_drift": float(np.linalg.norm(samples.mean(axis=0) - uv.mean(axis=0))),
    }


def _normalize_shape(uv: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    uv = np.asarray(uv, dtype=float)
    centroid = uv.mean(axis=0)
    centered = uv - centroid
    scale = float(np.linalg.norm(np.ptp(centered, axis=0))) or 1.0
    return centered / scale, centroid, scale


def cyclic_align_metric(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    """Order-only correspondence: center/scale for matching, then invert to source metric."""
    n = gp.PROFILE_SAMPLE_COUNT
    ref = gp.resample_closed(reference, n)
    cand = gp.resample_closed(candidate, n)
    if len(ref) != n or len(cand) != n:
        return {
            "aligned": cand,
            "PROFILE_CORRESPONDENCE_SUCCESS": False,
            "MAX_PROFILE_ALIGNMENT_ERROR": 1.0,
            "shift": 0,
            "reversed": False,
            "CORRESPONDENCE_NORMALIZATION_INVERTED": True,
            "PROFILE_CORRESPONDENCE_CHANGES_CENTROID": False,
            "SCALE_RECOVERY_ERROR": 1.0,
            "CENTROID_RECOVERY_ERROR": 1.0,
        }
    cand_c0 = cand.mean(axis=0)
    cand_ext0 = np.ptp(cand, axis=0)
    ref_n, _, _ = _normalize_shape(ref)
    cand_n, cand_c, cand_s = _normalize_shape(cand)
    best = float("inf")
    best_seq_n = cand_n
    best_shift = 0
    best_rev = False
    for reversed_ in (False, True):
        seq = cand_n[::-1].copy() if reversed_ else cand_n.copy()
        for k in range(n):
            rolled = np.roll(seq, k, axis=0)
            cost = float(np.linalg.norm(ref_n - rolled, axis=1).mean())
            if cost < best:
                best = cost
                best_seq_n = rolled
                best_shift = k
                best_rev = reversed_
    restored = best_seq_n * cand_s + cand_c
    scale_err = float(np.linalg.norm(np.ptp(restored, axis=0) - cand_ext0))
    centroid_err = float(np.linalg.norm(restored.mean(axis=0) - cand_c0))
    diag = float(np.linalg.norm(np.ptp(ref, axis=0))) or 1.0
    max_err = float(np.linalg.norm(best_seq_n - ref_n, axis=1).max())
    return {
        "aligned": restored,
        "PROFILE_CORRESPONDENCE_SUCCESS": bool(max_err <= 0.75),
        "MAX_PROFILE_ALIGNMENT_ERROR": max_err * diag,
        "mean_alignment_error": best,
        "shift": int(best_shift),
        "reversed": bool(best_rev),
        "CORRESPONDENCE_NORMALIZATION_INVERTED": True,
        "PROFILE_CORRESPONDENCE_CHANGES_CENTROID": bool(centroid_err > 1e-5 * max(diag, 1e-9)),
        "SCALE_RECOVERY_ERROR": scale_err,
        "CENTROID_RECOVERY_ERROR": centroid_err,
        "measured_section_centroid_2d": cand_c0.tolist(),
    }


def align_profile_sequence_metric(profiles: list[np.ndarray]) -> dict[str, Any]:
    if not profiles:
        return {
            "aligned": [],
            "PROFILE_CORRESPONDENCE_SUCCESS": False,
            "MAX_PROFILE_ALIGNMENT_ERROR": 1.0,
            "CORRESPONDENCE_NORMALIZATION_INVERTED": True,
            "PROFILE_CORRESPONDENCE_CHANGES_CENTROID": False,
            "SCALE_RECOVERY_ERROR": 0.0,
            "CENTROID_RECOVERY_ERROR": 0.0,
            "RESAMPLING_EXTENT_DRIFT": 0.0,
        }
    aligned = [gp.resample_closed(profiles[0], gp.PROFILE_SAMPLE_COUNT)]
    success = True
    max_err = 0.0
    changed_centroid = False
    scale_err = 0.0
    cent_err = 0.0
    drift = resampling_extent_drift(profiles[0])["RESAMPLING_EXTENT_DRIFT"]
    for nxt in profiles[1:]:
        drift = max(drift, resampling_extent_drift(nxt)["RESAMPLING_EXTENT_DRIFT"])
        result = cyclic_align_metric(aligned[-1], nxt)
        aligned.append(result["aligned"])
        success = success and bool(result.get("PROFILE_CORRESPONDENCE_SUCCESS"))
        max_err = max(max_err, float(result.get("MAX_PROFILE_ALIGNMENT_ERROR") or 0.0))
        changed_centroid = changed_centroid or bool(result.get("PROFILE_CORRESPONDENCE_CHANGES_CENTROID"))
        scale_err = max(scale_err, float(result.get("SCALE_RECOVERY_ERROR") or 0.0))
        cent_err = max(cent_err, float(result.get("CENTROID_RECOVERY_ERROR") or 0.0))
    return {
        "aligned": aligned,
        "PROFILE_CORRESPONDENCE_SUCCESS": success and len(aligned) >= 2,
        "MAX_PROFILE_ALIGNMENT_ERROR": max_err,
        "section_count": len(aligned),
        "CORRESPONDENCE_NORMALIZATION_INVERTED": True,
        "PROFILE_CORRESPONDENCE_CHANGES_CENTROID": bool(changed_centroid),
        "SCALE_RECOVERY_ERROR": scale_err,
        "CENTROID_RECOVERY_ERROR": cent_err,
        "RESAMPLING_EXTENT_DRIFT": drift,
    }


def profile_metrics(uv: np.ndarray, x: float | None = None) -> dict[str, float]:
    uv = np.asarray(uv, dtype=float)
    w, h = extent_uv(uv)
    c = uv.mean(axis=0) if len(uv) else np.zeros(2)
    return {
        "axial_position": float(x) if x is not None else 0.0,
        "centroid_u": float(c[0]),
        "centroid_v": float(c[1]),
        "width": w,
        "height": h,
        "area": gp.polygon_area(uv) if len(uv) >= 3 else 0.0,
        "perimeter": gp.polygon_perimeter(uv) if len(uv) >= 2 else 0.0,
    }


def loft_twist_score(profiles: list[np.ndarray]) -> dict[str, float]:
    angs = []
    crossings = 0
    for uv in profiles:
        uv = np.asarray(uv, dtype=float)
        if len(uv) < 3:
            continue
        c = uv.mean(axis=0)
        angs.append(float(np.arctan2(uv[0, 1] - c[1], uv[0, 0] - c[0])))
    for a, b in zip(profiles[:-1], profiles[1:]):
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        n = min(len(a), len(b))
        for k in range(n):
            p1, p2 = a[k], a[(k + 1) % n]
            q1, q2 = b[k % len(b)], b[(k + 1) % len(b)]

            def _orient(p, q, r):
                return np.sign((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]))

            if _orient(p1, p2, q1) != _orient(p1, p2, q2) and _orient(q1, q2, p1) != _orient(q1, q2, p2):
                crossings += 1
    unwrapped = np.unwrap(angs) if angs else np.zeros(1)
    return {
        "LOFT_TWIST_SCORE": float(np.ptp(unwrapped)) if len(unwrapped) else 0.0,
        "PROFILE_EDGE_CROSSING_COUNT": int(crossings),
        "LOFT_SELF_INTERSECTION_EVIDENCE": bool(crossings >= 4 or (len(unwrapped) and np.ptp(unwrapped) > 1.2)),
    }
