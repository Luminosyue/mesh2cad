# Near-pass Rescue V2

```json
{
  "NEAR_INPUT_N": 63,
  "NEAR_TO_STRICT_N": 9,
  "NEAR_STILL_NEAR_N": 52,
  "NEAR_TO_REJECT_N": 2,
  "NEAR_RESCUE_RATE": 0.14285714285714285,
  "primary_failure_counts": {
    "WRONG_REVOLVE_PROFILE": 13,
    "CENTROID_ALIGNMENT_ERROR": 2,
    "WRONG_RADIUS": 27,
    "WRONG_SKETCH_PROFILE": 17,
    "PARAMETER_ONLY_ERROR": 4
  },
  "effective_fixes": {
    "coordinate_descent_strict": 6,
    "coordinate_descent_balanced": 1,
    "axial_profile_refit": 1,
    "local_search_alternative": 1
  },
  "baseline_reproduction_max_error": 0.0
}
```

Initial failure labels are evidence-based hypotheses, not proven causes. Multiple failed thresholds can coexist. The full original 63-case cohort was retained. V1 programs and reloaded-STEP meshes remain an explicit candidate-0 baseline. Surface source points use the original seeds and 20,000-point protocol.

The optimizer updates explicit native CAD plane origins/orientations and sketch/depth/radius parameters. Coarse occupancy warping and fixed point subsets only propose candidates; no proxy metric can grant strict acceptance. Every new final candidate is executed, exported to STEP, reloaded and evaluated with the unchanged metric implementation.

Diagnosis counts: {"WRONG_REVOLVE_PROFILE": 13, "CENTROID_ALIGNMENT_ERROR": 2, "WRONG_RADIUS": 27, "WRONG_SKETCH_PROFILE": 17, "PARAMETER_ONLY_ERROR": 4}. Successful selected methods: {"coordinate_descent_strict": 6, "coordinate_descent_balanced": 1, "axial_profile_refit": 1, "local_search_alternative": 1}.

Remaining limitations include missing or changing section topology, open source surfaces with a surface centroid different from a closed solid, and a limited compact-family library. The bounded search does not prove a global optimum.


# Corrected Near-stage rescue analysis

Corrected Near cohort: 9 Strict, 52 Near, 2 Reject; rescue rate 14.29%.

The initial scalar-serialization parser defect prevented numeric candidates from running. It has been fixed and affected candidates rebuilt with identical parameter values. Initial reports are superseded, not treated as geometric evidence.

Remaining failed strict checks (overlapping): {'NCD': 19, 'bbox': 25, 'IoU': 40, 'centroid': 13}. Baseline selected in 5 cases. Successful methods: {'coordinate_descent_strict': 6, 'coordinate_descent_balanced': 1, 'axial_profile_refit': 1, 'local_search_alternative': 1}.

Three bounded coordinate sweeps and fixed structure limit the reachable shapes. The warped IoU64/4000-point optimization proxy can disagree with reloaded IoU128/20000-point evaluation, especially for thin geometry. This is a limitation, not proof of a global optimum.

Closed-section extraction can fail or miss topology. An inspected numerical Strict rescue closes a visible source opening. Open segmentation surfaces versus closed CAD can also cause a centroid mismatch; these issues need topology-aware fitting rather than looser thresholds.

The weighted ranking produces 2 Near-to-Reject changes despite score improvement; these are explicitly reported as classification regressions.

Continue the authorized 142 Reject cases with bounded structure alternatives only after this corrected Near analysis. No new objects, threshold changes, training or assembly.
