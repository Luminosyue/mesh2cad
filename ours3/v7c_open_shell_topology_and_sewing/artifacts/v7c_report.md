# V7C Open-Shell Topology and Sewing Report

## Outcome

`CURRENT_GATE=V7C_OPEN_SHELL_TOPOLOGY_AND_SEWING_PARTIAL`

The implementation is complete as a strict topology pipeline, but CASE09 is not a valid V7C shell result. The existing V7B surface pair does not contain sufficiently coincident design boundaries: 0/4 expected shared boundaries passed the geometry, endpoint, length, tangent, semantic, station-overlap, and adjacency gates. Surface-surface intersection found no usable design-length intersection. Consequently the run correctly stopped before shared-edge creation, pcurve creation, wire construction, trimming, and sewing.

## Key evidence

- Boundary candidates: 16 genuine BRep face boundaries; profile-sample-derived edges: 0.
- Fuselage: topological free edges 8 before / 8 after; result FACE_SET; Chamfer 0.0121443851; Hausdorff 0.196381659.
- Vertical tail: topological free edges 8 before / 8 after; result FACE_SET; Chamfer 0.0102987825; Hausdorff 0.253037655.
- Fuselage surface intersection: 0 curves. Vertical-tail intersection: 3 raw curves, maximum raw length 0.0132381644, all below the design-length threshold.
- Reconciled candidate curve-to-second-surface p95: fuselage 0.384530528; vertical tail 0.174436543; neither is a valid shared edge.
- No large-tolerance or forced sewing, no fake edge, no untrimmed fallback.
- Diagnostic counterfactual plumbing is effective: candidate-edge perturbation, natural-pcurve perturbation, and boundary-match swap all change their diagnostic outputs; invalid topology is rejected. Formal shared-edge/pcurve EFFECTIVE fields remain false because no accepted topology consumed them.
- Tests: 111 passed, 0 failed (37 V7C + 23 V7B + 16 V7A + 35 V7 contract).

## Required answers

1. V7B 只有 FACE_SET，因为两张面是独立创建的自然有界 B-spline face；每个面有独立 wire/edges，边 incidence 全为 1，没有共享 OCC topology。

2. 本轮没有任何一对边界通过 design-boundary 联合证据门槛。因此共享边界仍为 UNRESOLVED；不能把 nearest pair 当设计边。

3. 否。正式 V7C 没有创建 shared TopoDS_Edge，因为输入证据不足。

4. 否。两个 Face 仍各自引用独立 V7B 边；报告没有把几何近似边伪装成同一 underlying Edge。

5. 否。没有合法 shared edge，所以没有创建或宣称双面 pcurve。旧自然边各自已有 pcurve，只属于各自 Face。

6. 正式 shared-edge pcurve 误差为 N/A。boundary reconciliation 诊断候选在第二曲面上的 p95 误差分别为 0.384530528 和 0.174436543，均远超阈值。

7. 否。正式 V7C wire 未构造；缺失已接受 shared boundaries 时严格拒绝，不自动补 fake edge。

8. 否。trimmed Face 未创建；UNTRIMMED_FACE_FALLBACK_COUNT=0，因此没有静默退回旧面并声称 V7C success。

9. Sewing 未运行，因 trim 前置条件不成立；LARGE_TOLERANCE_SEWING_REQUIRED=false，FORCED_SEWING_COUNT=0。

10. FUSELAGE=FACE_SET；VERTICAL_TAIL=FACE_SET；均非 Shell/Solid。

11. 垂尾最坏 Hausdorff 点定位到 SIDE 区域，normalized distance=0.253037655，nearest boundary=CADPART_005_FACE_00_BND_03。

12. 尚未降低。duplicate coincident edges 当前为 0；两部件 free edges 仍各为 8；artificial-edge ratio 保持 V7B 原始值 0。

13. 否；PROFILE_SAMPLE_DERIVED_EDGE_COUNT=0。拓扑候选只来自 BREP_FACE_BOUNDARY。

14. Step 6 Semantic Wireframe Graph 应标为 🟡：数据结构与真实 BRep 边界图已实现，但共享语义边仍 unresolved。

15. Step 7 Global Intersection Topology Builder 应标为 🟡：intersection、matching、edge/pcurve/wire/trim/sew 模块与门禁已实现，但本输入没有形成可接受全局拓扑。

16. 下一步选 A：修局部 boundary / trim。需要先让两曲面在预期 design boundaries 上共享一致几何（或重做受约束曲面边界），再继续 sewing。

## Blockers

- `FUSELAGE_DESIGN_BOUNDARY_UNRESOLVED`
- `VERTICAL_TAIL_DESIGN_BOUNDARY_UNRESOLVED`
