# Old held-out run (seed=0, 20 epochs) — DIAGNOSTIC ONLY

This directory and `SpatialLM/saves/heldout_curve_*_s0` are **not** the paper
main table.

- Let B1-native / B1-budget-match finish to last checkpoint.
- Keep all logs, last checkpoints, and `heldout_decode/`.
- Use for overfitting analysis (val CE vs train CE, last vs implicit early best)
  and for debugging the STEP/Chamfer inference pipeline.
- Do **not** overwrite these files with `heldout_best_v2`.
- Do **not** select a checkpoint by test metrics and report it as the Gate.

Formal Gate: `../heldout_best_v2/` (best-val + early stopping, seed=42).
