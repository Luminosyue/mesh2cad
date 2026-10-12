# P3 X-Part 20-case full-sequence overfit

## Configuration

- Requested and frozen cases: **20** (20 different objects; `case_014` is Tank `PART_029`).
- Initialization: Airplane3 full-sequence warm start, model weights loaded from `/data/home/cuiyuehan/project/mesh2cad/ours3/airplane3_fullseq_14bit_ir_v1/runs/fast_refinement_v2_step80/checkpoint-40`; optimizer, scheduler and global step were new.
- Target: NEW20 only.
- Context: max audited full sequence `30992.0`; 5% margin selects **32768** from the required candidates.
- Learning rate: `5e-6`; micro batch `1`; gradient accumulation `1`; checkpoints requested at `20,40,80,160,320` updates.

## Data gates

Raw CAD, 14-bit dequantized CAD, Compact IR round-trip, Compact IR compiler, and STEP readback each passed **20/20**.

## Token audit

Mean raw-to-compact reduction is **31.77%**, median **26.40%**. The five longest compact targets are `case_013, case_002, case_015, case_007, case_001`; the longest full sequence is `30992.0` tokens.

## Training result

The requested full-parameter run reached update 3 and stopped with CUDA out-of-memory during the backward pass on a roughly 30k-token sample. A second run freezing the language tower still stopped at update 0 because the full-sequence attention allocation exceeded the 46 GB GPU. No valid training checkpoint was produced. These failures are retained in `logs/train.log` and `logs/train_fallback.log`; no case or long sequence was truncated.

The teacher-forced scan at the warm-start model (step 0) completed for all 20 cases: **0/20** exact, **96681** total token errors. Because the 20/20 TF gate was not reached, free generation and generated-CAD gates were not run.

Ground-truth Compact IR compilation and STEP readback remain **20/20**. The Tank source OBJ is retained as provided and is marked non-watertight by the mesh audit; its CadQuery target is a valid single solid.
