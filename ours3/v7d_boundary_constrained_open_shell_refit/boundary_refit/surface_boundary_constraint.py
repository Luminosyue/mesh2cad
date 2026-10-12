"""Numerical QA for actual constrained surface boundaries."""

import numpy as np

def boundary_error(points_a, points_b):
    values = np.linalg.norm(np.asarray(points_a, float) - np.asarray(points_b, float), axis=1)
    return {"mean": float(values.mean()), "p95": float(np.quantile(values, .95)), "max": float(values.max())}

def ablation_pass(unconstrained_p95, constrained_p95):
    return constrained_p95 < unconstrained_p95 * .1

