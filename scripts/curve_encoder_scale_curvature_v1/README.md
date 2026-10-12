# CURVE_ENCODER_SCALE_CURVATURE_V1

Disentangle **shape** vs **scale** to kill the long-LINE → CIRCLE shortcut.

| Exp | Shape | Scale | Curvature |
| --- | --- | --- | --- |
| C0 | object xyz+tan+s (P2 ref) | implicit | no |
| C1 | curve-local xyz+tan+s | none | no |
| C2 | curve-local | log(length) branch | no |
| C3 | curve-local | log(length) branch | turn/chord + Straightness Head |

Frozen: PointNet, 32 pts, 256-D, `frozen_v1`, type-aware sampler, same loss/budget. **No oversampling.**

Primary metrics: `LINE_TO_CIRCLE_FP`, `TOP_DECILE_LINE_TO_CIRCLE_FP`. Guardrail: CIRCLE recall.

```bash
bash scripts/curve_encoder_scale_curvature_v1/run_all.sh 5
```

Outputs: `ours3/curve_encoder_scale_curvature_v1/runs/{C0..C3}_frozen_v1/`
