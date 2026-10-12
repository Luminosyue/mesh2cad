# Eval suite — pointnet / B1_xyz_tangent

- ckpt: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_encoder_baseline_v1/checkpoints/pointnet_B1_xyz_tangent_canary/best.pt`
- split: test
- n: 17599

## Clean

- CURVE_TYPE_MACRO_F1 = 0.3371
- LINE_F1 = 0.9161
- CIRCLE_F1 = 0.4323
- ELLIPSE_F1 = 0.0000
- BSPLINE_F1 = 0.0000
- LINE_DIRECTION_ERROR: mean=3.756  med=2.251  p95=10.59  (n=15940)
- CIRCLE_NORMAL_ERROR: mean=41.78  med=29.83  p95=88.92  (n=1091)
- CIRCLE_RADIUS_ERROR: mean=7.602  med=2.242  p95=19.18  (n=1091)
- ELLIPSE_AXIS_ERROR: mean=65.03  med=70.92  p95=85.94  (n=36)
- RECON_CHAMFER: mean=0.4275  med=0.07785  p95=1.553  (n=17599)

## Noise robustness (partial=1.0)

| noise_rel | macro_F1 | CIRCLE_F1 | ELLIPSE_F1 | CIRCLE_NORMAL mean° | RECON_CHAMFER mean |
|---|---|---|---|---|---|
| 0 | 0.3371 | 0.4323 | 0.0000 | 41.7779426574707 | 0.4275056113335983 |
| 0.0001 | 0.3371 | 0.4322 | 0.0000 | 41.77756118774414 | 0.42746359712118637 |
| 0.001 | 0.3369 | 0.4316 | 0.0000 | 41.76622772216797 | 0.4262809355792603 |
| 0.005 | 0.3351 | 0.4265 | 0.0000 | 41.642635345458984 | 0.42410987341210576 |

## Partial-curve robustness (noise=0)

| frac | macro_F1 | LINE_F1 | CIRCLE_F1 | RECON_CHAMFER mean |
|---|---|---|---|---|
| 1 | 0.3371 | 0.9161 | 0.4323 | 0.4275056113335983 |
| 0.75 | 0.3402 | 0.9224 | 0.4383 | 0.4314692236577928 |
| 0.5 | 0.3536 | 0.9380 | 0.4765 | 0.4517467104921345 |
| 0.25 | 0.3423 | 0.9495 | 0.4195 | 0.49201098684848277 |

## Arc-coverage buckets (CIRCLE+ELLIPSE, clean)

| bucket | n | type_acc | recon_chamfer_mean |
|---|---|---|---|
| closed | 479 | 0.9979123173277662 | 3.934700256528523 |
| lt15 | 150 | 0.22666666666666666 | 0.3165599092841148 |
| 15_45 | 129 | 0.3798449612403101 | 0.5799089941925318 |
| 45_90 | 150 | 0.6 | 1.1106440739581982 |
| gt90 | 219 | 0.8858447488584474 | 2.5151792995665714 |
