"""Evidence-gated face-boundary matching; nearest alone is never accepted."""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree


def compare_boundaries(a, b, part_diagonal, station_overlap=0.0, adjacency_expected=True):
    pa, pb = np.asarray(a["points"], float), np.asarray(b["points"], float)
    da = cKDTree(pb).query(pa)[0]
    db = cKDTree(pa).query(pb)[0]
    distances = np.r_[da, db]
    same = np.linalg.norm(pa - pb, axis=1).mean()
    reverse = np.linalg.norm(pa - pb[::-1], axis=1).mean()
    orientation = "SAME" if same <= reverse else "REVERSED"
    endpoints = min(
        np.linalg.norm(pa[0] - pb[0]) + np.linalg.norm(pa[-1] - pb[-1]),
        np.linalg.norm(pa[0] - pb[-1]) + np.linalg.norm(pa[-1] - pb[0]),
    ) / 2
    length_ratio = min(a["length"], b["length"]) / max(a["length"], b["length"], 1e-15)
    tangent = max(abs(float(np.dot(a["tangent_start"], b["tangent_start"]))), abs(float(np.dot(a["tangent_start"], b["tangent_end"]))))
    scale = max(float(part_diagonal), 1e-15)
    distance_score = float(np.exp(-distances.mean() / (scale * 1e-3)))
    endpoint_score = float(np.exp(-endpoints / (scale * 2e-3)))
    score = 0.35 * distance_score + 0.20 * endpoint_score + 0.15 * length_ratio + 0.10 * tangent + 0.10 * station_overlap + 0.10 * float(adjacency_expected)
    gates = {
        "mean_distance": distances.mean() <= scale * 1e-3,
        "p95_distance": np.quantile(distances, .95) <= scale * 2e-3,
        "endpoint": endpoints <= scale * 3e-3,
        "length": length_ratio >= .90,
        "tangent": tangent >= .80,
        "station": station_overlap >= .50,
        "semantic": a["semantic_type"] == b["semantic_type"] and a["semantic_type"] in {"SIDE_BOUNDARY", "ROOT_BOUNDARY", "TIP_BOUNDARY"},
        "adjacency": bool(adjacency_expected),
    }
    accepted = all(gates.values()) and score >= .85
    return {
        "face_a_boundary": a["boundary_id"],
        "face_b_boundary": b["boundary_id"],
        "distance_mean": float(distances.mean()),
        "distance_p95": float(np.quantile(distances, .95)),
        "hausdorff": float(distances.max()),
        "endpoint_distance": float(endpoints),
        "length_ratio": float(length_ratio),
        "tangent_consistency": float(tangent),
        "orientation_relation": orientation,
        "station_overlap": float(station_overlap),
        "match_score": float(score),
        "evidence_gates": gates,
        "accepted": bool(accepted),
        "status": "ACCEPTED" if accepted else "UNRESOLVED",
    }


def match_face_pair(face_a, face_b, part_diagonal, station_overlap):
    pairs = [compare_boundaries(a, b, part_diagonal, station_overlap) for a in face_a["boundaries"] for b in face_b["boundaries"]]
    pairs.sort(key=lambda item: item["match_score"], reverse=True)
    accepted, used_a, used_b = [], set(), set()
    for pair in pairs:
        if pair["accepted"] and pair["face_a_boundary"] not in used_a and pair["face_b_boundary"] not in used_b:
            accepted.append(pair)
            used_a.add(pair["face_a_boundary"]); used_b.add(pair["face_b_boundary"])
    return pairs, accepted
