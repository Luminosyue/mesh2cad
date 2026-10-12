from __future__ import annotations

import numpy as np


def displacement_metrics(original, changed, strip_rows):
    original, changed = np.asarray(original, float), np.asarray(changed, float)
    displacement = np.linalg.norm(changed - original, axis=2)
    moved = displacement > 1e-12
    strip_mask = np.zeros_like(moved, dtype=bool); strip_mask[:, :strip_rows] = True
    inside = int(np.logical_and(moved, strip_mask).sum())
    moved_count = int(moved.sum())
    interior = displacement[:, strip_rows:].ravel()
    return {
        "TOTAL_CONTROL_POINT_COUNT": int(displacement.size),
        "MOVED_CONTROL_POINT_COUNT": moved_count,
        "MOVED_CONTROL_POINT_RATIO": float(moved_count / max(displacement.size, 1)),
        "BOUNDARY_STRIP_MOVEMENT_RATE": float(inside / max(moved_count, 1)),
        "MAX_CONTROL_POINT_DISPLACEMENT": float(displacement.max()),
        "P95_CONTROL_POINT_DISPLACEMENT": float(np.quantile(displacement, 0.95)),
        "ROW_MAX_DISPLACEMENTS": [float(displacement[:, row].max()) for row in range(displacement.shape[1])],
        "INTERIOR_RMS_DEVIATION_FROM_V7B": float(np.sqrt(np.mean(interior ** 2))) if len(interior) else 0.0,
        "INTERIOR_P95_DEVIATION_FROM_V7B": float(np.quantile(interior, 0.95)) if len(interior) else 0.0,
        "INTERIOR_MAX_DEVIATION_FROM_V7B": float(interior.max()) if len(interior) else 0.0,
        "displacement": displacement,
    }

