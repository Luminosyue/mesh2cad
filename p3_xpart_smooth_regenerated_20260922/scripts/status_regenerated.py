from pathlib import Path
from collections import Counter
import json
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
rows=[json.loads(p.read_text()) for p in (r/'cases').glob('*/*/report.json')]
print('STATUS',dict(Counter(x['status'] for x in rows)))
print('METHODS',dict(Counter(x.get('method') for x in rows)))
for x in rows:
    if x.get('method') in ('spline_revolve','radial_revolve') and x['status']=='ACCEPTED':print('REVOLVE',x['case_id'],x['part_id'],x['quality']['p95_distance_pct_diagonal'])
print('FAILED',[(x['case_id'],x['part_id'],x.get('error','')[:100]) for x in rows if x['status'] not in ('ACCEPTED','NEEDS_REFINEMENT')])
audits=[json.loads(p.read_text()) for p in (r/'validation').glob('*/*.json')]
print('AUDITS',len(audits),'PASSED',sum(a['passed'] for a in audits))
for a in audits:
    if not a['passed'] and a.get('exact_surface_check'):print('EXACT_FAILED',a['case_id'],a['part_id'],a.get('exact_surface_check'))
