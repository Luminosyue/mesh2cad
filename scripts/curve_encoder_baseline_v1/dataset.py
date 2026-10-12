"""Curve-level dataset + type-aware train sampler for encoder baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from torch.utils.data import Dataset, Sampler

from .config import (
    CACHE_DIR,
    CURVE_DATA_ROOT,
    FEATURE_DIM,
    ID_TO_TYPE,
    MAX_PARAM_DIM,
    N_POINTS,
    PARAM_DIM,
    PRIMARY_TYPES,
    SPLIT_DIR,
    TYPE_TO_ID,
)


def _normalized_s(xyz: np.ndarray, sampling_mode: str) -> np.ndarray:
    """Arc-length position in [0, 1]. Uniform-abscissa samples → linspace."""
    n = xyz.shape[0]
    mode = str(sampling_mode)
    if mode in ("uniform_abscissa", "abscissa_point"):
        if n == 1:
            return np.zeros((n, 1), dtype=np.float32)
        s = np.linspace(0.0, 1.0, n, dtype=np.float32).reshape(n, 1)
        return s
    # fallback: cumulative chord length on the stored polyline
    d = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(d)])
    total = float(cum[-1])
    if total < 1e-12:
        return np.zeros((n, 1), dtype=np.float32)
    return (cum / total).astype(np.float32).reshape(n, 1)


def _pack_params(curve_type: str, params: dict) -> np.ndarray:
    """Pack normalized analytic parameters into a fixed MAX_PARAM_DIM vector."""
    out = np.zeros((MAX_PARAM_DIM,), dtype=np.float32)
    mask = np.zeros((MAX_PARAM_DIM,), dtype=np.float32)
    if curve_type == "LINE":
        d = np.asarray(params["direction"], dtype=np.float32).reshape(3)
        nrm = float(np.linalg.norm(d))
        if nrm > 1e-12:
            d = d / nrm
        out[:3] = d
        mask[:3] = 1.0
    elif curve_type == "CIRCLE":
        out[0:3] = np.asarray(params["center"], dtype=np.float32)
        n = np.asarray(params["normal"], dtype=np.float32).reshape(3)
        nrm = float(np.linalg.norm(n))
        if nrm > 1e-12:
            n = n / nrm
        out[3:6] = n
        out[6] = float(params["radius"])
        mask[:7] = 1.0
    elif curve_type == "ELLIPSE":
        out[0:3] = np.asarray(params["center"], dtype=np.float32)
        maj = np.asarray(params["major_axis"], dtype=np.float32).reshape(3)
        mn = np.asarray(params["minor_axis"], dtype=np.float32).reshape(3)
        for arr, sl in ((maj, slice(3, 6)), (mn, slice(6, 9))):
            nrm = float(np.linalg.norm(arr))
            out[sl] = arr / nrm if nrm > 1e-12 else arr
        out[9] = float(params["major_radius"])
        out[10] = float(params["minor_radius"])
        mask[:11] = 1.0
    elif curve_type == "BSPLINE":
        pass
    else:
        raise ValueError(curve_type)
    return out, mask


def build_cache(split: str, force: bool = False) -> Path:
    """Materialize all primary-type curves for a CAD split into one npz+json."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / f"frozen_v1_{split}.npz"
    meta_path = CACHE_DIR / f"frozen_v1_{split}_meta.json"
    if out.is_file() and meta_path.is_file() and not force:
        return out

    rows = json.loads((SPLIT_DIR / f"{split}.json").read_text(encoding="utf-8"))
    xyzs, tans, ss, types, params, pmasks = [], [], [], [], [], []
    refs = []
    type_counts = {t: 0 for t in PRIMARY_TYPES}

    for r in rows:
        cad_dir = CURVE_DATA_ROOT / r["cad_dir"]
        z = np.load(cad_dir / "curve_samples.npz")
        curves = json.loads((cad_dir / "curves.json").read_text(encoding="utf-8"))["curves"]
        # align by edge_id
        by_edge = {int(c["edge_id"]): c for c in curves}
        edge_ids = z["curve_edge_id"]
        modes = z["sampling_mode"]
        for i in range(int(z["num_curves"][0])):
            tid = int(z["curve_type_id"][i])
            if tid not in ID_TO_TYPE:
                continue
            ctype = ID_TO_TYPE[tid]
            if ctype not in TYPE_TO_ID:
                continue
            edge_id = int(edge_ids[i])
            c = by_edge[edge_id]
            assert c["curve_type"] == ctype
            xyz = np.asarray(z["curve_xyz_normalized"][i], dtype=np.float32)
            tan = np.asarray(z["curve_tangent"][i], dtype=np.float32)
            assert xyz.shape == (N_POINTS, 3) and tan.shape == (N_POINTS, 3)
            s = _normalized_s(xyz, modes[i])
            pvec, pmask = _pack_params(ctype, c["normalized_parameters"])
            xyzs.append(xyz)
            tans.append(tan)
            ss.append(s)
            types.append(TYPE_TO_ID[ctype])
            params.append(pvec)
            pmasks.append(pmask)
            refs.append(
                {
                    "id": r["id"],
                    "dataset": r["dataset"],
                    "sample_id": r["sample_id"],
                    "edge_id": edge_id,
                    "curve_type": ctype,
                    "local_index": i,
                }
            )
            type_counts[ctype] += 1

    np.savez_compressed(
        out,
        xyz=np.stack(xyzs, 0),
        tangent=np.stack(tans, 0),
        s=np.stack(ss, 0),
        type_id=np.asarray(types, dtype=np.int64),
        param=np.stack(params, 0),
        param_mask=np.stack(pmasks, 0),
    )
    meta = {
        "split": split,
        "n_curves": len(refs),
        "n_cad": len(rows),
        "type_counts": type_counts,
        "n_points": N_POINTS,
        "refs": refs,
    }
    meta_path.write_text(json.dumps(meta) + "\n", encoding="utf-8")
    print(f"[cache] {split}: {len(refs)} curves → {out} counts={type_counts}")
    return out


def feature_channels(features: Sequence[str]) -> int:
    key = tuple(features)
    if key not in FEATURE_DIM:
        raise KeyError(f"unknown feature set {features}")
    return FEATURE_DIM[key]


class CurveEncoderDataset(Dataset):
    """Loads prebuilt cache. Input features never include GT type/params."""

    def __init__(self, split: str, features: Sequence[str], *, force_rebuild: bool = False):
        self.split = split
        self.features = tuple(features)
        self.in_dim = feature_channels(self.features)
        path = build_cache(split, force=force_rebuild)
        data = np.load(path)
        self.xyz = data["xyz"]
        self.tangent = data["tangent"]
        self.s = data["s"]
        self.type_id = data["type_id"]
        self.param = data["param"]
        self.param_mask = data["param_mask"]
        self.meta = json.loads(
            (CACHE_DIR / f"frozen_v1_{split}_meta.json").read_text(encoding="utf-8")
        )
        self.type_counts = self.meta["type_counts"]

    def __len__(self) -> int:
        return int(self.xyz.shape[0])

    def _feats(self, i: int) -> np.ndarray:
        parts = [self.xyz[i]]
        if "tangent" in self.features:
            parts.append(self.tangent[i])
        if "s" in self.features:
            parts.append(self.s[i])
        return np.concatenate(parts, axis=-1).astype(np.float32)

    def __getitem__(self, idx: int) -> dict:
        i = int(idx)
        return {
            "feats": torch.from_numpy(self._feats(i)),
            "xyz": torch.from_numpy(self.xyz[i]),
            "type_id": torch.tensor(int(self.type_id[i]), dtype=torch.long),
            "param": torch.from_numpy(self.param[i]),
            "param_mask": torch.from_numpy(self.param_mask[i]),
            "has_param": torch.tensor(
                float(PARAM_DIM[ID_TO_TYPE[int(self.type_id[i])]] > 0),
                dtype=torch.float32,
            ),
        }


class TypeAwareSampler(Sampler[int]):
    """Draw a fixed number of curve indices with type-balanced probabilities.

    Prob ∝ 1 / count(type) so rare ELLIPSE/BSPLINE appear often in train.
    Val/test must NOT use this — use sequential / shuffle only.
    """

    def __init__(
        self,
        type_id: np.ndarray,
        samples_per_epoch: int,
        seed: int = 0,
    ):
        self.type_id = np.asarray(type_id, dtype=np.int64)
        self.samples_per_epoch = int(samples_per_epoch)
        self.seed = int(seed)
        self.epoch = 0
        self._by_type = {
            t: np.where(self.type_id == t)[0] for t in range(len(PRIMARY_TYPES))
        }
        present = [t for t, ix in self._by_type.items() if len(ix) > 0]
        if not present:
            raise RuntimeError("empty TypeAwareSampler")
        self._present = present

    def set_epoch(self, epoch: int) -> None:
        self.epoch = int(epoch)

    def __len__(self) -> int:
        return self.samples_per_epoch

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch * 10007)
        # equal type probability among present types, then uniform within type
        types = rng.choice(self._present, size=self.samples_per_epoch, replace=True)
        for t in types:
            pool = self._by_type[int(t)]
            yield int(pool[rng.integers(0, len(pool))])


def collate_curves(batch: list[dict]) -> dict:
    out = {}
    for k in batch[0]:
        out[k] = torch.stack([b[k] for b in batch], 0)
    return out
