from __future__ import annotations

import numpy as np


def falloff(strip_rows):
    """Configurable monotone boundary influence; row zero is exact."""
    if strip_rows < 1:
        raise ValueError("BOUNDARY_STRIP_ROWS_MUST_BE_POSITIVE")
    if strip_rows == 1:
        return np.asarray([1.0])
    x = np.linspace(0.0, 1.0, strip_rows)
    return (1.0 - x) ** 2


def row_policy(row_index, strip_rows):
    if row_index == 0: return "HARD_FIXED_TO_MASTER"
    if row_index < strip_rows: return "SOFT_ANCHOR"
    return "HARD_FREEZE"

