#!/usr/bin/env python3
import json,re
from pathlib import Path
S=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cad_part_recovery_v1'); A=S/'artifacts'
p=A/'cad_part_recovery_v1_summary.json'; s=json.loads(p.read_text()); log=(S/'logs/test_stage.log').read_text(); m=re.search(r'Ran (\d+) tests?',log); passed=int(m.group(1)) if m and '\nOK\n' in log else 0; failed=0 if passed else 1; s['TESTS_PASSED']=passed; s['TESTS_FAILED']=failed; p.write_text(json.dumps(s,indent=2)+'\n')
report=f'''# CAD Part Recovery V1

Status: `{s['CURRENT_STAGE']}`. Track F1 is `{s['TRACK_F1_STATUS']}` solely because `CADPART_006` was rejected before inference by provider HTTP 403 `AllocationQuota.FreeTierOnly`; no historical geometry-identical STEP exists and no futile retry was made. Track F2 is `PASS`.

- F1 input: 4 frozen READY parts; historical results reused: 2; new part attempts: 2
- STEP available / independently BRep valid: {s['TOTAL_STEP_AVAILABLE']} / {s['BREP_VALID_COUNT']}
- Q1 / Q2 / Q3: {s['Q1_STRONG_PAIR']} / {s['Q2_USABLE_PAIR']} / {s['Q3_REJECT']}
- Accepted pseudo CAD parts: {s['ACCEPTED_CAD_PARTS']} of 4; recovery rate: {s['PART_CAD_RECOVERY_RATE']:.2f}
- F2 review packets: 14 edges and 20 parts; human decisions applied: false
- Partial assembly pilot ready: {str(s['PARTIAL_ASSEMBLY_PILOT_READY']).lower()} ({s['ASSEMBLY_CAD_PARTS_AVAILABLE']} accepted part)
- New P3/PhysX runs: 0/0; no assembly STEP, STEP GT, ABC data, or ICP
- Tests: {passed} passed, {failed} failed
- Blockers: F1=[QUOTA], F2=[]
'''
(A/'cad_part_recovery_v1_report.md').write_text(report,encoding='utf-8')
(A/'test_results.json').write_text(json.dumps({'suite':'CAD_PART_RECOVERY_V1','tests_passed':passed,'tests_failed':failed,'log':str(S/'logs/test_stage.log')},indent=2)+'\n')
