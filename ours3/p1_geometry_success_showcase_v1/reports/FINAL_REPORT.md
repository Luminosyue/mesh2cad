# P1 Geometry Success Showcase

CURRENT_GATE = P1_GEOMETRY_SUCCESS_CASES_INSUFFICIENT

Formal EXACT9998 VAL1000 mining found four numerically strong candidates satisfying P1 parse, STEP export/reload, and finite Chamfer/H95. However, under the required shared GT bbox transform, the rendered predictions for several candidates are visibly tiny or displaced relative to GT. Therefore fewer than four cases can be honestly claimed as simultaneous structure-and-geometry visual successes.

Main numerical candidates rendered for audit: deepcad__0062_00623202, deepcad__0008_00080235, deepcad__0002_00024054, fusion360__41970_24ba0c1b_0009. Backups are recorded in `selection/BACKUP_4CASE.csv`. The showcase image is retained as an audit artifact, not a claim of visual success.

No TEST1000, Holdout958, P1-v2 intermediate checkpoint, retraining, re-decoding, prediction modification, or evaluator modification was used. Do not continue trying to rescue old P1 through rendering; wait for the formal P1-v2 result.
