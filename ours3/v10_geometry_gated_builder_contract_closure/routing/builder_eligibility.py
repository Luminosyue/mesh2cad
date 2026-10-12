"""Builder eligibility from geometry evidence only. Qwen cannot write this object."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import yaml

from builders.preflight import loft_preflight
from builders.profiles import extract_profiles


FAMILIES = ["PLANE", "EXTRUSION", "CYLINDER", "REVOLUTION", "SWEEP", "LOFT", "PERIODIC_BSPLINE", "GENERAL_BSPLINE"]
COMPAT_PATH = Path(__file__).resolve().parents[1] / "config" / "builder_compatibility.yaml"
COMPAT = yaml.safe_load(COMPAT_PATH.read_text(encoding="utf-8")) if COMPAT_PATH.is_file() else {}


def _bank_validity(bank: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out = {k: {"valid": False, "reason": "NO_BANK_EVIDENCE", "score": 0.0} for k in FAMILIES}
    if not bank:
        return out
    for cand in bank.get("candidate_primitives") or []:
        kind = str(cand.get("primitive_type") or "").upper()
        if kind not in out:
            continue
        valid = bool((cand.get("validity") or {}).get("valid", False))
        reason = (cand.get("validity") or {}).get("reason")
        err = cand.get("fit_error") or {}
        score = 0.0
        if err.get("mean") is not None:
            score = float(max(0.0, 1.0 - float(err["mean"]) * 40.0))
        elif valid:
            score = 0.7
        prev = out[kind]
        if valid and (not prev["valid"] or score > prev["score"]):
            out[kind] = {"valid": True, "score": score, "reason": None}
        elif not prev["valid"]:
            out[kind] = {"valid": False, "score": max(prev["score"], score), "reason": reason or prev["reason"]}
    for sel in bank.get("selected_primitives") or []:
        kind = str(sel.get("primitive_type") or "").upper()
        if kind in out:
            out[kind]["valid"] = True
            out[kind]["score"] = max(float(out[kind].get("score") or 0), 0.8)
            out[kind]["reason"] = None
    return out


def _pca(vertices: np.ndarray):
    center = vertices.mean(0)
    _, _, vh = np.linalg.svd(vertices - center, full_matrices=False)
    return center, vh


def compute_eligibility(mesh, spec: dict[str, Any] | None, bank: dict[str, Any] | None, analyzer: dict[str, Any] | None, guard_cfg: dict[str, Any]) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, float)
    lo, hi = np.asarray(mesh.bounds, float)
    part_bbox = {"bbox_min": lo.tolist(), "bbox_max": hi.tolist(), "bbox_diag": float(np.linalg.norm(hi - lo))}
    eligibility = _bank_validity(bank)
    center, axes = _pca(vertices)
    q = (vertices - center) @ axes.T
    extents = np.ptp(q, axis=0)
    # plane: bank planes or thin residual
    residual = np.abs(q[:, 2])
    plane_score = float(np.clip(1.0 - residual.mean() / (0.08 * max(part_bbox["bbox_diag"], 1e-9)), 0, 1))
    if plane_score >= 0.55:
        eligibility["PLANE"] = {"valid": True, "score": max(plane_score, float(eligibility["PLANE"].get("score") or 0)), "reason": None}

    bins = np.linspace(q[:, 0].min(), q[:, 0].max(), 8)
    areas = []
    for a, b in zip(bins[:-1], bins[1:]):
        sl = q[(q[:, 0] >= a) & (q[:, 0] <= b)][:, 1:]
        if len(sl) >= 4:
            areas.append(float(np.prod(np.ptp(sl, axis=0) + 1e-9)))
    consistency = float(np.clip(1.0 - np.std(areas) / (np.mean(areas) + 1e-9), 0, 1)) if len(areas) >= 2 else 0.0

    radial = np.linalg.norm(q[:, 1:], axis=1)
    cyl_res = float(np.abs(radial - np.median(radial)).mean() / max(part_bbox["bbox_diag"], 1e-9))
    cyl_ok = cyl_res < 0.04
    eligibility["CYLINDER"] = {"valid": cyl_ok, "score": float(np.clip(1.0 - cyl_res * 12, 0, 1)), "reason": None if cyl_ok else "RADIAL_ERROR_TOO_HIGH"}
    rev_ok = cyl_ok and float(np.std(radial) / (np.mean(radial) + 1e-9)) > 0.12
    eligibility["REVOLUTION"] = {"valid": rev_ok, "score": float(eligibility["CYLINDER"]["score"] * 0.7), "reason": None if rev_ok else "NO_ROTATIONAL_SYMMETRY"}

    extracted = None
    loft_info = {"valid": False, "reason": "PROFILES_UNAVAILABLE", "score": 0.0}
    try:
        extracted = extract_profiles(mesh, 10, 10)
        pre = loft_preflight(extracted, part_bbox["bbox_diag"], guard_cfg)
        loft_ok = bool(pre["LOFT_PREFLIGHT_PASS"])
        loft_info = {
            "valid": loft_ok,
            "score": 0.75 if loft_ok else 0.15,
            "reason": None if loft_ok else (pre["reasons"][0] if pre.get("reasons") else "PROFILE_CORRESPONDENCE_INVALID"),
            "preflight": {k: pre[k] for k in ("LOFT_PREFLIGHT_PASS", "PROFILE_COUNT", "PROFILE_PAIR_CROSSING_COUNT", "MAX_PROFILE_SCALE_JUMP", "MAX_PROFILE_CENTROID_JUMP", "reasons") if k in pre},
        }
        scales = [float(np.linalg.norm(np.asarray(uv, float) - np.asarray(uv, float).mean(0), axis=1).mean()) for uv in extracted["profiles_uv"]]
        if len(scales) >= 2:
            consistency = max(consistency, float(np.clip(1.0 - np.std(scales) / (np.mean(scales) + 1e-9), 0, 1)))
    except Exception as exc:
        loft_info = {"valid": False, "reason": f"PROFILE_EXTRACT_FAILED:{type(exc).__name__}", "score": 0.0}
    closed_profile = extracted is not None and bool(extracted.get("closed", True))
    extrusion_ok = consistency >= 0.35 or bool(eligibility["EXTRUSION"].get("valid")) or (closed_profile and plane_score >= 0.55)
    eligibility["EXTRUSION"] = {
        "valid": bool(extrusion_ok),
        "score": max(consistency, float(eligibility["EXTRUSION"].get("score") or 0)),
        "reason": None if extrusion_ok else "SECTION_NOT_CONSTANT",
        "depth_ref": "SPEC.EXTENTS.longitudinal",
        "direction": axes[0].tolist(),
    }
    eligibility["LOFT"] = loft_info
    # Sweep requires a valid spine + non-crossing section; reuse loft correspondence as proxy.
    eligibility["SWEEP"] = {
        "valid": bool(loft_info["valid"]) and consistency >= 0.4,
        "score": float(loft_info["score"]) * 0.6,
        "reason": None if (loft_info["valid"] and consistency >= 0.4) else "SPINE_OR_SECTION_INVALID",
    }
    bspline_ok = bool(loft_info["valid"])
    eligibility["GENERAL_BSPLINE"] = {
        "valid": bspline_ok,
        "score": 0.2 if bspline_ok else 0.05,
        "reason": None if bspline_ok else "CONTROL_NET_SUPPORT_INSUFFICIENT",
    }
    eligibility["PERIODIC_BSPLINE"] = {
        "valid": False,
        "score": 0.05,
        "reason": "PERIODICITY_NOT_SUPPORTED_BY_EVIDENCE",
    }
    allowed = [name for name, payload in eligibility.items() if payload.get("valid")]
    if not allowed:
        if eligibility["EXTRUSION"]["score"] >= 0.3:
            eligibility["EXTRUSION"]["valid"] = True
            eligibility["EXTRUSION"]["reason"] = None
            allowed = ["EXTRUSION"]
        elif eligibility["PLANE"]["valid"]:
            allowed = ["PLANE"]
    for name, payload in eligibility.items():
        payload["compatibility_requires"] = list((COMPAT.get(name) or {}).get("requires") or [])
    return {
        "BUILDER_ELIGIBILITY": eligibility,
        "ALLOWED_BUILDERS": allowed,
        "part_bbox": part_bbox,
        "extracted_profiles": extracted,
        "compatibility_graph": COMPAT,
        "source": "GEOMETRY_ANALYZER+PRIMITIVE_BANK+MEASURED_SPEC+PROFILE_EVIDENCE",
        "qwen_authored": False,
    }
