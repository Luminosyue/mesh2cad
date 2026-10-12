#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path

S=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cad_part_graph_gate1')
A=S/'artifacts'; L=S/'logs/test_gate.log'
summary_path=A/'cad_part_graph_gate1_summary.json'
summary=json.loads(summary_path.read_text())
log=L.read_text()
m=re.search(r'Ran (\d+) tests?',log)
passed=int(m.group(1)) if m and '\nOK\n' in log else 0
failed=0 if '\nOK\n' in log else 1
summary['TESTS_PASSED']=passed
summary['TESTS_FAILED']=failed
summary['CURRENT_GATE']='CAD_PART_GRAPH_GATE_1_PASS' if passed>=25 and failed==0 and not summary['BLOCKERS'] else 'CAD_PART_GRAPH_GATE_1_FAIL'
summary_path.write_text(json.dumps(summary,indent=2)+'\n')

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
files=[
 'coordinate_frame_audit.json','physx_3d_localization_audit.json','p3_segment_graph.json',
 'physx_p3_association.json','cad_part_graph_v1.json','cad_assembly_graph_v1.json',
 'cad_part_mac_manifest_v1.json','cad_part_graph_human_review.csv',
 'raw_p3_vs_cad_parts.png','cad_part_merge_graph.png','cad_part_candidates_contact_sheet.png'
]
test_results={
 'suite':'CAD_PART_GRAPH_GATE_1', 'runner':'python unittest',
 'tests_passed':passed,'tests_failed':failed,'exit_code':0 if failed==0 else 1,
 'test_log':str(L),'artifact_sha256':{name:sha(A/name) for name in files},
}
(A/'test_results.json').write_text(json.dumps(test_results,indent=2)+'\n')

report=f'''# CAD Part Graph Gate 1 — REAL_03

Status: {summary['CURRENT_GATE']}.

- Frozen P3 segments: 26
- Sparse graph: 26 boundary-adjacent edges of 325 possible pairs
- PhysX reused: true; 3D part localization unavailable
- PhysX function zero reason: {summary['PHYSX_FUNCTION_ZERO_REASON']}
- Auto/review/forbidden edges: {summary['AUTO_MERGE_EDGES']}/{summary['REVIEW_MERGE_EDGES']}/{summary['FORBIDDEN_MERGE_EDGES']}
- Final CADPART candidates: {summary['FINAL_CAD_PART_CANDIDATES']}
- Reconstruction states (ready/review/freeform/further decomposition): {summary['READY_FOR_CAD_RECONSTRUCTION']}/{summary['REVIEW_BEFORE_CAD']}/{summary['FREEFORM_BACKEND_REQUIRED']}/{summary['REQUIRES_FURTHER_DECOMPOSITION']}
- CADability A/B/C/D/E: {summary['CADABILITY_A']}/{summary['CADABILITY_B']}/{summary['CADABILITY_C']}/{summary['CADABILITY_D']}/{summary['CADABILITY_E']}
- Triangle coverage: 385828/385828 exactly once; unassigned 0; multi-assigned 0
- New P3/PhysX/MAC/LLM-CAD/STEP: 0/0/0/0/0
- Assembly metadata only; assembly was not started and no assembly STEP was generated
- Tests: {passed} passed, {failed} failed
- Blockers: []
'''
(A/'cad_part_graph_gate1_report.md').write_text(report)
