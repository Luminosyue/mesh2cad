# 坦克零件：CadQuery 标准操作重建

45 份独立脚本和 STEP；38 件通过本次形状筛选，7 件仍需细化。全部脚本已重新运行验证。PART_042 车体为 5 个实体，连接拓扑仍未完全恢复。

每件的 `PART_###.py` 是独立脚本，只依赖 CadQuery 与 Python 标准库。它包含截面草图参数并通过拉伸、旋转、放样与布尔并集构造实体；不读取 STL、STEP、BREP 或三角网格控制点，也不调用旧版 Bézier 曲面分块。

安装 `pip install cadquery==2.8.0`，运行 `python PART_000.py`，STEP 会输出到脚本旁。编辑脚本内 `PARAMETERS` 可以调整截面、厚度、轴向位置等。`parameters.json` 供查看，修改它不会自动修改脚本。脚本中的 `build()` 返回 CadQuery Shape，可在 CQ-editor 中调用 `show_object(build())`。

## 精度与范围

这是从网格推断的近似重建，不是恢复原始设计历史，也不是全部零件均已完成工程级特征建模。旋转轮廓含样条；复杂件使用多截面放样、布尔并集和凹腔切除。`base_and_profile_pads` 按截面变化推断不同厚度区域，使用少量深度区间的拉伸特征，仍会简化圆角和连续厚度变化。`extruded_body_and_end_features` 使用主体与端部拉伸。没有声称已经识别所有孔、圆角、阵列或每个零件的设计意图。部分截面参数较多，修改主尺寸不等于具备原始设计约束。

实验中的均匀多层拉伸方案已经排除。多实体结果会在下表列明实体数，不能当作连接拓扑已恢复的单实体模型。

`APPROXIMATION_ACCEPTED` 表示通过本次探索性筛选：双向采样 P95 ≤ 1% 包围盒对角线、体积偏差 ≤ 10%、采样最大偏差 ≤ 4%。这不是用户指定的制造公差。`NEEDS_REFINEMENT` 表示脚本与 STEP 有效，但形状偏差未达上述条件，不能作为已完成的高保真替代。具体缺失和形状差异请看对比图。

每个最终 STEP 均重新导入检查，并以重新导入后实体的三角化结果计算误差；每方向 6000 个固定随机种子的表面样本，点到三角面距离，不做重新对齐，采样最大值不是严格 Hausdorff 距离。保留原 STL 数值坐标和装配位置；STL 无单位信息，STEP 标注 mm 不代表源模型物理单位已知。

## 逐件结果

| 零件 | 操作 | CAD 面数 | 实体数 | P95 / 对角线 | 体积偏差 | 状态 |
|---|---|---:|---:|---:|---:|---|
| PART_000 | loft | 66 | 1 | 0.097% | 2.51% | APPROXIMATION_ACCEPTED |
| PART_001 | loft | 130 | 1 | 0.137% | 2.20% | APPROXIMATION_ACCEPTED |
| PART_002 | loft | 34 | 1 | 0.355% | 0.50% | APPROXIMATION_ACCEPTED |
| PART_003 | loft | 66 | 1 | 0.076% | 3.39% | APPROXIMATION_ACCEPTED |
| PART_004 | branched_loft_and_pockets | 50 | 1 | 0.335% | 0.45% | APPROXIMATION_ACCEPTED |
| PART_005 | revolve | 14 | 1 | 0.505% | 0.29% | APPROXIMATION_ACCEPTED |
| PART_006 | revolve | 14 | 1 | 0.732% | 0.09% | APPROXIMATION_ACCEPTED |
| PART_007 | extruded_body_and_end_features | 179 | 1 | 0.510% | 0.17% | APPROXIMATION_ACCEPTED |
| PART_008 | loft | 34 | 1 | 0.261% | 0.61% | APPROXIMATION_ACCEPTED |
| PART_009 | revolve | 14 | 1 | 0.529% | 0.22% | APPROXIMATION_ACCEPTED |
| PART_010 | loft_with_pockets | 69 | 1 | 0.226% | 0.13% | APPROXIMATION_ACCEPTED |
| PART_011 | loft | 34 | 1 | 0.265% | 0.64% | APPROXIMATION_ACCEPTED |
| PART_012 | loft | 34 | 1 | 0.297% | 0.57% | APPROXIMATION_ACCEPTED |
| PART_013 | branched_loft_and_pockets | 60 | 1 | 0.252% | 0.27% | APPROXIMATION_ACCEPTED |
| PART_014 | revolve | 14 | 1 | 0.575% | 0.54% | APPROXIMATION_ACCEPTED |
| PART_015 | loft | 34 | 1 | 0.153% | 0.46% | APPROXIMATION_ACCEPTED |
| PART_016 | loft | 66 | 1 | 0.102% | 0.21% | APPROXIMATION_ACCEPTED |
| PART_017 | loft_with_pockets | 69 | 1 | 0.230% | 0.13% | APPROXIMATION_ACCEPTED |
| PART_018 | loft | 66 | 1 | 0.092% | 0.24% | APPROXIMATION_ACCEPTED |
| PART_019 | loft | 130 | 1 | 0.284% | 0.40% | APPROXIMATION_ACCEPTED |
| PART_020 | loft | 66 | 1 | 0.723% | 4.13% | APPROXIMATION_ACCEPTED |
| PART_021 | loft | 22 | 1 | 0.727% | 1.51% | APPROXIMATION_ACCEPTED |
| PART_022 | loft | 66 | 1 | 0.246% | 0.33% | APPROXIMATION_ACCEPTED |
| PART_023 | branched_loft_and_pockets | 106 | 1 | 0.539% | 0.98% | NEEDS_REFINEMENT |
| PART_024 | loft | 66 | 1 | 0.396% | 1.16% | APPROXIMATION_ACCEPTED |
| PART_025 | loft | 66 | 1 | 0.652% | 0.34% | APPROXIMATION_ACCEPTED |
| PART_026 | loft | 66 | 1 | 0.122% | 0.25% | APPROXIMATION_ACCEPTED |
| PART_027 | loft | 34 | 1 | 0.279% | 1.78% | APPROXIMATION_ACCEPTED |
| PART_028 | branched_loft_and_pockets | 78 | 1 | 0.691% | 0.05% | APPROXIMATION_ACCEPTED |
| PART_029 | base_and_profile_pads | 817 | 1 | 1.091% | 0.53% | NEEDS_REFINEMENT |
| PART_030 | branched_loft_and_pockets | 50 | 1 | 0.157% | 0.28% | APPROXIMATION_ACCEPTED |
| PART_031 | branched_loft_and_pockets | 76 | 1 | 0.506% | 0.12% | APPROXIMATION_ACCEPTED |
| PART_032 | loft | 66 | 1 | 0.113% | 0.19% | APPROXIMATION_ACCEPTED |
| PART_033 | revolve | 14 | 1 | 1.947% | 0.65% | NEEDS_REFINEMENT |
| PART_034 | loft | 34 | 1 | 0.218% | 0.40% | APPROXIMATION_ACCEPTED |
| PART_035 | branched_loft_and_pockets | 82 | 1 | 0.472% | 0.62% | APPROXIMATION_ACCEPTED |
| PART_036 | base_and_profile_pads | 554 | 1 | 0.964% | 0.50% | NEEDS_REFINEMENT |
| PART_037 | base_and_profile_pads | 1115 | 1 | 0.370% | 0.65% | APPROXIMATION_ACCEPTED |
| PART_038 | branched_loft_and_pockets | 58 | 1 | 0.605% | 0.88% | APPROXIMATION_ACCEPTED |
| PART_039 | branched_loft_and_pockets | 55 | 1 | 0.560% | 0.82% | APPROXIMATION_ACCEPTED |
| PART_040 | base_and_profile_pads | 1723 | 1 | 0.975% | 0.03% | NEEDS_REFINEMENT |
| PART_041 | branched_loft_and_pockets | 73 | 1 | 0.343% | 0.39% | NEEDS_REFINEMENT |
| PART_042 | base_and_profile_pads | 741 | 5 | 2.211% | 0.92% | NEEDS_REFINEMENT |
| PART_043 | loft | 34 | 1 | 0.095% | 0.85% | APPROXIMATION_ACCEPTED |
| PART_044 | loft | 258 | 1 | 0.171% | 0.57% | APPROXIMATION_ACCEPTED |
