# Tank45 training state audit

BASE_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000
RESUME_MODE=weights-only model load into a new Trainer run
WEIGHTS_ONLY_LOAD=YES
OPTIMIZER_STATE_RESTORED=NO
SCHEDULER_STATE_RESTORED=NO
GLOBAL_STEP_RESTORED=NO (training started at 0 and ended at 1000)

CONFIGURED_LR=1e-5
ACTUAL_LR_AT_START=1e-5
ACTUAL_LR_AT_1000=1e-5
SCHEDULER_TYPE=constant
WARMUP_STEPS=0
LR_STATE_BUG=NO
UNINTENDED_OPTIMIZER_RESUME=NO

MICRO_BATCH_SIZE=1
GRAD_ACCUM_STEPS=3
TOTAL_OPTIMIZER_UPDATES=1000
RECORDED_MICRO_BATCH_EXPOSURE_EVENTS=2925 (65 complete 45-part cycles); with GRAD_ACCUM_STEPS=3 and GLOBAL_STEP=1000, 3000 microbatches would be expected. This is an exposure-trace accounting mismatch, not evidence that the Trainer optimizer step count was 975.
MIN_PART_EXPOSURE=65
MAX_PART_EXPOSURE=65
BALANCED_EXPOSURE=YES at the saved exposure snapshot
UPDATE_COUNT_MISMATCH=YES for the recorded microbatch trace (2925 vs expected 3000)

TOTAL_GT_TOKEN_N=2235061
MIN_SUPERVISION_COVERAGE=1.0
MAX_SUPERVISION_COVERAGE=1.0
TARGET_TRUNCATION_BUG=NO evidence
CHUNK_COVERAGE_BUG=NO (block-level records cover all 2226 blocks; every block target ends in EOS)
LABEL_MASK_BUG=NO evidence; active labels equal prepared target tokens and EOS is active

LOSS_REDUCTION_MODE=standard causal CE over active labels
TOKEN_WEIGHT_IMBALANCE=YES in the sense that equal block/part exposure is not equal total-token exposure; this was measured, not corrected in this audit

TRAINABLE_PARAM_N=1237719808
TRAINABLE_PARAMETER_MISMATCH=NO (same frozen point tower / trainable language+projector scope as FAST)
SURFACE_INPUT_DTYPE=torch.float32 at projector prehook under BF16 autocast; CURVE_INPUT_DTYPE=torch.float32; gate path remains FP32 deterministic

TF_ERROR_AT_50=668648
TF_ERROR_AT_1000=528093
TF_ZERO_ERROR_AT_50=0/45
TF_ZERO_ERROR_AT_1000=5/45

ROOT_CAUSE=TRAINING_IS_CORRECT_BUT_MEMORIZATION_INCOMPLETE, with insufficient per-block coverage for long parts under equal-part exposure; additionally the exposure trace has an accounting mismatch that must be fixed before a new continuation. No evidence supports LR/scheduler, unintended optimizer resume, truncation, mask, or trainable-scope bugs.
NEXT_ACTION=DO_NOT_CONTINUE_BLINDLY; if continuing, change the sampling objective to guarantee block/token coverage and run a separately audited experiment.
