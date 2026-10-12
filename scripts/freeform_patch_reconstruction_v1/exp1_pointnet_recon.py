#!/usr/bin/env python3
"""Exp1: PointNet surface-only reconstruction → true LSQ 4×4 cubic poles.

Input:  1024×6 patch points (online resample on train; fixed npy on val/test)
Output: 4×4×3 control poles in patch-local frame
Loss:   0.1 * L_ctrl + 1.0 * L_surf (Chamfer on densified surfaces)
No boundary. No LLM. No Sonata (PointNet first).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from freeform_patch_reconstruction_v1.geom import chamfer_l1, hausdorff95  # noqa: E402
from freeform_surface_pack_v1.canonical_fit import (  # noqa: E402
    evaluate_fitted_grid,
    full_knot_vector,
    tensor_basis_row,
)
from freeform_surface_pack_v1.canonical import clamped_uniform_knots  # noqa: E402
from freeform_surface_pack_v1.resample import resample_patch  # noqa: E402

DEFAULT_PACK = ROOT / "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1"
GRID = 4
DEGREE = 3
N_POLES = GRID * GRID  # 16
DENSE_EVAL = 32


def patch_normalize(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    c = xyz.mean(axis=0)
    diag = float(np.linalg.norm(xyz.max(0) - xyz.min(0)))
    s = diag if diag > 1e-12 else 1.0
    return (xyz - c) / s, c, s


def apply_norm(xyz: np.ndarray, c: np.ndarray, s: float) -> np.ndarray:
    return (xyz - c) / s


def invert_norm(xyz: np.ndarray, c: np.ndarray, s: float) -> np.ndarray:
    return xyz * s + c


class BSplineDataset(Dataset):
    def __init__(self, pack_dir: Path, split: str, *, online: bool, seed: int = 0):
        man = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
        self.ids = [s["sample_id"] for s in man["samples"] if s["split"] == split]
        self.pack_dir = pack_dir
        self.online = online
        self.seed = seed
        self.split = split
        self.epoch = 0

    def set_epoch(self, epoch: int) -> None:
        self.epoch = int(epoch)

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        sid = self.ids[idx]
        d = self.pack_dir / "samples" / sid
        if self.online:
            seed = self.seed + self.epoch * 10007 + idx * 17
            pts = resample_patch(d, seed=seed).astype(np.float32)
        else:
            pts = np.load(d / "patch_points.npy").astype(np.float32)

        xyz = pts[:, :3]
        xyz_n, c, s = patch_normalize(xyz)
        feats = np.concatenate([xyz_n, pts[:, 3:6]], axis=1).astype(np.float32)

        canon = np.load(d / "canonical_surface.npz")
        poles = np.asarray(canon["poles"], dtype=np.float64)  # (4,4,3) world
        assert poles.shape == (GRID, GRID, 3)
        poles_n = apply_norm(poles.reshape(-1, 3), c, s).reshape(GRID, GRID, 3)

        # Dense GT surface in local frame (for surf loss / metrics)
        gt_dense = evaluate_fitted_grid(poles, degree=DEGREE, nu_eval=DENSE_EVAL, nv_eval=DENSE_EVAL)
        gt_dense_n = apply_norm(gt_dense, c, s).astype(np.float32)

        return {
            "feats": torch.from_numpy(feats),
            "poles": torch.from_numpy(poles_n.astype(np.float32)),
            "gt_dense": torch.from_numpy(gt_dense_n),
            "center": torch.from_numpy(c.astype(np.float32)),
            "scale": torch.tensor(s, dtype=torch.float32),
            "sample_id": sid,
        }


def collate(batch):
    out = {k: [b[k] for b in batch] for k in batch[0]}
    for k in ("feats", "poles", "gt_dense", "center", "scale"):
        out[k] = torch.stack(out[k], 0)
    return out


class PointNetEncoder(nn.Module):
    def __init__(self, in_ch=6, width=256):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_ch, width),
            nn.ReLU(inplace=True),
            nn.Linear(width, width),
            nn.ReLU(inplace=True),
            nn.Linear(width, width),
            nn.ReLU(inplace=True),
        )
        self.out_dim = width

    def forward(self, x):
        return self.mlp(x).max(1).values


class ReconModel(nn.Module):
    def __init__(self, width=256):
        super().__init__()
        self.enc = PointNetEncoder(6, width)
        self.dec = nn.Sequential(
            nn.Linear(width, width),
            nn.ReLU(inplace=True),
            nn.Linear(width, width),
            nn.ReLU(inplace=True),
            nn.Linear(width, N_POLES * 3),
        )

    def forward(self, feats):
        z = self.enc(feats)
        return self.dec(z).view(-1, GRID, GRID, 3)


def _basis_cache(device):
    """Precompute design matrix for 32×32 eval on unit domain."""
    uk, um = clamped_uniform_knots(GRID, DEGREE)
    vk, vm = clamped_uniform_knots(GRID, DEGREE)
    ku = full_knot_vector(uk, um)
    kv = full_knot_vector(vk, vm)
    us = np.linspace(0.0, 1.0, DENSE_EVAL)
    vs = np.linspace(0.0, 1.0, DENSE_EVAL)
    A = np.zeros((DENSE_EVAL * DENSE_EVAL, N_POLES), dtype=np.float64)
    k = 0
    for u in us:
        for v in vs:
            A[k] = tensor_basis_row(float(u), float(v), DEGREE, ku, kv)
            k += 1
    return torch.from_numpy(A.astype(np.float32)).to(device)


def densify_poles(poles: torch.Tensor, A: torch.Tensor) -> torch.Tensor:
    """poles (B,4,4,3) → dense (B,M,3) via fixed basis matrix A (M,16)."""
    b = poles.shape[0]
    flat = poles.reshape(b, N_POLES, 3)
    return torch.einsum("mp,bpc->bmc", A, flat)


def chamfer_torch(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """a,b: (B,M,3) → mean bidirectional NN L2 (not squared)."""
    # (B,M,N)
    d = torch.cdist(a, b, p=2)
    return 0.5 * (d.min(-1).values.mean(-1) + d.min(-2).values.mean(-1))


def train_one_epoch(model, loader, opt, A, device, lam_ctrl=0.1, lam_surf=1.0):
    model.train()
    total = {"loss": 0.0, "ctrl": 0.0, "surf": 0.0, "n": 0}
    for batch in loader:
        feats = batch["feats"].to(device)
        poles_gt = batch["poles"].to(device)
        gt_dense = batch["gt_dense"].to(device)
        pred = model(feats)
        l_ctrl = (pred - poles_gt).abs().mean()
        pred_dense = densify_poles(pred, A)
        l_surf = chamfer_torch(pred_dense, gt_dense).mean()
        loss = lam_ctrl * l_ctrl + lam_surf * l_surf
        opt.zero_grad()
        loss.backward()
        opt.step()
        bs = feats.size(0)
        total["loss"] += float(loss) * bs
        total["ctrl"] += float(l_ctrl) * bs
        total["surf"] += float(l_surf) * bs
        total["n"] += bs
    n = max(total["n"], 1)
    return {k: total[k] / n for k in ("loss", "ctrl", "surf")}


@torch.no_grad()
def evaluate(model, loader, A, device, mean_poles=None):
    model.eval()
    rows = []
    for batch in loader:
        feats = batch["feats"].to(device)
        poles_gt = batch["poles"].to(device)
        gt_dense = batch["gt_dense"].to(device)
        centers = batch["center"].numpy()
        scales = batch["scale"].numpy()
        pred = model(feats)
        pred_dense = densify_poles(pred, A)
        for i, sid in enumerate(batch["sample_id"]):
            pg = poles_gt[i].cpu().numpy()
            pp = pred[i].cpu().numpy()
            gd = gt_dense[i].cpu().numpy()
            pd = pred_dense[i].cpu().numpy()
            # world frame for reporting
            c, s = centers[i], float(scales[i])
            gd_w = invert_norm(gd, c, s)
            pd_w = invert_norm(pd, c, s)
            cd = chamfer_l1(pd_w, gd_w)
            hd = hausdorff95(pd_w, gd_w)
            diag = float(np.linalg.norm(gd_w.max(0) - gd_w.min(0)))
            ctrl = float(np.abs(pp - pg).mean())
            row = {
                "sample_id": sid,
                "ctrl_l1": ctrl,
                "chamfer": cd,
                "chamfer_rel": cd / max(diag, 1e-12),
                "hausdorff95": hd,
                "hausdorff95_rel": hd / max(diag, 1e-12),
                "diag": diag,
            }
            if mean_poles is not None:
                mp = densify_poles(mean_poles[None].to(device), A)[0].cpu().numpy()
                mp_w = invert_norm(mp, c, s)
                row["baseline_mean_chamfer_rel"] = chamfer_l1(mp_w, gd_w) / max(diag, 1e-12)
            rows.append(row)
    return rows


def summarize(rows, split_json, pack_dir):
    if not rows:
        return {}
    cds = np.array([r["chamfer_rel"] for r in rows])
    hds = np.array([r["hausdorff95_rel"] for r in rows])
    ctrls = np.array([r["ctrl_l1"] for r in rows])
    micro = {
        "n": len(rows),
        "ctrl_l1_mean": float(ctrls.mean()),
        "chamfer_rel_mean": float(cds.mean()),
        "chamfer_rel_median": float(np.median(cds)),
        "hausdorff95_rel_mean": float(hds.mean()),
        "hausdorff95_rel_median": float(np.median(hds)),
    }
    if rows and "baseline_mean_chamfer_rel" in rows[0]:
        b = np.array([r["baseline_mean_chamfer_rel"] for r in rows])
        micro["baseline_mean_chamfer_rel_mean"] = float(b.mean())
        micro["vs_baseline_ratio"] = float(cds.mean() / max(b.mean(), 1e-12))

    # per-part macro
    man = json.loads((pack_dir / "manifest.json").read_text())
    sid_to_part = {s["sample_id"]: s["part_id"] for s in man["samples"]}
    by_part = {}
    for r in rows:
        by_part.setdefault(sid_to_part[r["sample_id"]], []).append(r["chamfer_rel"])
    part_means = [float(np.mean(v)) for v in by_part.values()]
    micro["chamfer_rel_part_macro"] = float(np.mean(part_means)) if part_means else None
    micro["n_parts"] = len(part_means)
    return micro


def save_previews(model, loader, A, device, out_dir: Path, n=20):
    out_dir.mkdir(parents=True, exist_ok=True)
    model.eval()
    shown = 0
    rows_for_rank = []
    with torch.no_grad():
        for batch in loader:
            feats = batch["feats"].to(device)
            pred = model(feats)
            pred_dense = densify_poles(pred, A)
            poles_gt = batch["poles"]
            gt_dense = batch["gt_dense"]
            for i, sid in enumerate(batch["sample_id"]):
                c = batch["center"][i].numpy()
                s = float(batch["scale"][i])
                inp = invert_norm(batch["feats"][i, :, :3].numpy(), c, s)
                gt = invert_norm(gt_dense[i].numpy(), c, s)
                pr = invert_norm(pred_dense[i].cpu().numpy(), c, s)
                pg = invert_norm(poles_gt[i].numpy().reshape(-1, 3), c, s)
                pp = invert_norm(pred[i].cpu().numpy().reshape(-1, 3), c, s)
                cd = chamfer_l1(pr, gt)
                rows_for_rank.append((cd, sid, inp, gt, pr, pg, pp))
            if len(rows_for_rank) >= 200:
                break
    rows_for_rank.sort(key=lambda x: x[0])
    picks = []
    picks += [("best", x) for x in rows_for_rank[:5]]
    mid = len(rows_for_rank) // 2
    picks += [("median", x) for x in rows_for_rank[mid - 2 : mid + 3]]
    picks += [("worst", x) for x in rows_for_rank[-5:]]
    # also random extras
    rng = np.random.default_rng(0)
    for x in rng.choice(len(rows_for_rank), size=min(5, len(rows_for_rank)), replace=False):
        picks.append(("rand", rows_for_rank[int(x)]))

    for tag, (cd, sid, inp, gt, pr, pg, pp) in picks[:n]:
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.2), dpi=120)
        for ax, pts, title, color in [
            (axes[0], inp, "input", "#2c7bb6"),
            (axes[1], gt, "GT surf", "#1a9641"),
            (axes[2], pr, "pred surf", "#d7191c"),
        ]:
            ax.scatter(pts[:, 0], pts[:, 1], s=2, c=color, alpha=0.7)
            ax.set_aspect("equal")
            ax.set_title(title, fontsize=8)
            ax.axis("off")
        fig.suptitle(f"{tag} {sid} CD={cd:.4g}", fontsize=8)
        fig.savefig(out_dir / f"{tag}_{sid}.png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
        shown += 1
    return shown


def compute_mean_poles(pack_dir: Path, train_ids: list[str]) -> torch.Tensor:
    acc = np.zeros((GRID, GRID, 3), dtype=np.float64)
    n = 0
    for sid in train_ids:
        d = pack_dir / "samples" / sid
        pts = np.load(d / "patch_points.npy")
        xyz_n, c, s = patch_normalize(pts[:, :3])
        poles = np.load(d / "canonical_surface.npz")["poles"]
        poles_n = apply_norm(poles.reshape(-1, 3), c, s).reshape(GRID, GRID, 3)
        acc += poles_n
        n += 1
    return torch.from_numpy((acc / max(n, 1)).astype(np.float32))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--lam-ctrl", type=float, default=0.1)
    ap.add_argument("--lam-surf", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", type=str, default=None)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "ours3/freeform_patch_reconstruction_v1/exp1_pointnet_recon",
    )
    args = ap.parse_args()

    # Require true-fit gate
    gate_path = args.pack_dir / "canonical_4x4_fit_gate.json"
    if gate_path.is_file():
        g = json.loads(gate_path.read_text())
        if not str(g.get("CURRENT_GATE", "")).endswith("PASS"):
            print("CANONICAL_4X4_FIT_GATE not PASS; refuse Exp1.")
            return 2
        # sanity: representation rewritten
        sid0 = g["samples"][0]["sample_id"]
        rep = str(np.load(args.pack_dir / "samples" / sid0 / "canonical_surface.npz")["representation"][0])
        if "lsq" not in rep:
            print(f"canonical_surface not LSQ-fitted (repr={rep}); refuse Exp1.")
            return 2

    device = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    train_ds = BSplineDataset(args.pack_dir, "train", online=True, seed=args.seed)
    val_ds = BSplineDataset(args.pack_dir, "val", online=False, seed=args.seed)
    test_ds = BSplineDataset(args.pack_dir, "test", online=False, seed=args.seed)
    print(f"train={len(train_ds)} val={len(val_ds)} test={len(test_ds)} device={device}", flush=True)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate)

    model = ReconModel().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    A = _basis_cache(device)
    mean_poles = compute_mean_poles(args.pack_dir, train_ds.ids).to(device)

    best_val = math.inf
    best_state = None
    history = []
    for ep in range(1, args.epochs + 1):
        train_ds.set_epoch(ep)
        tr = train_one_epoch(model, train_loader, opt, A, device, args.lam_ctrl, args.lam_surf)
        val_rows = evaluate(model, val_loader, A, device, mean_poles=mean_poles)
        val_sum = summarize(val_rows, None, args.pack_dir)
        history.append({"epoch": ep, **tr, "val": val_sum})
        print(
            f"epoch {ep:02d} loss={tr['loss']:.4f} ctrl={tr['ctrl']:.4f} surf={tr['surf']:.4f} "
            f"val_cd={val_sum['chamfer_rel_mean']:.4e} val_part_macro={val_sum['chamfer_rel_part_macro']:.4e}",
            flush=True,
        )
        if val_sum["chamfer_rel_mean"] < best_val:
            best_val = val_sum["chamfer_rel_mean"]
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)

    test_rows = evaluate(model, test_loader, A, device, mean_poles=mean_poles)
    test_sum = summarize(test_rows, None, args.pack_dir)
    val_rows = evaluate(model, val_loader, A, device, mean_poles=mean_poles)
    val_sum = summarize(val_rows, None, args.pack_dir)

    # Gate: beat mean baseline on test, and train not collapsed vs test
    vs = test_sum.get("vs_baseline_ratio")
    gate = (
        "EXP1_RECON_PASS"
        if vs is not None and vs < 0.85 and test_sum["chamfer_rel_mean"] < 0.05
        else "EXP1_RECON_FAIL"
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    n_vis = save_previews(model, test_loader, A, device, args.out_dir / "previews", n=20)
    report = {
        "experiment": "freeform_patch_reconstruction_v1",
        "stage": "exp1_pointnet_surface_only",
        "canonical": "lsq_cubic_4x4",
        "online_train_resample": True,
        "lam_ctrl": args.lam_ctrl,
        "lam_surf": args.lam_surf,
        "device": str(device),
        "epochs": args.epochs,
        "val": val_sum,
        "test": test_sum,
        "CURRENT_GATE": gate,
        "n_previews": n_vis,
        "per_sample_test": test_rows,
    }
    (args.out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    torch.save({"model": best_state, "mean_poles": mean_poles.cpu()}, args.out_dir / "best.pt")

    lines = [
        "# Exp1 PointNet Surface-only Reconstruction (4×4 LSQ)",
        "",
        f"- CURRENT_GATE = **{gate}**",
        f"- test chamfer_rel mean/median = **{test_sum['chamfer_rel_mean']:.4e}** / **{test_sum['chamfer_rel_median']:.4e}**",
        f"- test part-macro chamfer_rel = **{test_sum['chamfer_rel_part_macro']:.4e}**",
        f"- test ctrl_l1 mean = **{test_sum['ctrl_l1_mean']:.4e}**",
        f"- test hausdorff95_rel median = **{test_sum['hausdorff95_rel_median']:.4e}**",
        f"- vs mean-baseline ratio = **{test_sum.get('vs_baseline_ratio')}** (<0.85 required)",
        f"- baseline mean CD = **{test_sum.get('baseline_mean_chamfer_rel_mean')}**",
        "",
        "Train uses online face_mesh resampling; val/test use fixed patch_points.npy.",
        "No boundary branch.",
        "",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines))
    print(json.dumps({k: report[k] for k in report if k != "per_sample_test"}, indent=2))
    print(f"wrote {args.out_dir / 'REPORT.md'}")
    return 0 if gate.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
