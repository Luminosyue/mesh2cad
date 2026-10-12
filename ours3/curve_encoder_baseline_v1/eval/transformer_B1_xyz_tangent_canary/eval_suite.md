# Eval suite — transformer / B1_xyz_tangent

- ckpt: `/data/home/cuiyuehan/project/mesh2cad/ours3/curve_encoder_baseline_v1/checkpoints/transformer_B1_xyz_tangent_canary/best.pt`
- split: test
- n: 17599

## Clean

- CURVE_TYPE_MACRO_F1 = 0.4099
- LINE_F1 = 0.9421
- CIRCLE_F1 = 0.6836
- ELLIPSE_F1 = 0.0138
- BSPLINE_F1 = 0.0000
- LINE_DIRECTION_ERROR: mean=5.965  med=2.145  p95=28.43  (n=15940)
- CIRCLE_NORMAL_ERROR: mean=56.17  med=60.13  p95=89.44  (n=1091)
- CIRCLE_RADIUS_ERROR: mean=6.143  med=0.985  p95=17.38  (n=1091)
- ELLIPSE_AXIS_ERROR: mean=64.12  med=68.45  p95=88.66  (n=36)
- RECON_CHAMFER: mean=0.257  med=0.06664  p95=0.7268  (n=17599)

## Noise robustness (partial=1.0)

| noise_rel | macro_F1 | CIRCLE_F1 | ELLIPSE_F1 | CIRCLE_NORMAL mean° | RECON_CHAMFER mean |
|---|---|---|---|---|---|
| 0 | 0.4099 | 0.6836 | 0.0138 | 56.16615295410156 | 0.25704561155489447 |
| 0.0001 | 0.4099 | 0.6836 | 0.0139 | 56.16637420654297 | 0.2569819932787742 |
| 0.001 | 0.4100 | 0.6839 | 0.0139 | 56.16880416870117 | 0.25553589318667536 |
| 0.005 | 0.4104 | 0.6852 | 0.0139 | 56.18301010131836 | 0.2519041493789477 |

## Partial-curve robustness (noise=0)

| frac | macro_F1 | LINE_F1 | CIRCLE_F1 | RECON_CHAMFER mean |
|---|---|---|---|---|
| 1 | 0.4099 | 0.9421 | 0.6836 | 0.25704561155489447 |
| 0.75 | 0.4057 | 0.9405 | 0.6656 | 0.2676169102941318 |
| 0.5 | 0.3986 | 0.9335 | 0.6471 | 0.3306931830720159 |
| 0.25 | 0.3299 | 0.9213 | 0.3865 | 0.4335214040655486 |

## Arc-coverage buckets (CIRCLE+ELLIPSE, clean)

| bucket | n | type_acc | recon_chamfer_mean |
|---|---|---|---|
| closed | 479 | 0.9979123173277662 | 3.290600619494666 |
| lt15 | 150 | 0.04 | 0.21341089045008024 |
| 15_45 | 129 | 0.023255813953488372 | 0.305668752929268 |
| 45_90 | 150 | 0.3333333333333333 | 0.7485903903593619 |
| gt90 | 219 | 0.8995433789954338 | 2.0397559348068555 |
