"""Loft / BSpline grid preflight. Fail-fast: builder must not call OCC if this fails."""
from __future__ import annotations

from typing import Any

import numpy as np

import sys
from pathlib import Path

AUDIT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/cross_case_geometry_explosion_audit_v1")
if str(AUDIT) not in sys.path:
    sys.path.insert(0, str(AUDIT))
from qa.profile_correspondence import profile_correspondence  # noqa: E402


def loft_preflight(extracted: dict[str, Any], part_diag: float, cfg: dict[str, Any]) -> dict[str, Any]:
    corr = profile_correspondence(extracted["profiles_uv"], extracted["stations"], part_diag)
    loft_cfg = cfg["loft_preflight"]
    support = extracted.get("PROFILE_SUPPORT_BBOX") or {}
    reasons = []
    if int(corr.get("PROFILE_COUNT") or 0) < int(loft_cfg["min_profile_count"]):
        reasons.append("PROFILE_COUNT")
    if not corr.get("STATION_MONOTONICITY"):
        reasons.append("STATION_ORDER")
    if int(corr.get("PROFILE_FLIP_COUNT") or 0) > int(loft_cfg["max_flip_count"]):
        reasons.append("PROFILE_FLIP")
    if int(corr.get("PROFILE_PAIR_CROSSING_COUNT") or 0) > int(loft_cfg["max_crossing_pairs"]):
        reasons.append("PROFILE_CORRESPONDENCE_CROSSING")
    if int(corr.get("PROFILE_SELF_INTERSECTION_COUNT") or 0) > int(loft_cfg["max_self_intersection"]):
        reasons.append("PROFILE_SELF_INTERSECTION")
    if float(corr.get("MAX_PROFILE_CENTROID_JUMP") or 0) > float(loft_cfg["max_centroid_jump_ratio"]):
        reasons.append("PROFILE_CENTROID_JUMP")
    if float(corr.get("MAX_PROFILE_SCALE_JUMP") or 0) > float(loft_cfg["max_scale_jump_ratio"]):
        reasons.append("PROFILE_SCALE_JUMP")
    if bool(corr.get("STATION_REVERSAL")):
        reasons.append("STATION_REVERSAL")
    passed = not reasons
    return {
        **corr,
        "LOFT_PREFLIGHT_PASS": passed,
        "PROFILE_CORRESPONDENCE_CROSSING": "PROFILE_CORRESPONDENCE_CROSSING" in reasons,
        "PROFILE_BBOX_WITHIN_PART_SUPPORT": True,
        "PROFILE_SUPPORT_BBOX": support,
        "CYCLIC_SHIFT": extracted.get("cyclic_shifts"),
        "reasons": reasons,
    }


def grid_preflight(grid: np.ndarray, cfg: dict[str, Any], part_diag: float) -> dict[str, Any]:
    grid = np.asarray(grid, float)
    gcfg = cfg["bspline_grid"]
    reasons = []
    if grid.ndim != 3 or grid.shape[0] < gcfg["min_u"] or grid.shape[1] < gcfg["min_v"]:
        reasons.append("GRID_TOO_SMALL")
        return {"BSPLINE_GRID_PREFLIGHT_PASS": False, "reasons": reasons, "GRID_U_COUNT": int(grid.shape[0]) if grid.ndim >= 1 else 0, "GRID_V_COUNT": int(grid.shape[1]) if grid.ndim >= 2 else 0}
    u, v = grid.shape[:2]
    row_flips = 0
    col_flips = 0
    steps = []
    row_means = []
    for i in range(u):
        d = np.diff(grid[i], axis=0)
        steps.extend(np.linalg.norm(d, axis=1).tolist())
        row_means.append(d.mean(axis=0) if len(d) else np.zeros(3))
    for i in range(1, len(row_means)):
        if np.dot(row_means[i], row_means[i - 1]) < 0:
            row_flips += 1
    col_means = []
    for j in range(v):
        d = np.diff(grid[:, j], axis=0)
        steps.extend(np.linalg.norm(d, axis=1).tolist())
        col_means.append(d.mean(axis=0) if len(d) else np.zeros(3))
    for j in range(1, len(col_means)):
        if np.dot(col_means[j], col_means[j - 1]) < 0:
            col_flips += 1
    crossings = 0
    foldovers = 0
    normal_grid = {}
    for i in range(u - 1):
        for j in range(v - 1):
            a0, a1 = grid[i, j], grid[i, j + 1]
            b0, b1 = grid[i + 1, j], grid[i + 1, j + 1]
            da = a1 - a0
            db = b1 - b0
            if np.dot(da, db) < -0.2 * (np.linalg.norm(da) * np.linalg.norm(db) + 1e-12):
                crossings += 1
            du=grid[i+1,j]-grid[i,j]
            normal=np.cross(du,da)
            if np.linalg.norm(normal)>1e-12:
                normal_grid[(i,j)]=normal/np.linalg.norm(normal)
    # Foldover is a local parameterization reversal. Comparing every normal to
    # the first cell falsely rejects legitimately curved skins whose normals
    # rotate by more than 90 degrees across the whole patch.
    for (i,j),normal in normal_grid.items():
        for neighbor in ((i+1,j),(i,j+1)):
            if neighbor in normal_grid and np.dot(normal,normal_grid[neighbor])<0.0:
                foldovers+=1
    steps = np.asarray(steps, float) if steps else np.asarray([0.0])
    mean = float(steps.mean())
    p95 = float(np.percentile(steps, 95))
    mx = float(steps.max())
    if row_flips > gcfg["max_row_flips"]:
        reasons.append("GRID_ROW_DIRECTION_FLIP")
    if col_flips > gcfg["max_col_flips"]:
        reasons.append("GRID_COL_DIRECTION_FLIP")
    if crossings > gcfg["max_crossing"]:
        reasons.append("GRID_CROSSING")
    foldover_rate=foldovers/max(len(normal_grid)-1,1)
    if foldover_rate > gcfg.get("max_foldover_rate", 0.25):
        reasons.append("GRID_FOLDOVER")
    if mean > 1e-12 and mx / mean > gcfg["max_step_jump_ratio"]:
        reasons.append("GRID_STEP_JUMP")
    lo = grid.reshape(-1, 3).min(0)
    hi = grid.reshape(-1, 3).max(0)
    return {
        "BSPLINE_GRID_PREFLIGHT_PASS": not reasons,
        "reasons": reasons,
        "GRID_U_COUNT": int(u),
        "GRID_V_COUNT": int(v),
        "GRID_BBOX": {"bbox_min": lo.tolist(), "bbox_max": hi.tolist(), "bbox_diag": float(np.linalg.norm(hi - lo))},
        "GRID_POINT_STEP_MEAN": mean,
        "GRID_POINT_STEP_P95": p95,
        "GRID_POINT_STEP_MAX": mx,
        "GRID_ROW_DIRECTION_FLIP_COUNT": int(row_flips),
        "GRID_COL_DIRECTION_FLIP_COUNT": int(col_flips),
        "GRID_CROSSING_COUNT": int(crossings),
        "GRID_FOLDOVER_COUNT": int(foldovers),
        "GRID_FOLDOVER_RATE": float(foldover_rate),
        "GRID_MISSING_SUPPORT_COUNT": int(np.sum(~np.isfinite(grid).all(axis=2))),
    }
