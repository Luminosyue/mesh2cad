# Reject CAD Repair V3

```json
{
  "TOTAL_PART_N": 209,
  "REPAIR_INPUT_N": 124,
  "PRESERVED_NON_REJECT_N": 85,
  "V2_STRICT_N": 15,
  "V2_NEAR_N": 70,
  "V2_REJECT_N": 124,
  "REJECT_TO_STRICT_N": 0,
  "REJECT_TO_NEAR_N": 7,
  "REJECT_STILL_REJECT_N": 117,
  "STRICT_ACCEPT_N": 15,
  "NEAR_PASS_N": 77,
  "REJECT_N": 117,
  "STRICT_ACCEPT_RATE": 0.07177033492822966,
  "MAJOR_STRICT_N": 14,
  "MAJOR_STRICT_RATE": 0.0915032679738562,
  "CLASSIFICATION_DAMAGE_N": 0,
  "SCORE_IMPROVED_N": 91,
  "SCORE_WORSE_N": 3,
  "ATTEMPTED_CANDIDATE_N": 471,
  "CANDIDATE_WITH_METRICS_N": 471,
  "SELECTED_STEP_RELOAD_PASS_N": 209,
  "PART_GEOMETRY_GATE": "FAIL",
  "CAN_START_REASSEMBLY": "NO",
  "CAN_SCALE_TO_100_OBJECTS": "NO",
  "NEXT_ALLOWED_STAGE": "IMPROVE_PART_CAD_FITTING",
  "V2_IoU_MEDIAN": 0.6767975969461191,
  "V3_IoU_MEDIAN": 0.6917446723760207,
  "V2_NCD_MEDIAN": 0.014963743191778662,
  "V3_NCD_MEDIAN": 0.014182424246242038,
  "V2_centroid_MEDIAN": 0.013539706904964968,
  "V3_centroid_MEDIAN": 0.010559633345438513,
  "V2_bbox_MEDIAN": 0.025328727439045906,
  "V3_bbox_MEDIAN": 0.02936746850502626,
  "remaining_failed_check_counts": {
    "IoU": 179,
    "NCD": 134,
    "bbox": 104,
    "centroid": 43
  },
  "SELECTED_PARSE_PASS_N": 209,
  "SELECTED_EXECUTE_PASS_N": 209,
  "REPAIR_SOURCE_OPEN_BOUNDARY_N": 122,
  "NO_CLOSED_GEOMETRY_PROPOSAL_N": 44
}
```

## Scope and validation

Only the 124 V2 Reject parts were fitted. All 15 Strict and 70 Near parts are copied byte-for-byte from V2. Original mesh, transforms, frozen source samples, seeds, 20000-point metric and IoU128 acceptance thresholds are unchanged. No P3, training, reassembly or expansion. Twelve CPU workers; no GPU inference. Every repaired part retains the V2 CAD baseline, reimports its STEP and reproduces its prior metrics.

## Fitting changes

Candidate proposals include measured closed-section extrusions, three-section lofts with consistent hole topology, and measured inner/outer revolution profiles. Repeated section topology must match; unsupported profiles and excess complexity are recorded, not silently dropped. One refinement starts from the actual V2 winner. Geometry proxies rank proposals before at most seven new native CAD executions per part; the baseline makes at most eight candidates. At most eight primitives, six Booleans and 96 sketch vertices. Proxy metrics never grant acceptance.

The final ranking is Strict, then Near, then Reject, followed by the unchanged weighted score (10*NCD + 1-IoU + 2*centroid + bbox). This prevents classification regression but can raise the weighted score when moving to a better class; score and classification changes are reported separately. Family labels describe the selected candidate; complex sketches, holes and union structure should be inspected in the native program.

## Limits

Open or inconsistent source sections often cannot support a closed solid profile; the library does not implement arbitrary freeform surfaces, automatic connected-frame decomposition or arbitrary CSG. Loft endpoint sections extrapolate the observed 3% and 97% sections to measured extent endpoints, so shape errors remain possible. Section-based profiles and finite candidate ranking do not establish a global optimum. Numerical Strict does not certify all small details or topology; the V2 opening discrepancy remains part of the preserved baseline limitations. No per-part LLM API calls are claimed: the assistant authored the construction policy, and geometry code fitted the numeric parameters.

The 12-case pilot was reviewed before the remaining cohort, and its outcomes were reused. V2 is read-only; integrity/VALIDATION.json records its complete guard. Recovered and remaining-reject comparisons are available in visualizations/index.html.


## Observed outcome and visual limitations

This round adds zero Strict parts. Seven numerical Near promotions must not be described as new strictly qualified CAD. Of the 124 repaired source parts, 122 have open boundary edges; 44 produce no supported closed-geometry proposal, leaving local parameter refinement only. Open boundaries are evidence of fitting difficulty, not proof that a part is impossible to reconstruct.

Visual inspection of object_00011/part_018 shows a lost end protrusion even though main-beam IoU and NCD improve. object_00002/part_002 still simplifies angular details. object_00017/part_002 receives a rotational candidate that remains visibly inconsistent with its asymmetric source and correctly remains Reject. These observations show that missing small features and wrong CAD family remain blockers alongside source openness. Numerical Near is an analysis label, not acceptance for training or assembly.

The overall bbox-error median worsens from 0.025329 to 0.029367, while NCD, IoU and centroid medians improve. Three cases have a worse weighted score because ranking prioritizes promotion from Reject to Near. There is no classification regression; all prior Strict and Near outputs remain byte-for-byte preserved. Keep V2 as the immutable comparison, and use these outputs as diagnostic experiments.

The next fitting investigation should preserve observed protrusions and holes while reconstructing supported boundaries and selecting appropriate compound structures. Thresholds and original input meshes remain unchanged.
