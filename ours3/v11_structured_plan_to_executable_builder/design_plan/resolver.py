"""Resolve plan references against the authoritative catalog. No auto-correction."""
from __future__ import annotations

from typing import Any

from design_plan.schema import BUILDER_REQUIRED_REFS, EXPECTED_FRAME, REF_EXPECTED_TYPE, is_ref


class ResolveError(RuntimeError):
    def __init__(self, code: str, payload: dict[str, Any]):
        super().__init__(code)
        self.code = code
        self.payload = payload


def _collect_refs(plan: dict[str, Any]) -> dict[str, Any]:
    refs = {}
    for bucket in ("geometry_refs", "topology_refs", "feature_refs"):
        block = plan.get(bucket) or {}
        if not isinstance(block, dict):
            continue
        refs.update(block)
    return refs


def resolve_plan(plan: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    entries = catalog["entries"]
    builder = str(plan.get("builder") or "")
    required = BUILDER_REQUIRED_REFS.get(builder) or []
    raw_refs = _collect_refs(plan)
    resolved = {}
    provenance = []
    not_found = []
    type_mismatch = []
    frame_mismatch = []
    for key in required:
        value = raw_refs.get(key)
        expected = REF_EXPECTED_TYPE.get(key)
        if value is None:
            not_found.append({"key": key, "ref": None})
            continue
        if key.endswith("_refs"):
            if not isinstance(value, list) or not value:
                type_mismatch.append({"key": key, "ref": value, "expected": expected, "got": type(value).__name__})
                continue
            items = []
            for ref in value:
                if not is_ref(ref) or ref not in entries:
                    not_found.append({"key": key, "ref": ref})
                    continue
                entry = entries[ref]
                item_type = expected.replace("_list", "") if expected else entry["type"]
                if entry["type"] != item_type and not (item_type == "scalar" and entry["type"] == "scalar"):
                    type_mismatch.append({"key": key, "ref": ref, "expected": item_type, "got": entry["type"]})
                    continue
                if entry.get("coordinate_frame") != EXPECTED_FRAME:
                    frame_mismatch.append({"key": key, "ref": ref, "got": entry.get("coordinate_frame")})
                    continue
                items.append(entry)
            if items and len(items) == len(value) and not any(x["key"] == key for x in not_found + type_mismatch):
                resolved[key] = {
                    "ref": value,
                    "type": expected,
                    "value": [e["value"] for e in items],
                    "coordinate_frame": EXPECTED_FRAME,
                    "entries": items,
                }
                for entry in items:
                    provenance.append(_prov(key, entry))
            continue
        if not is_ref(value):
            type_mismatch.append({"key": key, "ref": value, "expected": "reference_string", "got": type(value).__name__})
            continue
        if value not in entries:
            not_found.append({"key": key, "ref": value})
            continue
        entry = entries[value]
        if expected and entry["type"] != expected:
            type_mismatch.append({"key": key, "ref": value, "expected": expected, "got": entry["type"]})
            continue
        if entry.get("coordinate_frame") != EXPECTED_FRAME:
            frame_mismatch.append({"key": key, "ref": value, "got": entry.get("coordinate_frame")})
            continue
        resolved[key] = {
            "ref": value,
            "type": entry["type"],
            "value": entry["value"],
            "coordinate_frame": entry["coordinate_frame"],
            "entry": entry,
        }
        provenance.append(_prov(key, entry))
    eligibility_ref = plan.get("builder_eligibility_ref")
    if eligibility_ref:
        if eligibility_ref not in entries:
            not_found.append({"key": "builder_eligibility_ref", "ref": eligibility_ref})
        else:
            resolved["builder_eligibility_ref"] = entries[eligibility_ref]
    ok = not (not_found or type_mismatch or frame_mismatch)
    return {
        "REF_RESOLVE_SUCCESS": ok,
        "REF_TYPE_VALID": not type_mismatch,
        "REF_PROVENANCE_VALID": ok,
        "RESOLVED_FRAME": EXPECTED_FRAME,
        "EXPECTED_FRAME": EXPECTED_FRAME,
        "resolved": resolved,
        "provenance": provenance,
        "REFERENCE_NOT_FOUND": not_found,
        "REFERENCE_TYPE_MISMATCH": type_mismatch,
        "REFERENCE_FRAME_MISMATCH": frame_mismatch,
        "builder": builder,
        "plan": plan,
    }


def _prov(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "PARAMETER_NAME": name,
        "VALUE": entry.get("value"),
        "SOURCE_REF": entry.get("ref"),
        "SOURCE_FILE": entry.get("source_file"),
        "SOURCE_HASH": entry.get("source_hash"),
        "COORDINATE_FRAME": entry.get("coordinate_frame"),
        "AUTHORITY": entry.get("authority") or "MEASURED_SPEC",
        "TYPE": entry.get("type"),
    }
