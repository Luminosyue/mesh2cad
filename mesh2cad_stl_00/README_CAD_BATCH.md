# mesh2cad batch output

源目录：`/data/home/cuiyuehan/project/mesh2cad/mesh2cad_stl/parts`

批处理已完成 626 个 STL。每个样本在 `cad_results/<原相对路径去掉 .stl>/` 下生成：

- `cad_model.py`：可独立重建该样本 CAD 的 CadQuery 代码；
- `mesh_decimated.stl`：用于 CAD 重建的最多 5,000 面输入网格；
- `model.step`：OpenCascade 缝合后的分面 CAD；
- `metrics.json`：IoU 和 CAD 拓扑指标；
- `source.txt`：原 STL 相对路径。

## 质量筛选

IoU 使用源网格和用于缝合 CAD 的降面网格计算：自适应 64³ 体素占用交并比。阈值为 **0.90**。源 STL 不能直接作为 watertight solid，因此指标以表面体素占用为准；STEP 与 `mesh_decimated.stl` 使用同一组三角面生成，避免重新三角化引入额外误差。

| 项目 | 数量 |
|---|---:|
| 总 STL | 626 |
| 主目录保留 | 598 |
| 隔离 | 28 |
| IoU < 0.90 | 8 |
| IoU 达标但 CAD 无效/多壳 | 20 |

低质量原始 STL 已移动到：

`/data/home/cuiyuehan/project/mesh2cad/mesh2cad_stl/parts_rejected_iou_lt_0.90/`

这是可恢复的隔离目录，没有直接删除。完整清单：

- `cad_results/all_manifest.csv`
- `cad_results/kept_manifest.csv`
- `cad_results/rejected_manifest.csv`
- `cad_results/summary.json`

保留集 IoU 最小值为 0.90738，均值为 0.98168。

## 重建

单个样本：

```bash
cd /data/home/cuiyuehan/project/mesh2cad/mesh2cad_stl/cad_results/<sample>/
python3 cad_model.py
```

顶层 `rebuild_all.py` 可以批量重建全部结果目录：

```bash
python3 /data/home/cuiyuehan/project/mesh2cad/mesh2cad_stl/rebuild_all.py
```

运行环境需要 `cadquery` 和 `OCP`。模型是分面 shell；由于原始 STL 多数不是 watertight solid，`solids=0` 是预期结果。若必须得到实体 solid，需要先修复原网格边界/法向，再执行实体化。
## 可视化

- `cad_results/visualization/comparison.png`：4 个代表样本的 source mesh / reconstructed CAD / overlay 对比图。
- `cad_results/visualization/interactive.html`：可旋转、缩放，并切换 4 个代表样本的交互式查看器。