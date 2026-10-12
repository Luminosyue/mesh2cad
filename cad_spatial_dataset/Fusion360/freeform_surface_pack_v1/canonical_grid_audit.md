# Canonical grid audit (4×4 / 6×6 / 8×8)

- n_samples = **729**
- n_failed = **0**
- recommend_canonical_grid = **4x4**

bspline_ctrl = UV-grid samples used as cubic clamped BSpline poles (matches current pack decoder target semantics). bilinear_interp = densify UV samples by bilinear interpolation (representation lower bound).

| Canonical grid | GT refit Chamfer (rel, median) | Hausdorff95 (rel, median) | Normal consistency ↑ | Bilinear Chamfer (rel) |
|---|---:|---:|---:|---:|
| 4x4 | 0.000292322 | 0.000545545 | 0.9984 | 8.39763e-05 |
| 6x6 | 0.0070141 | 0.0230676 | 0.9999 | 2.98318e-05 |
| 8x8 | 0.00766165 | 0.0315346 | 1.0000 | 1.51195e-05 |

**Recommendation:** use `4x4` as the first reconstruction target (capacity bottleneck).
