"""Configurable part-level profile representation router; no part identifiers."""

DEFAULT_CONFIG = {
    "closed_profile_rate_threshold": 0.75,
    "open_shell_rate_threshold": 0.50,
}


def route_profile_types(profile_types, config=None):
    config = {**DEFAULT_CONFIG, **(config or {})}
    total = len(profile_types)
    if total == 0:
        return {"decision": "UNSUPPORTED", "reason": "NO_STATION_PROFILES"}
    closed = sum(value in {"CLOSED_SOLID_PROFILE", "CLOSED_MULTI_LOOP_PROFILE"} for value in profile_types)
    opened = sum(value == "OPEN_SHELL_PROFILE" for value in profile_types)
    invalid = sum(value == "INVALID_PROFILE" for value in profile_types)
    rates = {
        "closed_profile_rate": closed / total,
        "open_shell_profile_rate": opened / total,
        "invalid_profile_rate": invalid / total,
    }
    if rates["closed_profile_rate"] >= config["closed_profile_rate_threshold"]:
        decision, reason = "CLOSED_PROFILE_BRANCH", "CLOSED_RATE_AT_OR_ABOVE_THRESHOLD"
    elif rates["open_shell_profile_rate"] >= config["open_shell_rate_threshold"]:
        decision, reason = "OPEN_SHELL_BRANCH", "OPEN_SHELL_RATE_AT_OR_ABOVE_THRESHOLD"
    elif closed + opened > 0:
        decision, reason = "MIXED_BRANCH", "NO_DOMINANT_PROFILE_TYPE"
    else:
        decision, reason = "UNSUPPORTED", "ONLY_INVALID_PROFILES"
    return {"decision": decision, "reason": reason, **rates, "profile_count": total, "config": config}
