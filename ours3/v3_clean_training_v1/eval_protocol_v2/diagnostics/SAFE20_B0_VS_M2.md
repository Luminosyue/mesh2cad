# SAFE20 B0 vs M2

Status: **TRAIN_SELF_DECODE_DIAGNOSIS**, not held-out/generalization.

| Metric | B0 epoch8 | M2 epoch15 |
|---|---:|---:|
| eos | 17/20 | 19/20 |
| hit_cap | 3/20 | 1/20 |
| has_result | 17/20 | 19/20 |
| parse_pass | 17/20 | 16/20 |
| exec_pass | 17/20 | 16/20 |
| step_write_pass | 17/20 | 16/20 |
| step_reload_pass | 17/20 | 16/20 |

B0 token median/p90/max: {'median': 113.5, 'p90': 4096.0, 'max': 4096}
M2 token median/p90/max: {'median': 335.5, 'p90': 2180.0000000000005, 'max': 4096}

STEP=0 root cause: PRIOR_EVALUATOR_ENVIRONMENT_MISSING_CADQUERY; corrected executor shows STEP reload passes.
