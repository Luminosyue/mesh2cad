"""Structured plan validator: schema → eligibility → references. Never executes builders."""
from __future__ import annotations

from typing import Any

from design_plan.resolver import resolve_plan
from design_plan.schema import (
    ALLOWED_PLAN_KEYS,
    BUILDER_REQUIRED_REFS,
    HYPERPARAM_KEYS,
    PLAN_VERSION,
    REQUIRED_PLAN_KEYS,
    VALIDATOR_VERSION,
    is_ref,
    walk_naked_numbers,
)


def validate_plan(plan: dict[str, Any], eligibility: dict[str, Any], catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    reasons = []
    status = "PLAN_GENERATED"
    schema_valid = True
    if not isinstance(plan, dict):
        return _fail("PLAN_SCHEMA_REJECTED", ["NOT_AN_OBJECT"], plan, eligibility)
    unknown = sorted(set(plan) - ALLOWED_PLAN_KEYS)
    missing = sorted(REQUIRED_PLAN_KEYS - set(plan))
    if unknown:
        reasons.append("UNKNOWN_FIELDS:" + ",".join(unknown))
        schema_valid = False
    if missing:
        reasons.append("MISSING_FIELDS:" + ",".join(missing))
        schema_valid = False
    if str(plan.get("plan_version") or "") != PLAN_VERSION:
        reasons.append("BAD_PLAN_VERSION")
        schema_valid = False
    builder = str(plan.get("builder") or "")
    family = str(plan.get("construction_family") or "")
    if builder not in BUILDER_REQUIRED_REFS:
        reasons.append("UNKNOWN_BUILDER")
        schema_valid = False
    if family and family != builder:
        reasons.append("FAMILY_BUILDER_MISMATCH")
        schema_valid = False
    if not is_ref(str(plan.get("builder_eligibility_ref") or "")):
        reasons.append("BAD_ELIGIBILITY_REF")
        schema_valid = False
    geom = plan.get("geometry_refs")
    if not isinstance(geom, dict):
        reasons.append("GEOMETRY_REFS_NOT_OBJECT")
        schema_valid = False
        geom = {}
    for key, val in geom.items():
        if not (str(key).endswith("_ref") or str(key).endswith("_refs")):
            reasons.append(f"NON_REF_GEOMETRY_KEY:{key}")
            schema_valid = False
        if str(key).endswith("_refs"):
            if not isinstance(val, list) or not all(isinstance(x, str) and is_ref(x) for x in val):
                reasons.append(f"BAD_REF_LIST:{key}")
                schema_valid = False
        elif not (isinstance(val, str) and is_ref(val)):
            reasons.append(f"BAD_REF:{key}")
            schema_valid = False
    required = BUILDER_REQUIRED_REFS.get(builder) or []
    for key in required:
        if key not in geom and key not in (plan.get("topology_refs") or {}) and key not in (plan.get("feature_refs") or {}):
            reasons.append(f"MISSING_REQUIRED_REF:{key}")
            schema_valid = False
    options = plan.get("execution_options") or {}
    if options and not isinstance(options, dict):
        reasons.append("BAD_EXECUTION_OPTIONS")
        schema_valid = False
    elif isinstance(options, dict):
        for key in options:
            if key not in HYPERPARAM_KEYS:
                reasons.append(f"NON_HYPERPARAM_OPTION:{key}")
                schema_valid = False
    naked = walk_naked_numbers(plan)
    if naked:
        reasons.append("NAKED_GEOMETRY_NUMBER")
        schema_valid = False
    if not schema_valid:
        return _result("PLAN_SCHEMA_REJECTED", False, False, False, False, reasons, plan, eligibility, naked=naked)

    if builder == "OPEN_SHELL":
        return _result("OPEN_SHELL_PLAN_NOT_YET_EXECUTABLE", True, False, False, False, ["OPEN_SHELL_PLAN_UNSUPPORTED"], plan, eligibility)

    allowed = list(eligibility.get("ALLOWED_BUILDERS") or [])
    bank = eligibility.get("BUILDER_ELIGIBILITY") or {}
    if builder not in allowed or not (bank.get(builder) or {}).get("valid"):
        return _result("PLAN_GEOMETRY_REJECTED", True, False, False, False, ["BUILDER_NOT_GEOMETRY_APPROVED"], plan, eligibility)

    if catalog is None:
        return _result("PLAN_REFERENCE_REJECTED", True, True, False, False, ["CATALOG_REQUIRED"], plan, eligibility)

    resolved = resolve_plan(plan, catalog)
    if resolved["REFERENCE_NOT_FOUND"]:
        return _result("PLAN_REFERENCE_REJECTED", True, True, False, False, ["REFERENCE_NOT_FOUND"], plan, eligibility, resolved=resolved)
    if resolved["REFERENCE_TYPE_MISMATCH"]:
        return _result("PLAN_REFERENCE_REJECTED", True, True, False, False, ["REFERENCE_TYPE_MISMATCH"], plan, eligibility, resolved=resolved)
    if resolved["REFERENCE_FRAME_MISMATCH"]:
        return _result("PLAN_REFERENCE_REJECTED", True, True, False, False, ["REFERENCE_FRAME_MISMATCH"], plan, eligibility, resolved=resolved)
    if not resolved["REF_RESOLVE_SUCCESS"]:
        return _result("PLAN_REFERENCE_REJECTED", True, True, False, False, ["REF_RESOLVE_FAILED"], plan, eligibility, resolved=resolved)
    return _result("PLAN_EXECUTABLE", True, True, True, True, [], plan, eligibility, resolved=resolved)


def _fail(status, reasons, plan, eligibility):
    return _result(status, False, False, False, False, reasons, plan, eligibility)


def _result(status, schema_ok, geom_ok, ref_ok, executable, reasons, plan, eligibility, resolved=None, naked=None):
    return {
        "PLAN_STATUS": status,
        "PLAN_SCHEMA_VALID": schema_ok,
        "PLAN_GEOMETRY_VALID": geom_ok,
        "PLAN_REFERENCE_VALID": ref_ok,
        "PLAN_EXECUTABLE": executable,
        "PLAN_REJECT_REASON": reasons[0] if reasons else None,
        "reasons": reasons,
        "builder": plan.get("builder") if isinstance(plan, dict) else None,
        "GEOMETRY_ALLOWED_BUILDERS": list(eligibility.get("ALLOWED_BUILDERS") or []),
        "VALIDATOR_VERSION": VALIDATOR_VERSION,
        "resolved": resolved,
        "naked_numbers": naked or [],
        "QWEN_CAN_OVERRIDE_INVALID_GEOMETRY": False,
    }
