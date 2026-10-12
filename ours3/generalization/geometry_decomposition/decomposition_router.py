from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import trimesh

from .connected_component_splitter import split_connected_components
from .geometry_regime_segmenter import detect_regime
from .repetition_detector import detect_repetition
from .schema import ANALYTIC_REGIMES, RefinedPart


def _hash_ids(ids: list[int]) -> str:
    arr = np.asarray(sorted(ids), dtype=np.int64)
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


def _part_id(parent_id: str, regime: str, triangle_ids: list[int]) -> str:
    return f"{parent_id}_{regime}_{_hash_ids(triangle_ids)[:10]}"


def decompose_coarse_part(
    parent_id: str,
    mesh: trimesh.Trimesh,
    source_p3_segment_ids: list[int],
    global_triangle_ids: list[int],
) -> dict[str, Any]:
    components = split_connected_components(mesh)
    repetition_groups = detect_repetition(components)
    group_by_component = {}
    for group in repetition_groups:
        for comp_id in group["member_component_ids"]:
            group_by_component[comp_id] = group["group_id"]

    significant = [item for item in components if not item.tiny]
    if not significant:
        significant = components[:1]
    refined: list[RefinedPart] = []
    detections = []
    for component in significant:
        local_faces = component.face_indices
        submesh = mesh.submesh([local_faces], append=True, repair=False)
        triangle_ids = [int(global_triangle_ids[index]) for index in local_faces]
        evidence = detect_regime(submesh)
        regime = evidence["geometry_regime"]
        backend_eligibility = {
            "current_analytic": regime in ANALYTIC_REGIMES,
            "v6": regime in {"LOFTABLE_FREEFORM", "GENERAL_FREEFORM"},
            "mixed_direct_v6": False,
        }
        refined.append(RefinedPart(
            refined_part_id=_part_id(parent_id, regime, triangle_ids),
            parent_coarse_part_id=parent_id,
            source_p3_segment_ids=source_p3_segment_ids,
            triangle_ids=sorted(triangle_ids),
            geometry_regime=regime,
            geometry_confidence=float(evidence["geometry_confidence"]),
            connected_component_id=component.component_id,
            repetition_group_id=group_by_component.get(component.component_id),
            bbox=component.bbox,
            centroid=component.centroid,
            backend_eligibility=backend_eligibility,
            provenance={
                "triangle_ids_hash": _hash_ids(triangle_ids),
                "component_area_ratio": component.area_ratio,
                "component_bbox_diag_ratio": component.bbox_diag_ratio,
                "generic_detectors": ["connected_component", "normal_cluster", "pca_aspect", "repetition"],
            },
        ))
        detections.append({"component_id": component.component_id, **evidence})

    split_reason = "KEEP_SINGLE"
    if len(significant) > 1:
        split_reason = "SIGNIFICANT_CONNECTED_COMPONENTS"
    elif len({item.geometry_regime for item in refined}) > 1:
        split_reason = "GEOMETRY_REGIME"
    return {
        "refined_parts": refined,
        "components": components,
        "repetition_groups": repetition_groups,
        "detections": detections,
        "split_reason": split_reason,
        "split_performed": len(refined) > 1,
    }

