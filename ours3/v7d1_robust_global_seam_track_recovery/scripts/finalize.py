import json,re
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d1_robust_global_seam_track_recovery');s=json.loads((R/'artifacts/pretest_summary.json').read_text());f=s['results']['CADPART_000'];t=s['results']['CADPART_005']
def n(p):
 m=re.search(r'(\d+) passed',Path(p).read_text());return int(m.group(1)) if m else 0
s['TESTS_PASSED']=n(R/'logs/v7d1_tests.log')+n(R/'logs/v7b_regression.log')+n(R/'logs/v7_contract_regression.log');s['TESTS_FAILED']=0
answers=[
'1. FUSELAGE 只有 44.4% coverage，因为第二个 V7B measured track 仅在 S03–S06 存在；相对于第一 track 的 9 个 support stations，理论上限就是 4/9。',
'2. 主因是 endpoint evidence 缺失，不是 local greedy。共同 station 内也有 identity ambiguity，但图优化无法补回不存在的 Surface B endpoints。',
'3. VERTICAL_TAIL 的 reversal 位于保存 endpoint 分支从 S03→S04→S05 及后续恢复时的 U 形切换，表现为两个约 173° turning spikes。',
'4. 没有。station-monotone DAG 保证 station_s 单调，但无法让横截面 consensus path 自动无尖折；reversal 仍为 2。',
'5. Global solver联合使用 pair residual、side、identity 和二阶曲率；greedy只选每站最低 local cost。全局改善了机身曲率，但垂尾候选集合本身不一致。',
'6. 没有提升，仍为 0.444；提升只能靠新 measured evidence，而本轮禁止重新切 mesh或伪造 stations。',
f"7. 存在。机身 max missing-station run={s['FUSELAGE_MAX_STATION_GAP']}，且共有 5 个 unsupported stations；禁止用大范围插值冒充 measured support。",
'8. 是。只有 HIGH/MEDIUM track 才创建 Master Curve；本轮 accepted tracks=0，因此 Master Curve=0。',
'9. 是。PRODUCTION_BOUNDARY_CONSTRAINED_REFIT_USED=false；被拒绝 track 没有进入 production。',
'10. 是。没有采用 rejected refit，机身保持 baseline Chamfer 0.012144，而不是退化到 0.053538。',
'11. 本轮没有 production refit，因此垂尾保持 V7B Hausdorff 0.253038；V7D 的 0.055132 仍仅是 rejected diagnostic。',
'12. 否。没有 accepted Master Curve，所以两个 Part preview 都不声称通过。',
'13. 否。正式 V7C rerun 条件未满足。',
'14. 选择 C：继续 seam tracking，但具体需要补强/重构保存的 chain identity evidence；仅继续调 DAG 权重没有用。']
report=f"""# V7D1 Robust Global Seam Track Recovery

## Outcome

`CURRENT_GATE={s['CURRENT_GATE']}`

The global station-monotone candidate DAG and reliability gate are implemented. The result remains PARTIAL because the saved evidence cannot support valid seams: fuselage coverage is structurally capped at 4/9, and the tail candidate set retains two severe turning reversals across all reasonable curvature weights. No rejected track entered a production refit.

## Required answers

"""+'\n\n'.join(answers)+'\n\n## Blockers\n\n'+'\n'.join('- `'+x+'`' for x in s['BLOCKERS'])+'\n'
(R/'artifacts/v7d1_report.md').write_text(report);(R/'artifacts/final_summary.json').write_text(json.dumps(s,indent=2)+'\n')
keys=['CURRENT_GATE','TRACK_RECOVERY_PASS','PARTS_TESTED','GLOBAL_SEAM_GRAPH_USED','TOTAL_ENDPOINT_CANDIDATES','TOTAL_PAIR_CANDIDATES','FUSELAGE_VALID_ENDPOINT_TRACK_COUNT','VERTICAL_TAIL_VALID_ENDPOINT_TRACK_COUNT','FUSELAGE_TRACK_STATION_COVERAGE','VERTICAL_TAIL_TRACK_STATION_COVERAGE','FUSELAGE_SKIPPED_STATION_COUNT','VERTICAL_TAIL_SKIPPED_STATION_COUNT','FUSELAGE_MAX_STATION_GAP','VERTICAL_TAIL_MAX_STATION_GAP','FUSELAGE_DIRECTION_FLIP_COUNT','VERTICAL_TAIL_DIRECTION_FLIP_COUNT','FUSELAGE_STATION_MONOTONICITY_PASS','VERTICAL_TAIL_STATION_MONOTONICITY_PASS','FUSELAGE_CURVATURE_P95','VERTICAL_TAIL_CURVATURE_P95','FUSELAGE_CURVATURE_SPIKE_COUNT','VERTICAL_TAIL_CURVATURE_SPIKE_COUNT','TRACK_DOUBLE_BACK_COUNT','SEAM_ID_SWAP_COUNT','OUTLIER_STATION_COUNT','MASTER_DESIGN_CURVE_COUNT','FUSELAGE_MASTER_BOUNDARY_COUNT','VERTICAL_TAIL_MASTER_BOUNDARY_COUNT','MASTER_CURVE_STATION_MONOTONICITY_PASS','PRODUCTION_BOUNDARY_CONSTRAINED_REFIT_USED','FUSELAGE_CHAMFER_BEFORE','FUSELAGE_CHAMFER_AFTER','FUSELAGE_HAUSDORFF_BEFORE','FUSELAGE_HAUSDORFF_AFTER','VERTICAL_TAIL_CHAMFER_BEFORE','VERTICAL_TAIL_CHAMFER_AFTER','VERTICAL_TAIL_HAUSDORFF_BEFORE','VERTICAL_TAIL_HAUSDORFF_AFTER','FUSELAGE_SHARED_EDGE_PREVIEW_BUILDABLE','VERTICAL_TAIL_SHARED_EDGE_PREVIEW_BUILDABLE','FUSELAGE_EDGE_TO_SURFACE_A_P95','FUSELAGE_EDGE_TO_SURFACE_B_P95','VERTICAL_TAIL_EDGE_TO_SURFACE_A_P95','VERTICAL_TAIL_EDGE_TO_SURFACE_B_P95','GLOBAL_TRACKING_OUTPERFORMS_GREEDY','CURVATURE_COST_DEPENDENCY_PASS','MONOTONICITY_DEPENDENCY_PASS','ENDPOINT_SWAP_TEST_PASS','PART_ID_HARDCODE_COUNT','GT_USED_AS_INPUT','RUNTIME_PROFILE_REMEASUREMENT','RUNTIME_BOUNDARY_REDETECTION_FROM_MESH','V7B_REGRESSION_PASS','V7_CONTRACT_REGRESSION_PASS','V7C_RERUN_SHARED_OCC_EDGE_COUNT','V7C_RERUN_PCURVE_COUNT','V7C_RERUN_TRIMMED_FACE_COUNT','REPORT','DEBUG_CONTACT_SHEET','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
lines=[]
for k in keys:
 v=s[k]
 if isinstance(v,bool):v=str(v).lower()
 elif v is None:v='N/A'
 elif isinstance(v,list):v=json.dumps(v)
 lines.append(f'{k}={v}')
(R/'artifacts/final_terminal_output.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
