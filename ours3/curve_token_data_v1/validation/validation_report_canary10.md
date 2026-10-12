# Curve dataset validation (canary10)

```text
PARAMETER_EXTRACTION_PASS_RATE=100.0000%
GEOMETRY_RECONSTRUCTION_PASS_RATE=100.0000%
TOPOLOGY_VALID_RATE=100.0000%
```

`TOPOLOGY_VALID_RATE` measures whether the extracted incidence relations are
mutually consistent and every curve is bounded. Non-manifoldness is a property of
the source solid, not an extraction failure, so it is reported separately.

## Scope

- CAD validated: 10
- CAD validation errors: 0
- curves checked: 3855
- curve-level failures: 0
- NaN/Inf occurrences: 0
- fully manifold CAD: 10 (100.0000%)
- non-manifold edges (>2 faces), extracted with all face ids: 0

## Worst-case geometry errors (absolute, model units)

| metric | value |
|---|---|
| OCC rebuild point error (max) | 2.247e-14 |
| numpy (OCC-free) rebuild point error (max) | 1.139e-13 |
| endpoint error (max) | 4.996e-16 |
| tangent angular error (max) | 8.538e-07 deg |
| Chamfer, rebuilt vs OCC (max) | 4.878e-15 |
| sampled-polyline vs exact length (max rel) | 4.589e-03 |

The rows above measure the **exact float64 parameters** in `curves.json`.

## float32 sampled arrays

`curve_xyz` / `curve_xyz_normalized` are stored as float32, so their accuracy is
bounded by coordinate *magnitude*, not by part size. Some Fusion360 parts sit far
from the origin (world coordinates in the thousands with a small bbox), which costs
world-space precision that the recentred normalized copy does not pay.

| metric | value |
|---|---|
| sampled xyz vs OCC, world (max) | 3.124e-05 |
| sampled xyz vs OCC, normalized (max) | 1.999e-06 |
| largest absolute world coordinate | 980 |

## Max OCC rebuild error by curve type

| curve type | max error |
|---|---|
| BSPLINE | 2.247e-14 |
| CIRCLE | 0.000e+00 |
| ELLIPSE | 3.553e-15 |
| LINE | 3.580e-15 |
