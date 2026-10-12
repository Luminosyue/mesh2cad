# Original M2 Provenance Closure V1

**Gate:** `M2_FUSION360_ORIGINAL_M2_PROVENANCE_BLOCKED`

The formal historical run was identified as `/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2` and its best checkpoint as
`/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2/best_model` (best validation step 1500). The checkpoint directly contains all four
`edge_proj.net.*` CurveProjector tensors and no learned-query/cross-attention
summary tensors. Original M2 therefore used variable `K` curve tokens after the
historical cap of 128; Geometry Prefix V3's fixed K=8 is not part of this evidence.

Closure remains blocked because the current launcher, entrypoint, config, injector,
SpatialLM model, collator and loader files all postdate the historical run, the
project root has no Git history, and no historical tokenized `input_ids`/`labels`
or source snapshot was preserved. Checkpoint identity, tokenizer, manifest,
curve cardinality and CurveProjector checkpoint matching are confirmed; historical
splice, target-builder, label-mask, Dataset/Collator and exact DataLoader behavior
remain `INFERRED_NOT_PROVEN`.

No training, decode, Dora run, model change, tokenizer change or loader change was performed.
