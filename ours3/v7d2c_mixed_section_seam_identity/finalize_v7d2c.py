#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2c_mixed_section_seam_identity');s=json.loads((ROOT/'artifacts/pretest_summary.json').read_text())
report=f'''# V7D2C Mixed-Section Seam and Tail Chain Identity Recovery

## Gate

`{s['CURRENT_GATE']}`. FUSELAGE mixed-section recovery passes, but the Tail seam Track Gate remains partial. Production Master Curve count is zero; Common Control Net, refit, and V7C were not executed.

## Required answers

1. The old 44.4% was not an extraction bug. It was the representation assumption `two open chains per station`; measured FUSELAGE sections legitimately transition among closed loop, single open chain, and multi-open chain.
2. A closed loop contributes latent seam candidates sampled by normalized arc length. Selection is anchor-first and jointly optimized in the station-local frame.
3. No latent point leaves the measured loop; every selected XYZ is one of its measured arc-length samples.
4. A single open chain contributes its two real endpoints to SEAM_A and SEAM_B; it is never duplicated into two chains.
5. S03-S06 are the multi-open high-confidence anchor stations.
6. Both FUSELAGE seam evidence coverages rise from 44.4% to 100%; observed-only support is 75% and latent support is 25%.
7. Two continuous FUSELAGE diagnostic seam tracks are recovered with zero direction flips. They are evidence tracks, not production Master Curves.
8. The old Tail tracker selected locally compatible endpoint pairs before resolving whole-chain branch identity, allowing the chosen point trajectory to reverse near S04/S05.
9. Whole-chain matching selects the persistent longitudinal TRACK_0 branch. It removes one of two old flips/spikes, but S04/S05-derived geometry still has a large turn.
10. Tail flips reduce from 2 to 1, not zero.
11. Curvature spikes reduce from 2 to 1 and P95 from 3.0257 to 1.4518 rad, but remain above Gate.
12. V7D1 DAG weights do not need and were not adjusted.
13. The project is not yet ready for Master Boundary/Common Control Net because the Tail valid seam track count is zero.
14. Next allowed choice is C: continue Tail whole-chain-derived seam identity. Do not run V7C.
'''
(ROOT/'artifacts/v7d2c_report.md').write_text(report)
log=ROOT/'logs/tests.log';passed=failed=0
if log.exists():
 t=log.read_text();m=re.search(r'(\d+) passed',t);passed=int(m.group(1)) if m else 0;m=re.search(r'(\d+) failed',t);failed=int(m.group(1)) if m else 0
s['TESTS_PASSED']=passed;s['TESTS_FAILED']=failed
(ROOT/'artifacts/final_summary.json').write_text(json.dumps(s,indent=2)+'\n')
fields=['CURRENT_GATE','TRACK_RECOVERY_READY_FOR_V7D','FUSELAGE_MIXED_SECTION_MODEL_USED','FUSELAGE_CLOSED_LOOP_STATION_COUNT','FUSELAGE_SINGLE_OPEN_STATION_COUNT','FUSELAGE_MULTI_OPEN_STATION_COUNT','CLOSED_LOOP_LATENT_SEAM_USED','SINGLE_OPEN_ENDPOINT_EVIDENCE_USED','MULTI_OPEN_ANCHOR_EVIDENCE_USED','FUSELAGE_VALID_SEAM_TRACK_COUNT','FUSELAGE_SEAM_A_EVIDENCE_COVERAGE','FUSELAGE_SEAM_B_EVIDENCE_COVERAGE','FUSELAGE_OBSERVED_ONLY_COVERAGE','FUSELAGE_LATENT_SUPPORTED_COVERAGE','FUSELAGE_TRACK_STATION_COVERAGE','FUSELAGE_DIRECTION_FLIP_COUNT','FUSELAGE_CURVATURE_P95','FUSELAGE_LATENT_IDENTITY_JUMP_COUNT','VERTICAL_TAIL_WHOLE_CHAIN_IDENTITY_USED','VERTICAL_TAIL_VALID_CHAIN_TRACK_COUNT','VERTICAL_TAIL_VALID_SEAM_TRACK_COUNT','VERTICAL_TAIL_DIRECTION_FLIP_COUNT','VERTICAL_TAIL_CURVATURE_P95','VERTICAL_TAIL_CURVATURE_SPIKE_COUNT','VERTICAL_TAIL_STATION_MONOTONICITY_PASS','VERTICAL_TAIL_AMBIGUOUS_MATCH_COUNT','WHOLE_CHAIN_IDENTITY_OUTPERFORMS_ENDPOINT_TRACKING','SECOND_ORDER_TRAJECTORY_DEPENDENCY_PASS','SIDE_EVIDENCE_DEPENDENCY_PASS','V7B_SURFACE_PRIOR_USED','MIXED_SECTION_EVIDENCE_DEPENDENCY_PASS','PRODUCTION_MASTER_CURVE_COUNT','GT_USED_AS_INPUT','FINAL_GEOMETRY_METRIC_USED_FOR_TRACK_SELECTION','PART_ID_HARDCODE_COUNT','V7D1_TRACKER_WEIGHTS_CHANGED','REPORT','FUSELAGE_SEAM_CSV','TAIL_IDENTITY_CSV','DEBUG_CONTACT_SHEET','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
out='\n'.join(f'{k}={s[k]}' for k in fields)+'\n';(ROOT/'artifacts/final_terminal_output.txt').write_text(out);print(out,end='')
