import sys,json,subprocess,shutil,time
from pathlib import Path
import numpy as np
import trimesh
import cadquery as cq
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad')
import pilot_repaired as base
OLD=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v1'); OUT.mkdir(parents=True,exist_ok=True)
ENV=base.ENV.copy(); ENV.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
def load(p):
 m=trimesh.load(p,force='mesh',process=False)
 if isinstance(m,trimesh.Scene):m=m.to_mesh()
 m.merge_vertices();m.remove_unreferenced_vertices();return m
def code(pr):
 return '''import cadquery as cq
from pathlib import Path
def build_model():
 sections=%r; origin=%r; xdir=%r; normal=%r; wires=[]
 for sec in sections:
  plane=cq.Plane(origin=tuple(origin[i]+normal[i]*sec["z"] for i in range(3)),xDir=tuple(xdir),normal=tuple(normal))
  pts=[tuple(p) for p in sec["points"]]
  wires.append(cq.Workplane(plane).spline(pts,periodic=True).close().val())
 return cq.Workplane(obj=cq.Solid.makeLoft(wires,False))
if __name__=="__main__":
 body=build_model(); out=Path(__file__).parent
 cq.exporters.export(body,str(out/"reconstructed.step")); cq.exporters.export(body,str(out/"reconstructed.stl"),tolerance=1e-5,angularTolerance=.1)
 print({"valid":body.val().isValid(),"faces":len(body.val().Faces())})
'''%(pr['sections'],pr['origin'],pr['xdir'],pr['normal'])
def main():
 rs=[]
 for old in sorted((OLD/'cases/airplane').iterdir()):
  mp=old/'metrics.json'; pp=old/'parameters.json'
  if not mp.exists() or not pp.exists():continue
  d=json.loads(mp.read_text())
  if '/xpart_parts/' not in d.get('source_path',''):continue
  od=OUT/'cases/airplane'/old.name;od.mkdir(parents=True,exist_ok=True);shutil.copy2(old/'source.stl',od/'source.stl')
  pr=json.loads(pp.read_text());(od/'parameters.json').write_text(json.dumps(pr,indent=2));(od/'cad.py').write_text(code(pr))
  t=time.time()
  try:
   run=subprocess.run([sys.executable,'cad.py'],cwd=od,env=ENV,capture_output=True,text=True,timeout=900)
  except Exception as exc:
   print('RUN_ERROR',old.name,str(exc),flush=True)
   run=None
  status='SMOOTH_BSPLINE' if run is not None and run.returncode==0 and (od/'reconstructed.step').exists() else 'FAILED'
  if status=='FAILED':
   shutil.copy2(old/'reconstructed.step',od/'reconstructed.step');shutil.copy2(old/'reconstructed.stl',od/'reconstructed.stl')
  m=load(od/'source.stl');cm=load(od/'reconstructed.stl');mm=base.metrics(m,cm,high=True)
  sh=cq.importers.importStep(str(od/'reconstructed.step')).val();faces=len(sh.Faces());valid=bool(sh.isValid()) and len(sh.Solids())==1
  r={'case_id':'airplane','part_id':old.name,'source_path':d['source_path'],'geometry_family':status,'smooth_surface':status=='SMOOTH_BSPLINE','runtime_sec':time.time()-t,'brep_valid':valid,'step_reload':True,'cad_brep_face_count':faces,'valid_training_pair':bool(status=='SMOOTH_BSPLINE' and valid and mm['iou128']>=.8),**mm}
  (od/'metrics.json').write_text(json.dumps(r,indent=2));rs.append(r);print(old.name,status,'iou',round(mm['iou128'],5),'faces',faces,'time',round(time.time()-t,1),flush=True)
 (OUT/'summary_airplane.json').write_text(json.dumps({'total':len(rs),'smooth':sum(r['smooth_surface'] for r in rs),'failed':sum(not r['smooth_surface'] for r in rs),'iou128_mean':float(np.mean([r['iou128'] for r in rs]))},indent=2))
 (OUT/'all_results.json').write_text(json.dumps(rs,indent=2));print('DONE',len(rs))
if __name__=='__main__':main()






