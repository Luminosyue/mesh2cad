#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2d_vertical_tail_seam_endpoint_identity');s=json.loads((ROOT/'artifacts/pretest_summary.json').read_text())
report=f'''# V7D2D Vertical-Tail Seam Endpoint Identity Disambiguation

## Gate

`{s['CURRENT_GATE']}`. FUSELAGE and the accepted Tail whole-chain track remained byte-for-byte frozen. Endpoint-side identity was separated from endpoint array index and solved jointly for two seams, but the physical endpoint samples on the frozen chain cannot satisfy the zero-flip/zero-spike Gate.

## Required answers

1. V7D2C retained one flip because a valid whole-chain identity does not guarantee that either boundary endpoint trajectory is smooth; S05-S07-S08 bends sharply on the measured TRACK_0 endpoints.
2. The old remaining spike is centered at S07, between S05 and S08.
3. It is not caused solely by selecting endpoint_0 versus endpoint_1 incorrectly. Exhaustive audit of all 2^8 joint FORWARD/SWAP sequences found minimum combined flips=1 and spikes=3 for the two seams; no zero/zero sequence exists.
4. Endpoint array indices and physical SIDE_A/SIDE_B are decoupled by joint state assignments.
5. Physical side identity remains stable through orientation changes; synthetic array swapping preserves the physical seam.
6. Global DP prevents local state chatter and is no worse than greedy, but cannot remove geometry inherent in the frozen chain endpoints.
7. Combined two-seam flips do not reach zero; they remain 1.
8. Combined spikes do not reach zero; the selected two physical boundaries contain 3 total spikes.
9. Maximum P95 remains 1.4518209642 rad, so it does not significantly improve.
10. TAIL_SEAM_A is not valid under the strict Gate.
11. TAIL_SEAM_B is also not valid under the strict Gate.
12. The two seam assignments always use distinct endpoints at each station.
13. Synthetic endpoint array swapping does not alter physical seam identity.
14. No Chamfer or Hausdorff metric was used.
15. FUSELAGE stayed frozen with two 100% seams.
16. TRACK_RECOVERY_READY_FOR_V7D remains false.
17. V7D/V7C must not run.
18. Remaining class is B: CHAIN_GEOMETRY_AMBIGUOUS. With the accepted chain frozen, endpoint identity alone cannot satisfy the requested topology; the next task must revisit the physical whole-chain branch or seam topology rather than tune endpoint weights.
'''
(ROOT/'artifacts/v7d2d_report.md').write_text(report)
log=ROOT/'logs/tests.log';passed=failed=0
if log.exists():
 t=log.read_text();m=re.search(r'(\d+) passed',t);passed=int(m.group(1)) if m else 0;m=re.search(r'(\d+) failed',t);failed=int(m.group(1)) if m else 0
s['TESTS_PASSED']=passed;s['TESTS_FAILED']=failed;(ROOT/'artifacts/final_summary.json').write_text(json.dumps(s,indent=2)+'\n')
fields=['CURRENT_GATE','TRACK_RECOVERY_READY_FOR_V7D','FUSELAGE_FROZEN','FUSELAGE_VALID_SEAM_TRACK_COUNT','FUSELAGE_SEAM_A_EVIDENCE_COVERAGE','FUSELAGE_SEAM_B_EVIDENCE_COVERAGE','FUSELAGE_DIRECTION_FLIP_COUNT','TAIL_WHOLE_CHAIN_TRACK_UNCHANGED','TAIL_CHAIN_TRACK_HASH_BEFORE','TAIL_CHAIN_TRACK_HASH_AFTER','VERTICAL_TAIL_ENDPOINT_SIDE_IDENTITY_USED','GLOBAL_ENDPOINT_SIDE_SOLVER_USED','VERTICAL_TAIL_VALID_CHAIN_TRACK_COUNT','VERTICAL_TAIL_VALID_SEAM_TRACK_COUNT','VERTICAL_TAIL_SEAM_A_VALID','VERTICAL_TAIL_SEAM_B_VALID','VERTICAL_TAIL_DIRECTION_FLIP_COUNT_BEFORE','VERTICAL_TAIL_DIRECTION_FLIP_COUNT_AFTER','VERTICAL_TAIL_CURVATURE_P95_BEFORE','VERTICAL_TAIL_CURVATURE_P95_AFTER','VERTICAL_TAIL_CURVATURE_SPIKE_COUNT_BEFORE','VERTICAL_TAIL_CURVATURE_SPIKE_COUNT_AFTER','VERTICAL_TAIL_ENDPOINT_SIDE_SWITCH_COUNT','VERTICAL_TAIL_STATION_MONOTONICITY_PASS','SPIKE_STATION_ID','OLD_SPIKE_TURNING_ANGLE','NEW_SPIKE_TURNING_ANGLE','OLD_SPIKE_SELECTED_ENDPOINT','NEW_SPIKE_SELECTED_ENDPOINT','ENDPOINT_SIDE_IDENTITY_OUTPERFORMS_ENDPOINT_INDEX','SIGNED_SIDE_DEPENDENCY_PASS','SEAM_SECOND_ORDER_DEPENDENCY_PASS','GLOBAL_ENDPOINT_SIDE_SOLVER_OUTPERFORMS_GREEDY','ENDPOINT_ARRAY_SWAP_INVARIANCE_PASS','TRUE_SIDE_CROSSING_DETECTED','TAIL_REMAINING_SPIKE_CAUSE','TAIL_REMAINING_AMBIGUITY_CLASS','PRODUCTION_MASTER_CURVE_COUNT','GT_USED_AS_INPUT','FINAL_GEOMETRY_METRIC_USED_FOR_TRACK_SELECTION','PART_ID_HARDCODE_COUNT','V7D1_TRACKER_WEIGHTS_CHANGED','V7D2C_WHOLE_CHAIN_WEIGHTS_CHANGED','TAIL_ENDPOINT_IDENTITY_CSV','TAIL_SPIKE_DIAGNOSIS_CSV','DEBUG_CONTACT_SHEET','REPORT','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
out='\n'.join(f'{k}={s[k]}' for k in fields)+'\n';(ROOT/'artifacts/final_terminal_output.txt').write_text(out);print(out,end='')
