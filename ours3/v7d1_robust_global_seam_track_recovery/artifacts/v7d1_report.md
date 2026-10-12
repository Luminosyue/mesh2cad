# V7D1 Robust Global Seam Track Recovery

## Outcome

`CURRENT_GATE=V7D1_ROBUST_GLOBAL_SEAM_TRACK_RECOVERY_PARTIAL`

The global station-monotone candidate DAG and reliability gate are implemented. The result remains PARTIAL because the saved evidence cannot support valid seams: fuselage coverage is structurally capped at 4/9, and the tail candidate set retains two severe turning reversals across all reasonable curvature weights. No rejected track entered a production refit.

## Required answers

1. FUSELAGE 只有 44.4% coverage，因为第二个 V7B measured track 仅在 S03–S06 存在；相对于第一 track 的 9 个 support stations，理论上限就是 4/9。

2. 主因是 endpoint evidence 缺失，不是 local greedy。共同 station 内也有 identity ambiguity，但图优化无法补回不存在的 Surface B endpoints。

3. VERTICAL_TAIL 的 reversal 位于保存 endpoint 分支从 S03→S04→S05 及后续恢复时的 U 形切换，表现为两个约 173° turning spikes。

4. 没有。station-monotone DAG 保证 station_s 单调，但无法让横截面 consensus path 自动无尖折；reversal 仍为 2。

5. Global solver联合使用 pair residual、side、identity 和二阶曲率；greedy只选每站最低 local cost。全局改善了机身曲率，但垂尾候选集合本身不一致。

6. 没有提升，仍为 0.444；提升只能靠新 measured evidence，而本轮禁止重新切 mesh或伪造 stations。

7. 存在。机身 max missing-station run=4，且共有 5 个 unsupported stations；禁止用大范围插值冒充 measured support。

8. 是。只有 HIGH/MEDIUM track 才创建 Master Curve；本轮 accepted tracks=0，因此 Master Curve=0。

9. 是。PRODUCTION_BOUNDARY_CONSTRAINED_REFIT_USED=false；被拒绝 track 没有进入 production。

10. 是。没有采用 rejected refit，机身保持 baseline Chamfer 0.012144，而不是退化到 0.053538。

11. 本轮没有 production refit，因此垂尾保持 V7B Hausdorff 0.253038；V7D 的 0.055132 仍仅是 rejected diagnostic。

12. 否。没有 accepted Master Curve，所以两个 Part preview 都不声称通过。

13. 否。正式 V7C rerun 条件未满足。

14. 选择 C：继续 seam tracking，但具体需要补强/重构保存的 chain identity evidence；仅继续调 DAG 权重没有用。

## Blockers

- `FUSELAGE_INSUFFICIENT_MEASURED_STATION_COVERAGE`
- `VERTICAL_TAIL_GLOBAL_TRACK_RELIABILITY_REJECTED`
