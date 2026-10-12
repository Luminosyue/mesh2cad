#!/usr/bin/env python3
"""Build 7ch canonical edge ablation feature files on disk.

For each sample with features_canonical.npy (7ch xyz+normal+edge):
  - features_canonical_edge_zero.npy    : edge column = 0
  - features_canonical_edge_shuffle.npy : edge column permuted (destroys spatial alignment)

Real Dora edge reuses features_canonical.npy unchanged.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "cad_spatial_dataset/DeepCAD/manifest_train100.json"


def build_one(sample_dir: Path, seed: int) -> dict | None:
    src = sample_dir / "features_canonical.npy"
    if not src.exists():
        return None
    feats = np.load(src).astype(np.float32)
    if feats.ndim != 2 or feats.shape[1] < 7:
        return None

    xyzn = feats[:, :6].copy()
    edge = feats[:, 6].copy()

    zero = np.concatenate([xyzn, np.zeros((len(feats), 1), dtype=np.float32)], axis=1)
    np.save(sample_dir / "features_canonical_edge_zero.npy", zero)

    rng = np.random.default_rng(seed + (hash(sample_dir.name) & 0xFFFF))
    shuffled_edge = edge.copy()
    rng.shuffle(shuffled_edge)
    shuffle = np.concatenate([xyzn, shuffled_edge[:, None].astype(np.float32)], axis=1)
    np.save(sample_dir / "features_canonical_edge_shuffle.npy", shuffle)

    return {
        "sample_id": sample_dir.name,
        "n_points": int(len(feats)),
        "edge_mean": float(edge.mean()),
        "edge_p90": float(np.percentile(edge, 90)),
        "zero_path": str(sample_dir / "features_canonical_edge_zero.npy"),
        "shuffle_path": str(sample_dir / "features_canonical_edge_shuffle.npy"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build edge zero/shuffle canonical features")
    ap.add_argument("--train-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD/train")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--out-report",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/edge_ablation_features_report.json",
    )
    args = ap.parse_args()

    if args.manifest.exists():
        ids = [s.replace("/", "_") for s in json.loads(args.manifest.read_text())["sample_ids"]]
        dirs = [args.train_dir / sid for sid in ids if (args.train_dir / sid).is_dir()]
    else:
        dirs = sorted(p for p in args.train_dir.iterdir() if p.is_dir())

    reports = []
    for d in dirs:
        rep = build_one(d, args.seed)
        if rep:
            reports.append(rep)

    out = {"n_ok": len(reports), "seed": args.seed, "samples": reports}
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"n_ok": len(reports), "report": str(args.out_report)}, indent=2))
    return 0 if reports else 1


if __name__ == "__main__":
    raise SystemExit(main())
