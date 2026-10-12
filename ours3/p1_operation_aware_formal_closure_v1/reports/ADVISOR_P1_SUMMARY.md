# Advisor Summary

P1 reaches Exact `0.098`, Op-F1 `0.8119`, Parse `0.963`, and STEP export `0.958` on VAL1000.

Compared with A3, P1 improves Op-F1 by `0.0729`, Exact by `0.052`, Parse by `0.059`, and STEP export by `0.064`. It also exceeds A1 in Op-F1 by `0.0541`.

P1 also reduces MaxLen from `0.067` to `0.010` and UnderGen from `0.258` to `0.206`.

Operation-level audits identify the repaired/preserved/regressed operation categories in `operation_breakdown/P1_VS_A3_OPERATION_DELTA.csv`; the transition table separates missing-to-correct and wrong-type-to-correct rescues.

Geometry is broadly preserved: P1 has better Chamfer median, H95, Volume error, and geometry-valid coverage, while Chamfer mean remains higher because of outliers. The remaining risk is local parameter, placement, direction, or scale error.

P2 is deferred pending parameter/outlier review. TEST remains blind and no new training or decode was run.
