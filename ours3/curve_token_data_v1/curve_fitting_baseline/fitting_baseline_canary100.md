# Curve fitting baseline (canary100)

Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.
Errors ending in `_rel` are normalised by the object's bbox diagonal.
This baseline never contributes to the ground truth; it only measures how much
a classical fitter recovers, as the reference a Curve Encoder must beat.

## BSPLINE

- curves: 1407, fitted: 1407 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| max_residual_rel | 2.7602e-05 | 2.1983e-05 | 7.9190e-05 | 9.5373e-05 |
| rms_residual_rel | 1.7837e-05 | 1.4124e-05 | 4.4656e-05 | 6.5063e-05 |

## CIRCLE

- curves: 313, fitted: 313 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 1.4317e-05 | 1.0042e-08 | 1.0144e-04 | 7.1391e-04 |
| normal_angle_err_deg | 6.4373e-06 | 0.0000e+00 | 0.0000e+00 | 6.0886e-04 |
| radius_err_rel | 1.4312e-05 | 3.6405e-09 | 1.0143e-04 | 7.1390e-04 |
| radius_rel_err | 4.7205e-05 | 6.3805e-08 | 3.5202e-04 | 2.4777e-03 |
| rms_residual_rel | 6.2471e-09 | 6.5297e-09 | 9.8160e-09 | 4.9692e-08 |

## ELLIPSE

- curves: 358, fitted: 310 (86.59%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 5.8819e-02 | 4.4946e-04 | 2.8923e-01 | 2.2353e+00 |
| major_axis_angle_err_deg | 7.4119e+00 | 4.2505e-01 | 5.7743e+01 | 8.8711e+01 |
| major_radius_err_rel | 1.0170e-01 | 3.1997e-04 | 4.9439e-01 | 2.3445e+00 |
| minor_radius_err_rel | 3.3842e-02 | 3.2585e-04 | 2.5844e-01 | 7.4139e-01 |
| normal_angle_err_deg | 1.2390e-02 | 1.4335e-04 | 1.0084e-02 | 1.8046e+00 |
| rms_residual_rel | 8.8400e-06 | 6.1425e-09 | 3.9415e-08 | 6.1323e-04 |

## LINE

- curves: 6186, fitted: 6186 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| direction_angle_err_deg | 9.4343e-05 | 0.0000e+00 | 2.8345e-05 | 2.3979e-01 |
| endpoint_err_rel | 5.6898e-09 | 4.3795e-09 | 1.3880e-08 | 6.0889e-08 |
| length_rel_err | 6.1573e-06 | 4.1807e-08 | 3.4418e-06 | 1.6523e-02 |
| rms_residual_rel | 1.7378e-09 | 0.0000e+00 | 7.6630e-09 | 1.6109e-08 |
