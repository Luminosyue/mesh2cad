"""Rebuild delivered scripts in an isolated directory and check saved STEP."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,subprocess,tempfile,hashlib,shutil,concurrent.futures,time,signal
from rebuild_cases import ROOT,RUN,CODE,dump

def check(folder):
    import cadquery as cq,runpy
    folder=Path(folder);pid=folder.name;report=json.loads((folder/'report.json').read_text())
    with tempfile.TemporaryDirectory(prefix='cadquery_verify_') as td:
        p=Path(td)/f'{pid}.py';shutil.copy2(folder/p.name,p)
        module=runpy.run_path(str(p));built=module['build']();saved=cq.importers.importStep(str(folder/f'{pid}.step')).val()
        assert built.isValid() and saved.isValid()
        assert len(built.Solids())==len(saved.Solids())==report['cad_solids']
        assert len(built.Faces())==len(saved.Faces())
        a=sum(s.Volume(tol=1e-7) for s in built.Solids());b=sum(s.Volume(tol=1e-7) for s in saved.Solids())
        rel=abs(a-b)/max(abs(a),1e-14);assert rel<1e-5,rel
        source_hash=hashlib.sha256(Path(report['source']).read_bytes()).hexdigest();assert source_hash==report['source_sha256']
        result=dict(status='VERIFIED',independent_script_rebuild=True,step_valid=True,solids=len(saved.Solids()),faces=len(saved.Faces()),relative_volume_difference=rel,source_unchanged=True,script_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),step_sha256=hashlib.sha256((folder/f'{pid}.step').read_bytes()).hexdigest())
        dump(folder/'rebuild_validation.json',result)

def verify(folder):
    if (folder/'rebuild_validation.json').exists():return
    with (folder/'validation.log').open('w') as log:
        p=subprocess.Popen([sys.executable,str(__file__),'check',str(folder)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:rc=p.wait(timeout=100)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();rc=-9
    if rc!=0:dump(folder/'rebuild_validation.json',dict(status='VERIFICATION_TIMEOUT' if rc==-9 else 'VERIFICATION_FAILED',returncode=rc))

def watch():
    seen=set();futures={};last=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        while True:
            manifest=json.loads((RUN/'task_manifest.json').read_text());tasks=manifest['tasks']
            ready=[];jobsdone=0
            for case,pid in tasks:
                folder=ROOT/case/'xpart_parts_cadquery_features'/pid
                if (folder/'job_status.json').exists():
                    jobsdone+=1
                    if (folder/'report.json').exists() and str(folder) not in seen:ready.append(folder)
            for folder in ready:seen.add(str(folder));futures[pool.submit(verify,folder)]=folder
            done=sum(f.done() for f in futures)
            dump(RUN/'validation_progress.json',dict(total=len(tasks),jobs_finished=jobsdone,scheduled=len(futures),validation_finished=done))
            if jobsdone==len(tasks) and done==len(futures):break
            time.sleep(12)

if __name__=='__main__':
    if sys.argv[1]=='check':check(sys.argv[2])
    else:watch()
