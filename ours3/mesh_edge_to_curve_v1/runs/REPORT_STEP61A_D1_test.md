# Step 6.1A — mesh sharp edge → Curve Token (oracle grouping, test)

Frozen C2 backbone with D1 heads, seeds [0, 1, 2] (mean ± std over seeds). All arms evaluate the **same 12330 curves** with the same checkpoints; only the 32 input points differ.

- Oracle (to be replaced in 6.1B): grouping (which curve a mesh segment belongs to); ordering (projection onto the GT polyline)
- Purely mesh-derived: point positions; point spacing; tangents

## Coverage: which B-Rep curves survive the mesh path

A B-Rep edge whose dihedral is below the 30° sharp threshold cannot appear in the mesh sharp-edge set at all, so it is not a detection failure — it is out of scope for an edge-based pipeline.

| type | GT curves | B-Rep sharp | recovered | recall of all | recall of B-Rep sharp |
|---|---|---|---|---|---|
| BSPLINE | 132 | 132 | 132 | 100.0% | 100.0% |
| CIRCLE | 503 | 501 | 482 | 95.8% | 96.2% |
| ELLIPSE | 26 | 26 | 26 | 100.0% | 100.0% |
| LINE | 16486 | 12476 | 11690 | 70.9% | 93.6% |
| **all** | 17147 | — | 12330 | 71.9% | — |

Mesh sharp segments: 26997 total, 26995 assigned to a B-Rep curve (99.99%).

## Step 6.2 — how the mesh input differs from the exact input

Canonical frame (bbox diagonal = 6.0).

| type | n | max position dev (med / p90) | tangent angle° (med / p90) | spacing CV B-Rep / mesh | mesh points per curve (med) |
|---|---|---|---|---|---|
| LINE | 11690 | 0.00000 / 0.00000 | 0.000 / 0.014 | 0.0000 / 0.0000 | 2 |
| CIRCLE | 482 | 0.00537 / 0.02916 | 0.623 / 1.393 | 0.0000 / 0.0007 | 37 |
| ELLIPSE | 26 | 0.00019 / 0.00041 | 0.545 / 0.545 | 0.0000 / 0.0009 | 24 |
| BSPLINE | 132 | 0.00243 / 0.01396 | 1.220 / 1.493 | 0.0000 / 0.0006 | 6 |

## Model behaviour on the recovered subset

### Classification

| metric | B-Rep exact (train dist.) | B-Rep xyz + FD tangent | Mesh sharp edge (oracle group) |
|---|---|---|---|
| Macro F1 | 0.6994 ± 0.0104 | 0.6930 ± 0.0078 | 0.6948 ± 0.0065 |
| Bal Acc | 0.7029 ± 0.0035 | 0.7044 ± 0.0048 | 0.6944 ± 0.0060 |
| LINE F1 | 0.9958 ± 0.0007 | 0.9944 ± 0.0006 | 0.9954 ± 0.0007 |
| CIRCLE F1 | 0.9119 ± 0.0073 | 0.8859 ± 0.0051 | 0.9105 ± 0.0083 |
| ELLIPSE F1 | 0.1238 ± 0.0275 | 0.1192 ± 0.0254 | 0.1270 ± 0.0276 |
| BSPLINE F1 | 0.7660 ± 0.0316 | 0.7724 ± 0.0278 | 0.7462 ± 0.0314 |

### Geometry / parameters

| metric | B-Rep exact (train dist.) | B-Rep xyz + FD tangent | Mesh sharp edge (oracle group) |
|---|---|---|---|
| Chamfer (med) | 0.00945 ± 0.00281 | 0.00946 ± 0.00281 | 0.00946 ± 0.00279 |
| LINE dir° | 3.006 ± 1.266 | 3.010 ± 1.263 | 3.008 ± 1.264 |
| LINE len rel | 0.0186 ± 0.0122 | 0.0186 ± 0.0122 | 0.0186 ± 0.0122 |
| CIRCLE n° | 1.213 ± 0.224 | 1.217 ± 0.216 | 1.274 ± 0.234 |
| CIRCLE r rel | 0.0210 ± 0.0104 | 0.0213 ± 0.0099 | 0.0247 ± 0.0127 |
| ELLIPSE maj° | 18.77 ± 7.27 | 18.55 ± 6.65 | 18.53 ± 6.48 |
| BSPL deg acc | 0.912 ± 0.020 | 0.907 ± 0.013 | 0.909 ± 0.012 |
| BSPL ncp rel | 0.483 ± 0.055 | 0.488 ± 0.050 | 0.506 ± 0.038 |

