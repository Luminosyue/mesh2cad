# Demo5 full pipeline final report

The step-160 model was reconstructed from checkpoint-40 with the unchanged Demo5 protocol: full-parameter AdamW, context 16,384, dynamic lengths, SDPA, `use_cache=false`, gradient checkpointing, micro-batch 1, and round-robin balanced sampling. It reached `TF_ERROR_N=0` for all five cases at step 160.

The resulting minimal frozen checkpoint was saved under `frozen_tf5_success_v1/` with model safetensors, config, tokenizer reference, training config, module audit, and TF audit. Reloading that frozen checkpoint reproduced `5/5` TF zero exactly.

The five Demo5 objects are:

- `case_018`: `b015ipnvfw`, 142 generated model tokens, 39 q values
- `case_009`: `construction_60`, 395 generated model tokens, 125 q values
- `case_014`: Tank `PART_029`, 4,486 generated model tokens, 1,529 q values
- `case_010`: `vase`, 3,745 generated model tokens, 1,299 q values
- `case_005`: `azure_snake_tieks_leather_snake_print_ballet_flats`, 6,197 generated model tokens, 2,050 q values

All five free rollouts used empty targets, greedy decoding, no ground-truth prefix, no continuation, and no chunking. All five reached exact generated token sequences, natural EOS, exact q streams, valid parser/compiler/CAD/BRep, STEP export/readback, and exact geometry metrics. The final counts are:

- TF exact: `5/5`
- free token exact: `5/5`
- natural EOS: `5/5`
- parser/compiler: `5/5`
- CAD/BRep: `5/5`
- STEP readback: `5/5`
- geometry exact: `5/5`

Tank `PART_029` was reused from its validated gate rather than rerun. Its q stream is `1,529/1,529`, natural EOS passes, STEP readback passes, and volume error is `0.0`.

Smooth-shaded teaser renders were produced for input mesh, generated BRep, canonical BRep, and overlay for all five cases. Generated and canonical views hide tessellation triangle edges; the renderer uses tessellated display only for image rasterization and does not replace the CAD BRep artifacts.

`NEW5_MODEL_EXACT_PASS=TRUE`

`NEW5_FULL_PIPELINE_PASS=TRUE`

`NEW_CASE_TEASER_READY=YES`

The 20-case joint experiment was not started in this turn, as required by the finalization protocol.
