"""Eval with root-cause metrics: LINE→CIRCLE FP + top-decile FP + CIRCLE recall."""

from __future__ import annotations

import numpy as np
import torch

from curve_encoder_baseline_v1.metrics import (
    classification_metrics,
    primary_scorecard,
)
from curve_encoder_baseline_v1.losses import chamfer_l2
from curve_encoder_baseline_v1.config import PRIMARY_TYPES, TYPE_TO_ID


@torch.no_grad()
def evaluate_model(model, loader, device, spec: dict, line_p90: float) -> dict:
    model.eval()
    y_true, y_pred = [], []
    poly_lens = []
    chamfers = []
    frame = spec["frame"]

    for batch in loader:
        batch_d = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
        shape = batch_d["feats_object"] if frame == "object" else batch_d["feats_local"]
        xyz_tgt = batch_d["xyz_object"] if frame == "object" else batch_d["xyz_local"]
        out = model(
            shape,
            scale_feat=batch_d["scale_feat"] if spec["use_scale_branch"] else None,
            curv_feat=batch_d["curv_feat"] if spec["use_curvature"] else None,
        )
        pred = out["type_logits"].argmax(-1)
        y_true.append(batch_d["type_id"].cpu().numpy())
        y_pred.append(pred.cpu().numpy())
        poly_lens.append(batch_d["poly_len"].cpu().numpy())
        chamfers.append(chamfer_l2(out["recon_xyz"], xyz_tgt).cpu().numpy())

    y_true = np.concatenate(y_true)
    y_pred = np.concatenate(y_pred)
    poly_lens = np.concatenate(poly_lens)
    chamfers = np.concatenate(chamfers)

    clf = classification_metrics(y_true, y_pred)
    line_id = TYPE_TO_ID["LINE"]
    circ_id = TYPE_TO_ID["CIRCLE"]
    n_line = int((y_true == line_id).sum())
    l2c = (y_true == line_id) & (y_pred == circ_id)
    n_l2c = int(l2c.sum())
    # top-decile among LINE by length (use provided p90 threshold from same split)
    line_mask = y_true == line_id
    top = line_mask & (poly_lens >= line_p90)
    n_top = int(top.sum())
    top_fp = int((top & (y_pred == circ_id)).sum())
    circ_gt = y_true == circ_id
    circ_recall = float(((circ_gt) & (y_pred == circ_id)).sum() / max(circ_gt.sum(), 1))

    root = {
        "line_to_circle_fp": n_l2c,
        "n_line": n_line,
        "line_to_circle_rate": float(n_l2c / max(n_line, 1)),
        "top_decile_n_line": n_top,
        "top_decile_line_to_circle_fp": top_fp,
        "top_decile_line_to_circle_fp_rate": float(top_fp / max(n_top, 1)),
        "line_length_p90": float(line_p90),
        "circle_recall": circ_recall,
        "n_circle": int(circ_gt.sum()),
    }
    return {
        **clf,
        **root,
        "recon_chamfer": {
            "mean": float(chamfers.mean()) if chamfers.size else None,
            "median": float(np.median(chamfers)) if chamfers.size else None,
        },
        "n_curves": int(y_true.size),
        "type_support": {t: int((y_true == i).sum()) for i, t in enumerate(PRIMARY_TYPES)},
    }


def scorecard(m: dict) -> dict:
    base = primary_scorecard(m)
    return {
        **base,
        "line_to_circle_fp": m["line_to_circle_fp"],
        "line_to_circle_rate": m["line_to_circle_rate"],
        "top_decile_line_to_circle_fp": m["top_decile_line_to_circle_fp"],
        "top_decile_line_to_circle_fp_rate": m["top_decile_line_to_circle_fp_rate"],
        "circle_recall": m["circle_recall"],
    }
