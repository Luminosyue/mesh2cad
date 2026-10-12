# Baseline Comparison Summary

Frozen EXACT9998 VAL1000 manifest only. P1 and CAD-Recode are summarized from frozen V2 per-case artifacts. DeepCAD, CADFit, and Cadrille are not assigned fabricated values.

`IR` is explicitly defined in this closeout as usable frozen prediction artifact rate, separate from STEP Reload. IoU is computed by the same closeout evaluator as exact OCC solid intersection volume divided by fused union volume, after the frozen V2 coordinate adapter.

Denominators:

- P1: full 1000; STEP Reload 958; geometry-valid 239.
- CAD-Recode: full 1000; STEP Reload 840; geometry-valid 201.
- Strict P1/CAD-Recode common-valid: 190 exact IDs.
- IoU-valid after range validation: P1 238, CAD-Recode 198, strict common geometry-valid with IoU on both 187; out-of-range OCC boolean cases remain blank with case-level reasons.
- DeepCAD: no aligned prediction/STEP denominator.
- CADFit: 1000 normalized input cache files materialized, but no prediction/STEP outputs.
- Cadrille: no identified artifact.

Per-method-valid and strict common-valid metrics are kept separate. Means across different case sets are not used as strict cross-method winners. Exact IDs, paths, denominators, and failure reasons are in `tables/baseline_full_val1000.csv`.
