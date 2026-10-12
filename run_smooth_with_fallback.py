import os,sys,json,subprocess,shutil
from pathlib import Path
import numpy as np
import trimesh
import cadquery as cq
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad')
import pilot_repaired as base
OLD=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1'); OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_nurbs_air_tank_v1'); OUT.mkdir(parents=True,exist_ok=True)
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
 for si,sec in enumerate(sections):
  if si %% 3 != 0 and si not in (0,len(sections)-1): continue
  plane=cq.Plane(origin=tuple(origin[i]+normal[i]*sec["z"] for i in range(3)),xDir=tuple(xdir),normal=tuple(normal))
  pts=[tuple(p) for p in sec["points"]][::4]
  wires.append(cq.Workplane(plane).spline(pts,periodic=True).close().val())
 return cq.Workplane(obj=cq.Solid.makeLoft(wires,False))
if __name__=="__main__":
 body=build_model(); out=Path(__file__).parent
 cq.exporters.export(body,str(out/"reconstructed.step")); cq.exporters.export(body,str(out/"reconstructed.stl"),tolerance=1e-5,angularTolerance=.1)
 print({"valid":body.val().isValid(),"faces":len(body.faces())})
'''%(pr['sections'],pr['origin'],pr['xdir'],pr['normal'])
def main():
 results=[]
 for case in ('airplane','tank'):
  for old in sorted((OLD/'cases'/case).iterdir()):
   mp=old/'metrics.json'; pp=old/'parameters.json'
   if not mp.exists() or not pp.exists(): continue
   d=json.loads(mp.read_text())
   if '/xpart_parts/' not in d.get('source_path',''): continue
   od=OUT/'cases'/case/old.name;od.mkdir(parents=True,exist_ok=True)
   shutil.copy2(old/'source.stl',od/'source.stl'); pr=json.loads(pp.read_text())
   status='SMOOTH_BSPLINE'
   try:
    (od/'cad.py').write_text(code(pr)); run=subprocess.run([sys.executable,'cad.py'],cwd=od,env=ENV,capture_output=True,text=True,timeout=45)
    if run.returncode!=0 or not (od/'reconstructed.step').exists(): raise RuntimeError(run.stderr[-400:])
   except Exception as e:
    status='FALLBACK_POLYGON'; shutil.copy2(old/'reconstructed.step',od/'reconstructed.step'); shutil.copy2(old/'reconstructed.stl',od/'reconstructed.stl'); shutil.copy2(old/'cad.py',od/'cad.py')
   m=load(od/'source.stl');cm=load(od/'reconstructed.stl');mm=base.metrics(m,cm,high=True)
   sh=cq.importers.importStep(str(od/'reconstructed.step')).val(); faces=len(sh.Faces());valid=bool(sh.isValid()) and len(sh.Solids())>=1
   q='A_HIGH_CONFIDENCE' if mm['iou128']>=.9 else ('B_USABLE' if mm['iou128']>=.8 else ('C_NEAR_MISS' if mm['iou128']>=.65 else 'D_REJECT'))
   r={'case_id':case,'part_id':old.name,'source_path':d['source_path'],'geometry_family':status,'cad_program_exec':'PASS','brep_valid':valid,'step_reload':True,'smooth_surface':status=='SMOOTH_BSPLINE','cad_brep_face_count':faces,'quality_level':q,'valid_training_pair':bool(valid and q in ('A_HIGH_CONFIDENCE','B_USABLE')),'failure_reason':'' if status=='SMOOTH_BSPLINE' else 'SMOOTH_FALLBACK',**mm}
   (od/'metrics.json').write_text(json.dumps(r,indent=2)); results.append(r); print(case,old.name,status,round(mm['iou128'],4),flush=True)
 for case in ('airplane','tank'):
  rs=[r for r in results if r['case_id']==case]; (OUT/f'summary_{case}.json').write_text(json.dumps({'case':case,'total':len(rs),'smooth':sum(r['smooth_surface'] for r in rs),'fallback':sum(not r['smooth_surface'] for r in rs),'valid_pairs':sum(r['valid_training_pair'] for r in rs),'iou128_mean':float(np.mean([r['iou128'] for r in rs]))},indent=2))
 (OUT/'all_results.json').write_text(json.dumps(results,indent=2))
 print('DONE',len(results))
if __name__=='__main__':main()

