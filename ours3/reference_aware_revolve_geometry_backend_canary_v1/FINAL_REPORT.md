# Reference-aware Revolve Geometry Backend Canary V1

`CURRENT_GATE=REVOLVE_BACKEND_FAIL`

The backend now has explicit entity validation, deterministic wire ordering, axis normalization, and a true CadQuery revolve entry point for canonical profile geometry. The frozen Canary10 cannot enter the kernel: source query entities still lack canonical loop membership, sketch-frame transforms, and executable axis coordinates. All ten cases therefore stop at precondition; no STEP or geometry comparison is produced, and no approximation or source-STEP passthrough is accepted.
