# Curve fitting baseline (deepcad_train_clean)

Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.
Errors ending in `_rel` are normalised by the object's bbox diagonal.
This baseline never contributes to the ground truth; it only measures how much
a classical fitter recovers, as the reference a Curve Encoder must beat.

## CIRCLE

- curves: 266, fitted: 266 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 1.4358e-06 | 1.8190e-09 | 3.4476e-08 | 3.7807e-04 |
| normal_angle_err_deg | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 |
| radius_err_rel | 1.4330e-06 | 7.5221e-10 | 2.0609e-08 | 3.7806e-04 |
| radius_rel_err | 2.2373e-06 | 9.4485e-09 | 9.8282e-07 | 5.6268e-04 |
| rms_residual_rel | 6.0244e-09 | 4.1731e-09 | 1.2729e-08 | 5.5624e-08 |

## LINE

- curves: 23318, fitted: 23318 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| direction_angle_err_deg | 3.5863e-04 | 0.0000e+00 | 3.1150e-05 | 7.2753e-01 |
| endpoint_err_rel | 7.2921e-09 | 4.4464e-09 | 2.2808e-08 | 1.9836e-07 |
| length_rel_err | 1.7661e-05 | 3.8762e-08 | 1.8258e-06 | 3.4821e-02 |
| rms_residual_rel | 3.5462e-09 | 9.8060e-10 | 1.3830e-08 | 1.1742e-07 |
