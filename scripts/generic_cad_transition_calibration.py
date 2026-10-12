"""Transition profiles: cyclic correspondence, envelope clamp, centroid continuity."""
from __future__ import annotations

from typing import Any

import numpy as np

import generic_cad_profiles as gp
import generic_cad_profile_metric_calibration as pmc


def endpoint_envelope(a: np.ndarray, b: np.ndarray, pad: float = 0.03) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    lo = np.minimum(a.min(axis=0), b.min(axis=0))
    hi = np.maximum(a.max(axis=0), b.max(axis=0))
    span = np.maximum(hi - lo, 1e-12)
    return lo - pad * span, hi + pad * span


def clamp_to_envelope(uv: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    uv = np.asarray(uv, dtype=float)
    lo, hi = endpoint_envelope(a, b)
    return np.clip(uv, lo, hi)


def transition_profiles(uv_a: np.ndarray, uv_b: np.ndarray, count: int = 5) -> dict[str, Any]:
    start = gp.resample_closed(uv_a)
    aligned = pmc.cyclic_align_metric(start, uv_b)
    end = np.asarray(aligned["aligned"], dtype=float)
    xs_alpha = np.linspace(0.0, 1.0, max(int(count), 2))
    profiles = []
    overshoot = False
    widths = []
    heights = []
    cents = []
    env_w = max(float(np.ptp(start[:, 0])), float(np.ptp(end[:, 0])))
    env_h = max(float(np.ptp(start[:, 1])), float(np.ptp(end[:, 1])))
    env_a = max(gp.polygon_area(start), gp.polygon_area(end))
    for t in xs_alpha:
        uv = (1.0 - t) * start + t * end
        uv = clamp_to_envelope(uv, start, end)
        w, h = pmc.extent_uv(uv)
        widths.append(w)
        heights.append(h)
        cents.append(uv.mean(axis=0))
        if w > 1.08 * env_w or h > 1.08 * env_h or gp.polygon_area(uv) > 1.12 * env_a:
            overshoot = True
        profiles.append(uv)
    cents_a = np.asarray(cents, dtype=float)
    jumps = np.linalg.norm(np.diff(cents_a, axis=0), axis=1) if len(cents_a) > 1 else np.zeros(1)
    env_diag = float(np.linalg.norm([env_w, env_h])) or 1.0
    return {
        "profiles": profiles,
        "alphas": xs_alpha.tolist(),
        "PROFILE_CORRESPONDENCE_SUCCESS": aligned.get("PROFILE_CORRESPONDENCE_SUCCESS"),
        "CORRESPONDENCE_NORMALIZATION_INVERTED": aligned.get("CORRESPONDENCE_NORMALIZATION_INVERTED"),
        "PROFILE_CORRESPONDENCE_CHANGES_CENTROID": aligned.get("PROFILE_CORRESPONDENCE_CHANGES_CENTROID"),
        "MAX_PROFILE_ALIGNMENT_ERROR": aligned.get("MAX_PROFILE_ALIGNMENT_ERROR"),
        "TRANSITION_WIDTH_OVERSHOOT_RATIO": float(max(widths) / max(env_w, 1e-12)),
        "TRANSITION_HEIGHT_OVERSHOOT_RATIO": float(max(heights) / max(env_h, 1e-12)),
        "TRANSITION_AREA_OVERSHOOT_RATIO": float(max(gp.polygon_area(p) for p in profiles) / max(env_a, 1e-16)),
        "TRANSITION_OVERSHOOT_DETECTED": bool(overshoot),
        "MAX_TRANSITION_CENTROID_JUMP": float(jumps.max() if len(jumps) else 0.0),
        "MAX_TRANSITION_CENTROID_JUMP_NORMALIZED": float((jumps.max() if len(jumps) else 0.0) / env_diag),
        "centroids": cents_a.tolist(),
        "start_centroid": start.mean(axis=0).tolist(),
        "end_centroid": end.mean(axis=0).tolist(),
    }
