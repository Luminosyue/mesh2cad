# NEXT_STAGE_PARALLEL_V1 Report

The parallel stage is complete. Track A passed, Track B is externally blocked, and Track C passed independently.

## Track A — P3 part sanity

- Status: `PASS`; D case `REAL_03` was selected from the frozen Gate1 CSV.
- Reused 26 existing P3 outputs; triangle mapping valid: `True`; P3 rerun: `false`.
- Segment status counts: good 2, oversegmentation 4, undersegmentation 1, tiny 0, freeform 1, uncertain 18.
- Merge hypotheses: strong 2, weak 19; no merge was executed.
- MAC pilot candidates selected only: `2`; no part was sent to MAC.

## Track B — PhysX recovery

- Status: `BLOCKED`; checkpoint ready/load/smoke: `False/False/False`.
- Official local documentation requires the PhysX-Omni model snapshot, TRELLIS decoder snapshot, and Qwen processor assets.
- No valid local PhysX checkpoint was found. The official Hugging Face host was unreachable and no user-configured mirror existed.
- The smoke gate remained closed, so the 10-case batch was not attempted and no output was fabricated.

## Track C — geometry-only MAC baseline

- Status: `PASS`; provider ready: `True`.
- Original Gate1 A/B whole objects only: 4 attempted, 4 STEP, 4 independently valid BREP, 4 metric sets.
- Fixed quality classes: Q1=0, Q2=0, Q3=4; pseudo-pair feasible: `False`.
- LLM use: 16 calls, 229670 total tokens.

| Case | Gate1 | STEP | BREP valid | Chamfer normalized | P95 | Coverage .02 | Quality |
|---|---:|---:|---:|---:|---:|---:|---|
| REAL_05 | A | True | True | 0.069316 | 0.159553 | 0.348760 | Q3_REJECT |
| REAL_02 | B | True | True | 0.065845 | 0.153885 | 0.284320 | Q3_REJECT |
| REAL_06 | B | True | True | 0.206659 | 0.440318 | 0.085300 | Q3_REJECT |
| REAL_08 | B | True | True | 0.194256 | 0.485243 | 0.063120 | Q3_REJECT |

## Global invariants

- PhysX was not used in the MAC baseline.
- P3 inference was not rerun; no second P3 level was created.
- Assembly was not started.
- STEP GT and ABC GT were not used.
- Tests passed/failed: `111/0`.

## Blockers by track

- Track A: `[]`
- Track B: `['PHYSX_INFERENCE_CHECKPOINT_UNAVAILABLE']`
- Track C: `[]`
