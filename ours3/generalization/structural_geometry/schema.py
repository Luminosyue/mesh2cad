from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StructuralAnalysis:
    connected_component_count: int
    significant_component_count: int
    geometry_regime_count: int
    skeleton_branch_count: int
    profile_family_count: int
    major_hole_count: int
    void_region_count: int
    repetition_group_count: int
    attachment_count: int
    thickness_mode_count: int
    principal_axis_count: int
    source_occupancy_ratio: float
    source_surface_density: float
    bbox_fill_ratio: float
    void_fraction: float
    skeleton_to_volume_ratio: float
    local_thickness_variation: float
    structural_class: str
    sparse_open: bool
    negative_space_evidence: bool
    structural_branching: bool
    metadata: dict[str, Any] = field(default_factory=dict)

