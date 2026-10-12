"""Metrics and confidence for globally corresponding endpoint tracks."""

from __future__ import annotations

import numpy as np


def describe(track_id, points, station_count, source_station_count, part_diagonal, pair_distances):
    points = np.asarray(points, float)
    steps = np.diff(points, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    directions = steps / np.maximum(lengths[:, None], 1e-15)
    direction_flips = sum(float(np.dot(directions[i], directions[i + 1])) < 0.0 for i in range(max(0, len(directions) - 1)))
    curvature = [float(np.linalg.norm(directions[i + 1] - directions[i])) for i in range(max(0, len(directions) - 1))]
    coverage = station_count / max(source_station_count, 1)
    normalized_p95 = (float(np.quantile(lengths, 0.95)) if len(lengths) else 0.0) / max(part_diagonal, 1e-15)
    pair_p95 = float(np.quantile(pair_distances, 0.95)) / max(part_diagonal, 1e-15)
    confidence = "HIGH" if coverage >= 0.75 and direction_flips == 0 and normalized_p95 < 0.35 and pair_p95 <= 0.08 else "MEDIUM" if coverage >= 0.40 and direction_flips == 0 and pair_p95 <= 0.15 else "REJECT"
    return {
        "track_id": track_id,
        "TRACK_STATION_COUNT": int(station_count),
        "TRACK_STATION_COVERAGE": float(coverage),
        "TRACK_LENGTH": float(lengths.sum()),
        "STEP_DISTANCE_MEAN": float(lengths.mean()) if len(lengths) else 0.0,
        "STEP_DISTANCE_P95": float(np.quantile(lengths, 0.95)) if len(lengths) else 0.0,
        "CURVATURE_MEAN": float(np.mean(curvature)) if curvature else 0.0,
        "CURVATURE_P95": float(np.quantile(curvature, 0.95)) if curvature else 0.0,
        "DIRECTION_FLIP_COUNT": int(direction_flips),
        "TRACK_CONFIDENCE": confidence,
        "PAIR_DISTANCE_P95": float(np.quantile(pair_distances, 0.95)),
        "NORMALIZED_PAIR_DISTANCE_P95": pair_p95,
    }
