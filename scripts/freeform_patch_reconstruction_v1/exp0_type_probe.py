#!/usr/bin/env python3
"""Experiment 0: Surface-type probe — PLANE / CYLINDER / BSPLINE.

Input:  1024×6 xyz+normal patch points
Model:  encoder (pointnet|sonata) → global pool → MLP → 3 classes
No LLM.

Reports overall accuracy, BSpline P/R/F1, confusion matrix.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from freeform_patch_reconstruction_v1 import CLASSES, EXPERIMENT  # noqa: E402

DEFAULT_PACK = ROOT / "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1"
LABEL = {c: i for i, c in enumerate(CLASSES)}


class PatchDataset(Dataset):
    def __init__(self, pack_dir: Path, split: str | None, role: str):
        """role: 'bspline' | 'analytic' | 'all'"""
        man = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
        split_j = json.loads((pack_dir / "split.json").read_text(encoding="utf-8"))
        part_split = {}
        for sp in ("train", "val", "test"):
            for p in split_j[f"{sp}_parts"]:
                part_split[p] = sp

        rows = []
        if role in ("bspline", "all"):
            for s in man["samples"]:
                sp = s["split"]
                if split is not None and sp != split:
                    continue
                rows.append((s["sample_id"], "BSPLINE", sp))
        if role in ("analytic", "all"):
            for s in man.get("analytic_control", []):
                sp = part_split.get(s["part_id"], s.get("split", "train"))
                if split is not None and sp != split:
                    continue
                rows.append((s["sample_id"], s["surface_type"], sp))
        self.pack_dir = pack_dir
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        sid, stype, _ = self.rows[idx]
        pts = np.load(self.pack_dir / "samples" / sid / "patch_points.npy").astype(np.float32)
        # Normalize to unit-diagonal bbox centered at origin (per-patch)
        xyz = pts[:, :3]
        mn, mx = xyz.min(0), xyz.max(0)
        diag = float(np.linalg.norm(mx - mn))
        if diag > 1e-12:
            xyz = (xyz - mn) / diag
        feats = np.concatenate([xyz, pts[:, 3:6]], axis=1).astype(np.float32)
        return torch.from_numpy(feats), LABEL[stype], sid


class PointNetEncoder(nn.Module):
    """Cheap probe encoder (CPU-friendly). Same I/O contract as Sonata path."""

    def __init__(self, in_ch: int = 6, width: int = 128):
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, N, 6)
        h = self.mlp(x)
        return h.max(dim=1).values


class ProbeClassifier(nn.Module):
    def __init__(self, encoder: nn.Module, n_classes: int = 3):
        super().__init__()
        self.encoder = encoder
        self.head = nn.Sequential(
            nn.Linear(encoder.out_dim, encoder.out_dim),
            nn.ReLU(inplace=True),
            nn.Linear(encoder.out_dim, n_classes),
        )

    def forward(self, x):
        return self.head(self.encoder(x))


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    n = len(CLASSES)
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    acc = float((y_true == y_pred).mean()) if len(y_true) else 0.0
    b = LABEL["BSPLINE"]
    tp = int(cm[b, b])
    fp = int(cm[:, b].sum() - tp)
    fn = int(cm[b, :].sum() - tp)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "overall_accuracy": acc,
        "bspline_precision": prec,
        "bspline_recall": rec,
        "bspline_f1": f1,
        "confusion_matrix": cm.tolist(),
        "confusion_labels": list(CLASSES),
        "support": {CLASSES[i]: int(cm[i].sum()) for i in range(n)},
    }


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    ys, ps = [], []
    for x, y, _ in loader:
        x = x.to(device)
        logits = model(x)
        pred = logits.argmax(-1).cpu().numpy()
        ys.append(y.numpy())
        ps.append(pred)
    y_true = np.concatenate(ys) if ys else np.zeros(0, dtype=np.int64)
    y_pred = np.concatenate(ps) if ps else np.zeros(0, dtype=np.int64)
    return metrics(y_true, y_pred)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK)
    ap.add_argument("--encoder", choices=("pointnet", "sonata"), default="pointnet")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", type=str, default=None)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "ours3/freeform_patch_reconstruction_v1/exp0_type_probe",
    )
    args = ap.parse_args()

    device = torch.device(
        args.device
        or ("cuda" if torch.cuda.is_available() else "cpu")
    )
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    train_ds = PatchDataset(args.pack_dir, "train", "all")
    val_ds = PatchDataset(args.pack_dir, "val", "all")
    test_ds = PatchDataset(args.pack_dir, "test", "all")
    # Also evaluate on all-split pooled holdout if val empty of some class
    print(
        f"train={len(train_ds)} val={len(val_ds)} test={len(test_ds)} device={device} encoder={args.encoder}",
        flush=True,
    )
    # Class counts
    for name, ds in (("train", train_ds), ("val", val_ds), ("test", test_ds)):
        c = {CLASSES[i]: 0 for i in range(3)}
        for _, st, _ in ds.rows:
            c[st] += 1
        print(f"  {name} class counts: {c}", flush=True)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False)

    if args.encoder == "pointnet":
        enc = PointNetEncoder()
    else:
        raise NotImplementedError(
            "Sonata probe path needs GPU + SpatialLM checkpoint wiring; "
            "run with --encoder pointnet first to validate data signal, "
            "then enable sonata when CUDA is available."
        )

    model = ProbeClassifier(enc).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    crit = nn.CrossEntropyLoss()

    best_val_f1 = -1.0
    best_state = None
    history = []
    for ep in range(1, args.epochs + 1):
        model.train()
        total = 0.0
        n = 0
        for x, y, _ in train_loader:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = crit(model(x), y)
            loss.backward()
            opt.step()
            total += float(loss.item()) * len(y)
            n += len(y)
        val_m = evaluate(model, val_loader, device)
        history.append({"epoch": ep, "train_loss": total / max(n, 1), **val_m})
        print(
            f"epoch {ep:02d} loss={total / max(n, 1):.4f} "
            f"val_acc={val_m['overall_accuracy']:.3f} "
            f"bsp_f1={val_m['bspline_f1']:.3f}",
            flush=True,
        )
        if val_m["bspline_f1"] >= best_val_f1:
            best_val_f1 = val_m["bspline_f1"]
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    test_m = evaluate(model, test_loader, device)
    val_m = evaluate(model, val_loader, device)

    # Gate: BSpline F1 >= 0.7 and overall acc >= 0.7
    gate = (
        "EXP0_TYPE_PROBE_PASS"
        if test_m["bspline_f1"] >= 0.70 and test_m["overall_accuracy"] >= 0.70
        else "EXP0_TYPE_PROBE_FAIL"
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "experiment": EXPERIMENT,
        "stage": "exp0_type_probe",
        "encoder": args.encoder,
        "device": str(device),
        "epochs": args.epochs,
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "n_test": len(test_ds),
        "val": val_m,
        "test": test_m,
        "CURRENT_GATE": gate,
        "history_tail": history[-5:],
    }
    (args.out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    torch.save({"model": best_state, "encoder": args.encoder}, args.out_dir / "best.pt")

    cm = np.asarray(test_m["confusion_matrix"])
    lines = [
        f"# Exp0 Type Probe ({args.encoder})",
        "",
        f"- CURRENT_GATE = **{gate}**",
        f"- overall_accuracy = **{test_m['overall_accuracy']:.4f}**",
        f"- BSpline precision = **{test_m['bspline_precision']:.4f}**",
        f"- BSpline recall = **{test_m['bspline_recall']:.4f}**",
        f"- BSpline F1 = **{test_m['bspline_f1']:.4f}**",
        "",
        "## Confusion matrix (rows=GT, cols=Pred)",
        "",
        "|  | " + " | ".join(CLASSES) + " |",
        "|---|" + "|".join(["---:"] * 3) + "|",
    ]
    for i, name in enumerate(CLASSES):
        lines.append("| " + name + " | " + " | ".join(str(int(x)) for x in cm[i]) + " |")
    lines.append("")
    (args.out_dir / "REPORT.md").write_text("\n".join(lines))
    print(json.dumps({k: report[k] for k in report if k != "history_tail"}, indent=2))
    print(f"wrote {args.out_dir / 'REPORT.md'}")
    return 0 if gate.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
