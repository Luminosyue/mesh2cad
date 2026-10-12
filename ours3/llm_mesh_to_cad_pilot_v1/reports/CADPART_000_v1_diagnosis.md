# CADPART_000 V1 Diagnosis

- `CAD_PARSE`, `CAD_EXECUTION`, `SOLID_VALID`, and `STEP_EXPORT` passed.
- `STEP_RELOAD` failed: the reloaded STEP solid collapsed to a degenerate axial extent and became invalid.
- Root cause is geometric-kernel tolerance: the source coordinates are normalized to roughly one unit while STEP/CadQuery interprets dimensions as millimetres; sub-millimetre spline features did not survive the round trip.
- V2 retains every geometric parameter and the REVOLVE route, but introduces a recorded, exactly invertible source-to-CAD work transform of `x1000`, followed by `x0.001` for the evaluation tessellation.
- No source vertices, faces, comparison region, or metric denominator are changed.

