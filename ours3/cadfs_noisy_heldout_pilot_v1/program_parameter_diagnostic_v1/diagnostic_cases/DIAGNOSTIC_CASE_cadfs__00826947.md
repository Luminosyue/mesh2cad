# Diagnostic Case cadfs__00826947

M2 improves the official operation multiset; M2 geometry improves, but remaining numeric errors prevent exact recovery.

## Geometry Metrics

```json
{
  "gt_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/cadfs__00826947/target/cad_target.dsl",
  "b0_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/B0/cadfs__00826947.dsl",
  "m2_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/M2/cadfs__00826947.dsl",
  "gt_dsl_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/gt_dsl_step/cadfs__00826947.step",
  "b0_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0/step/cadfs__00826947.step",
  "m2_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2/step/cadfs__00826947.step",
  "b0_opf1": 0.0,
  "m2_opf1": 1.0,
  "b0_chamfer": 0.058538779285920946,
  "m2_chamfer": 0.049508050456728334,
  "b0_hausdorff95": 0.2572538652362406,
  "m2_hausdorff95": 0.1755174787083264,
  "b0_bbox_error": 0.41723111499753207,
  "m2_bbox_error": 0.11616032282425683
}
```

## Operation Alignment

```json
{
  "cad_id": "cadfs__00826947",
  "GT_OP_SEQUENCE": [
    "ExtrudePolygon"
  ],
  "B0_OP_SEQUENCE": [
    "Extrude",
    "Circle"
  ],
  "M2_OP_SEQUENCE": [
    "ExtrudePolygon"
  ],
  "B0_EDIT_DISTANCE": 2,
  "M2_EDIT_DISTANCE": 0,
  "B0_MATCHED_OPS": 0,
  "M2_MATCHED_OPS": 1,
  "B0_MISSING_OPS": [],
  "M2_MISSING_OPS": [],
  "B0_EXTRA_OPS": [
    "Extrude"
  ],
  "M2_EXTRA_OPS": [],
  "B0_WRONG_TYPE_OPS": [
    {
      "gt": "ExtrudePolygon",
      "pred": "Circle"
    }
  ],
  "M2_WRONG_TYPE_OPS": [],
  "B0_WRONG_ORDER": 0,
  "M2_WRONG_ORDER": 0,
  "B0_ALIGNMENT": [
    {
      "action": "INSERT",
      "gt_index": null,
      "pred_index": 0,
      "gt_op": null,
      "pred_op": "Extrude"
    },
    {
      "action": "SUBSTITUTE",
      "gt_index": 0,
      "pred_index": 1,
      "gt_op": "ExtrudePolygon",
      "pred_op": "Circle"
    }
  ],
  "M2_ALIGNMENT": [
    {
      "action": "MATCH",
      "gt_index": 0,
      "pred_index": 0,
      "gt_op": "ExtrudePolygon",
      "pred_op": "ExtrudePolygon"
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
      "op": "ExtrudePolygon",
      "parameter": "points",
      "category": "curve",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": [
        [
          -0.666429,
          -1.066286
        ],
        [
          0.666429,
          -1.066286
        ],
        [
          2.799001,
          1.066286
        ],
        [
          -2.799001,
          1.066286
        ]
      ],
      "pred": [
        [
          0.0,
          0.0
        ],
        [
          -5.807685,
          0.0
        ],
        [
          -5.807685,
          1.468477
        ],
        [
          0.0,
          1.468477
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 4.815644374743217,
        "max": 8.616078081301085
      },
      "normalized_error": 0.8023314298516584,
      "cad_id": "cadfs__00826947"
    },
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "ExtrudePolygon",
      "parameter": "height",
      "category": "feature",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": 0.3732,
      "pred": 0.346884,
      "kind": "length",
      "raw_error": 0.02631599999999995,
      "normalized_error": 0.07051446945337608,
      "cad_id": "cadfs__00826947"
    },
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "ExtrudePolygon",
      "parameter": "origin",
      "category": "placement",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": [
        2.797505,
        1.066286,
        0.0
      ],
      "pred": [
        5.807159,
        0.0,
        0.0
      ],
      "kind": "position",
      "raw_error": 3.192958351358815,
      "normalized_error": 0.5319767491425516,
      "cad_id": "cadfs__00826947"
    },
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "ExtrudePolygon",
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
      "cad_id": "cadfs__00826947"
    },
    {
      "arm": "M2",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "ExtrudePolygon",
      "parameter": "x_axis",
      "category": "placement",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": [
        1,
        0,
        0
      ],
      "pred": [
        1,
        0,
        0
      ],
      "kind": "direction",
      "raw_error": null,
      "normalized_error": 0.0,
      "angle_error_deg": 0.0,
      "cad_id": "cadfs__00826947"
    }
  ]
}
```

## Error Taxonomy

```json
{
  "cad_id": "cadfs__00826947",
  "B0_tags": [
    "STRUCTURE_ERROR",
    "PROFILE_TOPOLOGY_ERROR"
  ],
  "M2_tags": [
    "CURVE_SHAPE_PARAMETER_ERROR",
    "GLOBAL_PLACEMENT_ERROR",
    "FEATURE_PARAMETER_ERROR"
  ],
  "B0_primary": "STRUCTURE_ERROR",
  "M2_primary": "GLOBAL_PLACEMENT_ERROR"
}
```

## DSL

```text
GT:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-0.666429, -1.066286), (0.666429, -1.066286), (2.799001, 1.066286), (-2.799001, 1.066286)], height=0.3732, axis=(0, 0, 1), origin=(2.797505, 1.066286, 0.0), x_axis=(1, 0, 0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=2.118068), height=0.353011, axis=(0, 0, 1), origin=(2.117937, 2.117514, 0.0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.0, 0.0), (-5.807685, 0.0), (-5.807685, 1.468477), (0.0, 1.468477)], height=0.346884, axis=(0, 0, 1), origin=(5.807159, 0.0, 0.0), x_axis=(1, 0, 0))
result = body_0
```
