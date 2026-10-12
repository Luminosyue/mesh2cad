# P1 Final-Test Guard and P2 Size-Supervision Preparation V1

CURRENT_GATE = P2_SIZE_SUPERVISION_PREPARATION_COMPLETE

P2_TRAIN_READY = YES

P2_FINAL_EVAL_READY = NO

## P1 Final TEST

- Scheduler alive: True
- A0/A1/A2/A3/P1 progress: 449/410/390/0/0 case directories
- TEST_PARTIAL_METRICS_READ = NO
- FINAL_TEST_INTERFERENCE = NO

## P2 preparation

- Target: SIZE only
- Fields: Box width/height/depth; Extrude height; ExtrudePolygon height. Cylinder radius/height is coverage-gated.
- Mask FP/MISS: 0/0
- Lambda-0 loss-path parity: PASS
- TRAIN/VAL coverage: SUFFICIENT/SUFFICIENT
- No model training or decoding was started.

## Holdout

- 1000 model-blind candidates identified; ID and STEP-fingerprint overlap are zero.
- Final freeze is blocked until canonical DSL conversion/hash dedup and complexity stratification are completed.
