# CADFS Noisy Heldout Pilot V1

`CURRENT_GATE=CADFS_NOISY_HELDOUT_M2_NO_CLEAR_GAIN`

Held-out build: 27 reserve candidates attempted, 25 clean, 2 rejected by the frozen N2 noise gate. All train intersections are zero.

| Metric | B0 | M2 |
|---|---:|---:|
| EOS / Parse / Exec / STEP | 25/25 | 25/25 |
| Exact | 0/25 | 0/25 |
| Mean OpF1 | 0.860000 | 0.980000 |
| Chamfer mean | 0.050886 | 0.057227 |
| Chamfer median | 0.020317 | 0.022116 |
| Hausdorff95 median | 0.065117 | 0.059931 |
| BBox error median | 0.099135 | 0.086975 |

M2 improves program OpF1 on 3 cases and regresses on none, but corrected geometry is mixed: Chamfer M2/B0/tie = 3/6/16. This pilot does not show a clear geometry/generalization gain.
