"""Composite axial range, overlap, and pre/post sewing geometry audits."""
from __future__ import annotations

from typing import Any

import numpy as np


def axial_intervals(shaft: tuple[float, float], terminal: tuple[float, float], transition: tuple[float, float]) -> dict[str, float]:
    s0, s1 = sorted(shaft)
    t0, t1 = sorted(terminal)
    r0, r1 = sorted(transition)
    shaft_len = s1 - s0
    term_len = t1 - t0
    # gap: positive if disjoint, 0 if touching
    if s1 < t0:
        gap = t0 - s1
        overlap_st = 0.0
    elif t1 < s0:
        gap = s0 - t1
        overlap_st = 0.0
    else:
        gap = 0.0
        overlap_st = min(s1, t1) - max(s0, t0)

    def _ov(a0, a1, b0, b1):
        return max(0.0, min(a1, b1) - max(a0, b0))

    component = max(s1, t1, r1) - min(s0, t0, r0)
    overlap_shaft_trans = _ov(s0, s1, r0, r1)
    overlap_term_trans = _ov(t0, t1, r0, r1)
    return {
        "SOURCE_AXIAL_MIN": float(min(s0, t0)),
        "SOURCE_AXIAL_MAX": float(max(s1, t1)),
        "SHAFT_AXIAL_MIN": float(s0),
        "SHAFT_AXIAL_MAX": float(s1),
        "TERMINAL_AXIAL_MIN": float(t0),
        "TERMINAL_AXIAL_MAX": float(t1),
        "TRANSITION_AXIAL_MIN": float(r0),
        "TRANSITION_AXIAL_MAX": float(r1),
        "COMPOSITE_AXIAL_MIN": float(min(s0, t0, r0)),
        "COMPOSITE_AXIAL_MAX": float(max(s1, t1, r1)),
        "SHAFT_TERMINAL_GAP": float(gap),
        "SHAFT_TERMINAL_OVERLAP": float(max(overlap_st, 0.0)),
        "SHAFT_TRANSITION_OVERLAP": float(overlap_shaft_trans),
        "TERMINAL_TRANSITION_OVERLAP": float(overlap_term_trans),
        "OVERLAP_RATIO_TO_COMPONENT_LENGTH": float(
            max(overlap_st, overlap_shaft_trans + overlap_term_trans) / max(component, 1e-12)
        ),
        "COMPOSITE_AXIAL_OVERLAP_FAIL": bool(
            overlap_st / max(min(shaft_len, term_len), 1e-12) > 0.25
            or (overlap_shaft_trans + overlap_term_trans) / max(component, 1e-12) > 0.20
        ),
    }


def shape_bbox(shape: Any) -> np.ndarray | None:
    try:
        from OCP.Bnd import Bnd_Box
        from OCP.BRepBndLib import BRepBndLib

        box = Bnd_Box()
        BRepBndLib.Add_s(shape, box, True)
        xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
        return np.array([[xmin, ymin, zmin], [xmax, ymax, zmax]], dtype=float)
    except Exception:
        return None


def union_bbox(boxes: list[np.ndarray]) -> np.ndarray | None:
    valid = [b for b in boxes if b is not None]
    if not valid:
        return None
    lo = np.min([b[0] for b in valid], axis=0)
    hi = np.max([b[1] for b in valid], axis=0)
    return np.vstack([lo, hi])


def sewing_mutation(pre: np.ndarray | None, post: np.ndarray | None, centroid_shift: float = 0.0) -> dict[str, Any]:
    if pre is None or post is None:
        return {
            "PRE_TO_POST_SEW_EXTENT_CHANGE_X": None,
            "PRE_TO_POST_SEW_EXTENT_CHANGE_Y": None,
            "PRE_TO_POST_SEW_EXTENT_CHANGE_Z": None,
            "PRE_TO_POST_SEW_CENTROID_SHIFT": centroid_shift,
            "SEWING_GEOMETRY_MUTATION": False,
        }
    pre_ext = pre[1] - pre[0]
    post_ext = post[1] - post[0]
    change = (post_ext - pre_ext) / np.maximum(pre_ext, 1e-12)
    pre_c = pre.mean(axis=0)
    post_c = post.mean(axis=0)
    shift = float(np.linalg.norm(post_c - pre_c)) if centroid_shift == 0.0 else float(centroid_shift)
    mutation = bool(np.max(np.abs(change)) > 0.05 or shift > 0.05 * float(np.linalg.norm(pre_ext)))
    return {
        "PRESEW_COMBINED_BBOX": pre.tolist(),
        "POSTSEW_BBOX": post.tolist(),
        "PRE_TO_POST_SEW_EXTENT_CHANGE_X": float(change[0]),
        "PRE_TO_POST_SEW_EXTENT_CHANGE_Y": float(change[1]),
        "PRE_TO_POST_SEW_EXTENT_CHANGE_Z": float(change[2]),
        "PRE_TO_POST_SEW_CENTROID_SHIFT": shift,
        "SEWING_GEOMETRY_MUTATION": mutation,
    }


def local_extent_ratios(source_pts: np.ndarray, cad_pts: np.ndarray) -> dict[str, float]:
    src = np.asarray(source_pts, dtype=float)
    cad = np.asarray(cad_pts, dtype=float)
    if len(src) == 0 or len(cad) == 0:
        return {"axial": 0.0, "U": 0.0, "V": 0.0}
    src_ax, src_u, src_v = np.ptp(src[:, 0]), np.ptp(src[:, 1]), np.ptp(src[:, 2])
    cad_ax, cad_u, cad_v = np.ptp(cad[:, 0]), np.ptp(cad[:, 1]), np.ptp(cad[:, 2])
    return {
        "axial": float(cad_ax / max(src_ax, 1e-12)),
        "U": float(cad_u / max(src_u, 1e-12)),
        "V": float(cad_v / max(src_v, 1e-12)),
        "source_centroid": src.mean(axis=0).tolist(),
        "cad_centroid": cad.mean(axis=0).tolist(),
        "centroid_error": float(np.linalg.norm(src.mean(axis=0) - cad.mean(axis=0))),
    }
