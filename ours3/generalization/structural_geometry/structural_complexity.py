from __future__ import annotations

import trimesh

from .negative_space_analyzer import negative_space_evidence
from .occupancy_analyzer import occupancy_metrics
from .repetition_detector_v2 import detect_repetition_v2
from .skeletal_structure_detector import detect_skeletal_structure
from .topology_complexity import topology_complexity


def analyze(mesh: trimesh.Trimesh) -> dict:
    occupancy = occupancy_metrics(mesh, mesh)
    topology = topology_complexity(mesh)
    negative = negative_space_evidence(occupancy)
    skeletal = detect_skeletal_structure(mesh, occupancy, topology)
    repetition = detect_repetition_v2(mesh)
    components = mesh.split(only_watertight=False)
    significant = [item for item in components if len(item.faces) >= max(8, len(mesh.faces) * 0.005)]
    geometry_regimes = len(significant) if len(significant) > 1 else 1
    attachment_count = max(0, len(significant) - 1) if skeletal["structural_class"] == "BODY_WITH_APPENDAGES" else 0
    return {
        **occupancy,
        **topology,
        **negative,
        **skeletal,
        "geometry_regime_count": geometry_regimes,
        "profile_family_count": geometry_regimes,
        "repetition_group_count": repetition["repetition_group_count"],
        "repetition_member_count": repetition["repetition_member_count"],
        "repetition_confidence": repetition["confidence"],
        "attachment_count": attachment_count,
        "thickness_mode_count": 1,
        "local_thickness_variation": 0.0,
    }
