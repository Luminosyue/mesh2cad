# M2_EXACT9998_B0_M2_FINAL_TEST_EVAL_V1

## Gate

- CURRENT_GATE: `M2_EXACT9998_B0_M2_FINAL_TEST_EVAL_FAIL_M2_FREEZE`
- FINAL_TEST_EVAL: `FAIL`
- EXACT9998 test was not opened.
- TEST_N is frozen at `1000`; test manifest and ID-set hashes are recorded in `FINAL_REPORT.json`.

## Checkpoint freeze

B0 selected validation checkpoint: `checkpoint-6000`, global step `6000`, best validation loss `0.5020751357078552`.

M2 selected validation checkpoint: `checkpoint-6000`, global step `6000`, best validation loss `0.500813364982605`. The selection metadata itself is validation-only, but the structural M2 gate fails.

## Blocking finding

The saved M2 model has no `edge_proj` or CurveProjector weights. Its saved config has no curve-stream metadata, the training log has no CurveProjector attachment message, and the logged trainable/all parameter counts match B0. Therefore this run is not a valid `M2_GT_BREP_CURVE_ORACLE` checkpoint. Running B0/M2 test decode now would produce an invalid comparison and is intentionally blocked.

## Safety

No training, optimizer step, checkpoint modification, test-based selection, test decode tuning, manual prediction repair, or failed-case dropping was performed in this gate.

## Next step

Repair or retrain the M2 arm with an explicitly attached CurveProjector and saved `edge_proj.*` weights, then repeat the freeze gate before opening EXACT9998 test.
