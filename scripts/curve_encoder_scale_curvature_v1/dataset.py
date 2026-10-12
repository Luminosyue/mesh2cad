"""Dataset: object / curve-local frames + scale + curvature descriptors."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, Sampler

from curve_encoder_baseline_v1.config import (
    ID_TO_TYPE,
    MAX_PARAM_DIM,
    PARAM_DIM,
    PRIMARY_TYPES,
)
from curve_encoder_baseline_v1.dataset import TypeAwareSampler  # re-export

from .config import CACHE_DIR, CURV_DIM, N_POINTS, SCALE_DIM, SHAPE_DIM, TYPE_TO_ID


def curve_local_frame(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Center + scale by max bbox extent (avoids closed-circle chord≈0)."""
    xyz = np.asarray(xyz, dtype=np.float64)
    center = xyz.mean(axis=0)
    extent = xyz.max(axis=0) - xyz.min(axis=0)
    scale = float(np.max(extent))
    if scale < 1e-12:
        # degenerate: fall back to polyline length
        scale = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
    if scale < 1e-12:
        scale = 1.0
    local = ((xyz - center) / scale).astype(np.float32)
    return local, center.astype(np.float32), float(scale)


def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    c = float(np.clip(np.dot(a, b), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def curvature_descriptors(xyz: np.ndarray, tangent: np.ndarray) -> np.ndarray:
    """[chord_h, total_turn/360, mean_turn/180, max_turn/180] in ~[0,1]."""
    xyz = np.asarray(xyz, dtype=np.float64)
    tan = np.asarray(tangent, dtype=np.float64)
    poly = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
    if poly < 1e-12:
        poly = 1e-12
    p0, p1 = xyz[0], xyz[-1]
    chord = p1 - p0
    cl = float(np.linalg.norm(chord))
    if cl < 1e-12:
        c = xyz.mean(0)
        _, _, vt = np.linalg.svd(xyz - c, full_matrices=False)
        d = vt[0]
        perp = (xyz - c) - ((xyz - c) @ d)[:, None] * d
        max_dev = float(np.linalg.norm(perp, axis=1).max())
    else:
        d = chord / cl
        perp = (xyz - p0) - ((xyz - p0) @ d)[:, None] * d
        max_dev = float(np.linalg.norm(perp, axis=1).max())
    chord_h = max_dev / poly
    turns = np.array(
        [_angle_deg(tan[i], tan[i + 1]) for i in range(len(tan) - 1)], dtype=np.float64
    )
    total = float(turns.sum()) if turns.size else 0.0
    mean = float(turns.mean()) if turns.size else 0.0
    mx = float(turns.max()) if turns.size else 0.0
    # soft normalize for MLP stability
    out = np.array(
        [
            min(chord_h, 1.0),
            min(total / 360.0, 2.0),
            min(mean / 180.0, 1.0),
            min(mx / 180.0, 1.0),
        ],
        dtype=np.float32,
    )
    assert out.shape == (CURV_DIM,)
    return out


class ScaleCurvatureDataset(Dataset):
    """Wraps baseline frozen_v1_*.npz cache."""

    def __init__(self, split: str):
        path = CACHE_DIR / f"frozen_v1_{split}.npz"
        if not path.is_file():
            raise FileNotFoundError(path)
        data = np.load(path)
        self.xyz = data["xyz"]  # object-normalized
        self.tangent = data["tangent"]
        self.s = data["s"]
        self.type_id = data["type_id"]
        self.param = data["param"]
        self.param_mask = data["param_mask"]
        self.meta = json.loads(
            (CACHE_DIR / f"frozen_v1_{split}_meta.json").read_text(encoding="utf-8")
        )
        self.type_counts = self.meta["type_counts"]
        aug = CACHE_DIR / f"frozen_v1_{split}_scale_curv_aug.npz"
        if aug.is_file():
            a = np.load(aug)
            self.poly_len = a["poly_len"]
            self.log_len = a["log_len"]
            self.xyz_local = a["xyz_local"]
            self.curve_scale = a["curve_scale"]
            self.curv = a["curv"]
        else:
            n = len(self.type_id)
            self.poly_len = np.zeros((n,), dtype=np.float32)
            self.log_len = np.zeros((n, SCALE_DIM), dtype=np.float32)
            self.xyz_local = np.zeros_like(self.xyz)
            self.curve_scale = np.zeros((n,), dtype=np.float32)
            self.curv = np.zeros((n, CURV_DIM), dtype=np.float32)
            for i in range(n):
                xyz = self.xyz[i]
                self.poly_len[i] = float(
                    np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()
                )
                self.log_len[i, 0] = np.log(self.poly_len[i] + 1e-6)
                local, _, sc = curve_local_frame(xyz)
                self.xyz_local[i] = local
                self.curve_scale[i] = sc
                self.curv[i] = curvature_descriptors(xyz, self.tangent[i])
            np.savez_compressed(
                aug,
                poly_len=self.poly_len,
                log_len=self.log_len,
                xyz_local=self.xyz_local,
                curve_scale=self.curve_scale,
                curv=self.curv,
            )
            print(f"[aug-cache] wrote {aug}", flush=True)
        line_lens = self.poly_len[self.type_id == TYPE_TO_ID["LINE"]]
        self.line_length_p90 = (
            float(np.percentile(line_lens, 90)) if line_lens.size else 0.0
        )

    def __len__(self) -> int:
        return int(self.xyz.shape[0])

    def __getitem__(self, idx: int) -> dict:
        i = int(idx)
        # object-frame shape feats (C0)
        feats_obj = np.concatenate(
            [self.xyz[i], self.tangent[i], self.s[i]], axis=-1
        ).astype(np.float32)
        # curve-local shape feats (C1–C3)
        feats_loc = np.concatenate(
            [self.xyz_local[i], self.tangent[i], self.s[i]], axis=-1
        ).astype(np.float32)
        assert feats_obj.shape == (N_POINTS, SHAPE_DIM)
        tid = int(self.type_id[i])
        return {
            "feats_object": torch.from_numpy(feats_obj),
            "feats_local": torch.from_numpy(feats_loc),
            "xyz_object": torch.from_numpy(self.xyz[i]),
            "xyz_local": torch.from_numpy(self.xyz_local[i]),
            "scale_feat": torch.from_numpy(self.log_len[i]),
            "curv_feat": torch.from_numpy(self.curv[i]),
            "straight_gt": torch.from_numpy(self.curv[i, :2].copy()),  # chord_h, total/360
            "poly_len": torch.tensor(self.poly_len[i], dtype=torch.float32),
            "type_id": torch.tensor(tid, dtype=torch.long),
            "param": torch.from_numpy(self.param[i]),
            "param_mask": torch.from_numpy(self.param_mask[i]),
            "has_param": torch.tensor(
                float(PARAM_DIM[ID_TO_TYPE[tid]] > 0), dtype=torch.float32
            ),
        }


def collate(batch: list[dict]) -> dict:
    out = {}
    for k in batch[0]:
        out[k] = torch.stack([b[k] for b in batch], 0)
    return out
