from .part_route_state import PartRouteStatus


def classify_no_high_fidelity(role, evidence, allowed_builders, executable_builders):
    role = str(role or "UNKNOWN").upper()
    if role.startswith("UNKNOWN"):
        return PartRouteStatus.SEMANTIC_UNCERTAIN.value, "SEMANTIC_ROLE_UNCERTAIN"
    if role == "ROAD_WHEEL":
        if not evidence.get("cylinder_geometry_supported") and not evidence.get("revolution_geometry_supported"):
            return PartRouteStatus.GEOMETRY_EVIDENCE_INSUFFICIENT.value, "CIRCULAR_GEOMETRY_EVIDENCE_INSUFFICIENT"
        if evidence.get("cylinder_geometry_supported") and "CYLINDER" not in allowed_builders:
            return PartRouteStatus.NO_HIGH_FIDELITY_BUILDER.value, "GEOMETRY_SUPPORTS_BUILDER_BUT_ELIGIBILITY_MISSING"
        if evidence.get("revolution_geometry_supported") and "REVOLUTION" not in executable_builders:
            return PartRouteStatus.NO_HIGH_FIDELITY_BUILDER.value, "ELIGIBILITY_SUPPORTS_BUILDER_BUT_RUNTIME_MISSING"
    if role == "TRACK":
        if not evidence.get("closed_path_available") or not evidence.get("cross_section_available"):
            return PartRouteStatus.GEOMETRY_EVIDENCE_INSUFFICIENT.value, "TRACK_PATH_EVIDENCE_INSUFFICIENT"
        if "SWEEP" not in executable_builders:
            return PartRouteStatus.NO_HIGH_FIDELITY_BUILDER.value, "MISSING_EXECUTABLE_SWEEP"
    if role in {"FREEFORM_SKIN", "ORNAMENT", "UNKNOWN_BUILDING_PART"}:
        return PartRouteStatus.UNSUPPORTED_FEATURE.value, "CURRENT_FEATURE_FAMILY_UNSUPPORTED"
    return PartRouteStatus.NO_HIGH_FIDELITY_BUILDER.value, "NO_FIDELITY_COMPETITIVE_EXECUTABLE_CANDIDATE"
