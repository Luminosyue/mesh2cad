# Diagnostic Case cadfs__00984691

M2 improves the official operation multiset; M2 geometry does not improve because matched placement/profile/feature values remain incorrect.

## Geometry Metrics

```json
{
  "gt_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/cadfs__00984691/target/cad_target.dsl",
  "b0_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/B0/cadfs__00984691.dsl",
  "m2_pred_dsl_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/pred_dsl/M2/cadfs__00984691.dsl",
  "gt_dsl_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/geometry/gt_dsl_step/cadfs__00984691.step",
  "b0_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0/step/cadfs__00984691.step",
  "m2_pred_step_path": "/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2/step/cadfs__00984691.step",
  "b0_opf1": 0.0,
  "m2_opf1": 1.0,
  "b0_chamfer": 0.28380386344658864,
  "m2_chamfer": 0.41623177880124695,
  "b0_hausdorff95": 0.7811467406189239,
  "m2_hausdorff95": 0.8771594120683046,
  "b0_bbox_error": 1.0212035830644686,
  "m2_bbox_error": 1.2637121406446414
}
```

## Operation Alignment

```json
{
  "cad_id": "cadfs__00984691",
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
      "gt": 5.992724,
      "pred": 5.839977,
      "kind": "length",
      "raw_error": 0.15274699999999974,
      "normalized_error": 0.025488742681958946,
      "cad_id": "cadfs__00984691"
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
        0.104437,
        0.0,
        0.104435
      ],
      "pred": [
        0.486662,
        0.48666,
        0.0
      ],
      "kind": "position",
      "raw_error": 0.6275671879966319,
      "normalized_error": 0.10459464046882362,
      "cad_id": "cadfs__00984691"
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
        1,
        0
      ],
      "pred": [
        0,
        0,
        1
      ],
      "kind": "direction",
      "raw_error": null,
      "normalized_error": 90.0,
      "angle_error_deg": 90.0,
      "cad_id": "cadfs__00984691"
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
      "gt": 0.104453,
      "pred": 0.486665,
      "kind": "length",
      "raw_error": 0.382212,
      "normalized_error": 3.6591768546619052,
      "cad_id": "cadfs__00984691"
    }
  ]
}
```

## Error Taxonomy

```json
{
  "cad_id": "cadfs__00984691",
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
body_0 = Extrude(Circle(radius=0.104453), height=5.992724, axis=(0, 1, 0), origin=(0.104437, 0.0, 0.104435))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.0, 0.0), (5.364632, 0.0), (5.364632, 2.682316), (0.0, 2.682316)], height=0.160939, axis=(0, 0, 1), origin=(0.0, 0.0, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=0.486665), height=5.839977, axis=(0, 0, 1), origin=(0.486662, 0.48666, 0.0))
result = body_0
```
