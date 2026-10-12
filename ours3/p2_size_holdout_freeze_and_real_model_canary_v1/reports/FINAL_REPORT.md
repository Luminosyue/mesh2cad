# P2 Size Holdout Freeze and Real-Model Canary V1

CURRENT_GATE = HOLDOUT_FREEZE_PASS_CANARY_WAITING_FOR_FREE_GPU

## Holdout
- Initial/canonicalized/producer-valid/final: 1000/959/958/958
- Exact ID/program/geometry overlaps: 0/0/0
- P2_FINAL_EVAL_READY = YES
- Source = FUSION360_ONLY; near-duplicate threshold remains explicitly deferred.

## Real-model canary
- Status = WAITING_FOR_FREE_GPU
- No GPU had at least 24 GiB genuinely free without Final TEST responsibility.
- No real-model metric, parity value, gradient, optimizer step, or checkpoint is fabricated.
- P2_FULL_TRAIN_READY = NO

## Final TEST isolation
- Progress A0/A1/A2/A3/P1 = 549/513/474/0/0
- TEST_PARTIAL_METRICS_READ = NO
- FINAL_TEST_INTERFERENCE = NO
