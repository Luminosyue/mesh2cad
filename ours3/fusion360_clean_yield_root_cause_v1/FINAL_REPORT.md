# Fusion360 Clean Yield Root Cause V1

{
  "audit": "FUSION360_CLEAN_YIELD_ROOT_CAUSE_V1",
  "generated_utc": "2026-09-06T08:17:54.734682Z",
  "denominator": 160,
  "historical_clean": 94,
  "historical_removed": 66,
  "geometry_eligible_n": 132,
  "geometry_eligible_yield": 0.825,
  "training_ready_n": 90,
  "training_ready_yield": 0.5625,
  "context_overflow_n": 58,
  "overlap_n": 0,
  "hard_invalid_n": 28,
  "policy_exclusion_n": 42,
  "curve_cap": 128,
  "current_gate": "FUSION360_CLEAN_YIELD_INSUFFICIENT_FOR_10K",
  "data_cleaning_protocol_frozen": true,
  "full8625_allowed": false,
  "training_approved": false,
  "training_run": false,
  "decode_run": false,
  "dora_run": false,
  "model_changed": false,
  "c2_changed": false,
  "dsl_changed": false,
  "context_limit_changed": false,
  "next_step": "M2_CLEAN10K_CONTEXT_BUDGET_DECISION_V1 or FUSION360_DSL_STEP_FAILURE_ROOT_CAUSE_V1",
  "note": "Audits replay existing official assets; no producer, C2, DSL, STEP, surface or curve rerun was executed."
}

All 160 cases retain denominator 160. Geometry eligibility and training-ready eligibility are reported separately.
