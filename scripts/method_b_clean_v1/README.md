# method_b_clean_v1

按 Jerry Method-B（Curve Token）契约清洗数据。三源分桶，不做全局 shuffle 混池。

## 输出

```text
cad_spatial_dataset/method_b_pack_v1/cadfs/<id>/
  mesh_clean.obj
  mesh_noise_001.obj / _005.obj / _01.obj
  surface_points.npy          # [4096,6] xyz+normal，无 edge_score
  sharp_edges.npy             # [M,3] 锐边中点（canonical）
  edge_points.npy             # [1024,3] Method A 消融用
  curves.json                 # Method B 完整参数（OCC 精确提取）
  curves_compact.json         # Jerry 简表（line/circle/ellipse/bspline）
  normalization.json
  qa.json / metadata.json

cad_spatial_dataset/method_b_clean_v1/
  manifests/
    deepcad_curve_ready.json
    fusion360_curve_ready.json
    cadfs_candidates_500.json
    scale_overfit100.json
  statistics/method_b_clean_stats.md
```

## 冻结参数

| 项 | 值 |
|---|---|
| OCC linear | `max(0.01 * bbox_diag, 1e-6)` |
| OCC angular | `10°` |
| surface | 4096×6 |
| sharp | dihedral > 30° |
| noise σ | 0.001 / 0.005 / 0.01（相对 bbox 对角） |

## 运行

```bash
# 全流程：harvest DeepCAD/Fusion + 选 CADFS + 建 50 个 pack + 写 overfit100 manifest
python3 scripts/method_b_clean_v1/run.py --stage all --cadfs-n 50 --cadfs-pool 500 --workers 8

# 只扩 CADFS
python3 scripts/method_b_clean_v1/run.py --stage build --cadfs-n 200 --workers 16 --overwrite
```

DeepCAD / Fusion360 的 Method-B `curves.json` 已在 `ours3/curve_token_data_v1/`；本包 harvest 它们并写入分源 manifest，不重抽。CADFS 需要从 STEP 新建 pack。
