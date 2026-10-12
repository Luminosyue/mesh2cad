import json, re
from pathlib import Path

r=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/best_multipart_full_recovery_v2')
p=json.loads((r/'metrics/part_results.json').read_text());s=json.loads((r/'metrics/summary.json').read_text())
accepted=[x for x in p if x['quality']!='TRUE_FAILURE']
s['PARAMETRIC_CAD_AREA_COVERAGE']=sum(x['area_ratio'] for x in accepted if x.get('backend')=='PRIMITIVE_CSG')
s['LOFT_CAD_AREA_COVERAGE']=sum(x['area_ratio'] for x in accepted if x.get('backend')=='MULTI_SECTION_LOFT')
s['SURFACE_BREP_AREA_COVERAGE']=sum(x['area_ratio'] for x in accepted if x.get('backend')=='FREEFORM_BSPLINE_BREP')
log=(r/'logs/pytest.log').read_text();m=re.search(r'(\d+) passed(?:, (\d+) failed)?',log);assert m
s['TESTS_PASSED']=int(m.group(1));s['TESTS_FAILED']=int(m.group(2) or 0)
s['BLOCKERS']=[] if s['TOTAL_CAD_AREA_COVERAGE']>=.95 else ['TARGET_COVERAGE_BELOW_0.95']
(r/'metrics/summary.json').write_text(json.dumps(s,indent=2)+'\n')
(r/'artifacts/best_multipart_full_recovery_v2_report.md').write_text('# BEST_MULTIPART_FULL_RECOVERY_V2\n\n```json\n'+json.dumps(s,indent=2)+'\n```\n')
print(json.dumps(s,indent=2))
