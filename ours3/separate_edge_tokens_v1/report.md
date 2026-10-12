# Separate Edge Point Tokens V1 — Report

**CURRENT_GATE = `SEPARATE_EDGE_POINT_TOKENS_V1_FAIL`**

NEXT_PRIMARY_BLOCKER = `real_edge_measurably_differs_task_level_heldout`


## Gate checks

| check | result |
| --- | --- |
| baseline_not_broken | PASS |
| edge_score_not_broken | PASS |
| separate_edge_forward_ok | PASS |
| edge_projector_grad_nonzero | PASS |
| checkpoint_reload_ok | PASS |
| ten_sample_overfits | PASS |
| real_edge_measurably_differs_task_level_heldout | FAIL |

## 0. Non-regression of existing work

| key | value |
| --- | --- |
| BASELINE_CODE_MODIFIED | False |
| EDGE_SCORE_CODE_MODIFIED | False |
| OLD_CHECKPOINTS_MODIFIED | False |
| OLD_BASELINE_REGRESSION | PASS |
| EDGE_SCORE_REGRESSION | PASS |

## 1. Representation level

| key | value |
| --- | --- |
| SURFACE_CHANNELS | 6 |
| EDGE_CHANNELS | 6 |
| SURFACE_RAW_POINTS | 8192 |
| EDGE_RAW_POINTS | 1024 |
| SURFACE_VOXEL_COUNT | 7672 |
| EDGE_VOXEL_COUNT | 1006 |
| SURFACE_TOKEN_COUNT | 231 |
| EDGE_TOKEN_COUNT | 94 |
| SURFACE_TOKEN_SHAPE | [231, 2048] |
| EDGE_TOKEN_SHAPE | [94, 2048] |
| FINAL_LLM_INPUT_SHAPE | [1, 547, 2048] |
| SHARED_SONATA | True |
| SONATA_FROZEN | True |
| EDGE_PROJECTOR_SEPARATE | True |
| EDGE_PROJECTOR_INIT | copy_of_surface_projector |
| EDGE_PROJECTOR_TRAINABLE | 1313280 |
| TOTAL_PARAMETERS | 1347197056 |
| TRAINABLE_PARAMETERS | 1238440960 |
| SPECIAL_EDGE_TOKEN_TRAINABLE | True |
| SURFACE_PROJECTOR_GRAD_NORM | 45.310493 |
| EDGE_PROJECTOR_GRAD_NORM | 7.450421 |
| LLM_GRAD_NORM | 407.098696 |
| SONATA_GRAD_NORM | 0.000000 |
| REAL_VS_ZERO_EMBED_DELTA | 0.388840 |
| REAL_VS_WRONG_EMBED_DELTA | 0.726851 |
| REAL_VS_CORRUPTED_EMBED_DELTA | 0.298569 |

## 2. Task level

| key | value |
| --- | --- |
| OVERFIT1_INITIAL_LOSS | 11.297273 |
| OVERFIT1_FINAL_LOSS | 2.592834 |
| OVERFIT1_RELOAD_OK | True |
| OVERFIT10_INITIAL_LOSS | 10.495417 |
| OVERFIT10_FINAL_LOSS | 0.016004 |
| OVERFIT10_TOKEN_ACCURACY | 0.991501 |
| OVERFIT10_SURFACE_ONLY_LOSS | 0.061113 |
| OVERFIT10_EDGE_SCORE_LOSS | 0.017251 |
| OVERFIT10_SEPARATE_EDGE_LOSS | 0.016004 |
| OVERFIT100_SURFACE_ONLY_LOSS | 0.019707 |
| OVERFIT100_EDGE_SCORE_LOSS | 0.015956 |
| OVERFIT100_SEPARATE_EDGE_LOSS | 0.013468 |
| OVERFIT100_SURFACE_ONLY_VAL_LOSS | 2.797122 |
| OVERFIT100_EDGE_SCORE_VAL_LOSS | 2.699393 |
| OVERFIT100_SEPARATE_EDGE_VAL_LOSS | 2.756028 |

## 3. Structure level (same E2 checkpoint, four edge conditions)

The verdict uses the **held-out** split. The train split is reported separately because a model can read the edge stream as a per-sample fingerprint, which inflates the seen-part gap without any transferable geometric understanding.

| key | value |
| --- | --- |
| ABLATION_SPLIT_USED_FOR_VERDICT | held-out val (19 parts) |
| REAL_EDGE_EVAL_LOSS | 2.753214 |
| ZERO_EDGE_EVAL_LOSS | 2.752835 |
| WRONG_EDGE_EVAL_LOSS | 2.714381 |
| CORRUPTED_EDGE_EVAL_LOSS | 2.760241 |
| REAL_BEATS_ZERO | False |
| REAL_BEATS_WRONG | False |
| REAL_BEATS_CORRUPTED | True |
| EDGE_STRUCTURE_LEARNED | False |
| EDGE_PRESENCE_ONLY | False |
| EDGE_USED_AS_MEMORIZATION_KEY | True |

### Train-split ablation (memorization diagnostic)

| key | value |
| --- | --- |
| TRAINSET_REAL_EDGE_EVAL_LOSS | 0.013457 |
| TRAINSET_ZERO_EDGE_EVAL_LOSS | 0.017460 |
| TRAINSET_WRONG_EDGE_EVAL_LOSS | 0.207952 |
| TRAINSET_CORRUPTED_EDGE_EVAL_LOSS | 0.014549 |
| TRAINSET_EDGE_STRUCTURE_LEARNED | True |

### Per-condition detail

| condition | eval_loss | token_acc | cad_validity |
| --- | --- | --- | --- |
| real | 2.753214 | 0.683904 | 0.421053 |
| zero | 2.752835 | 0.684689 | 0.473684 |
| wrong | 2.714381 | 0.684352 | 0.368421 |
| corrupted | 2.760241 | 0.683118 | 0.473684 |

| paired comparison | real better on | mean loss gap |
| --- | --- | --- |
| real vs zero | 0.368421 | -0.000379 |
| real vs wrong | 0.368421 | -0.038833 |
| real vs corrupted | 0.578947 | 0.007026 |

## 4. Interpretation

The edge stream is **read** by the model but not **understood**.

On the 80 training parts, swapping in another part's edge cloud costs 0.207952 versus 0.013457 for the real edges, and the real edges win on every single part. So the edge tokens genuinely reach the decoder and carry per-sample information.

On the 19 held-out parts that advantage vanishes: real, zero, wrong and corrupted edges all land within noise of each other, and the real edges win on a minority of parts. The gap the model exploits is therefore a **per-sample fingerprint used for memorization**, not transferable geometric structure.

`EDGE_STRUCTURE_LEARNED=False` is the honest verdict for V1.
