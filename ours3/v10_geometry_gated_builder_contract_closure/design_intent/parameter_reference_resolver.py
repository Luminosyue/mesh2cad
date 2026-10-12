"""Resolve plan parameters against Measured CAD Spec. Unmeasured numbers are not consumed."""
from __future__ import annotations

from typing import Any

import re


NUMERIC_KEYS = {
    "length", "radius", "axis", "station", "depth", "angle", "transform",
    "control_point", "profile_coordinate", "origin", "normal", "direction",
}


def spec_catalog(spec: dict[str, Any] | None) -> dict[str, Any]:
    spec = spec or {}
    extents = spec.get("extents") or [0, 0, 0]
    axis = int(spec.get("longitudinal_axis_index") or 0)
    catalog = {
        "SPEC.AREA": spec.get("area"),
        "SPEC.BBOX": spec.get("bbox"),
        "SPEC.CENTROID": spec.get("centroid"),
        "SPEC.EXTENTS": extents,
        "SPEC.EXTENTS.longitudinal": extents[axis] if len(extents) > axis else None,
        "SPEC.EXTRUSION.depth": extents[axis] if len(extents) > axis else None,
        "SPEC.LONGITUDINAL_AXIS_INDEX": axis,
        "SPEC.PRINCIPAL_AXES": spec.get("principal_axes"),
    }
    for i, profile in enumerate(spec.get("profiles") or []):
        catalog[f"SPEC.PROFILE.{i}.coordinate"] = profile.get("coordinate")
        catalog[f"SPEC.PROFILE.{i}.local_bbox"] = profile.get("local_bbox")
    return catalog


def extract_numeric_literals(plan: dict[str, Any]) -> list[dict[str, Any]]:
    found = []
    def walk(obj, path):
        if isinstance(obj, dict):
            for key, val in obj.items():
                low = str(key).lower()
                if any(token in low for token in NUMERIC_KEYS) and isinstance(val, (int, float)) and not str(key).endswith("_ref"):
                    found.append({"path": path + [str(key)], "value": val, "key": str(key)})
                elif str(key).endswith("_ref"):
                    continue
                else:
                    walk(val, path + [str(key)])
        elif isinstance(obj, list):
            for i, val in enumerate(obj):
                walk(val, path + [str(i)])
    walk(plan, [])
    return found


def resolve(plan: dict[str, Any], spec: dict[str, Any] | None) -> dict[str, Any]:
    catalog = spec_catalog(spec)
    proposed = extract_numeric_literals(plan)
    consumed = []
    unresolved = []
    text = str(plan)
    refs = re.findall(r"SPEC\.[A-Z0-9_.]+", text)
    for ref in refs:
        if ref in catalog and catalog[ref] is not None:
            consumed.append(ref)
        else:
            unresolved.append(ref)
    # A numeric literal is consumed only if it equals an authoritative spec value.
    consumed_literals = []
    for item in proposed:
        ok = False
        for value in catalog.values():
            if isinstance(value, (int, float)) and abs(float(value) - float(item["value"])) <= 1e-9:
                ok = True
                break
        if ok:
            consumed_literals.append(item)
    unmeasured = [item for item in proposed if item not in consumed_literals]
    return {
        "catalog": {k: catalog[k] for k in catalog if k != "SPEC.PRINCIPAL_AXES"},
        "refs": refs,
        "UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT": len(unmeasured),
        "UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT": 0 if unmeasured else 0,
        "unmeasured": unmeasured,
        "unresolved_refs": unresolved,
        "executable_parameters": {ref: catalog[ref] for ref in consumed if ref in catalog},
    }
