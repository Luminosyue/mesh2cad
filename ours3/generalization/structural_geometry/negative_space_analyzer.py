from __future__ import annotations

import numpy as np


def negative_space_evidence(occupancy: dict) -> dict:
    source_occ = float(occupancy["source_occupancy_ratio"])
    cad_occ = float(occupancy["cad_occupancy_ratio"])
    void = float(occupancy["void_preservation_ratio"])
    sparse = source_occ < 0.55 or void > 0.75
    false_positive = float(occupancy["false_positive_occupancy_ratio"])
    return {
        "negative_space_evidence": bool(sparse),
        "source_void_fraction": 1.0 - source_occ,
        "candidate_void_fraction": 1.0 - cad_occ,
        "negative_space_hard_reject": bool(sparse and (false_positive > 0.25 or void < 0.55)),
        "negative_space_violation": bool(sparse and false_positive > 0.25),
    }
