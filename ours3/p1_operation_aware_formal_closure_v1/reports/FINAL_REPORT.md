# P1 Operation-Aware Formal Closure

## Frozen Scope

- VAL1000 only.
- Existing A1, A3, and P1 predictions reused.
- No training, no new decode, no evaluator/parser/executor/GT changes.
- TEST remains blind.

## Main Result

P1 vs A3 Op-F1 mean delta: `0.072947`; bootstrap 95% CI `[0.054187, 0.091668]`.

P1 vs A1 Op-F1 mean delta: `0.054075`; bootstrap 95% CI `[0.035571, 0.072169]`.

P1 is the current main model because it improves operation recovery, parse validity, STEP export/reload, and generation completeness over A3 while retaining broadly preserved geometry. The Chamfer mean remains outlier-sensitive.

## Interpretation

The evidence supports an operation-aware supervision effect consistent with fewer missing/wrong CAD operations and better generation completeness. It does not prove a causal mechanism beyond the frozen loss ablation.

P2 is deferred until the parameter and geometry-outlier audit is reviewed. The remaining risk is local parameter, placement, direction, or scale error rather than unresolved operation structure alone.
