# Fusion360 DSL STEP Hard Failure Root Cause V1

{
  "TOTAL_FUSION360": 160,
  "CURRENT_GEOMETRY_ELIGIBLE": 132,
  "HARD_FAILURE": 28,
  "CURRENT_GEOMETRY_YIELD": 0.825,
  "STEP_EXPORT_FAIL": 28,
  "SOURCE_STEP_VALID": 28,
  "RECOVERABLE_N": 0,
  "BLOCKED_N": 28,
  "MIN_RECOVERY_REQUIRED": 13,
  "SAFE_RECOVERY_TARGET": 16,
  "CONTEXT_OVERFLOW": 58,
  "TRAINING_RUN": "NO",
  "DECODE_RUN": "NO",
  "DORA_RUN": "NO",
  "FULL8625_STARTED": "NO",
  "PROJECT_SOURCE_CHANGED": "NO",
  "CURRENT_GATE": "FUSION360_GEOMETRY_RECOVERY_INSUFFICIENT_FOR_10K",
  "FULL8625_ALLOWED": "NO",
  "TRAINING_APPROVED": "NO",
  "root_cause_categories": {
    "RECOVERABLE_PIPELINE_BUG": 0,
    "RECOVERABLE_EXECUTOR_BUG": 0,
    "RECOVERABLE_NUMERICAL_ISSUE": 0,
    "REPRESENTATION_LIMIT": 0,
    "TRUE_SOURCE_INVALID": 0,
    "BLOCKED_MISSING_SOURCE_EVIDENCE": 28
  },
  "note": "No formal source, DSL, C2, surface, curve, tokenizer, loader, model, context, or cap change."
}

All 28 hard failures remain denominator-preserving and are blocked pending intermediate BRep/traceback evidence. No formal patch or scratch recovery was run.
