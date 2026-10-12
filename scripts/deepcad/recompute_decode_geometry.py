#!/usr/bin/env python3
"""Recompute Chamfer/H95/vol on existing decode outputs (cadfit-env has trimesh)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "cad_spatial_dataset/DeepCAD/train"


def _geom(gt_mesh: Path, pred_stl: Path, n: int = 20000, seed: int = 0) -> dict:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(gt_mesh), force="mesh")
    pred = trimesh.load(str(pred_stl), force="mesh")
    if isinstance(ref, trimesh.Scene):
        ref = ref.dump(concatenate=True)
    if isinstance(pred, trimesh.Scene):
        pred = pred.dump(concatenate=True)
    diag = float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))
    if diag < 1e-12:
        return {"error": "zero_diag"}
    rng = np.random.default_rng(seed)
    a, _ = trimesh.sample.sample_surface(ref, n, seed=int(rng.integers(1 << 30)))
    b, _ = trimesh.sample.sample_surface(pred, n, seed=int(rng.integers(1 << 30)))
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]
    ref_vol = float(abs(ref.volume)) if ref.is_volume else None
    pred_vol = float(abs(pred.volume)) if pred.is_volume else None
    vol_err = None
    if ref_vol and ref_vol > 0 and pred_vol is not None:
        vol_err = abs(pred_vol - ref_vol) / ref_vol
    return {
        "chamfer_norm": float((d_ab.mean() + d_ba.mean()) / 2 / diag),
        "hausdorff_95_norm": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag),
        "volume_error": vol_err,
    }


def recompute_variant(decode_dir: Path) -> dict:
    report_path = decode_dir / "report.json"
    report = json.loads(report_path.read_text())
    chamfers, haus, vols = [], [], []
    for row in report["samples"]:
        sid = row["sample_id"]
        if not row.get("step_ok"):
            continue
        stl = decode_dir / sid / "pred.stl"
        gt = TRAIN / sid / "model.obj"
        if not stl.exists() or not gt.exists():
            continue
        try:
            geom = _geom(gt, stl)
            row["geometry"] = geom
            if "chamfer_norm" in geom:
                chamfers.append(geom["chamfer_norm"])
                haus.append(geom["hausdorff_95_norm"])
                if geom.get("volume_error") is not None:
                    vols.append(geom["volume_error"])
        except Exception as exc:
            row["geometry"] = {"error": str(exc)}

    report["mean_chamfer_norm"] = float(np.mean(chamfers)) if chamfers else None
    report["mean_hausdorff_95_norm"] = float(np.mean(haus)) if haus else None
    report["mean_volume_error"] = float(np.mean(vols)) if vols else None
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return {
        "n_geom": len(chamfers),
        "mean_chamfer_norm": report["mean_chamfer_norm"],
        "mean_op_recall": report.get("mean_op_recall"),
        "step_valid_rate": report.get("step_valid_rate"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decode-root", type=Path, required=True)
    ap.add_argument("--variants", nargs="*", default=["baseline", "edge_zero", "edge_shuffle", "ours"])
    args = ap.parse_args()
    for v in args.variants:
        d = args.decode_root / v
        if not (d / "report.json").exists():
            print(f"skip {v}: no report")
            continue
        stats = recompute_variant(d)
        print(v, stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
