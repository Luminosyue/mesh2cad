"""LoftBuilder: preflight → ThruSections → post-build guard. Never bypass OCC."""
from __future__ import annotations

from typing import Any

import numpy as np

from builders import occ_api
from builders.post_build_guard import post_build_guard
from builders.preflight import loft_preflight
from builders.profiles import extract_profiles


def execute(mesh, plan: dict[str, Any], part_bbox: dict[str, Any], guard_cfg: dict[str, Any], counters: dict[str, int], extracted=None) -> dict[str, Any]:
    counters["LOFT_REQUEST"] = counters.get("LOFT_REQUEST", 0) + 1
    extracted = extracted or extract_profiles(mesh, int(plan.get("sections") or 10), int(plan.get("profile_count") or 10))
    pre = loft_preflight(extracted, part_bbox["bbox_diag"], guard_cfg)
    if not pre["LOFT_PREFLIGHT_PASS"]:
        counters["LOFT_PREFLIGHT_FAIL"] = counters.get("LOFT_PREFLIGHT_FAIL", 0) + 1
        return {
            "executed": False,
            "rejected_stage": "PREFLIGHT",
            "LOFT_PREFLIGHT_PASS": False,
            "preflight": pre,
            "shape": None,
        }
    ai = extracted["axis_index"]
    plane = [i for i in range(3) if i != ai]
    wires = []
    for coordinate, uv in zip(extracted["stations"], extracted["profiles_uv"]):
        pts = np.zeros((len(uv), 3))
        pts[:, ai] = coordinate
        pts[:, plane] = uv
        wires.append(occ_api.polygon_wire(pts))
    try:
        shape = occ_api.thru_sections(wires, preflight_passed=True)
    except Exception as exc:
        return {"executed": False, "rejected_stage": "OCC", "error": f"{type(exc).__name__}: {exc}", "shape": None, "preflight": pre}
    post = post_build_guard(shape, part_bbox, extracted["PROFILE_SUPPORT_BBOX"], guard_cfg)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT"] = counters.get("POST_BUILD_REJECT", 0) + 1
        return {"executed": True, "rejected_stage": "POST_BUILD", "BUILDER_OUTPUT_REJECTED": True, "post": post, "preflight": pre, "shape": None}
    return {"executed": True, "rejected_stage": None, "shape": shape, "preflight": pre, "post": post, "extracted": extracted}
