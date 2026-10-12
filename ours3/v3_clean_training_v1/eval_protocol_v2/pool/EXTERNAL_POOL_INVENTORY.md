# External pool inventory

This is a read-only asset inventory, not a clean-gate pass. `new_base_complete` means only that STEP, OBJ, DSL, transform, and 7D features exist. Tessellation, real V3 context, GT execution, curve/C2, and leakage/fingerprint gates remain to be run before any candidate is used.

{
  "DeepCAD": {
    "total_available": 2209,
    "already_in_v3_800": 594,
    "already_in_train688": 594,
    "new_candidates": 1615,
    "new_base_complete": 1600,
    "missing_asset_counts": {
      "model_step": 10,
      "model_obj": 14,
      "dsl": 15,
      "transform": 15,
      "features_7d": 15
    }
  },
  "Fusion360": {
    "total_available": 635,
    "already_in_v3_800": 94,
    "already_in_train688": 94,
    "new_candidates": 541,
    "new_base_complete": 508,
    "missing_asset_counts": {
      "model_step": 11,
      "model_obj": 11,
      "dsl": 33,
      "transform": 33,
      "features_7d": 33
    }
  },
  "CADFS": {
    "total_available": 334,
    "already_in_v3_800": 0,
    "already_in_train688": 0,
    "new_candidates": 334,
    "new_base_complete": 334,
    "missing_asset_counts": {}
  }
}
