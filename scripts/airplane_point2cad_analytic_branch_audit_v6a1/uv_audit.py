"""UV periodicity audit."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4


def surface_periodicity(model: dict) -> dict:
    typ = model.get("type", "unknown")
    out = {
        "surface_type": typ,
        "u_periodic": False,
        "v_periodic": False,
        "u_period": None,
        "v_period": None,
    }
    if typ == "cylinder":
        out["u_periodic"] = True
        out["u_period"] = 2 * np.pi
    elif typ == "cone":
        out["u_periodic"] = True
        out["u_period"] = 2 * np.pi
    elif typ == "sphere":
        out["u_periodic"] = True
        out["v_periodic"] = True
        out["u_period"] = 2 * np.pi
        out["v_period"] = np.pi
    return out


def uv_delta(u1: float, v1: float, u2: float, v2: float, peri: dict) -> tuple[float, float, bool]:
    du = abs(u1 - u2)
    dv = abs(v1 - v2)
    seam = False
    if peri.get("u_periodic") and peri.get("u_period"):
        p = float(peri["u_period"])
        du = min(du, abs(p - du))
        if abs(abs(u1 - u2) - p) < 0.05 * p:
            seam = True
    if peri.get("v_periodic") and peri.get("v_period"):
        p = float(peri["v_period"])
        dv = min(dv, abs(p - dv))
        if abs(abs(v1 - v2) - p) < 0.05 * p:
            seam = True
    return du, dv, seam


def audit_uv_rejections(candidates: list[dict], frags: list[dict], surfaces_models: list[dict], meshes) -> dict:
    from airplane_point2cad_curve_branch_recovery_v6a.fragments import mesh_uv_frame, project_uv

    peri = [surface_periodicity(m) for m in surfaces_models]
    uv_frames = [mesh_uv_frame(m) for m in meshes]
    fid = {f["fragment_id"]: f for f in frags}
    before = 0
    after = 0
    seam_cross = 0
    for c in candidates:
        fi = fid.get(c["fragment_i"])
        fj = fid.get(c["fragment_j"])
        if not fi or not fj:
            continue
        sa, sb = fi["surface_pair"]
        # naive ratio rejection
        if max(c.get("uv_ratio_A", 0), c.get("uv_ratio_B", 0)) > 0.35 and c.get("normalized_gap", 1) > 1e-3:
            before += 1
        # periodic-aware check at endpoints
        ea, eb = c["endpoint_i"], c["endpoint_j"]
        uva = fi["surface_A_uv"]["start" if ea == "s" else "end"]
        uvb = fj["surface_A_uv"]["start" if eb == "s" else "end"]
        ext_a = np.linalg.norm(np.asarray(fi["surface_A_uv"]["max"]) - np.asarray(fi["surface_A_uv"]["min"]))
        du, dv, seam = uv_delta(uva[0], uva[1], uvb[0], uvb[1], peri[sa])
        ratio = max(du, dv) / max(ext_a, 1e-9)
        if ratio > 0.35 and c.get("normalized_gap", 1) > 1e-3:
            after += 1
        if seam:
            seam_cross += 1
    return {
        "surfaces": peri,
        "UV_REJECTIONS_BEFORE_UNWRAP": before,
        "UV_REJECTIONS_AFTER_UNWRAP": after,
        "UV_SEAM_CROSSING_COUNT": seam_cross,
        "UV_PARAMETERIZATION_NOTE": (
            "V6A uses PCA mesh frames for open_spline surfaces; periodic unwrap only applies "
            "to analytic cone/cylinder. Most UV_DISCONTINUITY on open_spline pairs is frame ambiguity, "
            "not provable seam crossing."
        ),
    }
