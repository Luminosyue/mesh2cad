"""Part-agnostic dynamic-programming endpoint correspondence utilities."""

import numpy as np

ENDPOINT_STATES = ((0, 0), (0, -1), (-1, 0), (-1, -1))

def endpoint_cost(points_a, points_b, state):
    ia, ib = state
    return float(np.linalg.norm(np.asarray(points_a)[ia] - np.asarray(points_b)[ib]))

def has_fixed_index_rule(source_text):
    forbidden = ("if part ==", "if part_id ==", "FUSELAGE: use endpoint", "VERTICAL_TAIL: use endpoint")
    return any(item in source_text for item in forbidden)

