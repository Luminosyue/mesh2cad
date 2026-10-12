# V7D Boundary-Constrained Open-Shell Refit

## Outcome

`CURRENT_GATE=V7D_BOUNDARY_CONSTRAINED_OPEN_SHELL_REFIT_PARTIAL`

V7C blocker was reproduced exactly. A part-agnostic endpoint-pairing and boundary-control-row refit was implemented. It demonstrates that compatible B-spline boundaries are technically constructible, but neither recovered endpoint track is trustworthy enough to authorize a formal Master Design Curve. The diagnostic outputs are retained and explicitly rejected.

## Evidence

- Formal valid endpoint tracks: 0; invalid: 2.
- Formal Master Curves: 0; diagnostic curves: 2.
- Fuselage diagnostic refit regresses Chamfer 0.012144 → 0.053538 and Hausdorff 0.196382 → 0.443664.
- Tail diagnostic refit improves Chamfer 0.010299 → 0.008376 and Hausdorff 0.253038 → 0.055132, but the endpoint track has direction flips and the shared-edge preview fails the configured surface tolerance.
- No formal V7C rerun was launched from rejected evidence.

## Required answers

1. V7C 匹配不到 shared boundary，因为 V7B 两曲面由不同、覆盖区间不同的 chain tracks 独立拟合，自然边界既不重合也没有足够长的曲面交线。

2. 主因是 source open-shell endpoint correspondence ambiguity 加 independent surface fitting；不是 sewing tolerance，也不能归因于单一固定 boundary side。

3. FUSELAGE 稳定 endpoint tracks=0；诊断候选覆盖率=0.444、曲率=1.233，被拒绝。

4. VERTICAL_TAIL 稳定 endpoint tracks=0；诊断候选有 2 次方向反转，被拒绝。

5. 两条诊断 Master Curve 来自 measured chain endpoint evidence；但由于上游 tracks REJECT，正式 accepted Master Curve=0。

6. 诊断 refit 的两面可被固定到同一控制行；但这不能证明该行是真实设计 seam，所以正式答案是否。

7. ON 后诊断边界 P95：机身 0、垂尾 3.13e-13；OFF 分别为 0.0617444、0.0581086。

8. 数值上机身 P95 从 0.384531 降至 0，但该候选造成明显全局几何退化，不能验收。

9. 数值上垂尾 P95 从 0.174437 降至约 3.13e-13，但 endpoint track 不连续且 preview surface tolerance 未通过，不能验收。

10. 垂尾诊断 Hausdorff 从 0.253038 降至 0.055132，SIDE 修复信号有效，但仍只是 rejected-track 诊断。

11. 机身 preview 位于两面；垂尾 preview 对 surface B 的 P95 超 configured tolerance，因此强 Gate 未通过。

12. 不能正式重跑 V7C；accepted shared-boundary evidence 为 0。

13. 选择 B：继续修 endpoint tracks。首先解决机身低覆盖与垂尾 S05 分支跳变，再做正式 constrained refit。

## Blockers

- `FUSELAGE_ENDPOINT_TRACK_REJECTED`
- `FUSELAGE_GEOMETRY_REGRESSION`
- `VERTICAL_TAIL_ENDPOINT_TRACK_REJECTED`
- `VERTICAL_TAIL_PREVIEW`
