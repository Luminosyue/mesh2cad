# CURVE_ENCODER_BASELINE_V1 — strict 6-way table (TEST)

Implementation: `scripts/curve_encoder_baseline_v1 (canonical for this table)`  
Split: `frozen_v1` · metrics on **test** · config locked as above.

Do **not** mix numbers from `scripts/curve_encoder_v1` (legacy B0/B1) into this table.

## Test metrics

| Exp | Encoder | Input | Macro F1 | Bal Acc | LINE F1 | CIRCLE F1 | ELLIPSE F1 | BSPLINE F1 | Chamfer | LINE dir° | CIRCLE n° |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P0 | PointNet | xyz | 0.397 | 0.619 | 0.894 | 0.229 | 0.006 | 0.458 | 0.588 | 54.9 | 31.2 |
| P1 | PointNet | xyz+tan | 0.444 | 0.679 | 0.939 | 0.354 | 0.019 | 0.464 | 0.572 | 36.2 | 29.1 |
| P2 | PointNet | xyz+tan+s | 0.487 | 0.753 | 0.950 | 0.407 | 0.162 | 0.431 | 0.464 | 21.8 | 23.9 |
| T0 | Transformer | xyz | 0.396 | 0.626 | 0.905 | 0.272 | 0.005 | 0.404 | 0.564 | 53.4 | 34.6 |
| T1 | Transformer | xyz+tan | 0.463 | 0.720 | 0.948 | 0.410 | 0.067 | 0.428 | 0.564 | 21.3 | 33.2 |
| T2 | Transformer | xyz+tan+s | 0.448 | 0.702 | 0.943 | 0.401 | 0.041 | 0.408 | 0.585 | 25.7 | 30.9 |

## Config lock
- points=32, token_dim=256, split=frozen_v1
- epochs=30, samples_per_epoch=65536, batch=256
- type-aware train sampling; val/test natural CAD mix
- s: for uniform_abscissa (>99.8% curves): linspace(0,1,32); else cumulative chord length on xyz polyline — NEVER raw OCC curve_u

## Quick reads
- P2−P1 Macro F1 = +0.043, Chamfer Δ = -0.108
- T1−P1 Macro F1 = +0.019
- T2−P2 Macro F1 = -0.039

## Per-class pattern (test, best PointNet P2 / best Transformer T1)
- P2: LINE=0.950 CIRCLE=0.407 ELLIPSE=0.162 BSPLINE=0.431
- T1: LINE=0.948 CIRCLE=0.410 ELLIPSE=0.067 BSPLINE=0.428
- P1: LINE=0.939 CIRCLE=0.354 ELLIPSE=0.019 BSPLINE=0.464
