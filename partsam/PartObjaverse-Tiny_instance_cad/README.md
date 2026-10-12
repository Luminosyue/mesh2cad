# PartObjaverse-Tiny：按原文件夹转换 CAD

输入：`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl`

输出：`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_cad`

每个对象沿用原文件夹名称，每个 STL 对应：

- `part_XXX_cad.py`：独立运行的 Python / CadQuery 建模代码，内嵌顶点和三角面数据，无需读取原 STL。
- `part_XXX.step`：通用 CAD 交换文件。
- `part_XXX.brep`：Open CASCADE 原生 CAD 边界表示。
- `part_XXX_report.json`：原文件 SHA-256、网格状态、实体/曲面类型、退化面处理、CAD 有效性、STEP 重新导入验证。
- `part_XXX_conversion.log`：执行日志。
- `folder_summary.json`：本文件夹所有零件的处理结果。

## 几何类型与局限

本批次优先保留输入形状，输出为**三角平面构成的 BREP CAD**。代码可重新构建 CAD，但不代表已经恢复原始草图、拉伸、旋转等参数化设计历史，也不是自动生成平滑曲面的逆向拟合。

STL 若为封闭网格，则尝试输出 CAD 实体；开放网格输出 CAD 曲面/壳。不能把开放曲面当成闭合实体使用。非流形连接无法组成有效壳时，保留为独立面的集合，并在报告中标注 `independent_faces`。零面积退化三角面会被跳过，其索引记录在报告中。不会自动填补缺失区域或猜测厚度。

原网格文件不修改，原坐标数值及位置保留。STL 没有单位信息，STEP 标签为毫米，但原始物理单位未经确认。

部分输入含近乎共线的细长三角面，在 STEP 导入时会退化。对这些失败件，重试代码会跳过最小高低于 `1e-7`（原始数值单位）的三角面；报告中 `subtolerance_faces_skipped` 明确记录全部索引。此处理不补面、不引入厚度，可能保留微小开放边界。

## 重新运行单个零件

服务器已有 CadQuery、Open CASCADE 和 NumPy：

```bash
python3 对象文件夹/part_000_cad.py
```

输出到另外的位置：

```bash
python3 对象文件夹/part_000_cad.py --output-directory /需要的输出目录
```

## 批量进度及恢复

- `progress.json`：已处理数量、成功和失败数量、完成状态。
- `conversion_summary.csv`：全部零件结果清单（批次结束后生成）。
- `failed_files.json`：失败列表（批次结束后生成）。
- `input_inventory.json`：输入检查记录。
- `batch_run.log`：总体运行日志。

```bash
python3 scripts/server_cad_status.py
python3 scripts/server_batch_cad.py --workers 24
```

恢复运行时跳过已有完整成功结果，重试失败和未处理文件。每个零件独立进程，首轮超时 420 秒，复杂件重试延长至 1200 秒；失败保留日志，不计为完成转换。所有成功 STEP 必须重新导入后通过几何有效性、面数和包围尺寸检查。
