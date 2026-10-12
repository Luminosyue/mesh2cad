"""BuilderRegistry.execute(plan) is the only formal reconstruction entry."""
from __future__ import annotations

from typing import Any

from builders import bspline_skin_builder, extrusion_builder, loft_builder, occ_api
from design_intent.plan_validator import family_of, validate_plan


class BuilderNotApproved(RuntimeError):
    pass


def execute(plan: dict[str, Any], mesh, eligibility: dict[str, Any], spec: dict[str, Any] | None, guard_cfg: dict[str, Any], counters: dict[str, int]) -> dict[str, Any]:
    validation = validate_plan(plan, eligibility, spec)
    family = validation["family"]
    if family in ("LOFT", "SWEEP"):
        counters["LOFT_INVALID_REQUEST"] = counters.get("LOFT_INVALID_REQUEST", 0) + int(not validation["PLAN_EXECUTABLE"] and family == "LOFT")
    if family in ("GENERAL_BSPLINE", "PERIODIC_BSPLINE"):
        counters["BSPLINE_INVALID_REQUEST"] = counters.get("BSPLINE_INVALID_REQUEST", 0) + int(not validation["PLAN_EXECUTABLE"])
    counters["UNMEASURED_PROPOSED"] = counters.get("UNMEASURED_PROPOSED", 0) + int(validation.get("UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT") or 0)
    counters["UNMEASURED_CONSUMED"] = counters.get("UNMEASURED_CONSUMED", 0) + int(validation.get("UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT") or 0)
    if not validation["PLAN_EXECUTABLE"]:
        counters["INVALID_BUILDER_REQUEST"] = counters.get("INVALID_BUILDER_REQUEST", 0) + 1
        return {
            "executed": False,
            "blocked": True,
            "PLAN_EXECUTABLE": False,
            "validation": validation,
            "shape": None,
            "family": family,
            "CANDIDATE_SOURCE": plan.get("CANDIDATE_SOURCE") or "QWEN_PLAN",
        }
    part_bbox = eligibility["part_bbox"]
    extracted = eligibility.get("extracted_profiles")
    with occ_api.registry_authorized():
        if family == "LOFT":
            result = loft_builder.execute(mesh, plan, part_bbox, guard_cfg, counters, extracted=extracted)
        elif family in ("GENERAL_BSPLINE", "PERIODIC_BSPLINE", "SWEEP"):
            result = bspline_skin_builder.execute(mesh, plan, part_bbox, guard_cfg, counters, extracted=extracted)
        elif family in ("EXTRUSION", "REVOLUTION", "PLANE", "CYLINDER"):
            result = extrusion_builder.execute(mesh, plan, part_bbox, guard_cfg, counters, spec=spec)
        else:
            counters["INVALID_BUILDER_REQUEST"] = counters.get("INVALID_BUILDER_REQUEST", 0) + 1
            return {"executed": False, "blocked": True, "PLAN_EXECUTABLE": False, "validation": validation, "shape": None, "family": family}
    result["validation"] = validation
    result["PLAN_EXECUTABLE"] = True
    result["CANDIDATE_SOURCE"] = plan.get("CANDIDATE_SOURCE") or "QWEN_PLAN"
    result["family"] = family
    return result
