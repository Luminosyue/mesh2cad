# Eval suite — pointnet / B1_xyz_tangent

- ckpt: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_encoder_baseline_v1/checkpoints/pointnet_B1_xyz_tangent_full/best.pt`
- split: test
- n: 17599

## Clean

- CURVE_TYPE_MACRO_F1 = 0.6858
- LINE_F1 = 0.9916
- CIRCLE_F1 = 0.8610
- ELLIPSE_F1 = 0.0260
- BSPLINE_F1 = 0.8647
- LINE_DIRECTION_ERROR: mean=1.508  med=0.7289  p95=4.541  (n=15940)
- CIRCLE_NORMAL_ERROR: mean=29.4  med=8.846  p95=88.45  (n=1091)
- CIRCLE_RADIUS_ERROR: mean=3.99  med=0.2174  p95=16.63  (n=1091)
- ELLIPSE_AXIS_ERROR: mean=59.34  med=68.79  p95=84.92  (n=36)
- RECON_CHAMFER: mean=0.09101  med=0.02307  p95=0.1831  (n=17599)

## Noise robustness (partial=1.0)

| noise_rel | macro_F1 | CIRCLE_F1 | ELLIPSE_F1 | CIRCLE_NORMAL mean° | RECON_CHAMFER mean |
|---|---|---|---|---|---|
| 0 | 0.6858 | 0.8610 | 0.0260 | 29.404478073120117 | 0.09100933635474112 |
| 0.0001 | 0.6858 | 0.8610 | 0.0260 | 29.40444564819336 | 0.09097273266148787 |
| 0.001 | 0.6863 | 0.8615 | 0.0260 | 29.38890266418457 | 0.0910764803869255 |
| 0.005 | 0.6863 | 0.8601 | 0.0263 | 29.2083740234375 | 0.10494650063374868 |

## Partial-curve robustness (noise=0)

| frac | macro_F1 | LINE_F1 | CIRCLE_F1 | RECON_CHAMFER mean |
|---|---|---|---|---|
| 1 | 0.6858 | 0.9916 | 0.8610 | 0.09100933635474112 |
| 0.75 | 0.6828 | 0.9910 | 0.8456 | 0.16920767930739591 |
| 0.5 | 0.6575 | 0.9892 | 0.8087 | 0.27055719013832996 |
| 0.25 | 0.5361 | 0.9778 | 0.7337 | 0.3984637272916385 |

## Arc-coverage buckets (CIRCLE+ELLIPSE, clean)

| bucket | n | type_acc | recon_chamfer_mean |
|---|---|---|---|
| closed | 479 | 0.9979123173277662 | 1.3115497047007707 |
| lt15 | 150 | 0.06666666666666667 | 0.0634054827131331 |
| 15_45 | 129 | 0.49612403100775193 | 0.1432042090409948 |
| 45_90 | 150 | 0.9733333333333334 | 0.3682685914138953 |
| gt90 | 219 | 0.9908675799086758 | 1.1521985136210646 |
