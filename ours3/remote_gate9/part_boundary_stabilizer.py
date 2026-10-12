from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import trimesh


def _unit(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=float)
    norm = float(np.linalg.norm(value))
    return value / norm if norm > 1e-12 else np.zeros_like(value)


def _hash_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def _pca_axes(vertices: np.ndarray) -> np.ndarray:
    centered = np.asarray(vertices, dtype=float) - np.mean(vertices, axis=0)
    covariance = centered.T @ centered / max(len(centered), 1)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    return vectors[:, order].T


def _semantic_axis(role: str, extents: np.ndarray) -> int:
    role = str(role).upper()
    if "FUSELAGE" in role:
        preferred = 1
    elif "WING" in role or "TAILPLANE" in role:
        preferred = 0
    else:
        preferred = int(np.argmax(extents))
    if extents[preferred] >= 0.55 * float(np.max(extents)):
        return preferred
    return int(np.argmax(extents))


def _deterministic_sign(axis: np.ndarray, role: str, vertices: np.ndarray, axis_index: int) -> np.ndarray:
    result = _unit(axis)
    role = str(role).upper()
    if "LEFT" in role:
        desired = -1.0
    elif "RIGHT" in role:
        desired = 1.0
    else:
        desired = 1.0
    coordinate_direction = float(result[axis_index])
    if abs(coordinate_direction) > 1e-8 and np.sign(coordinate_direction) != desired:
        result = -result
    elif abs(coordinate_direction) <= 1e-8:
        anchor = vertices[np.argmax(vertices @ result)] - vertices[np.argmin(vertices @ result)]
        if float(np.dot(result, anchor)) < 0:
            result = -result
    return result


@dataclass(frozen=True)
class StablePartFrame:
    origin: np.ndarray
    axes: np.ndarray
    longitudinal_axis_index: int
    root: np.ndarray
    tip: np.ndarray
    determinant: float
    normal_orientation: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "origin": self.origin.tolist(),
            "axes": self.axes.tolist(),
            "longitudinal_axis_index": int(self.longitudinal_axis_index),
            "root": self.root.tolist(),
            "tip": self.tip.tolist(),
            "determinant": float(self.determinant),
            "normal_orientation": float(self.normal_orientation),
            "frame_hash": _hash_array(self.axes.astype(np.float64)),
        }


class StablePartFrameEstimator:
    """Estimate a semantic, deterministic frame from source-supported geometry."""

    def estimate(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        semantic_role: str,
        relation: dict[str, Any] | None = None,
    ) -> StablePartFrame:
        vertices = np.asarray(vertices, dtype=float)
        faces = np.asarray(faces, dtype=int)
        origin = np.mean(vertices, axis=0)
        extents = np.ptp(vertices, axis=0)
        axis_index = _semantic_axis(semantic_role, extents)
        pca = _pca_axes(vertices)
        longitudinal = pca[np.argmax(np.abs(pca[:, axis_index]))]
        longitudinal = _deterministic_sign(longitudinal, semantic_role, vertices, axis_index)

        remaining = [row for row in pca if abs(float(np.dot(row, longitudinal))) < 0.9]
        transverse = _unit(remaining[0] if remaining else pca[1])
        normal = _unit(np.cross(longitudinal, transverse))
        if faces.size:
            face_normals = np.asarray(
                trimesh.Trimesh(vertices=vertices, faces=faces, process=False).face_normals,
                dtype=float,
            )
            average_normal = _unit(np.mean(face_normals, axis=0))
            if np.linalg.norm(average_normal) > 1e-8 and np.dot(normal, average_normal) < 0:
                normal = -normal
        transverse = _unit(np.cross(normal, longitudinal))
        axes = np.vstack([longitudinal, transverse, normal])
        if np.linalg.det(axes) < 0:
            axes[1] *= -1
        projection = (vertices - origin) @ longitudinal
        root = vertices[int(np.argmin(projection))]
        tip = vertices[int(np.argmax(projection))]
        orientation = float(np.dot(normal, _unit(np.mean(
            trimesh.Trimesh(vertices=vertices, faces=faces, process=False).face_normals,
            axis=0,
        )))) if faces.size else 0.0
        return StablePartFrame(
            origin=origin,
            axes=axes,
            longitudinal_axis_index=axis_index,
            root=root,
            tip=tip,
            determinant=float(np.linalg.det(axes)),
            normal_orientation=orientation,
        )


def _edge_key(edge: np.ndarray) -> tuple[int, int]:
    edge = np.asarray(edge, dtype=int)
    return tuple(sorted((int(edge[0]), int(edge[1]))))


def boundary_metrics(source: trimesh.Trimesh, face_ids: np.ndarray) -> dict[str, Any]:
    face_ids = np.asarray(face_ids, dtype=int)
    faces = np.asarray(source.faces, dtype=int)[face_ids]
    if len(faces) == 0:
        return {
            "boundary_edge_count": 0,
            "boundary_component_count": 0,
            "open_boundary_count": 0,
            "boundary_length": 0.0,
            "boundary_points": [],
        }
    counts: dict[tuple[int, int], int] = {}
    for face in faces:
        for edge in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = _edge_key(edge)
            counts[key] = counts.get(key, 0) + 1
    boundary = sorted(key for key, count in counts.items() if count == 1)
    adjacency: dict[int, set[int]] = {}
    for a, b in boundary:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    unseen = set(adjacency)
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            node = stack.pop()
            for nxt in adjacency.get(node, ()):
                if nxt in unseen:
                    unseen.remove(nxt)
                    stack.append(nxt)
    points = np.asarray(source.vertices, dtype=float)
    boundary_points = []
    boundary_length = 0.0
    for a, b in boundary:
        boundary_length += float(np.linalg.norm(points[a] - points[b]))
        boundary_points.extend([points[a], 0.5 * (points[a] + points[b]), points[b]])
    return {
        "boundary_edge_count": len(boundary),
        "boundary_component_count": components,
        "open_boundary_count": components,
        "boundary_length": boundary_length,
        "boundary_points": np.asarray(boundary_points, dtype=float).tolist(),
    }


class PartBoundaryStabilizer:
    """Keep P3 membership source-supported while making graph/frame output stable."""

    def stabilize(
        self,
        source_mesh: trimesh.Trimesh,
        triangle_part_id: np.ndarray,
        cad_part_graph: dict[str, Any],
    ) -> dict[str, Any]:
        labels = np.asarray(triangle_part_id, dtype=int).copy()
        if len(labels) != len(source_mesh.faces):
            raise ValueError("triangle_part_id length must equal source face count")
        estimator = StablePartFrameEstimator()
        nodes = []
        for node in sorted(cad_part_graph.get("nodes", []), key=lambda item: str(item.get("part_id", ""))):
            segments = sorted(int(value) for value in node.get("source_segment_ids", []))
            face_ids = np.flatnonzero(np.isin(labels, segments))
            part = source_mesh.submesh([face_ids], append=True, repair=False)
            frame = estimator.estimate(
                np.asarray(part.vertices),
                np.asarray(part.faces),
                str(node.get("semantic_role", "UNKNOWN")),
                node.get("relations"),
            )
            nodes.append({
                **node,
                "source_segment_ids": segments,
                "support_triangle_ids": face_ids.tolist(),
                "triangle_count": int(len(face_ids)),
                "local_coordinate_frame": frame.axes.tolist(),
                "local_frame": frame.as_dict(),
                "boundary_metrics": boundary_metrics(source_mesh, face_ids),
                "source_derived": True,
                "historical_geometry_input": False,
                "old_part_mesh_reused": False,
                "old_triangle_membership_reused": False,
            })
        return {
            "schema": "STABILIZED_CAD_PART_GRAPH_SOURCE_DERIVED_V1",
            "source_derived": True,
            "historical_geometry_input": False,
            "old_part_mesh_reused": False,
            "old_triangle_membership_reused": False,
            "membership_changed_triangle_count": 0,
            "triangle_part_id": labels,
            "nodes": nodes,
        }
