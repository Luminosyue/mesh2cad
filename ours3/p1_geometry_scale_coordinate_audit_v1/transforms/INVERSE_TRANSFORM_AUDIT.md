# Inverse transform audit

Formal evaluator eval_cad_dsl.py divides nearest-surface distances by the GT bbox diagonal. It does not independently normalize or scale-align predictions. Predicted DSL is exported directly to STEP; no inverse transform back to GT world coordinates is present in the audited P1 path.
