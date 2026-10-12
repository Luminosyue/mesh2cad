"""Classification + reconstruction + per-type parameter metrics."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from curve_encoder_baseline_v1.losses import chamfer_l2
from curve_encoder_baseline_v1.metrics import classification_metrics

from .config import PRIMARY_TYPES, TYPE_TO_ID

LINE_ID = TYPE_TO_ID["LINE"]
CIRCLE_ID = TYPE_TO_ID["CIRCLE"]
ELLIPSE_ID = TYPE_TO_ID["ELLIPSE"]
BSPLINE_ID = TYPE_TO_ID["BSPLINE"]


def _axis_angle_deg(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    """Unsigned angle between axes (sign-ambiguous), degrees."""
    p = F.normalize(pred, dim=-1, eps=1e-9)
    g = F.normalize(gt, dim=-1, eps=1e-9)
    c = (p * g).sum(-1).abs().clamp(max=1.0)
    return torch.rad2deg(torch.arccos(c))


def _stats(v: np.ndarray) -> dict | None:
    if v.size == 0:
        return None
    return {
        "n": int(v.size),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "p90": float(np.percentile(v, 90)),
    }


@torch.no_grad()
def evaluate_model(model, loader, device, spec: dict, line_p90: float) -> dict:
    model.eval()
    use_recon = spec["use_recon"]
    use_param = spec["use_param"]

    y_true, y_pred, poly_lens, chamfers = [], [], [], []
    acc: dict[str, list[np.ndarray]] = {}

    def push(key: str, t: torch.Tensor) -> None:
        acc.setdefault(key, []).append(t.detach().cpu().numpy().reshape(-1))

    for batch in loader:
        b = {k: v.to(device) for k, v in batch.items()}
        out = model(b["shape_feats"], b["scale_feat"])
        tid = b["type_id"]
        y_true.append(tid.cpu().numpy())
        y_pred.append(out["type_logits"].argmax(-1).cpu().numpy())
        poly_lens.append(b["poly_len"].cpu().numpy())
        if use_recon:
            chamfers.append(chamfer_l2(out["recon_xyz"], b["xyz_target"]).cpu().numpy())
        if not use_param:
            continue

        m = tid == LINE_ID
        if m.any():
            p, g = out["line_param"][m], b["line_param"][m]
            push("line_dir_deg", _axis_angle_deg(p[:, 3:6], g[:, 3:6]))
            push("line_origin_dist", (p[:, 0:3] - g[:, 0:3]).norm(dim=-1))
            push("line_len_rel", (p[:, 6] - g[:, 6]).abs() / g[:, 6].abs().clamp_min(1e-3))
        m = tid == CIRCLE_ID
        if m.any():
            p, g = out["circle_param"][m], b["circle_param"][m]
            push("circle_center_dist", (p[:, 0:3] - g[:, 0:3]).norm(dim=-1))
            push("circle_normal_deg", _axis_angle_deg(p[:, 3:6], g[:, 3:6]))
            push("circle_radius_rel", (p[:, 6] - g[:, 6]).abs() / g[:, 6].abs().clamp_min(1e-3))
            push("circle_span_deg", (p[:, 11] - g[:, 11]).abs() * 360.0)
        m = tid == ELLIPSE_ID
        if m.any():
            p, g = out["ellipse_param"][m], b["ellipse_param"][m]
            push("ellipse_center_dist", (p[:, 0:3] - g[:, 0:3]).norm(dim=-1))
            push("ellipse_major_axis_deg", _axis_angle_deg(p[:, 3:6], g[:, 3:6]))
            push("ellipse_normal_deg", _axis_angle_deg(p[:, 9:12], g[:, 9:12]))
            push(
                "ellipse_r_major_rel",
                (p[:, 12] - g[:, 12]).abs() / g[:, 12].abs().clamp_min(1e-3),
            )
            push(
                "ellipse_r_minor_rel",
                (p[:, 13] - g[:, 13]).abs() / g[:, 13].abs().clamp_min(1e-3),
            )
        m = (tid == BSPLINE_ID) & (b["bspline_degree"] >= 0)
        if m.any():
            push(
                "bspline_degree_correct",
                (out["bspline_degree_logits"][m].argmax(-1) == b["bspline_degree"][m]).float(),
            )
            pred_ncp = out["bspline_logncp"][m].exp()
            gt_ncp = b["bspline_logncp"][m].exp()
            push("bspline_ncp_rel", (pred_ncp - gt_ncp).abs() / gt_ncp.clamp_min(1e-3))

    y_true = np.concatenate(y_true)
    y_pred = np.concatenate(y_pred)
    poly_lens = np.concatenate(poly_lens)

    clf = classification_metrics(y_true, y_pred)
    line_mask = y_true == LINE_ID
    n_line = int(line_mask.sum())
    n_l2c = int((line_mask & (y_pred == CIRCLE_ID)).sum())
    top = line_mask & (poly_lens >= line_p90)
    n_top = int(top.sum())
    top_fp = int((top & (y_pred == CIRCLE_ID)).sum())
    circ_gt = y_true == CIRCLE_ID

    params = {k: _stats(np.concatenate(v)) for k, v in acc.items()}
    ch = np.concatenate(chamfers) if chamfers else np.zeros((0,), dtype=np.float32)

    return {
        **clf,
        "line_to_circle_fp": n_l2c,
        "n_line": n_line,
        "line_to_circle_rate": float(n_l2c / max(n_line, 1)),
        "top_decile_n_line": n_top,
        "top_decile_line_to_circle_fp": top_fp,
        "top_decile_line_to_circle_fp_rate": float(top_fp / max(n_top, 1)),
        "line_length_p90": float(line_p90),
        "circle_recall": float((circ_gt & (y_pred == CIRCLE_ID)).sum() / max(circ_gt.sum(), 1)),
        "recon_chamfer": _stats(ch),
        "params": params,
        "n_curves": int(y_true.size),
        "type_support": {t: int((y_true == i).sum()) for i, t in enumerate(PRIMARY_TYPES)},
    }


def scorecard(m: dict) -> dict:
    out = {
        "macro_f1": m["macro_f1"],
        "balanced_accuracy": m["balanced_accuracy"],
        "LINE_f1": m["LINE_f1"],
        "CIRCLE_f1": m["CIRCLE_f1"],
        "ELLIPSE_f1": m["ELLIPSE_f1"],
        "BSPLINE_f1": m["BSPLINE_f1"],
        "overall_accuracy_NOT_primary": m["overall_accuracy"],
        "line_to_circle_fp": m["line_to_circle_fp"],
        "top_decile_line_to_circle_fp": m["top_decile_line_to_circle_fp"],
        "circle_recall": m["circle_recall"],
        "recon_chamfer_mean": (m["recon_chamfer"] or {}).get("mean"),
        "recon_chamfer_median": (m["recon_chamfer"] or {}).get("median"),
    }
    for k in (
        "line_dir_deg",
        "circle_normal_deg",
        "circle_radius_rel",
        "ellipse_major_axis_deg",
        "bspline_degree_correct",
    ):
        st = m["params"].get(k)
        out[k] = st["median"] if st else None
    return out
