# Eval suite — transformer / B1_xyz_tangent

- ckpt: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_encoder_baseline_v1/checkpoints/transformer_B1_xyz_tangent_full/best.pt`
- split: test
- n: 17599

## Clean

- CURVE_TYPE_MACRO_F1 = 0.6559
- LINE_F1 = 0.9894
- CIRCLE_F1 = 0.8450
- ELLIPSE_F1 = 0.0206
- BSPLINE_F1 = 0.7687
- LINE_DIRECTION_ERROR: mean=1.032  med=0.8026  p95=2.3  (n=15940)
- CIRCLE_NORMAL_ERROR: mean=25.94  med=7.366  p95=89.45  (n=1091)
- CIRCLE_RADIUS_ERROR: mean=3.709  med=0.3729  p95=12.92  (n=1091)
- ELLIPSE_AXIS_ERROR: mean=55.5  med=63.67  p95=84.94  (n=36)
- RECON_CHAMFER: mean=0.07037  med=0.02216  p95=0.2572  (n=17599)

## Noise robustness (partial=1.0)

| noise_rel | macro_F1 | CIRCLE_F1 | ELLIPSE_F1 | CIRCLE_NORMAL mean° | RECON_CHAMFER mean |
|---|---|---|---|---|---|
| 0 | 0.6559 | 0.8450 | 0.0206 | 25.943824768066406 | 0.07036541910692352 |
| 0.0001 | 0.6559 | 0.8450 | 0.0206 | 25.94373893737793 | 0.07031883875395897 |
| 0.001 | 0.6562 | 0.8444 | 0.0211 | 25.94500732421875 | 0.07101826555469963 |
| 0.005 | 0.6554 | 0.8457 | 0.0172 | 25.978670120239258 | 0.08677671389300039 |

## Partial-curve robustness (noise=0)

| frac | macro_F1 | LINE_F1 | CIRCLE_F1 | RECON_CHAMFER mean |
|---|---|---|---|---|
| 1 | 0.6559 | 0.9894 | 0.8450 | 0.07036541910692352 |
| 0.75 | 0.4725 | 0.9127 | 0.6291 | 0.1591462496963865 |
| 0.5 | 0.3735 | 0.8157 | 0.4924 | 0.2873397395406364 |
| 0.25 | 0.2589 | 0.5730 | 0.3501 | 0.44656527741867785 |

## Arc-coverage buckets (CIRCLE+ELLIPSE, clean)

| bucket | n | type_acc | recon_chamfer_mean |
|---|---|---|---|
| closed | 479 | 0.9979123173277662 | 0.5551159256808693 |
| lt15 | 150 | 0.04666666666666667 | 0.08237549318621556 |
| 15_45 | 129 | 0.5503875968992248 | 0.17463995234737562 |
| 45_90 | 150 | 0.94 | 0.3656753670920928 |
| gt90 | 219 | 0.9908675799086758 | 0.8641544102295621 |
