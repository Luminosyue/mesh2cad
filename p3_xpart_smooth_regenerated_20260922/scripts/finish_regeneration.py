from pathlib import Path
import json,time,subprocess,sys
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
while True:
    lines=(r/'batch.log').read_text().splitlines()
    try:s=json.loads(lines[-1])
    except (ValueError,IndexError):s={}
    if s.get('total_parts')==793 and not s.get('status_counts',{}).get('PENDING'):
        (r/'first_pass_done.json').write_text(json.dumps(dict(time=time.time(),summary=s)));print('FIRST_PASS_FINISHED',flush=True);break
    time.sleep(10)
while True:
    main_done='REFINEMENT_FINISHED' in (r/'refinement.log').read_text()
    extra_done='EXTRA_REFINEMENT_FINISHED' in (r/'extra_refinement.log').read_text()
    if main_done and extra_done:break
    time.sleep(10)
print('ALL_REFINEMENT_FINISHED',flush=True)
subprocess.run([sys.executable,str(r/'scripts/regenerate_smooth.py'),'--summary'],check=True)
# Avoid concurrently auditing paths with the first audit sweep.
while True:
    lines=(r/'audit.log').read_text().splitlines()
    if lines and lines[-1].startswith('{"total":'):break
    time.sleep(10)
with (r/'final_audit.log').open('w') as f:subprocess.run([sys.executable,str(r/'scripts/audit_regenerated.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
print('FINAL_AUDIT_FINISHED',flush=True)
(r/'pipeline_done.json').write_text(json.dumps(dict(time=time.time())))
