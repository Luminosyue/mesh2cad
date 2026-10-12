"""Held-out geometry controls for SpatialLM curve-token arms.

Applied at runtime (no edits under ``SpatialLM/``).

Legacy protocol (default, old heldout last-ckpt diagnostic):
  CAD_SURFACE_POINTS=4096
      Path-hash subsample of surface (and proportional B1 edge) raw points.
  CAD_EDGE_BUDGET_MATCH=1
      After voxelizing sharp edge points, keep at most K voxels where
      K = len(curve_tokens.npy) for that CAD.

best_v2 protocol (CAD_HELDOUT_PROTOCOL=best_v2):
  Shared surface index cache so B0/B1/M2 receive identical 4096 surface
  points for the same CAD. GridSample is forced to ``test`` mode so voxel
  representatives are deterministic (val/test never re-draw; train uses the
  same fixed subset — no extra surface RNG). B1-budget-match still truncates
  the *voxelized* second stream to K LLM tokens, not the raw edge-point count.

Install **after** ``curve_token_injector.install()`` when training M2, so this
module wraps the active second-stream loader.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np

from spatiallm_curve_token_v1.curve_token_injector import (  # noqa: E402
    curve_stream_enabled,
    load_curve_tokens,
)
from spatiallm_curve_token_v1.surface_cache import (  # noqa: E402
    SurfaceIndexCache,
    apply_indices,
    protocol_best_v2,
)


def surface_point_budget() -> int | None:
    raw = os.environ.get("CAD_SURFACE_POINTS", "").strip()
    if not raw:
        return None
    n = int(raw)
    if n <= 0:
        raise ValueError(f"CAD_SURFACE_POINTS must be positive, got {n}")
    return n


def edge_budget_match_enabled() -> bool:
    return os.environ.get("CAD_EDGE_BUDGET_MATCH", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _stable_seed(*parts: str, salt: int = 0) -> int:
    h = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
    return (int(h[:8], 16) ^ salt) & 0x7FFFFFFF


def subsample_rows(arr: np.ndarray, n: int, seed: int) -> np.ndarray:
    if n <= 0 or len(arr) <= n:
        return arr
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(len(arr), size=n, replace=False))
    return arr[idx]


def _voxelize_surface_edge(self, surface: np.ndarray, edge: np.ndarray | None):
    s_grid, s_xyz, s_normal, s_origin = self._voxelize_6ch(surface)
    surface_tensor = np.concatenate(
        [s_grid.astype(np.float32), s_xyz, s_normal], axis=1
    )
    if edge is None:
        return surface_tensor, None
    e_grid, e_xyz, e_normal, e_origin = self._voxelize_6ch(edge)
    e_grid = e_grid + (e_origin - s_origin)[None, :]
    e_grid = np.clip(e_grid, 0, self.num_bins - 1)
    edge_tensor = np.concatenate(
        [e_grid.astype(np.float32), e_xyz, e_normal], axis=1
    )
    return surface_tensor, edge_tensor


def _test_sepedge_transform(self):
    from spatiallm.pcd.transform import Compose

    return Compose(
        [
            dict(
                type="GridSample",
                grid_size=self.grid_size,
                hash_type="fnv",
                mode="test",
                keys=("coord", "normal"),
                return_grid_coord=True,
                return_min_coord=True,
                max_grid_coord=self.num_bins,
            )
        ]
    )


def _test_cad_transform(self):
    from spatiallm.pcd.transform import Compose

    return Compose(
        [
            dict(
                type="GridSample",
                grid_size=self.grid_size,
                hash_type="fnv",
                mode="test",
                keys=("coord", "normal", "edge_feat"),
                return_grid_coord=True,
                max_grid_coord=self.num_bins,
            )
        ]
    )


def _voxelize_6ch_test(self, feats: np.ndarray):
    sampled = _test_sepedge_transform(self)(
        {
            "name": "cad_part",
            "coord": feats[:, :3].astype(np.float64).copy(),
            "normal": feats[:, 3:6].astype(np.float64).copy(),
        }
    )
    grid_coord = np.asarray(sampled["grid_coord"], dtype=np.int64)
    xyz = np.asarray(sampled["coord"], dtype=np.float32)
    normal = np.asarray(sampled["normal"], dtype=np.float32)
    origin = np.rint(
        np.asarray(sampled["min_coord"], dtype=np.float64).reshape(3) / self.grid_size
    ).astype(np.int64)
    return grid_coord, xyz, normal, origin


def _install_legacy(plugin, original_surface, original_sepedge) -> None:
    n_surf_default = surface_point_budget()

    def _load_cad_npy(self, npy_path: str):
        n_surf = surface_point_budget()
        if n_surf is None:
            return original_surface(self, npy_path)
        feats = np.load(npy_path).astype(np.float64)
        if feats.ndim != 2 or feats.shape[1] < 6:
            raise ValueError(f"CAD features must be (N, >=6), got {feats.shape}")
        seed = _stable_seed(str(Path(npy_path).resolve()), "surface", salt=n_surf)
        feats = subsample_rows(feats, n_surf, seed)
        points = feats[:, :3]
        normals = feats[:, 3:6]
        edge = (
            feats[:, 6]
            if feats.shape[1] >= 7
            else np.zeros(len(feats), dtype=np.float64)
        )
        if not self.cad_use_edge_score:
            edge = np.zeros_like(edge)
        edge_feat = 2.0 * edge - 1.0
        coord = points.copy()
        if not self.cad_already_canonical and self.cad_target_diagonal > 0:
            extent = coord.max(0) - coord.min(0)
            diagonal = float(np.linalg.norm(extent))
            scale = float(self.cad_target_diagonal / diagonal) if diagonal > 0 else 1.0
            coord *= scale
        sampled = self.cad_transform(
            {
                "name": "cad_part",
                "coord": coord,
                "normal": normals.copy(),
                "edge_feat": edge_feat[:, None].copy(),
            }
        )
        grid_coord = np.asarray(sampled["grid_coord"], dtype=np.float32)
        xyz = np.asarray(sampled["coord"], dtype=np.float32)
        normal = np.asarray(sampled["normal"], dtype=np.float32)
        edge_col = np.asarray(sampled["edge_feat"], dtype=np.float32).reshape(-1, 1)
        if self.cad_use_edge_score:
            return np.concatenate([grid_coord, xyz, normal, edge_col], axis=1)
        return np.concatenate([grid_coord, xyz, normal], axis=1)

    def _load_cad_separate_edge(self, npy_path: str):
        n_surf = surface_point_budget()
        match = edge_budget_match_enabled()
        if n_surf is None and not match and not curve_stream_enabled():
            return original_sepedge(self, npy_path)

        surface_path = Path(npy_path)

        if curve_stream_enabled():
            surface = np.load(npy_path).astype(np.float64)
            if surface.ndim != 2 or surface.shape[1] != 6:
                raise ValueError(f"surface features must be (N, 6), got {surface.shape}")
            if n_surf is not None:
                seed = _stable_seed(str(surface_path.resolve()), "surface", salt=n_surf)
                surface = subsample_rows(surface, n_surf, seed)
            surface_tensor, _ = _voxelize_surface_edge(self, surface, None)
            return surface_tensor, load_curve_tokens(surface_path)

        edge_path = self._resolve_separate_edge_path(surface_path)
        surface = np.load(surface_path).astype(np.float64)
        edge = np.load(edge_path).astype(np.float64)
        for name, arr in (("surface", surface), ("edge", edge)):
            if arr.ndim != 2 or arr.shape[1] != 6:
                raise ValueError(
                    f"separate_edge_tokens_v1 {name} features must be (N, 6), got {arr.shape}"
                )

        if n_surf is not None:
            seed_s = _stable_seed(str(surface_path.resolve()), "surface", salt=n_surf)
            surface = subsample_rows(surface, n_surf, seed_s)
            n_edge_raw = max(1, int(round(len(edge) * (n_surf / 8192.0))))
            n_edge_raw = min(n_edge_raw, len(edge))
            seed_e = _stable_seed(str(edge_path.resolve()), "edge_raw", salt=n_surf)
            edge = subsample_rows(edge, n_edge_raw, seed_e)

        surface_tensor, edge_tensor = _voxelize_surface_edge(self, surface, edge)
        assert edge_tensor is not None

        if match:
            K = max(1, int(load_curve_tokens(surface_path).shape[0]))
            if len(edge_tensor) > K:
                seed_v = _stable_seed(str(surface_path.resolve()), "edge_vox", salt=K)
                edge_tensor = subsample_rows(edge_tensor, K, seed_v)

        return surface_tensor, edge_tensor

    plugin._load_cad_npy = _load_cad_npy
    plugin._load_cad_separate_edge = _load_cad_separate_edge
    print(
        f"[heldout_geometry] patched loaders "
        f"(protocol=legacy, CAD_SURFACE_POINTS={n_surf_default}, "
        f"budget_match={edge_budget_match_enabled()}, "
        f"curve_stream={curve_stream_enabled()})",
        flush=True,
    )


def _install_best_v2(plugin) -> None:
    cache = SurfaceIndexCache()
    cache.load()

    def _subsample_surface(npy_path: str, feats: np.ndarray) -> np.ndarray:
        # CADFS retrain inputs are explicitly frozen in the manifest.
        if "/cadfs_noisy_overfit100_v1/data100_retry3/" in str(Path(npy_path)):
            return feats
        idx = cache.indices_for(npy_path)
        return apply_indices(feats, idx)

    def _load_cad_npy(self, npy_path: str):
        feats = np.load(npy_path).astype(np.float64)
        if feats.ndim != 2 or feats.shape[1] < 6:
            raise ValueError(f"CAD features must be (N, >=6), got {feats.shape}")
        feats = _subsample_surface(npy_path, feats)
        points = feats[:, :3]
        normals = feats[:, 3:6]
        edge = (
            feats[:, 6]
            if feats.shape[1] >= 7
            else np.zeros(len(feats), dtype=np.float64)
        )
        if not self.cad_use_edge_score:
            edge = np.zeros_like(edge)
        edge_feat = 2.0 * edge - 1.0
        coord = points.copy()
        if not self.cad_already_canonical and self.cad_target_diagonal > 0:
            extent = coord.max(0) - coord.min(0)
            diagonal = float(np.linalg.norm(extent))
            scale = float(self.cad_target_diagonal / diagonal) if diagonal > 0 else 1.0
            coord *= scale
        sampled = _test_cad_transform(self)(
            {
                "name": "cad_part",
                "coord": coord,
                "normal": normals.copy(),
                "edge_feat": edge_feat[:, None].copy(),
            }
        )
        grid_coord = np.asarray(sampled["grid_coord"], dtype=np.float32)
        xyz = np.asarray(sampled["coord"], dtype=np.float32)
        normal = np.asarray(sampled["normal"], dtype=np.float32)
        edge_col = np.asarray(sampled["edge_feat"], dtype=np.float32).reshape(-1, 1)
        if self.cad_use_edge_score:
            return np.concatenate([grid_coord, xyz, normal, edge_col], axis=1)
        return np.concatenate([grid_coord, xyz, normal], axis=1)

    def _load_cad_separate_edge(self, npy_path: str):
        surface_path = Path(npy_path)
        surface = np.load(npy_path).astype(np.float64)
        if surface.ndim != 2 or surface.shape[1] != 6:
            raise ValueError(f"surface features must be (N, 6), got {surface.shape}")
        surface = _subsample_surface(npy_path, surface)

        if "/cadfs_noisy_overfit100_v1/data100_retry3/" in str(Path(npy_path)):
            return _voxelize_surface_edge(self, surface, None)

        if curve_stream_enabled():
            surface_tensor, _ = _voxelize_surface_edge(self, surface, None)
            return surface_tensor, load_curve_tokens(surface_path)

        edge_path = self._resolve_separate_edge_path(surface_path)
        edge = np.load(edge_path).astype(np.float64)
        if edge.ndim != 2 or edge.shape[1] != 6:
            raise ValueError(
                f"separate_edge_tokens_v1 edge features must be (N, 6), got {edge.shape}"
            )
        # Full sharp-edge cloud → voxels. Budget-match truncates *tokens*,
        # not the raw edge-point count.
        surface_tensor, edge_tensor = _voxelize_surface_edge(self, surface, edge)
        assert edge_tensor is not None
        if edge_budget_match_enabled():
            K = max(1, int(load_curve_tokens(surface_path).shape[0]))
            if len(edge_tensor) > K:
                seed_v = _stable_seed(
                    cad_key_from_path(surface_path), "edge_vox_llm", salt=K
                )
                edge_tensor = subsample_rows(edge_tensor, K, seed_v)
        return surface_tensor, edge_tensor

    def cad_key_from_path(surface_path: Path) -> str:
        from spatiallm_curve_token_v1.surface_cache import cad_key_from_surface_path

        return cad_key_from_surface_path(surface_path)

    plugin._voxelize_6ch = _voxelize_6ch_test
    plugin._load_cad_npy = _load_cad_npy
    plugin._load_cad_separate_edge = _load_cad_separate_edge
    print(
        f"[heldout_geometry] patched loaders "
        f"(protocol=best_v2, cache={cache.path}, n={len(cache.load())}, "
        f"grid_sample=test, budget_match={edge_budget_match_enabled()}, "
        f"curve_stream={curve_stream_enabled()})",
        flush=True,
    )


def install() -> None:
    """Patch SpatialLMPlugin loaders. Safe to call multiple times."""
    from spatiallm.tuner.data import mm_plugin

    plugin = mm_plugin.SpatialLMPlugin
    if getattr(plugin, "_heldout_geometry_patched", False):
        return

    original_surface = plugin._load_cad_npy
    original_sepedge = plugin._load_cad_separate_edge
    if protocol_best_v2():
        _install_best_v2(plugin)
    else:
        _install_legacy(plugin, original_surface, original_sepedge)
    plugin._heldout_geometry_patched = True
