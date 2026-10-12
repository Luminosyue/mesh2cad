"""Reserve a disjoint, bounded tail of the completed refinement queue."""
from pathlib import Path
import json,time,sys
from concurrent.futures import ThreadPoolExecutor
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
ns={};exec((ROOT/'scripts/refine_follow.py').read_text().split('with ThreadPoolExecutor(max_workers=8) as pool:')[0],ns)
paths=[]
for p in sorted((ROOT/'cases').glob('*/*/report.json'),reverse=True):
    r=json.loads(p.read_text());od=ROOT/'refinements'/r['case_id']/r['part_id']
    if r['case_id']<'birdhouse' or r['status']=='ACCEPTED' or not r.get('artifacts_complete') or od.exists():continue
    paths.append(p)
# Leave the original follower its earlier backlog; each reservation is visible to it.
paths=paths[:min(100,max(0,len(paths)-24))]
if '--resume' in sys.argv:paths=[Path(p) for p in json.loads((ROOT/'extra_refinement_inputs.json').read_text())]
(ROOT/'extra_refinement_inputs.json').write_text(json.dumps([str(p) for p in paths]))
for p in paths:
    od=ROOT/'refinements'/p.parent.parent.name/p.parent.name;od.mkdir(parents=True,exist_ok=True)
    (od/'follow_done.json').write_text(json.dumps(dict(status='reserved_by_extra_worker',time=time.time())))
print('RESERVED',len(paths),flush=True)
with ThreadPoolExecutor(max_workers=16) as pool:results=list(pool.map(ns['run'],paths))
(ROOT/'extra_refinement_done.json').write_text(json.dumps(dict(parts=len(results))))
print('EXTRA_REFINEMENT_FINISHED',len(results),flush=True)
