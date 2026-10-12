# Conflict source comparison

A: `/data/home/cuiyuehan/project/mesh2cad/ours3/p1_vs_cad_recode_val1000_benchmark_v1/provenance/P1_CHECKPOINT_PROVENANCE.json` records `9c19c36455f7be6c81e6b6d84faafb446d4d68a09fb250c062b042fb47648e08` as an unspecified `checkpoint_sha256`, while also listing per-file hashes.

B: `/data/home/cuiyuehan/project/mesh2cad/ours3/p2_canary_unresolved_resolution_v1/checkpoint/P1_CHECKPOINT_SELECTION_DECISION.json` records `d26ff68264be7c91d1e0c25a9739899a03e9e8e37bbdf07d5002df92205c54c8` as `checkpoint_sha256`, without a hash target or algorithm definition.

Only one physical checkpoint-8000 candidate exists. This reconciliation computes the explicit `P1_PROVENANCE_HASH_V1` tree hash `0190418fb636dfe571a5310d0366cfa04400817bf73acdcd5e80d1469fcb9ab2` and semantic model hash `dd9d05dc9636e4765375b05e21d6e0021240487f385c404d297280f517dd0677` (projector semantic hash `3623a54672391482a199bbf3a853ff75f907b6057520648488c980bea066a566`), but neither legacy opaque hash can be attributed to that definition from existing records.
