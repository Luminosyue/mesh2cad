# V3 frozen pilot-eval 150 qualitative visualization v1

隔离目录。只读 frozen pilot-eval 结果，不重训、不重 decode、不读 official test，不改任何原始 `per_cad.jsonl` / `SUMMARY.json`。

## 路径

- 脚本：`scripts/v3_pilot_visualization_v1/`
- 输出：`ours3/.../geometry_prefix_v3/v3_1k/pilot_eval_150_frozen_v1/visualization_v1/`

```bash
python scripts/v3_pilot_visualization_v1/run_visualization.py
```

## 读什么

- GT 几何：`surface_input` 同目录 `mesh.obj`（与 Chamfer 评估同一份）
- B0 / B1 / M2：frozen `per_cad.jsonl` 里的 `generated_dsl`，用已修复 executor **重放** 成 STEP/STL
- 指标：直接用 frozen jsonl（Op F1、Chamfer、Hausdorff95、runaway、parse、execute、STEP）

## 12 样本选样规则（固定，非手挑）

公平对比优先 **91 条 common-valid**（三臂 STEP reload 都成功）。

| 类别 | n | 集合 | 规则 | 目的 |
|---|---|---|---|---|
| A M2 明显最好 | 3 | 91 | `M2 OpF1 - max(B0,B1)` 最大，且 `min(B0,B1) Chamfer - M2 Chamfer >= 0.05` | 看 M2 结构/几何优势是否可见 |
| B B0 明显最好 | 3 | 91 | `M2 Chamfer - B0 Chamfer >= 0.25`，按 gap 降序 | 看 M2 在哪些类型上会输 |
| C 三者接近 | 3 | 91 | OpF1 spread ≤ 0.08 且 Chamfer spread ≤ 0.08；先 mean OpF1 再 spread 再 mean Chamfer | 简单 CAD 三者都能做 |
| D M2 失败 | 3 | 150 | M2 STEP 失败，且 B0 或 B1 STEP 成功；各取 1 个 runaway / parse / geom-fail | 稳定性失败长什么样 |

类别之间 `cad_id` 不重复。并列时用 `cad_id` 字典序打破平局。

## 每张图干什么

| 文件 | 用途 |
|---|---|
| `figures/total_summary.png` | 150 overall 与 91 common-valid 的 runaway / STEP / Op F1 / Chamfer / H95 |
| `figures/total_summary_table.png` | 同一组数字的表 |
| `figures/gallery_12.png` | 12 样本 isometric：GT \| B0 \| B1 \| M2 |
| `figures/gallery_12_boards.png` | 12 张完整三视角 board 竖拼 |
| `figures/m2_advantage.png` | 类别 A，三视角四列 |
| `figures/failure_board.png` | 类别 D，三视角四列；失败格显示 `STEP_FAIL` |
| `figures/scatter_opf1_vs_chamfer.png` | 每点一个样本；看 M2 是否往高 F1、低 Chamfer 偏 |
| `figures/scatter_generated_length_vs_step.png` | 生成长度比 vs STEP 成败 |
| `samples/<id>/board.png` | 单样本：iso / front / top × GT/B0/B1/M2 |
| `samples/<id>/overlay.png` | GT 浅灰 + 预测半透明，**共用 GT 坐标系**（看尺寸/错位） |
| `samples/<id>/ops.png` | GT vs 三臂 operation 签名 |
| `selected_cases.json` | 选样规则、分数、每臂指标 |
| `visualization_manifest.json` | 相机、归一化、文件清单 |

## 渲染规范

- 白背景、固定相机：iso `(1.15,-1.35,0.95)` / front `(0,-2,0)` / top `(0,0,2)`
- board：每个 shape 自己平移到 bbox 中心，再按最大 extent 缩到同一视觉尺度
- overlay：用 GT 的中心和 extent，三臂共用，才能看出偏大/偏小
- STEP 不存在或重放失败：灰底 `STEP_FAIL` + failure_reason

## 这套图要回答的两件事

1. M2 到底在哪些样本上真的更好（类别 A + overlay + ops）
2. M2 的稳定性问题具体长什么样（类别 D + length–STEP 散点）
