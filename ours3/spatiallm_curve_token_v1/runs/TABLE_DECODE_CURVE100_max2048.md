# Curve100 overfit decode — B0 / B1 / M2

Same 100 CADs the arms memorized. CE already ~0 for all; this table asks whether
generation actually recovers DSL / geometry.

| arm | n | exact | op F1 | op recall | pred/gt ops | under-gen | STEP valid | Chamfer↓ | H95↓ | EOS | MAX_LEN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 100 | 0.950 | 0.953 | 0.958 | 0.96 | 0.050 | 0.960 | 0.0416 | 0.0702 | 0.97 | 0.03 |
| B1 | 100 | 0.860 | 0.930 | 0.930 | 0.93 | 0.070 | 0.920 | 0.0423 | 0.0689 | 0.94 | 0.06 |
| M2 | 100 | 0.950 | 0.960 | 0.960 | 0.96 | 0.040 | 0.950 | 0.0404 | 0.0662 | 0.96 | 0.04 |

