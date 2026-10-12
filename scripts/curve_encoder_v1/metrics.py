"""Evaluation metrics for Curve Encoder V1."""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np


TYPE_NAMES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")


def _batched_chamfer(a: np.ndarray, b: np.ndarray, chunk: int = 2048) -> np.ndarray:
    """Symmetric Chamfer for [N,32,3] point sets, computed in chunks."""
    n = a.shape[0]
    out = np.empty(n, dtype=np.float64)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        aa, bb = a[s:e], b[s:e]
        # [B, 32, 32]
        d2 = ((aa[:, :, None, :] - bb[:, None, :, :]) ** 2).sum(-1)
        out[s:e] = 0.5 * (np.sqrt(d2.min(2).mean(1)) + np.sqrt(d2.min(1).mean(1)))
    return out


def _safe_div(a: float, b: float) -> float:
    return float(a / b) if b else 0.0


def confusion_and_f1(y_true: np.ndarray, y_pred: np.ndarray, n_types: int = 4) -> dict:
    cm = np.zeros((n_types, n_types), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        if 0 <= t < n_types and 0 <= p < n_types:
            cm[t, p] += 1
    per = {}
    f1s = []
    for i, name in enumerate(TYPE_NAMES):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = _safe_div(tp, tp + fp)
        rec = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * prec * rec, prec + rec) if (prec + rec) else 0.0
        per[name] = {"precision": prec, "recall": rec, "f1": f1, "support": int(cm[i, :].sum())}
        if per[name]["support"] > 0:
            f1s.append(f1)
    return {
        "confusion": cm.tolist(),
        "per_type": per,
        "macro_f1": float(np.mean(f1s)) if f1s else 0.0,
        "accuracy": _safe_div(np.trace(cm), cm.sum()),
    }


def _angle_deg(a: np.ndarray, b: np.ndarray, abs_cos: bool = True) -> np.ndarray:
    a = a / np.clip(np.linalg.norm(a, axis=-1, keepdims=True), 1e-8, None)
    b = b / np.clip(np.linalg.norm(b, axis=-1, keepdims=True), 1e-8, None)
    cos = np.sum(a * b, axis=-1)
    if abs_cos:
        cos = np.abs(cos)
    cos = np.clip(cos, -1.0, 1.0)
    return np.degrees(np.arccos(cos))


def _summarize(arr: np.ndarray) -> dict:
    if arr.size == 0:
        return {"n": 0, "mean": None, "median": None, "p95": None, "max": None}
    return {
        "n": int(arr.size),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p95": float(np.percentile(arr, 95)),
        "max": float(np.max(arr)),
    }


def geometry_metrics(
    type_id: np.ndarray,
    xyz_gt: np.ndarray,
    xyz_pred: np.ndarray,
    params_gt: np.ndarray,
    params_pred: np.ndarray,
    arc_deg: np.ndarray,
    is_closed: np.ndarray,
) -> dict:
    """Compute reconstruction + type-conditioned parameter errors."""
    # Ordered L2 / Chamfer-proxy (same sample grid).
    per_pt = np.linalg.norm(xyz_pred - xyz_gt, axis=-1)  # [N, 32]
    recon_mean = per_pt.mean(axis=-1)
    # Vectorized symmetric Chamfer on 32-point sets (chunked for memory).
    chamfers = _batched_chamfer(xyz_gt, xyz_pred, chunk=2048)

    out = {
        "RECON_L2": _summarize(recon_mean),
        "RECON_CHAMFER": _summarize(chamfers),
    }

    # LINE direction
    m = type_id == 0
    if m.any():
        ang = _angle_deg(params_pred[m, 3:6], params_gt[m, 3:6], abs_cos=True)
        out["LINE_DIRECTION_ERROR"] = _summarize(ang)
        out["LINE_ORIGIN_ERROR"] = _summarize(np.linalg.norm(params_pred[m, 0:3] - params_gt[m, 0:3], axis=-1))

    # CIRCLE
    m = type_id == 1
    if m.any():
        out["CIRCLE_NORMAL_ERROR"] = _summarize(_angle_deg(params_pred[m, 3:6], params_gt[m, 3:6], abs_cos=True))
        out["CIRCLE_RADIUS_ERROR"] = _summarize(np.abs(params_pred[m, 6] - params_gt[m, 6]))
        out["CIRCLE_CENTER_ERROR"] = _summarize(np.linalg.norm(params_pred[m, 0:3] - params_gt[m, 0:3], axis=-1))

    # ELLIPSE
    m = type_id == 2
    if m.any():
        out["ELLIPSE_NORMAL_ERROR"] = _summarize(_angle_deg(params_pred[m, 3:6], params_gt[m, 3:6], abs_cos=True))
        out["ELLIPSE_AXIS_ERROR"] = _summarize(_angle_deg(params_pred[m, 6:9], params_gt[m, 6:9], abs_cos=True))
        out["ELLIPSE_MAJOR_RADIUS_ERROR"] = _summarize(np.abs(params_pred[m, 9] - params_gt[m, 9]))
        out["ELLIPSE_MINOR_RADIUS_ERROR"] = _summarize(np.abs(params_pred[m, 10] - params_gt[m, 10]))

    # Arc-coverage buckets for CIRCLE + ELLIPSE
    circ_ell = (type_id == 1) | (type_id == 2)
    buckets = {}
    if circ_ell.any():
        defs = [
            ("closed", None),
            ("lt15", (0.0, 15.0)),
            ("15_45", (15.0, 45.0)),
            ("45_90", (45.0, 90.0)),
            ("gt90", (90.0, 360.01)),
        ]
        for name, rng in defs:
            if name == "closed":
                sel = circ_ell & (is_closed.astype(bool))
            else:
                lo, hi = rng
                sel = circ_ell & (~is_closed.astype(bool)) & (arc_deg >= lo) & (arc_deg < hi)
            if not sel.any():
                buckets[name] = {"n": 0}
                continue
            buckets[name] = {
                "n": int(sel.sum()),
                "recon_chamfer_mean": float(chamfers[sel].mean()),
                "type_acc": float((type_id[sel] == type_id[sel]).mean()),  # placeholder overwritten below
            }
    out["arc_buckets"] = buckets
    return out


def attach_type_preds_to_buckets(
    metrics: dict,
    type_id: np.ndarray,
    type_pred: np.ndarray,
    arc_deg: np.ndarray,
    is_closed: np.ndarray,
) -> dict:
    circ_ell = (type_id == 1) | (type_id == 2)
    buckets = metrics.get("arc_buckets", {})
    defs = {
        "closed": circ_ell & is_closed.astype(bool),
        "lt15": circ_ell & (~is_closed.astype(bool)) & (arc_deg >= 0) & (arc_deg < 15),
        "15_45": circ_ell & (~is_closed.astype(bool)) & (arc_deg >= 15) & (arc_deg < 45),
        "45_90": circ_ell & (~is_closed.astype(bool)) & (arc_deg >= 45) & (arc_deg < 90),
        "gt90": circ_ell & (~is_closed.astype(bool)) & (arc_deg >= 90) & (arc_deg < 360.01),
    }
    for name, sel in defs.items():
        if name not in buckets:
            continue
        if not sel.any():
            continue
        buckets[name]["type_acc"] = float((type_pred[sel] == type_id[sel]).mean())
        # Parameter-relevant error by dominant type in bucket
        sub_true = type_id[sel]
        # Circle normal among circles in bucket
        csel = sel & (type_id == 1)
        esel = sel & (type_id == 2)
        buckets[name]["n_circle"] = int(csel.sum())
        buckets[name]["n_ellipse"] = int(esel.sum())
    metrics["arc_buckets"] = buckets
    return metrics
