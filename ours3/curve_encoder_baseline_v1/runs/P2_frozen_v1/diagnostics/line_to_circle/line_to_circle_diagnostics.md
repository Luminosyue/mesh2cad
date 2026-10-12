# LINE→CIRCLE diagnostics (P2 detailed, P0–T2 counts)

No model changes. Metrics: median / P90 / P95.

## 0. Cross-exp LINE→CIRCLE counts (test)

| Exp | LINE→CIRCLE | / n_LINE | frac | share of pred CIRCLE |
| --- | ---: | ---: | ---: | ---: |
| P0 | 2213 | 16486 | 12.906% | 85.7% |
| P1 | 1500 | 16486 | 8.748% | 75.9% |
| P2 | 1248 | 16486 | 7.278% | 72.0% |
| T0 | 1691 | 16486 | 9.862% | 82.4% |
| T1 | 1236 | 16486 | 7.208% | 71.6% |
| T2 | 1277 | 16486 | 7.447% | 72.3% |

## 1–2. Group geometry table (P2)

| Group | n | chord height (med/P90/P95) | total turn° | mean turn° | length | axis-align |
| --- | ---: | --- | --- | --- | --- | --- |
| LINE→LINE | 14918 | 1.117e-08 / 3.911e-06 / 8.015e-06 | 0.003552 / 0.003552 / 0.003553 | 0.0001146 / 0.0001146 / 0.0001146 | 0.248 / 3.464 / 4.789 | 1 / 1 / 1 |
| LINE→CIRCLE | 1248 | 0 / 6.885e-08 / 2.101e-07 | 0.003552 / 0.003552 / 0.003552 | 0.0001146 / 0.0001146 / 0.0001146 | 6.777 / 32.79 / 42.39 | 1 / 1 / 1 |
| CIRCLE→CIRCLE | 455 | 0.1592 / 0.318 / 0.3359 | 360 / 360 / 360 | 11.61 / 11.61 / 11.61 | 6.604 / 78.72 / 118.2 | 1 / 1 / 1 |
| CIRCLE→LINE | 7 | 0.006605 / 0.01973 / 0.02958 | 3.031 / 9.07 / 13.6 | 0.09778 / 0.2926 / 0.4387 | 0.08424 / 0.1065 / 0.1232 | 0.8698 / 1 / 1 |
| short_CIRCLE→LINE | 7 | 0.006605 / 0.01973 / 0.02958 | 3.031 / 9.07 / 13.6 | 0.09778 / 0.2926 / 0.4387 | 0.08424 / 0.1065 / 0.1232 | 0.8698 / 1 / 1 |

### LINE→CIRCLE chord-height bins

- **≈0 (<1e-4)**: 1248 / 1248 (100.0%)
- **tiny [1e-4,1e-3)**: 0 / 1248 (0.0%)
- **small [1e-3,1e-2)**: 0 / 1248 (0.0%)
- **bent [1e-2,1e-1)**: 0 / 1248 (0.0%)
- **very_bent ≥1e-1**: 0 / 1248 (0.0%)

## 4. LINE→CIRCLE rate by length bucket

| bucket | n_LINE | n_FP | rate | FP chordH med | FP totalTurn med |
| --- | ---: | ---: | ---: | ---: | ---: |
| <P10 | 1649 | 2 | 0.121% | 4.986606754647662e-06 | 0.003552397634594632 |
| P10–P25 | 2473 | 17 | 0.687% | 1.4880932404698412e-06 | 0.003552496228775541 |
| P25–P50 | 4108 | 16 | 0.389% | 0.0 | 0.003552496228775541 |
| P50–P75 | 4131 | 224 | 5.422% | 0.0 | 0.003552496228775541 |
| P75–P90 | 2466 | 226 | 9.165% | 0.0 | 0.003552496228775541 |
| >P90 | 1659 | 763 | 45.992% | 0.0 | 0.003552496228775541 |

## 5. Orientation / frame (P2)

- **LINE→LINE** dominant axis: X=5248 (35.2%), Y=4752 (31.9%), Z=4918 (33.0%); axis_aligned_ratio med=1.000
- **LINE→CIRCLE** dominant axis: X=407 (32.6%), Y=392 (31.4%), Z=449 (36.0%); axis_aligned_ratio med=1.000

## Figures

- `geom_histograms.png`
- `length_bucket_rates.png`

## Auto reads

- Chord height medians: A=1.117e-08, B=0, C=0.1592. B≈A (true straight LINEs misclassified).
- Total turn° medians: A=0.003552, B=0.003552, C=360.
- LINE→CIRCLE counts: P1=1500, P2=1248 (Δ=-252, -16.8% vs P1).
- Highest LINE→CIRCLE rate length bucket: **>P90** (45.99%, n_FP=763).
