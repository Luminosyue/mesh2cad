from __future__ import annotations

import numpy as np
from OCP.gp import gp_Pnt

from .boundary_strip import falloff
from .control_net_anchor import displacement_metrics


def poles(surface):
    return np.asarray([[[surface.Pole(u, v).X(), surface.Pole(u, v).Y(), surface.Pole(u, v).Z()] for v in range(1, surface.NbVPoles() + 1)] for u in range(1, surface.NbUPoles() + 1)])


def apply(surface, master_poles, boundary_side, strip_rows, anchor_enabled=True):
    result = surface.Copy()
    original = poles(result)
    master_poles = np.asarray(master_poles, float)
    if len(master_poles) != result.NbUPoles():
        raise ValueError("MASTER_POLE_COUNT_MISMATCH")
    weights = falloff(strip_rows) if anchor_enabled else np.ones(result.NbVPoles())
    boundary_column = 0 if boundary_side == "V_MIN" else result.NbVPoles() - 1
    for u in range(result.NbUPoles()):
        delta = master_poles[u] - original[u, boundary_column]
        for distance, weight in enumerate(weights):
            column = distance if boundary_side == "V_MIN" else result.NbVPoles() - 1 - distance
            point = original[u, column] + delta * weight
            result.SetPole(u + 1, column + 1, gp_Pnt(*map(float, point)))
    changed = poles(result)
    metrics = displacement_metrics(original, changed, strip_rows if anchor_enabled else result.NbVPoles())
    metrics["BOUNDARY_STRIP_ROWS"] = int(strip_rows)
    metrics["ANCHOR_ENABLED"] = bool(anchor_enabled)
    return result, metrics, original, changed

