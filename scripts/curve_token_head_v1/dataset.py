"""Curve-level dataset with full per-type parameter supervision (curve-local)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from curve_encoder_scale_curvature_v1.dataset import (
    ScaleCurvatureDataset,
    curve_local_frame,
)

from .config import (
    BSPLINE_DEGREES,
    CACHE_DIR,
    CIRCLE_DIM,
    CURVE_DATA_ROOT,
    ELLIPSE_DIM,
    ID_TO_TYPE,
    LINE_DIM,
    SPLIT_DIR,
    TYPE_TO_ID,
)

TWOPI = 2.0 * math.pi
DEGREE_TO_CLASS = {d: i for i, d in enumerate(BSPLINE_DEGREES)}


def _unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64).reshape(3)
    n = float(np.linalg.norm(v))
    return (v / n) if n > 1e-12 else v


def _to_local(p: np.ndarray, centroid: np.ndarray, scale: float) -> np.ndarray:
    return (np.asarray(p, dtype=np.float64).reshape(3) - centroid) / scale


def pack_params(
    ctype: str,
    p: dict,
    centroid: np.ndarray,
    scale: float,
    seg_len: float,
    u0: float,
    u1: float,
) -> tuple[np.ndarray, int, float]:
    """Build the per-type target vector in a given curve-local frame.

    Returns ``(param_vector, bspline_degree_class, bspline_log_ncp)``; only the
    slot matching ``ctype`` is meaningful.
    """
    if ctype == "LINE":
        v = np.zeros((LINE_DIM,), dtype=np.float32)
        d = _unit(p["direction"])
        o = _to_local(p["origin"], centroid, scale)
        # OCC origin is arbitrary along the line; anchor it at the point
        # closest to the local frame origin so the target is unique.
        v[0:3] = o - float(o @ d) * d
        v[3:6] = d
        v[6] = seg_len / scale
        return v, -1, 0.0
    if ctype == "CIRCLE":
        v = np.zeros((CIRCLE_DIM,), dtype=np.float32)
        v[0:3] = _to_local(p["center"], centroid, scale)
        v[3:6] = _unit(p["normal"])
        v[6] = float(p["radius"]) / scale
        v[7] = math.cos(u0)
        v[8] = math.sin(u0)
        v[9] = math.cos(u1)
        v[10] = math.sin(u1)
        v[11] = min(abs(u1 - u0) / TWOPI, 1.0)
        return v, -1, 0.0
    if ctype == "ELLIPSE":
        v = np.zeros((ELLIPSE_DIM,), dtype=np.float32)
        v[0:3] = _to_local(p["center"], centroid, scale)
        v[3:6] = _unit(p["major_axis"])
        v[6:9] = _unit(p["minor_axis"])
        v[9:12] = _unit(p["normal"])
        v[12] = float(p["major_radius"]) / scale
        v[13] = float(p["minor_radius"]) / scale
        v[14] = math.cos(u0)
        v[15] = math.sin(u0)
        v[16] = min(abs(u1 - u0) / TWOPI, 1.0)
        return v, -1, 0.0
    if ctype == "BSPLINE":
        deg = DEGREE_TO_CLASS.get(int(p["degree"]), -1)
        return (
            np.zeros((0,), dtype=np.float32),
            deg,
            math.log(float(p["num_control_points"]) + 1e-6),
        )
    raise ValueError(ctype)


def build_param_cache(split: str, force: bool = False) -> Path:
    """Extended per-type params, aligned 1:1 with the baseline frozen_v1 cache."""
    out = CACHE_DIR / f"frozen_v1_{split}_fullparam.npz"
    if out.is_file() and not force:
        return out

    base = np.load(CACHE_DIR / f"frozen_v1_{split}.npz")
    base_types = base["type_id"]
    base_xyz = base["xyz"]
    n_total = int(base_types.shape[0])

    line = np.zeros((n_total, LINE_DIM), dtype=np.float32)
    circle = np.zeros((n_total, CIRCLE_DIM), dtype=np.float32)
    ellipse = np.zeros((n_total, ELLIPSE_DIM), dtype=np.float32)
    bs_degree = np.full((n_total,), -1, dtype=np.int64)
    bs_logncp = np.zeros((n_total, 1), dtype=np.float32)

    rows = json.loads((SPLIT_DIR / f"{split}.json").read_text(encoding="utf-8"))
    k = 0
    for r in rows:
        cad_dir = CURVE_DATA_ROOT / r["cad_dir"]
        z = np.load(cad_dir / "curve_samples.npz")
        curves = json.loads((cad_dir / "curves.json").read_text(encoding="utf-8"))["curves"]
        by_edge = {int(c["edge_id"]): c for c in curves}
        for i in range(int(z["num_curves"][0])):
            tid = int(z["curve_type_id"][i])
            if tid not in ID_TO_TYPE:
                continue
            ctype = ID_TO_TYPE[tid]
            if ctype not in TYPE_TO_ID:
                continue
            assert int(base_types[k]) == TYPE_TO_ID[ctype], (
                f"cache misalignment at {k}: {base_types[k]} vs {ctype}"
            )
            c = by_edge[int(z["curve_edge_id"][i])]
            p = c["normalized_parameters"]
            xyz = base_xyz[k].astype(np.float64)
            centroid = xyz.mean(axis=0)
            _, _, scale = curve_local_frame(xyz)
            u0 = float(c["u_start"])
            u1 = float(c["u_end"])

            # OCC u for a line is arc length in *world* units; take the extent
            # from the normalized samples instead so units stay consistent.
            seg_len = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
            vec, deg_cls, log_ncp = pack_params(ctype, p, centroid, scale, seg_len, u0, u1)
            if ctype == "LINE":
                line[k] = vec
            elif ctype == "CIRCLE":
                circle[k] = vec
            elif ctype == "ELLIPSE":
                ellipse[k] = vec
            elif ctype == "BSPLINE":
                bs_degree[k] = deg_cls
                bs_logncp[k, 0] = log_ncp
            k += 1

    assert k == n_total, f"built {k} != cache {n_total}"
    np.savez_compressed(
        out,
        line=line,
        circle=circle,
        ellipse=ellipse,
        bspline_degree=bs_degree,
        bspline_logncp=bs_logncp,
    )
    print(f"[fullparam] {split}: {n_total} curves → {out}", flush=True)
    return out


class CurveTokenDataset(Dataset):
    """Frozen C2 inputs + type + 32-point recon target + full per-type params."""

    def __init__(self, split: str, force_rebuild: bool = False):
        self.base = ScaleCurvatureDataset(split)
        path = build_param_cache(split, force=force_rebuild)
        d = np.load(path)
        self.line = d["line"]
        self.circle = d["circle"]
        self.ellipse = d["ellipse"]
        self.bs_degree = d["bspline_degree"]
        self.bs_logncp = d["bspline_logncp"]
        self.split = split
        self.type_counts = self.base.type_counts
        self.type_id = self.base.type_id
        self.line_length_p90 = self.base.line_length_p90

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, idx: int) -> dict:
        i = int(idx)
        b = self.base[i]
        return {
            # frozen C2 inputs
            "shape_feats": b["feats_local"],
            "scale_feat": b["scale_feat"],
            # recon target in the same (curve-local) frame as the shape input
            "xyz_target": b["xyz_local"],
            "type_id": b["type_id"],
            "poly_len": b["poly_len"],
            # per-type parameter targets
            "line_param": torch.from_numpy(self.line[i]),
            "circle_param": torch.from_numpy(self.circle[i]),
            "ellipse_param": torch.from_numpy(self.ellipse[i]),
            "bspline_degree": torch.tensor(int(self.bs_degree[i]), dtype=torch.long),
            "bspline_logncp": torch.from_numpy(self.bs_logncp[i]),
        }


def collate(batch: list[dict]) -> dict:
    return {k: torch.stack([b[k] for b in batch], 0) for k in batch[0]}
