# CURVE_TOKEN_HEAD_V1 — Step 4 key experiment (frozen C2, frozen_v1 test)

Seeds: [0, 1, 2]. Values are mean ± std over seeds.

- **D0**: frozen C2 backbone + type head only (classification baseline)
- **D1**: frozen C2 backbone + type + reconstruction + parameter heads

### Classification

| Exp | n seeds | Macro F1 | Bal Acc | LINE F1 | CIRCLE F1 | ELLIPSE F1 | BSPLINE F1 | L→C FP |
|---|---|---|---|---|---|---|---|---|
| D0 | 3 | 0.6796 ± 0.0363 | 0.7065 ± 0.0048 | 0.9957 ± 0.0019 | 0.9171 ± 0.0066 | 0.1283 ± 0.0303 | 0.6772 ± 0.1115 | 20.7 ± 9.5 |
| D1 | 3 | 0.7004 ± 0.0104 | 0.7040 ± 0.0038 | 0.9970 ± 0.0005 | 0.9149 ± 0.0072 | 0.1238 ± 0.0275 | 0.7660 ± 0.0316 | 22.7 ± 0.5 |

### Geometry / parameters (median)

| Exp | n seeds | Chamfer (med) | LINE dir° | CIRCLE n° | CIRCLE r rel | ELLIPSE maj° | BSPL deg acc |
|---|---|---|---|---|---|---|---|
| D0 | 3 | — | — | — | — | — | — |
| D1 | 3 | 0.00801 ± 0.00303 | 2.35 ± 1.09 | 1.22 ± 0.22 | 0.0217 ± 0.0106 | 18.77 ± 7.27 | 1.000 ± 0.000 |

### Per-seed Macro F1

| Exp | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| D0 | 0.7239 | 0.6349 | 0.6800 |
| D1 | 0.6972 | 0.6896 | 0.7144 |

### Verdict

- Macro F1 delta (D1 − D0) = +0.0208; max per-arm seed std = 0.0363 → **within seed noise — adding geometry supervision does not measurably change classification**.
- D1 adds geometry the token did not expose before: reconstruction Chamfer median 0.00801 in curve-local units.

