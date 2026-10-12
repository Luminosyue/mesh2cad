# DEBUG_MULTI_SAMPLE_MEMORIZATION_FAST

**FAST_GATE=PASS**
BEST_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1/runs/quick/checkpoint-60
BEST_EVALUATION=checkpoint-60
NEXT_GATE=AIRPLANE_9_PART_ELIGIBLE

## 执行边界

原有 24 项评估全部复用，未重跑。仅对修正推理后的 checkpoint-2000 做新的三件完整复评；该复评完成前没有追加训练。GT、词表、EOS/PAD、serializer、block grammar、几何源文件、executor 均保持冻结，SHA256 复核通过。

诊断预算 20 分钟；新增训练最多 300 次 optimizer updates、训练总预算 20 分钟；完整评估总墙钟预算 60 分钟。首轮低学习率 150 updates，保留 150 次给有证据支持的单因素加权尝试。预算中止的结果标为未完成，不能算通过。

## 诊断结论

训练 collator 的几何输入为 BF16，旧推理为 FP32。现推理先转为训练输入 dtype，确保送入 point backbone 的数值一致；源 mesh 和 curve 文件没有修改。BF16 decoder 的 cache 开关会改变舍入，PART_005 自由生成第 1200 token 出现 163/812 并列差异。这发生在原始首分叉 981 之后，不能解释或抹去原先的首错。

关闭 TF32、改用 FP32 decoder/lm_head 后，核验位置的同前缀 logits 最大差异为 1.8656254e-05，argmax 一致。三件首块 use_cache=True/False 的全部生成 token 分别一致；这是首块诊断，不冒充整件 Gate。三件 END/EOS 末尾附近另做了同 GT 前缀逐 token 检查。

完整训练前向、无 cache 前缀前向、逐 token cache 推理均保留 logit 向量。完整目标 43680 tokens 含每块 EOS 参与 loss；prompt 的最近 384-token suffix 是原协议，两条路径一致；目标未截断，最大 collated length 小于 4096。

## 对照表

| Experiment | Part | TF errors | First divergence | Pred/GT blocks | Raw exact | END+EOS | CAD | STEP | STEP readback | Complete |
|---|---|---:|---:|---|---|---|---|---|---|---|
| original-2000 | PART_000 | 0 | None | 6/6 | True | True | True | True | not measured in old run | True |
| original-2000 | PART_001 | 10 | 207 | 64/13 | False | False | False | False | not measured in old run | True |
| original-2000 | PART_005 | 47 | 981 | 64/25 | False | False | False | False | not measured in old run | True |
| original-3000 | PART_000 | 1 | 3200 | 6/6 | False | True | True | True | not measured in old run | True |
| original-3000 | PART_001 | 4 | 3354 | 25/13 | False | True | False | False | not measured in old run | True |
| original-3000 | PART_005 | 7 | 689 | 30/25 | False | True | False | False | not measured in old run | True |
| baseline_fixed | PART_000 | 0 | None | 6/6 | True | True | True | True | True | True |
| baseline_fixed | PART_001 | 10 | 207 | 64/13 | False | False | False | False | False | True |
| baseline_fixed | PART_005 | 47 | 981 | 64/25 | False | False | False | False | False | True |
| checkpoint-150 | PART_000 | 0 | None | 6/6 | True | True | True | True | True | True |
| checkpoint-150 | PART_001 | 0 | None | 13/13 | True | True | True | True | True | True |
| checkpoint-150 | PART_005 | 0 | None | 25/25 | True | True | True | True | True | True |
| checkpoint-60 | PART_000 | 0 | None | 6/6 | True | True | True | True | True | True |
| checkpoint-60 | PART_001 | 0 | None | 13/13 | True | True | True | True | True | True |
| checkpoint-60 | PART_005 | 0 | None | 25/25 | True | True | True | True | True | True |

## 最佳点及训练

排序固定为 free-decoding raw exact 数 → CAD 执行且 STEP 回读成功数 → TF 错误数越少越好。只将三件均完成完整评估的 checkpoint 纳入排名，最后一步不自动视为最佳。

```json
{
  "tag": "checkpoint-60",
  "complete_case_n": 3,
  "exact_n": 3,
  "cad_step_readback_n": 3,
  "TF_errors": 0,
  "gate_n": 3,
  "checkpoint": "/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1/runs/quick/checkpoint-60",
  "resolved_checkpoint": "/var/tmp/cuiyuehan_p1_fast_hb0skcbt/quick/checkpoint-60"
}
```

低学习率阶段从原 checkpoint-2000 加载全部权重，AdamW 使用原配置和新状态（该 checkpoint 没有 optimizer state；未混用 checkpoint-3000 状态）。学习率 1e-5 constant；batch=1、梯度累积=3，每个 update 恰好一个 block 来自每件；part 内固定种子循环覆盖所有 blocks；seed=42，随机增强/旋转关闭。三件 block 采样等频，完整程序等效曝光因 6/13/25 blocks 而不同，曝光记录见 audits。

## 重复错误位置

| Part/block/token | Evaluation | GT | Prediction | Margin |
|---|---|---|---|---:|
| 无重复错误位置 | — | — | — | — |

完整错误轨迹见 token_error_trajectory.json；同前缀 GT 诊断数据仅用于定位和训练 loss，全部 Gate 自由生成从空程序开始、只使用模型自身已经生成的 block。未替换预测 token，未强制插入 END/EOS，也未依赖 GT 长度停止。

## 加权决策

```json
{
  "RUN_WEIGHTED_TRIAL": false,
  "reason": "Strict 3/3 raw-token exact, CAD execution and independent STEP readback already passed; no residual TF errors at best checkpoint",
  "new_optimizer_updates_used": 150,
  "unused_update_budget": 150
}
```

EOS 审计：训练标签与 tokenizer EOS/PAD 均为 128009；原 generation_config 接受 [128001, 128008, 128009]，本轮保留该配置。没有 forced_eos、forced_bos、min-length 或 token suppression。即使生成其他终止 ID，也必须满足完整原始 token exact 才能通过，因此不会把替代 EOS 当作 exact。

## 运行结束状态

```json
{
  "phase": "COMPLETE",
  "elapsed_seconds": 1979.9984622001648,
  "active": [],
  "errors": [],
  "FAST_GATE": "PASS",
  "best_checkpoint": "/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1/runs/quick/checkpoint-60",
  "GPU5_restored": true,
  "complete_evaluation_count": 9
}
```

## 最佳模型复现

下面命令通过本轮实际使用的评估入口，从空程序开始自由生成；替换 PART_000 为 PART_001/PART_005 可分别复现另外两件。使用新的输出 tag 避免复用已有结果。

```bash
CUDA_VISIBLE_DEVICES=1 /usr/bin/python3 /data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1/launch/fast_evaluate.py /data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1/runs/quick/checkpoint-60 PART_000 reproduce_best
```

本轮没有增加 token 位置或 END/EOS 权重，除非 audits/weighted_trial_decision.json 明确记录已运行的加权试验。低学习率、三件等频与梯度累积共同构成这一短程配置；没有做独立消融，不能将成功唯一归因于其中某一个因素。
