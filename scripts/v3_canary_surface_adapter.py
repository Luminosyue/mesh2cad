"""Isolated explicit-path adapter for Canary20 surface assets.

This module deliberately does not alter the legacy held-out loader.  It uses
the exact old 4096-point policy and the old voxelisation implementation, but
gets dataset/sample identity from the caller's manifest instead of deriving it
from an isolated output path.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from spatiallm_curve_token_v1 import heldout_geometry
from spatiallm_curve_token_v1.surface_cache import (
    SurfaceIndexCache,
    apply_indices,
    cad_key,
    make_indices,
)


def load_surface_for_encoder(plugin, surface_npy_path: str | Path, dataset: str,
                             sample_id: str) -> tuple[np.ndarray, dict]:
    """Return the exact V3 encoder input tensor for an explicitly identified CAD.

    Existing cache entries remain the source of truth.  New isolated canary
    assets have no legacy cache entry, so they use the frozen cache's documented
    deterministic `make_indices` policy with the manifest-provided key.
    """
    path = Path(surface_npy_path)
    ds = str(dataset).strip().lower()
    if ds not in {"deepcad", "fusion360"}:
        raise ValueError(f"unsupported explicit dataset={dataset!r}")
    if not str(sample_id).strip():
        raise ValueError("sample_id must be supplied explicitly")

    raw = np.load(path).astype(np.float64)
    if raw.ndim != 2 or raw.shape[1] != 6:
        raise ValueError(f"surface features must be (N, 6), got {raw.shape}: {path}")
    if not np.isfinite(raw).all():
        raise ValueError(f"non-finite surface features: {path}")

    key = cad_key(ds, str(sample_id))
    cache = SurfaceIndexCache()
    entries = cache.load()
    if key in entries:
        idx = entries[key]
        index_source = "legacy_cache"
    else:
        idx = make_indices(key, len(raw))
        index_source = "frozen_deterministic_policy"
    sampled = apply_indices(raw, idx)
    tensor, _ = heldout_geometry._voxelize_surface_edge(plugin, sampled, None)
    if tensor.ndim != 2 or tensor.shape[1] != 9 or not np.isfinite(tensor).all():
        raise ValueError(f"invalid V3 surface tensor {tensor.shape}: {path}")
    return tensor, {
        "surface_path": str(path),
        "dataset": dataset,
        "sample_id": str(sample_id),
        "surface_input_shape": list(raw.shape),
        "sampled_shape": list(sampled.shape),
        "v3_surface_tensor_shape": list(tensor.shape),
        "input_finite": True,
        "index_count": int(len(idx)),
        "index_source": index_source,
    }
