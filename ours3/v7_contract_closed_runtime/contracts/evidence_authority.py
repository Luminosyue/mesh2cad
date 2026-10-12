"""Single source of truth for the V7 geometry execution contract."""
AUTHORITIES = {
    "SOURCE_AUDIT": {"source_sha", "original_bbox", "triangle_count", "source_transform", "watertight_status"},
    "P3": {"triangle_membership", "support_triangle_ids"},
    "GEOMETRY_ANALYZER": {"part_bbox", "part_dimensions", "principal_axis", "construction_axis", "stations", "closed_profiles", "profile_planes", "span", "cross_sections"},
    "DESIGN_INTENT_MAC": {"representation_family", "builder_choice", "allowed_construction_parameters", "program_structure"},
    "RUNTIME": {"execution", "brep_creation", "occ_operations"},
}

RUNTIME_FORBIDDEN_INFERENCES = {
    "axis_from_mesh_extents", "station_regeneration", "representation_remapping",
    "profile_count_clamp", "case_specific_override", "historical_step_reuse",
}

BUILDER_CONTRACT = {
    "EXTRUSION": "ExtrusionBuilder",
    "REVOLUTION": "RevolutionBuilder",
    "LOFT": "LoftBuilder",
    "RULED": "RuledBuilder",
    "BSPLINE_SKIN": "BSplineSkinBuilder",
}

def validate_requested_parameters(plan, spec):
    requested = int(plan["profile_count"])
    available = len(spec["profiles"])
    if requested < 2 or requested > available:
        raise ValueError(f"CONTRACT_VIOLATION requested_profile_count={requested} available={available}")
    if plan["hypothesis"] not in BUILDER_CONTRACT:
        raise ValueError(f"CONTRACT_VIOLATION unknown hypothesis {plan['hypothesis']}")
    return requested
