"""Evidence-based station profile classification for V7B."""

VALID_TYPES = {
    "CLOSED_SOLID_PROFILE",
    "CLOSED_MULTI_LOOP_PROFILE",
    "OPEN_SHELL_PROFILE",
    "INVALID_PROFILE",
}


def classify_profile(record, source_part_watertight=None):
    cycles = int(record.get("closed_path_count", 0))
    components = int(record.get("raw_path_count", 0))
    endpoints = int(record.get("open_endpoint_count", 0))
    junctions = int(record.get("junction_count", 0))
    histogram = record.get("node_degree_histogram", {})
    open_count = int(record.get("open_path_count", 0))
    reasons = []
    has_valid_cycle = cycles >= 1 and bool(record.get("outer_loop"))
    if has_valid_cycle:
        profile_type = "CLOSED_MULTI_LOOP_PROFILE" if cycles > 1 else "CLOSED_SOLID_PROFILE"
        reasons += ["VALID_CLOSED_CYCLE", "OUTER_LOOP_PRESENT"]
        if open_count:
            reasons.append("RESIDUAL_OPEN_COMPONENTS_EXCLUDED_FROM_OUTER_PROFILE")
        if junctions:
            reasons.append("RESIDUAL_GRAPH_JUNCTIONS_EXCLUDED_FROM_OUTER_PROFILE")
    elif junctions or any(int(key) > 2 and int(value) > 0 for key, value in histogram.items()):
        profile_type = "INVALID_PROFILE"
        reasons.append("GRAPH_HAS_JUNCTION")
    elif cycles == 0 and open_count > 0 and endpoints >= 2:
        profile_type = "OPEN_SHELL_PROFILE"
        reasons += ["NO_CLOSED_CYCLE", "ORDERABLE_OPEN_COMPONENTS"]
        reasons.append("TWO_OPEN_ENDPOINTS" if endpoints == 2 else "MULTIPLE_OPEN_ENDPOINT_PAIRS")
    else:
        profile_type = "INVALID_PROFILE"
        reasons.append("INSUFFICIENT_OR_AMBIGUOUS_GRAPH_EVIDENCE")
    if components > 1:
        reasons.append("MULTIPLE_GRAPH_COMPONENTS")
    if source_part_watertight is False:
        reasons.append("SOURCE_PART_NON_WATERTIGHT")
    result = {
        "station_id": record.get("station_id"),
        "profile_type": profile_type,
        "classification_reason": reasons,
        "raw_segment_graph": {
            "component_count": components,
            "degree_histogram": histogram,
            "open_endpoint_count": endpoints,
            "closed_loop_count": cycles,
            "open_chain_count": open_count,
            "junction_count": junctions,
        },
        "station_continuity_evaluated": True,
    }
    assert result["profile_type"] in VALID_TYPES
    return result
