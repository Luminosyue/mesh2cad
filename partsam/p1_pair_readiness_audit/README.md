# mesh–CAD 配对接入现有 P1 的核查

核查时间：2026-09-19。依据服务器上的真实训练配置、资产注册表、导出代码和本批 CAD 文件。

结论：可以构建相同接口的数据集，但当前 2112 对文件尚不能直接用于原 P1。缺少的关键步骤是可执行的建模操作程序重建；STEP 转换成功不等于完成训练样本构建。无法保证全部零件都能通过原有筛选。

## 核对的是哪个 P1

用户所指为 `ours3/p1_operation_aware_structure_loss_v1`，使用 `ours3/exact9998_v1`，训练/验证/测试为 7998/1000/1000。它不是 `curve_encoder_baseline_v1` 中也叫 P1 的 PointNet 基线。

主路径均相对于服务器 `/data/home/cuiyuehan/project/mesh2cad`。

## 数据接口与当前缺口

| 项目 | 现有 P1 / exact9998 | 本批配对现状 |
|---|---|---|
| surface | `surface_points.npy`，xyz + normal；检查的真实样本为 `[8192,6]`，此处是存储形状 | 可从 mesh 采样，但尚未制作并验证对应训练资产 |
| 曲线 | CAD BREP 曲线、采样、类型、拓扑、同一 canonical 坐标变换 | 当前 CAD 保留三角剖分边；不等价于恢复设计曲线 |
| encoder 输入 | 每曲线 `[32,7]`：局部 xyz、tangent、s；另有 log length | 可以计算张量，但输入几何质量需要先解决 |
| C2 tokens | 冻结 C2、sharp-only、按长度排序、最多 128 条，float32 `[K,256]`，`1 <= K <= 128` | 尚无整批符合此协议的 tokens 和注册表 |
| 目标程序 | `program_canonical.dsl`，含建模操作并以 `result` 给出结果 | 2112 个生成脚本中，0 个包含所检查的 P1 DSL 操作调用；canonical DSL 文件为 0 |
| 对话包装 | ShareGPT `conversations` + `point_clouds`，目标是操作程序 | 可以适配；仅包装不能补齐监督 |
| 清洗与监督 | 几何、去重、坐标、资产一致性、上下文、EOS/result、标签与 operation mask | 需要另行运行，不能沿用 STEP 检查作为通过证明 |

真实样本 `deepcad__0000_00000525` 的目标包含 `ExtrudePolygon`、`Box` 和 `Union`；曲线 tokens 为 `[42,256]`。现有 P1 的 operation mask 代码还识别 `Axis, Chamfer, Circle, Cut, Cylinder, Extrude, Fillet, PolygonProfile, Revolve, Sketch, TrueRevolve` 等调用。模型的具体执行器和目标生成器也必须支持所选操作，不能只满足关键字检查。

## 当前 CAD 转换完成度

源目录：`partsam/PartObjaverse-Tiny_instance_stl`。

结果目录：`partsam/PartObjaverse-Tiny_instance_cad`。

200 个对象目录，2112 个 STL 全部生成 CAD code、STEP、BREP，最终完整性检查通过。结果类别：2098 个 faceted_surface、7 个 faceted_solid、7 个 independent_faces。这批 code 的作用是重建三角面 BREP，不是恢复原始设计操作历史。

额外读取了 3 个 STEP（100、742、60 个面）；它们均只有 PLANE 面和 LINE 边，连通实体样本也一样保留三角剖分。此处是明确的抽样结果，不是对 2112 个文件逐边统计。

目前确认符合完整 P1 训练条件的样本数为 0。这表示尚未完成该类样本构建和准入验证，不表示所有源 mesh 都无法重建。

## 要得到等价训练形式的实施顺序

1. 对 mesh 做对象级筛选，优先选择可用少量拉伸、回转、布尔操作表达的零件；开放网格不能默认填补为真实实体。
2. 拟合几何并生成现有执行器支持的操作 DSL，执行程序得到 CAD。操作历史是重建的伪监督，记录来源和误差，不标注为原始设计真值。
3. 对程序生成 CAD 与源 mesh 做几何一致性检查。阈值应按对象尺度制定；不能只检查 STEP 可打开。
4. 对 mesh surface、CAD curves、目标程序使用同一个 canonical 变换，保存变换记录。明确 surface 是原 mesh 还是重建 CAD 的采样，避免混淆输入来源。
5. 使用原 sharp-only 规则提取曲线并通过实际冻结 C2 导出 `[K,256]`，零锐边样本按原协议剔除或独立研究；不能静默替换为 all-edges。
6. 构造 ShareGPT JSON、dataset_info、资产与 token 注册表；复用上下文、监督标签和 operation mask 核查。
7. 按原始对象文件夹划分 train/val/test，同一对象的不同零件不能跨集合；做几何去重并检查原有评测集污染。先独立保存为重建数据源，再决定如何混合训练。

建议先做 10–20 个几何简单零件的完整试验，统计程序执行、几何拟合、锐边 tokens 和上下文筛选的通过率，再扩大。该建议不是已经完成的批量重建结果。本轮没有启动训练，也没有修改原 exact9998 或模型权重。

## 轮胎示例的更正

上一轮将 PointNet 基线 P1 和操作监督 P1 混淆。现已重新导出轮胎示例的 C2 tokens，使用：

`ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt`

SHA-256：`553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9`。

导出器：`scripts/spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py`。

光滑轮胎共有 18 条 BREP 曲线（10 CIRCLE、8 BSPLINE），但 30 度阈值下锐边数为 0。全边版本 `[18,256]` 仅作诊断；sharp-only 为 `[0,256]`，不满足当前 P1 的非空 token 要求。轮胎还缺少通过验证的 canonical 操作 DSL，因此尚不能作为完整训练样本。

服务器核查记录：`partsam/p1_pair_readiness_audit/p1_pair_readiness_audit.json`。

核查脚本：`partsam/audit_p1_pairs.py`。
