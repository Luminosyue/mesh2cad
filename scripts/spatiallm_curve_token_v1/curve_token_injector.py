"""Step 2: inject Curve Tokens as SpatialLM's second geometry stream.

Everything here is applied at runtime by monkey-patching, so no file under
``SpatialLM/`` is modified and the Method-A configs stay untouched.

The key idea: J2 already built a generic *second geometry stream* (marker tokens
``<|reserved_special_token_6/8/7|>``, a splice region, label masking, a separate
projector). Curve Tokens reuse that slot verbatim and only swap the payload:

    B1  edge point cloud  →  shared Sonata  →  edge_proj    →  M tokens
    M2  curve tokens      →  (already encoded, frozen)  →  CurveProjector  →  K tokens

Because both arms use the same markers in the same position, the prompt is
byte-identical and the only variable is the representation.

Enable with ``CAD_USE_SEPARATE_EDGE_TOKENS=1`` and ``CAD_SECOND_STREAM=curve_tokens``.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from spatiallm_curve_token_v1.config import (  # noqa: E402
    CURVE_TOKEN_DIM,
    MAX_CURVE_TOKENS,
    TOKEN_ROOT,
)
from spatiallm_curve_token_v1.curve_projector import build_curve_projector  # noqa: E402

SECOND_STREAM_ENV = "CAD_SECOND_STREAM"
CURVE_STREAM = "curve_tokens"
_DATASET_BY_PACK_DIR = {"DeepCAD": "deepcad", "Fusion360": "fusion360"}
_REGISTRY_CACHE: dict[Path, dict[str, dict]] = {}
_ACTIVE_CURVE_MODEL = None


def _load_registry(path: Path) -> dict[str, dict]:
    path = path.resolve()
    if path in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[path]
    if not path.is_file():
        raise FileNotFoundError(f"curve-token registry not found: {path}")
    by_id: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            cad_id = row["cad_id"]
            if cad_id in by_id:
                raise ValueError(f"duplicate cad_id {cad_id!r} in {path}:{line_no}")
            by_id[cad_id] = row
    _REGISTRY_CACHE[path] = by_id
    return by_id


def curve_stream_enabled() -> bool:
    return os.environ.get(SECOND_STREAM_ENV, "edge_points").strip().lower() == CURVE_STREAM


def resolve_curve_token_path(surface_path: Path) -> Path:
    """``.../<DeepCAD|Fusion360>/geometry_pack_v1/<sid>/surface_points.npy`` → tokens."""
    surface_path = Path(surface_path)
    sample_id = surface_path.parent.name
    dataset = None
    for part in surface_path.parts:
        if part in _DATASET_BY_PACK_DIR:
            dataset = _DATASET_BY_PACK_DIR[part]
    if dataset is None:
        raise ValueError(f"cannot infer dataset from surface path {surface_path}")
    registry_path = os.environ.get("CURVE_TOKEN_REGISTRY")
    require_registry = os.environ.get("REQUIRE_CURVE_TOKEN_REGISTRY", "0").lower() in ("1", "true", "yes")
    if registry_path:
        cad_id = f"{dataset}__{sample_id}"
        registry = _load_registry(Path(registry_path))
        if cad_id not in registry:
            raise KeyError(f"curve-token registry has no exact entry for {cad_id}")
        row = registry[cad_id]
        if row.get("dataset", "").lower() != dataset:
            raise ValueError(f"registry dataset mismatch for {cad_id}: {row.get('dataset')!r}")
        path = Path(row["curve_token_path"])
    else:
        if require_registry:
            raise RuntimeError("REQUIRE_CURVE_TOKEN_REGISTRY=1 but CURVE_TOKEN_REGISTRY is unset")
        root = Path(os.environ.get("CURVE_TOKEN_ROOT", str(TOKEN_ROOT)))
        path = root / dataset / sample_id / "curve_tokens.npy"
    if not path.is_file():
        raise FileNotFoundError(
            f"curve tokens missing for {dataset}/{sample_id}: {path}; "
            "run scripts/spatiallm_curve_token_v1/export_curve_tokens.py"
        )
    return path


def load_curve_tokens(surface_path: Path) -> np.ndarray:
    tokens = np.load(resolve_curve_token_path(surface_path)).astype(np.float32)
    if tokens.ndim != 2 or tokens.shape[1] != CURVE_TOKEN_DIM:
        raise ValueError(f"curve tokens must be (K, {CURVE_TOKEN_DIM}), got {tokens.shape}")
    if len(tokens) > MAX_CURVE_TOKENS:
        raise ValueError(
            f"{len(tokens)} curve tokens exceeds MAX_CURVE_TOKENS={MAX_CURVE_TOKENS}; "
            "re-export with the same cap"
        )
    if len(tokens) < 1:
        raise ValueError("curve token cache must contain at least one retained curve")
    if not np.isfinite(tokens).all():
        raise ValueError(f"curve tokens contain non-finite values: {resolve_curve_token_path(surface_path)}")
    return tokens


# ---------------------------------------------------------------- data plugin


def patch_mm_plugin() -> None:
    from spatiallm.tuner.data import mm_plugin

    plugin = mm_plugin.SpatialLMPlugin
    if getattr(plugin, "_curve_token_patched", False):
        return
    original = plugin._load_cad_separate_edge

    def _load_cad_second_stream(self, npy_path: str):
        if not curve_stream_enabled():
            return original(self, npy_path)
        surface = np.load(npy_path).astype(np.float64)
        if surface.ndim != 2 or surface.shape[1] != 6:
            raise ValueError(f"surface features must be (N, 6), got {surface.shape}")
        s_grid, s_xyz, s_normal, _ = self._voxelize_6ch(surface)
        surface_tensor = np.concatenate(
            [s_grid.astype(np.float32), s_xyz, s_normal], axis=1
        )
        return surface_tensor, load_curve_tokens(Path(npy_path))

    plugin._load_cad_separate_edge = _load_cad_second_stream
    plugin._curve_token_patched = True
    print("[curve_token_injector] patched SpatialLMPlugin second stream", flush=True)


# ---------------------------------------------------------------------- model


def _forward_geometry_with_curve_tokens(
    self, surface_points, edge_points=None, device=None, dtype=None
):
    """Surface goes through Sonata; the second stream is already encoded."""
    surface_tokens = self.forward_point_cloud(
        surface_points, device, dtype, projector=self.point_proj
    )
    if edge_points is None:
        return surface_tokens, None
    if self.edge_proj is None:
        raise ValueError("curve tokens supplied but no curve projector is attached")
    # the collator NaN-pads the batch to a common K
    feats = edge_points[~torch.isnan(edge_points).any(dim=1)]
    proj_dtype = next(self.edge_proj.parameters()).dtype
    curve_tokens = self.edge_proj(feats.to(device=device, dtype=proj_dtype))
    return surface_tokens, curve_tokens.unsqueeze(0).to(dtype)


def patch_model_patcher() -> None:
    from spatiallm.tuner.framework import patcher as sp_patcher

    if getattr(sp_patcher, "_curve_token_patched", False):
        return
    original = sp_patcher._attach_edge_projector

    def _attach_second_stream_projector(model) -> None:
        global _ACTIVE_CURVE_MODEL
        if not curve_stream_enabled():
            return original(model)
        ref = next(model.point_proj.parameters())
        projector = build_curve_projector(CURVE_TOKEN_DIM, model.config.hidden_size)
        model.edge_proj = projector.to(device=ref.device, dtype=ref.dtype)
        _ACTIVE_CURVE_MODEL = model
        model.separate_edge_tokens = True
        model.config.separate_edge_tokens = True
        model.config.edge_start_token_id = model.edge_start_token_id
        model.config.edge_end_token_id = model.edge_end_token_id
        model.config.edge_token_id = model.edge_token_id
        # recorded so a checkpoint is self-describing: in curve-token mode the
        # `edge_proj.*` weights ARE the CurveProjector, deliberately occupying
        # the same slot as B1's edge projector.
        model.config.curve_token_stream = True
        model.config.curve_token_dim = CURVE_TOKEN_DIM
        model.config.curve_projector_kind = projector.kind
        type(model).forward_geometry = _forward_geometry_with_curve_tokens
        n_params = sum(p.numel() for p in projector.parameters())
        print(
            f"[curve_token_injector] attached CurveProjector "
            f"({projector.kind}, {CURVE_TOKEN_DIM}->{model.config.hidden_size}, "
            f"{n_params:,} params) as the second geometry stream",
            flush=True,
        )

    sp_patcher._attach_edge_projector = _attach_second_stream_projector
    sp_patcher._curve_token_patched = True


def install() -> None:
    """Apply every patch. Must run before the model or dataset is built."""
    # The curve stream and the model-side second projector are one contract.
    # Keep the model factory from silently taking the surface-only path when a
    # caller selected curve tokens but forgot the companion environment flag.
    if curve_stream_enabled():
        os.environ.setdefault("CAD_USE_SEPARATE_EDGE_TOKENS", "1")
    patch_mm_plugin()
    patch_model_patcher()
    if curve_stream_enabled():
        print(
            f"[curve_token_injector] second stream = curve tokens "
            f"(dim={CURVE_TOKEN_DIM}, cap={MAX_CURVE_TOKENS}, root={TOKEN_ROOT})",
            flush=True,
        )
    else:
        print(
            "[curve_token_injector] installed but inactive "
            f"({SECOND_STREAM_ENV} != {CURVE_STREAM}); behaviour unchanged",
            flush=True,
        )
