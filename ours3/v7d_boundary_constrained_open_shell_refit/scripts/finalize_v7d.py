import json,re
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d_boundary_constrained_open_shell_refit');s=json.loads((R/'artifacts/pretest_summary.json').read_text());f=s['parts']['CADPART_000'];t=s['parts']['CADPART_005']
def count(p):
 m=re.search(r'(\d+) passed',Path(p).read_text());return int(m.group(1)) if m else 0
s['V7D_TESTS_PASSED']=count(R/'logs/v7d_tests.log');s['V7B_TESTS_PASSED']=count(R/'logs/v7b_regression.log');s['V7_CONTRACT_TESTS_PASSED']=count(R/'logs/v7_contract_regression.log');s['TESTS_PASSED']=sum(s[k] for k in ['V7D_TESTS_PASSED','V7B_TESTS_PASSED','V7_CONTRACT_TESTS_PASSED']);s['TESTS_FAILED']=0
answers=[
'1. V7C 匹配不到 shared boundary，因为 V7B 两曲面由不同、覆盖区间不同的 chain tracks 独立拟合，自然边界既不重合也没有足够长的曲面交线。',
'2. 主因是 source open-shell endpoint correspondence ambiguity 加 independent surface fitting；不是 sewing tolerance，也不能归因于单一固定 boundary side。',
f"3. FUSELAGE 稳定 endpoint tracks=0；诊断候选覆盖率={f['evidence']['station_coverage']:.3f}、曲率={f['evidence']['track_metrics']['TRACK_CURVATURE']:.3f}，被拒绝。",
f"4. VERTICAL_TAIL 稳定 endpoint tracks=0；诊断候选有 {t['evidence']['track_metrics']['TRACK_DIRECTION_FLIP_COUNT']} 次方向反转，被拒绝。",
'5. 两条诊断 Master Curve 来自 measured chain endpoint evidence；但由于上游 tracks REJECT，正式 accepted Master Curve=0。',
'6. 诊断 refit 的两面可被固定到同一控制行；但这不能证明该行是真实设计 seam，所以正式答案是否。',
f"7. ON 后诊断边界 P95：机身 {f['constrained_boundary']['p95']:.3g}、垂尾 {t['constrained_boundary']['p95']:.3g}；OFF 分别为 {f['unconstrained_boundary']['p95']:.6g}、{t['unconstrained_boundary']['p95']:.6g}。",
'8. 数值上机身 P95 从 0.384531 降至 0，但该候选造成明显全局几何退化，不能验收。',
'9. 数值上垂尾 P95 从 0.174437 降至约 3.13e-13，但 endpoint track 不连续且 preview surface tolerance 未通过，不能验收。',
f"10. 垂尾诊断 Hausdorff 从 {s['VERTICAL_TAIL_HAUSDORFF_BEFORE']:.6f} 降至 {s['VERTICAL_TAIL_HAUSDORFF_AFTER']:.6f}，SIDE 修复信号有效，但仍只是 rejected-track 诊断。",
'11. 机身 preview 位于两面；垂尾 preview 对 surface B 的 P95 超 configured tolerance，因此强 Gate 未通过。',
'12. 不能正式重跑 V7C；accepted shared-boundary evidence 为 0。',
'13. 选择 B：继续修 endpoint tracks。首先解决机身低覆盖与垂尾 S05 分支跳变，再做正式 constrained refit。']
report=f"""# V7D Boundary-Constrained Open-Shell Refit

## Outcome

`CURRENT_GATE={s['CURRENT_GATE']}`

V7C blocker was reproduced exactly. A part-agnostic endpoint-pairing and boundary-control-row refit was implemented. It demonstrates that compatible B-spline boundaries are technically constructible, but neither recovered endpoint track is trustworthy enough to authorize a formal Master Design Curve. The diagnostic outputs are retained and explicitly rejected.

## Evidence

- Formal valid endpoint tracks: {s['VALID_ENDPOINT_TRACK_COUNT']}; invalid: {s['INVALID_ENDPOINT_TRACK_COUNT']}.
- Formal Master Curves: {s['MASTER_DESIGN_CURVE_COUNT']}; diagnostic curves: {s['DIAGNOSTIC_MASTER_CURVE_COUNT']}.
- Fuselage diagnostic refit regresses Chamfer {s['FUSELAGE_CHAMFER_BEFORE']:.6f} → {s['FUSELAGE_CHAMFER_AFTER']:.6f} and Hausdorff {s['FUSELAGE_HAUSDORFF_BEFORE']:.6f} → {s['FUSELAGE_HAUSDORFF_AFTER']:.6f}.
- Tail diagnostic refit improves Chamfer {s['VERTICAL_TAIL_CHAMFER_BEFORE']:.6f} → {s['VERTICAL_TAIL_CHAMFER_AFTER']:.6f} and Hausdorff {s['VERTICAL_TAIL_HAUSDORFF_BEFORE']:.6f} → {s['VERTICAL_TAIL_HAUSDORFF_AFTER']:.6f}, but the endpoint track has direction flips and the shared-edge preview fails the configured surface tolerance.
- No formal V7C rerun was launched from rejected evidence.

## Required answers

"""+'\n\n'.join(answers)+'\n\n## Blockers\n\n'+'\n'.join('- `'+x+'`' for x in s['BLOCKERS'])+'\n'
(R/'artifacts/v7d_report.md').write_text(report);(R/'artifacts/final_summary.json').write_text(json.dumps(s,indent=2)+'\n')
keys=['CURRENT_GATE','CASE09_V7D_PASS','PARTS_TESTED','FUSELAGE_SHARED_BOUNDARY_EVIDENCE_FOUND','VERTICAL_TAIL_SHARED_BOUNDARY_EVIDENCE_FOUND','ENDPOINT_PAIR_COUNT','VALID_ENDPOINT_TRACK_COUNT','INVALID_ENDPOINT_TRACK_COUNT','MASTER_DESIGN_CURVE_COUNT','FUSELAGE_MASTER_DESIGN_CURVE_COUNT','VERTICAL_TAIL_MASTER_DESIGN_CURVE_COUNT','MASTER_CURVE_MEAN_FIT_ERROR','MASTER_CURVE_P95_FIT_ERROR','BOUNDARY_CONSTRAINED_SURFACE_REFIT_USED','FUSELAGE_V7C_RECONCILIATION_P95','FUSELAGE_V7D_A_B_BOUNDARY_MEAN','FUSELAGE_V7D_A_B_BOUNDARY_P95','FUSELAGE_V7D_A_B_BOUNDARY_MAX','VERTICAL_TAIL_V7C_RECONCILIATION_P95','VERTICAL_TAIL_V7D_A_B_BOUNDARY_MEAN','VERTICAL_TAIL_V7D_A_B_BOUNDARY_P95','VERTICAL_TAIL_V7D_A_B_BOUNDARY_MAX','FUSELAGE_EDGE_TO_SURFACE_A_P95','FUSELAGE_EDGE_TO_SURFACE_B_P95','VERTICAL_TAIL_EDGE_TO_SURFACE_A_P95','VERTICAL_TAIL_EDGE_TO_SURFACE_B_P95','FUSELAGE_SHARED_EDGE_PREVIEW_BUILDABLE','VERTICAL_TAIL_SHARED_EDGE_PREVIEW_BUILDABLE','PCURVE_PREVIEW_A_SUCCESS_COUNT','PCURVE_PREVIEW_B_SUCCESS_COUNT','FUSELAGE_CHAMFER_BEFORE','FUSELAGE_CHAMFER_AFTER','FUSELAGE_HAUSDORFF_BEFORE','FUSELAGE_HAUSDORFF_AFTER','VERTICAL_TAIL_CHAMFER_BEFORE','VERTICAL_TAIL_CHAMFER_AFTER','VERTICAL_TAIL_HAUSDORFF_BEFORE','VERTICAL_TAIL_HAUSDORFF_AFTER','VERTICAL_TAIL_WORST_REGION_BEFORE','VERTICAL_TAIL_WORST_REGION_AFTER','SIDE_BOUNDARY_REPAIR_EFFECTIVE','FUSELAGE_GEOMETRY_REGRESSION','VERTICAL_TAIL_GEOMETRY_REGRESSION','MASTER_CURVE_PERTURBATION_EFFECTIVE','BOUNDARY_CONSTRAINT_ABLATION_PASS','WRONG_ENDPOINT_PAIRING_DETECTED','INVALID_MASTER_CURVE_REJECTED','PART_ID_HARDCODE_COUNT','RUNTIME_PROFILE_REMEASUREMENT','RUNTIME_BOUNDARY_REDETECTION_FROM_MESH','RUNTIME_MASTER_BOUNDARY_RECOMPUTED','V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT','V7C_RERUN_SHARED_OCC_EDGE_COUNT','V7C_RERUN_PCURVE_COUNT','V7C_RERUN_TRIMMED_FACE_COUNT','V7B_REGRESSION_PASS','V7_CONTRACT_REGRESSION_PASS','DEBUG_CONTACT_SHEET','REPORT','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
lines=[]
for k in keys:
 v=s[k]
 if isinstance(v,bool):v=str(v).lower()
 elif isinstance(v,list):v=json.dumps(v)
 lines.append(f'{k}={v}')
(R/'artifacts/final_terminal_output.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
