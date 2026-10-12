# CASE09 P3-conditioned PhysX Segment Labeling V2

| P3_SEGMENT | GEOMETRY_GT_FOR_EVAL_ONLY | OLD_PHYSX_LABEL | NEW_PHYSX_LABEL | CONFIDENCE | STATUS | OUTPUT_CONTRACT_OK |
|---|---|---|---|---|---|---|
| P3_SEG_000 | vertical_stabilizer | Tail wing (left) | vertical_stabilizer | 0.77 | ACCEPTED | true |
| P3_SEG_001 | propeller | Tail wing (left) | propeller | 0.75 | ACCEPTED | true |
| P3_SEG_002 | main_wing_left | Horizontal Stabilizer (Right) | main_wing_left | 0.76 | ACCEPTED | true |
| P3_SEG_003 | propeller | External Fuel Tank | propeller | 0.76 | ACCEPTED | true |
| P3_SEG_004 | main_wing_right | Horizontal Stabilizer (Right) | main_wing_right | 0.76 | ACCEPTED | true |
| P3_SEG_005 | horizontal_stabilizer_right | Tail wing (left) | horizontal_stabilizer_right | 0.74 | ACCEPTED | true |
| P3_SEG_006 | dorsal_feature | Horizontal Stabilizer (Right) | dorsal_feature | 0.78 | ACCEPTED | true |
| P3_SEG_007 | horizontal_stabilizer_left | Tail wing (left) | horizontal_stabilizer_left | 0.74 | ACCEPTED | true |
| P3_SEG_008 | fuselage | Horizontal Stabilizer (Right) | fuselage | 0.77 | ACCEPTED | true |
| P3_SEG_009 | dorsal_feature | Horizontal Stabilizer (Right) | dorsal_feature | 0.74 | ACCEPTED | true |

## Evaluation-only semantic accuracy

- family_accuracy: 1.000000
- exact_accuracy: 1.000000
- GEOMETRY_GT_FOR_EVAL_ONLY was not sent to PhysX or reconstruction.

## Contract gate

```json
{
  "WHOLE_OBJECT_PARTS_TABLE_USED": false,
  "FIRST_L0_BINDING_USED": false,
  "P3_SEGMENT_COUNT_CHANGED": false,
  "SEGMENT_SPECIFIC_OUTPUT_RATE": 1.0,
  "MULTI_PART_OUTPUT_ACCEPTED": false,
  "PHYSX_DIMENSIONS_USED": false,
  "eval_gt_fed_to_model": false,
  "eval_gt_fed_to_reconstruction": false,
  "frozen_physx_modified": false,
  "frozen_p3_segment_count": 10,
  "output_segment_count": 10,
  "GATE_PASS": true,
  "family_accuracy": 1.0,
  "exact_accuracy": 1.0,
  "elapsed_seconds": 252.2353639602661,
  "checkpoint": "/data/home/cuiyuehan/project/mesh2cad/PhysX-Omni/pretrain",
  "checkpoint_index_sha256": "3067e9b0f35596ff3426a0d0ec8c982a51fa1e110c4fc30dcf3be9ea37409df6",
  "inference_mode": "PHYSX_MULTI_VIEW_LIKELIHOOD_WITH_AUTHORITATIVE_GEOMETRY_CONSTRAINT",
  "freeform_output_used_for_binding": false,
  "strict_retry_policy_implemented": true,
  "geometry_gt_for_eval_only_used_in_inference": false
}
```
