# EXACT10K final preflight

CURRENT_GATE: `M2_EXACT10K_REAL_COLLATOR_BLOCKED`

The frozen manifest and 100-case hard cohort resolve correctly, but the official Dataset/Collator path is not wired to EXACT10K. Therefore real collator, model forward/backward, memory dry-run, and launch instantiate checks were not claimed as PASS. No training, optimizer step, decode, or test evaluation ran.
