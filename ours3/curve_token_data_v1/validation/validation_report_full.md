# Curve dataset validation (full)

```text
PARAMETER_EXTRACTION_PASS_RATE=100.0000%
GEOMETRY_RECONSTRUCTION_PASS_RATE=100.0000%
TOPOLOGY_VALID_RATE=100.0000%
```

`TOPOLOGY_VALID_RATE` measures whether the extracted incidence relations are
mutually consistent and every curve is bounded. Non-manifoldness is a property of
the source solid, not an extraction failure, so it is reported separately.

## Scope

- CAD validated: 2796
- CAD validation errors: 0
- curves checked: 172622
- curve-level failures: 0
- NaN/Inf occurrences: 0
- fully manifold CAD: 2710 (96.9242%)
- non-manifold edges (>2 faces), extracted with all face ids: 376

## Worst-case geometry errors (absolute, model units)

| metric | value |
|---|---|
| OCC rebuild point error (max) | 9.095e-13 |
| numpy (OCC-free) rebuild point error (max) | 9.095e-13 |
| endpoint error (max) | 8.882e-16 |
| tangent angular error (max) | 1.207e-06 deg |
| Chamfer, rebuilt vs OCC (max) | 1.303e-13 |
| sampled-polyline vs exact length (max rel) | 8.579e-03 |

The rows above measure the **exact float64 parameters** in `curves.json`.

## float32 sampled arrays

`curve_xyz` / `curve_xyz_normalized` are stored as float32, so their accuracy is
bounded by coordinate *magnitude*, not by part size. Some Fusion360 parts sit far
from the origin (world coordinates in the thousands with a small bbox), which costs
world-space precision that the recentred normalized copy does not pay.

| metric | value |
|---|---|
| sampled xyz vs OCC, world (max) | 9.925e-04 |
| sampled xyz vs OCC, normalized (max) | 7.684e-05 |
| largest absolute world coordinate | 2.743e+04 |

## Max OCC rebuild error by curve type

| curve type | max error |
|---|---|
| BSPLINE | 2.542e-13 |
| CIRCLE | 1.271e-13 |
| ELLIPSE | 3.580e-15 |
| LINE | 9.095e-13 |
