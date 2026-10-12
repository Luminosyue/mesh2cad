from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh


@dataclass(frozen=True)
class Component:
    component_id: int
    face_indices: list[int]
    area: float
    area_ratio: float
    bbox: list[list[float]]
    centroid: list[float]
    bbox_diag_ratio: float
    tiny: bool


def split_connected_components(mesh: trimesh.Trimesh) -> list[Component]:
    """Return deterministic face-index connected components without changing mesh geometry."""
    faces = np.asarray(mesh.faces)
    adjacency = [[] for _ in range(len(faces))]
    for left, right in np.asarray(mesh.face_adjacency, dtype=np.int64):
        adjacency[int(left)].append(int(right))
        adjacency[int(right)].append(int(left))

    seen = np.zeros(len(faces), dtype=bool)
    total_area = max(float(mesh.area), 1e-12)
    total_diag = max(float(np.linalg.norm(mesh.extents)), 1e-12)
    areas = np.asarray(mesh.area_faces, dtype=float)
    components: list[Component] = []
    for start in range(len(faces)):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        group: list[int] = []
        while stack:
            current = stack.pop()
            group.append(current)
            for nxt in adjacency[current]:
                if not seen[nxt]:
                    seen[nxt] = True
                    stack.append(nxt)
        group = sorted(group)
        sub = mesh.submesh([group], append=True, repair=False)
        area = float(areas[group].sum())
        bbox_diag = float(np.linalg.norm(sub.extents))
        area_ratio = area / total_area
        bbox_ratio = bbox_diag / total_diag
        # Triangle count alone is not scale-normalized: a valid coarse box may
        # have only a few faces. Use low area/scale support as the primary
        # fragment signal and let triangle count break ties for tiny pieces.
        tiny = bool(
            area_ratio < 0.01
            or bbox_ratio < 0.04
            or (len(group) < 20 and area_ratio < 0.05)
        )
        components.append(Component(
            component_id=len(components),
            face_indices=group,
            area=area,
            area_ratio=area_ratio,
            bbox=sub.bounds.tolist(),
            centroid=sub.centroid.tolist(),
            bbox_diag_ratio=bbox_ratio,
            tiny=tiny,
        ))
    components.sort(key=lambda item: (-int(not item.tiny), -item.area, item.component_id))
    return [
        Component(index, item.face_indices, item.area, item.area_ratio, item.bbox, item.centroid, item.bbox_diag_ratio, item.tiny)
        for index, item in enumerate(components)
    ]
