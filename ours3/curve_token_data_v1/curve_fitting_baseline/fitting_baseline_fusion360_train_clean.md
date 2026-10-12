# Curve fitting baseline (fusion360_train_clean)

Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.
Errors ending in `_rel` are normalised by the object's bbox diagonal.
This baseline never contributes to the ground truth; it only measures how much
a classical fitter recovers, as the reference a Curve Encoder must beat.

## BSPLINE

- curves: 438, fitted: 438 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| max_residual_rel | 3.5149e-05 | 3.1665e-05 | 9.0778e-05 | 9.9306e-05 |
| rms_residual_rel | 2.0712e-05 | 1.9489e-05 | 4.6145e-05 | 6.2767e-05 |

## CIRCLE

- curves: 1327, fitted: 1327 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 5.9788e-07 | 4.9446e-09 | 9.7107e-07 | 1.4249e-04 |
| normal_angle_err_deg | 1.5297e-06 | 0.0000e+00 | 0.0000e+00 | 6.0886e-04 |
| radius_err_rel | 5.9553e-07 | 2.6449e-09 | 9.6736e-07 | 1.4246e-04 |
| radius_rel_err | 5.3882e-06 | 4.2469e-08 | 5.3929e-06 | 7.2915e-04 |
| rms_residual_rel | 6.8502e-09 | 5.0978e-09 | 1.4929e-08 | 9.0143e-08 |

## ELLIPSE

- curves: 54, fitted: 47 (87.04%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 1.5337e-01 | 3.0387e-02 | 9.4606e-01 | 2.2353e+00 |
| major_axis_angle_err_deg | 1.8567e+01 | 1.5246e+00 | 8.4889e+01 | 8.8711e+01 |
| major_radius_err_rel | 1.8244e-01 | 2.0381e-02 | 1.2173e+00 | 2.3445e+00 |
| minor_radius_err_rel | 8.1656e-02 | 2.9414e-02 | 3.5688e-01 | 6.3181e-01 |
| normal_angle_err_deg | 9.3691e-04 | 1.3011e-04 | 8.6217e-04 | 3.1942e-02 |
| rms_residual_rel | 4.4057e-06 | 9.0537e-09 | 1.0340e-08 | 2.0113e-04 |

## LINE

- curves: 5291, fitted: 5291 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| direction_angle_err_deg | 3.7702e-06 | 0.0000e+00 | 1.8351e-05 | 6.0408e-04 |
| endpoint_err_rel | 7.3046e-09 | 4.5195e-09 | 2.2923e-08 | 1.8082e-07 |
| length_rel_err | 5.7660e-07 | 1.1033e-08 | 2.6524e-06 | 2.1060e-04 |
| rms_residual_rel | 1.4753e-09 | 0.0000e+00 | 6.7731e-09 | 1.0494e-07 |
