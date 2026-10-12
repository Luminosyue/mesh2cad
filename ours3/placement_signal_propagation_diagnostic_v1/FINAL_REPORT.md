# Placement Signal Propagation Diagnostic V1
FINAL_GATE=`PLACEMENT_PIPELINE_MULTIPLE_FAILURES`
FIRST_FAILURE_STAGE=`C2 additive fusion`

## Frozen cohort
- train CAD=100 curves=1348
- heldout CAD=25 curves=398

## Descriptor integrity
- field integrity `True` maxabs=0.000e+00
- centroid std [0.26990725947296035, 0.21246884975300395, 0.16849580421725344]
- zero-var dims []

## Curve-level centroid probe (fit train100, eval heldout25; ridge=1.0 z-scored linear)
| rep | R2_mean | MAE_mean |
|---|---:|---:|
| C2_ONLY | -0.0327 | 0.135184 |
| PLACEMENT_RESIDUAL_ONLY | 0.9906 | 0.006279 |
| C2_PLUS_PLACEMENT | -0.0325 | 0.135281 |
| SHUFFLE | -0.0466 | 0.136498 |
| ZERO | -0.0555 | 0.137501 |

## Other curve-level targets (ridge linear, heldout R2_mean)
| target | C2 | residual | enhanced |
|---|---:|---:|---:|
| bbox_extent | 0.9312 | 0.9959 | 0.9310 |
| endpoint_A | 0.2566 | 0.9988 | 0.2728 |
| endpoint_B | 0.2596 | 0.9984 | 0.2728 |
| plane_normal | 0.0847 | 0.2543 | 0.0848 |

MLP centroid: residual R2=0.9682, enhanced R2=-0.0310.

## Residual magnitude (heldout25 curves)
- mean ||C2||=16.6022
- mean ||P||=0.033612
- mean ratio=0.002123 median=0.002158 P90=0.002584

## 8-token summary CAD-level probe
- OLD_M2 12-D R2=-26.5779 layout(min/max) R2=0.7012
- M2-Placement 12-D R2=-26.1261 layout(min/max) R2=0.6964
- summary cosine mean=0.999158 relative L2 mean=0.039799

## Outlier cadfs__00982874
- residual ratio mean=0.002071
- summary rel L2=0.048978
- DSL changed=True

Old M2 and Placement both fail GT Union; Placement jumped to a different ExtrudePolygon (axis z vs x).

## Answer
Placement information first fails at: **C2 additive fusion**.
FINAL_GATE=`PLACEMENT_PIPELINE_MULTIPLE_FAILURES` failures=['C2 additive fusion', '8-token summary']
