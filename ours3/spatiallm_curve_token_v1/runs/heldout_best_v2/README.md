# heldout_best_v2 — formal paper Gate

This directory is the **only** held-out comparison that may enter the paper
main table.

## Protocol

- All four arms initialize from `SpatialLM/models/SpatialLM1.1-Llama-1B`.
- Not initialized from Curve100 probe checkpoints.
- Not resumed from the old 20-epoch last checkpoints under `runs/heldout/`.
- Checkpoint = **minimum validation `eval_loss`**. Test is never used to pick a checkpoint.
- `num_train_epochs: 20` is an upper bound. EarlyStopping patience=4, threshold=0.0.
- `eval_steps = save_steps = 250`, `load_best_model_at_end: true`.
- The reloaded best weights are copied to `<arm>/best_model/` and must not be deleted.
- Shared surface index cache: `surface_idx4096.npz`. B0/B1/M2 see the same 4096 surface points per CAD. GridSample is `test` mode (deterministic). Train does not re-draw surface points.
- B1-budget-match caps **voxelized second-stream LLM tokens** at K = curve-token count, not raw edge-point count.
- Curve Encoder is frozen and is not modified in this round.
- Decode: `do_sample=false`, `num_beams=1`, `max_new_tokens=4096`, fixed 280 test CADs, **one checkpoint per arm** (`best_model/`).

## Layout

```
logs/{B0,B1n,B1b,M2}.log   # training logs (not inside HF save_dir)
b0/  b1_native/  b1_budget_match/  m2/
  dataset_dict.json
  selection.json
  best_model/          # keep forever
  checkpoint-*         # rotatable (save_total_limit=4; best is also copied)
decode/                # best-val test decode only
TABLE.md
surface_idx4096.npz    # shared 4096 surface indices, all arms
```

## Old `runs/heldout/`

Last-checkpoint diagnostic. Keep it. Do not overwrite. Do not put it in the paper main table.
