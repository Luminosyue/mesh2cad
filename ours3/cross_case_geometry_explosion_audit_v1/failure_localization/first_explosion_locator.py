"""Locate the first stage where geometry explosion appears for a CAD part."""
from __future__ import annotations

from typing import Any

STAGE_ORDER = [
    "STAGE_0_P3_SEGMENT",
    "STAGE_1_CAD_PART_AFTER_MERGE",
    "STAGE_2_GEOMETRY_ANALYZER",
    "STAGE_3_MEASURED_CAD_SPEC",
    "STAGE_4_SELECTED_PRIMITIVE",
    "STAGE_5_SEMANTIC_WIREFRAME",
    "STAGE_6_DESIGN_INTENT",
    "STAGE_7_BUILDER_RAW_OUTPUT",
    "STAGE_8_TRIMMED_BREP",
    "STAGE_9_PARAMETER_OPTIMIZED",
    "STAGE_10_ASSEMBLY_PLACEMENT",
]

FAILURE_CLASSES = [
    "PART_MERGE_ERROR",
    "TRANSFORM_ERROR",
    "SCALE_ERROR",
    "AXIS_ERROR",
    "STATION_ERROR",
    "PROFILE_CORRESPONDENCE_ERROR",
    "OPEN_CHAIN_CORRESPONDENCE_ERROR",
    "PRIMITIVE_SELECTION_ERROR",
    "PRIMITIVE_PARAMETER_ERROR",
    "LOFT_DOMAIN_ERROR",
    "BSPLINE_CONTROL_NET_ERROR",
    "SWEEP_SPINE_ERROR",
    "REVOLUTION_AXIS_ERROR",
    "EXTRUSION_DIRECTION_ERROR",
    "WIREFRAME_TOPOLOGY_ERROR",
    "PCURVE_ERROR",
    "TRIMMING_ERROR",
    "ASSEMBLY_PLACEMENT_ERROR",
    "UNKNOWN",
]


def _status(stage: dict[str, Any] | None) -> str:
    if not stage:
        return "ABSENT"
    return str(stage.get("GEOMETRY_EXPLOSION_STATUS") or stage.get("status") or "ABSENT")


def locate(stages: dict[str, Any], extras: dict[str, Any] | None = None) -> dict[str, Any]:
    extras = extras or {}
    first = None
    first_payload = None
    for name in STAGE_ORDER:
        status = _status(stages.get(name))
        if status == "REJECT":
            first = name
            first_payload = stages[name]
            break
    primary, secondary = classify_failure(first, stages, extras)
    return {
        "FIRST_EXPLOSION_STAGE": first,
        "PRIMARY_FAILURE_CLASS": primary,
        "SECONDARY_FAILURE_CLASSES": secondary,
        "BBOX_RATIO_AT_FAILURE": None if not first_payload else first_payload.get("CAD_BBOX_DIAG_RATIO") or first_payload.get("CAD_TO_PART_DIAG_RATIO"),
        "MAX_EDGE_RATIO_AT_FAILURE": None if not first_payload else first_payload.get("MAX_EDGE_LENGTH_RATIO"),
        "MAX_FACE_RATIO_AT_FAILURE": None if not first_payload else first_payload.get("MAX_FACE_EXTENT_RATIO"),
        "COORDINATE_FRAME": None if not first_payload else first_payload.get("COORDINATE_FRAME_DECLARATION"),
        "DETAIL": None if not first_payload else first_payload.get("GEOMETRY_EXPLOSION_REASONS") or first_payload.get("detail"),
    }


def classify_failure(first_stage: str | None, stages: dict[str, Any], extras: dict[str, Any]) -> tuple[str, list[str]]:
    secondary: list[str] = []
    if first_stage is None:
        return "UNKNOWN", secondary
    builder = str(extras.get("builder") or extras.get("representation") or "").upper()
    corr = extras.get("profile_correspondence") or {}
    primitive = extras.get("primitive_selection") or {}
    transform = extras.get("transform") or {}

    if first_stage == "STAGE_1_CAD_PART_AFTER_MERGE" and _status(stages.get("STAGE_0_P3_SEGMENT")) == "PASS":
        return "PART_MERGE_ERROR", secondary
    if first_stage == "STAGE_10_ASSEMBLY_PLACEMENT":
        return "ASSEMBLY_PLACEMENT_ERROR", secondary
    if first_stage in ("STAGE_4_SELECTED_PRIMITIVE",) or (
        first_stage in ("STAGE_7_BUILDER_RAW_OUTPUT", "STAGE_8_TRIMMED_BREP")
        and primitive.get("conflict")
    ):
        secondary.append("PRIMITIVE_SELECTION_ERROR")
    if first_stage == "STAGE_5_SEMANTIC_WIREFRAME":
        return "WIREFRAME_TOPOLOGY_ERROR", secondary
    if first_stage in ("STAGE_7_BUILDER_RAW_OUTPUT", "STAGE_8_TRIMMED_BREP", "STAGE_9_PARAMETER_OPTIMIZED"):
        payload = stages.get(first_stage) or {}
        reasons = set(payload.get("GEOMETRY_EXPLOSION_REASONS") or [])
        if payload.get("CONTROL_NET_OUTLIER") or "CONTROL_NET_OUT_OF_RANGE" in reasons:
            primary = "BSPLINE_CONTROL_NET_ERROR"
        elif int(corr.get("PROFILE_PAIR_CROSSING_COUNT") or 0) > 2 or corr.get("LOFT_PREFLIGHT_PASS") is False:
            primary = "PROFILE_CORRESPONDENCE_ERROR"
            if "LOFT" in builder or "SKIN" in builder or "BSPLINE" in builder:
                secondary.append("LOFT_DOMAIN_ERROR")
        elif payload.get("SURFACE_DOMAIN_EXPLOSION") or "LOFT_DOMAIN_ERROR" in reasons:
            primary = "LOFT_DOMAIN_ERROR"
        elif "SWEEP" in builder:
            primary = "SWEEP_SPINE_ERROR"
        elif "REVOL" in builder:
            primary = "REVOLUTION_AXIS_ERROR"
        elif "EXTRUD" in builder or "EXTRUSION" in builder or "PRISM" in builder:
            primary = "EXTRUSION_DIRECTION_ERROR"
        elif "PCURVE_DOMAIN_ERROR" in reasons:
            primary = "PCURVE_ERROR"
        elif first_stage == "STAGE_8_TRIMMED_BREP" and _status(stages.get("STAGE_7_BUILDER_RAW_OUTPUT")) == "PASS":
            primary = "TRIMMING_ERROR"
        elif transform.get("TRANSFORM_SCALE_MISMATCH"):
            primary = "TRANSFORM_ERROR"
        elif "BBOX_DIAG_RATIO_TOO_HIGH" in reasons:
            primary = "SCALE_ERROR"
            if "LOFT" in builder or "SKIN" in builder:
                secondary.append("LOFT_DOMAIN_ERROR")
        else:
            primary = "UNKNOWN"
        if primitive.get("conflict") and "PRIMITIVE_SELECTION_ERROR" not in secondary:
            secondary.append("PRIMITIVE_SELECTION_ERROR")
        return primary, list(dict.fromkeys(secondary))
    if first_stage in ("STAGE_2_GEOMETRY_ANALYZER", "STAGE_3_MEASURED_CAD_SPEC"):
        return "SCALE_ERROR", secondary
    return "UNKNOWN", secondary
