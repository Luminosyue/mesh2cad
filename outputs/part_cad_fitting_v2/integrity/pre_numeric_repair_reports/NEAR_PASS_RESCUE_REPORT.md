# Near-pass Rescue V2

```json
{
  "NEAR_INPUT_N": 63,
  "NEAR_TO_STRICT_N": 5,
  "NEAR_STILL_NEAR_N": 58,
  "NEAR_TO_REJECT_N": 0,
  "NEAR_RESCUE_RATE": 0.07936507936507936,
  "primary_failure_counts": {
    "WRONG_REVOLVE_PROFILE": 13,
    "CENTROID_ALIGNMENT_ERROR": 2,
    "WRONG_RADIUS": 27,
    "WRONG_SKETCH_PROFILE": 17,
    "PARAMETER_ONLY_ERROR": 4
  },
  "effective_fixes": {
    "coordinate_descent_strict": 3,
    "coordinate_descent_balanced": 1,
    "axial_profile_refit": 1
  },
  "baseline_reproduction_max_error": 0.0
}
```

Initial failure labels are evidence-based hypotheses, not proven causes. Multiple failed thresholds can coexist. The full original 63-case cohort was retained. V1 programs and reloaded-STEP meshes remain an explicit candidate-0 baseline. Surface source points use the original seeds and 20,000-point protocol.

The optimizer updates explicit native CAD plane origins/orientations and sketch/depth/radius parameters. Coarse occupancy warping and fixed point subsets only propose candidates; no proxy metric can grant strict acceptance. Every new final candidate is executed, exported to STEP, reloaded and evaluated with the unchanged metric implementation.

Diagnosis counts: {"WRONG_REVOLVE_PROFILE": 13, "CENTROID_ALIGNMENT_ERROR": 2, "WRONG_RADIUS": 27, "WRONG_SKETCH_PROFILE": 17, "PARAMETER_ONLY_ERROR": 4}. Successful selected methods: {"coordinate_descent_strict": 3, "coordinate_descent_balanced": 1, "axial_profile_refit": 1}.

Remaining limitations include missing or changing section topology, open source surfaces with a surface centroid different from a closed solid, and a limited compact-family library. The bounded search does not prove a global optimum.
