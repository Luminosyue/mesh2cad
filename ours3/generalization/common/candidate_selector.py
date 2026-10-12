from __future__ import annotations

from typing import Any


def select_candidate(candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    eligible = [item for item in candidates if item.get("safety_pass") and not item.get("hard_reject")]
    if not eligible:
        return None, [
            {"candidate_id": item.get("candidate_id"), "reason": item.get("reject_reason", "NO_SAFE_CANDIDATE")}
            for item in candidates
        ]
    best_chamfer = min(float(item.get("metrics", {}).get("chamfer", 1e30)) for item in eligible)
    tolerance = max(best_chamfer * 1.05, best_chamfer + 1e-9)
    near = [item for item in eligible if float(item.get("metrics", {}).get("chamfer", 1e30)) <= tolerance]
    winner = max(
        near,
        key=lambda item: (
            float(item.get("metrics", {}).get("analytic_surface_ratio", 0.0)),
            float(item.get("metrics", {}).get("nativeness_score", 0.0)),
            -float(item.get("metrics", {}).get("chamfer", 1e30)),
            -float(item.get("metrics", {}).get("face_count", 1e30)),
        ),
    )
    rejected = []
    for item in candidates:
        if item is winner:
            continue
        rejected.append({
            "candidate_id": item.get("candidate_id"),
            "reason": item.get("reject_reason") if item.get("hard_reject") else "LOWER_FIDELITY_OR_NATIVE_ORDER",
        })
    return winner, rejected

