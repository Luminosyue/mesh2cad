# M2 Fusion360 Split-Source Contract Validation V1

CURRENT_GATE: M2_FUSION360_SPLIT_SOURCE_M2_CONTRACT_FAIL
SPLIT_SOURCE_CONTRACT_APPROVED: NO
FULL8625_ALLOWED: NO

The candidate historical contract is:
- OBJ-derived sampled XYZ supplies the transform branch.
- STEP/B-Rep supplies Original M2 surface, GT curves, and C2.

Reused frozen results: execution non-regression 592/592, canonical geometry 590/592, surface interface 592/592, GT curve extraction 592/592, curve compatibility 591/592, and P1 transform equivalence pass.

The contract cannot pass because common592 C2 input/forward, K=8, tokenizer/EOS/loss-mask, real M2 loader, B0 loader, and end-to-end determinism remain NOT_AUDITED in the existing artifacts. No new execution, Dora run, training, decode, or implementation change was performed.
