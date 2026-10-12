"""Refine finished nonpassing parts alongside the first pass; never touch tank."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['LP_NUM_THREADS']='2';os.environ['VTK_SMP_MAX_THREADS']='2'
from pathlib import Path
import sys,json,time,subprocess
from concurrent.futures import ThreadPoolExecutor
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
def run(report_path):
    r=json.loads(report_path.read_text());case=r['case_id'];part=r['part_id'];od=ROOT/'refinements'/case/part;od.mkdir(parents=True,exist_ok=True)
    source=r.get('source_path') or str(Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')/case/'xpart_parts'/part/('complete_part_'+part[5:]+'.obj'))
    source=str(Path(source).relative_to('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases'))
    with (od/'run.log').open('w') as f:
        try:
            rr=subprocess.run([sys.executable,str(ROOT/'scripts/regenerate_smooth.py'),'--part',source,'--refine'],stdout=f,stderr=subprocess.STDOUT,timeout=300)
            status='completed' if rr.returncode==0 else 'process_failed'
        except subprocess.TimeoutExpired:status='timeout'
    (od/'follow_done.json').write_text(json.dumps(dict(case=case,part=part,status=status)))
    result=json.loads((ROOT/'cases'/case/part/'report.json').read_text())
    print('REFINED',case,part,status,result.get('status'),flush=True)
    return result

with ThreadPoolExecutor(max_workers=8) as pool:
    active={};claimed=set();done=0
    while True:
        for key,future in list(active.items()):
            if future.done():
                try:future.result()
                except Exception as e:print('ERROR',key,str(e),flush=True)
                del active[key];done+=1
        paths=sorted((ROOT/'cases').glob('*/*/report.json'));available=[]
        for p in paths:
            try:r=json.loads(p.read_text())
            except Exception:continue
            key=(r['case_id'],r['part_id'])
            if key[0]=='tank' or key in claimed:continue
            rp=ROOT/'refinements'/key[0]/key[1]/'follow_done.json'
            if rp.exists():claimed.add(key);continue
            if r['status']=='ACCEPTED':continue
            if r.get('artifacts_complete') or r['status'] in ('FAILED','TIMEOUT','INCOMPLETE'):available.append((p,key))
        for p,key in available[:max(0,8-len(active))]:claimed.add(key);active[key]=pool.submit(run,p)
        (ROOT/'refinement_progress.json').write_text(json.dumps(dict(done=done,active=len(active),waiting=len(available),claimed=len(claimed))))
        finished=(ROOT/'first_pass_done.json').exists()
        if finished and not active and not available:break
        time.sleep(5)
print('REFINEMENT_FINISHED',done,flush=True)
