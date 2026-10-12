# PartObjaverse Pilot20 summary

- TOTAL_N: 20
- PARSE_VALID_N: 20
- EXEC_VALID_N: 20
- STEP_EXPORT_N: 20
- STEP_RELOAD_N: 20
- BREP_VALID_N: 20
- METRICS_VALID_N: 20
- GEOMETRY_METRICS_N: 20/20
- CD mean / median / std: 0.08193355558329204 / 0.08070211430033827 / 0.044106604187822626
- IoU mean / median / std: None / None / None
- Normal mean / median: 0.7150929415575156 / 0.7412550685640253

## Protocol

- METRIC_COORDINATE_SPACE=normalized
- NORMALIZATION_PROTOCOL=max_bbox_extent_to_1
- SAMPLING_N=100000

## Category breakdown

- BOX_BOOLEAN_LIKE: N=4, BREP_VALID_RATE=1.0, CD_MEAN=0.06832840113525787, CD_MEDIAN=0.061414245863686816, IOU_MEAN=None, IOU_MEDIAN=None
- EXTRUDE_LIKE: N=4, BREP_VALID_RATE=1.0, CD_MEAN=0.04139474855871451, CD_MEDIAN=0.038629855954214545, IOU_MEAN=None, IOU_MEDIAN=None
- REVOLVE_CYLINDER_LIKE: N=4, BREP_VALID_RATE=1.0, CD_MEAN=0.1296921136073904, CD_MEDIAN=0.13261195561443168, IOU_MEAN=None, IOU_MEDIAN=None
- SHELL_LIKE: N=4, BREP_VALID_RATE=1.0, CD_MEAN=0.07816027080644736, CD_MEDIAN=0.06767602027099758, IOU_MEAN=None, IOU_MEDIAN=None
- HARDER_FREEFORM: N=4, BREP_VALID_RATE=1.0, CD_MEAN=0.09209224380865011, CD_MEDIAN=0.09281952530411601, IOU_MEAN=None, IOU_MEDIAN=None

## Refinement
- V1_VALID_N=20, V2_VALID_N=20, V3_VALID_N=20
- BEST_IS_V1_N=18, BEST_IS_V2_N=1, BEST_IS_V3_N=1
- REFINEMENT_IMPROVED_N=2
- REFINEMENT_DEGRADED_N=19
- REFINEMENT_INVALIDATED_N=0

{
  "version_valid": "STEP reload and B-Rep valid and geometry metrics valid",
  "refinement_improved": "a valid v2/v3 has Chamfer-L1 at least 1e-6 lower than valid v1",
  "refinement_degraded": "a later consecutive valid round has Chamfer-L1 at least 1e-6 higher",
  "refinement_invalidated": "a valid round is immediately followed by an invalid round",
  "best": "STEP reload and B-Rep valid hard conditions; then lowest Chamfer-L1, highest IoU, highest normal consistency, lowest bbox error"
}
