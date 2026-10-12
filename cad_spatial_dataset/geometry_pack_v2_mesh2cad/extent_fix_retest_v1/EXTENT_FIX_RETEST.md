# Fusion360 extent converter 复测

只修圆/矩形快捷分支的 `symmetric` / `height_two`，以及负距离符号。阈值仍是 Chamfer≤0.01 且 coverage≥0.98。未改 V2-100、训练或 split。对照 20 条此前已通过、且不在本子集内的样本全部仍通过。

| 集合 | n | 修前通过 | 修后通过 | 新通过 | 回退 |
|---|---:|---:|---:|---:|---:|
| 圆/矩形非单侧（原 53/53 全灭） | 53 | 0 | **14** | 14 | 0 |
| 其中仅 circle 非单侧 | 33 | 0 | 11 | 11 | 0 |
| 其中仅 rectangle 非单侧 | 19 | 0 | 3 | 3 | 0 |
| 负 extent 距离 | 182 | 20 | **65** | 46 | 1 |
| 两集合并集 | 216 | 20 | **78** | 59 | 1 |
| 此前已通过对照 | 20 | 20 | 20 | 0 | 0 |

中位数（可测几何）：

- 圆/矩形非单侧：Chamfer 0.044 → 0.016，coverage 0.52 → 0.87
- 负距离：Chamfer 0.031 → 0.0095，coverage 0.63 → 0.91

DSL 已写出 extent：例如 `fusion360__21865_c190b734_0000` 现为 `Extrude(..., height=60, ..., symmetric=True)`，但该条仍未过门禁（coverage 仍为 0）。说明 extent kwargs 已接到，剩余误差在 circle 中心/sketch 定位，不是没传 symmetric。

回退 1 条：`fusion360__41234_74275eb0_0001`。修前 Chamfer 0.0097 / coverage 0.995；修后执行 `Standard_OutOfRange('NCollection_Sequence::ChangeValue')`。源有负距离 -8.89/-13.97，现 DSL 保留负高度后 CadQuery 挤出崩溃。不回滚符号修复，记为执行器边界。

53 条里仍失败 39：circle 23、rectangle 17（可重叠），其中 18 条同时有负距离。下一步是 P2 矩形 Box 定位和 circle 中心，而不是再改 extent 开关。
