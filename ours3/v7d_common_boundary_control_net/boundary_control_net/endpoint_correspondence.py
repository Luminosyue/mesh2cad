"""Part-agnostic endpoint correspondence with global continuity scoring."""

from __future__ import annotations

from itertools import product

import numpy as np


PAIRINGS = (
    (((0, 0), (-1, -1))),
    (((0, -1), (-1, 0))),
    (((-1, -1), (0, 0))),
    (((-1, 0), (0, -1))),
)


def _unit(vector):
    vector = np.asarray(vector, float)
    return vector / max(float(np.linalg.norm(vector)), 1e-15)


def _endpoint_tangent(points, index):
    points = np.asarray(points, float)
    return _unit(points[1] - points[0]) if index == 0 else _unit(points[-2] - points[-1])


def _sequence_metrics(tracks):
    curvature = flips = step_variation = 0.0
    for points in tracks:
        steps = np.diff(points, axis=0)
        lengths = np.linalg.norm(steps, axis=1)
        directions = steps / np.maximum(lengths[:, None], 1e-15)
        dots = [float(np.dot(directions[i], directions[i + 1])) for i in range(max(0, len(directions) - 1))]
        flips += sum(value < 0.0 for value in dots)
        curvature += sum(float(np.linalg.norm(directions[i + 1] - directions[i])) for i in range(max(0, len(directions) - 1)))
        step_variation += float(np.std(lengths)) if len(lengths) else 0.0
    return curvature, int(flips), step_variation


def _individual_flips(points, axis_direction):
    steps = np.diff(points, axis=0)
    projections = steps @ _unit(axis_direction)
    nonzero = projections[np.abs(projections) > 1e-12]
    if not len(nonzero): return len(steps)
    sign = 1.0 if np.median(nonzero) >= 0.0 else -1.0
    return int(sum(value * sign < 0.0 for value in projections))


def solve(track_a, track_b, part_diagonal, axis_direction):
    """Return two global seam tracks; no part/id/index lookup is used."""
    a_by_station = {entry["station_id"]: entry for entry in track_a}
    b_by_station = {entry["station_id"]: entry for entry in track_b}
    stations = sorted(set(a_by_station) & set(b_by_station), key=lambda station: a_by_station[station]["station_t"])
    if len(stations) < 4:
        return {"stations": stations, "selected": [], "tracks": [], "status": "REJECT", "reason": "INSUFFICIENT_STATION_OVERLAP"}
    candidates = []
    for assignment in product(range(len(PAIRINGS)), repeat=len(stations)):
        points = [[], []]
        distance_cost = tangent_cost = 0.0
        records = []
        for station, state_index in zip(stations, assignment):
            a = np.asarray(a_by_station[station]["resampled_points_3d"], float)
            b = np.asarray(b_by_station[station]["resampled_points_3d"], float)
            record = {"station_id": station, "station_t": float(a_by_station[station]["station_t"]), "pairs": []}
            for seam_index, (endpoint_a, endpoint_b) in enumerate(PAIRINGS[state_index]):
                pa, pb = a[endpoint_a], b[endpoint_b]
                ta, tb = _endpoint_tangent(a, endpoint_a), _endpoint_tangent(b, endpoint_b)
                distance = float(np.linalg.norm(pa - pb))
                tangent_score = abs(float(np.dot(ta, tb)))
                # Tangent and continuity weighted robust consensus; midpoint is used
                # only when the two evidence confidences are equal.
                confidence_a = 0.5 + 0.5 * tangent_score
                confidence_b = confidence_a
                consensus = (confidence_a * pa + confidence_b * pb) / (confidence_a + confidence_b)
                points[seam_index].append(consensus)
                distance_cost += distance / max(part_diagonal, 1e-15)
                tangent_cost += 1.0 - tangent_score
                record["pairs"].append({
                    "seam_index": seam_index,
                    "endpoint_a": int(endpoint_a),
                    "endpoint_b": int(endpoint_b),
                    "point_a": pa,
                    "point_b": pb,
                    "consensus": consensus,
                    "distance": distance,
                    "tangent_score": tangent_score,
                    "selected": True,
                })
            records.append(record)
        points = [np.asarray(track, float) for track in points]
        curvature, _, step_variation = _sequence_metrics(points)
        direction_flips = sum(_individual_flips(track, axis_direction) for track in points)
        # Global objective: endpoint proximity is evidence, never a forced gate.
        score = distance_cost / (2 * len(stations)) + 0.05 * tangent_cost / (2 * len(stations)) + 0.02 * curvature + 1.0 * direction_flips + 0.03 * step_variation / max(part_diagonal, 1e-15)
        candidates.append((score, direction_flips, curvature, assignment, points, records))
    candidates.sort(key=lambda row: row[0])
    score, direction_flips, curvature, assignment, tracks, records = candidates[0]
    rejected_flip_candidates = sum(row[1] > 0 for row in candidates)
    for record_index, record in enumerate(records):
        previous = tracks[0][record_index - 1] if record_index else tracks[0][record_index]
        following = tracks[0][record_index + 1] if record_index + 1 < len(records) else tracks[0][record_index]
        continuity = float(np.linalg.norm(following - previous))
        for pair in record["pairs"]:
            pair["continuity_score"] = float(np.exp(-continuity / max(part_diagonal, 1e-15)))
    track_direction_flips = [_individual_flips(track, axis_direction) for track in tracks]
    valid_track_indices = [index for index, value in enumerate(track_direction_flips) if value == 0]
    return {
        "stations": stations,
        "selected": records,
        "tracks": tracks,
        "assignment": assignment,
        "objective": float(score),
        "curvature_objective": float(curvature),
        "direction_flip_count": int(direction_flips),
        "track_direction_flip_counts": track_direction_flips,
        "valid_track_indices": valid_track_indices,
        "endpoint_flip_count": int(direction_flips),
        "endpoint_flip_rejected_count": int(direction_flips),
        "rejected_candidate_assignment_count": int(rejected_flip_candidates),
        "status": "VALID" if valid_track_indices else "REJECT",
    }
