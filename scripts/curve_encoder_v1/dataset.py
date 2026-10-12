"""Curve dataset with noise and partial-observation augmentations.

Geometry-only: never exposes curve_type as an input feature.

Coordinates are converted to a *curve-local* frame (subtract sample centroid)
so the encoder sees shape rather than absolute object placement. Position
parameters (origin / center) are shifted by the same centroid; directions and
radii are unchanged.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from .config import (
    ABLATIONS,
    CACHE_DIR,
)


class CurveCacheDataset(Dataset):
    def __init__(
        self,
        cache_path: Path | None = None,
        split: str = "train",
        ablation: str = "B1_xyz_tangent",
        noise_rel: float = 0.0,
        partial_frac: float = 1.0,
        target_diagonal: float = 6.0,
        seed: int = 0,
        max_curves: int | None = None,
        center_curve: bool = True,
    ):
        if ablation not in ABLATIONS:
            raise ValueError(f"unknown ablation {ablation}; choose from {list(ABLATIONS)}")
        self.ablation = ablation
        self.cfg = ABLATIONS[ablation]
        self.noise_rel = float(noise_rel)
        self.partial_frac = float(partial_frac)
        self.target_diagonal = float(target_diagonal)
        self.seed = int(seed)
        self.center_curve = bool(center_curve)

        cache_path = cache_path or (CACHE_DIR / "curves_cache.npz")
        z = np.load(cache_path, allow_pickle=True)
        split_id = {"train": 0, "val": 1, "test": 2}[split]
        mask = z["encoder_split"] == split_id
        idx = np.where(mask)[0]
        if max_curves is not None:
            rng = np.random.default_rng(seed)
            if len(idx) > max_curves:
                idx = np.sort(rng.choice(idx, size=max_curves, replace=False))

        self.idx = idx.astype(np.int64)
        self.xyz = z["xyz_n"]
        self.tan = z["tangent"]
        self.type_id = z["type_id"]
        self.length_n = z["length_n"]
        self.is_closed = z["is_closed"]
        self.params = z["params"]
        self.param_mask = z["param_mask"]
        self.arc_deg = z["arc_deg"]
        self.cad_index = z["cad_index"]
        self.edge_id = z["edge_id"]
        self.n_sample = int(z["n_sample"][0])

    def __len__(self) -> int:
        return len(self.idx)

    def _augment(
        self, xyz: np.ndarray, tan: np.ndarray, params: np.ndarray, i: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return (feat, point_mask, xyz_gt_local, params_local)."""
        n = xyz.shape[0]
        point_mask = np.ones(n, dtype=np.float32)
        xyz_work = xyz.astype(np.float32).copy()
        tan_in = tan.astype(np.float32).copy()
        j = int(self.idx[i])

        # Partial contiguous observation along arc-length order.
        if self.partial_frac < 1.0 - 1e-9:
            keep = max(2, int(round(self.partial_frac * n)))
            rng = np.random.default_rng(self.seed + 17 * i + 91)
            if bool(self.is_closed[j]):
                start = int(rng.integers(0, n))
                sel = np.array([(start + k) % n for k in range(keep)], dtype=np.int64)
            else:
                start = int(rng.integers(0, max(1, n - keep + 1)))
                sel = np.arange(start, start + keep, dtype=np.int64)
            point_mask[:] = 0.0
            point_mask[sel] = 1.0
        else:
            sel = np.arange(n, dtype=np.int64)

        if self.noise_rel > 0:
            rng = np.random.default_rng(self.seed + 31 * i + 7)
            sigma = self.noise_rel * self.target_diagonal
            xyz_work = xyz_work + rng.normal(0.0, sigma, size=xyz_work.shape).astype(np.float32)

        # Curve-local frame from the *observed* (kept) points.
        if self.center_curve:
            centroid = xyz_work[sel].mean(axis=0).astype(np.float32)
        else:
            centroid = np.zeros(3, dtype=np.float32)
        xyz_local = xyz_work - centroid
        params_local = params.astype(np.float32).copy()
        # Position slots: LINE origin [0:3], CIRCLE/ELLIPSE center [0:3]
        params_local[0:3] = params_local[0:3] - centroid

        xyz_in = xyz_local.copy()
        miss = point_mask < 0.5
        xyz_in[miss] = 0.0
        tan_in[miss] = 0.0

        cols = [xyz_in]
        if self.cfg["use_tangent"]:
            cols.append(tan_in)
        feat = np.concatenate(cols, axis=-1).astype(np.float32)
        return feat, point_mask, xyz_local.astype(np.float32), params_local

    def __getitem__(self, i: int) -> dict:
        j = int(self.idx[i])
        feat, point_mask, xyz_gt, params = self._augment(
            self.xyz[j], self.tan[j], self.params[j], i
        )
        sample = {
            "feat": torch.from_numpy(feat),
            "point_mask": torch.from_numpy(point_mask),
            "xyz_gt": torch.from_numpy(xyz_gt),
            "type_id": torch.tensor(int(self.type_id[j]), dtype=torch.long),
            "params": torch.from_numpy(params),
            "param_mask": torch.from_numpy(self.param_mask[j].astype(np.float32)),
            "length_n": torch.tensor(float(self.length_n[j]), dtype=torch.float32),
            "is_closed": torch.tensor(float(self.is_closed[j]), dtype=torch.float32),
            "arc_deg": torch.tensor(float(self.arc_deg[j]), dtype=torch.float32),
            "cad_index": torch.tensor(int(self.cad_index[j]), dtype=torch.long),
            "edge_id": torch.tensor(int(self.edge_id[j]), dtype=torch.long),
            "index": torch.tensor(j, dtype=torch.long),
        }
        if self.cfg["use_scalars"]:
            n = feat.shape[0]
            scalars = np.stack(
                [
                    np.full(n, float(self.length_n[j]), dtype=np.float32),
                    np.full(n, float(self.is_closed[j]), dtype=np.float32),
                ],
                axis=-1,
            )
            sample["feat"] = torch.from_numpy(
                np.concatenate([feat, scalars], axis=-1).astype(np.float32)
            )
        return sample


def input_dim(ablation: str) -> int:
    cfg = ABLATIONS[ablation]
    d = 3
    if cfg["use_tangent"]:
        d += 3
    if cfg["use_scalars"]:
        d += 2
    return d


def make_loader(dataset: CurveCacheDataset, batch_size: int, shuffle: bool, num_workers: int = 0):
    return torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        drop_last=False,
        pin_memory=torch.cuda.is_available(),
    )
