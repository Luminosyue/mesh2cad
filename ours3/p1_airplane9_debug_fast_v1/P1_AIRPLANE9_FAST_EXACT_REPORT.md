# P1 AIRPLANE9 FAST EXACT REPORT

P1_A3_GATE=PASS
EXACT_MEMORIZATION_STABLE=YES

This is a training-set memorization gate, not evidence of held-out generalization.

## Provenance and frozen protocol

BASE_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_quick_overfit_airplane9_v1/runs/quick/checkpoint-2000
Original9 weights loaded; fresh AdamW because optimizer.pt was absent. No weights were initialized from FAST3. Prior FAST3 actually began from initial airplane3 checkpoint-2000; the request’s original9 attribution for that earlier run was corrected.
Frozen GT, tokenizer, grammar, serializer, geometry assets, model implementation and CAD executor hashes verified unchanged.

## Data and training

TRAIN_PART_N=9; TOTAL_BLOCK_N=134; TOTAL_TOKEN_N=133347 (includes every per-block EOS)
MIN_TOKEN_N=5615; MAX_TOKEN_N=25133; MEDIAN_TOKEN_N=12932
All9 GT parse/execute/STEP roundtrips passed. Every134 target sequence was checked against active labels, including EOS; no truncation.
LR=1e-5; SCHEDULER=constant; WARMUP=0; WEIGHT_DECAY=0; SEED=42
MICRO_BATCH_SIZE=1; GRAD_ACCUM_STEPS=9; PARTS_PER_EFFECTIVE_UPDATE=9
SAMPLER=deterministic part round-robin, shuffled cyclic block queues within each part; no augmentation
BALANCED_EXPOSURE=YES; max-min<=1 at every microstep, exactly equal after each update
ACTUAL_UPDATES=148; MAX_EXTRA_UPDATES=500; WALL_BUDGET=4h
FINAL_EXPOSURES={'PART_000': 149, 'PART_001': 149, 'PART_002': 149, 'PART_003': 149, 'PART_004': 149, 'PART_005': 149, 'PART_006': 149, 'PART_007': 149, 'PART_008': 148}

## Numerical path

GEOMETRY_DTYPE_ALIGNED=YES; surface and curve inputs quantized to BF16 in both training and gate. Training uses FP32 stored parameters with BF16 autocast and TF32 enabled, matching FAST. Projector prehook input/weight dtype is FP32; autocast enabled. Gate loads checkpoint with the established BF16 loader then model.float(), FP32 projectors/decoder, autocast disabled, TF32 disabled. This includes the same BF16 weight quantization as successful FAST; it is not an unquantized FP32 checkpoint loader.
GATE_EVAL_FP32=YES; do_sample=False; num_beams=1. Fresh seeded model per part for TF scans.
Free decode begins with empty program, uses only own generated prefix (protocol recent384 suffix), fixed1280 token/block and64 block caps. Natural CAD_COMPLETE plus final block EOS required. EOS/PAD128009 unchanged; generation EOS list unchanged. No GT stopping, repair, clipping, or GT prefix.

## Trajectory

| Extra optimizer updates | Total TF errors | TF zero parts | Free exact |
|---:|---:|---:|---:|
| +10 | 65 | 1/9 | Not run |
| +20 | 13 | 4/9 | Not run |
| +30 | 2 | 7/9 | Not run |
| +40 | 1 | 8/9 | Not run |
| +60 | 0 | 9/9 | 9/9 |
| +80 | 0 | 9/9 | 9/9 |
| +100 | 0 | 9/9 | Not run |

FIRST_9_OF_9_TF_ZERO_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1/runs/quick/checkpoint-/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1/runs/quick/checkpoint-60
FIRST_9_OF_9_EXACT_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1/runs/quick/checkpoint-/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1/runs/quick/checkpoint-60
BEST_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1/runs/quick/checkpoint-60
Best exact checkpoint ranked by raw exact count, CAD/STEP success, fewer TF errors, then earliest update. TF-only fallback is explicitly not a free-decoding success.

## Best checkpoint per-part evidence

| Part | GT / pred blocks | GT / pred tokens | TF errors | Raw exact | Natural end | CAD execute | STEP readback |
|---|---:|---:|---:|---|---|---|---|
| PART_000 | 6 / 6 | 5615 / 5615 | 0 | True | True | True | True |
| PART_001 | 13 / 13 | 12932 / 12932 | 0 | True | True | True | True |
| PART_002 | 13 / 13 | 12933 / 12933 | 0 | True | True | True | True |
| PART_003 | 13 / 13 | 12941 / 12941 | 0 | True | True | True | True |
| PART_004 | 13 / 13 | 12932 / 12932 | 0 | True | True | True | True |
| PART_005 | 25 / 25 | 25133 / 25133 | 0 | True | True | True | True |
| PART_006 | 13 / 13 | 12888 / 12888 | 0 | True | True | True | True |
| PART_007 | 13 / 13 | 12929 / 12929 | 0 | True | True | True | True |
| PART_008 | 25 / 25 | 25044 / 25044 | 0 | True | True | True | True |

FREE_CASES_EVALUATED_AT_BEST=9/9
RAW_TOKEN_EXACT_N=9/9
BLOCK_EXACT_N=9/9
BLOCK_COUNT_EXACT_N=9/9
EOS_N=9/9
PARSE_PASS_N=9/9
EXEC_PASS_N=9/9
STEP_EXPORT_PASS_N=9/9
STEP_ROUNDTRIP_PASS_N=9/9
SAFETY_CAP_HIT_N=0
TF_ZERO_ERROR_N=9/9

NEXT_GATE=P1-A4 GENERALIZATION / HELD-OUT
Memorization training stopped; no held-out experiment launched.

## Evidence

Dataset audit, full checkpoint trajectory, all raw prediction and GT tokens, per-token TF logits/margins, execution logs, exported STEP, config, scripts, sampler indices/exposures, checkpoint weight loading evidence, and immutable source hashes are preserved under this experiment. Independent validation rechecked raw sequence equality, token counts, EOS/caps, STEP readback and all frozen hashes.
Conditioning matrices use mean projected tokens from the last scanned checkpoint; fused means an equal-weight mean of branch summaries, not a modified architecture.
