# DeepCAD Metric Definition Audit

Official source: rundiwu/DeepCAD, evaluation/evaluate_ae_cd.py, commit f7b350790a3bce0267a5345339fd09be0250c8cb.

## CD

- DEEPCAD_CD_DEFINITION: symmetric Chamfer distance implemented as the sum of two means of squared nearest-neighbor distances.
- Direction 1: each GT point queries the generated-point KDTree.
- Direction 2: each generated point queries the GT-point KDTree.
- DEEPCAD_SURFACE_SAMPLE_N: default 2000 points (--n_points), sampled from GT PLY and generated STL surface.
- DEEPCAD_DISTANCE_SQUARED: yes (np.square).
- DEEPCAD_DISTANCE_SYMMETRIC: yes, summed, not averaged across directions.
- Generated points are transformed by gen_points / scale - offset; official call uses offset=0 and scale=1. If generated coordinates exceed 2, only generated points are normalized by max absolute coordinate. GT points are not normalized in this branch.
- GT sampling uses Python random.sample without a seed in the official script, so results are stochastic unless the caller supplies deterministic seeding externally.

## IR / invalid

A case returns invalid (None) when its GT PLY is missing, vec2CADsolid raises, CADsolid2pc raises including an empty or void BRep box, or downstream generated point sampling fails. The script counts None as invalid and reports invalid / total; it does not equate IR with STEP reload.

DEEPCAD_IR_DEFINITION = invalid_case_count / total_case_count, using the failure conditions above.

## IoU

The official evaluate_ae_cd.py contains no IoU definition. IoU must therefore be specified separately as a solid-volume Boolean metric with explicit frame, normalization, and invalid-case denominator policy. Existing V2 Chamfer and STEP metrics must remain unchanged.

## Compatibility finding

The frozen DeepCAD requirements specify NumPy 1.18.1, while the probed cadfit-env has NumPy 2.2.6. The official script uses deprecated np.float; running it unmodified under NumPy 2.x is expected to fail before evaluation. No source modification was made.

DEEPCAD_METRIC_PROTOCOL_RECOVERED=PARTIAL
FORMAL_VAL1000_STARTED=NO
CURRENT_GATE=DEEPCAD_METRIC_DEFINITION_REQUIRES_FREEZE