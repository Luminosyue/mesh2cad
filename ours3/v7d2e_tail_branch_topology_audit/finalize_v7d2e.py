#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'v7d2e_tail_branch_topology_audit'
p=OUT/'artifacts/pretest_summary.json'; d=json.load(open(p))
log=(OUT/'logs/tests.log').read_text()
import re
m=re.search(r'(\d+) passed',log); f=re.search(r'(\d+) failed',log)
d['TESTS_PASSED']=int(m.group(1)) if m else 0
d['TESTS_FAILED']=int(f.group(1)) if f else 0
if d['TESTS_FAILED'] or not d['TESTS_PASSED']:
 d['CURRENT_GATE']='V7D2E_VERTICAL_TAIL_BRANCH_TOPOLOGY_AND_ADAPTIVE_STATION_AUDIT_FAIL'
 d['BLOCKERS']=sorted(set(d.get('BLOCKERS',[])+['TEST_FAILURE']))
(OUT/'artifacts/final_summary.json').write_text(json.dumps(d,indent=2)+'\n')
fields=['CURRENT_GATE','TAIL_S07_ROOT_CAUSE_IDENTIFIED','TAIL_S07_ROOT_CAUSE','S06_RAW_SECTION_AVAILABLE','S06_VALID_CHAIN_AVAILABLE','S06_CURRENTLY_SKIPPED_REASON','TAIL_LOCAL_BRANCH_GRAPH_USED','TAIL_CURRENT_BRANCH_RANK','TAIL_ALTERNATIVE_BRANCH_COUNT','SMOOTHER_BUT_WEAKER_BRANCH_REJECTED','OFFLINE_ADAPTIVE_EVIDENCE_REGEN','ADAPTIVE_STATION_COUNT','ADAPTIVE_VALID_CHAIN_COUNT','WORLD_SPACE_SPIKE_PRESENT','LOCAL_SPACE_SPIKE_PRESENT','LOCAL_FRAME_FLIP_COUNT','LOCAL_FRAME_CAUSAL','TAIL_SECTION_TOPOLOGY_TRANSITION','TAIL_SECTION_TOPOLOGY_TRANSITION_TYPE','TAIL_IDENTITY_FLIP_COUNT','TAIL_SOURCE_SUPPORTED_GEOMETRIC_TURN_COUNT','TAIL_CURRENT_TURNING_ANGLE','TAIL_ADAPTIVE_TURNING_ANGLE','TRUE_SOURCE_GEOMETRIC_BEND','WRONG_PHYSICAL_CHAIN_BRANCH','MISSING_INTERMEDIATE_STATION_EVIDENCE','SEAM_VALIDITY_CONTRACT_NEEDS_REVISION','FUSELAGE_HASH_UNCHANGED','V7D3_ARTIFACT_HASH_UNCHANGED','GT_USED_AS_INPUT','FINAL_CAD_METRIC_USED_FOR_DECISION','REPORT','BRANCH_CSV','ADAPTIVE_EVIDENCE_CSV','DEBUG_CONTACT_SHEET','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
lines=[]
for k in fields:
 v=d[k]
 if isinstance(v,bool):v=str(v).lower()
 elif isinstance(v,list):v=json.dumps(v)
 lines.append(f'{k}={v}')
text='\n'.join(lines)+'\n';(OUT/'artifacts/final_terminal_output.txt').write_text(text);print(text,end='')
