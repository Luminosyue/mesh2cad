"""Minimal typed canonical reference layer for the REVOLVE canary.

This module is intentionally independent of FeatureScript query execution. A
converter resolves source queries into stable IDs; the executor only resolves
typed canonical references and rejects missing or ambiguous symbols.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "canonical-reference-v1"


def stable_id(cad_id: str, kind: str, source_ref: str) -> str:
    """Generate a deterministic ID without depending on traversal/hash order."""
    raw = f"{cad_id}\0{kind}\0{source_ref}".encode()
    return f"{kind}_{hashlib.sha256(raw).hexdigest()[:16]}"


@dataclass(frozen=True)
class EntityRef:
    entity_id: str
    kind: str
    source_ref: str
    geometry: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProfileRef:
    profile_id: str
    sketch_ref: str
    outer_loop: tuple[str, ...]
    inner_loops: tuple[tuple[str, ...], ...] = ()
    disjoint_regions: tuple[tuple[str, ...], ...] = ()
    source_ref: str = ""


@dataclass(frozen=True)
class AxisRef:
    axis_id: str
    source_ref: str
    origin: tuple[float, float, float]
    direction: tuple[float, float, float]
    source_type: str = "entity-derived"


@dataclass(frozen=True)
class RevolveRef:
    feature_id: str
    profile_ref: str
    axis_ref: str
    angle: str | float
    dependencies: tuple[str, ...]
    body_ref: str | None = None


class ReferenceError(ValueError):
    pass


class SymbolTable:
    def __init__(self) -> None:
        self.sketches: dict[str, dict[str, Any]] = {}
        self.entities: dict[str, EntityRef] = {}
        self.profiles: dict[str, ProfileRef] = {}
        self.axes: dict[str, AxisRef] = {}
        self.features: dict[str, RevolveRef] = {}

    def _put(self, table: dict, key: str, value: Any) -> None:
        if key in table:
            raise ReferenceError(f"DUPLICATE_ID:{key}")
        table[key] = value

    def add_sketch(self, sketch_id: str, value: dict[str, Any]) -> None:
        self._put(self.sketches, sketch_id, value)

    def add_entity(self, value: EntityRef) -> None:
        self._put(self.entities, value.entity_id, value)

    def add_profile(self, value: ProfileRef) -> None:
        if value.sketch_ref not in self.sketches:
            raise ReferenceError(f"MISSING_REF:{value.sketch_ref}")
        for entity_id in value.outer_loop:
            if entity_id not in self.entities:
                raise ReferenceError(f"MISSING_REF:{entity_id}")
        self._put(self.profiles, value.profile_id, value)

    def add_axis(self, value: AxisRef) -> None:
        if value.source_ref and value.source_ref not in self.entities:
            raise ReferenceError(f"MISSING_REF:{value.source_ref}")
        self._put(self.axes, value.axis_id, value)

    def add_feature(self, value: RevolveRef) -> None:
        if value.profile_ref not in self.profiles:
            raise ReferenceError(f"MISSING_REF:{value.profile_ref}")
        if value.axis_ref not in self.axes:
            raise ReferenceError(f"MISSING_REF:{value.axis_ref}")
        for dependency in value.dependencies:
            if dependency not in self.profiles and dependency not in self.axes and dependency not in self.features:
                raise ReferenceError(f"MISSING_REF:{dependency}")
        self._put(self.features, value.feature_id, value)

    def resolve_profile(self, ref: str) -> ProfileRef:
        if ref not in self.profiles:
            raise ReferenceError(f"MISSING_REF:{ref}")
        return self.profiles[ref]

    def resolve_axis(self, ref: str) -> AxisRef:
        if ref not in self.axes:
            raise ReferenceError(f"MISSING_REF:{ref}")
        return self.axes[ref]

    def resolve_revolve(self, ref: str) -> RevolveRef:
        if ref not in self.features:
            raise ReferenceError(f"MISSING_REF:{ref}")
        return self.features[ref]


def resolve_source_query(cad_id: str, query: str, kind: str) -> dict[str, Any]:
    """Resolve a source query to a stable canonical identity.

    The original query is retained as provenance. This resolver is deliberately
    deterministic and refuses empty queries; full geometric disambiguation is a
    converter responsibility, not an executor fallback.
    """
    query = " ".join(str(query).split())
    if not query:
        raise ReferenceError(f"{kind.upper()}_QUERY_UNRESOLVED")
    return {"original_query": query, "resolved_source_entity": query, "canonical_id": stable_id(cad_id, kind, query), "resolution_reason": "stable hash of cad_id/kind/source query", "deterministic": True}


def serialize(table: SymbolTable, result: str) -> str:
    payload = {"schema_version": SCHEMA_VERSION, "sketches": table.sketches, "entities": {k: asdict(v) for k, v in table.entities.items()}, "profiles": {k: asdict(v) for k, v in table.profiles.items()}, "axes": {k: asdict(v) for k, v in table.axes.items()}, "features": {k: asdict(v) for k, v in table.features.items()}, "result": result}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def parse_and_roundtrip(text: str) -> tuple[dict[str, Any], str]:
    payload = json.loads(text)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ReferenceError("SCHEMA_VERSION_MISMATCH")
    if not isinstance(payload.get("result"), str):
        raise ReferenceError("MISSING_RESULT_REF")
    again = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return payload, again


def execute_revolve(table: SymbolTable, feature_ref: str) -> dict[str, Any]:
    feature = table.resolve_revolve(feature_ref)
    profile = table.resolve_profile(feature.profile_ref)
    axis = table.resolve_axis(feature.axis_ref)
    if not profile.outer_loop:
        raise ReferenceError("INVALID_PROFILE:empty_outer_loop")
    # The current geometry backend has no operation that consumes typed
    # profile/axis refs. Refuse execution rather than silently approximating.
    raise ReferenceError("REVOLVE_GEOMETRY_BACKEND_REQUIRES_REFERENCE_AWARE_PROFILE_WIRE")
