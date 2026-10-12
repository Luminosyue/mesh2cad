from __future__ import annotations

from typing import Any

import numpy as np

from .geometry_features import mixed_structure_score


def _clip01(x: float) -> float:
    return float(np.clip(x, 0.0, 1.0))


def compute_router_scores(features: dict[str, Any], mesh) -> dict[str, Any]:
    tr = features["THICKNESS_RATIO"]
    extrusion = features["EXTRUSION_EVIDENCE"]
    revolution = features["REVOLUTION_SCORE"]
    freeform = features["FREEFORM_SCORE"]
    planar = features["PLANAR_SUPPORT_RATIO"]
    mixed, regime_count, entropy = mixed_structure_score(mesh, features)

    thin_local = _clip01(1.0 - features["THICKNESS_P50"] / 0.08)
    thin_bbox = _clip01(1.0 - tr / 0.16)
    thin_score = 0.5 * thin_local + 0.5 * thin_bbox
    av = features.get("area_volume_ratio") or 0.0
    shell_like = _clip01(min(1.0, max(0.0, (av - 25.0) / 90.0)))
    curved_surface = _clip01(0.5 * features["HIGH_CURVATURE_RATIO"] + 0.3 * features["MEDIUM_CURVATURE_RATIO"] + 0.2 * freeform)
    regular_extrusion = _clip01(extrusion * (1.0 - 0.5 * freeform))
    volumetric = _clip01(0.4 * (1.0 - shell_like) + 0.3 * min(1.0, tr / 0.22) + 0.3 * (1.0 - features["SECTION_AREA_CV"]))
    revolve_gap = _clip01(revolution * (1.0 - regular_extrusion))
    section_var = _clip01(0.5 * features["SECTION_AREA_CV"] + 0.5 * features["SECTION_SHAPE_VARIATION"])

    cadfit_score = _clip01(
        0.40 * regular_extrusion
        + 0.25 * volumetric
        + 0.10 * planar
        + 0.15 * (1.0 if av < 40.0 else 0.0)
        + 0.10 * (revolution if regular_extrusion > 0.4 else 0.0)
        - 0.15 * freeform
        - 0.10 * mixed
        - 0.10 * thin_score
        - 0.15 * revolve_gap
    )
    routeb_score = _clip01(
        0.25 * thin_score
        + 0.25 * shell_like
        + 0.20 * freeform
        + 0.15 * curved_surface
        + 0.15 * section_var
        + 0.15 * revolve_gap
        - 0.15 * regular_extrusion
        - 0.10 * volumetric
    )
    decompose_score = _clip01(
        0.50 * mixed
        + 0.15 * min(1.0, max(0.0, (regime_count - 1) / 2.0))
        + 0.10 * entropy
        + 0.30 * (1.0 if (revolution > 0.5 and av > 80.0) else 0.0)
    )

    scores = {
        "CADFIT_SCORE": float(cadfit_score),
        "ROUTEB_SCORE": float(routeb_score),
        "DECOMPOSE_SCORE": float(decompose_score),
        "mixed_structure_score": float(mixed),
        "geometry_regime_count": int(regime_count),
        "internal_boundary_score": float(entropy),
    }

    ranked = sorted(
        [
            ("REGULAR_CADFIT", cadfit_score),
            ("THIN_FREEFORM", routeb_score),
            ("MIXED_STRUCTURE", decompose_score),
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    if ranked[0][0] == "MIXED_STRUCTURE" and ranked[0][1] < ranked[1][1] + 0.08:
        ranked = ranked[1:] + ranked[:1]
    best_name, best_val = ranked[0]
    second_val = ranked[1][1]
    confidence = _clip01(0.5 + 0.5 * (best_val - second_val))

    reason_codes = []
    if tr < 0.15 or thin_local > 0.55:
        reason_codes.append("THIN_SHEET")
    if shell_like > 0.45:
        reason_codes.append("THIN_SHELL_HIGH_AV_RATIO")
    if features["SECTION_AREA_CV"] > 0.35 or features["SECTION_SHAPE_VARIATION"] > 0.35:
        reason_codes.append("HIGH_SECTION_VARIATION")
    if regular_extrusion > 0.55:
        reason_codes.append("STRONG_EXTRUSION_EVIDENCE")
    if revolution > 0.55:
        reason_codes.append("ROTATIONAL_CORE")
    if revolve_gap > 0.45:
        reason_codes.append("REVOLVE_EVIDENCE_WITHOUT_PRISMATIC")
    if freeform > 0.55:
        reason_codes.append("FREEFORM_SURFACE_DOMINANT")
    if mixed > 0.45 or regime_count >= 3:
        reason_codes.append("MULTIPLE_GEOMETRY_REGIMES")

    selected_route = best_name
    if confidence < 0.35:
        selected_route = "UNSUPPORTED"
        reason_codes.append("LOW_ROUTER_CONFIDENCE")

    route_map = {
        "REGULAR_CADFIT": "CADFIT",
        "THIN_FREEFORM": "DORA_POINT2CAD",
        "MIXED_STRUCTURE": "DECOMPOSE_FIRST",
        "UNSUPPORTED": "UNSUPPORTED",
    }

    return {
        **features,
        **scores,
        "selected_route": selected_route,
        "selected_backend": route_map[selected_route],
        "confidence": float(confidence),
        "reason_codes": reason_codes,
        "score_ranking": [{"route": n, "score": float(v)} for n, v in ranked],
    }
