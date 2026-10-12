# 轮胎 part_006：Curve Encoder 输入

2026-09-19 更正：下文文件名中的 P1 指 PointNet 曲线编码器基线，不是用户所指的 `p1_operation_aware_structure_loss_v1` 训练实验。C2 文件已重新使用实际训练的 `C2_frozen_v1` checkpoint 导出，替换上一版 D1 head checkpoint 结果。本轮胎缺少通过验证的操作 DSL，且 sharp-only 曲线数为 0，因此不能直接作为该 P1 的训练样本。

输入 CAD 是本次对桌面 `part_006.stl` 重建的 `part_006_smooth.step`，不是批量转换中的同名零件。

服务器目录：

```text
/data/home/cuiyuehan/project/mesh2cad/partsam/tire_part006_curve_encoder
```

## 直接用于基线 P1

你现有的 `scripts/curve_encoder_baseline_v1/config.py` 中，P1 定义为 `pointnet` + `xyz,tangent`。

| 文件 | 字段或形状 | 用途 |
|---|---|---|
| `p1_feats.npy` | float32 `[18,32,6]` | 可以直接输入 P1 的特征 |
| `encoder_input_p1.npz` | `feats`, `xyz`, `tangent`, `s`, `point_mask`, `edge_id`, `sharp_mask`, `seam_mask` | 特征及曲线对应关系 |
| `encoder_input_p1.pt` | `feats`, `edge_id` | 相同内容的 PyTorch 张量 |
| `p1_curve_tokens.npy` | float32 `[18,256]` | 使用已有 P1 checkpoint 实际推理得到的 token |
| `curve_labels.npz` | `type_id`, `param`, `param_mask` | 解析曲线类型与参数，仅供监督或核对，不输入 encoder |

每条曲线采样 32 个点。特征第 0–2 通道为对象归一化 xyz，第 3–5 通道为单位切向量。**切向量不是曲面法向量**。P1 不使用第七维弧长位置，也不使用 C2 的独立尺度分支。

```python
from pathlib import Path
import numpy as np
import torch

d = Path('/data/home/cuiyuehan/project/mesh2cad/partsam/tire_part006_curve_encoder')
z = np.load(d / 'encoder_input_p1.npz')
x = torch.from_numpy(z['feats'])  # [18,32,6]，18 条曲线作为 batch
with torch.no_grad():
    result = p1_model(x.to(device))
    tokens = result['token']      # [18,256]
```

完整加载已有 checkpoint 的可运行例子见 `load_p1_example.py`。

## 原始曲线信息

- `curves.json`：18 条曲线的 `edge_id`、类型、参数范围、长度、端点、切线、面/顶点关联，以及原始和归一化解析参数。
- `curve_samples.npz`：你现有 `curve_token_v1` 数据格式，含 `curve_xyz`、`curve_xyz_normalized`、`curve_tangent`、`curve_u`、`curve_mask`、类型、拓扑等。
- `curve_samples_256.npz`：每条曲线 256 点，用于检查或可视化。
- `topology.json`：顶点、边、面关系。
- `normalization.json` / `coordinate_transform.json`：对象坐标变换。
- `baseline_cache_single_cad.npz`：与基线缓存同字段的单 CAD 数据，不会写入现有训练缓存或划分。
- `tire_curves_preview.png`：曲线可视化。

圆/圆弧参数包括圆心、法向、半径、局部轴和参数区间；B-spline 参数包括次数、控制点、节点、重数、权重等。共 10 条 CIRCLE（9 个整圆和 1 条圆弧）、8 条 BSPLINE。类型 ID 沿用项目的 `LINE=0, CIRCLE=1, ELLIPSE=2, BSPLINE=3`，不是直接使用 Open CASCADE 的枚举值。

## 采样和归一化

直接调用服务器上已有的 `curve_token_v1` 代码，采用每曲线 32 点的弧长采样，并记录实际采样方式。

此新样例没有现成的 Track A 变换，所以使用项目既有 fallback：

```text
scale = 6 / CAD 包围盒对角线长度
translation = -scale * bbox_min
xyz_normalized = scale * xyz_world + translation
```

方向向量保持不变。如果后续还要给同一模型输入 surface points，必须对 surface 使用这里同一份 `coordinate_transform.json`，避免两路坐标系不一致。

## 与后续 C2 / SpatialLM 区分

另提供 `encoder_input_c2_all_edges.npz`：`feats=[18,32,7]`、`scale_feat=[18,1]`。配方直接复用 `spatiallm_curve_token_c2_frozen_v2.export_curve_tokens.curve_inputs`，即曲线局部 xyz + tangent + s，以及 `log(对象归一化曲线折线长度 + 1e-6)`。`c2_curve_tokens_all_edges.npy` 是实际冻结 C2 checkpoint 的诊断性推理结果。

**这个平滑 CAD 在项目默认 30° 阈值下没有锐边。**因此，严格遵循原 C2 sharp-only 选择规则时，`encoder_input_c2_sharp_only.npz` 是 `[0,32,7]`，`c2_curve_tokens_sharp_only.npy` 是 `[0,256]`。不能直接把 all-edges 版本当成和 sharp-only 训练协议完全相同的数据。

18 条曲线中有 9 条回转曲面的参数接缝，其余包括光滑曲面分段边界。这些是重建 CAD 的拓扑曲线，不全部是物体上真实锐利的轮廓，也不能视为原设计的真值。`seam_mask`、`sharp_mask` 和 `curves.json` 提供筛选依据。

## 已完成的验证

- 18 条曲线的解析参数提取与几何重建核对均通过。
- 32 点采样全部有效、数值有限；单位切向量范数最大误差约 `5.96e-8`。
- 使用 `ours3/curve_encoder_baseline_v1/runs/P1_frozen_v1/best.pt`，CPU 推理输出 `[18,256]`。
- 使用 `ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt`，验证 C2 all-edges 输入可执行；checkpoint SHA-256 为 `553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9`。
- 原训练数据、模型权重均未修改。checkpoint 和源 STEP 的 SHA-256 记录在 `curve_export_summary.json`。

在服务器本目录执行 `python3 export_tire_curves.py` 可重新生成以上文件；该脚本依赖当前 mesh2cad 仓库中的原有模块。
