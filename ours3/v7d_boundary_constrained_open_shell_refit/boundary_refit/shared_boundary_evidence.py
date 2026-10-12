"""Confidence gating for measured open-chain endpoint seam evidence."""

def confidence(track_metrics, pair_p95, part_diagonal):
    coverage = track_metrics["TRACK_STATION_COVERAGE"]
    flips = track_metrics["TRACK_DIRECTION_FLIP_COUNT"]
    curvature = track_metrics["TRACK_CURVATURE"]
    residual = pair_p95 / max(part_diagonal, 1e-15)
    if coverage >= .8 and flips == 0 and curvature <= .25 and residual <= .02:
        return "HIGH"
    if coverage >= .6 and flips == 0 and curvature <= .5 and residual <= .05:
        return "MEDIUM"
    return "REJECT"

