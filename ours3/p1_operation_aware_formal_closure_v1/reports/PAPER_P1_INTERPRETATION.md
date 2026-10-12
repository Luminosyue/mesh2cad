# Paper Interpretation

## Main Finding

Explicit curve geometry provides useful CAD structural cues, but naive all-curve conditioning can create operation-level interference. Operation-aware structural supervision improves the mapping from geometry to CAD operations.

## Mechanistic Evidence

P1 improves operation-level recovery, parse/STEP validity, and generation completeness relative to A3. Operation-level rescue and transition tables are provided in `operation_breakdown/`.

## Geometry Trade-off

Geometry is broadly preserved, with improved medians/H95/volume behavior and a remaining Chamfer-mean outlier tail. This should be reported as a trade-off, not as uniform geometric improvement.

## Limitation

The evidence is consistent with the loss mechanism but is not a causal proof beyond this loss ablation. Numeric placement and scale remain separately audited residuals.

## Next Step

Freeze P1 as the main model and keep TEST blind. Defer P2 until parameter/outlier evidence justifies a clean parameter-focused intervention.
