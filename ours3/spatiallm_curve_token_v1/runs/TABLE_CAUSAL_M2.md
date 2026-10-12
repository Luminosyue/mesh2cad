# M2 free causal test (frozen checkpoint, no retrain)

Question: on the overfit 100 CADs, does the model actually read curve tokens?

Budgets: **correct / shuffle re-run at max_new_tokens=4096**; drop / zero
kept from the 2048 archive when not re-run (gap already large).

| variant | budget | n | exact↑ | op F1↑ | STEP↑ | under-gen↓ | Chamfer↓ | MAX_LEN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M2-correct | 4096 | 100 | 0.950 | 0.960 | 0.950 | 0.040 | 0.0404 | 0.04 |
| M2-correct (GT≤2048) | 4096 | 96 | 0.990 | 1.000 | 0.990 | 0.000 | 0.0404 | 0.00 |
| M2-drop | 2048† | 100 | 0.170 | 0.398 | 0.420 | 0.620 | 0.1098 | 0.02 |
| M2-zero | 2048† | 100 | 0.470 | 0.547 | 0.820 | 0.450 | 0.0954 | 0.02 |
| M2-shuffle | 4096 | 100 | 0.270 | 0.442 | 0.590 | 0.510 | 0.0865 | 0.07 |
| M2-shuffle (GT≤2048) | 4096 | 96 | 0.281 | 0.460 | 0.615 | 0.490 | 0.0865 | 0.07 |

† from `causal_m2_max2048/` (not re-decoded at 4096).

## Reading

- If **drop / zero / shuffle ≈ correct**: surface stream carries the memorization;
  curve tokens are not causally used (Gate can still pass; do not claim curve prior is learned).
- If **shuffle / zero / drop collapse**: model depends on the curve stream content.

Full 2048 causal table: `TABLE_CAUSAL_M2_max2048.md`.

