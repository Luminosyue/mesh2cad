# Corrected M2 Fresh Train V1 — blocked at step-1 gate

CURRENT_GATE = M2_CORRECTED_STEP1_PROJECTOR_UPDATE_BLOCKED

CORRECTED_M2_TRAINING_COMPLETE = NO

M2_FINAL_EVAL_ELIGIBLE = NO

NEXT_STEP = resolve step1 warmup semantics without changing frozen B0 optimization protocol

The fresh run loaded the pristine B0 base, registered the 592,128-parameter CurveProjector, used exact registry lookup, and began at global step 0. The step-1 audit found finite nonzero projector gradients and an unchanged Frozen C2 hash. However, the first AdamW call used LR 0.0 under the inherited B0 warmup/scheduler ordering, so the projector hash did not change after step 1.

The run was stopped at approximately step 96, before checkpoint-250. No checkpoint audit or final evaluation was performed. Test remained untouched.

Changing LR, warmup, or scheduler ordering would violate the frozen B0 comparison protocol, while continuing would violate the explicit requirement that `PROJECTOR_UPDATED_AFTER_STEP1 = YES`. The run is therefore blocked pending an explicit protocol decision.
