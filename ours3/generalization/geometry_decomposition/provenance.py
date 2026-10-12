from __future__ import annotations

import hashlib

import numpy as np


def triangle_ids_hash(ids: list[int]) -> str:
    arr = np.asarray(sorted(ids), dtype=np.int64)
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()

