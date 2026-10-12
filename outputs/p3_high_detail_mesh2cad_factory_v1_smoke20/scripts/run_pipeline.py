"""Replay the recorded Smoke20 pipeline. Never exceeds 20 objects."""
import os,argparse,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,choices=[3,5,20],required=True);ap.add_argument('--stage',choices=['decompose','features','cad','assemble','visualize','finalize','replay'],required=True);a=ap.parse_args()
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
cad='/data/miniconda3/envs/cadfit-env/bin/python';p3='/data/miniconda3/envs/hunyuan/bin/python'
def run(script,*args,python=cad):subprocess.run([python,'-B',str(O/'scripts'/script),*map(str,args)],env=env,check=True)
if a.stage in ['decompose','replay']:run('p3_smoke_segment.py','--limit',a.limit,python=p3)
if a.stage in ['features','replay']:run('p3_part_features.py','--limit',a.limit)
if a.stage=='replay':
 for response in sorted((O/'scripts').glob('p3_plans*.json')):run('p3_install_plans.py','--response',response)
if a.stage in ['cad','replay']:run('p3_part_cad.py','--limit',a.limit)
if a.stage in ['assemble','replay']:run('p3_assemble.py','--limit',a.limit)
if a.stage in ['visualize','replay']:run('p3_visualize.py','--limit',a.limit)
if a.stage in ['finalize','replay']:
 run('p3_stage_check.py','--limit',a.limit)
 if a.limit==20:
  run('p3_report.py');run('p3_validate.py');run('p3_validate_assembly.py')
