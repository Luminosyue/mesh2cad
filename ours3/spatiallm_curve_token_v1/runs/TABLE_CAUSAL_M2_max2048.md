# M2 free causal test (frozen checkpoint, no retrain)

Question: on the overfit 100 CADs, does the model actually read curve tokens?

| variant | n | exact↑ | op F1↑ | STEP↑ | under-gen↓ | Chamfer↓ | MAX_LEN |
|---|---:|---:|---:|---:|---:|---:|---:|
| M2-correct | 100 | 0.950 | 0.960 | 0.950 | 0.040 | 0.0404 | 0.04 |
| M2-drop | 100 | 0.170 | 0.398 | 0.420 | 0.620 | 0.1098 | 0.02 |
| M2-zero | 100 | 0.470 | 0.547 | 0.820 | 0.450 | 0.0954 | 0.02 |
| M2-shuffle | 100 | 0.270 | 0.478 | 0.620 | 0.480 | 0.0864 | 0.11 |

## Reading

- If **drop / zero / shuffle ≈ correct**: surface stream carries the memorization;
  curve tokens are not causally used (Gate can still pass; do not claim curve prior is learned).
- If **shuffle / zero / drop collapse**: model depends on the curve stream content.

