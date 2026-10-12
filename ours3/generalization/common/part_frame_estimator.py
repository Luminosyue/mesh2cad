from __future__ import annotations

import numpy as np


def _unit(value: np.ndarray) -> np.ndarray:
    return value / max(float(np.linalg.norm(value)), 1e-12)


class StablePartFrameEstimator:
    def estimate(self, vertices: np.ndarray, supporting_normals: np.ndarray | None = None) -> dict:
        points = np.asarray(vertices, dtype=float)
        center = points.mean(axis=0)
        _, values, axes = np.linalg.svd(points - center, full_matrices=False)
        axes = np.asarray(axes, dtype=float)
        order = np.argsort(values)[::-1]
        axes = axes[order]
        if supporting_normals is not None and len(supporting_normals):
            normal = _unit(np.asarray(supporting_normals, dtype=float).mean(axis=0))
            closest = int(np.argmax(np.abs(axes @ normal)))
            axes[[2, closest]] = axes[[closest, 2]]
            if float(np.dot(axes[2], normal)) < 0:
                axes[2] *= -1
        for index in range(3):
            axis = axes[index]
            pivot = int(np.argmax(np.abs(axis)))
            if axis[pivot] < 0:
                axes[index] *= -1
        if np.linalg.det(axes) < 0:
            axes[1] *= -1
        transform = np.eye(4)
        transform[:3, :3] = axes.T
        transform[:3, 3] = -axes.T @ center
        inverse = np.linalg.inv(transform)
        return {
            "center": center.tolist(),
            "axes": axes.tolist(),
            "singular_values": values.tolist(),
            "world_up_used": False,
            "frame_method": "PCA_WITH_DETERMINISTIC_SIGN_AND_NORMAL_SUPPORT",
            "local_to_world": inverse.tolist(),
            "world_to_local": transform.tolist(),
        }

