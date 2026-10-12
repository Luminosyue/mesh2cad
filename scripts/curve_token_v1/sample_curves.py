#!/usr/bin/env python3
"""Fixed-size sampled representation of every curve.

Sampling is (approximately) uniform in **arc length** rather than in parameter,
which matters most for B-splines whose parameterisation is far from arc length.
The strategy that actually produced each curve's samples is recorded per curve.
"""

from __future__ import annotations

import numpy as np

from .canonicalize_curves import Normalization
from .config import CURVE_TYPE_IDS
from .occ_curve_v1 import arclength_params, eval_point_tangent


def sample_curve(adaptor, n_sample: int, u0: float, u1: float) -> dict:
    params, mode = arclength_params(adaptor, n_sample, u0, u1)
    xyz = np.zeros((n_sample, 3), dtype=np.float64)
    tan = np.zeros((n_sample, 3), dtype=np.float64)
    mask = np.zeros(n_sample, dtype=bool)
    for i, u in enumerate(params):
        try:
            p, t = eval_point_tangent(adaptor, float(u))
        except Exception:  # noqa: BLE001
            continue
        if not (np.all(np.isfinite(p)) and np.all(np.isfinite(t))):
            continue
        xyz[i] = p
        tan[i] = t
        mask[i] = True

    # Arc length of the sampled polyline; compared against the exact length in
    # validation to catch under-resolved curves.
    poly_len = 0.0
    if mask.sum() >= 2:
        pts = xyz[mask]
        poly_len = float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())

    return {
        "u": params.astype(np.float64),
        "xyz": xyz,
        "tangent": tan,
        "mask": mask,
        "mode": mode,
        "polyline_length": poly_len,
    }


def build_sample_arrays(
    adaptors: list,
    records: list[dict],
    n_sample: int,
    nz: Normalization,
) -> dict[str, np.ndarray]:
    """Sample every curve of one CAD object into stacked [N_curve, n_sample, *] arrays.

    No padding to a dataset-wide MAX_CURVES: N_curve is this object's real count,
    and batch padding is left to a future dataloader.
    """
    n = len(records)
    xyz = np.zeros((n, n_sample, 3), dtype=np.float32)
    xyz_n = np.zeros((n, n_sample, 3), dtype=np.float32)
    tan = np.zeros((n, n_sample, 3), dtype=np.float32)
    mask = np.zeros((n, n_sample), dtype=bool)
    # float64: curve_u is the key for re-evaluating a curve exactly, so rounding
    # it to float32 would inject avoidable error at every downstream use
    uu = np.zeros((n, n_sample), dtype=np.float64)
    modes: list[str] = []
    poly_len = np.zeros(n, dtype=np.float32)

    for i, (adaptor, rec) in enumerate(zip(adaptors, records)):
        s = sample_curve(adaptor, n_sample, rec["u_start"], rec["u_end"])
        xyz[i] = s["xyz"].astype(np.float32)
        xyz_n[i] = nz.points(s["xyz"]).astype(np.float32)
        tan[i] = s["tangent"].astype(np.float32)
        mask[i] = s["mask"]
        uu[i] = s["u"]
        modes.append(s["mode"])
        poly_len[i] = s["polyline_length"]
        rec["sampling"] = {
            "n_sample": int(n_sample),
            "mode": s["mode"],
            "n_valid": int(s["mask"].sum()),
            "polyline_length": float(s["polyline_length"]),
        }

    return {
        "curve_xyz": xyz,
        "curve_xyz_normalized": xyz_n,
        # unit tangents are invariant under uniform scale + translation, so one
        # array serves both coordinate frames
        "curve_tangent": tan,
        "curve_mask": mask,
        "curve_u": uu,
        "curve_polyline_length": poly_len,
        "curve_type_id": np.array(
            [CURVE_TYPE_IDS.get(r["curve_type"], CURVE_TYPE_IDS["OTHER"]) for r in records],
            dtype=np.int32,
        ),
        "curve_length": np.array([r["length"] for r in records], dtype=np.float32),
        "curve_length_normalized": np.array(
            [nz.s * r["length"] for r in records], dtype=np.float32
        ),
        "curve_edge_id": np.array([r["edge_id"] for r in records], dtype=np.int32),
        "curve_is_closed": np.array([r["is_closed"] for r in records], dtype=bool),
        "curve_n_faces": np.array([r["n_faces"] for r in records], dtype=np.int32),
        "sampling_mode": np.array(modes, dtype="<U24"),
        "n_sample": np.array([n_sample], dtype=np.int64),
        "num_curves": np.array([n], dtype=np.int64),
    }
