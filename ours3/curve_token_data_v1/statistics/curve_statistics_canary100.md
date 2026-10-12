# Track B curve dataset statistics (canary100)

```text
TOTAL_CAD=100
VALID_CAD=100
FAILED_CAD=0
TOTAL_CURVES=9779
```

## Curve type distribution

| curve type | count | % of curves |
|---|---|---|
| LINE | 7256 | 74.1998% |
| CIRCLE | 657 | 6.7185% |
| ELLIPSE | 365 | 3.7325% |
| BSPLINE | 1501 | 15.3492% |

## Distributions

| quantity | n | mean | median | P90 | P95 | P99 | max |
|---|---|---|---|---|---|---|---|
| curves per CAD | 100 | 97.79 | 25 | 313.1 | 441.4 | 599.4 | 1034 |
| curve length (world units) | 9779 | 21.2 | 0.4625 | 10.4 | 45.72 | 1000 | 1700 |
| faces per edge | 9779 | 1.986 | 2 | 2 | 2 | 2 | 4 |
| edges per face (per-CAD mean) | 100 | 4.279 | 4.5 | 5.645 | 5.721 | 5.925 | 6.59 |

## B-Spline complexity

- instances: 1501
- degree distribution: `{'3': 1429, '4': 3, '5': 64, '6': 1, '7': 2, '8': 2}`
- rational: 0 (0.000%)
- periodic: 20 (1.332%)
- closed: 20 (1.332%)

| quantity | n | mean | median | P90 | P95 | P99 | max |
|---|---|---|---|---|---|---|---|
| control points | 1501 | 13.7 | 7 | 25 | 30 | 65 | 82 |
| knot count | 1501 | 6.645 | 3 | 10 | 16 | 51 | 71 |

### Most complex B-Spline instances

| degree | control points | knots | rational | periodic |
|---|---|---|---|---|
| 3 | 82 | 28 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |
| 5 | 75 | 71 | False | False |

## Topology

| quantity | count | % of curves |
|---|---|---|
| boundary edges (1 face) | 158 | 1.6157% |
| manifold edges (2 faces) | 9611 | 98.2820% |
| non-manifold edges (>2 faces) | 10 | 0.1023% |
| free edges (0 faces) | 0 | 0.0000% |
| closed curves | 244 | 2.4951% |
| open curves | 9535 | 97.5049% |

- CAD with self-consistent topology: 100 (100.0000%)
- CAD that are fully manifold: 97 (97.0000%)

Non-manifold edges (>2 adjacent faces) occur in solids built by unioning bodies
that touch along an edge. They are extracted faithfully (the curve simply carries
3+ face ids) and are reported here rather than treated as an extraction failure.

## Extraction health

- curves with exact parameters extracted: 9779
- curves whose parameters reproduce the OCC curve: 9779
- skipped topological edges: 0 `{}`
- sampling strategy used: `{'uniform_abscissa': 9772, 'abscissa_point': 7}`
- reconstruction backend used for verification: `{'numpy': 9759, 'occ_rebuild': 20}` (`numpy` = parameters are consumable without OCC)
- CAD reusing the Track A normalization transform: 100
- non-primary curve types encountered: `none`

## Per split

| split | CAD | curves |
|---|---|---|
| deepcad_train | 50 | 4967 |
| fusion360_train | 50 | 4812 |
