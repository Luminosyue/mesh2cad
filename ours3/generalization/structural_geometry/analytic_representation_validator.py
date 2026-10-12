from __future__ import annotations


def validate_representation(analysis: dict, explainability: dict) -> dict:
    over_simplification = bool(
        analysis.get("negative_space_evidence")
        and (
            explainability.get("false_positive_occupancy_ratio", 0.0) > 0.25
            or not explainability.get("analytic_negative_space_pass", False)
        )
    )
    return {
        "analytic_over_simplification": over_simplification,
        "representation_validator_pass": not over_simplification,
    }
