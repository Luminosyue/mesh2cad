import pathlib,json,sys,ast,subprocess,os,hashlib
import numpy as np
from fusion_units_probe import R,save
O=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v2'
def main():
 inv=json.loads((O/'fusion_inventory.json').read_text());errors=[];count=0
 for r in inv:
  d=O/'samples'/r['cad_id'];p=pathlib.Path(r['pack']);c=json.loads((d/'unit_contract.json').read_text());tf=json.loads((d/'coordinate_transform.json').read_text())
  xyz=np.load(p/'surface_points_source.npy');old=np.load(p/'surface_points.npy');new=np.load(d/'surface_points.npy')
  expected=old.copy();expected[:,:3]=xyz*tf['scale']+np.array(tf['translation'])
  checks=dict(surface_array_exact=np.array_equal(new,expected),normals_bitwise_unchanged=np.array_equal(new[:,3:],old[:,3:]),row_count=new.shape==(8192,6),shared_scale=c['source_to_canonical_scale']==c['dsl_to_canonical_scale']==tf['scale'],canonical_diag_6=abs(tf['source_diagonal']*tf['scale']-6)<1e-12)
  oldtree=ast.parse((d/'cad_target_before_units.dsl').read_text());newtree=ast.parse((d/'cad_target_mm.dsl').read_text())
  def preserved(t):
   return [(n.func.id,[(k.arg,ast.dump(k.value)) for k in n.keywords if k.arg in ('axis','normal','x_axis','y_axis','symmetric')]) for n in ast.walk(t) if isinstance(n,ast.Call)]
  checks['op_order_and_directions_identical']=preserved(oldtree)==preserved(newtree)
  if not all(checks.values()):errors.append(dict(cad_id=r['cad_id'],checks=checks))
  count+=1
 env=os.environ.copy();env['PYTHONPATH']=str(R/'scripts');env['PYTHONDONTWRITEBYTECODE']='1';env['CUDA_VISIBLE_DEVICES']=''
 test=pathlib.Path(__file__).parent/'test_fusion_unit_contract.py';proc=subprocess.run([sys.executable,'-B',str(test)],capture_output=True,text=True,env=env)
 with (O/'UNIT_TESTS.log').open('x') as f:f.write(proc.stdout+proc.stderr)
 save(O/'IMPLEMENTATION_VALIDATION.json',dict(samples_checked=count,errors=errors,passed=not errors and proc.returncode==0,unit_test_returncode=proc.returncode,unit_tests=4,scope='Dimensional conversion and shared source-STEP-to-canonical surface/DSL transform only; not a model token budget or practical curves validation'))
 print(json.dumps(dict(samples_checked=count,errors=errors,unit_test_returncode=proc.returncode)))
if __name__=='__main__':main()
