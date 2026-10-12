#!/usr/bin/env python3
"""Materialise the separate_edge_tokens_v1 data cache.

Writes, per sample, into a directory that is disjoint from every existing
surface / edge_score artefact:

    cad_spatial_dataset/DeepCAD/separate_edge_tokens_v1/<sample_id>/
        surface_points.npy   (8192, 6)  = [x, y, z, nx, ny, nz], canonical
        edge_points.npy      (1024, 6)  = [x, y, z, nx, ny, nz], canonical
        metadata.json

Nothing under `train/<sample_id>/` is read-modify-written; the source tree is
opened read-only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from separate_edge_tokens_v1.edge_sampling import (  # noqa: E402
    DEFAULT_NUM_EDGE_POINTS,
    EDGE_CHANNELS,
    SURFACE_CHANNELS,
    build_edge_cloud,
)

DEFAULT_TRAIN_DIR = ROOT / "cad_spatial_dataset/DeepCAD/train"
DEFAULT_CACHE_DIR = ROOT / "cad_spatial_dataset/DeepCAD/separate_edge_tokens_v1"
EXPERIMENT = "separate_edge_tokens_v1"


def build_one(
    sample_dir: Path,
    cache_dir: Path,
    num_edge_points: int = DEFAULT_NUM_EDGE_POINTS,
    seed: int = 0,
    overwrite: bool = False,
) -> dict:
    sample_id = sample_dir.name
    out_dir = cache_dir / sample_id
    meta_path = out_dir / "metadata.json"
    if meta_path.is_file() and not overwrite:
        return json.loads(meta_path.read_text(encoding="utf-8"))

    surface_canonical = sample_dir / "features_canonical.npy"
    if not surface_canonical.is_file():
        raise FileNotFoundError(f"{sample_id}: missing {surface_canonical.name}")

    feats = np.load(surface_canonical)
    if feats.ndim != 2 or feats.shape[1] < SURFACE_CHANNELS:
        raise ValueError(f"{sample_id}: bad surface shape {feats.shape}")

    # Surface branch is strictly 6D for this experiment: edge_score is dropped.
    surface = feats[:, :SURFACE_CHANNELS].astype(np.float32)

    edge = build_edge_cloud(
        sample_dir,
        num_edge_points=num_edge_points,
        seed=seed,
        surface_features=feats.astype(np.float64),
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "surface_points.npy", surface)
    np.save(out_dir / "edge_points.npy", edge.features)
    np.save(out_dir / "edge_segment_index.npy", edge.segment_index.astype(np.int32))

    s_xyz = surface[:, :3]
    e_xyz = edge.features[:, :3]
    # Edges must lie inside the surface hull; a large overshoot means the two
    # clouds were canonicalised with different transforms.
    surf_min, surf_max = s_xyz.min(axis=0), s_xyz.max(axis=0)
    diag = float(np.linalg.norm(surf_max - surf_min))
    overshoot = float(
        max(
            np.max(surf_min - e_xyz.min(axis=0)),
            np.max(e_xyz.max(axis=0) - surf_max),
            0.0,
        )
    )

    metadata = {
        "experiment": EXPERIMENT,
        "sample_id": sample_id,
        "num_surface_points": int(surface.shape[0]),
        "num_edge_points": int(edge.features.shape[0]),
        "surface_channels": SURFACE_CHANNELS,
        "edge_channels": EDGE_CHANNELS,
        "surface_source": "features_canonical.npy[:, :6]",
        "edge_source": "dora/salient_edges.npz segments, arc-length proportional resampling",
        "edge_normal_policy": "adjacent face-normal mean -> nearest surface normal -> degenerate",
        "sharp_threshold": "Dora SES dihedral threshold as stored in salient_edges.npz",
        "canonical_frame": "features_canonical.npy (shared T from coordinate_transform.json)",
        "surface_bbox_min": surf_min.tolist(),
        "surface_bbox_max": surf_max.tolist(),
        "surface_diagonal": diag,
        "edge_outside_surface_bbox": overshoot,
        "edge_inside_surface_bbox": bool(overshoot <= 1e-3 * max(diag, 1e-9)),
        "seed": seed,
        "edge_stats": edge.stats,
    }
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train-dir", type=Path, default=DEFAULT_TRAIN_DIR)
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    ap.add_argument("--ids-file", type=Path, default=None, help="one sample id per line")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--num-edge-points", type=int, default=DEFAULT_NUM_EDGE_POINTS)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if args.ids_file and args.ids_file.is_file():
        ids = [
            ln.strip()
            for ln in args.ids_file.read_text(encoding="utf-8").splitlines()
            if ln.strip()
        ]
    else:
        ids = sorted(p.name for p in args.train_dir.iterdir() if p.is_dir())
    if args.limit is not None:
        ids = ids[: args.limit]

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    ok, failed = [], []
    for sid in ids:
        try:
            meta = build_one(
                args.train_dir / sid,
                args.cache_dir,
                num_edge_points=args.num_edge_points,
                seed=args.seed,
                overwrite=args.overwrite,
            )
            ok.append(meta)
        except Exception as exc:  # noqa: BLE001 - reported, not hidden
            failed.append({"sample_id": sid, "error": f"{type(exc).__name__}: {exc}"})

    summary = {
        "experiment": EXPERIMENT,
        "cache_dir": str(args.cache_dir),
        "requested": len(ids),
        "built": len(ok),
        "failed": len(failed),
        "num_edge_points": args.num_edge_points,
        "failures": failed[:50],
    }
    if ok:
        overshoot = [m["edge_outside_surface_bbox"] for m in ok]
        face_frac = [m["edge_stats"]["normal_face_pair_frac"] for m in ok]
        segs = [m["edge_stats"]["num_segments"] for m in ok]
        summary["edge_outside_bbox_max"] = float(np.max(overshoot))
        summary["normal_face_pair_frac_mean"] = float(np.mean(face_frac))
        summary["normal_face_pair_frac_min"] = float(np.min(face_frac))
        summary["segments_min"] = int(np.min(segs))
        summary["segments_median"] = float(np.median(segs))
        summary["segments_max"] = int(np.max(segs))

    (args.cache_dir / "build_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if not failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
