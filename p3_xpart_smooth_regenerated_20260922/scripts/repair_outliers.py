"""Re-fit high-error outputs after rejecting degenerate circle fits."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
R=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
if '--one' in sys.argv:
    import regenerate_smooth as rs
    import refine_sections
    refine_sections.candidates=lambda mesh:rs.candidates(mesh,[])
    rs.process(Path(sys.argv[2]),True);sys.exit()
paths=[]
for p in sorted((R/'cases').glob('*/*/report.json')):
    r=json.loads(p.read_text())
    if r.get('quality',{}).get('p95_distance_pct_diagonal',0)>5 or r['case_id']=='vase':paths.append(r)
print('TARGETS',len(paths),[(r['case_id'],r['part_id']) for r in paths],flush=True)
if '--retry-errors' in sys.argv:
    paths=[r for r in paths if "name 'poly' is not defined" in (R/'outlier_logs'/r['case_id']/(r['part_id']+'.log')).read_text()]
    print('RETRY_CORRECTED_WORKERS',len(paths),flush=True)
def run(r):
    log=R/'outlier_logs'/r['case_id']/(r['part_id']+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as f:
        try:result=subprocess.run([sys.executable,__file__,'--one',r['source_path']],stdout=f,stderr=subprocess.STDOUT,timeout=300);status=result.returncode
        except subprocess.TimeoutExpired:status='timeout'
    new=json.loads((R/'cases'/r['case_id']/r['part_id']/'report.json').read_text())
    print('OUTLIER',r['case_id'],r['part_id'],status,new['status'],new.get('quality',{}).get('p95_distance_pct_diagonal'),flush=True)
with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(run,paths))
print('OUTLIER_REPAIR_FINISHED',flush=True)
