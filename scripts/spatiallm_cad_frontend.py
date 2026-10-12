#!/usr/bin/env python3
"""SpatialLM front-end adapted from xyzrgb to xyz + normal + edge_score.

Three pieces are needed to push a cad_spatial_dataset part through the
pretrained SpatialLM point encoder:

1. `preprocess_cad_point_cloud` -- the SpatialLM preprocessing chain
   (PositiveShift -> GridSample) applied to 7-channel CAD features instead of
   xyzrgb, producing the (1, N, 10) tensor `forward_point_cloud` expects:
   [grid_coord(3) | xyz(3) | nx,ny,nz(3) | edge(1)].

2. `load_spatiallm_with_edge_channel` -- the pretrained checkpoint declares
   `point_config["in_channels"] = 6` (xyz + rgb). The embedding stem is widened
   to 7 in place so the extra column receives edge_score, keeping every other
   pretrained weight untouched.

3. `token_pool_index` -- reproduces Sonata's four GridPooling stages in numpy so
   each output token can be traced back to the input points it pools, which is
   what makes the edge ablation interpretable per token.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn

SPATIALLM_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/SpatialLM")
DEFAULT_MODEL_PATH = SPATIALLM_ROOT / "models/SpatialLM1.1-Llama-1B"

# xyz + normal + edge_score
CAD_IN_CHANNELS = 7
# stem columns of the pretrained checkpoint: [x, y, z, r, g, b]
PRETRAINED_COLOR_COLUMNS = (3, 4, 5)
EDGE_INIT_CHOICES = ("rgb_mean", "rgb_sum", "zero", "randn")


def _ensure_spatiallm_importable() -> None:
    root = str(SPATIALLM_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


@dataclass
class PreprocessedPart:
    """Everything downstream code needs about one preprocessed part."""

    tensor: torch.Tensor  # (1, N, 10) float32, ready for forward_point_cloud
    grid_coord: np.ndarray  # (N, 3) int64 voxel indices
    kept_index: np.ndarray  # (N,) indices into the original 8192 points
    edge_score: np.ndarray  # (N,) raw edge_score of the kept points
    scale: float  # metres per original unit
    stats: dict


def preprocess_cad_point_cloud(
    points: np.ndarray,
    normals: np.ndarray,
    edge_score: np.ndarray,
    num_bins: int = 1280,
    target_diagonal: float = 6.0,
    edge_encoding: str = "signed",
    already_canonical: bool = False,
) -> PreprocessedPart:
    """Voxelize a CAD part into the 10-column tensor SpatialLM's encoder reads.

    When `already_canonical=True`, points are assumed to already live in CAD
    canonical space (diag≈target_diagonal, min≈0) and no scale/PositiveShift is
    applied — matching offline features_canonical.npy + mm_plugin CAD mode.
    """
    _ensure_spatiallm_importable()
    from spatiallm import Layout
    from spatiallm.pcd.transform import Compose

    if edge_encoding not in ("signed", "raw"):
        raise ValueError(f"edge_encoding must be 'signed' or 'raw', got {edge_encoding!r}")

    grid_size = Layout.get_grid_size(num_bins)
    coord = points.astype(np.float64).copy()
    extent = coord.max(0) - coord.min(0)
    diagonal = float(np.linalg.norm(extent))
    if already_canonical or target_diagonal <= 0:
        scale = 1.0
    else:
        scale = float(target_diagonal / diagonal) if diagonal > 0 else 1.0
        coord *= scale

    # NormalizeColor maps rgb 0..255 onto [-1, 1], so the pretrained stem expects
    # its non-xyz columns in [-1, 1]. Normals already live there; edge_score is
    # in [0, 1] and is remapped to match unless raw values are requested.
    edge = edge_score.astype(np.float64)
    edge_feat = 2.0 * edge - 1.0 if edge_encoding == "signed" else edge

    steps = []
    if not already_canonical:
        steps.append(dict(type="PositiveShift"))
    steps.append(
        dict(
            type="GridSample",
            grid_size=grid_size,
            hash_type="fnv",
            mode="test",
            keys=("coord", "normal", "edge_feat", "edge_raw", "source_index"),
            return_grid_coord=True,
            max_grid_coord=num_bins,
        )
    )
    transform = Compose(steps)
    sampled = transform(
        {
            "name": "cad_part",
            "coord": coord,
            "normal": normals.astype(np.float64).copy(),
            "edge_feat": edge_feat[:, None].copy(),
            "edge_raw": edge.copy(),
            "source_index": np.arange(points.shape[0]),
        }
    )

    grid_coord = np.asarray(sampled["grid_coord"], dtype=np.int64)
    xyz = np.asarray(sampled["coord"], dtype=np.float32)
    normal = np.asarray(sampled["normal"], dtype=np.float32)
    edge_col = np.asarray(sampled["edge_feat"], dtype=np.float32).reshape(-1, 1)

    stacked = np.concatenate([grid_coord.astype(np.float32), xyz, normal, edge_col], axis=1)
    tensor = torch.as_tensor(stacked[None, ...], dtype=torch.float32)

    stats = {
        "num_points_in": int(points.shape[0]),
        "num_voxels": int(grid_coord.shape[0]),
        "grid_size_m": float(grid_size),
        "scale": scale,
        "bbox_diagonal_original": diagonal,
        "bbox_diagonal_scaled": diagonal * scale,
        "grid_extent": (grid_coord.max(0) - grid_coord.min(0) + 1).tolist(),
        "edge_encoding": edge_encoding,
        "feat_channels": stacked.shape[1] - 3,
    }
    return PreprocessedPart(
        tensor=tensor,
        grid_coord=grid_coord,
        kept_index=np.asarray(sampled["source_index"], dtype=np.int64),
        edge_score=np.asarray(sampled["edge_raw"], dtype=np.float32),
        scale=scale,
        stats=stats,
    )


def replace_edge_column(tensor: torch.Tensor, value: np.ndarray | float) -> torch.Tensor:
    """Return a copy of a (1, N, 10) tensor with the edge column overwritten."""
    out = tensor.clone()
    if isinstance(value, np.ndarray):
        out[0, :, -1] = torch.as_tensor(value, dtype=out.dtype)
    else:
        out[0, :, -1] = float(value)
    return out


def widen_embedding_stem(
    stem: nn.Linear,
    edge_init: str = "rgb_mean",
    edge_scale: float = 1.0,
    generator: torch.Generator | None = None,
) -> nn.Linear:
    """Widen the Sonata embedding stem from 6 to 7 input channels.

    The first six columns keep their pretrained values (xyz + rgb). The new
    column is what edge_score multiplies, so its initialization decides whether
    edge_score can influence the embedding at all:

    - rgb_mean : average of the three pretrained colour columns. edge_score
                 enters at the same magnitude the encoder already expects from a
                 photometric channel, so it is immediately influential.
    - rgb_sum  : sum of the colour columns; same direction, 3x the gain.
    - zero     : edge_score is wired through but multiplied by 0, so it cannot
                 change any token. Useful as a negative control.
    - randn    : fresh Gaussian column scaled like the pretrained stem.
    """
    if edge_init not in EDGE_INIT_CHOICES:
        raise ValueError(f"edge_init must be one of {EDGE_INIT_CHOICES}, got {edge_init!r}")
    if stem.in_features != CAD_IN_CHANNELS - 1:
        raise ValueError(f"expected a 6-channel stem, got in_features={stem.in_features}")

    weight = stem.weight.data
    color = weight[:, list(PRETRAINED_COLOR_COLUMNS)]
    if edge_init == "rgb_mean":
        edge_column = color.mean(dim=1)
    elif edge_init == "rgb_sum":
        edge_column = color.sum(dim=1)
    elif edge_init == "zero":
        edge_column = torch.zeros_like(weight[:, 0])
    else:
        edge_column = torch.randn(
            weight.shape[0], generator=generator, dtype=weight.dtype, device=weight.device
        ) * color.std()
    edge_column = edge_column * edge_scale

    widened = nn.Linear(CAD_IN_CHANNELS, stem.out_features, bias=stem.bias is not None)
    widened = widened.to(device=weight.device, dtype=weight.dtype)
    with torch.no_grad():
        widened.weight.copy_(torch.cat([weight, edge_column[:, None]], dim=1))
        if stem.bias is not None:
            widened.bias.copy_(stem.bias.data)
    return widened


def set_deterministic_serialization(point_backbone: nn.Module) -> None:
    """Freeze Sonata's random serialization-order shuffling.

    Sonata picks one of four space-filling curve orders per attention block at
    random. That randomness changes token values run to run, which would
    contaminate an A/B comparison between two feature variants.
    """
    for module in point_backbone.modules():
        if hasattr(module, "shuffle_orders"):
            module.shuffle_orders = False


def load_spatiallm_with_edge_channel(
    model_path: Path | str = DEFAULT_MODEL_PATH,
    edge_init: str = "rgb_mean",
    edge_scale: float = 1.0,
    device: str = "cuda",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
):
    """Load SpatialLM and switch its point encoder to in_channels = 7."""
    _ensure_spatiallm_importable()
    import spatiallm  # noqa: F401  registers spatiallm_llama with AutoModelForCausalLM
    from transformers import AutoModelForCausalLM

    model = AutoModelForCausalLM.from_pretrained(str(model_path), torch_dtype=dtype)
    stem = model.point_backbone.embedding.stem.linear
    if stem.in_features != CAD_IN_CHANNELS:
        generator = torch.Generator(device="cpu").manual_seed(seed)
        model.point_backbone.embedding.stem.linear = widen_embedding_stem(
            stem, edge_init=edge_init, edge_scale=edge_scale, generator=generator
        )
    model.point_backbone.embedding.in_channels = CAD_IN_CHANNELS
    model.config.point_config["in_channels"] = CAD_IN_CHANNELS

    set_deterministic_serialization(model.point_backbone)
    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    model.eval()
    return model


def token_pool_index(grid_coord: np.ndarray, num_stages: int = 4, stride: int = 2):
    """Map each input voxel to the output token that pools it.

    Sonata's GridPooling divides grid_coord by `stride` and calls
    torch.unique(sorted=True, dim=0); the row order of that unique result is the
    token order. np.unique(axis=0) sorts rows the same way, so replaying the
    four stages here recovers the point -> token assignment exactly.
    """
    coord = grid_coord.copy()
    mapping = np.arange(coord.shape[0])
    for _ in range(num_stages):
        coord = coord // stride
        unique, inverse = np.unique(coord, axis=0, return_inverse=True)
        mapping = inverse.reshape(-1)[mapping]
        coord = unique
    return mapping, coord


def per_token_edge_score(mapping: np.ndarray, edge_score: np.ndarray, num_tokens: int):
    """Aggregate point-level edge_score into mean/max per output token."""
    counts = np.bincount(mapping, minlength=num_tokens).astype(np.float64)
    total = np.bincount(mapping, weights=edge_score.astype(np.float64), minlength=num_tokens)
    mean = np.divide(total, counts, out=np.zeros_like(total), where=counts > 0)
    maximum = np.zeros(num_tokens, dtype=np.float64)
    np.maximum.at(maximum, mapping, edge_score.astype(np.float64))
    return mean, maximum, counts
