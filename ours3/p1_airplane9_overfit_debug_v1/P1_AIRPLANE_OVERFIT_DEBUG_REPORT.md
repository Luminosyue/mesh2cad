# P1 airplane9 第一轮 overfit 严格诊断

## 结论

**PRIMARY_ROOT_CAUSE=C. AUTOREGRESSIVE_ROLLOUT_FAILURE**。原 airplane9 checkpoint-2000 并未实现逐 token 记忆。模型在第 2 个 block 内先写错坐标，错误前缀进入后续 block 后产生漂移；不是把正确的 6 个 block 写完才忘记 EOS。

单样本实验的 **checkpoint-500 已通过 SINGLE_PART_EXACT_OVERFIT=PASS**：TOKEN_ACC=1.0、EOS_ACC=1.0、6/6 blocks 完全一致、5615/5615 生成 token（含各 block 的 EOS）一致，CAD 解析/执行/STEP 导出均通过。程序结束来自模型生成的 `# CAD_COMPLETE` 和 EOS，未使用 GT 长度或 block 数停止，也未修补预测。

## 实验冻结与范围

原目录：`/data/home/cuiyuehan/project/mesh2cad/ours3/p1_quick_overfit_airplane9_v1`。停止原 decoder 与最终状态监控后记录 SHA-256，诊断后复核 56 个文件无修改，详见 `frozen_manifest.json`、`freeze_verification.json`。未修改 checkpoint、原 prediction、log、GT 或原 evaluation result。

独立诊断目录：`/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_overfit_debug_v1`。单样本目录：`/data/home/cuiyuehan/project/mesh2cad/ours3/p1_single_airplane_part_overfit_v1`。训练继续使用原始 6 个 target block、同一 serializer、mesh/点云与曲线特征，没有更改目标程序。

本次是训练样本记忆测试。输入沿用原数据中的点云及 GT CAD 提取的曲线特征（oracle CAD curve inputs），不代表 held-out 泛化或从未知 mesh 重建的完整系统能力。

## loss 与 token 数口径

历史字段 `TRAIN_LOSS=0.02149` 实际是 27 个训练集 block 的 eval memorization loss；全程平均 train loss 为 0.3872258。报告保留历史口径用于对照，但不将它误称为全 134 blocks 的最终训练误差。

本次对全部 134 blocks 重新 teacher-force：TOKEN_ACC=0.9968803198，EOS_ACC=1.0，总计 133347 个有效 label，其中 416 个 token 的 argmax 不等于 GT。

PART_000 原 inventory 的 full_target_tokens=5610 是整段程序字符串的分词口径；逐 block tokenization 后代码为 5609 tokens，另有 6 个受监督 block EOS，因此本诊断的 token denominator 为 5615。二者不混用。

## Stage 1–3：EOS 与 label 证据

```text
TARGET_N=9
TARGET_WITH_EOS_N=9
TARGET_WITHOUT_EOS_N=0
EOS_LABEL_ACTIVE_N=9
EOS_LABEL_MASKED_N=0
PAD_EQUALS_EOS=YES
BLOCK_TARGET_N=134
BLOCK_WITH_EOS_N=134
BLOCK_EOS_ACTIVE_N=134
EOS_MASK_BUG_FOUND=NO
TRAIN_EOS_ID=128009
GENERATION_EOS_ID=[128001, 128008, 128009]
EOS_ID_MATCH=YES
```

EOS 与 PAD 均为 `<|eot_id|>` / 128009。所有 9 个程序末 block 的 EOS label 均有效，134 个 block 也均有效；真正 padding 的 labels 是 -100。CSV/JSON 同时保存 BOS/PAD/EOS、末 30 个 token、EOS raw sequence position、label 值、最后有效 label、padding 起点。位置字段以 0 为起点。

真实代码路径：`SpatialLM/spatiallm/tuner/data/collator.py::_encode_messages_example` 使用 `target_label = target_ids`；HF `DataCollatorForSeq2Seq.__call__` 为新增 padding 添加 -100，而不是按 `input_ids == pad_token_id` 全局抹除；`spatiallm/model/spatiallm_llama.py::_splice_labels` 只 mask 插入的几何位置与补齐位置。精确绝对路径、行号、源码和真实 input_ids/labels 见 `evidence/label_mask_and_generation_sources.json`、`evidence/actual_collator_case0.json`。

训练 EOS 标量与推理 EOS 列表并非字面相等，但实际训练 token 128009 包含于推理停止集合 [128001,128008,128009]；因此 EOS 匹配含义为可被实际停止条件识别，不把列表多出的合法 token 误判为缺失 EOS。完整 runtime/saved/effective 配置见 `generation_config_audit.json`，有效 do_sample=False、num_beams=1、max_new_tokens=1280、use_cache=True。

token EOS 结束一次 block 生成；`# CAD_COMPLETE` 结束整个 CAD program。**6 个训练 block 各自都有 EOS**，若把第一次 EOS 当成整程序结束，会人为只生成 1 个 block。本次保留原协议，不使用 GT block count；同时保存每个 block 的原始生成 token、EOS 位置和结束原因。

## Stage 4：PART_000 teacher-forced 结果

TOKEN_ACC=0.9955476402; BLOCK_TOKEN_ACC=[1.0, 0.9941348973607038, 0.9939879759519038, 0.993103448275862, 0.9970674486803519, 0.9943714821763602]
STRUCTURE_CONTROL_TOKEN_ACC=0.9981250000; EOS_ACC=1.0; SEQUENCE_NLL=101.5548211977; MEAN_NLL=0.0180863439

structure/control 定义：包含 ASCII 字母、语法标点、换行或 EOS 的 token。每个 GT token 的概率、NLL、预测 token 与对错均保存在 `teacher_forced_case0.json`。

```text
GT_EOS_POSITION=block 6; raw sequence index0 1017; geometry-expanded index0 1110
GT_EOS_TOKEN=<|eot_id|>
EOS_PROBABILITY=0.999920070171
EOS_RANK=1
TOP1_TOKEN="<|eot_id|>"
TOP1_PROBABILITY=0.999920070171
TOP2_TOKEN="\n"
TOP2_PROBABILITY=0.000042645872
TOP3_TOKEN="\n\n"
TOP3_PROBABILITY=0.000025866029
LIKELY_TERMINATION_SUPERVISION_FAILURE=NO
```

首个 teacher-forced 错误在 block 2、第 98 个 token：GT=`33`，top-1=`32`，GT 概率约 0.16361。最终 EOS 的高概率是在完整正确 GT 前缀下得到的，不能推导出漂移前缀下也会正确结束。

## Stage 5–6：真实自由解码与首次分叉

新诊断生成 64 blocks；安全 cap=64，cap_hit=True，自然程序结束=False。cap 到达只记为失败/未结束，不算正常完成。

FIRST_DIVERGENCE_TOKEN=1121（1-based，计入 block EOS）; FIRST_DIVERGENCE_BLOCK=2; WITHIN_BLOCK_TOKEN=98。第 1 个 block 一致；第 2 个 block 坐标中的 `[-33.09263, ...]` 首先变为 `[-32.09263, ...]`。这与 teacher-forced 首错相同。

逐 block 原始 GT/pred 和逐 token 原始 ID 全量保存。`case0_block_diff.txt` 展示前 10 个 block（第 7–10 个无 GT）；`case0/token_alignment.jsonl` 按 block 内位置逐 token 对照，缺失侧为 null，未删除任何多余 token。

## 排除性检查：精度和缓存

134 个训练/推理文本 prompt 的 token 序列相同。另观察到 collator 几何输入是 BF16、独立 decoder 是 FP32，且 cached generation 的原 attention mask 长度与几何展开后的 KV 长度不同。没有据此直接改代码或宣布 bug。

对原 checkpoint 的 block 2，用原 cache、无 cache、仅实例内对齐 cache mask 三种方式各生成 128 tokens：首次错误 token0 分别为 {'baseline_cached': 97, 'no_cache': 97, 'geometry_cache_mask_aligned': 97}；均仍在原坐标位置分叉。单样本 checkpoint-100 将 teacher-forcing 几何替换为实际推理 FP32 输入后，准确率与首错不变。证据见 `cache_ablation_block2.json`、`geometry_input_precision_audit.json`、`precision_probe/comparison.json`。

这些控制只支持“本次观察到的首错并未被上述变更消除”，不等于证明所有长序列或其他样本都不存在缓存/精度风险。本报告没有部署这些实验性改动。

## Stage 7–9：单样本 exact-overfit Gate

从与原 9-part 实验相同的 checkpoint-8000 初始化，只用 PART_000 的原始 6 个 block。保存并评估 100、200、500 steps。100-step 的高 token 准确率仍留下 5 个错误 token，因此不满足 exact gate；按 Stage 9 暂停追加训练并完成 EOS/输入/缓存审计。暂停时已存在 checkpoint-500，随后其原始自由解码通过全部 Gate，因此结束训练，未继续保存 1000/2000 steps。这两个更晚 checkpoint 不存在，不报告为已测。

| Checkpoint | Train loss（日志四位小数） | TF token acc | EOS acc | Pred blocks | Token/Block exact | Parse/Exec/STEP | Gate |
|---|---:|---:|---:|---:|---|---|---|
| 100 | 0.0151 | 0.99910953 | 1.0 | 13 | False/False | False/False/False | FAIL |
| 200 | 0.0112 | 0.99661621 | 1.0 | 64 | False/False | False/False/False | FAIL |
| 500 | 0.0 | 1.00000000 | 1.0 | 6 | True/True | True/True/True | PASS |

checkpoint-500 的日志 train loss 被四舍五入为 0.0，**不是数学上的零损失**；独立 teacher-forcing mean NLL=2.156874856e-05。训练侧 eval loss=2.110361856466625e-05。

通过 checkpoint：`/data/home/cuiyuehan/project/mesh2cad/ours3/p1_single_airplane_part_overfit_v1/runs/quick/checkpoint-500`。新 checkpoint 实际存储于 `runs` 符号链接所指向的 `/tmp` 专用目录（因为 /data 当时仅余约 29 GiB），路径与存储说明见 `/data/home/cuiyuehan/project/mesh2cad/ours3/p1_single_airplane_part_overfit_v1/audits/setup.json`。长期保存时需将此专用 checkpoint 目录迁移至有空间的持久卷。

真实模型 STEP：`single_checks/checkpoint-500/prediction.step`；原坐标版本：`single_checks/checkpoint-500/prediction_original_coordinates.step`。两者均由原始 prediction.py 执行导出，未使用 GT program 替换。

## Stage 11：保持原分母的指标

```text
TRAIN_CASE_N=9
TOKEN_ACC=0.9968803197672239
EOS_ACC=1.0
NEW_DIAGNOSTIC_FREE_EVALUATED_N=1
FREE_UNEVALUATED_N=8
BLOCK_COUNT_EXACT_N=0/9
SEQUENCE_EXACT_N=0/9
PARSE_PASS_N=0/9
EXEC_PASS_N=0/9
STEP_PASS_N=0/9
```

9 original parts retained. Numerators are confirmed successes from 1 newly evaluated part; remaining 8 NOT_EVALUATED, not counted as failures or silently removed. These are not complete 9-part free-decode accuracy estimates.

冻结前原任务累计完成 2/9；这份旧快照保留在原目录，未用它代替本轮 1-case 诊断。新的完整 9-part free-decode 准确率为 NOT_MEASURED，8 个未重测样本不被宣称成功或失败。


## 最终机器可读结论

```text
TRAIN_LOSS=0.02149  # 历史字段：实际为27-block memorization eval loss，不是全程平均train loss
PRIMARY_ROOT_CAUSE=AUTOREGRESSIVE_ROLLOUT_FAILURE
SECONDARY_ISSUE=No additional causal bug established; geometry dtype and cache-mask lengths differ, but the tested ablations reproduce the same initial error
AIRPLANE_PART_N=9
CAD_BLOCK_N=134
CHECKPOINT=checkpoint-2000
REPORTED_TRAIN_MEMORIZATION_LOSS=0.02148919180035591
ACTUAL_RUN_AVG_TRAIN_LOSS=0.3872258018180728
TARGET_N=9
TARGET_WITH_EOS_N=9
TARGET_WITHOUT_EOS_N=0
EOS_LABEL_ACTIVE_N=9
EOS_LABEL_MASKED_N=0
PAD_EQUALS_EOS=YES
BLOCK_TARGET_N=134
BLOCK_WITH_EOS_N=134
BLOCK_EOS_ACTIVE_N=134
EOS_MASK_BUG_FOUND=NO
TRAIN_EOS_ID=128009
GENERATION_EOS_ID=[128001, 128008, 128009]
EOS_ID_MATCH=YES
TEACHER_FORCED_TOKEN_ACC=0.9955476402493322
EOS_PROB_AT_GT_END=0.9999200701713562
EOS_RANK_AT_GT_END=1
GT_BLOCK_COUNT_CASE0=6
PRED_BLOCK_COUNT_CASE0=64
FIRST_DIVERGENCE_TOKEN=1121
FIRST_DIVERGENCE_BLOCK=2
FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN=98
DIAGNOSIS=AUTOREGRESSIVE_ROLLOUT_FAILURE
SINGLE_PART_EXACT_OVERFIT=PASS
SINGLE_PART_PRED_BLOCK_COUNT=6
SINGLE_PART_EOS_ACC=1.0
SINGLE_PART_SEQUENCE_EXACT=True
NEXT_GATE=A2: 3 airplane parts, require 3/3 exact free-decoding; not launched in this diagnosis
LIKELY_TERMINATION_SUPERVISION_FAILURE=NO
ROOT_CAUSE=AUTOREGRESSIVE_ROLLOUT_FAILURE
```

## 下一道 Gate

A1 已通过。下一步为 A2：固定 3 个 airplane parts，要求 3/3 自由生成逐 token/逐 block exact match 且解析、执行、STEP 全通过；之后才允许回到 A3 的 9 parts/134 blocks。此次诊断没有启动 3-part 或重训 9-part。

主要复现入口：`scripts/p1_debug_runtime.py audit`、`scripts/p1_debug_runtime.py teacher`、`scripts/p1_evaluate_debug.py --checkpoint ... --out <new_directory> --teacher`。所有生成使用 greedy、每 block 1280-token cap、整程序 64-block 安全 cap，成功要求模型预测 END 与 EOS 且全序列一致。复现请选择新目录，保留本轮证据。
