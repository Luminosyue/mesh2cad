"""Versioned, hash-bound measured chain descriptors for V7D2B."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

import numpy as np


def geometry_hash(points):
    array = np.asarray(points, dtype="<f8")
    return hashlib.sha256(array.tobytes()).hexdigest()


def resample(points, count=32):
    points = np.asarray(points, float)
    distances = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    if len(points) < 2 or distances[-1] <= 1e-12:
        raise ValueError("DEGENERATE_CHAIN")
    targets = np.linspace(0.0, distances[-1], int(count))
    return np.vstack([np.interp(targets, distances, points[:, axis]) for axis in range(3)]).T


def descriptor(points, origin, basis_u, basis_v, station_id, chain_id, count=32):
    points = np.asarray(points, float)
    origin, u, v = (np.asarray(value, float) for value in (origin, basis_u, basis_v))
    sampled = resample(points, count)
    local = np.c_[(sampled - origin) @ u, (sampled - origin) @ v]
    steps = np.diff(sampled, axis=0)
    tangents = steps / np.maximum(np.linalg.norm(steps, axis=1, keepdims=True), 1e-15)
    turns = []
    for first, second in zip(tangents[:-1], tangents[1:]):
        turns.append(math.acos(np.clip(float(np.dot(first, second)), -1.0, 1.0)))
    centered = points - points.mean(axis=0)
    principal = np.linalg.svd(centered, full_matrices=False)[2][0]
    if np.dot(principal, points[-1] - points[0]) < 0:
        principal = -principal
    gh = geometry_hash(points)
    result = {
        "descriptor_version": "V7D2B_CHAIN_DESCRIPTOR_V1",
        "station_id": station_id,
        "chain_id": chain_id,
        "arc_length": float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum()),
        "centroid": points.mean(axis=0).tolist(),
        "bbox": [points.min(axis=0).tolist(), points.max(axis=0).tolist()],
        "endpoint_0": points[0].tolist(),
        "endpoint_1": points[-1].tolist(),
        "endpoint_tangent_0": tangents[0].tolist(),
        "endpoint_tangent_1": tangents[-1].tolist(),
        "principal_direction": principal.tolist(),
        "station_local_coordinates": local.tolist(),
        "local_u_range": [float(local[:, 0].min()), float(local[:, 0].max())],
        "local_v_range": [float(local[:, 1].min()), float(local[:, 1].max())],
        "resampled_points_local": local.tolist(),
        "resampled_shape_forward": local.tolist(),
        "resampled_shape_reversed": local[::-1].tolist(),
        "curvature_signature": turns,
        "side_signature": float(np.mean(local[:, 1])),
        "orientation_signature": (local[-1] - local[0]).tolist(),
        "geometry_hash": gh,
        "descriptor_source_geometry_hash": gh,
        "descriptor_dirty": False,
    }
    return result


@dataclass
class ChainRecord:
    station_id: str
    chain_id: str
    points: np.ndarray
    origin: np.ndarray
    basis_u: np.ndarray
    basis_v: np.ndarray
    data: dict | None = None
    dirty: bool = True

    def recompute_descriptor(self):
        self.data = descriptor(self.points, self.origin, self.basis_u, self.basis_v,
                               self.station_id, self.chain_id)
        self.dirty = False
        return self.data

    def reverse(self, recompute=True):
        self.points = np.asarray(self.points)[::-1].copy()
        self.dirty = True
        if self.data is not None:
            self.data["descriptor_dirty"] = True
        if recompute:
            self.recompute_descriptor()

    def assert_clean(self):
        stale = (self.dirty or self.data is None or
                 self.data.get("descriptor_dirty", True) or
                 geometry_hash(self.points) != self.data.get("descriptor_source_geometry_hash"))
        if stale:
            raise ValueError("STALE_DESCRIPTOR_DETECTED")
        return True


def canonicalize(record: ChainRecord):
    """Generic station-local orientation: lexicographically smaller (u,v) endpoint first."""
    points = np.asarray(record.points, float)
    local = np.c_[(points[[0, -1]] - record.origin) @ record.basis_u,
                  (points[[0, -1]] - record.origin) @ record.basis_v]
    reversed_order = tuple(local[1]) < tuple(local[0])
    if reversed_order:
        record.reverse(recompute=False)
    record.recompute_descriptor()
    record.data["orientation_state"] = "CANONICAL_REVERSED" if reversed_order else "CANONICAL_FORWARD"
    record.data["point_order_reversed"] = reversed_order
    return reversed_order


def clean_json(value):
    if isinstance(value, dict): return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean_json(v) for v in value]
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    return value


def descriptor_hash(value):
    payload = json.dumps(clean_json(value), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()
