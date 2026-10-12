# Track B curve dataset statistics (full)

```text
TOTAL_CAD=2796
VALID_CAD=2796
FAILED_CAD=0
TOTAL_CURVES=172622
```

## Curve type distribution

| curve type | count | % of curves |
|---|---|---|
| LINE | 164564 | 95.3320% |
| CIRCLE | 6127 | 3.5494% |
| ELLIPSE | 366 | 0.2120% |
| BSPLINE | 1565 | 0.9066% |

## Distributions

| quantity | n | mean | median | P90 | P95 | P99 | max |
|---|---|---|---|---|---|---|---|
| curves per CAD | 2796 | 61.74 | 23 | 174 | 266.2 | 513.3 | 1034 |
| curve length (world units) | 172622 | 15.46 | 0.08535 | 1.5 | 18 | 250 | 2.743e+04 |
| faces per edge | 172622 | 1.995 | 2 | 2 | 2 | 2 | 4 |
| edges per face (per-CAD mean) | 2796 | 4.29 | 4.364 | 5.684 | 5.829 | 5.928 | 8.4 |

## B-Spline complexity

- instances: 1565
- degree distribution: `{'3': 1455, '4': 3, '5': 102, '6': 1, '7': 2, '8': 2}`
- rational: 0 (0.000%)
- periodic: 20 (1.278%)
- closed: 20 (1.278%)

| quantity | n | mean | median | P90 | P95 | P99 | max |
|---|---|---|---|---|---|---|---|
| control points | 1565 | 14.46 | 10 | 25 | 34 | 75 | 95 |
| knot count | 1565 | 7.454 | 5 | 10 | 21 | 66.52 | 91 |

### Most complex B-Spline instances

| degree | control points | knots | rational | periodic |
|---|---|---|---|---|
| 5 | 95 | 91 | False | False |
| 5 | 95 | 91 | False | False |
| 5 | 84 | 80 | False | False |
| 5 | 84 | 80 | False | False |
| 3 | 82 | 28 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |

## Topology

| quantity | count | % of curves |
|---|---|---|
| boundary edges (1 face) | 1578 | 0.9141% |
| manifold edges (2 faces) | 170668 | 98.8680% |
| non-manifold edges (>2 faces) | 376 | 0.2178% |
| free edges (0 faces) | 0 | 0.0000% |
| closed curves | 2925 | 1.6945% |
| open curves | 169697 | 98.3055% |

- CAD with self-consistent topology: 2796 (100.0000%)
- CAD that are fully manifold: 2710 (96.9242%)

Non-manifold edges (>2 adjacent faces) occur in solids built by unioning bodies
that touch along an edge. They are extracted faithfully (the curve simply carries
3+ face ids) and are reported here rather than treated as an extraction failure.

## Extraction health

- curves with exact parameters extracted: 172622
- curves whose parameters reproduce the OCC curve: 172622
- skipped topological edges: 0 `{}`
- sampling strategy used: `{'uniform_abscissa': 172283, 'abscissa_point': 338, 'parameter_uniform': 1}`
- reconstruction backend used for verification: `{'numpy': 172602, 'occ_rebuild': 20}` (`numpy` = parameters are consumable without OCC)
- CAD reusing the Track A normalization transform: 2796
- non-primary curve types encountered: `none`

## Per split

| split | CAD | curves |
|---|---|---|
| deepcad_train | 2194 | 150822 |
| fusion360_train | 602 | 21800 |
