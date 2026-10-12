# Curve fitting baseline (canary10)

Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.
Errors ending in `_rel` are normalised by the object's bbox diagonal.
This baseline never contributes to the ground truth; it only measures how much
a classical fitter recovers, as the reference a Curve Encoder must beat.

## BSPLINE

- curves: 913, fitted: 913 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| max_residual_rel | 2.4866e-05 | 1.7574e-05 | 6.5525e-05 | 9.5373e-05 |
| rms_residual_rel | 1.6292e-05 | 1.1426e-05 | 4.1631e-05 | 6.5063e-05 |

## CIRCLE

- curves: 142, fitted: 142 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 2.3701e-05 | 3.0552e-08 | 1.7756e-04 | 7.1391e-04 |
| normal_angle_err_deg | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 |
| radius_err_rel | 2.3698e-05 | 2.3614e-08 | 1.7756e-04 | 7.1390e-04 |
| radius_rel_err | 8.2423e-05 | 4.0270e-07 | 6.1616e-04 | 2.4777e-03 |
| rms_residual_rel | 6.5061e-09 | 7.6847e-09 | 1.1057e-08 | 1.6188e-08 |

## ELLIPSE

- curves: 259, fitted: 216 (83.40%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 5.8655e-02 | 1.2654e-03 | 2.9654e-01 | 1.2254e+00 |
| major_axis_angle_err_deg | 6.4425e+00 | 7.4413e-01 | 3.5547e+01 | 8.5361e+01 |
| major_radius_err_rel | 1.0324e-01 | 9.1519e-04 | 5.9405e-01 | 2.3443e+00 |
| minor_radius_err_rel | 3.5918e-02 | 7.3411e-04 | 2.4358e-01 | 7.4139e-01 |
| normal_angle_err_deg | 1.7486e-02 | 2.6524e-04 | 1.4888e-02 | 1.8046e+00 |
| rms_residual_rel | 8.9142e-06 | 5.2880e-09 | 4.6611e-07 | 4.6891e-04 |

## LINE

- curves: 2541, fitted: 2541 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| direction_angle_err_deg | 8.0066e-06 | 0.0000e+00 | 3.0617e-05 | 7.6457e-04 |
| endpoint_err_rel | 6.0690e-09 | 4.3291e-09 | 1.4483e-08 | 3.0755e-08 |
| length_rel_err | 7.7927e-07 | 5.0982e-08 | 3.8639e-06 | 3.0521e-05 |
| rms_residual_rel | 1.1811e-09 | 0.0000e+00 | 5.4844e-09 | 1.0199e-08 |
