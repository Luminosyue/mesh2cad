#!/usr/bin/env python3
"""Forward a CAD part through the SpatialLM point front-end and prove that
edge_score reaches the tokens.

Pipeline (no LLM decoding, no training -- forward only):

    PART_005.npz -> SpatialLM preprocessing -> Sonata (in_channels=7)
                 -> projector -> tokens [K, hidden_dim]

Three feature variants share identical xyz and normals and differ only in the
edge column, so the voxel grid and therefore the token ordering are identical
and tokens can be compared index by index:

    A  edge := 0            edge channel present but carries no information
    B  edge := edge_score   the real Dora signal
    C  edge := perm(e)      same edge histogram, scrambled across the surface

B is encoded twice to measure the run-to-run numerical noise floor, so any
reported A/B difference can be checked against it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cad-spatial")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spatiallm_cad_frontend import (  # noqa: E402
    DEFAULT_MODEL_PATH,
    EDGE_INIT_CHOICES,
    load_spatiallm_with_edge_channel,
    per_token_edge_score,
    preprocess_cad_point_cloud,
    replace_edge_column,
    token_pool_index,
)

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
VIEW = np.array([[0.82, -0.38, 0.0], [0.22, 0.30, 0.86]], dtype=float)
EDGE_CMAP = LinearSegmentedColormap.from_list(
    "edge_score", ["#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62", "#b2182b"]
)


def project(xyz: np.ndarray) -> np.ndarray:
    return xyz @ VIEW.T


@torch.no_grad()
def encode(model, tensor: torch.Tensor, device: str) -> np.ndarray:
    """Run one variant through forward_point_cloud and return (K, hidden_dim)."""
    tokens = model.forward_point_cloud(tensor[0].to(device), device, torch.float32)
    return tokens.squeeze(0).float().cpu().numpy()


def compare(reference: np.ndarray, other: np.ndarray) -> dict:
    delta = other - reference
    delta_norm = np.linalg.norm(delta, axis=1)
    ref_norm = np.linalg.norm(reference, axis=1)
    relative = np.divide(delta_norm, ref_norm, out=np.zeros_like(delta_norm), where=ref_norm > 0)
    cos = np.sum(reference * other, axis=1) / np.maximum(
        ref_norm * np.linalg.norm(other, axis=1), 1e-12
    )
    return {
        "identical": bool(np.array_equal(reference, other)),
        "delta_l2_mean": float(delta_norm.mean()),
        "delta_l2_max": float(delta_norm.max()),
        "relative_delta_mean": float(relative.mean()),
        "relative_delta_median": float(np.median(relative)),
        "relative_delta_max": float(relative.max()),
        "cosine_mean": float(cos.mean()),
        "cosine_min": float(cos.min()),
        "frac_tokens_cos_below_0_999": float((cos < 0.999).mean()),
        "_relative": relative,
        "_cosine": cos,
    }


def strip_arrays(metrics: dict) -> dict:
    return {k: v for k, v in metrics.items() if not k.startswith("_")}


def localization(relative: np.ndarray, token_edge: np.ndarray) -> dict:
    """Is the token change concentrated where the sharp edges are?"""
    order = np.argsort(token_edge)
    n = token_edge.shape[0]
    decile = max(1, n // 10)
    low = relative[order[:decile]].mean()
    high = relative[order[-decile:]].mean()
    result = {
        "pearson_r": float(pearsonr(token_edge, relative)[0]),
        "spearman_r": float(spearmanr(token_edge, relative).statistic),
        "mean_relative_delta_low_edge_decile": float(low),
        "mean_relative_delta_high_edge_decile": float(high),
        "high_over_low_ratio": float(high / low) if low > 0 else float("inf"),
    }
    return result


def make_figure(
    part_id: str,
    points: np.ndarray,
    edge_score: np.ndarray,
    token_xyz: np.ndarray,
    token_edge: np.ndarray,
    rel_ab: np.ndarray,
    rel_bc: np.ndarray,
    noise_floor: float,
    out_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle(
        f"{part_id}  edge_score -> SpatialLM point tokens  (forward only, no LLM)",
        fontsize=13,
    )

    p2d = project(points)
    order = np.argsort(edge_score)
    ax = axes[0]
    sc = ax.scatter(
        p2d[order, 0], p2d[order, 1], c=edge_score[order], s=2.0, cmap=EDGE_CMAP, vmin=0, vmax=1
    )
    ax.set_title("1. input edge_score (8192 pts)")
    fig.colorbar(sc, ax=ax, fraction=0.046)

    t2d = project(token_xyz)
    ax = axes[1]
    sc = ax.scatter(t2d[:, 0], t2d[:, 1], c=token_edge, s=42.0, cmap=EDGE_CMAP, vmin=0, vmax=1)
    ax.set_title(f"2. per-token max edge_score (K={token_xyz.shape[0]})")
    fig.colorbar(sc, ax=ax, fraction=0.046)

    ax = axes[2]
    sc = ax.scatter(t2d[:, 0], t2d[:, 1], c=rel_ab, s=42.0, cmap="magma")
    ax.set_title("3. token change  ||B-A|| / ||A||")
    fig.colorbar(sc, ax=ax, fraction=0.046)

    ax = axes[3]
    ax.scatter(token_edge, rel_ab, s=14.0, c="#b2182b", label="B (real) vs A (edge=0)")
    ax.scatter(token_edge, rel_bc, s=14.0, c="#2166ac", alpha=0.55, label="B vs C (shuffled)")
    if noise_floor > 0:
        ax.axhline(
            noise_floor, color="grey", ls="--", lw=1.0, label=f"noise floor {noise_floor:.2e}"
        )
    else:
        ax.plot([], [], " ", label="noise floor = 0 (deterministic)")
    ax.set_xlabel("per-token max edge_score")
    ax.set_ylabel("relative token change")
    ax.set_yscale("log")
    ax.legend(fontsize=8)
    ax.set_title("4. change vs edge_score")

    for ax in axes[:3]:
        ax.set_aspect("equal")
        ax.axis("off")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--npz",
        type=Path,
        default=ROOT / "cad_spatial_dataset/PART_005/spatiallm/PART_005.npz",
        help="npz written by prepare_spatiallm_cad_input.py",
    )
    parser.add_argument("--out-dir", type=Path, default=None, help="default: <npz parent>")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument(
        "--edge-init",
        choices=EDGE_INIT_CHOICES,
        default="rgb_mean",
        help="initialization of the new 7th stem column (see spatiallm_cad_frontend)",
    )
    parser.add_argument("--edge-scale", type=float, default=1.0)
    parser.add_argument(
        "--target-diagonal",
        type=float,
        default=6.0,
        help="metres the part bbox diagonal is rescaled to before voxelization",
    )
    parser.add_argument("--edge-encoding", choices=("signed", "raw"), default="signed")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out_dir = (args.out_dir or args.npz.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    part_id = args.npz.stem

    data = np.load(args.npz, allow_pickle=True)
    points = data["points"]
    normals = data["normals"]
    edge_score = data["edge_score"]

    part = preprocess_cad_point_cloud(
        points,
        normals,
        edge_score,
        target_diagonal=args.target_diagonal,
        edge_encoding=args.edge_encoding,
    )
    print("preprocessing:", json.dumps(part.stats, indent=2))

    mapping, token_grid = token_pool_index(part.grid_coord)
    expected_tokens = token_grid.shape[0]

    shuffled_edge = data["features_shuffled_edge"][:, -1][part.kept_index]
    if args.edge_encoding == "signed":
        shuffled_col = 2.0 * shuffled_edge.astype(np.float64) - 1.0
        zero_col = -1.0
    else:
        shuffled_col = shuffled_edge.astype(np.float64)
        zero_col = 0.0

    variants = {
        "A_no_edge": replace_edge_column(part.tensor, zero_col),
        "B_edge": part.tensor,
        "C_shuffled_edge": replace_edge_column(part.tensor, shuffled_col),
    }

    torch.manual_seed(args.seed)
    model = load_spatiallm_with_edge_channel(
        args.model_path,
        edge_init=args.edge_init,
        edge_scale=args.edge_scale,
        device=args.device,
        dtype=torch.float32,
        seed=args.seed,
    )
    print(f"point encoder in_channels = {model.config.point_config['in_channels']}")
    print(f"embedding stem = {model.point_backbone.embedding.stem.linear}")

    tokens = {name: encode(model, tensor, args.device) for name, tensor in variants.items()}
    tokens["B_edge_rerun"] = encode(model, variants["B_edge"], args.device)

    shapes = {name: list(t.shape) for name, t in tokens.items()}
    print("token shapes:", shapes)
    if len({tuple(s) for s in shapes.values()}) != 1:
        raise RuntimeError(f"variants produced different token counts: {shapes}")
    num_tokens, hidden_dim = tokens["B_edge"].shape
    if num_tokens != expected_tokens:
        raise RuntimeError(
            f"replayed pooling predicted {expected_tokens} tokens, encoder produced {num_tokens}"
        )

    for name, arr in tokens.items():
        np.save(out_dir / f"{part_id}_tokens_{name}.npy", arr)

    token_edge_mean, token_edge_max, token_counts = per_token_edge_score(
        mapping, part.edge_score, num_tokens
    )

    noise = compare(tokens["B_edge"], tokens["B_edge_rerun"])
    ab = compare(tokens["A_no_edge"], tokens["B_edge"])
    bc = compare(tokens["B_edge"], tokens["C_shuffled_edge"])
    ac = compare(tokens["A_no_edge"], tokens["C_shuffled_edge"])

    noise_floor = noise["relative_delta_mean"]
    report = {
        "part_id": part_id,
        "npz": str(args.npz),
        "model_path": str(args.model_path),
        "edge_init": args.edge_init,
        "edge_scale": args.edge_scale,
        "edge_encoding": args.edge_encoding,
        "in_channels": int(model.config.point_config["in_channels"]),
        "hidden_dim": int(hidden_dim),
        "num_tokens": int(num_tokens),
        "preprocessing": part.stats,
        "points_per_token": {
            "min": int(token_counts.min()),
            "mean": float(token_counts.mean()),
            "max": int(token_counts.max()),
        },
        "noise_floor_B_vs_B_rerun": strip_arrays(noise),
        "A_no_edge_vs_B_edge": strip_arrays(ab),
        "B_edge_vs_C_shuffled_edge": strip_arrays(bc),
        "A_no_edge_vs_C_shuffled_edge": strip_arrays(ac),
        "encoder_is_deterministic": bool(noise["identical"]),
        "signal_to_noise": (
            None if noise_floor == 0.0 else float(ab["relative_delta_mean"] / noise_floor)
        ),
        "localization_A_vs_B": {
            "vs_token_mean_edge": localization(ab["_relative"], token_edge_mean),
            "vs_token_max_edge": localization(ab["_relative"], token_edge_max),
        },
    }

    report_path = out_dir / f"{part_id}_edge_embedding_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    # place each token at the centroid of the original points it pools, so the
    # token panels are directly comparable with the input point panel
    kept_points = points[part.kept_index]
    token_xyz = np.zeros((num_tokens, 3), dtype=np.float64)
    np.add.at(token_xyz, mapping, kept_points)
    token_xyz /= np.maximum(token_counts, 1)[:, None]

    fig_path = out_dir / f"{part_id}_edge_embedding.png"
    make_figure(
        part_id,
        points,
        edge_score,
        token_xyz,
        token_edge_max,
        ab["_relative"],
        bc["_relative"],
        noise_floor,
        fig_path,
    )

    print(f"\ntokens: [{num_tokens}, {hidden_dim}]")
    noise_desc = (
        "0 (reruns bitwise identical)" if noise["identical"] else f"{noise_floor:.3e}"
    )
    print(f"noise floor (B vs B rerun) relative delta : {noise_desc}")
    print(f"A (edge=0) vs B (edge)     relative delta : {ab['relative_delta_mean']:.3e}")
    print(f"B (edge) vs C (shuffled)   relative delta : {bc['relative_delta_mean']:.3e}")
    loc = report["localization_A_vs_B"]["vs_token_max_edge"]
    print(f"corr(delta, token max edge) spearman      : {loc['spearman_r']:.3f}")
    print(f"high-edge decile / low-edge decile delta  : {loc['high_over_low_ratio']:.2f}x")
    print(f"\nreport : {report_path}")
    print(f"figure : {fig_path}")


if __name__ == "__main__":
    main()
