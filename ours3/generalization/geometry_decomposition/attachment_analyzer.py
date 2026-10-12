from __future__ import annotations

from typing import Any

import numpy as np


def attachment_relations(parts: list[dict[str, Any]], tolerance_ratio: float = 0.03) -> list[dict[str, Any]]:
    rows = []
    if not parts:
        return rows
    lows = np.asarray([part["bbox"][0] for part in parts], dtype=float)
    highs = np.asarray([part["bbox"][1] for part in parts], dtype=float)
    diag = max(float(np.linalg.norm(highs.max(axis=0) - lows.min(axis=0))), 1e-12)
    tol = diag * tolerance_ratio
    for i, left in enumerate(parts):
        for right in parts[i + 1:]:
            a0, a1 = np.asarray(left["bbox"][0]), np.asarray(left["bbox"][1])
            b0, b1 = np.asarray(right["bbox"][0]), np.asarray(right["bbox"][1])
            gap = np.maximum(np.maximum(a0 - b1, b0 - a1), 0.0)
            distance = float(np.linalg.norm(gap))
            if distance <= tol:
                rows.append({
                    "left_refined_part_id": left["refined_part_id"],
                    "right_refined_part_id": right["refined_part_id"],
                    "attachment_type": "TOUCHING" if distance > 1e-9 else "INTERSECTING",
                    "distance": distance,
                })
    return rows

