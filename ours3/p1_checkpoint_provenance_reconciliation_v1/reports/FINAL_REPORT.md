# P1 checkpoint provenance reconciliation

CURRENT_GATE = P1_CHECKPOINT_PROVENANCE_RESOLVED
RESULT_PATTERN = HASH_SEMANTICS_CONFLICT_ONLY
P1_CHECKPOINT_IDENTITY_RESOLVED = YES
canonical_checkpoint_path = /data/home/cuiyuehan/project/mesh2cad/ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000
checkpoint_tree_sha256 = 0190418fb636dfe571a5310d0366cfa04400817bf73acdcd5e80d1469fcb9ab2
semantic_model_state_sha256 = dd9d05dc9636e4765375b05e21d6e0021240487f385c404d297280f517dd0677
semantic_curve_projector_sha256 = 3623a54672391482a199bbf3a853ff75f907b6057520648488c980bea066a566
strict_load = PASS
selection_rule = MIN_VAL_BASE_CE
selected_step = 8000
selected_val_base_ce = 0.5098320841789246
val1000_prediction_source_recovered = YES
test1000_reevaluated = NO
holdout958_used = NO

The single physical candidate strict-loads under the original architecture. Legacy opaque hashes remain semantically undefined and conflict; the canonical identity is therefore unresolved until the legacy hash definitions are reconciled. No training, inference, checkpoint writes, or old-file modifications were performed.
