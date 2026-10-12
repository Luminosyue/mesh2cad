# P2 test diagnostics

## A. Confusion matrix (rows=GT, cols=Pred)

| GT \ Pred | LINE | CIRCLE | ELLIPSE | BSPLINE | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| LINE | 14918 | 1248 | 50 | 270 | 16486 |
| CIRCLE | 7 | 455 | 15 | 26 | 503 |
| ELLIPSE | 0 | 16 | 8 | 2 | 26 |
| BSPLINE | 0 | 14 | 0 | 118 | 132 |

### Focus counts

- **ELLIPSE→CIRCLE**: 16 / 26 (61.5%)
- **ELLIPSE→LINE**: 0 / 26 (0.0%)
- **ELLIPSE→BSPLINE**: 2 / 26 (7.7%)
- **ELLIPSE→ELLIPSE**: 8 / 26 (30.8%)
- **CIRCLE→LINE**: 7 / 503 (1.4%)
- **CIRCLE→CIRCLE**: 455 / 503 (90.5%)
- **CIRCLE→ELLIPSE**: 15 / 503 (3.0%)
- **CIRCLE→BSPLINE**: 26 / 503 (5.2%)
- **BSPLINE→LINE**: 0 / 132 (0.0%)
- **BSPLINE→BSPLINE**: 118 / 132 (89.4%)
- **BSPLINE→CIRCLE**: 14 / 132 (10.6%)
- **BSPLINE→ELLIPSE**: 0 / 132 (0.0%)

## B. Arc-span buckets (GT-conditioned recall)

Span = `|u_end − u_start|` in degrees (OCC angle parameter). `closed` overrides span buckets.

### ELLIPSE

| bucket | n_gt | recall | →LINE | →CIRCLE | →ELLIPSE | →BSPLINE | span° mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| closed | 0 | — | — | — | — | — | — |
| <15° | 6 | 0.667 | 0 | 0 | 4 | 2 | 4.1 |
| 15°–45° | 0 | — | — | — | — | — | — |
| 45°–90° | 0 | — | — | — | — | — | — |
| 90°–180° | 20 | 0.200 | 0 | 16 | 4 | 0 | 180.0 |
| >180° | 0 | — | — | — | — | — | — |

### CIRCLE

| bucket | n_gt | recall | →LINE | →CIRCLE | →ELLIPSE | →BSPLINE | span° mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| closed | 250 | 0.980 | 0 | 245 | 1 | 4 | 360.0 |
| <15° | 29 | 0.379 | 6 | 11 | 3 | 9 | 3.5 |
| 15°–45° | 19 | 0.842 | 1 | 16 | 1 | 1 | 34.3 |
| 45°–90° | 60 | 0.850 | 0 | 51 | 6 | 3 | 70.5 |
| 90°–180° | 102 | 0.892 | 0 | 91 | 3 | 8 | 119.3 |
| >180° | 43 | 0.953 | 0 | 41 | 1 | 1 | 270.4 |

## ELLIPSE→CIRCLE geometry (near-circular?)

- misclassified as CIRCLE: n=16, span° median=180.0, axis_ratio(minor/major) median=0.9807854242532044, eccentricity median=0.19508959856395244
- bucket mix: {'closed': 0, '<15°': 0, '15°–45°': 0, '45°–90°': 0, '90°–180°': 16, '>180°': 0}
- correctly classified: n=8, span° median=93.42990219930235, axis_ratio median=0.963352343551936, eccentricity median=0.2597479756974444

