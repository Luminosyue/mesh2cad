from __future__ import annotations

from typing import Any


BUILDER_CAPABILITIES = {
    "CURRENT_ANALYTIC": {
        "supported_outer_loops": 1,
        "supported_inner_loops": 0,
        "hole_support": False,
        "multi_profile_support": False,
        "open_wire_support": False,
        "compound_support": False,
        "repetition_support": False,
        "thin_wall_support": False,
    },
    "V6_GEOMETRY": {
        "supported_outer_loops": 0,
        "supported_inner_loops": 0,
        "hole_support": False,
        "multi_profile_support": False,
        "open_wire_support": False,
        "compound_support": False,
        "repetition_support": False,
        "thin_wall_support": False,
    },
}


def builder_capability_audit(backend: str, analysis: dict[str, Any]) -> dict[str, Any]:
    capabilities = BUILDER_CAPABILITIES.get(backend, {})
    holes = int(analysis.get("major_hole_count", 0))
    structural_class = str(analysis.get("structural_class", "UNKNOWN"))
    insufficient = bool(
        holes > 0 and not capabilities.get("hole_support", False)
        or analysis.get("structural_branching") and not capabilities.get("compound_support", False)
        or structural_class in {"ROD_NETWORK", "SPARSE_FRAME", "OPEN_FRAME", "BODY_WITH_APPENDAGES"}
        and backend == "CURRENT_ANALYTIC"
    )
    return {
        "builder_type": backend,
        "builder_capability_insufficient": insufficient,
        "analytic_builder_coverage_gap": insufficient,
        "capabilities": capabilities,
    }


def explainability(analysis: dict[str, Any], candidate_metrics: dict[str, Any], backend: str) -> dict[str, Any]:
    capability = builder_capability_audit(backend, analysis)
    geometry_fit = float(candidate_metrics.get("geometry_fit_score", 0.0))
    occupancy_pass = float(candidate_metrics.get("occupancy_iou", 0.0)) >= 0.35
    negative_pass = not bool(candidate_metrics.get("negative_space_hard_reject"))
    section_pass = float(candidate_metrics.get("section_occupancy_iou_mean", 0.0)) >= 0.30
    topology_pass = not capability["builder_capability_insufficient"]
    score = float(np_mean([
        geometry_fit,
        float(candidate_metrics.get("occupancy_iou", 0.0)),
        float(candidate_metrics.get("void_preservation_ratio", 0.0)),
        float(candidate_metrics.get("section_occupancy_iou_mean", 0.0)),
        1.0 if topology_pass else 0.0,
    ]))
    explainable = bool(
        geometry_fit >= 0.35
        and occupancy_pass
        and negative_pass
        and section_pass
        and topology_pass
        and float(candidate_metrics.get("false_positive_occupancy_ratio", 1.0)) < 0.25
    )
    return {
        "representation_explainability_score": score,
        "single_construction_explainable": explainable,
        "analytic_representation_pass": explainable,
        "analytic_occupancy_pass": occupancy_pass,
        "analytic_negative_space_pass": negative_pass,
        "analytic_section_pass": section_pass,
        "analytic_topology_pass": topology_pass,
        **capability,
    }


def np_mean(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)

