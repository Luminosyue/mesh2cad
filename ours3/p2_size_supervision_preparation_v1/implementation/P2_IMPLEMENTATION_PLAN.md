# P2 Implementation Plan

1. Start from the same pristine base, seed, data, curve cache, optimizer, and schedule as P1.
2. Install the isolated P2 runtime; do not modify P1 source.
3. Map only AST-declared operation-specific size fields to response token spans, then relocate exact subsequences after geometry insertion.
4. Apply the same causal shift to labels and size mask.
5. Train fresh with `L_base + 1.0 L_op + lambda_size L_size`; candidate lambdas are 0.25, 0.5, 1.0 after a small TRAIN/VAL canary.
6. Select checkpoints using frozen VAL base CE; report VAL size CE separately.
7. No training is authorized by this preparation.
