from pathlib import Path
import csv, subprocess, time, os
from multiprocessing import Pool
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); BASE=ROOT/'ours3/cadfit_val1000_baseline_v1'; OUT=ROOT/'ours3/cadfit_recovered_meshes_v1'; BUILD=ROOT/'scripts/deepcad/build_deepcad_sample.py'; PY='/data/miniconda3/envs/cadfit-env/bin/python'
def one(cid):
    short=cid.split('__',1)[-1]; src=ROOT/'cad_spatial_dataset/DeepCAD/official/data/cad_json'/short[:4]/(short[5:]+'.json'); sample=OUT/'DeepCAD/train'/short
    if (sample/'model.stl').exists() and (sample/'model.step').exists(): return [cid,'ALREADY_PRESENT',0,'']
    t=time.time()
    try:
        p=subprocess.run([PY,str(BUILD),'--json',str(src),'--output',str(OUT),'--sample-id',short,'--num-points','8192','--no-vis'],cwd=ROOT,capture_output=True,text=True,timeout=600)
        ok=p.returncode==0 and (sample/'model.stl').exists() and (sample/'model.step').exists(); return [cid,'PASS' if ok else 'FAILED',round(time.time()-t,2),(p.stderr or p.stdout)[-500:]]
    except Exception as e: return [cid,'TIMEOUT_OR_EXCEPTION',round(time.time()-t,2),repr(e)]
def main():
    rows=list(csv.DictReader((BASE/'input/CADFIT_INPUT_AUDIT.csv').open())); ids=[r['case_id'] for r in rows if r['source_format']=='MISSING']; remaining=[c for c in ids if not (OUT/'DeepCAD/train'/c.split('__',1)[-1]/'model.stl').exists()]
    out=OUT/'RECOVERY_STATUS_PARALLEL.csv'
    with out.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['case_id','status','elapsed_sec','error']); f.flush()
        with Pool(6) as pool:
            for i,res in enumerate(pool.imap_unordered(one,remaining),1): w.writerow(res); f.flush(); print(f'[{i}/{len(remaining)}] {res[0]} {res[1]}',flush=True)
if __name__=='__main__': main()
