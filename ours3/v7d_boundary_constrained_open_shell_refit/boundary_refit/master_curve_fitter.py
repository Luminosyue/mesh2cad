"""Master-curve provenance and rejection checks."""

import numpy as np

def provenance(curve_id, station_ids, chain_ids):
    return {"curve_id": curve_id, "source": "MEASURED_OPEN_CHAIN_ENDPOINT_TRACK", "source_station_ids": list(station_ids), "source_chain_ids": list(chain_ids), "source_mesh_resection": False, "bbox_generated": False, "convex_hull_generated": False}

def valid_fit(errors, part_diagonal, confidence):
    errors = np.asarray(errors, float)
    return confidence in {"HIGH", "MEDIUM"} and len(errors) >= 4 and np.quantile(errors, .95) <= part_diagonal * .02

