# 坦克整体装配与可视化

- `tank_assembly.step`：精确 CAD 装配，45 个命名零件、49 个实体，保留原坐标及独立零件。
- `tank_viewer.html`：双击在浏览器打开。无需网络，支持拖动旋转、滚轮缩放、逐件隐藏与待细化零件高亮。
- `tank_assembly.png`：整体斜视图。
- `tank_multiview.png`：四视角预览。
- `tank_assembly_comparison.png`：左侧原始 STL，右侧 CadQuery 重建装配，同坐标与视角。
- `tank_assembly_preview.glb`：轻量化三维预览，展示用几何已居中并归一化；精确尺寸和坐标以 STEP 为准。
- `assembly_report.json`：组成、坐标范围和整体 STEP 重新导入检查结果。
- `rebuild_assembly.py`：从上一批 CadQuery STEP 文件重新装配的脚本。

本次使用最近交付的 CadQuery 特征重建版本，按源模型已有的相对位置装配，没有添加机械配合约束，也没有把各零件布尔融合为一个实体。源 STL 物理单位未知，保留其数值坐标。

仍需细化的零件：PART_023、PART_029、PART_033、PART_036、PART_040、PART_041、PART_042。PART_042 车体包含 5 个实体，部分连接与细节尚未恢复；装配不会自动修复这些问题。网页中可勾选“标出待细化零件”查看。
