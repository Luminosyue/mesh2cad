from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any


ALLOWED_FAMILIES = {
    "PLANE",
    "EXTRUSION",
    "CYLINDER",
    "REVOLUTION",
    "LOFT",
    "SWEEP",
    "GENERAL_BSPLINE",
    "PERIODIC_BSPLINE",
    "OPEN_SHELL",
}


@dataclass
class Mesh2CADIntermediatePlan:
    candidate_id: str
    construction_family: str
    operation_sequence: list[str]
    topology_hypothesis: dict[str, Any]
    profile_hypothesis: dict[str, Any]
    axis_hypothesis: dict[str, Any]
    boolean_relations: list[dict[str, Any]]
    raw_numeric_parameters: list[dict[str, Any]]
    raw_cadquery_program: str
    rationale: str
    parser_status: str = "PARSE_VALID"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json_object(text: str) -> dict[str, Any]:
    block = re.search(r"```(?:json)?\s*(.*?)```", text, re.S | re.I)
    raw = block.group(1) if block else text
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("MESH2CAD_RESPONSE_HAS_NO_JSON")
    value = json.loads(raw[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("MESH2CAD_RESPONSE_NOT_OBJECT")
    return value


def _raw_numbers(value: Any, path: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, bool):
        return rows
    if isinstance(value, (int, float)):
        rows.append({"path": ".".join(path), "value": value})
    elif isinstance(value, dict):
        for key, item in value.items():
            if key not in {"confidence", "candidate_index"}:
                rows.extend(_raw_numbers(item, path + (str(key),)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_raw_numbers(item, path + (str(index),)))
    return rows


def parse_response(text: str, expected_count: int = 4) -> list[Mesh2CADIntermediatePlan]:
    payload = _json_object(text)
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("MESH2CAD_CANDIDATES_MISSING")
    parsed: list[Mesh2CADIntermediatePlan] = []
    seen: set[str] = set()
    for index, item in enumerate(candidates[:expected_count]):
        if not isinstance(item, dict):
            continue
        family = str(item.get("construction_family") or item.get("builder") or "").upper()
        if family not in ALLOWED_FAMILIES or family in seen:
            continue
        seen.add(family)
        raw_program = str(item.get("raw_cadquery_program") or "")
        parsed.append(
            Mesh2CADIntermediatePlan(
                candidate_id=str(item.get("candidate_id") or f"MESH2CAD_{index + 1:02d}"),
                construction_family=family,
                operation_sequence=[str(value) for value in item.get("operation_sequence") or [family]],
                topology_hypothesis=dict(item.get("topology_hypothesis") or {}),
                profile_hypothesis=dict(item.get("profile_hypothesis") or {}),
                axis_hypothesis=dict(item.get("axis_hypothesis") or {}),
                boolean_relations=list(item.get("boolean_relations") or []),
                raw_numeric_parameters=_raw_numbers(item),
                raw_cadquery_program=raw_program,
                rationale=str(item.get("rationale") or ""),
            )
        )
    if not parsed:
        raise ValueError("MESH2CAD_NO_VALID_UNIQUE_FAMILY")
    return parsed

