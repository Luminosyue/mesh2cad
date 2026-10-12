"""Plan validator: schema, allowed builder, parameter refs, then builder preflight gate."""
from __future__ import annotations

from typing import Any

from design_intent.parameter_reference_resolver import resolve

FAMILY_ALIASES = [
    ("CLOSED_PROFILE", "EXTRUSION"),
    ("PROFILE_EXTRUSION", "EXTRUSION"),
    ("SUBFEATURE_EXTRUSION", "EXTRUSION"),
    ("EXTRUSION", "EXTRUSION"),
    ("EXTRUDE", "EXTRUSION"),
    ("REVOLUTION", "REVOLUTION"),
    ("REVOL", "REVOLUTION"),
    ("SWEEP", "SWEEP"),
    ("PERIODIC", "PERIODIC_BSPLINE"),
    ("SEMANTIC_FREEFORM", "GENERAL_BSPLINE"),
    ("FREEFORM", "GENERAL_BSPLINE"),
    ("SKIN", "GENERAL_BSPLINE"),
    ("GENERAL_BSPLINE", "GENERAL_BSPLINE"),
    ("BSPLINE", "GENERAL_BSPLINE"),
    ("LOFT", "LOFT"),
    ("PLANE", "PLANE"),
    ("CYLINDER", "CYLINDER"),
]


def family_of(representation: str) -> str:
    text = (representation or "").upper()
    for needle, family in FAMILY_ALIASES:
        if needle in text:
            return family
    return "UNSUPPORTED"


def validate_plan(plan: dict[str, Any], eligibility: dict[str, Any], spec: dict[str, Any] | None) -> dict[str, Any]:
    representation = str(plan.get("builder") or plan.get("representation") or "")
    family = family_of(representation)
    allowed = list(eligibility.get("ALLOWED_BUILDERS") or [])
    bank = eligibility.get("BUILDER_ELIGIBILITY") or {}
    params = resolve(plan, spec)
    reasons = []
    decision = "ACCEPT"
    if family == "UNSUPPORTED":
        reasons.append("UNKNOWN_BUILDER")
        decision = "REJECT_BUILDER_NOT_GEOMETRY_APPROVED"
    elif family not in allowed or not (bank.get(family) or {}).get("valid"):
        reasons.append("BUILDER_NOT_ALLOWED")
        decision = "REJECT_BUILDER_NOT_GEOMETRY_APPROVED"
    if params["UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT"] > 0:
        reasons.append("UNMEASURED_QWEN_GEOMETRY_PARAMETER")
        decision = "REJECT_UNMEASURED_PARAMETER"
    if params["unresolved_refs"]:
        reasons.append("MISSING_PARAMETER_REF")
        decision = "REJECT_PARAMETER_REF"
    executable = decision == "ACCEPT"
    return {
        "schema_valid": True,
        "QWEN_REQUESTED_BUILDER": family,
        "GEOMETRY_ALLOWED_BUILDERS": allowed,
        "PLAN_VALIDATION_DECISION": decision,
        "PLAN_VALIDATION_STATUS": decision,
        "PLAN_EXECUTABLE": executable,
        "reasons": reasons,
        "parameter_resolution": params,
        "UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT": params["UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT"],
        "UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT": 0,
        "representation": representation,
        "family": family,
    }
