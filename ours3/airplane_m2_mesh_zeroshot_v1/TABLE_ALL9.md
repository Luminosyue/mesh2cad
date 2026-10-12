# Airplane mesh-derived curve zero-shot (canary / stress)

Not a formal main result — M2 trained on B-Rep oracle curves; airplane uses mesh-fitted curves.

| part | role | K | B0 STEP | M2 STEP | B0 Chamfer_rel | M2 Chamfer_rel | B0 cov | M2 cov |
|---|---|---:|:---:|:---:|---:|---:|---:|---:|
| PART_000 | vertical_tail | 1 | Y | Y | 0.0569 | 0.3672 | 0.015 | 0.003 |
| PART_001 | left_wing | 5 | Y | Y | 0.1032 | 0.0675 | 0.005 | 0.005 |
| PART_002 | left_propeller | 12 | N | Y | nan | 0.1531 | nan | 0.011 |
| PART_003 | right_propeller | 14 | Y | Y | 0.1647 | 0.0644 | 0.000 | 0.010 |
| PART_004 | right_wing | 8 | Y | Y | 0.0820 | 0.1191 | 0.002 | 0.004 |
| PART_005 | fuselage | 30 | Y | Y | 0.2335 | 0.3920 | 0.001 | 0.002 |
| PART_006 | right_tailplane | 7 | Y | Y | 0.0520 | 0.2779 | 0.009 | 0.000 |
| PART_007 | left_tailplane | 4 | Y | Y | 0.0366 | 0.0366 | 0.010 | 0.010 |
| PART_008 | dorsal_feature | 58 | Y | N | 0.0564 | nan | 0.023 | nan |
