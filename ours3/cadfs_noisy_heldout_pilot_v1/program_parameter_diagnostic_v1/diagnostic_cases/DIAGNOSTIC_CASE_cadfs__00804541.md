# Diagnostic Case cadfs__00804541

B0 and M2 differ geometrically despite similar operation-level signal; M2 geometry does not improve because matched placement/profile/feature values remain incorrect.

## Geometry Metrics

```json
{
  "gt_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/cadfs__00804541/target/cad_target.dsl",
  "b0_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/B0/cadfs__00804541.dsl",
  "m2_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/M2/cadfs__00804541.dsl",
  "gt_dsl_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/gt_dsl_step/cadfs__00804541.step",
  "b0_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0/step/cadfs__00804541.step",
  "m2_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2/step/cadfs__00804541.step",
  "b0_opf1": 1.0,
  "m2_opf1": 1.0,
  "b0_chamfer": 0.029371803058284157,
  "m2_chamfer": 0.0551805410464104,
  "b0_hausdorff95": 0.10188737041611545,
  "m2_hausdorff95": 0.22932767723154174,
  "b0_bbox_error": 0.11236517384302569,
  "m2_bbox_error": 0.25982676707642866
}
```

## Operation Alignment

```json
{
  "cad_id": "cadfs__00804541",
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
          -0.880066,
          1.279926
        ],
        [
          1.1676,
          1.279926
        ],
        [
          1.1676,
          -4.192072
        ],
        [
          -0.880066,
          -4.192072
        ]
      ],
      "pred": [
        [
          1.329,
          -2.623026
        ],
        [
          -1.329,
          -2.623026
        ],
        [
          -1.329,
          2.623026
        ],
        [
          1.329,
          2.623026
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 5.88502094669539,
        "max": 7.258000572444452
      },
      "normalized_error": 0.9808473599995149,
      "cad_id": "cadfs__00804541"
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
      "gt": 1.365111,
      "pred": 1.189105,
      "kind": "length",
      "raw_error": 0.17600599999999988,
      "normalized_error": 0.12893163999118012,
      "cad_id": "cadfs__00804541"
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
        0.880109,
        4.192158,
        0.0
      ],
      "pred": [
        1.329,
        2.623026,
        0.0
      ],
      "kind": "position",
      "raw_error": 1.6320779280735955,
      "normalized_error": 0.27201590980969587,
      "cad_id": "cadfs__00804541"
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
      "cad_id": "cadfs__00804541"
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
      "cad_id": "cadfs__00804541"
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
          -0.880066,
          1.279926
        ],
        [
          1.1676,
          1.279926
        ],
        [
          1.1676,
          -4.192072
        ],
        [
          -0.880066,
          -4.192072
        ]
      ],
      "pred": [
        [
          -1.755025,
          -2.052803
        ],
        [
          1.673602,
          -2.052803
        ],
        [
          1.673602,
          2.747275
        ],
        [
          -1.755025,
          2.747275
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 5.192163148489361,
        "max": 6.994289816563938
      },
      "normalized_error": 0.8653698199226068,
      "cad_id": "cadfs__00804541"
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
      "gt": 1.365111,
      "pred": 1.097161,
      "kind": "length",
      "raw_error": 0.2679499999999999,
      "normalized_error": 0.19628440471141168,
      "cad_id": "cadfs__00804541"
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
        0.880109,
        4.192158,
        0.0
      ],
      "pred": [
        1.755006,
        2.052777,
        0.0
      ],
      "kind": "position",
      "raw_error": 2.311362330698067,
      "normalized_error": 0.3852311929901564,
      "cad_id": "cadfs__00804541"
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
      "cad_id": "cadfs__00804541"
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
      "cad_id": "cadfs__00804541"
    }
  ]
}
```

## Error Taxonomy

```json
{
  "cad_id": "cadfs__00804541",
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
body_0 = ExtrudePolygon(points=[(-0.880066, 1.279926), (1.1676, 1.279926), (1.1676, -4.192072), (-0.880066, -4.192072)], height=1.365111, axis=(0, 0, 1), origin=(0.880109, 4.192158, 0.0), x_axis=(1, 0, 0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(1.329, -2.623026), (-1.329, -2.623026), (-1.329, 2.623026), (1.329, 2.623026)], height=1.189105, axis=(0, 0, 1), origin=(1.329, 2.623026, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-1.755025, -2.052803), (1.673602, -2.052803), (1.673602, 2.747275), (-1.755025, 2.747275)], height=1.097161, axis=(0, 0, 1), origin=(1.755006, 2.052777, 0.0), x_axis=(1, 0, 0))
result = body_0
```
