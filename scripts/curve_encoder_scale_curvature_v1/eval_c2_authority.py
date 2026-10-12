#!/usr/bin/env python3
"""Authoritative C2 epoch-4 test suite (classification / geom / probe / NN / invariance).

Pinned checkpoint:
  ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt
  sha256 553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9
  best_epoch 4
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_encoder_baseline_v1.config import ID_TO_TYPE, PRIMARY_TYPES, TYPE_TO_ID  # noqa: E402
from curve_encoder_baseline_v1.losses import chamfer_l2  # noqa: E402
from curve_encoder_scale_curvature_v1.config import EXPERIMENTS  # noqa: E402
from curve_encoder_scale_curvature_v1.dataset import (  # noqa: E402
    ScaleCurvatureDataset,
    collate,
    curve_local_frame,
)
from curve_encoder_scale_curvature_v1.models import build_model  # noqa: E402

PINNED_CKPT = (
    ROOT / "ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"
)
PINNED_SHA256 = "553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9"
PINNED_EPOCH = 4
SPEC = EXPERIMENTS["C2"]
N_TYPES = 4
TOKEN_DIM = 256


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _stats(xs) -> dict:
    a = np.asarray(xs, dtype=np.float64).reshape(-1)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return {"n": 0, "mean": None, "median": None, "p90": None, "p95": None}
    return {
        "n": int(a.size),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)),
    }


def _angle_deg(a: np.ndarray, b: np.ndarray, *, unsigned: bool = True) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    na = np.linalg.norm(a) + 1e-12
    nb = np.linalg.norm(b) + 1e-12
    c = float(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0))
    ang = float(np.degrees(np.arccos(c)))
    if unsigned:
        ang = min(ang, 180.0 - ang)
    return ang


def classification_full(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    n = N_TYPES
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true.tolist(), y_pred.tolist()):
        cm[int(t), int(p)] += 1
    per = {}
    recs, precs, f1s = [], [], []
    tp_all = fp_all = fn_all = 0
    for i, name in enumerate(PRIMARY_TYPES):
        tp = int(cm[i, i])
        fp = int(cm[:, i].sum() - tp)
        fn = int(cm[i, :].sum() - tp)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per[name] = {
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1),
            "support": int(cm[i, :].sum()),
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }
        recs.append(rec)
        precs.append(prec)
        f1s.append(f1)
        tp_all += tp
        fp_all += fp
        fn_all += fn
    micro_p = tp_all / (tp_all + fp_all) if (tp_all + fp_all) else 0.0
    micro_r = tp_all / (tp_all + fn_all) if (tp_all + fn_all) else 0.0
    micro_f1 = (
        2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) else 0.0
    )
    labels = list(PRIMARY_TYPES)
    ell = cm[TYPE_TO_ID["ELLIPSE"]]
    bsp = cm[TYPE_TO_ID["BSPLINE"]]
    return {
        "overall_accuracy": float((y_true == y_pred).mean()) if len(y_true) else 0.0,
        "macro_f1": float(np.mean(f1s)),
        "micro_f1": float(micro_f1),
        "balanced_accuracy": float(np.mean(recs)),
        "per_type": per,
        "confusion_matrix": cm.tolist(),
        "confusion_labels": labels,
        "line_to_circle": int(cm[0, 1]),
        "circle_to_line": int(cm[1, 0]),
        "ellipse_row": {labels[j]: int(ell[j]) for j in range(n)},
        "bspline_row": {labels[j]: int(bsp[j]) for j in range(n)},
        "n_curves": int(y_true.size),
        "type_support": {t: int((y_true == i).sum()) for i, t in enumerate(PRIMARY_TYPES)},
    }


class LinearProbe(nn.Module):
    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.fc = nn.Linear(in_dim, out_dim)

    def forward(self, x):
        return self.fc(x)


class MLPProbe(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)


def load_c2(device: torch.device):
    if not PINNED_CKPT.is_file():
        raise SystemExit(f"missing pinned C2 ckpt: {PINNED_CKPT}")
    digest = sha256_file(PINNED_CKPT)
    if digest != PINNED_SHA256:
        raise SystemExit(
            f"C2 sha256 mismatch:\n  got  {digest}\n  want {PINNED_SHA256}"
        )
    ckpt = torch.load(PINNED_CKPT, map_location="cpu", weights_only=False)
    epoch = int(ckpt.get("epoch", -1))
    if epoch != PINNED_EPOCH:
        raise SystemExit(f"C2 epoch mismatch: ckpt={epoch} want={PINNED_EPOCH}")
    model = build_model(SPEC)
    model.load_state_dict(ckpt["model"])
    model.eval().to(device)
    for p in model.parameters():
        p.requires_grad_(False)
    frozen = all(not p.requires_grad for p in model.parameters())
    return model, {
        "CURVE_ENCODER_CHECKPOINT": str(PINNED_CKPT.relative_to(ROOT)),
        "CURVE_ENCODER_CHECKPOINT_SHA256": digest,
        "CURVE_ENCODER_FROZEN": frozen,
        "best_epoch": epoch,
        "spec": SPEC,
        "ckpt_val_scorecard": ckpt.get("val"),
        "exp": ckpt.get("exp"),
    }


@torch.no_grad()
def encode_split(model, split: str, device: torch.device, batch_size: int) -> dict:
    ds = ScaleCurvatureDataset(split)
    loader = DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        collate_fn=collate,
        pin_memory=device.type == "cuda",
    )
    tokens, shapes, types, params, poly = [], [], [], [], []
    pred_types, pred_params, recon, xyz_local = [], [], [], []
    for batch in loader:
        batch = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
        shape = batch["feats_local"]
        scale = batch["scale_feat"]
        h = model.shape_enc(shape)
        z_parts = [h, model.scale_mlp(scale)]
        z = model.fuse(torch.cat(z_parts, dim=-1))
        type_logits = model.type_head(z)
        recon_xyz = model.recon_head(z)
        param = model.param_head(z)
        tokens.append(z.float().cpu().numpy())
        shapes.append(h.float().cpu().numpy())
        types.append(batch["type_id"].cpu().numpy())
        params.append(batch["param"].cpu().numpy())
        poly.append(batch["poly_len"].cpu().numpy())
        pred_types.append(type_logits.argmax(-1).cpu().numpy())
        pred_params.append(param.float().cpu().numpy())
        recon.append(recon_xyz.float().cpu().numpy())
        xyz_local.append(batch["xyz_local"].cpu().numpy())
    return {
        "token": np.concatenate(tokens).astype(np.float32),
        "shape_h": np.concatenate(shapes).astype(np.float32),
        "type_id": np.concatenate(types).astype(np.int64),
        "param": np.concatenate(params).astype(np.float32),
        "poly_len": np.concatenate(poly).astype(np.float32),
        "pred_type": np.concatenate(pred_types).astype(np.int64),
        "pred_param": np.concatenate(pred_params).astype(np.float32),
        "recon_xyz": np.concatenate(recon).astype(np.float32),
        "xyz_local": np.concatenate(xyz_local).astype(np.float32),
        "line_length_p90": float(ds.line_length_p90),
        "xyz": ds.xyz.astype(np.float32),
        "tangent": ds.tangent.astype(np.float32),
        "s": ds.s.astype(np.float32),
        "log_len": ds.log_len.astype(np.float32),
    }


def test1(pack: dict) -> dict:
    y_true = pack["type_id"]
    y_pred = pack["pred_type"]
    clf = classification_full(y_true, y_pred)
    line_id, circ_id = TYPE_TO_ID["LINE"], TYPE_TO_ID["CIRCLE"]
    n_line = int((y_true == line_id).sum())
    l2c = int(((y_true == line_id) & (y_pred == circ_id)).sum())
    c2l = int(((y_true == circ_id) & (y_pred == line_id)).sum())
    top = (y_true == line_id) & (pack["poly_len"] >= pack["line_length_p90"])
    top_fp = int((top & (y_pred == circ_id)).sum())
    clf.update(
        {
            "line_to_circle_fp": l2c,
            "line_to_circle_rate": float(l2c / max(n_line, 1)),
            "circle_to_line_fp": c2l,
            "circle_to_line_rate": float(c2l / max(int((y_true == circ_id).sum()), 1)),
            "top_decile_n_line": int(top.sum()),
            "top_decile_line_to_circle_fp": top_fp,
            "top_decile_line_to_circle_fp_rate": float(top_fp / max(int(top.sum()), 1)),
            "line_length_p90": float(pack["line_length_p90"]),
        }
    )
    return clf


def test2(pack: dict, device: torch.device, batch_size: int) -> dict:
    y_true = pack["type_id"]
    pred_p = pack["pred_param"]
    gt_p = pack["param"]
    recon = pack["recon_xyz"]
    xyz = pack["xyz_local"]
    geom = {
        "line_direction_err_deg": [],
        "circle_center_err": [],
        "circle_normal_err_deg": [],
        "circle_radius_err": [],
        "circle_radius_rel_err": [],
        "ellipse_center_err": [],
        "ellipse_major_axis_err_deg": [],
        "ellipse_minor_axis_err_deg": [],
        "ellipse_major_r_err": [],
        "ellipse_minor_r_err": [],
        "ellipse_major_r_rel_err": [],
        "ellipse_minor_r_rel_err": [],
    }
    for i, t in enumerate(y_true.tolist()):
        pp, gp = pred_p[i], gt_p[i]
        if t == 0:
            geom["line_direction_err_deg"].append(_angle_deg(pp[0:3], gp[0:3]))
        elif t == 1:
            geom["circle_center_err"].append(float(np.linalg.norm(pp[0:3] - gp[0:3])))
            geom["circle_normal_err_deg"].append(_angle_deg(pp[3:6], gp[3:6]))
            geom["circle_radius_err"].append(float(abs(pp[6] - gp[6])))
            geom["circle_radius_rel_err"].append(
                float(abs(pp[6] - gp[6]) / (abs(gp[6]) + 1e-6))
            )
        elif t == 2:
            geom["ellipse_center_err"].append(float(np.linalg.norm(pp[0:3] - gp[0:3])))
            geom["ellipse_major_axis_err_deg"].append(_angle_deg(pp[3:6], gp[3:6]))
            geom["ellipse_minor_axis_err_deg"].append(_angle_deg(pp[6:9], gp[6:9]))
            geom["ellipse_major_r_err"].append(float(abs(pp[9] - gp[9])))
            geom["ellipse_minor_r_err"].append(float(abs(pp[10] - gp[10])))
            geom["ellipse_major_r_rel_err"].append(
                float(abs(pp[9] - gp[9]) / (abs(gp[9]) + 1e-6))
            )
            geom["ellipse_minor_r_rel_err"].append(
                float(abs(pp[10] - gp[10]) / (abs(gp[10]) + 1e-6))
            )

    chamfers = []
    ordered_mse = []
    ordered_rmse = []
    xt = torch.from_numpy(xyz)
    rt = torch.from_numpy(recon)
    for s in range(0, len(xt), batch_size):
        a = rt[s : s + batch_size].to(device)
        b = xt[s : s + batch_size].to(device)
        chamfers.append(chamfer_l2(a, b).cpu().numpy())
        mse = ((a - b) ** 2).mean(dim=(1, 2)).cpu().numpy()
        ordered_mse.append(mse)
        ordered_rmse.append(np.sqrt(mse))
    chamfers = np.concatenate(chamfers)
    ordered_mse = np.concatenate(ordered_mse)
    ordered_rmse = np.concatenate(ordered_rmse)

    per_type_recon = {}
    for i, name in enumerate(PRIMARY_TYPES):
        m = y_true == i
        per_type_recon[name] = {
            "chamfer": _stats(chamfers[m]),
            "ordered_mse": _stats(ordered_mse[m]),
            "ordered_rmse": _stats(ordered_rmse[m]),
        }
    return {
        "frame_note": (
            "C2 recon is supervised in curve-local frame "
            "(center + bbox-extent scale). Param head is supervised in "
            "object-normalized analytic param space from frozen_v1 cache."
        ),
        "geom": {k: _stats(v) for k, v in geom.items()},
        "recon": {
            "chamfer": _stats(chamfers),
            "ordered_mse": _stats(ordered_mse),
            "ordered_rmse": _stats(ordered_rmse),
            "per_type": per_type_recon,
        },
    }


def _make_loader(x, y, batch_size, shuffle):
    ds = TensorDataset(
        torch.from_numpy(np.asarray(x, dtype=np.float32)),
        torch.from_numpy(np.asarray(y)),
    )
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, drop_last=False)


def _train_probe(
    probe: nn.Module,
    train_x,
    train_y,
    val_x,
    val_y,
    *,
    task: str,
    device: torch.device,
    epochs: int,
    batch_size: int,
    lr: float,
) -> dict:
    probe = probe.to(device)
    opt = torch.optim.AdamW(probe.parameters(), lr=lr, weight_decay=1e-4)
    y_dtype = torch.long if task == "type" else torch.float32
    tr = _make_loader(train_x, np.asarray(train_y), batch_size, True)
    va_x = torch.from_numpy(np.asarray(val_x, dtype=np.float32)).to(device)
    va_y = torch.from_numpy(np.asarray(val_y)).to(device)
    if task != "type":
        va_y = va_y.float()
    else:
        va_y = va_y.long()

    best = {"score": -1e18, "state": None, "epoch": 0}
    history = []
    for epoch in range(1, epochs + 1):
        probe.train()
        total = 0.0
        n = 0
        for xb, yb in tr:
            xb = xb.to(device)
            yb = yb.to(device)
            if task != "type":
                yb = yb.float()
            else:
                yb = yb.long()
            pred = probe(xb)
            if task == "type":
                loss = F.cross_entropy(pred, yb)
            elif task == "direction":
                pred_n = F.normalize(pred, dim=-1, eps=1e-6)
                gt_n = F.normalize(yb, dim=-1, eps=1e-6)
                d1 = ((pred_n - gt_n) ** 2).sum(-1)
                d2 = ((pred_n + gt_n) ** 2).sum(-1)
                loss = torch.minimum(d1, d2).mean()
            else:
                loss = F.smooth_l1_loss(pred.squeeze(-1), yb.reshape(-1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            bs = xb.size(0)
            total += float(loss.detach()) * bs
            n += bs
        probe.eval()
        with torch.no_grad():
            vp = probe(va_x)
            if task == "type":
                pred = vp.argmax(-1).cpu().numpy()
                yt = va_y.cpu().numpy()
                score = classification_full(yt, pred)["macro_f1"]
            elif task == "direction":
                pp = vp.cpu().numpy()
                gg = va_y.cpu().numpy()
                angs = [_angle_deg(pp[i], gg[i]) for i in range(len(pp))]
                score = -float(np.mean(angs)) if angs else -1e9
            else:
                err = (vp.squeeze(-1) - va_y.reshape(-1)).abs().mean().item()
                score = -float(err)
        history.append({"epoch": epoch, "train_loss": total / max(n, 1), "val_score": score})
        if score > best["score"]:
            best = {
                "score": score,
                "state": {k: v.detach().cpu().clone() for k, v in probe.state_dict().items()},
                "epoch": epoch,
            }
    probe.load_state_dict(best["state"])
    probe.eval()
    return {"probe": probe, "best_epoch": best["epoch"], "history": history}


@torch.no_grad()
def _eval_probe(probe, x, y, task: str, device: torch.device) -> dict:
    probe.eval()
    xt = torch.from_numpy(np.asarray(x, dtype=np.float32)).to(device)
    pred = probe(xt).cpu().numpy()
    y = np.asarray(y)
    if task == "type":
        yhat = pred.argmax(-1)
        out = classification_full(y.astype(np.int64), yhat.astype(np.int64))
        majority = int(np.bincount(y.astype(np.int64), minlength=N_TYPES).argmax())
        maj_pred = np.full_like(y, majority)
        out["majority_baseline_macro_f1"] = classification_full(
            y.astype(np.int64), maj_pred.astype(np.int64)
        )["macro_f1"]
        out["majority_baseline_class"] = ID_TO_TYPE[majority]
        return out
    if task == "direction":
        angs = np.array([_angle_deg(pred[i], y[i]) for i in range(len(y))], dtype=np.float64)
        return {"angular_err_deg": _stats(angs)}
    pred = pred.reshape(-1)
    y = y.reshape(-1)
    abs_err = np.abs(pred - y)
    rel = abs_err / (np.abs(y) + 1e-6)
    if len(pred) > 2:
        pearson = float(np.corrcoef(pred, y)[0, 1])
    else:
        pearson = None
    return {
        "abs_err": _stats(abs_err),
        "rel_err": _stats(rel),
        "pred": {"mean": float(pred.mean()), "std": float(pred.std())},
        "gt": {"mean": float(y.mean()), "std": float(y.std())},
        "pearson": pearson,
    }


def test3(packs: dict, device: torch.device, args) -> dict:
    """Frozen-token probes. C2 is never updated."""
    results = {"note": "C2 frozen. Probes trained on train tokens, selected on val, reported on test."}
    tasks = []

    def _xy(split, token_key, mask_fn, y_fn):
        p = packs[split]
        m = mask_fn(p)
        return p[token_key][m], y_fn(p)[m]

    tasks.append(("type", "token", lambda p: np.ones(len(p["type_id"]), bool), lambda p: p["type_id"], 4, "type"))
    tasks.append(("length_log", "token", lambda p: np.ones(len(p["type_id"]), bool), lambda p: p["log_len"][:, 0], 1, "reg"))
    tasks.append(("length_log_shape_only", "shape_h", lambda p: np.ones(len(p["type_id"]), bool), lambda p: p["log_len"][:, 0], 1, "reg"))
    tasks.append(("radius_circle", "token", lambda p: p["type_id"] == 1, lambda p: p["param"][:, 6], 1, "reg"))
    tasks.append(("direction_line", "token", lambda p: p["type_id"] == 0, lambda p: p["param"][:, 0:3], 3, "direction"))

    out = {}
    for name, token_key, mask_fn, y_fn, out_dim, kind in tasks:
        tr_x, tr_y = _xy("train", token_key, mask_fn, y_fn)
        va_x, va_y = _xy("val", token_key, mask_fn, y_fn)
        te_x, te_y = _xy("test", token_key, mask_fn, y_fn)
        task_kind = "type" if kind == "type" else ("direction" if kind == "direction" else "reg")
        row = {
            "token_source": token_key,
            "n_train": int(len(tr_x)),
            "n_val": int(len(va_x)),
            "n_test": int(len(te_x)),
        }
        if kind == "reg":
            mean_tr = float(np.mean(tr_y))
            naive = np.full_like(np.asarray(te_y, dtype=np.float64), mean_tr)
            abs_err = np.abs(naive - np.asarray(te_y, dtype=np.float64))
            rel = abs_err / (np.abs(te_y) + 1e-6)
            row["mean_baseline"] = {
                "train_mean": mean_tr,
                "abs_err": _stats(abs_err),
                "rel_err": _stats(rel),
            }
        elif kind == "direction":
            # naive: train mean direction
            m = np.mean(np.asarray(tr_y), axis=0)
            angs = [_angle_deg(m, te_y[i]) for i in range(len(te_y))]
            row["mean_baseline"] = {"angular_err_deg": _stats(angs)}

        for arch, ctor in (("linear", LinearProbe), ("mlp2", MLPProbe)):
            probe = ctor(TOKEN_DIM, out_dim)
            trained = _train_probe(
                probe,
                tr_x,
                tr_y,
                va_x,
                va_y,
                task=task_kind,
                device=device,
                epochs=args.probe_epochs,
                batch_size=args.probe_batch_size,
                lr=args.probe_lr,
            )
            ev = _eval_probe(trained["probe"], te_x, te_y, task_kind, device)
            row[arch] = {
                "best_val_epoch": trained["best_epoch"],
                "test": ev,
            }
            del trained
        out[name] = row
        print(f"[test3] {name} n_test={row['n_test']}", flush=True)
    results["tasks"] = out
    return results


@torch.no_grad()
def test4(packs: dict, device: torch.device, k: int = 5, n_examples: int = 8) -> dict:
    train = packs["train"]
    test = packs["test"]
    tr = F.normalize(torch.from_numpy(train["token"]).to(device), dim=-1)
    te = F.normalize(torch.from_numpy(test["token"]).to(device), dim=-1)
    n_q = te.size(0)
    all_idx = torch.empty((n_q, k), dtype=torch.long)
    all_sim = torch.empty((n_q, k), dtype=torch.float32)
    bs = 256
    for s in range(0, n_q, bs):
        q = te[s : s + bs]
        sim = q @ tr.T
        top = sim.topk(k, dim=-1)
        all_idx[s : s + bs] = top.indices.cpu()
        all_sim[s : s + bs] = top.values.cpu()
    nn_idx = all_idx.numpy()
    nn_sim = all_sim.numpy()
    tr_type = train["type_id"]
    te_type = test["type_id"]
    tr_len = train["poly_len"]
    te_len = test["poly_len"]
    tr_rad = train["param"][:, 6]
    te_rad = test["param"][:, 6]

    type_match_at1 = (tr_type[nn_idx[:, 0]] == te_type)
    type_match_at5 = np.array(
        [np.any(tr_type[nn_idx[i]] == te_type[i]) for i in range(n_q)]
    )
    maj5 = np.array(
        [
            int(np.bincount(tr_type[nn_idx[i]], minlength=N_TYPES).argmax())
            for i in range(n_q)
        ]
    )
    per_type = {}
    for i, name in enumerate(PRIMARY_TYPES):
        m = te_type == i
        if not m.any():
            continue
        rel_len = np.abs(tr_len[nn_idx[m, 0]] - te_len[m]) / (te_len[m] + 1e-6)
        row = {
            "n": int(m.sum()),
            "type_match@1": float(type_match_at1[m].mean()),
            "type_match@5_any": float(type_match_at5[m].mean()),
            "type_match@5_majority": float((maj5[m] == i).mean()),
            "nn1_cosine": _stats(nn_sim[m, 0]),
            "nn1_length_rel_err": _stats(rel_len),
        }
        if name == "CIRCLE":
            same = tr_type[nn_idx[m, 0]] == 1
            rad_q = te_rad[m]
            rad_n = tr_rad[nn_idx[m, 0]]
            rel_r = np.abs(rad_n - rad_q) / (np.abs(rad_q) + 1e-6)
            row["nn1_is_circle"] = float(same.mean())
            row["nn1_radius_rel_err_all"] = _stats(rel_r)
            row["nn1_radius_rel_err_when_circle"] = _stats(rel_r[same])
        per_type[name] = row

    rng = np.random.default_rng(0)
    examples = []
    for i, name in enumerate(PRIMARY_TYPES):
        idx = np.where(te_type == i)[0]
        if idx.size == 0:
            continue
        pick = rng.choice(idx, size=min(n_examples, idx.size), replace=False)
        for qid in pick:
            neigh = []
            for j in range(k):
                nid = int(nn_idx[qid, j])
                item = {
                    "rank": j + 1,
                    "cosine": float(nn_sim[qid, j]),
                    "type": ID_TO_TYPE[int(tr_type[nid])],
                    "length": float(tr_len[nid]),
                }
                if int(tr_type[nid]) == 1:
                    item["radius"] = float(tr_rad[nid])
                neigh.append(item)
            ex = {
                "query_type": name,
                "query_length": float(te_len[qid]),
                "neighbors": neigh,
            }
            if i == 1:
                ex["query_radius"] = float(te_rad[qid])
            examples.append(ex)
    return {
        "k": k,
        "n_train": int(len(tr_type)),
        "n_test": int(n_q),
        "overall": {
            "type_match@1": float(type_match_at1.mean()),
            "type_match@5_any": float(type_match_at5.mean()),
            "type_match@5_majority": float((maj5 == te_type).mean()),
            "nn1_cosine": _stats(nn_sim[:, 0]),
        },
        "per_type": per_type,
        "examples": examples,
    }


def _random_rotation(rng: np.random.Generator) -> np.ndarray:
    a = rng.normal(size=(3, 3))
    q, r = np.linalg.qr(a)
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q.astype(np.float32)


def _polyline_len(xyz: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())


def _feats_from_xyz_tan(xyz: np.ndarray, tan: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    local, _, _ = curve_local_frame(xyz)
    n = xyz.shape[0]
    s = np.linspace(0.0, 1.0, n, dtype=np.float32).reshape(n, 1)
    feats = np.concatenate([local, tan.astype(np.float32), s], axis=-1).astype(np.float32)
    length = _polyline_len(xyz)
    log_len = np.array([math.log(length + 1e-6)], dtype=np.float32)
    return feats, log_len, length


@torch.no_grad()
def _encode_feats(model, feats, log_len, device):
    x = torch.from_numpy(feats).to(device)
    s = torch.from_numpy(log_len).to(device)
    h = model.shape_enc(x)
    z = model.fuse(torch.cat([h, model.scale_mlp(s)], dim=-1))
    return (
        F.normalize(z, dim=-1).cpu().numpy(),
        F.normalize(h, dim=-1).cpu().numpy(),
        z.cpu().numpy(),
        h.cpu().numpy(),
    )


def test5(model, pack: dict, device: torch.device, per_type: int = 256) -> dict:
    rng = np.random.default_rng(0)
    xyz_all = pack["xyz"]
    tan_all = pack["tangent"]
    y = pack["type_id"]
    chosen = []
    for t in range(N_TYPES):
        idx = np.where(y == t)[0]
        if idx.size == 0:
            continue
        take = min(per_type, idx.size)
        chosen.extend(rng.choice(idx, size=take, replace=False).tolist())
    chosen = np.asarray(chosen, dtype=np.int64)

    xyz = xyz_all[chosen]
    tan = tan_all[chosen]
    types = y[chosen]
    n = len(chosen)
    identity_feats = []
    identity_log = []
    for i in range(n):
        f, lg, _ = _feats_from_xyz_tan(xyz[i], tan[i])
        identity_feats.append(f)
        identity_log.append(lg)
    identity_feats = np.stack(identity_feats, 0)
    identity_log = np.stack(identity_log, 0)
    z0, h0, _, _ = _encode_feats(model, identity_feats, identity_log, device)

    # Compare vs dataset features (stored local xyz + stored s) as pipeline check.
    ds_feats = np.concatenate(
        [pack["xyz_local"][chosen], tan, pack["s"][chosen]], axis=-1
    ).astype(np.float32)
    ds_log = pack["log_len"][chosen]
    z_ds, _, _, _ = _encode_feats(model, ds_feats, ds_log, device)
    ident_vs_ds = np.sum(z0 * z_ds, axis=-1)

    perturbations = {}

    def _apply(name, xyz_p, tan_p, types_mask=None):
        feats, logs = [], []
        keep = np.ones(n, dtype=bool) if types_mask is None else types_mask
        idxs = np.where(keep)[0]
        for i in idxs:
            f, lg, _ = _feats_from_xyz_tan(xyz_p[i], tan_p[i])
            feats.append(f)
            logs.append(lg)
        if not feats:
            perturbations[name] = {"n": 0}
            return
        feats = np.stack(feats, 0)
        logs = np.stack(logs, 0)
        zp, hp, _, _ = _encode_feats(model, feats, logs, device)
        cos_z = np.sum(z0[keep] * zp, axis=-1)
        cos_h = np.sum(h0[keep] * hp, axis=-1)
        row = {
            "n": int(keep.sum()),
            "fused_token_cosine": _stats(cos_z),
            "shape_token_cosine": _stats(cos_h),
            "per_type": {},
        }
        for ti, tname in enumerate(PRIMARY_TYPES):
            m = types[keep] == ti
            if m.any():
                row["per_type"][tname] = {
                    "n": int(m.sum()),
                    "fused_token_cosine": _stats(cos_z[m]),
                    "shape_token_cosine": _stats(cos_h[m]),
                }
        perturbations[name] = row

    offset = np.array([10.0, -7.0, 4.0], dtype=np.float32)
    _apply("translate", xyz + offset, tan)

    xyz_rot = np.empty_like(xyz)
    tan_rot = np.empty_like(tan)
    for i in range(n):
        r = _random_rotation(rng)
        xyz_rot[i] = xyz[i] @ r.T
        tan_rot[i] = tan[i] @ r.T
    _apply("rotate", xyz_rot, tan_rot)

    xyz_rev = xyz[:, ::-1, :].copy()
    tan_rev = -tan[:, ::-1, :].copy()
    _apply("reverse", xyz_rev, tan_rev)

    closed = np.zeros(n, dtype=bool)
    for i in range(n):
        if types[i] in (1, 2):
            closed[i] = True
            continue
        chord = float(np.linalg.norm(xyz[i, -1] - xyz[i, 0]))
        plen = _polyline_len(xyz[i])
        closed[i] = plen > 1e-8 and (chord / plen) < 0.05
    shift = 8
    xyz_roll = np.roll(xyz, shift=-shift, axis=1)
    tan_roll = np.roll(tan, shift=-shift, axis=1)
    _apply("resample_start_shift8", xyz_roll, tan_roll, closed)

    _apply("scale_x2", xyz * 2.0, tan)

    return {
        "design_note": {
            "local_frame": "center + max-bbox-extent scale; NO rotational canonicalization",
            "expected_translate": "fused and shape tokens ~invariant",
            "expected_rotate": "NOT invariant (orientation is kept in local xyz + object-frame tangents)",
            "expected_reverse": "not guaranteed; s and tangent both flip",
            "expected_resample_start": "PointNet is permutation-invariant but s is arc-parameter; closed curves may move",
            "expected_scale_x2": "shape token ~invariant; fused token should change via log(length)",
        },
        "n_sampled": int(n),
        "per_type_requested": per_type,
        "identity_vs_dataset_feats_cosine": _stats(ident_vs_ds),
        "perturbations": perturbations,
    }


def _fmt_stats(s: dict, nd=4) -> str:
    if not s or s.get("n", 0) == 0:
        return "n=0"
    return (
        f"n={s['n']} mean={s['mean']:.{nd}f} median={s['median']:.{nd}f} "
        f"p90={s['p90']:.{nd}f} p95={s['p95']:.{nd}f}"
    )


def _json_dump(path: Path, obj) -> None:
    def _conv(x):
        if isinstance(x, dict):
            return {k: _conv(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [_conv(v) for v in x]
        if isinstance(x, (np.floating, float)):
            v = float(x)
            return None if not math.isfinite(v) else v
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, np.ndarray):
            return _conv(x.tolist())
        return x

    path.write_text(json.dumps(_conv(obj), indent=2, ensure_ascii=False) + "\n")


def _probe_line(task_name: str, row: dict) -> list[str]:
    lines = [f"### {task_name}  (token=`{row['token_source']}`, n_test={row['n_test']})"]
    for arch in ("linear", "mlp2"):
        ev = row[arch]["test"]
        prefix = f"- **{arch}** (val-best epoch {row[arch]['best_val_epoch']})"
        if "macro_f1" in ev:
            lines.append(
                f"{prefix}: macro F1={ev['macro_f1']:.4f}  micro F1={ev['micro_f1']:.4f}  "
                f"LINE F1={ev['per_type']['LINE']['f1']:.3f}  "
                f"CIRCLE F1={ev['per_type']['CIRCLE']['f1']:.3f}  "
                f"ELLIPSE F1={ev['per_type']['ELLIPSE']['f1']:.3f}  "
                f"BSPLINE F1={ev['per_type']['BSPLINE']['f1']:.3f}"
            )
            lines.append(
                f"  majority baseline macro F1={ev['majority_baseline_macro_f1']:.4f} "
                f"({ev['majority_baseline_class']})"
            )
        elif "angular_err_deg" in ev:
            lines.append(f"{prefix}: angular err deg `{_fmt_stats(ev['angular_err_deg'])}`")
        else:
            extra = f" pearson={ev['pearson']:.4f}" if ev.get("pearson") is not None else ""
            lines.append(
                f"{prefix}: abs `{_fmt_stats(ev['abs_err'])}`  rel `{_fmt_stats(ev['rel_err'])}`{extra}"
            )
    if "mean_baseline" in row:
        b = row["mean_baseline"]
        if "angular_err_deg" in b:
            lines.append(f"- mean baseline angular err: `{_fmt_stats(b['angular_err_deg'])}`")
        else:
            lines.append(
                f"- mean baseline abs `{_fmt_stats(b['abs_err'])}`  rel `{_fmt_stats(b['rel_err'])}`"
            )
    lines.append("")
    return lines


def write_report(out_dir: Path, provenance: dict, t1: dict, t2: dict, t3: dict, t4: dict, t5: dict) -> None:
    lines = []
    a = lines.append
    a("# C2 epoch 4 权威评测报告")
    a("")
    a("本报告只使用 provenance 已核对的 C2 checkpoint，不沿用旧 D1/C2 混乱结果。")
    a("")
    a("## Provenance")
    a("")
    a(f"- checkpoint: `{provenance['CURVE_ENCODER_CHECKPOINT']}`")
    a(f"- sha256: `{provenance['CURVE_ENCODER_CHECKPOINT_SHA256']}`")
    a(f"- best_epoch: **{provenance['best_epoch']}**")
    a(f"- frozen: `{provenance['CURVE_ENCODER_FROZEN']}`")
    a(f"- spec: {provenance['spec']['desc']}")
    a(f"- token: fused 256-D (`out['token']`), 即送给 SpatialLM 的向量")
    a("")
    a("## Test 1 — Intrinsic classification")
    a("")
    a(f"- n_curves = {t1['n_curves']}")
    a(f"- support: {t1['type_support']}")
    a("")
    a("| type | precision | recall | F1 | support |")
    a("| --- | ---: | ---: | ---: | ---: |")
    for name in PRIMARY_TYPES:
        p = t1["per_type"][name]
        a(
            f"| {name} | {p['precision']:.4f} | {p['recall']:.4f} | {p['f1']:.4f} | {p['support']} |"
        )
    a("")
    a(f"- **Macro F1** = {t1['macro_f1']:.4f}")
    a(f"- **Micro F1** = {t1['micro_f1']:.4f} （单标签多分类下等于 overall accuracy {t1['overall_accuracy']:.4f}）")
    a(f"- Balanced accuracy = {t1['balanced_accuracy']:.4f}")
    a("")
    a("Confusion（行=GT，列=Pred，顺序 LINE / CIRCLE / ELLIPSE / BSPLINE）:")
    a("")
    a("```")
    a(json.dumps(t1["confusion_matrix"], indent=2))
    a("```")
    a("")
    a(f"- **LINE→CIRCLE** = {t1['line_to_circle']}  (rate {t1['line_to_circle_rate']:.6f})")
    a(f"- **CIRCLE→LINE** = {t1['circle_to_line']}  (rate {t1['circle_to_line_rate']:.6f})")
    a(f"- **ELLIPSE row** = {t1['ellipse_row']}")
    a(f"- **BSPLINE row** = {t1['bspline_row']}")
    a("")
    a("## Test 2 — Param / Recon geometry")
    a("")
    a(t2["frame_note"])
    a("")
    a("### LINE")
    a(f"- direction error (deg, unsigned): `{_fmt_stats(t2['geom']['line_direction_err_deg'])}`")
    a("")
    a("### CIRCLE")
    a(f"- center error: `{_fmt_stats(t2['geom']['circle_center_err'])}`")
    a(f"- normal angular error (deg): `{_fmt_stats(t2['geom']['circle_normal_err_deg'])}`")
    a(f"- radius error (abs): `{_fmt_stats(t2['geom']['circle_radius_err'])}`")
    a(f"- radius relative error: `{_fmt_stats(t2['geom']['circle_radius_rel_err'])}`")
    a("")
    a("### ELLIPSE")
    a(f"- center error: `{_fmt_stats(t2['geom']['ellipse_center_err'])}`")
    a(f"- major radius abs / rel: `{_fmt_stats(t2['geom']['ellipse_major_r_err'])}` / `{_fmt_stats(t2['geom']['ellipse_major_r_rel_err'])}`")
    a(f"- minor radius abs / rel: `{_fmt_stats(t2['geom']['ellipse_minor_r_err'])}` / `{_fmt_stats(t2['geom']['ellipse_minor_r_rel_err'])}`")
    a(f"- major-axis orientation (deg): `{_fmt_stats(t2['geom']['ellipse_major_axis_err_deg'])}`")
    a(f"- minor-axis orientation (deg): `{_fmt_stats(t2['geom']['ellipse_minor_axis_err_deg'])}`")
    a("")
    a("### Reconstruction (curve-local frame)")
    a(f"- Chamfer: `{_fmt_stats(t2['recon']['chamfer'])}`")
    a(f"- ordered MSE: `{_fmt_stats(t2['recon']['ordered_mse'])}`")
    a(f"- ordered RMSE: `{_fmt_stats(t2['recon']['ordered_rmse'])}`")
    a("")
    a("| type | chamfer mean/median/p90/p95 | ordered MSE mean/median |")
    a("| --- | --- | --- |")
    for name in PRIMARY_TYPES:
        c = t2["recon"]["per_type"][name]["chamfer"]
        o = t2["recon"]["per_type"][name]["ordered_mse"]
        if c["n"] == 0:
            a(f"| {name} | n=0 | n=0 |")
        else:
            a(
                f"| {name} | {c['mean']:.4f} / {c['median']:.4f} / {c['p90']:.4f} / {c['p95']:.4f} "
                f"| {o['mean']:.4f} / {o['median']:.4f} |"
            )
    a("")
    a("## Test 3 — Frozen 256-D token probes")
    a("")
    a("C2 全程冻结。Probe 只看 `out['token']`（除非标明 shape_only）。")
    a("`length_log_shape_only` 用来检查 scale 是否泄漏进 shape branch：若 disentangle 成功，shape token 不应轻易预测 log(length)。")
    a("")
    for name, row in t3["tasks"].items():
        lines.extend(_probe_line(name, row))
    a("## Test 4 — Nearest-neighbor sanity")
    a("")
    a(f"- gallery=train ({t4['n_train']}), query=test ({t4['n_test']}), cosine k={t4['k']}")
    a(f"- overall type_match@1 = {t4['overall']['type_match@1']:.4f}")
    a(f"- overall type_match@5 any = {t4['overall']['type_match@5_any']:.4f}")
    a(f"- overall type_match@5 majority = {t4['overall']['type_match@5_majority']:.4f}")
    a(f"- nn1 cosine: `{_fmt_stats(t4['overall']['nn1_cosine'])}`")
    a("")
    a("| type | n | type@1 | type@5 any | type@5 maj | nn1 cosine mean | length rel mean |")
    a("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for name in PRIMARY_TYPES:
        r = t4["per_type"][name]
        a(
            f"| {name} | {r['n']} | {r['type_match@1']:.3f} | {r['type_match@5_any']:.3f} | "
            f"{r['type_match@5_majority']:.3f} | {r['nn1_cosine']['mean']:.3f} | "
            f"{r['nn1_length_rel_err']['mean']:.3f} |"
        )
    if "CIRCLE" in t4["per_type"] and t4["per_type"]["CIRCLE"].get("nn1_radius_rel_err_when_circle"):
        cr = t4["per_type"]["CIRCLE"]
        a("")
        a(f"- CIRCLE nn1 is CIRCLE: {cr['nn1_is_circle']:.3f}")
        a(f"- CIRCLE nn1 radius rel-err (when neighbor is CIRCLE): `{_fmt_stats(cr['nn1_radius_rel_err_when_circle'])}`")
    a("")
    a("抽样 examples 见 `test4_nn.json`。")
    a("")
    a("## Test 5 — Invariance")
    a("")
    a(f"- identity vs dataset feature pipeline cosine: `{_fmt_stats(t5['identity_vs_dataset_feats_cosine'])}`")
    a("")
    a("| perturbation | n | fused cosine mean/median/p90 | shape cosine mean/median/p90 |")
    a("| --- | ---: | --- | --- |")
    for name, row in t5["perturbations"].items():
        if row.get("n", 0) == 0:
            a(f"| {name} | 0 | — | — |")
            continue
        f = row["fused_token_cosine"]
        s = row["shape_token_cosine"]
        a(
            f"| {name} | {row['n']} | {f['mean']:.4f} / {f['median']:.4f} / {f['p90']:.4f} "
            f"| {s['mean']:.4f} / {s['median']:.4f} / {s['p90']:.4f} |"
        )
    a("")
    a("设计预期：")
    for k, v in t5["design_note"].items():
        a(f"- {k}: {v}")
    a("")
    a("## 怎么读这些数")
    a("")
    a("- Test 1 只说明 type head。Type 好、Param/Recon 差 → 更像 classifier。")
    a("- Test 2 看 param/recon 是否留下几何。")
    a("- Test 3 看 **token 本身** 有没有 CAD 几何，不依赖 C2 自己的 head。")
    a("- fused token 预测 length 容易是预期内的（scale branch 显式注入了 log-length）。")
    a("- shape-only 预测 length 若也很容易，则 shape/scale 分离不干净。")
    a("- Test 4 / 5 是 sanity，不是论文主表。")
    a("")
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--probe-epochs", type=int, default=20)
    ap.add_argument("--probe-batch-size", type=int, default=2048)
    ap.add_argument("--probe-lr", type=float, default=1e-3)
    ap.add_argument("--nn-k", type=int, default=5)
    ap.add_argument("--invariance-per-type", type=int, default=256)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT
        / "ours3/curve_encoder_scale_curvature_v1/reports/C2_epoch4_authority_v1",
    )
    args = ap.parse_args()
    set_seed(0)
    device = torch.device(args.device)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    print(f"[c2-auth] device={device} out={out_dir}", flush=True)

    model, provenance = load_c2(device)
    _json_dump(out_dir / "PROVENANCE.json", provenance)
    print(json.dumps(provenance, indent=2), flush=True)

    packs = {}
    for split in ("train", "val", "test"):
        print(f"[c2-auth] encode {split}", flush=True)
        packs[split] = encode_split(model, split, device, args.batch_size)
        print(
            f"[c2-auth] {split} n={len(packs[split]['type_id'])} "
            f"token={packs[split]['token'].shape}",
            flush=True,
        )

    print("[c2-auth] Test 1", flush=True)
    t1 = test1(packs["test"])
    _json_dump(out_dir / "test1_classification.json", t1)

    print("[c2-auth] Test 2", flush=True)
    t2 = test2(packs["test"], device, args.batch_size)
    _json_dump(out_dir / "test2_param_recon.json", t2)

    print("[c2-auth] Test 3 probes", flush=True)
    t3 = test3(packs, device, args)
    _json_dump(out_dir / "test3_probe.json", t3)

    print("[c2-auth] Test 4 NN", flush=True)
    t4 = test4(packs, device, k=args.nn_k)
    _json_dump(out_dir / "test4_nn.json", t4)

    print("[c2-auth] Test 5 invariance", flush=True)
    t5 = test5(model, packs["test"], device, per_type=args.invariance_per_type)
    _json_dump(out_dir / "test5_invariance.json", t5)

    write_report(out_dir, provenance, t1, t2, t3, t4, t5)
    elapsed = time.time() - t0
    summary = {
        "seconds": elapsed,
        "test1_macro_f1": t1["macro_f1"],
        "test1_micro_f1": t1["micro_f1"],
        "test2_chamfer_mean": t2["recon"]["chamfer"]["mean"],
        "test2_line_dir_mean": t2["geom"]["line_direction_err_deg"]["mean"],
        "test2_circle_radius_rel_mean": t2["geom"]["circle_radius_rel_err"]["mean"],
    }
    _json_dump(out_dir / "SUMMARY.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    print(f"[c2-auth] wrote {out_dir / 'REPORT.md'} in {elapsed:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
