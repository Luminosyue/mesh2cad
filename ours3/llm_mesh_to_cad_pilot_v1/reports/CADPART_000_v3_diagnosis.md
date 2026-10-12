# CADPART_000 V3 Diagnosis

- `CAD_PARSE=PASS`, but `CAD_EXECUTION=FAIL`.
- CadQuery reports `BRepBuilderAPI_DisconnectedWire` while closing the mixed line/spline radial profile.
- Consequently no solid, STEP, reload, tessellation, or geometric comparison is claimed for V3.
- The failure is preserved as required. A V4 is not attempted because this pilot is capped at three rounds.
- V2 remains the best eligible result because it is the only version with successful STEP reload and complete geometry metrics.

