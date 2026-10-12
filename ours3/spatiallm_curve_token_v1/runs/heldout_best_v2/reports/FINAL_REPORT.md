# SpatialLM Curve Token best_v2 接管审计：停止报告

审计时间：2026-08-26 18:54 +08:00。仅执行只读检查；未启动、停止或修改任何现有训练。未读取旧 test 指标，未执行 test decode。Phase 0 未全部完成，Phase 1–6 未执行。

## Gates

- PREFLIGHT_AUDIT=STOPPED_PROTOCOL_AND_ACTIVE_RUN_CONFLICT
- COMMON_COHORT_GATE=PASS_FILE_PRESENCE_ONLY
- CURVE_PROTOCOL_GATE=PENDING_NORMALIZATION_AND_PROVENANCE_VERIFICATION
- B1_BUDGET_MATCH_GATE=FAIL_STRICT_POST_ENCODER_GUARANTEE
- BEST_CHECKPOINT_RETENTION_GATE=NOT_VERIFIED
- B0_BEST_TEST=NOT_RUN
- B1_NATIVE_BEST_TEST=NOT_RUN
- B1_BUDGET_MATCH_BEST_TEST=NOT_RUN
- M2_BEST_TEST=NOT_RUN
- M2_STRUCTURE_GATE=PENDING
- M2_GEOMETRY_GATE=PENDING
- ORACLE_TO_MESHFIT_DOMAIN_GAP_GATE=NOT_RUN
- AIRPLANE_BEST_ZERO_SHOT_GATE=NOT_RUN
- PRIMARY_BLOCKER=PRE_ENCODER_BUDGET_TRUNCATION_AND_EXISTING_ACTIVE_RUNS
- NEXT_RECOMMENDED_CHANGE=APPROVE_ISOLATED_POST_ENCODER_BUDGET_FIX_AND_RESTART_PROTOCOL

## 必须停止的证据

项目根目录 /data/home/cuiyuehan/project/mesh2cad 不是 Git 仓库；实际 SpatialLM 子仓库 commit 为 8913c44d84a450c53e9340b13317f8cf7144a738，存在用户修改。本次没有回退或改动。

目标 heldout_best_v2 已存在，且以下进程在本次接管前已经运行，不能当作本次通过审计后启动的正式实验：

| Arm | PID | GPU |
|---|---:|---:|
| B0 | 326722 | 0 |
| B1-native | 326593 | 3 |
| B1-budget-match | 326591 | 4 |
| M2 | 326724 | 5 |

它们执行 scripts/spatiallm_curve_token_v1/train_heldout_arm.py，分别读取该目录 configs/heldout_best_v2_*.yaml。本次未终止这些进程，也没有认可它们已通过全部 preflight/smoke 门禁。GPU 4 还存在 PID 332117；不触碰该进程。

### B1 budget 的实现位置错误

- scripts/spatiallm_curve_token_v1/heldout_geometry.py:312–317 在 dataset loader 中对 voxelized edge_tensor 截取最多 K 行，发生在 point encoder 之前。
- SpatialLM/spatiallm/model/spatiallm_llama.py:206–234 随后调用 point_backbone；:256 将 edge 输入送入这一编码路径。
- SpatialLM/spatiallm/model/sonata_encoder.py:649–657 在每个 GridPooling 中按 stride 除网格并合并相同网格；:919–937 返回 encoder 最终特征。
- 原始 base config 的 Sonata stride=[2,2,2,2]。因此 encoder 输入 K 行不能保证输出 K 个 LLM token；当前代码也未在编码后验证或恢复严格相等。
- :312 使用 max(1,K)，不符合用户要求的 zero-curve 空流协议。本次在 2796 个现有 token 文件中未发现 K=0，因此这是边界协议缺陷，而非已观测到的 zero-curve 样本失败。
- 未执行 100 样本真实 encoder forward token 审计；不能报告严格 budget-match 成功，也不虚构实际 token 差值。

### 已查到的其他偏差

现有 M2 best_v2 config 的 logging_steps=10，而本次要求为25；配置和入口位于旧 scripts/spatiallm_curve_token_v1，而非指定的新 scripts/spatiallm_curve_token_best_v2。现有训练不能无说明地继承为本次新实验。

## 已完成的只读检查

使用 (dataset,sample_id) 作为 manifest 的命名空间主键：
- train/val/test 行数及唯一 ID 数为 2236/280/280；三组两两交集均为0。
- Curve100 ∩ train=100，∩ val=0，∩ test=0。
- 三个 split 的 surface 文件、edge 文件、curve_tokens 文件及 DSL conversation 记录存在性共同覆盖均为100%。
- 所有2796份 curve_tokens.npy 均非空。
- 现有 surface_idx4096.npz 覆盖全部2796个 ID，每条4096个不同索引且均在[0,8192)。
- 尚未完成跨源 CAD 别名/内容重复、增强版本归属、原始 frozen_v1 provenance 的核验；ID 无交集不代表完整泄漏门禁通过。
- 文件存在性不代表全部几何质量或实际 collator cohort 已通过。

## C2 / D1 的初步结论

训练 token 导出器 export_curve_tokens.py 和飞机 prepare_parts.py 共同调用 curve_inputs、load_backbone(DEFAULT_CKPT)，均取模型 out["token"]。
DEFAULT_CKPT=ours3/curve_token_head_v1/runs/D1_frozen_v1_seed0/best.pt。
curve_token_head_v1/models.py 显示 token 为 D1 checkpoint 所含 C2Backbone 的输出，不能仅凭“C2 tokens”名称认定飞机绕过 D1。
已确认函数/默认 checkpoint 路径共享；尚未核对历史产物对应权重哈希、完整 object normalization 和实际采样数据，故不宣告完整协议通过或 mismatch。

## 最小修复方案（尚未实施）

1. 请用户确认如何处理占用 heldout_best_v2 的现有四臂运行。本次不终止、不覆盖；建议保留为待审计既有运行。
2. 在允许的新隔离子目录中实现 post-encoder token 选择：完整 edge 经 Sonata 后，暴露最终 token 坐标，确定性 FPS 恰好选 K_M2 个，保持相同 marker/mask。
3. 若原生 post-encoder token 数小于 K_M2，应显式失败并报告，不通过重复 token、减少 M2 输入或改名隐瞒。
4. 实现 K=0 空内容流；至少100个 train 样本真实 forward 检查数量100%相等，另加 zero-curve 合成协议测试，不加入训练。
5. 补全 Phase 0（来源去重、归一化协议、冻结 tower、surface 实际输入一致性、磁盘预算），之后才能生成四臂配置与 smoke tests。
6. 四臂均从同一原始 base 开始；只有所有 best-val checkpoint 保留/回载验证通过后才解码 test。

## 用户的十项研究问题

1–10 均不能由本次只读审计回答：没有通过门禁的正式 best-val test、配对比较或 oracle/meshfit/airplane best 数据。现阶段不能判断过拟合贡献、结构/几何收益、长流与表示的因果关系、curve 内容使用或域差主因；不能给出可写论文的正式比较结论。用户提供的旧 last 结果仍仅为 diagnostic。本次没有重新读取这些指标。

## 环境

Python 3.11.15；PyTorch 2.4.1+cu124；Transformers 4.46.1；torch CUDA 12.4；驱动550.144.03；8× NVIDIA L20 46068MiB。
18:52快照 GPU 1/2/6/7 各占用1MiB；GPU状态随时可能改变，启动前必须重新确认。
/data 剩余416G、使用率96%；尚未测算四臂 checkpoint 总预算，因此不宣告磁盘充足。

所有旧代码、数据、模型和结果保持不变。此报告是停止报告，不是全部阶段完成报告。

