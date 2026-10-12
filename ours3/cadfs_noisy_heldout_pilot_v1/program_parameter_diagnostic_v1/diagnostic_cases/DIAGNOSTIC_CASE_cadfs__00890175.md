# Diagnostic Case cadfs__00890175

B0 and M2 differ geometrically despite similar operation-level signal; M2 geometry does not improve because matched placement/profile/feature values remain incorrect.

## Geometry Metrics

```json
{
  "gt_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/cadfs__00890175/target/cad_target.dsl",
  "b0_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/B0/cadfs__00890175.dsl",
  "m2_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/M2/cadfs__00890175.dsl",
  "gt_dsl_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/gt_dsl_step/cadfs__00890175.step",
  "b0_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0/step/cadfs__00890175.step",
  "m2_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2/step/cadfs__00890175.step",
  "b0_opf1": 1.0,
  "m2_opf1": 1.0,
  "b0_chamfer": 0.42446818676967163,
  "m2_chamfer": 0.440058704482735,
  "b0_hausdorff95": 0.8749177271569692,
  "m2_hausdorff95": 0.8748658268681799,
  "b0_bbox_error": 1.2447277605965332,
  "m2_bbox_error": 1.2966470645146109
}
```

## Operation Alignment

```json
{
  "cad_id": "cadfs__00890175",
  "GT_OP_SEQUENCE": [
    "ExtrudePolygon"
  ],
  "B0_OP_SEQUENCE": [
    "ExtrudePolygon"
  ],
  "M2_OP_SEQUENCE": [
    "ExtrudePolygon"
  ],
  "B0_EDIT_DISTANCE": 0,
  "M2_EDIT_DISTANCE": 0,
  "B0_MATCHED_OPS": 1,
  "M2_MATCHED_OPS": 1,
  "B0_MISSING_OPS": [],
  "M2_MISSING_OPS": [],
  "B0_EXTRA_OPS": [],
  "M2_EXTRA_OPS": [],
  "B0_WRONG_TYPE_OPS": [],
  "M2_WRONG_TYPE_OPS": [],
  "B0_WRONG_ORDER": 0,
  "M2_WRONG_ORDER": 0,
  "B0_ALIGNMENT": [
    {
      "action": "MATCH",
      "gt_index": 0,
      "pred_index": 0,
      "gt_op": "ExtrudePolygon",
      "pred_op": "ExtrudePolygon"
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
  "B0": [
    {
      "arm": "B0",
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
          0.297044,
          -0.297044
        ],
        [
          -0.297044,
          -0.297044
        ],
        [
          -0.297044,
          0.297044
        ],
        [
          0.297044,
          0.297044
        ]
      ],
      "pred": [
        [
          0.0,
          0.0
        ],
        [
          3.042854,
          0.0
        ],
        [
          3.042854,
          4.640353
        ],
        [
          0.0,
          4.640353
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 3.401400590510625,
        "max": 5.478982726737237
      },
      "normalized_error": 0.5669001257772017,
      "cad_id": "cadfs__00890175"
    },
    {
      "arm": "B0",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "ExtrudePolygon",
      "parameter": "height",
      "category": "feature",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": 5.940885,
      "pred": 0.160939,
      "kind": "length",
      "raw_error": 5.779946,
      "normalized_error": 0.9729099284029231,
      "cad_id": "cadfs__00890175"
    },
    {
      "arm": "B0",
      "gt_call_index": 0,
      "pred_call_index": 0,
      "op": "ExtrudePolygon",
      "parameter": "origin",
      "category": "placement",
      "gt_present": true,
      "pred_present": true,
      "status": "COMPARED",
      "gt": [
        0.297044,
        0.297044,
        0.0
      ],
      "pred": [
        0.0,
        0.0,
        0.0
      ],
      "kind": "position",
      "raw_error": 0.4200836534215536,
      "normalized_error": 0.07001394561581889,
      "cad_id": "cadfs__00890175"
    },
    {
      "arm": "B0",
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
      "cad_id": "cadfs__00890175"
    },
    {
      "arm": "B0",
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
      "cad_id": "cadfs__00890175"
    }
  ],
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
          0.297044,
          -0.297044
        ],
        [
          -0.297044,
          -0.297044
        ],
        [
          -0.297044,
          0.297044
        ],
        [
          0.297044,
          0.297044
        ]
      ],
      "pred": [
        [
          0.0,
          0.0
        ],
        [
          5.364632,
          0.0
        ],
        [
          5.364632,
          2.682316
        ],
        [
          0.0,
          2.682316
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 3.65921644907614,
        "max": 6.143622517941674
      },
      "normalized_error": 0.6098694376118323,
      "cad_id": "cadfs__00890175"
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
      "gt": 5.940885,
      "pred": 0.160939,
      "kind": "length",
      "raw_error": 5.779946,
      "normalized_error": 0.9729099284029231,
      "cad_id": "cadfs__00890175"
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
        0.297044,
        0.297044,
        0.0
      ],
      "pred": [
        0.0,
        0.0,
        0.0
      ],
      "kind": "position",
      "raw_error": 0.4200836534215536,
      "normalized_error": 0.07001394561581889,
      "cad_id": "cadfs__00890175"
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
      "cad_id": "cadfs__00890175"
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
      "cad_id": "cadfs__00890175"
    }
  ]
}
```

## Error Taxonomy

```json
{
  "cad_id": "cadfs__00890175",
  "B0_tags": [
    "CURVE_SHAPE_PARAMETER_ERROR",
    "GLOBAL_PLACEMENT_ERROR",
    "FEATURE_PARAMETER_ERROR"
  ],
  "M2_tags": [
    "CURVE_SHAPE_PARAMETER_ERROR",
    "GLOBAL_PLACEMENT_ERROR",
    "FEATURE_PARAMETER_ERROR"
  ],
  "B0_primary": "GLOBAL_PLACEMENT_ERROR",
  "M2_primary": "GLOBAL_PLACEMENT_ERROR"
}
```

## DSL

```text
GT:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.297044, -0.297044), (-0.297044, -0.297044), (-0.297044, 0.297044), (0.297044, 0.297044)], height=5.940885, axis=(0, 0, 1), origin=(0.297044, 0.297044, 0.0), x_axis=(1, 0, 0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.0, 0.0), (3.042854, 0.0), (3.042854, 4.640353), (0.0, 4.640353)], height=0.160939, axis=(0, 0, 1), origin=(0.0, 0.0, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.0, 0.0), (5.364632, 0.0), (5.364632, 2.682316), (0.0, 2.682316)], height=0.160939, axis=(0, 0, 1), origin=(0.0, 0.0, 0.0), x_axis=(1, 0, 0))
result = body_0
```
