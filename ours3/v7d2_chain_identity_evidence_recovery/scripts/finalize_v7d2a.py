#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2_chain_identity_evidence_recovery')
s=json.loads((ROOT/'artifacts/pretest_summary.json').read_text())
report=f'''# V7D2A Chain Identity Evidence Audit

## Outcome

The audit passed. No recovery/refit operation was executed. The FUSELAGE 4/9 ceiling is upstream of V7D1 DAG scoring: all 12 stations have raw intersections, but only 9 stations contain any saved open chain and only S03-S06 contain the two measured chain identities needed to form a seam endpoint pair.

The saved `raw_segment_graph` objects are count summaries only; graph nodes/edges were not persisted. Therefore option A cannot reconstruct the missing FUSELAGE chain geometry from current artifacts. A versioned, offline Geometry Analyzer extraction must persist every raw graph component and its ordered coordinates. Runtime remeasurement remains forbidden.

## Vertical-tail direction audit

The two global-path spikes occur at S04 and S05. The persisted chain geometry alternates by about 178 degrees across adjacent stations despite `orientation_flips_fixed=7`. The implementation reverses point arrays but does not recompute the descriptor later used as the preceding orientation reference. Consequently endpoint indices no longer denote stable physical endpoints; endpoint-state changes line up with the 171.07 and 173.77 degree path turns.

## Coverage semantics

- Raw section: fraction of the 12 requested stations with a measured intersection.
- Open chain: union of stations represented by either selected seam track, divided by 12 requested stations.
- Chain identity and endpoint evidence: stations shared by both selected tracks, divided by their open-chain union support. This preserves the V7D1 4/9 and 6/8 physical ceilings.

## Prohibited operations

DAG weights unchanged; no interpolation, Master Curve, constrained refit, V7C, Sewing, or runtime geometry remeasurement was executed.
'''
(ROOT/'artifacts/v7d2a_evidence_audit_report.md').write_text(report)
s['REPORT']=str(ROOT/'artifacts/v7d2a_evidence_audit_report.md')
test_log=ROOT/'logs/tests.log'
passed=failed=0
if test_log.exists():
 import re
 text_log=test_log.read_text()
 match=re.search(r'(\d+) passed',text_log)
 if match: passed=int(match.group(1))
 match=re.search(r'(\d+) failed',text_log)
 if match: failed=int(match.group(1))
s['TESTS']={'passed':passed,'failed':failed}
(ROOT/'artifacts/final_summary.json').write_text(json.dumps(s,indent=2)+'\n')
fields=['CURRENT_GATE','FUSELAGE_RAW_SECTION_COVERAGE','FUSELAGE_OPEN_CHAIN_COVERAGE','FUSELAGE_CHAIN_IDENTITY_COVERAGE','FUSELAGE_ENDPOINT_EVIDENCE_COVERAGE','VERTICAL_TAIL_RAW_SECTION_COVERAGE','VERTICAL_TAIL_OPEN_CHAIN_COVERAGE','VERTICAL_TAIL_CHAIN_IDENTITY_COVERAGE','VERTICAL_TAIL_ENDPOINT_EVIDENCE_COVERAGE','FUSELAGE_MISSING_EVIDENCE_CLASS','VERTICAL_TAIL_DIRECTION_REVERSAL_ROOT_CAUSE','OFFLINE_GEOMETRY_ANALYZER_REGEN_REQUIRED','NEXT_FIX','BLOCKERS']
text='\n'.join(f'{k}={s[k]}' for k in fields)+'\n'
(ROOT/'artifacts/final_terminal_output.txt').write_text(text)
print(text,end='')
