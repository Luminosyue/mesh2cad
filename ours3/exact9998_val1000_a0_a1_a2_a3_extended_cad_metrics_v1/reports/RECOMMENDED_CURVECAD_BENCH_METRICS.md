# Recommended CurveCAD-Bench Metrics

## HEADLINE
- Program structure: Exact, Op-F1, Op Recall.
- Executability: Parse, STEP Export, STEP Reload with denominator N=1000.
- Geometry: Chamfer and H95 reported with geometry-valid coverage and common-valid paired subsets.
- Topology: face/edge/solid count error and valid-BRep rate.

## SECONDARY
- Surface area relative error.
- Dependency edge precision/recall/F1.
- Curve count and curve geometry assignment error.
- Placement/scale errors.

## DIAGNOSTIC
- Curve type macro-F1 under geometric assignment.
- Euler characteristic error.
- AST-aligned parameter error.
- Wire/profile closure interpretation.

## DEFERRED
- Normal consistency until a shared reliable normal tessellation is frozen.
- Manifold rate until a true manifold checker is available.
- Graph edit distance until node-cost semantics are frozen.
