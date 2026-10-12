from __future__ import annotations

from typing import Any

import numpy as np
import trimesh


def recursive_split_mesh(
    mesh: trimesh.Trimesh,
    min_faces: int = 80,
    normal_angle_degrees: float = 42.0,
    max_parts: int = 24,
) -> list[tuple[list[int], trimesh.Trimesh]]:
    """Split only on strong geometric boundaries and preserve source coordinates."""
    if len(mesh.faces) < min_faces * 2:
        return [([int(index) for index in range(len(mesh.faces))], mesh)]

    components = list(mesh.split(only_watertight=False))
    if len(components) > 1:
        significant = [
            item
            for item in components
            if len(item.faces) >= max(min_faces, int(len(mesh.faces) * 0.01))
        ]
        if len(significant) > 1:
            return [([], item) for item in significant]

    try:
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
    except Exception:
        return [([int(index) for index in range(len(mesh.faces))], mesh)]

    adjacency = np.asarray(mesh.face_adjacency, dtype=np.int64)
    if len(adjacency) == 0:
        return [([int(index) for index in range(len(mesh.faces))], mesh)]
    normals = np.asarray(mesh.face_normals, dtype=float)
    dots = np.sum(normals[adjacency[:, 0]] * normals[adjacency[:, 1]], axis=1)
    threshold = float(np.cos(np.deg2rad(normal_angle_degrees)))
    kept = adjacency[dots >= threshold]
    if len(kept) == 0:
        return [([int(index) for index in range(len(mesh.faces))], mesh)]
    rows = np.concatenate([kept[:, 0], kept[:, 1]])
    cols = np.concatenate([kept[:, 1], kept[:, 0]])
    graph = coo_matrix(
        (np.ones(len(rows), dtype=np.uint8), (rows, cols)),
        shape=(len(mesh.faces), len(mesh.faces)),
    )
    _, labels = connected_components(graph.tocsr(), directed=False)
    groups = [
        np.flatnonzero(labels == label)
        for label in np.unique(labels)
        if int(np.sum(labels == label)) >= min_faces
    ]
    if len(groups) <= 1 or len(groups) > max_parts:
        return [([int(index) for index in range(len(mesh.faces))], mesh)]
    covered = sum(len(group) for group in groups)
    if covered / max(len(mesh.faces), 1) < 0.96:
        return [([int(index) for index in range(len(mesh.faces))], mesh)]
    return [
        (
            [int(index) for index in group],
            mesh.submesh([group.tolist()], append=True, repair=False),
        )
        for group in groups
    ]


def structural_decomposition_decision(analysis: dict[str, Any]) -> dict[str, Any]:
    structural_class = analysis.get("structural_class", "UNKNOWN")
    evidence = {
        "significant_components": int(analysis.get("significant_component_count", 1)),
        "repetition_groups": int(analysis.get("repetition_group_count", 0)),
        "attachment_count": int(analysis.get("attachment_count", 0)),
    }
    if structural_class in {"ROD_NETWORK", "SPARSE_FRAME", "OPEN_FRAME", "BODY_WITH_APPENDAGES"}:
        return {
            "recursive_decomposition_required": True,
            "structural_split_recommended": True,
            "split_reason": "STRUCTURAL_BRANCHING_OR_SPARSE_OCCUPANCY",
            "split_evidence": evidence,
        }
    return {
        "recursive_decomposition_required": False,
        "structural_split_recommended": False,
        "split_reason": "SINGLE_STRUCTURAL_REGION",
        "split_evidence": evidence,
    }
