from pathlib import Path
import json
from collections import Counter
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
reports=list((r/'cases').glob('*/*/report.json'));rows=[json.loads(p.read_text()) for p in reports]
print('STATUS',dict(Counter(x['status'] for x in rows)),'COMPLETE',sum(x.get('artifacts_complete',False) for x in rows))
stale=[]
for p,x in zip(reports,rows):
    fp=r/'refinements'/x['case_id']/x['part_id']/'follow_done.json'
    if x['status']=='NEEDS_REFINEMENT' and not x.get('visual_review') and not x.get('refinement_of_current_run') and fp.exists() and p.stat().st_mtime>fp.stat().st_mtime:stale.append((x['case_id'],x['part_id']))
print('STALE_EARLY_REFINEMENTS',stale)
audits=[json.loads(p.read_text()) for p in (r/'validation').glob('*/*.json')]
print('AUDIT',len(audits),'PASSED',sum(a['passed'] for a in audits))
current=0;failed=[]
import hashlib
for a in audits:
    od=r/'cases'/a['case_id']/a['part_id']
    h={n:hashlib.sha256((od/n).read_bytes()).hexdigest() for n in ('cad.py','model.step','report.json')}
    if h==a.get('hashes'):
        current+=1
        if not a['passed']:failed.append((a['case_id'],a['part_id'],a['errors']))
print('CURRENT_AUDITS',current,'CURRENT_FAILURES',failed)
for a in sorted(rows,key=lambda x:-(x.get('quality') or {}).get('p95_distance_pct_diagonal',0))[:5]:print('LARGEST_ERROR',a['case_id'],a['part_id'],a.get('quality'))
