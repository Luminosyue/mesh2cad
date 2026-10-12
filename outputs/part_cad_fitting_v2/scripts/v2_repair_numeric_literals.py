"""Repair representation only; retain candidate IDs, parameter values and failed evidence."""
from v2_common import *
import argparse,sys,shutil,subprocess
from concurrent.futures import ProcessPoolExecutor
import trimesh
from metric_runtime import evaluate
from execute_candidate import validate

class Scalars(ast.NodeTransformer):
 def visit_Call(self,n):
  n=self.generic_visit(n)
  if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='np' and n.func.attr in ['float64','float32']:
   assert len(n.args)==1 and not n.keywords
   return ast.copy_location(ast.Constant(float(ast.literal_eval(n.args[0]))),n)
  return n

def repair(row):
 d=O/'cases'/row['case_id'];changed=0
 for dest in sorted((d/'candidates').glob('candidate_*')):
  rp=dest/'record.json'
  if not rp.exists():
   if (dest/'execution').exists() and not (dest/'execution_interrupted').exists():(dest/'execution').rename(dest/'execution_interrupted')
   continue
  rec=read(rp)
  if rec.get('execution',{}).get('error')!='Disallowed CAD operation: float64':continue
  code=(dest/'cad.py').read_text();tree=Scalars().visit(ast.parse(code));ast.fix_missing_locations(tree);fixed=ast.unparse(tree)+'\n';validate(fixed)
  assert 'np.float' not in fixed
  shutil.copyfile(rp,dest/'record.before_numeric_repair.json');shutil.copyfile(dest/'cad.py',dest/'cad.before_numeric_repair.py');(dest/'cad.py').write_text(fixed)
  p=subprocess.run([sys.executable,'-B',str(O/'scripts/execute_candidate.py'),str(dest/'cad.py'),str(dest/'execution_numeric_repair')],capture_output=True,text=True,timeout=120)
  (dest/'numeric_repair.log').write_text(p.stdout+'\n'+p.stderr);ex=read(dest/'execution_numeric_repair/execution.json');rec['execution']=ex;rec['numeric_serialization_repair']=True
  if ex.get('tessellation_pass'):
   m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);cm=trimesh.load(dest/'execution_numeric_repair/cad_mesh_from_reloaded_step.ply',force='mesh',process=True);met=evaluate(m,cm,row['seed']);rec.update(metrics=met,score=score(met));shutil.copyfile(dest/'execution_numeric_repair/cad.step',dest/'cad.step');shutil.copyfile(dest/'execution_numeric_repair/cad_mesh_from_reloaded_step.ply',dest/'cad_mesh.ply')
  dump(rp,rec);changed+=1
 if changed and (d/'result.json').exists():
  rp=d/'result.json';shutil.copyfile(rp,d/'result.before_numeric_repair.json');r=read(rp);attempts=[read(p) for p in sorted((d/'candidates').glob('candidate_*/record.json'))];valid=[x for x in attempts if 'metrics' in x];best=min(valid,key=lambda x:(not x['metrics']['strict_pass'],x['score']));bd=Path(best['path'])
  for f in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:shutil.copyfile(bd/f,d/'cad'/f)
  dump(d/'metrics/metrics.json',best['metrics']);r.update(attempts=attempts,v2_status=status(best['metrics']),v2_metrics=best['metrics'],selected_candidate=best['candidate_id'],fix_type=best['fix_type'],v2_score=best['score'],numeric_serialization_repair=True);dump(rp,r)
 print(row['case_id'],'repaired',changed,flush=True);return changed

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['near','reject'],required=True);a=ap.parse_args();rows=[r for r in read(O/'manifests/cases.json') if r['v1_status']=={'near':'NEAR_PASS','reject':'REJECT'}[a.group]]
 with ProcessPoolExecutor(max_workers=8) as pool:counts=list(pool.map(repair,rows))
 dump(O/'integrity'/('NUMERIC_REPAIR_'+a.group+'.json'),{'case_n':len(rows),'affected_case_n':sum(n>0 for n in counts),'repaired_candidate_n':sum(counts),'parameters_and_candidate_ids_unchanged':True,'original_failure_records_retained':True})
 print('REPAIR_COMPLETE',a.group,sum(counts),flush=True)
