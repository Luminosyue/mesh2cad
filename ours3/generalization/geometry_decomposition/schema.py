from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RefinedPart:
    refined_part_id: str
    parent_coarse_part_id: str
    source_p3_segment_ids: list[int]
    triangle_ids: list[int]
    geometry_regime: str
    geometry_confidence: float
    connected_component_id: int
    repetition_group_id: str | None
    bbox: list[list[float]]
    centroid: list[float]
    backend_eligibility: dict[str, bool]
    provenance: dict[str, Any] = field(default_factory=dict)


ANALYTIC_REGIMES = {
    "PLANAR_PATCH",
    "THIN_PLATE",
    "LINEAR_ROD",
    "CYLINDRICAL_ROD",
    "PROFILE_EXTRUSION",
    "BOX_PRISM",
    "REVOLUTIONAL",
}

