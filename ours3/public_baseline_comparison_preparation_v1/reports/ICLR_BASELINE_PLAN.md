# ICLR Baseline Plan

1. Point2CAD: pin repo commit/checkpoint, build a point-cloud adapter from existing VAL geometry only, run one smoke case, then VAL1000 if the contract is exact.
2. DeepCAD: verify official checkpoint and source-case preprocessing; run inference-only if possible, otherwise mark retrain required.
3. CAD-Recode: audit checkpoint, runtime, output vocabulary, and STEP execution before any quantitative comparison.

Public table inclusion gate: same input group, same EXACT9998 VAL split, deterministic canonical mapping, and shared evaluator. Until all gates pass, report feasibility and N/A rather than paper numbers as directly comparable.
