"""Shared 4096-from-8192 surface index cache for held-out best_v2.

All four arms (B0 / B1-native / B1-budget-match / M2) must see the same
4096 surface points for a given CAD. Indices are keyed by ``dataset/sample_id``,
not by absolute path, so SpatialLM's relative media paths and decode-time
absolute paths resolve to the same subset.

Val/test never re-draw: the cache is the source of truth. Train uses the same
indices (no extra surface resampling); GridSample is forced to ``test`` mode
in the v2 geometry patch so voxel representatives are also deterministic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from spatiallm_curve_token_v1.config import (
    HELDOUT_BEST_V2,
    JOINT_DATASET_DIR,
    PACK_ROOT,
    SURFACE_IDX_CACHE,
)

N_KEEP = 4096
CACHE_SEED = 42
SPLITS = ("train", "val", "test")


def protocol_best_v2() -> bool:
    import os

    return os.environ.get("CAD_HELDOUT_PROTOCOL", "").strip().lower() in {
        "best_v2",
        "heldout_best_v2",
        "1",
        "true",
    }


def cache_path() -> Path:
    import os

    raw = os.environ.get("CAD_SURFACE_CACHE", "").strip()
    return Path(raw) if raw else SURFACE_IDX_CACHE


def cad_key(dataset: str, sample_id: str) -> str:
    return f"{dataset}/{sample_id}"


def cad_key_from_surface_path(npy_path: str | Path) -> str:
    p = Path(npy_path)
    sample_id = p.parent.name
    dataset_dir = p.parent.parent.parent.name.lower()
    if "fusion" in dataset_dir:
        ds = "fusion360"
    elif "deepcad" in dataset_dir:
        ds = "deepcad"
    else:
        raise ValueError(f"cannot infer dataset from {npy_path}")
    return cad_key(ds, sample_id)


def _stable_seed(*parts: str, salt: int = 0) -> int:
    h = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
    return (int(h[:8], 16) ^ salt) & 0x7FFFFFFF


def make_indices(cad_key_str: str, n_src: int, n_keep: int = N_KEEP, seed: int = CACHE_SEED) -> np.ndarray:
    n_keep = min(int(n_keep), int(n_src))
    if n_keep <= 0:
        raise ValueError(f"{cad_key_str}: n_src={n_src}")
    if n_keep == n_src:
        return np.arange(n_src, dtype=np.int32)
    rng = np.random.default_rng(_stable_seed(cad_key_str, "surface4096", salt=seed))
    return np.sort(rng.choice(n_src, size=n_keep, replace=False)).astype(np.int32)


def apply_indices(arr: np.ndarray, idx: np.ndarray) -> np.ndarray:
    if len(arr) < len(idx):
        raise ValueError(f"array has {len(arr)} rows, cache wants {len(idx)}")
    return arr[idx]


class SurfaceIndexCache:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path is not None else cache_path()
        self._data: dict[str, np.ndarray] | None = None

    def load(self) -> dict[str, np.ndarray]:
        if self._data is not None:
            return self._data
        if not self.path.is_file():
            raise FileNotFoundError(
                f"surface index cache missing: {self.path}. "
                "Run scripts/spatiallm_curve_token_v1/build_surface_cache.py"
            )
        raw = np.load(self.path, allow_pickle=False)
        self._data = {k: raw[k] for k in raw.files}
        return self._data

    def indices_for(self, npy_path: str | Path) -> np.ndarray:
        key = cad_key_from_surface_path(npy_path)
        data = self.load()
        if key not in data:
            raise KeyError(f"{key} not in surface cache {self.path}")
        return data[key]


def _iter_split_records() -> list[dict]:
    rows = []
    for split in SPLITS:
        p = JOINT_DATASET_DIR / f"joint_j0j2_v1_{split}.json"
        recs = json.loads(p.read_text(encoding="utf-8"))
        for rec in recs:
            rec = dict(rec)
            rec["_split"] = split
            rows.append(rec)
    return rows


def build_cache(out: Path | None = None, seed: int = CACHE_SEED, n_keep: int = N_KEEP) -> Path:
    out = Path(out) if out is not None else SURFACE_IDX_CACHE
    out.parent.mkdir(parents=True, exist_ok=True)
    arrays: dict[str, np.ndarray] = {}
    manifest = {
        "n_keep": n_keep,
        "seed": seed,
        "selection": "md5(cad_key|surface4096) xor seed → numpy Generator.choice, sorted",
        "test_used_for_selection": False,
        "splits": {},
        "n_short": 0,
    }
    for rec in _iter_split_records():
        ds = rec["dataset"]
        sid = rec["sample_id"]
        key = cad_key(ds, sid)
        if key in arrays:
            continue
        npy = PACK_ROOT[ds] / sid / "surface_points.npy"
        if not npy.is_file():
            raise FileNotFoundError(npy)
        n_src = int(np.load(npy, mmap_mode="r").shape[0])
        idx = make_indices(key, n_src, n_keep=n_keep, seed=seed)
        arrays[key] = idx
        if len(idx) < n_keep:
            manifest["n_short"] += 1
        split = rec["_split"]
        bucket = manifest["splits"].setdefault(split, {"n": 0})
        bucket["n"] += 1
    np.savez_compressed(out, **arrays)
    manifest["n_cads"] = len(arrays)
    manifest["path"] = str(out)
    man_path = out.with_suffix(".manifest.json")
    man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[surface_cache] wrote {len(arrays)} CADs → {out}")
    print(f"[surface_cache] manifest {man_path}")
    return out


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=SURFACE_IDX_CACHE)
    ap.add_argument("--seed", type=int, default=CACHE_SEED)
    ap.add_argument("--n-keep", type=int, default=N_KEEP)
    args = ap.parse_args()
    HELDOUT_BEST_V2.mkdir(parents=True, exist_ok=True)
    build_cache(out=args.out, seed=args.seed, n_keep=args.n_keep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
