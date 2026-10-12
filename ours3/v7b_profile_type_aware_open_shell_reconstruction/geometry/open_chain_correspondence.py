"""Topology-safe open-chain ordering, resampling, and station correspondence."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.interpolate import splprep, splev


def chain_length(points):
    points = np.asarray(points, float)
    return float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum()) if len(points) > 1 else 0.0


def ordered_chain_from_graph(nodes, edges, component):
    """Traverse a simple graph chain; coordinate sorting is intentionally forbidden."""
    nodes = np.asarray(nodes, float)
    component = set(int(value) for value in component)
    adjacency = {node: set() for node in component}
    for a, b in edges:
        if a in component and b in component:
            adjacency[a].add(b)
            adjacency[b].add(a)
    endpoints = sorted(node for node in component if len(adjacency[node]) == 1)
    if len(endpoints) != 2 or any(len(adjacency[node]) not in {1, 2} for node in component):
        raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
    order, previous, current = [endpoints[0]], None, endpoints[0]
    while current != endpoints[1]:
        choices = adjacency[current] - ({previous} if previous is not None else set())
        if len(choices) != 1:
            raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
        nxt = next(iter(choices))
        if nxt in order:
            raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
        order.append(nxt)
        previous, current = current, nxt
    return nodes[order]


def resample_open_chain(points, count=64):
    points = np.asarray(points, float)
    if len(points) < 2:
        raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
    distances = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    if distances[-1] <= 1e-12:
        raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
    targets = np.linspace(0.0, distances[-1], int(count))
    return np.vstack([np.interp(targets, distances, points[:, axis]) for axis in range(3)]).T


def fit_open_bspline(raw_points, resampled_points, smoothing=0.0):
    raw = np.asarray(raw_points, float)
    sampled = np.asarray(resampled_points, float)
    k = min(3, len(sampled) - 1)
    tck, _ = splprep(sampled.T, s=float(smoothing), k=k, per=False)
    dense = np.asarray(splev(np.linspace(0, 1, max(256, len(sampled) * 4)), tck)).T
    # QA measures each raw point to the dense smooth curve.
    distances = np.min(np.linalg.norm(raw[:, None, :] - dense[None, :, :], axis=2), axis=1)
    scale = max(chain_length(raw), 1e-12)
    mean_error = float(distances.mean() / scale)
    p95_error = float(np.quantile(distances / scale, 0.95))
    return {
        "curve_type": "OPEN_BSPLINE",
        "periodic": False,
        "valid": bool(mean_error <= 0.01 and p95_error <= 0.025),
        "mean_error": mean_error,
        "p95_error": p95_error,
        "max_error": float(distances.max() / scale),
        "dense_points_3d": dense.tolist(),
    }


def descriptor(chain, plane_origin, basis_u, basis_v):
    points = np.asarray(chain, float)
    origin, u, v = map(lambda value: np.asarray(value, float), (plane_origin, basis_u, basis_v))
    uv = np.c_[(points - origin) @ u, (points - origin) @ v]
    span = np.maximum(np.ptp(uv, axis=0), 1e-12)
    normalized = (uv - uv.mean(0)) / span
    sample = np.vstack([np.interp(np.linspace(0, len(points) - 1, 16), np.arange(len(points)), normalized[:, i]) for i in range(2)]).T
    return {
        "centroid_uv": uv.mean(0),
        "endpoints_uv": uv[[0, -1]],
        "length": chain_length(points),
        "orientation": points[-1] - points[0],
        "shape": sample,
    }


def correspondence_cost(a, b, scale):
    center = np.linalg.norm(a["centroid_uv"] - b["centroid_uv"]) / scale
    length = abs(a["length"] - b["length"]) / max(a["length"], b["length"], 1e-12)
    same = np.linalg.norm(a["endpoints_uv"] - b["endpoints_uv"])
    flipped = np.linalg.norm(a["endpoints_uv"] - b["endpoints_uv"][::-1])
    endpoint = min(same, flipped) / scale
    shape = min(np.mean(np.linalg.norm(a["shape"] - b["shape"], axis=1)), np.mean(np.linalg.norm(a["shape"] - b["shape"][::-1], axis=1)))
    return float(0.35 * center + 0.25 * length + 0.25 * endpoint + 0.15 * shape), flipped < same


def build_chain_tracks(stations, max_cost=1.25):
    """Associate chains across adjacent stations by geometry, not raw list order."""
    tracks = {}
    next_track = 0
    previous = []
    assignments = []
    flips = 0
    for station in stations:
        current = station["chains"]
        if not current:
            previous = []
            continue
        if not previous:
            for chain in current:
                track_id = f"TRACK_{next_track}"
                next_track += 1
                chain["track_id"] = track_id
                tracks.setdefault(track_id, []).append(chain)
        else:
            scale = max(max(item["descriptor"]["length"] for item in previous + current), 1e-12)
            matrix = np.asarray([[correspondence_cost(a["descriptor"], b["descriptor"], scale)[0] for b in current] for a in previous])
            row_ids, col_ids = linear_sum_assignment(matrix)
            matched = set()
            for row, col in zip(row_ids, col_ids):
                if matrix[row, col] > max_cost:
                    continue
                chain = current[col]
                chain["track_id"] = previous[row]["track_id"]
                _, reverse = correspondence_cost(previous[row]["descriptor"], chain["descriptor"], scale)
                if reverse:
                    chain["raw_points_3d"] = chain["raw_points_3d"][::-1].copy()
                    chain["resampled_points_3d"] = chain["resampled_points_3d"][::-1].copy()
                    chain["orientation_reversed"] = True
                    flips += 1
                tracks.setdefault(chain["track_id"], []).append(chain)
                assignments.append({"from": previous[row]["chain_key"], "to": chain["chain_key"], "track_id": chain["track_id"], "cost": float(matrix[row, col])})
                matched.add(col)
            for col, chain in enumerate(current):
                if col not in matched:
                    track_id = f"TRACK_{next_track}"
                    next_track += 1
                    chain["track_id"] = track_id
                    tracks.setdefault(track_id, []).append(chain)
        previous = current
    return tracks, assignments, flips
