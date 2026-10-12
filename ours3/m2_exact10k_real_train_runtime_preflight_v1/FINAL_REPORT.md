# EXACT10K Real Train Runtime Preflight

CURRENT_GATE = M2_EXACT10K_REBASELINE_TRAINING_PROTOCOL_FROZEN

TRAINING_APPROVED = YES

NEXT_STEP = M2_EXACT10K_B0_M2_TRAIN_V1

B0 and Original M2 used the same pristine base, official Dataset/Collator semantics, context 8192, bf16, microbatch 1, gradient accumulation 4, and no optimizer step. Real K=128 and full TRAIN=8000 collator length audits passed.
