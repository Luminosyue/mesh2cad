import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json,sys,hashlib,subprocess,shutil,traceback,argparse,ast,datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np,trimesh
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
from fit_logic import basis_for_axis,projected_profile
from historical_fit import section_loft_profile
from metric_runtime import evaluate,plane
from cad_emit import emit_profiles,emit_loft,score
O=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False))
def generate(m,features,plan):
 rows=[];errors=[]
 ev=features['axis_evidence'];axis_order=[features['best_radial_axis_index']]+[i for i in range(len(ev)) if i!=features['best_radial_axis_index']]
 def add(kind,code,params):
  if len(rows)<8 and code not in [r['code'] for r in rows]:rows.append({'kind':kind,'code':code,'parameters':params})
 def primitive(kind,i):
  a=ev[i];B=np.array(a['basis']);lo=np.array(a['lo']);hi=np.array(a['hi']);ext=hi-lo
  if kind=='box':
   origin=B@((lo+hi)/2);code='import cadquery as cq\nplane = '+plane(origin,B)+'\nresult = cq.Workplane(plane).box('+','.join(map(repr,ext.tolist()))+')\n';params={'extents':ext.tolist(),'origin':origin.tolist()}
  else:
   xy=np.array(a['circle_center']);origin=B@np.r_[xy,lo[2]];radius=float(a['radius_median']);height=float(ext[2]);code='import cadquery as cq\nplane = '+plane(origin,B)+f'\nresult = cq.Workplane(plane).circle({radius!r}).extrude({height!r})\n';params={'radius':radius,'height':height,'origin':origin.tolist()}
  add(kind,code,params)
 def extrusion(i):
  spec=projected_profile(m,np.array(ev[i]['axis']),96);add('extrusion_with_cuts' if any(p['holes'] for p in spec['profiles']) else 'extrusion',emit_profiles(spec),spec)
 def revolve(i):
  a=ev[i];B=np.array(a['basis']);q=np.asarray(m.vertices)@B;xy=np.array(a['circle_center']);rad=np.linalg.norm(q[:,:2]-xy,axis=1);z=q[:,2];lo=float(z.min());hi=float(z.max());cuts=np.linspace(lo,hi,13);profile=[]
  for j in range(12):
   mask=(z>=cuts[j])&(z<=cuts[j+1])
   if mask.sum()<3:continue
   profile.append([float(np.quantile(rad[mask],.98)),float((cuts[j]+cuts[j+1])/2)])
  if len(profile)<4:raise ValueError('radial profile lacks >=4 supported bins')
  profile[0][1]=lo;profile[-1][1]=hi;poly=[[0.,lo]]+profile+[[0.,hi]]
  origin=B@np.r_[xy,0.];rp=np.column_stack([B[:,0],B[:,2],-B[:,1]])
  code='import cadquery as cq\nplane = '+plane(origin,rp)+f'\nresult = cq.Workplane(plane).polyline({poly!r}).close().revolve(360, (0,0), (0,1))\n'
  add('revolve',code,{'profile':poly,'axis':a['axis'],'circle_center':xy.tolist(),'radial_relative_mad':a['radial_relative_mad']})
 def loft(i):
  spec=section_loft_profile(m,np.array(ev[i]['axis']),True,section_count=6,points_per_loop=12);add('section_loft',emit_loft(spec),spec)
 def multi(i):
  components=sorted(m.split(only_watertight=False),key=lambda x:-x.area)
  if not 2<=len(components)<=7:raise ValueError('component count outside 2..7 budget')
  lines=['import cadquery as cq'];specs=[]
  for j,comp in enumerate(components):
   spec=projected_profile(comp,np.array(ev[i]['axis']),24)
   if len(spec['profiles'])!=1 or spec['profiles'][0]['holes']:raise ValueError('complex component sketch')
   B=np.array(spec['basis']);h=spec['zmax']-spec['zmin'];origin=np.array(spec['center'])+B[:,2]*spec['zmin'];pts=spec['profiles'][0]['outer']
   if h<1e-5:raise ValueError('unobserved component thickness; no thin-sheet fabrication in this factory')
   lines.extend([f'plane{j} = '+plane(origin,B),f'p{j} = cq.Workplane(plane{j}).polyline({pts!r}).close().extrude({h!r})']);specs.append(spec)
  if sum(len(s['profiles'][0]['outer']) for s in specs)>96:raise ValueError('assembly sketch budget')
  lines.append('result = p0'+''.join(f'.union(p{j})' for j in range(1,len(specs))));add('multi_primitive','\n'.join(lines)+'\n',{'components':specs})
 family=plan['cad_family'];primary=axis_order[0] if family=='C_REVOLVE' else 0
 jobs=[]
 if family=='C_REVOLVE':jobs=[('revolve',axis_order[0]),('cylinder',axis_order[0]),('revolve',axis_order[1] if len(axis_order)>1 else 0)]
 elif family in ['F_MULTI_PRIMITIVE','G_FRAME_OR_BEAM_STRUCTURE','E_BOOLEAN_COMPOSITION']:jobs=[('multi',0),('extrusion',0),('extrusion',1)]
 else:jobs=[('extrusion',0),('extrusion',1),('loft',0)]
 jobs += [('loft',primary),('extrusion',2),('cylinder',axis_order[0]),('box',0),('extrusion',3),('loft',1),('revolve',axis_order[0])]
 seen=set()
 for kind,i in jobs:
  if len(rows)>=8:break
  if i>=len(ev) or (kind,i) in seen:continue
  seen.add((kind,i))
  try:
   if kind in ['box','cylinder']:primitive(kind,i)
   else:{'extrusion':extrusion,'revolve':revolve,'loft':loft,'multi':multi}[kind](i)
  except Exception as e:errors.append({'kind':kind,'axis_index':i,'reason':str(e)})
 return rows,errors
def runpart(item):
 object_id,part_id=item;d=O/'objects'/object_id/'parts'/part_id
 if (d/'result.json').exists():return json.loads((d/'result.json').read_text())
 features=json.loads((d/'features/features.json').read_text());plan=json.loads((d/'planner/plan.json').read_text());m=trimesh.load(features['local_mesh_path'],force='mesh',process=True)
 out={'object_id':object_id,'part_id':part_id,'source_part_sha256':features['part_mesh_sha256'],'size_class':features['size_class'],'cad_family':plan['cad_family'],
  'family_confidence':plan['family_confidence'],'family_reason':plan['family_reason'],'xpart_used':False,'xpart_reason':features['xpart_reason'],'status':'REJECT','attempts':[]}
 proposals,errors=generate(m,features,plan);out['generation_errors']=errors
 for i,p in enumerate(proposals):
  a=d/'candidates'/f'candidate_{i:02d}';a.mkdir(exist_ok=False);(a/'cad.py').write_text(p['code']);dump(a/'parameters.json',p['parameters']);r={'index':i,'kind':p['kind'],'path':str(a)}
  try:
   process=subprocess.run([sys.executable,'-B',str(O/'scripts/execute_candidate.py'),str(a/'cad.py'),str(a/'execution')],capture_output=True,text=True,timeout=120,env=os.environ.copy())
   (a/'execution.log').write_text(process.stdout+'\n'+process.stderr);ex=json.loads((a/'execution/execution.json').read_text());r['execution']=ex
   if ex.get('tessellation_pass'):
    cm=trimesh.load(a/'execution/cad_mesh_from_reloaded_step.ply',force='mesh',process=True);seed=20261006+int(object_id.split('_')[-1])*1000+int(part_id.split('_')[-1])*10
    met=evaluate(m,cm,seed);met.update(source_part_sha256=features['part_mesh_sha256'],normalized_mesh_sha256=sha(features['local_mesh_path']),step_sha256=sha(a/'execution/cad.step'),cad_mesh_sha256=sha(a/'execution/cad_mesh_from_reloaded_step.ply'))
    r.update(metrics=met,score=score(met));dump(a/'metrics.json',met)
  except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
  out['attempts'].append(r);dump(a/'record.json',r)
  if r.get('metrics',{}).get('strict_pass') and len(out['attempts'])>=2:break
 valid=[x for x in out['attempts'] if x.get('metrics')]
 if valid:
  best=min(valid,key=lambda x:(not x['metrics']['strict_pass'],x['score']));met=best['metrics'];a=Path(best['path']);status='STRICT_ACCEPT' if met['strict_pass'] else 'NEAR_PASS' if met['iou']>=.70 and met['normalized_chamfer']<=.02 else 'REJECT'
  for src,dst in [('cad.py','cad/cad.py'),('parameters.json','cad/parameters.json'),('execution/cad.step','cad/cad.step'),('execution/execution.json','cad/reload_metadata.json'),('metrics.json','metrics/metrics.json')]:shutil.copyfile(a/src,d/dst)
  cm=trimesh.load(a/'execution/cad_mesh_from_reloaded_step.ply',force='mesh',process=True);cm.export(d/'cad/part_cad_mesh_from_step.obj');shutil.copyfile(a/'execution/cad_mesh_from_reloaded_step.ply',d/'cad/cad_mesh_from_reloaded_step.ply')
  out.update(status=status,metrics=met,best_candidate_id=best['index'],best_kind=best['kind'],step_path=str(d/'cad/cad.step'),cad_program_path=str(d/'cad/cad.py'),cad_mesh_path=str(d/'cad/cad_mesh_from_reloaded_step.ply'),failure_reason=None if status=='STRICT_ACCEPT' else 'GEOMETRY_MISMATCH')
 else:out.update(failure_reason='CAD_EXECUTION_FAILURE' if proposals else 'CAD_TOO_COMPLEX')
 out['candidate_n']=len(out['attempts']);dump(d/'result.json',out);print(json.dumps({'object':object_id,'part':part_id,'status':out['status'],'iou':out.get('metrics',{}).get('iou'),'kind':out.get('best_kind')}),flush=True);return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,required=True);a=ap.parse_args();items=[]
 for obj in json.loads((O/'manifests/objects_frozen.json').read_text())[:a.limit]:
  for p in (O/'objects'/obj['object_id']/'parts').glob('*/planner/plan.json'):items.append((obj['object_id'],p.parents[1].name))
 workers=min(12,max(1,int(os.environ.get('P3_CAD_WORKERS','4'))))
 with ProcessPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(runpart,sorted(items)))
 print('PART_STAGE_COMPLETE',a.limit,len(rows),flush=True)
