# Curve100 overfit decode — B0 / B1 / M2 (max_new_tokens=4096)

Same 100 CADs the arms memorized. **Main eval budget is 4096**
(separates output-length hard caps from content failures).
Appendix: `TABLE_DECODE_CURVE100_max2048.md` / `decode_max2048/`.

## All 100

| arm | n | exact | op F1 | op recall | pred/gt ops | under-gen | STEP valid | Chamfer↓ | H95↓ | EOS | MAX_LEN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 100 | 0.940 | 0.953 | 0.958 | 0.96 | 0.050 | 0.960 | 0.0420 | 0.0703 | 0.97 | 0.03 |
| B1 | 100 | 0.900 | 0.921 | 0.922 | 0.93 | 0.070 | 0.930 | 0.0403 | 0.0687 | 0.98 | 0.02 |
| M2 | 100 | 0.950 | 0.960 | 0.960 | 0.96 | 0.040 | 0.950 | 0.0404 | 0.0662 | 0.96 | 0.04 |

## Exclude GT length > 2048 (n=96)

Drops the 4 CADs whose GT DSL exceeds the old 2048 generation budget
(`deepcad__0029_00298546`, `fusion360__23658_*`, `fusion360__36066_*`,
`fusion360__38288_*`). Remaining failures are content, not length-cap.

| arm | n | exact | op F1 | op recall | pred/gt ops | under-gen | STEP valid | Chamfer↓ | H95↓ | EOS | MAX_LEN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 96 | 0.979 | 0.990 | 0.990 | 0.99 | 0.010 | 0.990 | 0.0418 | 0.0692 | 1.00 | 0.00 |
| B1 | 96 | 0.938 | 0.958 | 0.958 | 0.97 | 0.031 | 0.958 | 0.0391 | 0.0662 | 0.99 | 0.01 |
| M2 | 96 | 0.990 | 1.000 | 1.000 | 1.00 | 0.000 | 0.990 | 0.0404 | 0.0662 | 1.00 | 0.00 |

## Appendix — previous max_new_tokens=2048 (all 100)

| arm | n | exact | op F1 | op recall | pred/gt ops | under-gen | STEP valid | Chamfer↓ | H95↓ | EOS | MAX_LEN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 100 | 0.950 | 0.953 | 0.958 | 0.96 | 0.050 | 0.960 | 0.0416 | 0.0702 | 0.97 | 0.03 |
| B1 | 100 | 0.860 | 0.930 | 0.930 | 0.93 | 0.070 | 0.920 | 0.0423 | 0.0689 | 0.94 | 0.06 |
| M2 | 100 | 0.950 | 0.960 | 0.960 | 0.96 | 0.040 | 0.950 | 0.0404 | 0.0662 | 0.96 | 0.04 |

