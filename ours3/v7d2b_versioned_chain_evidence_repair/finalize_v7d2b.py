#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2b_versioned_chain_evidence_repair')
s=json.loads((ROOT/'artifacts/pretest_summary.json').read_text())
s['TAIL_ORIENTATION_BUG_FIXED']=True
s['TAIL_GEOMETRIC_CHAIN_IDENTITY_STILL_AMBIGUOUS']=True
s['NEXT_FIX']='B_FUSELAGE_MIXED_CLOSED_OPEN_SEAM_EVIDENCE_REFORMULATION_AND_C_TAIL_CHAIN_IDENTITY_MATCHING'
s['BLOCKERS']=sorted(set(s.get('BLOCKERS',[])+['TAIL_GEOMETRIC_CHAIN_IDENTITY_STILL_AMBIGUOUS']))
(ROOT/'artifacts/pretest_summary.json').write_text(json.dumps(s,indent=2)+'\n')
report=f'''# V7D2B Versioned Chain Evidence Regeneration and Identity Repair

## Gate decision

`{s['CURRENT_GATE']}`. Evidence persistence and descriptor safety repairs pass, but track recovery does not. No Master Curve, control net, constrained refit, V7C, pcurve, trim, Sewing, Qwen, MAC, or PhysX operation was executed.

## FUSELAGE root cause

All 12 authoritative planes were regenerated from the unchanged measured axis and station planes. S00, S01, and S07 are real closed cycles. S02 and S08-S11 contain exactly one connected simple open component. Only S03-S06 contain at least two trackable open components. Thus the 4/9 seam ceiling is a property of these section observations, not lost serialization, filtering, clustering, or the V7D1 DAG. Four additional components that V7B did not serialize were valid open chains, but all occur inside S03-S06 and do not extend station support. Four tiny open components were retained as rejected evidence rather than silently discarded.

Endpoint clustering showed zero potential over-merges and zero under-merges under the unchanged part-relative tolerance. Every graph now contains node coordinates, source-segment-bound edges, component membership, filters, and rejected geometry.

## VERTICAL_TAIL result

The stale-descriptor bug and dirty/hash guard were repaired: mutating geometry without recomputation is rejected, and reversing with recomputation changes the descriptor hash while keeping geometry/descriptor hashes consistent. Nevertheless, the identical frozen V7D1 tracker still reports two direction flips and two curvature spikes. Therefore stale descriptors were a real defect but not a sufficient cause of the S04/S05 global-path turns; tail geometric branch/chain identity remains ambiguous.

## Required answers

1. FUSELAGE only had two trackable chains at S03-S06 because the other supporting sections physically contain one simple open component; S00/S01/S07 are closed cycles.
2. Offline regeneration recovered the second chain at 0 additional stations.
3. Four previously unpersisted components are valid open chains, all within already-supported S03-S06.
4. No endpoint clustering over-merge or under-merge was detected.
5. FUSELAGE chain identity coverage remains 44.44% (4/9).
6. The tail spikes are not fully caused by the stale descriptor: the defect is reproduced and fixed, but the spikes remain.
7. Both direction reversals do not disappear in the frozen tracker; count remains 2.
8. Canonical chain endpoint identity swaps are 0, but the selected seam path remains invalid.
9. V7D1 DAG weights were not adjusted.
10. Neither part has a valid seam track under the frozen Track Gate.
11. The project is not ready to re-enter Master Curve/control-net/refit.
12. Next choice: FUSELAGE needs a different physical seam evidence formulation for mixed closed/open stations, while the immediate allowed branch is C: continue tail chain identity matching. Do not run V7C.
'''
(ROOT/'artifacts/v7d2b_report.md').write_text(report)
log=ROOT/'logs/tests.log';passed=failed=0
if log.exists():
 text=log.read_text();m=re.search(r'(\d+) passed',text);passed=int(m.group(1)) if m else 0;m=re.search(r'(\d+) failed',text);failed=int(m.group(1)) if m else 0
s['TESTS_PASSED']=passed;s['TESTS_FAILED']=failed
(ROOT/'artifacts/final_summary.json').write_text(json.dumps(s,indent=2)+'\n')
fields=['CURRENT_GATE','EVIDENCE_REPAIR_PASS','TRACK_RECOVERY_READY_FOR_V7D','FUSELAGE_VERSIONED_EVIDENCE_REGENERATED','EVIDENCE_VERSION','RAW_SECTION_GRAPH_FULL_GEOMETRY_PERSISTED','REJECTED_COMPONENT_GEOMETRY_PERSISTED','FUSELAGE_RAW_SECTION_COVERAGE_BEFORE','FUSELAGE_RAW_SECTION_COVERAGE_AFTER','FUSELAGE_OPEN_CHAIN_COVERAGE_BEFORE','FUSELAGE_OPEN_CHAIN_COVERAGE_AFTER','FUSELAGE_STATIONS_WITH_2_TRACKABLE_CHAINS_BEFORE','FUSELAGE_STATIONS_WITH_2_TRACKABLE_CHAINS_AFTER','FUSELAGE_CHAIN_IDENTITY_COVERAGE_BEFORE','FUSELAGE_CHAIN_IDENTITY_COVERAGE_AFTER','FUSELAGE_ENDPOINT_EVIDENCE_COVERAGE_BEFORE','FUSELAGE_ENDPOINT_EVIDENCE_COVERAGE_AFTER','FUSELAGE_VALID_ENDPOINT_TRACK_COUNT','FUSELAGE_TRACK_STATION_COVERAGE','FUSELAGE_MAX_STATION_GAP','FUSELAGE_DIRECTION_FLIP_COUNT','FUSELAGE_CURVATURE_P95','FUSELAGE_CURVATURE_SPIKE_COUNT','VERTICAL_TAIL_STALE_DESCRIPTOR_BUG_FIXED','TAIL_ORIENTATION_BUG_FIXED','TAIL_GEOMETRIC_CHAIN_IDENTITY_STILL_AMBIGUOUS','DESCRIPTOR_DIRTY_GUARD_IMPLEMENTED','STALE_DESCRIPTOR_GUARD_TEST_PASS','DESCRIPTOR_RECOMPUTE_EFFECTIVE','VERTICAL_TAIL_CHAIN_IDENTITY_COVERAGE_BEFORE','VERTICAL_TAIL_CHAIN_IDENTITY_COVERAGE_AFTER','VERTICAL_TAIL_ENDPOINT_EVIDENCE_COVERAGE_BEFORE','VERTICAL_TAIL_ENDPOINT_EVIDENCE_COVERAGE_AFTER','VERTICAL_TAIL_VALID_ENDPOINT_TRACK_COUNT','VERTICAL_TAIL_TRACK_STATION_COVERAGE','VERTICAL_TAIL_DIRECTION_FLIP_COUNT','VERTICAL_TAIL_CURVATURE_P95','VERTICAL_TAIL_CURVATURE_SPIKE_COUNT','ENDPOINT_ID_SWAP_COUNT','CHAIN_GEOMETRY_DESCRIPTOR_HASH_CONSISTENT','EVIDENCE_REGEN_DEPENDENCY_PASS','TAIL_CANONICAL_ORIENTATION_DEPENDENCY_PASS','V7D1_TRACKER_CONFIG_CHANGED','OFFLINE_GEOMETRY_ANALYZER_REGENERATION','RUNTIME_PROFILE_REMEASUREMENT','RUNTIME_BOUNDARY_REDETECTION_FROM_MESH','RUNTIME_CHAIN_REEXTRACTION','PART_ID_HARDCODE_COUNT','GT_USED_AS_INPUT','V7B_SOURCE_ARTIFACTS_UNCHANGED','NEXT_FIX','EVIDENCE_COMPLETENESS_CSV','FUSELAGE_FILTER_AUDIT_CSV','TAIL_ORIENTATION_CSV','REPORT','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
out='\n'.join(f'{k}={s[k]}' for k in fields)+'\n';(ROOT/'artifacts/final_terminal_output.txt').write_text(out);print(out,end='')
