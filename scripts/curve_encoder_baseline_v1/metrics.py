"""Primary metrics: Macro-F1 / Balanced Acc / per-type F1 / Chamfer / geom errors."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F

from .config import ID_TO_TYPE, PRIMARY_TYPES
from .losses import chamfer_l2


def _angle_deg(a: np.ndarray, b: np.ndarray, *, unsigned: bool = True) -> float:
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    c = float(np.clip(np.dot(a, b), -1.0, 1.0))
    ang = float(np.degrees(np.arccos(c)))
    if unsigned:
        ang = min(ang, 180.0 - ang)
    return ang


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    n = len(PRIMARY_TYPES)
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true.tolist(), y_pred.tolist()):
        cm[int(t), int(p)] += 1

    per_f1 = {}
    recalls = []
    for i, name in enumerate(PRIMARY_TYPES):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_f1[f"{name}_f1"] = float(f1)
        per_f1[f"{name}_recall"] = float(rec)
        per_f1[f"{name}_precision"] = float(prec)
        recalls.append(rec)

    macro_f1 = float(np.mean([per_f1[f"{t}_f1"] for t in PRIMARY_TYPES]))
    balanced_acc = float(np.mean(recalls))
    overall_acc = float((y_true == y_pred).mean()) if len(y_true) else 0.0
    # majority baseline awareness
    majority = int(np.bincount(y_true, minlength=n).argmax()) if len(y_true) else 0
    return {
        "overall_accuracy": overall_acc,
        "macro_f1": macro_f1,
        "balanced_accuracy": balanced_acc,
        "majority_class": ID_TO_TYPE[majority],
        "confusion_matrix": cm.tolist(),
        **per_f1,
    }


@torch.no_grad()
def evaluate_model(model, loader, device: torch.device) -> dict:
    model.eval()
    y_true, y_pred = [], []
    chamfers = []
    ordered = []
    geom = defaultdict(list)

    for batch in loader:
        feats = batch["feats"].to(device)
        xyz = batch["xyz"].to(device)
        type_id = batch["type_id"].to(device)
        param = batch["param"].to(device)
        out = model(feats)
        pred_type = out["type_logits"].argmax(dim=-1)
        y_true.append(type_id.cpu().numpy())
        y_pred.append(pred_type.cpu().numpy())

        ch = chamfer_l2(out["recon_xyz"], xyz)
        chamfers.append(ch.cpu().numpy())
        ord_err = ((out["recon_xyz"] - xyz) ** 2).mean(dim=(1, 2)).sqrt().cpu().numpy()
        ordered.append(ord_err)

        pred_p = out["param"]
        tid = type_id.cpu().numpy()
        for i in range(tid.shape[0]):
            t = int(tid[i])
            pp = pred_p[i].cpu().numpy()
            gp = param[i].cpu().numpy()
            if t == 0:  # LINE
                geom["line_direction_err_deg"].append(_angle_deg(pp[0:3], gp[0:3]))
            elif t == 1:  # CIRCLE
                geom["circle_normal_err_deg"].append(_angle_deg(pp[3:6], gp[3:6]))
                geom["circle_center_err"].append(float(np.linalg.norm(pp[0:3] - gp[0:3])))
                geom["circle_radius_rel_err"].append(
                    float(abs(pp[6] - gp[6]) / (abs(gp[6]) + 1e-6))
                )
            elif t == 2:  # ELLIPSE
                geom["ellipse_major_axis_err_deg"].append(_angle_deg(pp[3:6], gp[3:6]))
                geom["ellipse_minor_axis_err_deg"].append(_angle_deg(pp[6:9], gp[6:9]))
                geom["ellipse_center_err"].append(float(np.linalg.norm(pp[0:3] - gp[0:3])))
                geom["ellipse_major_r_rel_err"].append(
                    float(abs(pp[9] - gp[9]) / (abs(gp[9]) + 1e-6))
                )
                geom["ellipse_minor_r_rel_err"].append(
                    float(abs(pp[10] - gp[10]) / (abs(gp[10]) + 1e-6))
                )

    y_true = np.concatenate(y_true) if y_true else np.zeros((0,), dtype=np.int64)
    y_pred = np.concatenate(y_pred) if y_pred else np.zeros((0,), dtype=np.int64)
    clf = classification_metrics(y_true, y_pred)
    chamfers = np.concatenate(chamfers) if chamfers else np.zeros((0,))
    ordered = np.concatenate(ordered) if ordered else np.zeros((0,))

    def _stat(xs):
        if not xs:
            return {"n": 0, "mean": None, "median": None, "p95": None}
        a = np.asarray(xs, dtype=np.float64)
        return {
            "n": int(a.size),
            "mean": float(a.mean()),
            "median": float(np.median(a)),
            "p95": float(np.percentile(a, 95)),
        }

    return {
        **clf,
        "recon_chamfer": {
            "mean": float(chamfers.mean()) if chamfers.size else None,
            "median": float(np.median(chamfers)) if chamfers.size else None,
            "p95": float(np.percentile(chamfers, 95)) if chamfers.size else None,
        },
        "recon_ordered_rmse": {
            "mean": float(ordered.mean()) if ordered.size else None,
            "median": float(np.median(ordered)) if ordered.size else None,
        },
        "geom": {k: _stat(v) for k, v in geom.items()},
        "n_curves": int(y_true.size),
        "type_support": {
            t: int((y_true == i).sum()) for i, t in enumerate(PRIMARY_TYPES)
        },
    }


def primary_scorecard(metrics: dict) -> dict:
    """Compact view of the metrics that matter (not overall accuracy)."""
    g = metrics.get("geom", {})
    return {
        "macro_f1": metrics["macro_f1"],
        "balanced_accuracy": metrics["balanced_accuracy"],
        "LINE_f1": metrics["LINE_f1"],
        "CIRCLE_f1": metrics["CIRCLE_f1"],
        "ELLIPSE_f1": metrics["ELLIPSE_f1"],
        "BSPLINE_f1": metrics["BSPLINE_f1"],
        "recon_chamfer_mean": metrics["recon_chamfer"]["mean"],
        "line_direction_err_deg_mean": (g.get("line_direction_err_deg") or {}).get("mean"),
        "circle_normal_err_deg_mean": (g.get("circle_normal_err_deg") or {}).get("mean"),
        "circle_radius_rel_err_mean": (g.get("circle_radius_rel_err") or {}).get("mean"),
        "ellipse_major_axis_err_deg_mean": (g.get("ellipse_major_axis_err_deg") or {}).get(
            "mean"
        ),
        "overall_accuracy_NOT_primary": metrics["overall_accuracy"],
    }
