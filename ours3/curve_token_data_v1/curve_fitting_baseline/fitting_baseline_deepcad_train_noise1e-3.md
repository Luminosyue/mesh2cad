# Curve fitting baseline (deepcad_train_noise1e-3)

Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.
Errors ending in `_rel` are normalised by the object's bbox diagonal.
This baseline never contributes to the ground truth; it only measures how much
a classical fitter recovers, as the reference a Curve Encoder must beat.

## CIRCLE

- curves: 266, fitted: 266 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 1.2522e-02 | 4.4701e-04 | 2.2418e-02 | 6.7212e-01 |
| normal_angle_err_deg | 2.9689e+00 | 4.7432e-01 | 1.2111e+01 | 8.5361e+01 |
| radius_err_rel | 1.2007e-02 | 2.1491e-04 | 1.5628e-02 | 6.6995e-01 |
| radius_rel_err | 8.6766e-02 | 3.8695e-03 | 5.5167e-01 | 9.9711e-01 |
| rms_residual_rel | 1.3616e-03 | 1.3168e-03 | 1.6316e-03 | 2.1160e-03 |

## LINE

- curves: 23318, fitted: 23318 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| direction_angle_err_deg | 3.3709e+00 | 9.1927e-01 | 1.3090e+01 | 8.9752e+01 |
| endpoint_err_rel | 1.0154e-03 | 9.1758e-04 | 2.1564e-03 | 4.3630e-03 |
| length_rel_err | 1.2372e+01 | 1.7673e-02 | 5.4806e-01 | 1.3885e+04 |
| rms_residual_rel | 1.3516e-03 | 1.3540e-03 | 1.5575e-03 | 1.8631e-03 |
