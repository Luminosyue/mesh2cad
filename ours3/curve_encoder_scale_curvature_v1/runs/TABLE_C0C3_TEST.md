# CURVE_ENCODER_SCALE_CURVATURE_V1 — test scorecard

Primary: LINE→CIRCLE FP / top-decile FP. Guardrail: CIRCLE recall ≥ ~85%.

P2 reference: L→C=1248 (7.3%), top90 FP=46%, CIRCLE rec=90.5%, MacroF1=0.487


| Exp | LINE→CIRCLE | rate | top90% FP | top90 rate | CIRCLE rec | Macro F1 | Bal Acc | LINE F1 | CIRCLE F1 | ELLIPSE F1 | BSPLINE F1 | Chamfer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | 1433 | 8.7% | 910 | 54.9% | 0.547 | 0.379 | 0.625 | 0.789 | 0.246 | 0.007 | 0.475 | 1.061 |
| C1 | 0 | 0.0% | 0 | 0.0% | 0.934 | 0.652 | 0.710 | 0.993 | 0.947 | 0.036 | 0.635 | 0.008 |
| C2 | 4 | 0.0% | 0 | 0.0% | 0.881 | 0.683 | 0.678 | 0.996 | 0.905 | 0.064 | 0.766 | 0.030 |
| C3 | 3 | 0.0% | 3 | 0.2% | 0.859 | 0.605 | 0.691 | 0.988 | 0.892 | 0.036 | 0.505 | 0.037 |
