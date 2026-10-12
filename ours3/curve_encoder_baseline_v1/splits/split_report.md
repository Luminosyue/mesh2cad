# CAD-level encoder splits

- seed: 42
- families: 2702
- CADs: 2796
- counts: {'train': 2231, 'val': 280, 'test': 285}

## Type coverage (CADs containing type)

| split | LINE | CIRCLE | ELLIPSE | BSPLINE |
|---|---|---|---|---|
| train | 2231 | 721 | 8 | 14 |
| val | 280 | 106 | 7 | 18 |
| test | 285 | 104 | 6 | 19 |

Split unit is CAD (Fusion360: family = project_hash). Curves are never split across sets.
