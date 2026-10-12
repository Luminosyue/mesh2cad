# PartSAM → P1：已生成的独立试验数据

生成日期：2026-09-19。

服务器目录：`/data/home/cuiyuehan/project/mesh2cad/partsam_p1_training_v1`。

对之前指定的 `partsam/PartObjaverse-Tiny_instance_stl` 中 2112 个 STL 完成一轮操作拟合与准入检查，最终得到 **16 个满足本轮数据接口与质量门槛的样本：train 13、val 2、test 1**。来自 13 个对象，按对象分组，兄弟零件不会跨集合。

这些是从 mesh 重建的操作程序伪监督；规模适合检查训练流程，不能替代原 exact9998，也不能据此声称恢复了原始 CAD 设计历史。本轮未启动模型训练。

## 已补齐的内容

每个通过样本位于 `PartSAM/geometry_pack_v1/<object_id>_part_XXX/`：

| 文件 | 内容 |
|---|---|
| `program_canonical.dsl` | 可执行的建模操作目标，含 `ExtrudePolygon`、`Box`、`Cut`、`Union` 中适用的操作 |
| `model.step`、`model.brep`、`model.stl` | 由目标程序生成的 CAD 和网格 |
| `surface_points.npy` | 原始 STL 采样，float32 `[8192,6]`，xyz + 单位面法向 |
| `features_canonical.npy` | 相同的 canonical surface 特征 |
| `coordinate_transform.json` | 原 STL bbox 对角线缩放为 6，同一个变换作用于输入与目标 |
| `curves.json`、`topology.json`、`brep_edges.json` | 重建 CAD 的曲线参数、拓扑与锐边标志 |
| `curve_samples.npz` | 每条曲线 32 点，含 xyz、tangent、mask、类型等原项目字段 |
| `selected_curve_indices.npy` | 按长度排序的锐边选择，最多 128 条 |
| `encoder_input_c2.npz` | `feats=[K,32,7]`、`scale_feat=[K,1]`、对应 edge_id |
| `curve_tokens.npy` | 实际冻结 C2 输出，float32 `[K,256]`，`1 <= K <= 128` |
| `geometry_validation.json`、`training_record.json` | 几何误差、来源、哈希、split 与准入记录 |

`curve_points_sharp_xyztangent.npy` 的后三维是曲线切向量，不是曲面法向，不能当成 surface 点输入。

根目录的 `partsam_p1_train.json`、`partsam_p1_val.json`、`partsam_p1_test.json` 与 `dataset_info.json` 使用实际 P1 的 ShareGPT 接口。`ASSET_REGISTRY.jsonl`、`CURVE_TOKEN_REGISTRY.jsonl` 和 `masks/*_OPERATION_TOKEN_MASK_REGISTRY.jsonl` 分别登记资产、冻结 tokens 和目标 operation token 位置。

## 筛选与验证

操作拟合从这批原 STL 直接进行。本轮尝试最多三个候选轴的轮廓拉伸、盒体和圆柱；多轮廓通过 Union/Cut 组合。没有实施通用自由曲面或任意历史恢复。已有另一套 `partsam_cad_iou_top1000_v1` 候选的同名零件与此处 STL 抽查不匹配，因此其几何和质量分数未作为这批数据的监督来源，只以只读方式复用了候选轴/轮廓拟合辅助函数。

几何准入要求：每方向 4096 个确定性面积采样点，以实际点到三角面的距离评估；除以源 bbox 对角线后，两个方向的均值分别不超过 0.003、P95 分别不超过 0.01，采样最大值不超过 0.03。阈值是本轮重建数据的明确策略，不冒充原 DeepCAD 的原生历史真值检查。采样最大值不是完整解析 Hausdorff 证明。

30 个样本先通过几何和曲线检查；其中剔除 11 个无法可靠确定厚度的近似平面结果，再剔除 3 个保守上下文上界超过 8192 的样本，保留 16 个。上下文上界按每个 surface voxel 最多占一个 token 估算，可能比实际 Sonata 降采样后的长度更保守。

排除总计 2096：

- 2032：本轮支持的操作拟合粗筛误差过大。
- 50：精细双向表面距离检查未通过。
- 11：厚度退化。沿挤出方向的高度或 `2*volume/area` 小于源对角线的 `1e-4`，不能用浮点噪声冒充实体厚度。
- 3：保守上下文预算未通过。

完整排除记录在 `EXCLUDED.jsonl`。排除只代表当前方法/门槛没有通过，不表示这些 mesh 无法被更丰富的重建方法处理。

16 个通过样本均已验证：

- 用项目原 DSL 执行器重新执行目标，STEP 有效，面数一致，面积/体积相对差小于 `1e-7`。
- 原 P1 实际数据 collator 读取 surface 和 C2 tokens，operation mask 对齐且不落在屏蔽标签上；目标完整、result 和 EOS 有监督。
- 使用原训练配置的 `use_fast_tokenizer=false` 再验证一次，不只检查 fast tokenizer。
- 原 STL 哈希未变化；冻结 C2 checkpoint 哈希未变化；对象 split 无交叉。
- 没有执行 LLM 前向、反向或优化器更新；本轮验证范围是数据、执行器和真实 collator。

冻结 C2：`ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt`。

SHA-256：`553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9`。

筛选严格采用 `dihedral > 30°` 的锐边，按长度排序、最多 128 条；没有偷偷改成 all-edges。surface 来自原始 mesh，曲线和程序来自重建 CAD，因此这是与原训练任务同接口的伪监督扩展集。

## 使用方式

`scripts/partsam_p1_runtime.py` 在当前进程中增加 PartSAM 数据源识别，并指向这份 operation mask 注册表；原 P1 源代码和 exact9998 文件不改动。**不能直接把新 JSON 交给未适配的旧入口**，旧入口只识别 DeepCAD/Fusion360 路径和旧 mask 注册表。

试验配置：`configs/p1_partsam_pilot.yaml`。沿用原 P1 基础模型、模板、冻结 surface tower、学习率和 operation loss，设置一轮试验，按 epoch 验证与保存。数据规模太小，配置仅用于跑通流程，不代表正式训练方案。

在服务器上手动启动（本轮未执行）：

```bash
cd /data/home/cuiyuehan/project/mesh2cad
python3 partsam_p1_training_v1/scripts/partsam_p1_runtime.py \
  partsam_p1_training_v1/configs/p1_partsam_pilot.yaml
```

启动前按服务器资源安排设置 `CUDA_VISIBLE_DEVICES`。这条命令会实际训练并把结果写入独立 `runs/p1_pilot`，不会覆盖原 P1 结果。

重新构建与检查：

```bash
python3 partsam_p1_training_v1/scripts/build_partsam_p1.py --workers 24
python3 partsam_p1_training_v1/scripts/finalize_partsam_p1.py
python3 partsam_p1_training_v1/scripts/validate_package_partsam_p1.py
```

构建脚本按版本和每零件记录断点续跑，依赖当前服务器的 mesh2cad 模块与原 STL。发布 zip 包含通过样本的源 STL、全部训练资产、注册表、排除清单、脚本和配置；JSON 路径仍指向服务器的绝对路径，搬到其他机器需统一修改根目录与路径，不能直接当作本机免依赖程序运行。

## 与旧 DeepCAD 数据混合的边界

本轮保留独立数据集，检查了新目标与旧验证/测试目标的精确 AST 重复；没有完成针对旧 exact9998 的几何近重复检索。`legacy_exact9998_mixing_approved=false` 明确记录在资产注册表。若要混入旧训练集并继续报告原评测结果，应先补跨数据源几何去重；当前独立数据的对象分组检查不能代替它。
