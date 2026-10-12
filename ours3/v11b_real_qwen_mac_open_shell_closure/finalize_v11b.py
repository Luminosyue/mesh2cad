#!/usr/bin/env python3
import json,re
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'v11b_real_qwen_mac_open_shell_closure';p=OUT/'artifacts/pretest_summary.json';d=json.load(open(p));log=(OUT/'logs/tests.log').read_text();m=re.search(r'(\d+) passed',log);f=re.search(r'(\d+) failed',log);d['TESTS_PASSED']=int(m.group(1)) if m else 0;d['TESTS_FAILED']=int(f.group(1)) if f else 0
if d['TESTS_FAILED'] or not d['TESTS_PASSED']:d['CURRENT_GATE']='V11B_REAL_QWEN_MAC_AND_OPEN_SHELL_CLOSURE_FAIL';d['V11B_PASS']=False;d['BLOCKERS']=sorted(set(d['BLOCKERS']+['TEST_FAILURE']))
(OUT/'artifacts/final_summary.json').write_text(json.dumps(d,indent=2)+'\n')
fields=['CURRENT_GATE','V11B_PASS','REAL_QWEN_CALLS','REAL_QWEN_REPAIR_CALLS','REAL_QWEN_EXECUTABLE_PLAN_COUNT','REAL_QWEN_EXECUTION_SUCCESS_COUNT','REAL_QWEN_FRESH_BREP_COUNT','QWEN_PLACEHOLDER_REF_REJECT_COUNT','QWEN_AUTO_REFERENCE_CORRECTION_COUNT','REAL_MAC_CALLS','REAL_MAC_EXECUTABLE_PLAN_COUNT','MAC_FRESH_BREP_COUNT','MAC_EXTERNAL_RESOURCE_FAILURE','MAC_TO_V11_ADAPTER_TEST_PASS','MAC_INVALID_BUILDER_EXECUTED_COUNT','MAC_UNMEASURED_PARAMETER_CONSUMED_COUNT','MAC_DIRECT_OCC_BYPASS_COUNT','OPEN_SHELL_EXECUTABLE_PLAN_COUNT','OPEN_SHELL_FRESH_BREP_COUNT','OPEN_SHELL_SHARED_OCC_EDGE_COUNT','OPEN_SHELL_PCURVE_COUNT','OPEN_SHELL_TRIMMED_FACE_COUNT','OPEN_SHELL_HISTORICAL_STEP_REUSED','QWEN_CANDIDATE_COUNT','MAC_CANDIDATE_COUNT','GEOMETRY_ALTERNATIVE_CANDIDATE_COUNT','EXECUTED_PARAMETER_WITHOUT_REF_COUNT','INVALID_BUILDER_EXECUTED_COUNT','DIRECT_PLAN_TO_OCC_BYPASS_COUNT','HISTORICAL_STEP_REUSED','FALLBACK_USED','GEOMETRY_EXPLOSION_COUNT','V10_REGRESSION_PASS','V7D3_REGRESSION_PASS','REPORT','TESTS_PASSED','TESTS_FAILED','BLOCKERS']
lines=[]
for k in fields:
 v=d[k]
 if isinstance(v,bool):v=str(v).lower()
 elif isinstance(v,list):v=json.dumps(v)
 lines.append(f'{k}={v}')
text='\n'.join(lines)+'\n';(OUT/'artifacts/final_terminal_output.txt').write_text(text);print(text,end='')
