# Curve Samples Recovery and Native Bridge

当前门禁：`CHAMFER_NATIVE_POINT_CLOUD_SCHEMA_BLOCKED`。

历史 STEP -> curve_samples.npz -> Frozen C2 -> [K,256] 链路已恢复。CANARY4 四例均通过，输出为有限的 float32 `[48,256]`，且使用历史 sharp-only edge 规则和原始 exporter。Dataset `__getitem__` 也通过。

原生 P1 collator 尚未通过：Synthetic64 的 `surface_points.npy` 实际为 `[128,3]`，而 native `SpatialLMPlugin._load_cad_separate_edge` 要求 `[N,6]` 的 xyz+normal。由于法向缺失，本轮不补零、不复制坐标、不改 loader，也不宣称 native forward/runtime PASS。

因此 FULL64 未执行，未启动训练，未修改 canonical P1、C2、tokenizer、CurveProjector、EXACT9998 registry 或 Synthetic64 gt.step/gt.dsl。下一阶段只能在隔离目录提供真实的 native `[N,6]` surface asset 后重跑 CANARY4 collator。
