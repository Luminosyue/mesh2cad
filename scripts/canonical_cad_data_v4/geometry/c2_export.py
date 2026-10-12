"""Frozen C2 token export. Checkpoint is never trained here."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

SCRIPTS = Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from curve_encoder_baseline_v1.dataset import _normalized_s  # noqa: E402
from curve_encoder_scale_curvature_v1.config import EXPERIMENTS  # noqa: E402
from curve_encoder_scale_curvature_v1.dataset import curve_local_frame  # noqa: E402
from curve_encoder_scale_curvature_v1.models import build_model  # noqa: E402

from ..config import C2_CHECKPOINT, C2_TOKEN_DIM
from ..hashutil import sha256_file

_MODEL = None
_CKPT_META = None


def load_c2(device: str | None = None):
    global _MODEL, _CKPT_META
    if _MODEL is not None:
        return _MODEL, _CKPT_META
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    ckpt = torch.load(C2_CHECKPOINT, map_location="cpu", weights_only=False)
    if ckpt.get("exp") != "C2":
        raise ValueError(f"expected C2 checkpoint, got {ckpt.get('exp')}")
    model = build_model(EXPERIMENTS[ckpt["exp"]])
    model.load_state_dict(ckpt["model"])
    model.eval().to(dev)
    for p in model.parameters():
        p.requires_grad_(False)
    _MODEL = (model, dev)
    _CKPT_META = {
        "C2_CHECKPOINT": str(C2_CHECKPOINT),
        "C2_CHECKPOINT_SHA256": sha256_file(C2_CHECKPOINT),
        "C2_EPOCH": int(ckpt.get("epoch", ckpt.get("best_epoch", -1))),
        "C2_FROZEN": True,
        "C2_EXP": ckpt.get("exp"),
        "token_dim": C2_TOKEN_DIM,
    }
    return _MODEL, _CKPT_META


def _curve_inputs(xyz: np.ndarray, tangent: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    local, _, _ = curve_local_frame(xyz)
    s = _normalized_s(xyz.astype(np.float32), "uniform_abscissa")
    feats = np.concatenate([local, tangent.astype(np.float32), s], axis=-1).astype(np.float32)
    poly = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
    return feats, np.array([np.log(poly + 1e-6)], dtype=np.float32)


def encode_curves(curves: list[dict], device: str | None = None) -> tuple[np.ndarray, dict]:
    (model, dev), meta = load_c2(device)
    if not curves:
        tokens = np.zeros((0, C2_TOKEN_DIM), dtype=np.float32)
        out_meta = dict(meta)
        out_meta.update({"n_curves": 0, "curve_order_hash": "empty"})
        return tokens, out_meta

    feats, scales = [], []
    order_keys = []
    for c in curves:
        xyz = np.asarray(c["xyz"], dtype=np.float64)
        tan = np.asarray(c["tangent"], dtype=np.float32)
        f, sc = _curve_inputs(xyz, tan)
        feats.append(f)
        scales.append(sc)
        order_keys.append(f"{c.get('curve_id')}:{c.get('curve_type')}:{c.get('polyline_length')}")
    feats_a = np.stack(feats, 0)
    scales_a = np.stack(scales, 0)
    with torch.no_grad():
        out = model(torch.from_numpy(feats_a).to(dev), torch.from_numpy(scales_a).to(dev))
        tokens = out["token"].float().cpu().numpy().astype(np.float32)
    assert tokens.shape == (len(curves), C2_TOKEN_DIM), tokens.shape
    from ..hashutil import sha256_text

    out_meta = dict(meta)
    out_meta.update(
        {
            "n_curves": len(curves),
            "curve_order_hash": sha256_text("|".join(order_keys)),
            "shape": list(tokens.shape),
        }
    )
    return tokens, out_meta
