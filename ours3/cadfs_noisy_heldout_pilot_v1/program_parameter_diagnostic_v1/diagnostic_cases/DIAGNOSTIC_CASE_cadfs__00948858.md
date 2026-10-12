# Diagnostic Case cadfs__00948858

B0 and M2 differ geometrically despite similar operation-level signal; M2 geometry does not improve because matched placement/profile/feature values remain incorrect.

## Geometry Metrics

```json
{
  "gt_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/cadfs__00948858/target/cad_target.dsl",
  "b0_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/B0/cadfs__00948858.dsl",
  "m2_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/M2/cadfs__00948858.dsl",
  "gt_dsl_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/gt_dsl_step/cadfs__00948858.step",
  "b0_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0/step/cadfs__00948858.step",
  "m2_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2/step/cadfs__00948858.step",
  "b0_opf1": 1.0,
  "m2_opf1": 1.0,
  "b0_chamfer": 0.017976164692096733,
  "m2_chamfer": 0.02759706919121595,
  "b0_hausdorff95": 0.03063671210170925,
  "m2_hausdorff95": 0.05046505153523127,
  "b0_bbox_error": 0.039261932458624596,
  "m2_bbox_error": 0.07427822668478508
}
```

## Operation Alignment

```json
{
  "cad_id": "cadfs__00948858",
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
          -0.904534,
          0.904534
        ],
        [
          0.904534,
          0.904534
        ],
        [
          0.904534,
          -0.904534
        ],
        [
          -0.904534,
          -0.904534
        ]
      ],
      "pred": [
        [
          -0.912004,
          1.04117
        ],
        [
          0.74503,
          1.04117
        ],
        [
          0.74503,
          -0.615864
        ],
        [
          -0.912004,
          -0.615864
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 0.24135963182061848,
        "max": 0.32980584427205045
      },
      "normalized_error": 0.040226606145950854,
      "cad_id": "cadfs__00948858"
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
      "gt": 5.427204,
      "pred": 5.523448,
      "kind": "length",
      "raw_error": 0.09624400000000044,
      "normalized_error": 0.017733624901514748,
      "cad_id": "cadfs__00948858"
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
        0.904534,
        0.904534,
        0.0
      ],
      "pred": [
        0.912002,
        0.615858,
        0.0
      ],
      "kind": "position",
      "raw_error": 0.28877258180097354,
      "normalized_error": 0.04812876464151449,
      "cad_id": "cadfs__00948858"
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
      "cad_id": "cadfs__00948858"
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
      "cad_id": "cadfs__00948858"
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
          -0.904534,
          0.904534
        ],
        [
          0.904534,
          0.904534
        ],
        [
          0.904534,
          -0.904534
        ],
        [
          -0.904534,
          -0.904534
        ]
      ],
      "pred": [
        [
          -1.044466,
          1.044466
        ],
        [
          1.044466,
          1.044466
        ],
        [
          1.044466,
          -1.044466
        ],
        [
          -1.044466,
          -1.044466
        ]
      ],
      "kind": "points",
      "raw_error": {
        "mean": 0.19789373220999187,
        "max": 0.19789373220999187
      },
      "normalized_error": 0.03298228939245327,
      "cad_id": "cadfs__00948858"
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
      "gt": 5.427204,
      "pred": 5.22233,
      "kind": "length",
      "raw_error": 0.20487399999999933,
      "normalized_error": 0.037749456257770916,
      "cad_id": "cadfs__00948858"
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
        0.904534,
        0.904534,
        0.0
      ],
      "pred": [
        1.044466,
        1.044466,
        0.0
      ],
      "kind": "position",
      "raw_error": 0.19789373220999187,
      "normalized_error": 0.03298228939245327,
      "cad_id": "cadfs__00948858"
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
      "cad_id": "cadfs__00948858"
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
      "cad_id": "cadfs__00948858"
    }
  ]
}
```

## Error Taxonomy

```json
{
  "cad_id": "cadfs__00948858",
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
body_0 = ExtrudePolygon(points=[(-0.904534, 0.904534), (0.904534, 0.904534), (0.904534, -0.904534), (-0.904534, -0.904534)], height=5.427204, axis=(0, 0, 1), origin=(0.904534, 0.904534, 0.0), x_axis=(1, 0, 0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-0.912004, 1.04117), (0.74503, 1.04117), (0.74503, -0.615864), (-0.912004, -0.615864)], height=5.523448, axis=(0, 0, 1), origin=(0.912002, 0.615858, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-1.044466, 1.044466), (1.044466, 1.044466), (1.044466, -1.044466), (-1.044466, -1.044466)], height=5.22233, axis=(0, 0, 1), origin=(1.044466, 1.044466, 0.0), x_axis=(1, 0, 0))
result = body_0
```
