# PART CAD FITTING V2

```json
{
  "TOTAL_PART_N": 209,
  "MAJOR_PART_N": 153,
  "V1_STRICT_N": 4,
  "V1_NEAR_N": 63,
  "V1_REJECT_N": 142,
  "NEAR_INPUT_N": 63,
  "NEAR_TO_STRICT_N": 9,
  "NEAR_STILL_NEAR_N": 52,
  "NEAR_TO_REJECT_N": 2,
  "NEAR_RESCUE_RATE": 0.14285714285714285,
  "TOP_NEAR_FAILURE_1": "WRONG_RADIUS",
  "TOP_NEAR_FAILURE_2": "WRONG_SKETCH_PROFILE",
  "TOP_NEAR_FAILURE_3": "WRONG_REVOLVE_PROFILE",
  "REJECT_INPUT_N": 142,
  "REJECT_TO_STRICT_N": 2,
  "REJECT_TO_NEAR_N": 18,
  "REJECT_STILL_REJECT_N": 122,
  "CAD_PARSE_PASS_N": 209,
  "CAD_EXECUTE_PASS_N": 209,
  "STEP_RELOAD_PASS_N": 209,
  "STRICT_ACCEPT_N": 15,
  "NEAR_PASS_N": 70,
  "REJECT_N": 124,
  "STRICT_ACCEPT_RATE": 0.07177033492822966,
  "MAJOR_PART_STRICT_N": 14,
  "MAJOR_PART_STRICT_RATE": 0.0915032679738562,
  "NCD_MEDIAN_V1": 0.01796431414406417,
  "NCD_MEDIAN_V2": 0.014963743191778662,
  "IoU_MEDIAN_V1": 0.6029508168063701,
  "IoU_MEDIAN_V2": 0.6767975969461191,
  "centroid_MEDIAN_V1": 0.02968992949426596,
  "centroid_MEDIAN_V2": 0.013539706904964968,
  "IMPROVED_N": 199,
  "UNCHANGED_N": 10,
  "WORSE_N": 0,
  "STRICT_RESCUE_N": 11,
  "STRICT_DAMAGE_N": 0,
  "PART_GEOMETRY_GATE": "FAIL",
  "CAN_START_REASSEMBLY_V2": "NO",
  "CAN_SCALE_TO_100_OBJECTS": "NO",
  "PRIMARY_REMAINING_BLOCKER": "Remaining strict failures {\"IoU\": 179, \"NCD\": 134, \"bbox\": 92, \"centroid\": 82}; limited profile/topology coverage and bounded local search",
  "NEXT_ALLOWED_STAGE": "IMPROVE_PART_CAD_FITTING",
  "FREEFORM_UNSUPPORTED_N": 21,
  "SIMPLE_PRIMITIVE_STRICT_RATE": 0.0,
  "EXTRUSION_STRICT_RATE": 0.047619047619047616,
  "REVOLVE_STRICT_RATE": 0.06666666666666667,
  "EXTRUDE_CUT_STRICT_RATE": 0.0,
  "BOOLEAN_STRICT_RATE": null,
  "MULTI_PRIMITIVE_STRICT_RATE": 0.0,
  "FRAME_BEAM_STRICT_RATE": 0.22857142857142856,
  "ATTEMPTED_CANDIDATE_N": 1552,
  "CANDIDATE_WITHOUT_FINAL_METRICS_N": 0,
  "EXECUTION_COUNT_SCOPE": "Selected final candidate per part; all attempted candidate failures remain in case records",
  "CLASSIFICATION_WORSE_N": 2,
  "REMAINING_FAILED_CHECK_COUNTS": {
    "IoU": 179,
    "NCD": 134,
    "bbox": 92,
    "centroid": 82
  }
}
```

## Changes and results

Same 20 objects, 209 P3 parts and 153 major parts. Source mesh bytes, original part/object transforms and normalizations are unchanged. Near-pass stage ran before any Reject fitting. New fitting adds bounded deterministic local scale/origin/rotation optimization, robust side-surface circle/cylinder fits, axial radial-profile refinement, stable closed-section fitting, and bounded primitive/component alternatives for rejected cases. Successful rescue methods: {"coordinate_descent_strict": 6, "coordinate_descent_balanced": 1, "axial_profile_refit": 1, "local_search_alternative": 1, "stable_section_with_supported_cuts": 2}.

Historical pipeline.py and build_partsam_p1.py were read and copied, never run with their original output paths. Their axis/profile/loft/primitive enumeration informed the new emitters; their older 512-point ranking was not substituted for the frozen evaluator.

## Comparison definitions

Candidate 0 is the V1 geometry, STEP reimported and the frozen STEP-derived tessellation rescored with identical seeds; all baseline numerical drift is recorded. New candidates use fresh native CQ execution -> STEP export -> reload tessellation. Eight candidates include baseline. Primitive count <=8, Boolean count <=6, bounded sketches <=96. No case-ID-specific numerical conditions, mesh import CAD, source normalization changes, P3/X-Part inference or training. No source object reselection.

IMPROVED means strict rescue or reduction in the declared score; UNCHANGED means score difference <=1e-8; WORSE means score increases without strict rescue. This is not a claim that every individual metric improved. Family tables group both V1 and V2 outcomes by the same V2 family assignment, allowing paired comparisons. Per-case planning labels are deterministic reconciliations under an interactive-assistant-authored structure policy; no independent per-part LLM API calls are claimed.

## Limits

The fixed-grid optimization proxy is approximate and may disagree with final IoU128. Acceptance always uses the original evaluator, itself an approximate scan-fill voxel metric, not exact Boolean solid IoU. Surface centroid differences can persist for open segmentation surfaces and closed CAD. Error labels are hypotheses from measured evidence. Hole/protrusion and Boolean-order causes without sufficient evidence remain unasserted; zero taxonomy counts do not prove absence. General connected frame-graph decomposition and arbitrary constructive-solid-geometry search are not implemented. H-family rejected outputs are diagnostic baselines, not accepted training CAD.

Strict baseline cases remain preserved. Full-object coverage is only predicted from major-part strict status; no assembly was performed. Do not interpret this as verified whole-object quality.

## Storage

All V2 results are on /data under outputs/part_cad_fitting_v2. The temporary /var/tmp attempt was removed at the user request. Separately and explicitly authorized, nine historical optimizer.pt files were deleted to free about 83 GiB; model weights were retained. This exception is distinct from the CAD input/output read-only guard.


# Corrected Near-stage rescue analysis

Corrected Near cohort: 9 Strict, 52 Near, 2 Reject; rescue rate 14.29%.

The initial scalar-serialization parser defect prevented numeric candidates from running. It has been fixed and affected candidates rebuilt with identical parameter values. Initial reports are superseded, not treated as geometric evidence.

Remaining failed strict checks (overlapping): {'NCD': 19, 'bbox': 25, 'IoU': 40, 'centroid': 13}. Baseline selected in 5 cases. Successful methods: {'coordinate_descent_strict': 6, 'coordinate_descent_balanced': 1, 'axial_profile_refit': 1, 'local_search_alternative': 1}.

Three bounded coordinate sweeps and fixed structure limit the reachable shapes. The warped IoU64/4000-point optimization proxy can disagree with reloaded IoU128/20000-point evaluation, especially for thin geometry. This is a limitation, not proof of a global optimum.

Closed-section extraction can fail or miss topology. An inspected numerical Strict rescue closes a visible source opening. Open segmentation surfaces versus closed CAD can also cause a centroid mismatch; these issues need topology-aware fitting rather than looser thresholds.

The weighted ranking produces 2 Near-to-Reject changes despite score improvement; these are explicitly reported as classification regressions.

Continue the authorized 142 Reject cases with bounded structure alternatives only after this corrected Near analysis. No new objects, threshold changes, training or assembly.


# Numeric serialization defect and repair

A candidate-level audit found native CAD parser failures caused by NumPy scalar repr emitting `np.float64(...)` in generated numeric expressions. This was an implementation defect, not evidence that the geometry family could not fit. The initial 5/63 Near rescue count and the first low-yield explanation were provisional and are superseded by the repaired rescore.

The code generator now converts NumPy arrays and scalars to ordinary Python literals. Regression checks cover the six native kinds present in this dataset: extrusion, extrusion with cuts, box, cylinder, section loft and revolve. The original restricted native-CAD validator is unchanged.

Already generated failing candidates are repaired by replacing scalar wrappers with the exact numeric argument, retaining candidate IDs and fitted parameter vectors. Their failed code and execution records are retained beside the corrected records. They are rebuilt, exported, reloaded and rescored with the same frozen evaluator. This does not add structural candidates or increase the eight-candidate budget. The Reject run was paused until Near repair and review finish. Interrupted executions are archived before resumption.

Candidate records contain `numeric_serialization_repair`; per-case pre-repair results and the initial Near reports are retained under explicit pre-repair names. Final counts must come from reports/summary.json after repair. The final validator checks every active candidate against the native AST validator, including candidates that were not selected.


# Visual fidelity limits

object_00004/part_005 meets the fixed Strict numerical gate, but the rendered source has a visible central opening that V2 closes. Cross-section features did not identify a stable nested hole; source openness versus a true design hole is unresolved. Numerical Strict is not a certification of topology or every high-detail feature. Keep this case under manual topology review before training use. No acceptance threshold or status has been silently changed.

object_00002/part_013 shows a closer outline after bounded parameter fitting. object_00014/part_002 improves IoU and NCD but remains Near due to other strict checks.
