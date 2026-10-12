# 复杂高模 Mesh → 参数化 CAD：第一阶段交付包

## 1. 已完成内容

本交付包已经完成一个**受控最小可行实验**：

```text
高模三角 Mesh（53,248 faces）
        ↓
按连通体拆分 5 个 Part
        ↓
顶点聚类简化（9,320 faces，降低 82.50%）
        ↓
PCA + 几何模型选择
        ↓
1 个 box + 4 个 cylinders
        ↓
参数 JSON + OpenSCAD CAD 程序 + 重建 Mesh
        ↓
Chamfer / Hausdorff 评价
```

结果：

- 输入：26,634 vertices，53,248 faces，5 个水密连通 Part；
- 低模：4,670 vertices，9,320 faces；
- 参数重建：5 个基元，1 个 box 和 4 个 cylinders；
- 归一化 Chamfer：0.003185；
- 归一化 Hausdorff：0.011310。

这个实验验证的是**数据与评价闭环**，不是开放世界 Mesh-to-CAD 已解决。当前只支持分离的规则零件、box 和 cylinder，未支持融合零件、孔洞、布尔历史、圆角、倒角和自由曲面。

## 2. 文件结构

```text
mesh_to_cad_stage1/
├── run_mvp.py                     # 可直接重复运行的受控 MVP
├── export_step_cadquery.py        # 有 CadQuery 环境时导出 STEP
├── environment.yml                # 推荐独立 Conda 环境
├── README.md
└── outputs/
    ├── 01_input_highpoly_table.ply/.obj
    ├── 02_lowpoly_vertex_cluster.ply/.obj
    ├── 03_parametric_reconstruction.ply/.obj
    ├── 03_parametric_reconstruction.scad
    ├── primitives.json
    ├── metrics.json
    ├── part_*.ply
    └── preview_*.png
```

## 3. 复现实验

当前基础实验只需要 `numpy scipy trimesh matplotlib`：

```bash
python run_mvp.py
```

有 CadQuery 后，将参数基元导出为 STEP：

```bash
conda env create -f environment.yml
conda activate mesh2cad-stage1
python export_step_cadquery.py \
  --input outputs/primitives.json \
  --output outputs/03_parametric_reconstruction.step
```

然后用 FreeCAD 打开 STEP，检查：

1. 是否能正常读取；
2. 是否包含 5 个独立 Part；
3. 面类型是否为平面和圆柱面，而不是大量三角面；
4. 能否修改圆柱半径、长度和桌面尺寸；
5. 再导出 Mesh，与输入计算 Chamfer/Hausdorff。

## 4. 接下来必须做的真实实验

### 轨道 A：有 CAD 真值的受控实验

优先使用 ABC Dataset。它同时提供显式参数曲线/曲面和可采样的 Mesh，因此可以把 CAD 高精度离散化为高模，再测试是否恢复回原 B-Rep。

建议先选 10–20 个模型，分层覆盖：

- 只含平面；
- 平面 + 圆柱；
- 带孔和布尔切除；
- 圆角/倒角；
- 圆锥、球面或圆环面；
- 至少 1–2 个自由曲面。

每个样本生成三档 Mesh：50k、10k、2k faces，比较简化前后和重建结果。

### 轨道 B：开放世界复杂 Mesh 压力测试

优先从 PartNet 或 PartObjaverse-Tiny 选 5 个对象：

- 桌子；
- 椅子；
- 交通工具；
- 电子设备；
- 一个表面复杂但不适合制造的角色/动物资产作为反例。

先跑 Trimesh 连通体，再跑 PartField。必须人工标记：

- 分出的 Part 是否是可制造零件；
- 是否只是颜色/纹理区域；
- 是否把一个零件切碎；
- 是否把多个真实零件合并。

## 5. 推荐方法顺序

```text
Mesh 审计：Trimesh
简化基线：PyMeshLab QEM
开放世界 Part：PartField
解析基元：RANSAC / SPFN / ParSeNet
完整 B-Rep：Point2CAD
可执行 CAD 程序：CADFit + CAD-Recode
最终内核验证：CadQuery / Open CASCADE Shape Healing + STEP
```

不要先复现没有完整代码的 Mesh2Brep，也不要一开始训练自己的网络。先在官方 demo 和小样本上测清楚输入约束、成功率、耗时和失败类型。

## 6. 统一评价协议

每个样本至少记录：

- 输入 vertices、faces、连通体数、水密性、非流形边数；
- 分割 Part 数和人工可制造 Part 正确率；
- 简化率、Chamfer、Hausdorff、法向误差；
- CAD 是否能由内核构造；
- STEP 是否可写、可重读；
- solid 是否有效、水密；
- 解析曲面类型准确率；
- 半径、长度、角度等参数误差；
- B-Rep face/edge/vertex 数量误差与邻接匹配；
- 单样本运行时间和失败阶段。

过滤门建议：

```text
STEP 可重读 = true
有效 solid = true
归一化 Chamfer < 0.01（首轮暂定）
归一化 Hausdorff < 0.03（首轮暂定）
不存在明显丢孔、薄壁消失或 Part 合并
```

阈值应通过 ABC 真值实验重新标定，不能直接作为最终论文标准。

## 7. 关键来源

- Open3D Mesh simplification: https://www.open3d.org/docs/release/tutorial/geometry/mesh.html
- PyMeshLab filters: https://pymeshlab.readthedocs.io/en/latest/filter_list.html
- PartField: https://github.com/nv-tlabs/PartField
- SAMPart3D: https://github.com/Pointcept/SAMPart3D
- Point2CAD: https://github.com/prs-eth/point2cad
- CAD-Recode: https://github.com/filaPro/cad-recode
- CADFit: https://github.com/ghadinehme/CADFit
- Open CASCADE Shape Healing: https://dev.opencascade.org/doc/overview/html/occt_user_guides__shape_healing.html
- ABC Dataset: https://deep-geometry.github.io/abc-dataset/
