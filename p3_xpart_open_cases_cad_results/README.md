# p3_xpart_open_cases STL → CAD

处理目录：`/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases`

## 结果

目录中发现 45 个 STL（均位于 `tank/xpart_parts/`）。全部样本均成功生成并通过 CAD 回读验证：

| 指标 | 数量 / 数值 |
|---|---:|
| 输入 STL | 45 |
| 生成 CAD code | 45 |
| 生成 STEP | 45 |
| CAD 重建成功 | 45 |
| 有效 CAD | 45 |
| CAD solid 数量 | 每个 1 |
| IoU < 0.90 | 0 |
| 保留 | 45 |
| 隔离 / 删除 | 0 |
| 表面 IoU 均值 | 0.967006 |
| 表面 IoU 最小值 | 0.930277 |
| 体积 IoU 均值 | 0.995317 |
| 体积 IoU 最小值 | 0.939641 |

没有低于 0.90 的数据，因此没有移动任何源 STL；原目录保持 45 个 STL。

## 输出结构

`p3_xpart_open_cases_cad_results/samples/<原 STL 相对路径去掉 .stl>/` 下每个样本包含：

- `cad_model.py`：独立可运行的 CadQuery/OCP CAD 重建代码，内嵌降面三角网格数据；
- `mesh_decimated.stl`：最多 5,000 面的重建输入；
- `model.step`：代码生成并回读验证过的 STEP；
- `cad_rebuilt.stl`：STEP 回读后的三角网格；
- `metrics.json`：IoU、拓扑和重建日志指标；
- `rebuild.log`：该样本的 code 重建输出。

## 指标定义

筛选指标是表面体素 IoU：源 STL 和 STEP 回读网格使用相同世界坐标和 64 个最长轴分辨率的体素网格，计算表面占用集合的交并比。源网格与 STEP 都闭合且方向一致的 45 个样本另外计算体积 IoU；体积 IoU 采用 64³ 共同包围盒采样点的实体占用交并比。

源网格三角面数平均为 35,978；CAD 使用 Quadric decimation 后统一为 5,000 面。每个生成 CAD 均回读为 1 个有效 solid。表面 IoU 最低的是 `tank/xpart_parts/PART_038.stl`，为 0.930277；其体积 IoU 为 0.986755，仍明显通过阈值。

## 批量重建

单个样本：

```bash
cd /data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results/samples/tank/xpart_parts/PART_000
python3 cad_model.py
```

批量结果清单：

- `all_manifest.csv`
- `kept_manifest.csv`
- `rejected_manifest.csv`
- `error_manifest.csv`
- `summary.json`

筛选代码和参数保存在服务器：

`/data/home/cuiyuehan/project/mesh2cad/p3_batch.py`