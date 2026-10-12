# M2 EXACT9998 Curve Token Cache Completion V1

CURRENT_GATE = M2_EXACT9998_CURVE_BRANCH_INTEGRATION_FIXED
M2_INTEGRATION_FIXED = YES
NEXT_STEP = M2_EXACT9998_CORRECTED_M2_FRESH_TRAIN_V1

Curve source: train 7998/7998, val 1000/1000, test 1000/1000
Curve tokens: train 7998/7998, val 1000/1000, missing 0, schema fail 0
Reuse: old verified 2514, rebuilt verified 7484; new export this round 0
C2 SHA256: 553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9
K: min 1, median 24.0, max 128; K=128 present

Canary and integration gates:
- C2 token canary: 100/100 exact
- Determinism: 10/10 exact
- Projector: registered, 592128 params, 4 state keys, in optimizer
- Forward/splice: 4 calls, K=128 pass, real splice pass
- Gradient: FINITE_NONZERO; C2 gradient NONE
- Checkpoint strict reload: PASS; optimizer serialization: PASS

Safety: no M2 training, no optimizer.step, no test forward/decode/metric, no geometry evaluation. EXACT9998 hashes unchanged.
