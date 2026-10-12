from __future__ import annotations

import math
from typing import Any


BUILDER_ORDER = {
    "PLANAR_FACE": 0,
    "PROFILE_EXTRUSION": 0,
    "TAPERED_EXTRUSION": 1,
    "REVOLUTION": 2,
    "BOOLEAN_CUT": 3,
    "BOOLEAN_UNION": 4,
    "BOX_PRISM": 5,
    "V6_GEOMETRY": 6,
}


def candidate_score(metrics: dict[str, Any]) -> float:
    return float(
        0.30 * metrics.get("chamfer", math.inf)
        + 0.20 * metrics.get("hausdorff", math.inf)
        + 0.25 * metrics.get("false_positive_occupancy", 1.0)
        + 0.15 * (1.0 - metrics.get("coverage", 0.0))
        + 0.10 * metrics.get("normal_error", 1.0)
    )


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for candidate in candidates:
        item = dict(candidate)
        item["score"] = candidate_score(item.get("metrics", {})) if item.get("qa_pass") else math.inf
        ranked.append(item)
    ranked.sort(key=lambda row: (
        row["score"],
        BUILDER_ORDER.get(row.get("builder_family", "UNKNOWN"), 99),
        row.get("candidate_id", ""),
    ))
    for index, row in enumerate(ranked):
        row["rank"] = index + 1
        row["selected"] = bool(index == 0 and row.get("qa_pass"))
        if not row["selected"] and row.get("qa_pass"):
            row["primary_reject_reason"] = "RANKING_REJECT"
            row["secondary_reject_reason"] = f"winner_score={ranked[0]['score']}"
    return ranked
