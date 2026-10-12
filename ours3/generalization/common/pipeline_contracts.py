from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PartRecord:
    part_id: str
    triangle_ids: list[int]
    semantic_role: str
    role_family: str
    mesh_path: Path
    geometry_class: str = "UNKNOWN"
    frame: dict[str, Any] = field(default_factory=dict)
    geometry: dict[str, Any] = field(default_factory=dict)
    adjacency: list[str] = field(default_factory=list)
    parent_part_id: str | None = None
    semantic_confidence: float | None = None
    semantic_geometry_conflict: bool = False


@dataclass
class CandidateRecord:
    candidate_id: str
    part_id: str
    backend: str
    step_path: Path | None
    metrics: dict[str, Any]
    safety_pass: bool
    hard_reject: bool
    reject_reason: str | None = None
    selection_score: tuple[float, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

