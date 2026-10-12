# Canary20 Phase-B path blocker

- **SURFACE_LOADER_PATH:** `scripts/spatiallm_curve_token_v1/heldout_geometry.py`
- **DATASET_INFERENCE_FUNCTION:** `spatiallm_curve_token_v1.surface_cache.cad_key_from_surface_path`
- **SONATA_FORWARD_FUNCTION:** `SpatialLMLlamaForCausalLM.forward_point_cloud`
- **OLD_EXPECTED_INPUT:** `surface_points.npy` `(8192,6)` -> frozen 4096-point index policy -> test-mode V3 voxel tensor `(N,9)`.

Root cause: `_install_best_v2._load_cad_separate_edge` calls `SurfaceIndexCache.indices_for`, which calls `cad_key_from_surface_path`; that function assumes the third parent is `DeepCAD` or `Fusion360`. The isolated Canary path does not have that layout. Legacy code is unchanged; Phase-B uses `v3_canary_surface_adapter.load_surface_for_encoder` with manifest dataset/sample identity.
