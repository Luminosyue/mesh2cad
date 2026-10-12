# CURVE_TOKEN_HEAD_V1 — D0 vs D1 (frozen C2 backbone, frozen_v1 test)

Backbone frozen as C2: curve-local xyz+tangent+s → PointNet, log(length) scale branch, fusion → 256-D Curve Token.

- **D0**: frozen C2 backbone + type head only (classification baseline) (best epoch 30)
- **D1**: frozen C2 backbone + type + reconstruction + parameter heads (best epoch 22)

### Classification

| Exp | Macro F1 | Bal Acc | LINE F1 | CIRCLE F1 | ELLIPSE F1 | BSPLINE F1 | L→C FP |
|---|---|---|---|---|---|---|---|
| D0 | 0.7239 | 0.7087 | 0.9980 | 0.9259 | 0.1538 | 0.8178 | 19 |
| D1 | 0.6972 | 0.7047 | 0.9970 | 0.9216 | 0.0857 | 0.7846 | 23 |

### Geometry / parameters (median)

| Exp | Chamfer (med) | LINE dir° | CIRCLE n° | CIRCLE r rel | ELLIPSE maj° | BSPL deg acc |
|---|---|---|---|---|---|---|
| D0 | — | — | — | — | — | — |
| D1 | 0.00796 | 1.97 | 1.37 | 0.0321 | 8.69 | 1.000 |

### Full parameter error stats (test)

**D1**

| metric | n | mean | median | p90 |
|---|---|---|---|---|
| bspline_degree_correct | 132 | 0.9394 | 1.0000 | 1.0000 |
| bspline_ncp_rel | 132 | 0.7169 | 0.5468 | 1.3257 |
| circle_center_dist | 503 | 2.2167 | 0.2227 | 1.2270 |
| circle_normal_deg | 503 | 2.4722 | 1.3652 | 4.2047 |
| circle_radius_rel | 503 | 0.0842 | 0.0321 | 0.1986 |
| circle_span_deg | 503 | 13.0881 | 6.7337 | 29.9222 |
| ellipse_center_dist | 26 | 3.9218 | 3.6587 | 5.2496 |
| ellipse_major_axis_deg | 26 | 29.5161 | 8.6935 | 64.8493 |
| ellipse_normal_deg | 26 | 47.4834 | 36.6141 | 83.6941 |
| ellipse_r_major_rel | 26 | 4.7938 | 1.2077 | 11.2136 |
| ellipse_r_minor_rel | 26 | 1.2841 | 0.3373 | 2.9777 |
| line_dir_deg | 16486 | 3.2171 | 1.9693 | 7.0206 |
| line_len_rel | 16486 | 0.0169 | 0.0104 | 0.0385 |
| line_origin_dist | 16486 | 0.0038 | 0.0032 | 0.0064 |

