"""Complexity, geometry fingerprint, aircraft relevance — config-driven."""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from ..config import ADVANCED_OPS, COMPLEXITY, FINGERPRINT


def complexity_label(rec: dict[str, Any]) -> str:
    n_ops = int(rec.get("num_operations") or 0)
    advanced = 0
    for k in ADVANCED_OPS:
        flag = rec.get(f"has_{k}")
        if flag:
            advanced += 1
    n_bspline = int(rec.get("num_bspline") or 0)
    hard = (
        n_ops > COMPLEXITY["medium_max_ops"]
        or advanced >= COMPLEXITY["hard_advanced_min"]
        or n_bspline >= 4
        or (rec.get("has_loft") and rec.get("has_sweep"))
    )
    if hard:
        return "hard"
    medium = n_ops >= 6 or advanced == 1 or n_bspline >= 1
    if medium:
        return "medium"
    if n_ops <= COMPLEXITY["simple_max_ops"] and advanced == 0:
        return "simple"
    return "medium"


def geometry_fingerprint(rec: dict[str, Any], xyz: np.ndarray | None) -> str:
    cfg = FINGERPRINT
    ext = rec.get("bbox_extent") or [0, 0, 0]
    vol = rec.get("volume") or 0.0
    area = rec.get("surface_area") or 0.0
    ext_a = np.asarray(ext, dtype=np.float64)
    diag = float(np.linalg.norm(ext_a)) or 1.0
    ext_n = (ext_a / diag).round(cfg["bbox_decimals"])
    vol_n = round(float(vol) / (diag**3 + 1e-12), cfg["metric_decimals"])
    area_n = round(float(area) / (diag**2 + 1e-12), cfg["metric_decimals"])
    parts = [str(ext_n.tolist()), str(vol_n), str(area_n)]
    if xyz is not None and len(xyz):
        q = np.round(np.asarray(xyz[:, :3], dtype=np.float64) / diag / cfg["xyz_quant"])
        # order-invariant: sort quantized points
        q = q[np.lexsort((q[:, 2], q[:, 1], q[:, 0]))]
        parts.append(hashlib.sha256(q.astype(np.int32).tobytes()).hexdigest())
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def aircraft_relevance(rec: dict[str, Any]) -> int:
    """0=low, 1=possibly useful, 2=strongly useful. Not a train split."""
    score = 0
    if rec.get("has_loft") or rec.get("has_sweep"):
        score += 2
    if rec.get("has_revolve"):
        score += 1
    if rec.get("has_shell"):
        score += 1
    if int(rec.get("num_ellipse") or 0) > 0:
        score += 1
    if int(rec.get("num_bspline") or 0) >= 2:
        score += 1
    ext = rec.get("bbox_extent")
    if ext and len(ext) == 3:
        a = sorted(float(x) for x in ext)
        if a[2] > 1e-12 and a[0] / a[2] < 0.15 and a[1] / a[2] < 0.4:
            score += 2  # elongated / wing-like plate
        elif a[2] > 1e-12 and a[0] / a[2] < 0.25:
            score += 1
    if rec.get("has_mirror") or rec.get("has_pattern"):
        score += 1
    if score >= 4:
        return 2
    if score >= 2:
        return 1
    return 0
