from __future__ import annotations
import csv, json, subprocess, sys, time
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
BASE = ROOT / 'ours3/cadfit_val1000_baseline_v1'
OUT = ROOT / 'ours3/cadfit_recovered_meshes_v1'
BUILD = ROOT / 'scripts/deepcad/build_deepcad_sample.py'
ENV_PY = '/data/miniconda3/envs/cadfit-env/bin/python'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((BASE/'input/CADFIT_INPUT_AUDIT.csv').open()))
    missing = [r['case_id'] for r in rows if r['source_format'] == 'MISSING']
    status_path = OUT/'RECOVERY_STATUS.csv'
    with status_path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['case_id','source_json','returncode','status','elapsed_sec','error'])
        w.writeheader()
        for i, cid in enumerate(missing, 1):
            short = cid.split('__', 1)[-1]
            src = ROOT/'cad_spatial_dataset/DeepCAD/official/data/cad_json'/short[:4]/(short[5:]+'.json')
            sample = OUT/'DeepCAD/train'/short
            if not src.exists():
                w.writerow({'case_id':cid,'source_json':str(src),'returncode':'','status':'SOURCE_JSON_MISSING','elapsed_sec':'','error':''}); f.flush(); continue
            if (sample/'model.stl').exists() and (sample/'model.step').exists():
                w.writerow({'case_id':cid,'source_json':str(src),'returncode':0,'status':'ALREADY_PRESENT','elapsed_sec':0,'error':''}); f.flush(); continue
            t=time.time()
            cmd=[ENV_PY, str(BUILD), '--json', str(src), '--output', str(OUT), '--sample-id', short, '--num-points', '8192', '--no-vis']
            try:
                proc=subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
                ok=proc.returncode==0 and (sample/'model.stl').exists() and (sample/'model.step').exists()
                status='PASS' if ok else 'FAILED'
                err=(proc.stderr or proc.stdout)[-1000:]
            except Exception as e:
                proc=None; status='TIMEOUT_OR_EXCEPTION'; err=repr(e)
            w.writerow({'case_id':cid,'source_json':str(src),'returncode':proc.returncode if proc else '','status':status,'elapsed_sec':round(time.time()-t,2),'error':err}); f.flush()
            print(f'[{i}/{len(missing)}] {cid} {status}', flush=True)
    print('DONE', status_path)

if __name__=='__main__': main()
