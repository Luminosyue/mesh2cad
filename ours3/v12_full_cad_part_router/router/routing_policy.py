SAFETY_REJECTS = {
    "SCHEMA_INVALID",
    "REFERENCE_INVALID",
    "BUILDER_NOT_ELIGIBLE",
    "EXPLOSION",
    "OCC_INVALID",
    "EXECUTION_FAILED",
}


def tts_key(candidate):
    """Safety -> fidelity -> nativeness -> complexity, never score through a hard reject."""
    safe = bool(candidate.get("safety_pass")) and not candidate.get("hard_reject")
    return (
        int(safe),
        float(candidate.get("fidelity_score", 0.0)),
        float(candidate.get("nativeness_score", 0.0)),
        -float(candidate.get("complexity_score", 1.0)),
    )


def select_candidate(candidates):
    eligible = [c for c in candidates if not c.get("hard_reject") and c.get("safety_pass")]
    if not eligible:
        return None, [{"candidate_id": c.get("candidate_id"), "reason": c.get("reject_reason", "HARD_REJECT")} for c in candidates]
    winner = max(eligible, key=tts_key)
    rejected = []
    for c in candidates:
        if c is winner:
            continue
        reason = c.get("reject_reason") if c.get("hard_reject") else "LOWER_TTS_ORDER"
        rejected.append({"candidate_id": c.get("candidate_id"), "reason": reason})
    return winner, rejected
