from pathlib import Path
import json,subprocess,sys,shutil,concurrent.futures
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_historical_route_100_20261011/runs/new_object_006')
rows=json.loads((O/'part_results.json').read_text());selected={}
for r in rows:
 if r.get('step_reload_pass'):
  p=Path(r['cad_program_path']);compile(p.read_text(),str(p),'exec');selected.setdefault(r['method'],r)
def run(item):
 method,r=item;d=O/'validation'/method;d.mkdir(parents=True,exist_ok=True);src=Path(r['cad_program_path']);p=d/src.name;shutil.copy2(src,p)
 proc=subprocess.run([sys.executable,'-B',str(p)],capture_output=True,text=True,timeout=180)
 (d/'execution.log').write_text(proc.stdout+proc.stderr)
 result={'method':method,'object_id':r['object_id'],'part_id':r['part_id'],'returncode':proc.returncode,'step_created':p.with_suffix('.step').exists()}
 assert proc.returncode==0 and result['step_created'],result
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,selected.items()))
report={'syntax_checked_n':sum(r.get('step_reload_pass',False) for r in rows),'representative_standalone_programs':results,'status':'PASS'}
(O/'program_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
