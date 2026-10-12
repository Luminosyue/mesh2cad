from __future__ import annotations

from .schema import RefinedPart


def graph_rows(parts: list[RefinedPart]) -> list[dict]:
    return [
        {
            "refined_part_id": part.refined_part_id,
            "parent_coarse_part_id": part.parent_coarse_part_id,
            "source_p3_segment_ids": part.source_p3_segment_ids,
            "triangle_count": len(part.triangle_ids),
            "triangle_ids_hash": part.provenance["triangle_ids_hash"],
            "geometry_regime": part.geometry_regime,
            "geometry_confidence": part.geometry_confidence,
            "connected_component_id": part.connected_component_id,
            "repetition_group_id": part.repetition_group_id,
            "bbox": part.bbox,
            "centroid": part.centroid,
            "backend_eligibility": part.backend_eligibility,
            "provenance": part.provenance,
        }
        for part in parts
    ]

