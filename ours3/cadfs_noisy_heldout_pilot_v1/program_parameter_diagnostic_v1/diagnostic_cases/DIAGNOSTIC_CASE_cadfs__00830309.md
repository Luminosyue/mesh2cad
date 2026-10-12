# Diagnostic Case cadfs__00830309

M2 improves the official operation multiset; M2 geometry improves, but remaining numeric errors prevent exact recovery.

## Geometry Metrics

```json
{
  "gt_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/cadfs__00830309/target/cad_target.dsl",
  "b0_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/B0/cadfs__00830309.dsl",
  "m2_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/M2/cadfs__00830309.dsl",
  "gt_dsl_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/gt_dsl_step/cadfs__00830309.step",
  "b0_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0/step/cadfs__00830309.step",
  "m2_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2/step/cadfs__00830309.step",
  "b0_opf1": 0.0,
  "m2_opf1": 1.0,
  "b0_chamfer": 0.019137201610084777,
  "m2_chamfer": 0.01023700730726661,
  "b0_hausdorff95": 0.08214520752481808,
  "m2_hausdorff95": 0.016274072500673507,
  "b0_bbox_error": 0.14195077233117545,
  "m2_bbox_error": 0.009524293738261084
}
```

## Operation Alignment

```json
{
  "cad_id": "cadfs__00830309",
  "GT_OP_SEQUENCE": [
    "Extrude",
    "Circle"
  ],
  "B0_OP_SEQUENCE": [
    "ExtrudePolygon"
  ],
  "M2_OP_SEQUENCE": [
    "Extrude",
    "Circle"
  ],
  "B0_EDIT_DISTANCE": 2,
  "M2_EDIT_DISTANCE": 0,
  "B0_MATCHED_OPS": 0,
  "M2_MATCHED_OPS": 2,
  "B0_MISSING_OPS": [
    "Extrude"
  ],
  "M2_MISSING_OPS": [],
  "B0_EXTRA_OPS": [],
  "M2_EXTRA_OPS": [],
  "B0_WRONG_TYPE_OPS": [
    {
      "gt": "Circle",
      "pred": "ExtrudePolygon"
    }
  ],
  "M2_WRONG_TYPE_OPS": [],
  "B0_WRONG_ORDER": 0,
  "M2_WRONG_ORDER": 0,
  "B0_ALIGNMENT": [
    {
      "action": "DELETE",
      "gt_index": 0,
      "pred_index": null,
      "gt_op": "Extrude",
      "pred_op": null
    },
    {
      "action": "SUBSTITUTE",
      "gt_index": 1,
      "pred_index": 0,
      "gt_op": "Circle",
      "pred_op": "ExtrudePolygon"
    }
  ],
  "M2_ALIGNMENT": [
    {
      "action": "MATCH",
      "gt_index": 0,
      "pred_index": 0,
      "gt_op": "Extrude",
      "pred_op": "Extrude"
    },
    {
      "action": "MATCH",
      "gt_index": 1,
      "pred_index": 1,
      "gt_op": "Circle",
      "pred_op": "Circle"
    }
  ]
}
```

## Parameter Diff

```json
{
  "B0": [],
  "M2": [
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "Extrude",
      "parameter": "height",
      "category": "feature",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": 0.127306,
      "pred": 0.070805,
      "kind": "length",
      "raw_error": 0.056500999999999996,
      "normalized_error": 0.443820401237962,
      "cad_id": "cadfs__00830309"
    },
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "Extrude",
      "parameter": "origin",
      "category": "placement",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": [
        2.11953,
        2.121462,
        0.0
      ],
      "pred": [
        2.122956,
        2.117655,
        0.0
      ],
      "kind": "position",
      "raw_error": 0.005121593990155689,
      "normalized_error": 0.0008533590982128929,
      "cad_id": "cadfs__00830309"
    },
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "Extrude",
      "parameter": "axis",
      "category": "placement",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": [
        0,
        0,
        1
      ],
      "pred": [
        0,
        0,
        1
      ],
      "kind": "direction",
      "raw_error": null,
      "normalized_error": 0.0,
      "angle_error_deg": 0.0,
      "cad_id": "cadfs__00830309"
    },
    {
      "arm": "M2",
      "gt_call_index": 1,
      "pred_call_index": 1,
      "op": "Circle",
      "parameter": "radius",
      "category": "curve",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": 2.121769,
      "pred": 2.124149,
      "kind": "length",
      "raw_error": 0.0023800000000000487,
      "normalized_error": 0.0011217055202522276,
      "cad_id": "cadfs__00830309"
    }
  ]
}
```

## Error Taxonomy

```json
{
  "cad_id": "cadfs__00830309",
  "B0_tags": [
    "STRUCTURE_ERROR",
    "PROFILE_TOPOLOGY_ERROR"
  ],
  "M2_tags": [
    "CURVE_SHAPE_PARAMETER_ERROR",
    "FEATURE_PARAMETER_ERROR"
  ],
  "B0_primary": "STRUCTURE_ERROR",
  "M2_primary": "CURVE_SHAPE_PARAMETER_ERROR"
}
```

## DSL

```text
GT:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=2.121769), height=0.127306, axis=(0, 0, 1), origin=(2.11953, 2.121462, 0.0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-3.853795, 3.046349), (0.945538, 3.046349), (0.945538, -0.553152), (-3.853795, -0.553152)], height=0.099986, axis=(0, 0, 1), origin=(3.853865, 0.553123, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=2.124149), height=0.070805, axis=(0, 0, 1), origin=(2.122956, 2.117655, 0.0))
result = body_0
```
