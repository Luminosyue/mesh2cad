# M2 EXACT10K Rebaseline Protocol

CURRENT_GATE: `M2_EXACT10K_TRAINING_PROTOCOL_BLOCKED`

TRAINING_APPROVED: `NO`

The EXACT10K dataset is frozen at 10,000 IDs with 8,000/1,000/1,000 splits and zero leakage. This round performed protocol auditing only. No training, optimizer step, decode, or test evaluation was run.

Blockers: exact10k loader adapter audit, B0/M2 train-mode memory dry-runs, final smoke tests, launch preflight, and reconciliation of the actual `256 -> 512 -> 2048` edge adapter with the requested `256 -> 256 -> 2048` specification.
