# Dora Edge Ablation — Canonical Train100 Val (n=19)

## Summary

| Method | exact | op_recall | op_f1 | parse | STEP | Chamfer | H95 | vol_err |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 6ch Base | 0.0000 | 0.1491 | 0.1637 | 0.6316 | 0.6316 | 0.0624 | 0.1587 | 0.5689 |
| 7ch Zero | 0.0000 | 0.2368 | 0.2076 | 0.7895 | 0.7895 | 0.0486 | 0.1574 | 0.4033 |
| 7ch Shuffle | 0.0000 | 0.2105 | 0.2076 | 0.5789 | 0.5789 | 0.0818 | 0.2058 | 0.3599 |
| 7ch Real | 0.0000 | 0.2544 | 0.2314 | 0.7368 | 0.7368 | 0.0465 | 0.1417 | 0.4722 |

## Key comparison: Zero vs Shuffle vs Real

- **mean_op_recall**: Zero=0.23684210526315788 Shuffle=0.21052631578947367 Real=0.25438596491228066
- **mean_chamfer_norm**: Zero=0.04856156841022159 Shuffle=0.08179859559702705 Real=0.04653615877332994
- **step_valid_rate**: Zero=0.7894736842105263 Shuffle=0.5789473684210527 Real=0.7368421052631579
