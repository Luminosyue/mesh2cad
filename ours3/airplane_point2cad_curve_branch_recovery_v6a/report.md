# Airplane Point2CAD Curve Branch Recovery V6A

## Before / After vs V5

| Metric | V5 | V6A |
| --- | ---: | ---: |
| official surface pairs | 3 | 3 |
| raw fragments | 23 | 21 |
| recovered branches | N/A | 19 |
| accepted branch connections | N/A | 2 |
| rejected branch connections | N/A | 314 |
| degree1 endpoints | 46 | 50 |
| degree2 endpoints | 7 | 5 |
| open wires | 43 | 44 |
| closed wires | 2 | 2 |
| valid trimmed faces | 2 | 2 |
| free shell edges | 0 | 0 |
| closed shells | 0 | 0 |
| clean solids | 0 | 0 |
| STEP reload valid | True | True |
| IoU | N/A | 0.0381246780010304 |
| Chamfer | N/A | 0.09372411503268203 |
| Hausdorff | N/A | 0.47713762814136906 |

NEXT_PRIMARY_BLOCKER=INTERSECTION_BRANCH_FRAGMENTATION
first_blocker={'part': 'PART_002', 'surface': 0, 'wire': 'WIRE_001', 'start': [-0.3190402161993985, -0.8649326994639991, 0.10440564193820631], 'end': [-0.2257623349610868, -0.8768641739659374, 0.09472666405550478], 'expected_surface_pair': [0, 1], 'candidate_fragments': ['P2C_CURVE_000_C00', 'P2C_CURVE_000_C01', 'P2C_CURVE_000_C02'], 'best_candidate_gap': 0.0, 'best_candidate_tangent_angle': 23.380166708571267, 'best_candidate_uv_gap': 0.0945346362970156, 'best_candidate_support_fraction': 1.0, 'reason_rejected': 'GAP_TOO_LARGE,UV_DISCONTINUITY', 'blocker_category': 'INTERSECTION_BRANCH_FRAGMENTATION'}

