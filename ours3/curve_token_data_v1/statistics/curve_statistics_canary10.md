# Track B curve dataset statistics (canary10)

```text
TOTAL_CAD=10
VALID_CAD=10
FAILED_CAD=0
TOTAL_CURVES=3855
```

## Curve type distribution

| curve type | count | % of curves |
|---|---|---|
| LINE | 2541 | 65.9144% |
| CIRCLE | 142 | 3.6835% |
| ELLIPSE | 259 | 6.7185% |
| BSPLINE | 913 | 23.6835% |

## Distributions

| quantity | n | mean | median | P90 | P95 | P99 | max |
|---|---|---|---|---|---|---|---|
| curves per CAD | 10 | 385.5 | 431 | 638.9 | 836.4 | 994.5 | 1034 |
| curve length (world units) | 3855 | 7.531 | 0.4649 | 1.671 | 26.31 | 219.4 | 706.9 |
| faces per edge | 3855 | 1.995 | 2 | 2 | 2 | 2 | 2 |
| edges per face (per-CAD mean) | 10 | 5.209 | 5.422 | 5.707 | 5.712 | 5.717 | 5.718 |

## B-Spline complexity

- instances: 913
- degree distribution: `{'3': 912, '6': 1}`
- rational: 0 (0.000%)
- periodic: 6 (0.657%)
- closed: 6 (0.657%)

| quantity | n | mean | median | P90 | P95 | P99 | max |
|---|---|---|---|---|---|---|---|
| control points | 913 | 11.96 | 6 | 22 | 25 | 34 | 67 |
| knot count | 913 | 5.114 | 3 | 8 | 9 | 17 | 33 |

### Most complex B-Spline instances

| degree | control points | knots | rational | periodic |
|---|---|---|---|---|
| 6 | 67 | 14 | False | False |
| 3 | 65 | 33 | False | True |
| 3 | 65 | 33 | False | True |
| 3 | 65 | 33 | False | True |
| 3 | 57 | 29 | False | True |
| 3 | 57 | 29 | False | True |
| 3 | 57 | 29 | False | True |
| 3 | 34 | 17 | False | False |
| 3 | 34 | 17 | False | False |
| 3 | 34 | 17 | False | False |

## Topology

| quantity | count | % of curves |
|---|---|---|
| boundary edges (1 face) | 21 | 0.5447% |
| manifold edges (2 faces) | 3834 | 99.4553% |
| non-manifold edges (>2 faces) | 0 | 0.0000% |
| free edges (0 faces) | 0 | 0.0000% |
| closed curves | 30 | 0.7782% |
| open curves | 3825 | 99.2218% |

- CAD with self-consistent topology: 10 (100.0000%)
- CAD that are fully manifold: 10 (100.0000%)

Non-manifold edges (>2 adjacent faces) occur in solids built by unioning bodies
that touch along an edge. They are extracted faithfully (the curve simply carries
3+ face ids) and are reported here rather than treated as an extraction failure.

## Extraction health

- curves with exact parameters extracted: 3855
- curves whose parameters reproduce the OCC curve: 3855
- skipped topological edges: 0 `{}`
- sampling strategy used: `{'uniform_abscissa': 3855}`
- reconstruction backend used for verification: `{'numpy': 3849, 'occ_rebuild': 6}` (`numpy` = parameters are consumable without OCC)
- CAD reusing the Track A normalization transform: 10
- non-primary curve types encountered: `none`

## Per split

| split | CAD | curves |
|---|---|---|
| deepcad_train | 5 | 1722 |
| fusion360_train | 5 | 2133 |
