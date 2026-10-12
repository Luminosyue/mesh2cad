# P1-A2 airplane 3-part exact memorization

**P1_A2_GATE=FAIL**。独立实验，固定分母 3 个训练零件。所有结果来自对应 checkpoint 的实际 greedy 自由生成。
实验目录：`/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1`。模型位于 `runs/quick/checkpoint-*`。

## 最终 Gate

```text
TRAIN_CASE_N=3
MAX_TRAIN_STEPS=3000
TOTAL_OPTIMIZER_STEPS=3000
FIRST_3_OF_3_EXACT_CHECKPOINT=None
FIRST_3_OF_3_EXACT_STEP=None
TRAIN_LOSS_AT_FIRST_PASS=None
TRAIN_LOSS_LAST10_MEAN_AT_FIRST_PASS=None
BEST_CHECKPOINT=checkpoint-2000
EXACT_MEMORIZATION_STABLE=NO
P1_A2_GATE=FAIL
NEXT_GATE=DEBUG_MULTI_SAMPLE_MEMORIZATION
FROZEN_INPUTS_PASS=True
SEQUENCE_EXACT_N=1/3
BLOCK_COUNT_EXACT_N=1/3
EOS_TERMINATED_N=1/3
PARSE_PASS_N=1/3
EXEC_PASS_N=1/3
STEP_PASS_N=1/3
SAFETY_CAP_HIT_N=2
PART_A=PART_000
PART_A_BLOCKS=6
PART_A_TOKENS=5615
TOKEN_ACC_A=1.0
EOS_ACC_A=1.0
MIN_TOKEN_MARGIN_A=1.125
PART_A_EXPOSURES=408
PART_B=PART_001
PART_B_BLOCKS=13
PART_B_TOKENS=12932
TOKEN_ACC_B=0.9992267244045778
EOS_ACC_B=1.0
MIN_TOKEN_MARGIN_B=-23.78125
PART_B_EXPOSURES=887
PART_C=PART_005
PART_C_BLOCKS=25
PART_C_TOKENS=25133
TOKEN_ACC_C=0.9981299486730594
EOS_ACC_C=1.0
MIN_TOKEN_MARGIN_C=-13.15625
PART_C_EXPOSURES=1705
SAMPLING_BALANCE=Unchanged uniform shuffled block sampling; unequal part block exposures, approximately equal full-program equivalents
EFFECTIVE_EXPOSURE_PER_SAMPLE={'PART_000': 68.0, 'PART_001': 68.23076923076923, 'PART_005': 68.2}
FIRST_FULL_GATE_PASS_CHECKPOINT=None
DIAGNOSIS_AT_FINAL_CHECKPOINT=MULTI_SAMPLE_ROLLOUT_INSTABILITY
PART_SPECIFIC_EXACT_REGRESSION=YES
BORROWED_GPU_RESERVATIONS_RESTORED=True
```

主表的 N/3、token accuracy、margin 指标统一取 BEST_CHECKPOINT；曝光量字段取全部训练步骤。各 checkpoint 的完整指标逐行列在后面。

## 数据与冻结协议

A 为已通过单样本验证的 PART_000；B 为 block/token 中位数附近的 PART_001；C 为原九件中程序最长的 PART_005。三个 GT 均通过原 executor 执行和 STEP 导出。

TOKEN_COUNT 采用每个训练 block 的原始目标 token 加 EOS 的总和；selected_3parts.json 中另保留原 inventory whole-program 计数。二者分块边界定义不同。

GT、serializer、词表、EOS/PAD、block grammar、mesh preprocessing、executor 均冻结，原实验文件大小与修改时间、pipeline 与 GT SHA256 复核通过。

初始化仍为原 checkpoint-8000，未用单样本 checkpoint-500 热启动。batch=1，gradient accumulation=1，lr=5e-5 constant，seed=42；full fine-tuning，冻结 point tower。训练日志保存每步未舍入 loss。

## 每个 checkpoint 的自由生成与 teacher-forcing

| Checkpoint | Part | TF token acc | EOS acc | Pred/GT blocks | Raw token exact | END+EOS | Cap | Parse/Exec/STEP | First divergence block/token |
|---|---|---:|---:|---:|---|---|---|---|---|
| checkpoint-250 | PART_000 | 0.976313446 | 1.000000 | 64/6 | False | False | True | False/False/False | 1/31 |
| checkpoint-250 | PART_001 | 0.977265697 | 1.000000 | 64/13 | False | False | True | False/False/False | 1/22 |
| checkpoint-250 | PART_005 | 0.987983926 | 1.000000 | 64/25 | False | False | True | False/False/False | 1/31 |
| checkpoint-500 | PART_000 | 0.994122885 | 1.000000 | 61/6 | False | True | False | False/False/False | 1/308 |
| checkpoint-500 | PART_001 | 0.993736468 | 1.000000 | 64/13 | False | False | True | False/False/False | 1/487 |
| checkpoint-500 | PART_005 | 0.997652489 | 1.000000 | 8/25 | False | True | False | False/False/False | 1/761 |
| checkpoint-750 | PART_000 | 0.995903829 | 1.000000 | 64/6 | False | False | True | False/False/False | 1/328 |
| checkpoint-750 | PART_001 | 0.996288277 | 1.000000 | 49/13 | False | True | False | False/False/False | 1/115 |
| checkpoint-750 | PART_005 | 0.997652489 | 1.000000 | 64/25 | False | False | True | False/False/False | 1/512 |
| checkpoint-1000 | PART_000 | 0.998575245 | 1.000000 | 64/6 | False | False | True | False/False/False | 1/629 |
| checkpoint-1000 | PART_001 | 0.997757501 | 1.000000 | 19/13 | False | True | False | False/False/False | 1/118 |
| checkpoint-1000 | PART_005 | 0.998289102 | 1.000000 | 64/25 | False | False | True | False/False/False | 2/1844 |
| checkpoint-1500 | PART_000 | 0.995547640 | 1.000000 | 64/6 | False | False | True | False/False/False | 1/36 |
| checkpoint-1500 | PART_001 | 0.995824312 | 1.000000 | 29/13 | False | True | False | False/False/False | 1/22 |
| checkpoint-1500 | PART_005 | 0.998846139 | 1.000000 | 64/25 | False | False | True | False/False/False | 1/987 |
| checkpoint-2000 | PART_000 | 1.000000000 | 1.000000 | 6/6 | True | True | False | True/True/True | None/None |
| checkpoint-2000 | PART_001 | 0.999226724 | 1.000000 | 64/13 | False | False | True | False/False/False | 1/207 |
| checkpoint-2000 | PART_005 | 0.998129949 | 1.000000 | 64/25 | False | False | True | False/False/False | 1/981 |
| checkpoint-2500 | PART_000 | 0.997328584 | 1.000000 | 64/6 | False | False | True | False/False/False | 1/328 |
| checkpoint-2500 | PART_001 | 0.999768017 | 1.000000 | 64/13 | False | False | True | False/False/False | 4/3305 |
| checkpoint-2500 | PART_005 | 0.999403175 | 1.000000 | 64/25 | False | False | True | False/False/False | 5/4377 |
| checkpoint-3000 | PART_000 | 0.999821906 | 1.000000 | 6/6 | False | True | False | True/True/True | 4/3200 |
| checkpoint-3000 | PART_001 | 0.999690690 | 1.000000 | 25/13 | False | True | False | False/False/False | 4/3354 |
| checkpoint-3000 | PART_005 | 0.999721482 | 1.000000 | 30/25 | False | True | False | False/False/False | 1/689 |

| Checkpoint | Macro mean token acc | Min token acc | EOS acc all | Strict Gate count |
|---|---:|---:|---:|---:|
| 250 | 0.980521023 | 0.976313446 | 1.000000 | 0/3 |
| 500 | 0.995170614 | 0.993736468 | 1.000000 | 0/3 |
| 750 | 0.996614865 | 0.995903829 | 1.000000 | 0/3 |
| 1000 | 0.998207283 | 0.997757501 | 1.000000 | 0/3 |
| 1500 | 0.996739364 | 0.995547640 | 1.000000 | 0/3 |
| 2000 | 0.999118891 | 0.998129949 | 1.000000 | 1/3 |
| 2500 | 0.998833259 | 0.997328584 | 1.000000 | 0/3 |
| 3000 | 0.999744692 | 0.999690690 | 1.000000 | 0/3 |

每块通过 EOS 结束，完整程序必须由模型输出 `# CAD_COMPLETE`，最后仍要求自然 EOS。do_sample=False、num_beams=1、max_new_tokens=1280/块、64 blocks 安全上限；未按 GT 长度/块数截断，也没有删除多余 block。完整原始 token 数组（含每块 EOS）独立复核 exact。

## 首次 PASS 与稳定性

首次通过：None；紧接的保存 checkpoint：None；连续两次严格 Gate 通过：False。best 优先取首次严格通过，若没有通过则依次按通过数、exact 数、最低 TF accuracy、首次分叉位置选择。

## Token margin

TOKEN_MARGIN = GT logit − 最强非 GT 竞争 token logit。SECOND_BEST 指相对 GT 的最强替代项；当 GT 为 top-1 时它也是全局第二名。错误 token 的 margin 可以为负。

| Part at best checkpoint | Min | P1 | P5 | Median | Worst block/token | GT / competitor |
|---|---:|---:|---:|---:|---|---|
| PART_000 | 1.125 | 4.94625 | 6.75 | 13.9375 | 3/80 | '0' / '1' |
| PART_001 | -23.7812 | 4.75 | 6.6875 | 13.6875 | 5/218 | '238' / '065' |
| PART_005 | -13.1562 | 4.1875 | 6.625 | 14 | 6/738 | '293' / '928' |

所有 checkpoint 的统计见 token_margin_analysis.csv；每个监督 token 的 logit、概率、margin、NLL 见 teacher_tokens.jsonl.gz。正 margin 只证明本次确定性 teacher-forcing 的 top-1 领先，不等于对扰动稳健。

## 实际训练曝光

保持原 block 级 shuffled sampling，没有改成 part 均衡 sampler。一个训练 step 只监督一个 block。复杂零件 block 更多，因此 PART_EXPOSURES 不相等；完整程序等效次数用 block 曝光数除以该零件 block 数。单样本 500 steps 对 6 blocks，等效 83.333 次完整程序曝光，不能解释为每个 token 看过 500 次。

| Checkpoint | Part | Block exposures | Full-program equivalents | Relative to single-500 |
|---|---|---:|---:|---:|
| 250 | PART_000 | 35 | 5.8333 | 0.0700 |
| 250 | PART_001 | 74 | 5.6923 | 0.0683 |
| 250 | PART_005 | 141 | 5.6400 | 0.0677 |
| 500 | PART_000 | 68 | 11.3333 | 0.1360 |
| 500 | PART_001 | 146 | 11.2308 | 0.1348 |
| 500 | PART_005 | 286 | 11.4400 | 0.1373 |
| 750 | PART_000 | 102 | 17.0000 | 0.2040 |
| 750 | PART_001 | 221 | 17.0000 | 0.2040 |
| 750 | PART_005 | 427 | 17.0800 | 0.2050 |
| 1000 | PART_000 | 138 | 23.0000 | 0.2760 |
| 1000 | PART_001 | 293 | 22.5385 | 0.2705 |
| 1000 | PART_005 | 569 | 22.7600 | 0.2731 |
| 1500 | PART_000 | 204 | 34.0000 | 0.4080 |
| 1500 | PART_001 | 442 | 34.0000 | 0.4080 |
| 1500 | PART_005 | 854 | 34.1600 | 0.4099 |
| 2000 | PART_000 | 274 | 45.6667 | 0.5480 |
| 2000 | PART_001 | 592 | 45.5385 | 0.5465 |
| 2000 | PART_005 | 1134 | 45.3600 | 0.5443 |
| 2500 | PART_000 | 341 | 56.8333 | 0.6820 |
| 2500 | PART_001 | 739 | 56.8462 | 0.6822 |
| 2500 | PART_005 | 1420 | 56.8000 | 0.6816 |
| 3000 | PART_000 | 408 | 68.0000 | 0.8160 |
| 3000 | PART_001 | 887 | 68.2308 | 0.8188 |
| 3000 | PART_005 | 1705 | 68.2000 | 0.8184 |

逐 block 曝光计数在 audits/exposure_checkpoint-*.json，可检查实际 sampler 覆盖与离散误差。

## 失败诊断与原始证据

单样本 500-step 是曝光量参照，不是多样本成功所需的硬阈值。PART_000 在联合训练的 2000-step 已严格通过，说明曝光次数不能单独解释全部失败。

单件 exact 回退记录：`[{"part": "PART_000", "from_step": 2000, "to_step": 2500}]`。这些单件回退不等于曾经达到过 3/3；本轮 3/3 稳定性只根据完整 Gate 单独判断。

PART_000 的 GT sequence NLL 从 checkpoint-2000 的 6.793957 降到 checkpoint-3000 的 5.573397，但 raw token exact 从 True 变为 False，最小 margin 从 1.125 变为 -0.375。平均损失改善不保证最薄弱 token 继续保持 top-1。固定分叉 token 的跨 checkpoint margin 轨迹见 divergence_token_margin_trajectory.csv。

- PART_001: MULTI_SAMPLE_ROLLOUT_INSTABILITY; blocks=13, tokens=12932, mean NLL=0.0048746175, first divergence=1/207, min margin=-23.78125.
  GT-prefix token diagnostics at divergence: `{"block": 1, "token_in_block": 207, "gt_id": 21893, "gt_token": "781", "top1_id": 17267, "top1_token": "279", "second_best_id": 17267, "second_best_token": "279", "GT_LOGIT": 18.0, "SECOND_BEST_LOGIT": 21.625, "TOKEN_MARGIN": -3.625, "GT_TOKEN_PROB": 0.02558349259197712, "TOP1_PROB": 0.9600135087966919, "NLL": 3.6658079624176025, "CORRECT": false, "EOS": false, "expanded_position0": 492}`
- PART_005: MULTI_SAMPLE_MEMORIZATION_INCOMPLETE; blocks=25, tokens=25133, mean NLL=0.0072633393, first divergence=1/981, min margin=-13.15625.
  GT-prefix token diagnostics at divergence: `{"block": 1, "token_in_block": 981, "gt_id": 15, "gt_token": "0", "top1_id": 16, "top1_token": "1", "second_best_id": 16, "second_best_token": "1", "GT_LOGIT": 15.375, "SECOND_BEST_LOGIT": 18.25, "TOKEN_MARGIN": -2.875, "GT_TOKEN_PROB": 0.05338948592543602, "TOP1_PROB": 0.9463512301445007, "NLL": 2.9301414489746094, "CORRECT": false, "EOS": false, "expanded_position0": 1167}`

## 预算终点诊断

最终 checkpoint-3000：MULTI_SAMPLE_ROLLOUT_INSTABILITY。该分类单独针对预算终点，不能与按完整 Gate 表现选择的 best checkpoint 混用。

| Part | TF errors | TF token acc | Mean NLL | Free first divergence | Min margin | Exact |
|---|---:|---:|---:|---:|---:|---|
| PART_000 | 1 | 0.999821906 | 0.000992590683 | 3200 | -0.375 | False |
| PART_001 | 4 | 0.999690690 | 0.00121293388 | 3354 | -2.125 | False |
| PART_005 | 7 | 0.999721482 | 0.00162197175 | 689 | -4.25 | False |

后期三个 checkpoint 的最低 TF accuracy 所属零件分别为 `{2000: 'PART_005', 2500: 'PART_000', 3000: 'PART_001'}`；最弱样本发生轮换，本轮不支持把失败统一归结为单一持续落后的 CASE_SPECIFIC_HARD_SAMPLE。


接近 100% 的 TF accuracy 仍允许残余 token 错误；本报告不会把近满分描述为已经完全记忆。Case-specific hard sample 需跨 checkpoint 持续落后，不能只按程序最长或一次最早分叉判定。完整逐件轨迹保留在上表与 CSV 中。

每个失败结果目录含 failure_diff_<part>_<checkpoint>.txt，展示首次分叉前后至少 ±30 tokens 及相邻完整 block。teacher_forced.json 记录 FIRST_WRONG_TOKEN、GT/top1 概率；result.json 记录全部 Gate 字段。首分叉处 TF 诊断基于 GT prefix；发生 cascade 后不得将其当作预测 prefix 下的概率。

checkpoint_metrics.csv 提供完整逐件指标；evaluations/checkpoint-*/summary.json 提供每个 checkpoint 的固定分母汇总。可执行预测另有 metrics.json、prediction.step、原坐标 STEP。

本轮不启动 9-part 或 held-out benchmark。

## 预算决定

```json
{
  "STEPS_REVIEWED": [
    2000,
    2500,
    3000
  ],
  "EVAL_LOSS": {
    "250": 0.06310257315635681,
    "500": 0.01729768142104149,
    "750": 0.013345316983759403,
    "1000": 0.01147096510976553,
    "1250": 0.0038172691129148006,
    "1500": 0.010441785678267479,
    "1750": 0.00323240808211267,
    "2000": 0.005680467467755079,
    "2250": 0.004600515589118004,
    "2500": 0.003964221570640802,
    "2750": 0.002397744683548808,
    "3000": 0.0014440182130783796
  },
  "TF_ACCURACY_BY_PART": {
    "PART_000": [
      1.0,
      0.9973285841495992,
      0.9998219056099733
    ],
    "PART_001": [
      0.9992267244045778,
      0.9997680173213733,
      0.9996906897618311
    ],
    "PART_005": [
      0.9981299486730594,
      0.9994031751084231,
      0.9997214817172642
    ]
  },
  "MEAN_TF_ACCURACY": [
    0.999118891025879,
    0.9988332588597986,
    0.9997446923630229
  ],
  "FIRST_DIVERGENCE_BY_PART": {
    "PART_000": [
      5616,
      328,
      3200
    ],
    "PART_001": [
      207,
      3305,
      3354
    ],
    "PART_005": [
      981,
      4377,
      689
    ]
  },
  "MIN_MARGIN_BY_PART": {
    "PART_000": [
      1.125,
      -6.875,
      -0.375
    ],
    "PART_001": [
      -23.78125,
      -4.0,
      -2.125
    ],
    "PART_005": [
      -13.15625,
      -21.125,
      -4.25
    ]
  },
  "LOSS_CONTINUES_DOWN": true,
  "TF_ACCURACY_CONTINUES_UP": true,
  "DIVERGENCE_CONTINUES_LATER": false,
  "CHECKPOINT_3000_PASS": false,
  "EXTEND_AUTHORIZED_BY_METRICS": false,
  "RESUME_STEP": 3000,
  "NEW_MAX_STEPS": 5000,
  "INTERPRETATION": "Predeclared before collecting checkpoint-2000 free decoding: loss must decline across all three late saved checkpoints; latest macro mean TF accuracy must exceed both preceding values; each latest first-divergence position must be no earlier than either preceding checkpoint and at least one must improve. Individual token-accuracy regressions and intermediate oscillations remain visible. Exact sequences are right-censored at GT token count + 1. This review does not start training.",
  "FULL_EVALUATION_COMPLETED": {
    "2000/PART_000": true,
    "2000/PART_001": true,
    "2000/PART_005": true,
    "2500/PART_000": true,
    "2500/PART_001": true,
    "2500/PART_005": true,
    "3000/PART_000": true,
    "3000/PART_001": true,
    "3000/PART_005": true
  },
  "TRAIN_LOSS_LAST100_MEAN": {
    "2000": 0.008724734553834424,
    "2500": 0.011652324835886248,
    "3000": 0.00350591789567261
  },
  "TRAIN_LOSS_CONTINUES_DOWN": false,
  "ACTUAL_MAX_STEPS": 3000,
  "DECISION": "STOP_AT_3000; NO_EXTENSION",
  "PARTIAL_EVIDENCE_NOTE": "A recorded raw-token divergence proves sequence failure permanently; unfinished matching prefixes are never classified. This budget decision never stops or truncates the pending full rollouts."
}
```

## 评估恢复与 CAD 图

部分评估为调度 GPU 在 block 边界恢复：prefix 仅从该模型已保存的原始预测 token 重建，不使用 GT prefix。每次恢复都独立重放最后一个已保存 block，并要求原始 token 完全一致，见各结果目录的 resume_audit.jsonl。DECODE_SECONDS 是最终工作进程中的测量区间，不用于不同 checkpoint 的速度比较。

CAD 对照图使用已导出的真实 STEP：p1_a2_checkpoint2000_cad_comparison.png 与 p1_a2_checkpoint3000_cad_comparison.png。上排为 GT，下排为对应 checkpoint 的实际预测；不可执行的程序明确显示无 CAD，不以 GT 代替。

下一轮建议仍限定这三个零件，优先检验降低学习率、增加梯度累积能否减少已通过样本的回退；当前证据尚不能确定干扰的唯一原因。本轮未执行这些新训练，也未启动 9-part Gate。


## Teacher-forcing 并列值核验

TF top-1 统一采用 torch.argmax，与 greedy decoding 的并列规则一致。24 项在独立进程中从对应 checkpoint 重新加载、重置 seed 后复核；GT logits、最强竞争 logits、概率、margin 与 NLL 均与原始统计逐 token 完全一致。共 80 个 top-1 token ID 因并列值规则改变，13 项 accuracy 发生变化；全部 Gate 判定不变。原 topk 统计备份与逐项差异保留在 audits/argmax_teacher_verification/。自由生成文件 SHA256 前后一致，最终 checkpoint-3000 指标不变。
