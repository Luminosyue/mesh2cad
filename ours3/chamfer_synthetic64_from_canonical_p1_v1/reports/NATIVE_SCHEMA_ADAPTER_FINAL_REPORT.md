# P1_SYNTHETIC64_NATIVE_SCHEMA_COMPATIBILITY_ADAPTER_V1

CURRENT_GATE = CHAMFER_NATIVE_SCHEMA_BRIDGE_BLOCKED

The original P1 native schema and runtime are recovered. `edge_clouds` is produced from the frozen offline curve-token cache, not from raw curves or `curve_*.json`. The historical generator is `scripts/spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py`, which requires `curve_samples.npz` with the original curve sample arrays before running the frozen C2 checkpoint.

Synthetic64 currently contains `gt.step`, `curve_*.json`, and surface assets, but no native-schema `curve_samples.npz` or registered curve-token cache. Creating `edge_clouds` by padding, pooling, or copying raw curves would be invalid. Therefore no Synthetic64 native cache or registry was fabricated, and no original registry was modified.

P1_CHAMFER_TRAINING_STARTED = NO
NEXT_ALLOWED_STAGE = BUILD_READ_ONLY_CURVE_SAMPLES_NPZ_THEN_RUN_HISTORICAL_EXPORTER
