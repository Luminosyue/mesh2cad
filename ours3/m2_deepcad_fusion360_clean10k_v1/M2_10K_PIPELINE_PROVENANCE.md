# M2_DEEPCAD_FUSION360_CLEAN10K_V1 provenance gate

`CURRENT_GATE = M2_10K_PIPELINE_PROVENANCE_FAIL`

The real frozen V3/M2 code path and the existing disk provenance agree on:

`STEP -> OCC tessellation -> clean mesh -> uniform 8192x6 surface sampling`

No mentor-noise call, implementation, or frozen noise configuration is present in the original M2 geometry-pack, V3 adapter, or clean-training modules. Adding CADFS N2 or writing a new noise implementation would violate the contract. Therefore source cleaning, Canary40, pilot500, full-pool build, training, and decode were not started.

Next action requires one protocol clarification: either reproduce the actual original clean-surface M2 pipeline, or supply the exact formal mentor-noise implementation path and config SHA256.
