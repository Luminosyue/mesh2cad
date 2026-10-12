from __future__ import annotations


def route(analysis: dict, explainability: dict) -> dict:
    structural = analysis.get("structural_class", "UNKNOWN")
    if (
        explainability.get("single_construction_explainable")
        and not explainability.get("builder_capability_insufficient")
        and not analysis.get("negative_space_hard_reject")
    ):
        return {"route": "CURRENT_ANALYTIC", "reason": "SINGLE_CONSTRUCTION_EXPLAINABLE", "v6_eligible": False}
    if structural in {"SPARSE_FRAME", "OPEN_FRAME", "ROD_NETWORK", "BODY_WITH_APPENDAGES"}:
        return {"route": "RECURSIVE_DECOMPOSITION", "reason": "STRUCTURAL_COMPLEXITY", "v6_eligible": False}
    coherent_freeform = bool(
        structural in {"SOLID_LIKE", "SURFACE_LIKE"}
        and int(analysis.get("significant_component_count", 1)) <= 1
        and not analysis.get("structural_branching")
        and int(analysis.get("major_hole_count", 0)) == 0
        and not analysis.get("negative_space_hard_reject")
    )
    if coherent_freeform:
        return {"route": "V6_GEOMETRY", "reason": "COHERENT_FREEFORM", "v6_eligible": True}
    return {"route": "OMIT", "reason": "INSUFFICIENT_EXPLAINABILITY", "v6_eligible": False}
