# Curve fitting baseline (full)

Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.
Errors ending in `_rel` are normalised by the object's bbox diagonal.
This baseline never contributes to the ground truth; it only measures how much
a classical fitter recovers, as the reference a Curve Encoder must beat.

## CIRCLE

- curves: 22, fitted: 22 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| center_err_rel | 5.9800e-09 | 3.6867e-09 | 2.0098e-08 | 2.5740e-08 |
| normal_angle_err_deg | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 |
| radius_err_rel | 2.3493e-09 | 5.4070e-10 | 6.6610e-09 | 1.8397e-08 |
| radius_rel_err | 4.8468e-08 | 3.7838e-09 | 2.6632e-07 | 2.9262e-07 |
| rms_residual_rel | 7.3762e-09 | 2.7352e-09 | 4.7581e-08 | 4.9692e-08 |

## LINE

- curves: 5510, fitted: 5510 (100.00%)

| metric | mean | median | P95 | max |
|---|---|---|---|---|
| direction_angle_err_deg | 5.6215e-05 | 0.0000e+00 | 3.9004e-05 | 7.0968e-02 |
| endpoint_err_rel | 6.3539e-09 | 4.8892e-09 | 1.7811e-08 | 6.0889e-08 |
| length_rel_err | 6.5960e-07 | 4.3081e-08 | 1.9646e-06 | 3.4142e-04 |
| rms_residual_rel | 2.7484e-09 | 9.5751e-10 | 1.0314e-08 | 2.2352e-08 |
