#!/usr/bin/env python3
"""Merge one cad_spatial_dataset part into a single SpatialLM input npz.

SpatialLM consumes [x, y, z, r, g, b]. This replaces color with
(normal, edge_score), so every point becomes:

    p_i = [x, y, z, nx, ny, nz, e]        e = edge_score from Dora

Alongside the real feature matrix the npz also stores the ablation variants
consumed by test_edge_embedding.py:

    features_zero_edge      e := 0        (edge channel carries no information)
    features_shuffled_edge  e := perm(e)  (same edge histogram, wrong geometry)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
FEATURE_LAYOUT = ["x", "y", "z", "nx", "ny", "nz", "edge_score"]


def load_part(part_dir: Path) -> dict[str, np.ndarray]:
    points = np.load(part_dir / "points.npy").astype(np.float32)
    normals = np.load(part_dir / "normals.npy").astype(np.float32)
    edge = np.load(part_dir / "edge_score.npy").astype(np.float32)

    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"points.npy must be (N,3), got {points.shape}")
    if normals.shape != points.shape:
        raise ValueError(f"normals.npy {normals.shape} != points.npy {points.shape}")
    if edge.shape != (points.shape[0],):
        raise ValueError(f"edge_score.npy must be ({points.shape[0]},), got {edge.shape}")

    finite = np.isfinite(points).all(1) & np.isfinite(normals).all(1) & np.isfinite(edge)
    if not finite.all():
        raise ValueError(f"{int((~finite).sum())} points carry nan/inf values")

    return {"points": points, "normals": normals, "edge_score": edge}


def build_features(points: np.ndarray, normals: np.ndarray, edge: np.ndarray) -> np.ndarray:
    return np.concatenate([points, normals, edge[:, None]], axis=1).astype(np.float32)


def describe(name: str, edge: np.ndarray) -> dict:
    return {
        "variant": name,
        "min": float(edge.min()),
        "max": float(edge.max()),
        "mean": float(edge.mean()),
        "frac_ge_0_5": float((edge >= 0.5).mean()),
        "frac_ge_0_8": float((edge >= 0.8).mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--part-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/PART_005",
        help="cad_spatial_dataset part directory holding points/normals/edge_score .npy",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output npz (default: <part-dir>/spatiallm/<part_id>.npz)",
    )
    parser.add_argument("--seed", type=int, default=0, help="seed for the shuffled-edge variant")
    args = parser.parse_args()

    part_dir = args.part_dir.resolve()
    part_id = part_dir.name
    out_path = args.out or (part_dir / "spatiallm" / f"{part_id}.npz")
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    arrays = load_part(part_dir)
    points, normals, edge = arrays["points"], arrays["normals"], arrays["edge_score"]

    features = build_features(points, normals, edge)
    zero_edge = build_features(points, normals, np.zeros_like(edge))
    rng = np.random.default_rng(args.seed)
    shuffled = edge[rng.permutation(edge.shape[0])]
    shuffled_edge = build_features(points, normals, shuffled)

    bbox_min = points.min(0)
    bbox_max = points.max(0)
    meta = {
        "part_id": part_id,
        "part_dir": str(part_dir),
        "num_points": int(points.shape[0]),
        "feature_layout": FEATURE_LAYOUT,
        "bbox_min": bbox_min.tolist(),
        "bbox_max": bbox_max.tolist(),
        "bbox_extent": (bbox_max - bbox_min).tolist(),
        "bbox_diagonal": float(np.linalg.norm(bbox_max - bbox_min)),
        "normal_norm_range": [
            float(np.linalg.norm(normals, axis=1).min()),
            float(np.linalg.norm(normals, axis=1).max()),
        ],
        "shuffle_seed": args.seed,
        "edge_variants": [
            describe("features", edge),
            describe("features_zero_edge", np.zeros_like(edge)),
            describe("features_shuffled_edge", shuffled),
        ],
    }

    np.savez(
        out_path,
        points=points,
        normals=normals,
        edge_score=edge,
        features=features,
        features_zero_edge=zero_edge,
        features_shuffled_edge=shuffled_edge,
        feature_layout=np.array(FEATURE_LAYOUT),
        meta_json=np.array(json.dumps(meta)),
    )

    print(f"part            : {part_id}")
    print(f"points.npy      : {points.shape}")
    print(f"normals.npy     : {normals.shape}")
    print(f"edge_score.npy  : {edge.shape}")
    print(f"features        : {features.shape}   layout={FEATURE_LAYOUT}")
    print(f"bbox extent     : {np.round(bbox_max - bbox_min, 4).tolist()}  diag={meta['bbox_diagonal']:.4f}")
    print(f"edge_score      : mean={edge.mean():.4f}  frac>=0.5={float((edge >= 0.5).mean()):.4f}")
    print(f"wrote           : {out_path}")


if __name__ == "__main__":
    main()
