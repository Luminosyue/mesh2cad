from __future__ import annotations

import numpy as np
import trimesh


def topology_complexity(mesh: trimesh.Trimesh) -> dict:
    components = mesh.split(only_watertight=False)
    boundary_edges = 0
    try:
        edges_face = np.asarray(mesh.edges_face, dtype=np.int64)
        if edges_face.ndim == 2 and edges_face.shape[1] == 2:
            boundary_edges = int(np.sum(np.any(edges_face < 0, axis=1)))
    except Exception:
        boundary_edges = 0
    face_adjacency = np.asarray(mesh.face_adjacency, dtype=np.int64)
    degree = np.bincount(face_adjacency.reshape(-1), minlength=len(mesh.faces)) if len(face_adjacency) else np.zeros(len(mesh.faces))
    branch_count = int(np.sum(degree >= 5))
    euler = None
    try:
        euler = int(mesh.euler_number)
    except Exception:
        pass
    return {
        "connected_component_count": len(components),
        "significant_component_count": sum(len(item.faces) >= max(8, len(mesh.faces) * 0.005) for item in components),
        "boundary_edge_count": boundary_edges,
        "skeleton_branch_count": branch_count,
        "major_hole_count": int(max(0, 1 - (euler or 0))) if mesh.is_watertight else 0,
        "void_region_count": int(max(0, len(components) - 1)),
        "source_topology_complexity_score": float(min(1.0, (branch_count / max(len(mesh.faces), 1)) * 12.0 + (0.2 if not mesh.is_watertight else 0.0))),
        "principal_axis_count": 3 if len(mesh.vertices) else 0,
    }
