# Fitter decision path (read-only source audit)

Source: `scripts/dora_fitted_curve_dataset_v1.py`, `process()`. Each maximal chain from `extract_chains()` is fitted as one primitive:

1. `linefit(p)` is always attempted.
2. If line RMS / object diagonal > `FIT_TOL_REL=0.005` and >=4 points: `circlefit(p, closed_loop)`.
3. If still failing and >=6 points: `ellipsefit(p, closed_loop)`.
4. If still failing: `splinefit(p, closed_loop, diag)`.

`extract_chains()` stops a walk only at degree != 2 vertices; any degree-2 sequence is retained as one chain. The primitive acceptance is only RMS / object diagonal. There is no explicit radius/extent limit, no fitted-to-chain unsupported-region guard, no sweep-support check, and no semantic guard for a chain that crosses an unobserved geometric boundary. Thus a large circle/ellipse can be accepted when its sparse ordered input points have small residual under the algebraic fit, even though much of the sampled primitive has no chain support. This report does not modify those rules.
