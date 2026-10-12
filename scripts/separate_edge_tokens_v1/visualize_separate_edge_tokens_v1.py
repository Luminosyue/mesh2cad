#!/usr/bin/env python3
"""Human inspection of the separate_edge_tokens_v1 surface/edge split.

Per sample, three projections plus a diagnostics panel let a reviewer answer:

1. do edge points sit on sharp edges?
2. do edge points float off the surface?
3. did sampling collapse onto a few mesh vertices?
4. are long segments sampled densely enough?
5. is any edge cloud empty?
6. do surface and edge share one normalization?

Surface is drawn as small translucent grey dots; edges as larger opaque red
dots, so the two are never confusable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-sepedge")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import CACHE_DIR, OUT_ROOT, json_dump  # noqa: E402

VIEWS = {
    "xy": (0, 1),
    "xz": (0, 2),
    "yz": (1, 2),
}


def nearest_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    from scipy.spatial import cKDTree

    return cKDTree(b).query(a, k=1)[0]


def diagnose(surface: np.ndarray, edge: np.ndarray, meta: dict) -> dict:
    s_xyz, e_xyz = surface[:, :3], edge[:, :3]
    diag = float(np.linalg.norm(s_xyz.max(0) - s_xyz.min(0)))

    d_edge_to_surface = nearest_distance(e_xyz, s_xyz)
    unique_edge = np.unique(np.round(e_xyz, 6), axis=0).shape[0]

    s_min, s_max = s_xyz.min(0), s_xyz.max(0)
    outside = float(
        max(np.max(s_min - e_xyz.min(0)), np.max(e_xyz.max(0) - s_max), 0.0)
    )

    stats = meta.get("edge_stats", {})
    return {
        "sample_id": meta.get("sample_id"),
        "num_surface_points": int(surface.shape[0]),
        "num_edge_points": int(edge.shape[0]),
        "edge_empty": bool(edge.shape[0] == 0),
        "surface_diagonal": diag,
        # 2. floating edges: distance from each edge point to the nearest surface point
        "edge_to_surface_dist_mean_rel": float(d_edge_to_surface.mean() / max(diag, 1e-9)),
        "edge_to_surface_dist_max_rel": float(d_edge_to_surface.max() / max(diag, 1e-9)),
        # 3. vertex collapse: how many distinct locations were actually produced
        "unique_edge_locations": int(unique_edge),
        "unique_edge_fraction": float(unique_edge / max(edge.shape[0], 1)),
        # 4. long-segment density
        "points_per_segment_min": stats.get("points_per_segment_min"),
        "points_per_segment_max": stats.get("points_per_segment_max"),
        "num_segments": stats.get("num_segments"),
        # 6. shared normalization
        "edge_outside_surface_bbox": outside,
        "shared_normalization_ok": bool(outside <= 1e-2 * max(diag, 1e-9)),
        "surface_bbox_min": s_min.tolist(),
        "surface_bbox_max": s_max.tolist(),
        "edge_bbox_min": e_xyz.min(0).tolist(),
        "edge_bbox_max": e_xyz.max(0).tolist(),
        "edge_normal_norm_mean": float(np.linalg.norm(edge[:, 3:6], axis=1).mean()),
        "surface_normal_norm_mean": float(np.linalg.norm(surface[:, 3:6], axis=1).mean()),
    }


def plot_sample(sample_id: str, surface: np.ndarray, edge: np.ndarray, diag: dict, out_path: Path):
    fig, axes = plt.subplots(1, 4, figsize=(21, 5.4))
    fig.suptitle(
        f"{sample_id}   separate_edge_tokens_v1   "
        f"surface={surface.shape[0]}x6 (grey)   edge={edge.shape[0]}x6 (red)",
        fontsize=13,
    )

    for ax, (name, (i, j)) in zip(axes[:3], VIEWS.items()):
        ax.scatter(
            surface[:, i], surface[:, j], s=1.2, c="#9e9e9e", alpha=0.35, linewidths=0,
            label="surface",
        )
        ax.scatter(
            edge[:, i], edge[:, j], s=7.0, c="#d62728", alpha=0.95, linewidths=0,
            marker="o", label="sharp edge",
        )
        ax.set_title(f"{name} projection")
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        if name == "xy":
            ax.legend(loc="upper right", fontsize=8, markerscale=3)

    ax = axes[3]
    ax.axis("off")
    lines = [
        f"segments              : {diag['num_segments']}",
        f"edge points           : {diag['num_edge_points']}",
        f"unique edge locations : {diag['unique_edge_locations']} "
        f"({diag['unique_edge_fraction']:.1%})",
        f"pts/segment           : {diag['points_per_segment_min']} .. {diag['points_per_segment_max']}",
        "",
        f"edge->surface dist (rel diag)",
        f"   mean               : {diag['edge_to_surface_dist_mean_rel']:.2e}",
        f"   max                : {diag['edge_to_surface_dist_max_rel']:.2e}",
        "",
        f"edge outside bbox     : {diag['edge_outside_surface_bbox']:.2e}",
        f"shared normalization  : {diag['shared_normalization_ok']}",
        "",
        f"|n| surface           : {diag['surface_normal_norm_mean']:.4f}",
        f"|n| edge              : {diag['edge_normal_norm_mean']:.4f}",
    ]
    ax.text(
        0.0, 0.98, "\n".join(lines), va="top", ha="left", family="monospace", fontsize=10
    )
    ax.set_title("diagnostics")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    ap.add_argument("--out-dir", type=Path, default=OUT_ROOT / "data_debug/debug_visualizations")
    ap.add_argument("--num-samples", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ids", nargs="*", default=None)
    args = ap.parse_args()

    all_ids = sorted(
        p.name for p in args.cache_dir.iterdir()
        if p.is_dir() and (p / "edge_points.npy").is_file()
    )
    if args.ids:
        ids = [i for i in args.ids if i in all_ids]
    else:
        rng = np.random.default_rng(args.seed)
        pick = rng.choice(len(all_ids), size=min(args.num_samples, len(all_ids)), replace=False)
        ids = [all_ids[i] for i in sorted(pick)]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = []
    for sid in ids:
        d = args.cache_dir / sid
        surface = np.load(d / "surface_points.npy")
        edge = np.load(d / "edge_points.npy")
        meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
        diag = diagnose(surface, edge, meta)
        plot_sample(sid, surface, edge, diag, args.out_dir / f"{sid}.png")
        diagnostics.append(diag)

    summary = {
        "num_visualized": len(diagnostics),
        "output_dir": str(args.out_dir),
        "any_edge_empty": any(d["edge_empty"] for d in diagnostics),
        "worst_edge_to_surface_max_rel": max(
            d["edge_to_surface_dist_max_rel"] for d in diagnostics
        ),
        "min_unique_edge_fraction": min(d["unique_edge_fraction"] for d in diagnostics),
        "all_shared_normalization_ok": all(d["shared_normalization_ok"] for d in diagnostics),
        "per_sample": diagnostics,
    }
    json_dump(args.out_dir.parent / "debug_diagnostics.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "per_sample"}, indent=2))
    for d in diagnostics:
        print(
            f"  {d['sample_id']}: seg={d['num_segments']:4d} "
            f"uniq={d['unique_edge_fraction']:.1%} "
            f"e2s_max={d['edge_to_surface_dist_max_rel']:.2e} "
            f"norm_ok={d['shared_normalization_ok']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
