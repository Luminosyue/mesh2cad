import time,json,subprocess,os,zipfile,traceback
from pathlib import Path
root=Path(__file__).resolve().parent
python='/data/miniconda3/envs/cadrille/bin/python'
try:
    start=time.time()
    while True:
        done=[]
        for i in range(2):
            p=root/'cadrille'/f'SHARD_{i}.DONE'
            if p.exists():done.append(json.loads(p.read_text()))
        if len(done)==2 and sum(r['parts'] for r in done)==306:break
        assert time.time()-start<1800,'Inference completion timeout'
        time.sleep(10)
    for method in ['cadrille','cadrecode']:
        count=len(list((root/method).glob('*/PART_*/STATUS.json')))
        assert count==306,(method,count)
    for script in ['finalize_run.py','render_results.py']:
        env=os.environ.copy();env.update(OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',EGL_PLATFORM='surfaceless',LIBGL_ALWAYS_SOFTWARE='1')
        proc=subprocess.run([python,'-u',str(root/script)],cwd=root,env=env,timeout=1200)
        assert proc.returncode==0,(script,proc.returncode)
    out=root/'deliverables'
    for method in ['cadrille','cadrecode']:
        path=out/f'{method}_21_CAD.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in (out/method).rglob('*'):
                if p.is_file():z.write(p,p.relative_to(out))
            for p in (out/'scripts').glob('*.py'):z.write(p,p.relative_to(out))
            for f in ['README.md','SUMMARY.json','summary.csv','MANIFEST.json','INPUT_COORDINATE_AUDIT.json','comparison_21.png']:z.write(out/f,f)
    with zipfile.ZipFile(out/'source_parts_and_previews.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for sub in ['input_parts','previews']:
            for p in (out/sub).rglob('*'):
                if p.is_file():z.write(p,p.relative_to(out))
    (root/'PIPELINE_DONE.json').write_text(json.dumps(dict(status='COMPLETE',finished=time.time(),output=str(out)),indent=2))
except Exception:
    (root/'PIPELINE_ERROR.txt').write_text(traceback.format_exc());raise
