"""Immediate post-OCC geometry guard. Rejected shapes never enter wireframe/QA/TTS."""
from __future__ import annotations

from typing import Any

import sys
from pathlib import Path

AUDIT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/cross_case_geometry_explosion_audit_v1")
if str(AUDIT) not in sys.path:
    sys.path.insert(0, str(AUDIT))
from qa.occ_metrics import bbox_of_shape, measure_shape  # noqa: E402


def post_build_guard(shape, part_bbox: dict[str, Any], profile_bbox: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    measured = measure_shape(shape)
    part_diag = max(float(part_bbox.get("bbox_diag") or 1e-12), 1e-12)
    profile_diag = max(float(profile_bbox.get("bbox_diag") or part_diag), 1e-12)
    out_diag = float(measured.get("bbox_diag") or 0.0)
    post = cfg["post_build"]
    reasons = []
    if out_diag / part_diag >= post["output_to_part_diag_reject"]:
        reasons.append("OUTPUT_BBOX_DIAG_RATIO_TO_PART")
    if out_diag / profile_diag >= post["output_to_profile_diag_reject"]:
        reasons.append("OUTPUT_TO_PROFILE_BBOX_RATIO")
    if float(measured.get("max_edge_length") or 0) / part_diag >= post["max_edge_to_part_reject"]:
        reasons.append("MAX_EDGE_RATIO_TO_PART")
    if float(measured.get("max_face_bbox_diag") or 0) / part_diag >= post["max_face_to_part_reject"]:
        reasons.append("MAX_FACE_EXTENT_RATIO_TO_PART")
    return {
        "BUILDER_OUTPUT_REJECTED": bool(reasons),
        "reasons": reasons,
        "OUTPUT_BBOX_DIAG_RATIO_TO_PART": out_diag / part_diag,
        "MAX_EDGE_RATIO_TO_PART": float(measured.get("max_edge_length") or 0) / part_diag,
        "MAX_FACE_EXTENT_RATIO_TO_PART": float(measured.get("max_face_bbox_diag") or 0) / part_diag,
        "measured": {k: measured[k] for k in ("bbox_min", "bbox_max", "bbox_diag", "centroid", "max_edge_length", "max_face_bbox_diag", "control_point_count", "control_point_bbox") if k in measured},
    }
