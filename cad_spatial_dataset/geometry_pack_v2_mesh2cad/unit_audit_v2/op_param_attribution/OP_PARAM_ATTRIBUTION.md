# Fusion360 602：按 CAD operation 参数类型的失败归因

单位合同已修；本报告只诊断 residual label geometry，不改转换器。通过定义与 602 复测相同：Chamfer≤0.01 且 coverage≥0.98。

总体：235/602 = 39.04% 通过。

## 主对照：不要把根因归到圆/矩形 sketch

圆/矩形快捷分支（`Extrude(Circle)` / `Box`）不写 `symmetric` / `height_two`；polygon 分支会写。因此必须拆开 profile × extent。

### 2×2（样本含该类操作，可重叠）

| profile | one-side | two-side / symmetric |
|---|---:|---:|
| circle | 127/286 = 44.4% | 0/34 = 0.0% |
| rectangle | 24/166 = 14.5% | 0/20 = 0.0% |
| polygon（对照） | 110/288 = 38.2% | 12/54 = 22.2% |

### 2×2（同一 profile 的 extent 类型互斥：只有 one-side，或只有 two-side/symm）

| profile | only one-side | only two-side / symmetric |
|---|---:|---:|
| circle | 127/280 = 45.4% | 0/28 = 0.0% |
| rectangle | 24/160 = 15.0% | 0/14 = 0.0% |
| polygon（对照） | 108/268 = 40.3% | 10/34 = 29.4% |

### 2×2（纯样本：转换结果里非 hole body 全是该 profile）

| profile | only one-side | only two-side / symmetric |
|---|---:|---:|
| circle | 98/153 = 64.1% | 0/14 = 0.0% |
| rectangle | 15/75 = 20.0% | 0/9 = 0.0% |
| polygon（对照） | 79/136 = 58.1% | 8/23 = 34.8% |

### DSL 是否真的写出了 extent kwargs

| 集合 | n | DSL 含 symmetric/height_two | 其中通过 | DSL 无 kwargs 且通过 |
|---|---:|---:|---:|---:|
| circle_one_side | 286 | 12 | 3 | 124 |
| circle_two_side_or_symm | 34 | 20 | 0 | 0 |
| rectangle_one_side | 166 | 15 | 0 | 24 |
| rectangle_two_side_or_symm | 20 | 9 | 0 | 0 |
| polygon_one_side | 288 | 22 | 2 | 108 |
| polygon_two_side_or_symm | 54 | 53 | 11 | 1 |

同一 profile 同时含 one-side 与 two-side 的样本：circle 6，rectangle 6。

## P0 其余：extent type / start offset / direction

- 全部 one-side：223/510 = 43.7%
- 含 two-side 或 symmetric：12/92 = 13.0%
- 含负 extent 距离：20/182 = 11.0%
- 全部非负距离：215/420 = 51.2%
- 负 extent_one 且全部 one-side：18/148 = 12.2%
- 负距离且含 two-side：2/33 = 6.1%

源 extent_type 样本通过率：
- `OneSideFeatureExtentType`: 227/552 = 41.1%
- `SymmetricFeatureExtentType`: 9/71 = 12.7%
- `TwoSidesFeatureExtentType`: 3/23 = 13.0%

start_extent 样本通过率：
- `ProfilePlaneStartDefinition`: 235/602 = 39.0%

## P1：revolve / sketch frame / boolean

- timeline 类型计数：{'Sketch': 1375, 'ExtrudeFeature': 1245}
- 含 Revolve：n=0
- timeline 出现 Sketch/Extrude 以外类型：n=0
- sketch origin 非零：43/201 = 21.4%
- sketch origin 全为零：192/401 = 47.9%
- sketch 轴非 canonical：173/456 = 37.9%
- sketch 轴全 canonical：62/146 = 42.5%
- 仅 NewBody：171/344 = 49.7%
- 含 Cut：25/154 = 16.2%
- 含 Join：43/176 = 24.4%
- 被过滤的 Intersect：0/1 = 0.0%
- DSL 无 Cut/Union：91/186 = 48.9%

## P2：circle/rectangle 参数化与局部操作

- 含 circle body：127/314 = 40.4%
- 含 rectangle body：24/180 = 13.3%
- 含 polygon body：120/322 = 37.3%
- 含 hole：101/254 = 39.8%
- fillet/chamfer/pattern timeline：n=0

## 吸烟枪集合拿掉之后还剩什么

圆/矩形非单侧拉伸：53/53 失败。
去掉这 53 条后：通过 235/549，失败 314。
剩余失败上的共存标记（可重叠）：{'negative_extent_distance': 143, 'noncanonical_sketch_frame': 259, 'boolean_cut_join_intersect': 161, 'polygon_profile': 179, 'hole': 124, 'reload_fail': 5, 'unflagged': 14, 'filtered_intersect': 1}

## 结论

- circle one-side 127/280 = 45.4% vs two-side/symm 0/28 = 0.0%
- rectangle one-side 24/160 = 15.0% vs two-side/symm 0/14 = 0.0%
- polygon 对照 one-side 108/268 = 40.3% vs two-side/symm 10/34 = 29.4%
- 模式是否符合“extent converter 而非 sketch converter”：True
- polygon two-side 是否并非全灭（说明 DSL 执行器能处理双侧，问题在圆/矩形快捷分支丢参数）：True

下一步应修 `fusion360_to_dsl.py` 的 circle/rectangle 快捷分支，把 symmetric/height_two 传下去；并让 `cad_dsl.py` 的 Extrude/Box 接受这两类 extent。负距离方向与 polygon 残差是第二优先级，本报告不修代码。

