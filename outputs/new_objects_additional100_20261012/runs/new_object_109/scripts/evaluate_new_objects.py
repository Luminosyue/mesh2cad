import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import sys,json,hashlib,concurrent.futures,traceback
import numpy as np,trimesh,cadquery as cq
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_additional100_20261012/runs/new_object_109')
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_fitting_v2_native/scripts')
from metric_runtime import evaluate
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(mesh,reference):
 m=mesh.copy();m.apply_translation(-reference.bounds.mean(0));m.apply_scale(1/max(reference.extents));return m
def mesh_shape(shape,tol):
 v,f=shape.tessellate(tol,.1);return trimesh.Trimesh([x.toTuple() for x in v],f,process=True)
def part_job(item):
 obj,part=item;oid=obj['object_id'];pid=part['part_id'];number=int(pid.split('_')[-1]);upper=f'PART_{number:03d}';d=O/'objects'/oid;fit=d/'xpart_parts_cadquery_features'/upper;out=fit/'current_protocol_metrics.json'
 if out.exists():return json.loads(out.read_text())
 r={'object_id':oid,'part_id':pid,'size_class':part['size_class'],'p3_label':part['p3_label'],'source_part_path':part['part_mesh_path'],'source_part_sha256':part['part_mesh_sha256'],'xpart_reexecuted':True}
 try:
  step=fit/(upper+'.step');r['cad_generated']=step.is_file()
  if not step.is_file():raise ValueError('NO_VALID_CAD')
  src=trimesh.load(part['part_mesh_path'],force='mesh',process=True);assert sha(Path(part['part_mesh_path']))==part['part_mesh_sha256']
  xp=next((d/'xpart_parts'/upper).glob('complete*.obj'));complete=trimesh.load(xp,force='mesh',process=True)
  shape=cq.importers.importStep(str(step)).val();assert shape.isValid() and len(shape.Solids())>0
  cad=mesh_shape(shape,float(max(complete.extents))*.00025);cad.export(fit/'cad_evaluation_mesh.ply')
  seed=20261011+int(oid.split('_')[-1])*10000+number*10
  a=evaluate(normalize(complete,complete),normalize(cad,complete),seed)
  c=evaluate(normalize(src,src),normalize(cad,src),seed)
  drift=evaluate(normalize(src,src),normalize(complete,src),seed)
  drift['evaluation_source']='XPART_COMPLETION_MESH'
  params=json.loads((fit/'parameters.json').read_text());r.update(step_path=str(step),cad_program_path=str(fit/(upper+'.py')),step_sha256=sha(step),xpart_mesh_path=str(xp),xpart_sha256=sha(xp),original_watertight=bool(src.is_watertight),completed_watertight=bool(complete.is_watertight),step_reload_pass=True,solid_count=len(shape.Solids()),face_count=len(shape.Faces()),cad_vs_completed=a,cad_vs_original=c,completion_vs_original=drift,method=params['operation'],section_count=params.get('section_count'),feature_count=len(params.get('features',[])),profile_point_count=sum(len(q) for f in params.get('features',[]) for z,q in f.get('sections',[])),strict_against_completed=a['strict_pass'],strict_against_original=c['strict_pass'])
  r['status']='STRICT_ORIGINAL' if c['strict_pass'] else 'STRICT_COMPLETED_ONLY' if a['strict_pass'] else 'GEOMETRY_REJECT'
 except Exception as e:r.update(status='FAILED',error=str(e),traceback=traceback.format_exc())
 dump(out,r);print(json.dumps({'object':oid,'part':pid,'status':r['status'],'iou_completed':r.get('cad_vs_completed',{}).get('iou'),'iou_original':r.get('cad_vs_original',{}).get('iou')}),flush=True);return r
def main():
 objects=json.loads((O/'manifests/objects_frozen.json').read_text());items=[]
 for obj in objects:
  pm=json.loads((O/'objects'/obj['object_id']/'p3/parts_manifest.json').read_text());items.extend((obj,p) for p in pm['parts'])
 with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:parts=list(pool.map(part_job,items))
 dump(O/'part_results.json',parts);object_rows=[]
 for obj in objects:
  oid=obj['object_id'];d=O/'objects'/oid;group=[p for p in parts if p['object_id']==oid];valid=[p for p in group if p.get('step_reload_pass')];src=trimesh.load(obj['canonical_path'],force='mesh',process=True);r={'object_id':oid,'name':obj['name'],'p3_part_count':len(group),'cad_valid_part_count':len(valid),'strict_original_part_count':sum(p.get('strict_against_original',False) for p in group),'strict_completed_part_count':sum(p.get('strict_against_completed',False) for p in group),'all_parts_present':len(valid)==len(group),'full_strict_original':len(valid)==len(group) and all(p.get('strict_against_original',False) for p in group),'assembly_type':'DIAGNOSTIC_ALL_VALID_CANDIDATES_NOT_STRICT_GT'}
  if valid:
   shapes=[cq.importers.importStep(p['step_path']).val() for p in valid];assembly=cq.Compound.makeCompound(shapes);dest=d/'assembly/diagnostic_canonical.step';assembly.exportStep(str(dest));loaded=cq.importers.importStep(str(dest)).val();assert loaded.isValid();cad=mesh_shape(loaded,.0005);cad.export(d/'assembly/diagnostic_canonical.ply');r['geometry']=evaluate(src,cad,20261011+int(oid.split('_')[-1]));T=np.array(obj['inverse_object_transform']);world=loaded.scale(float(T[0,0])).translate(tuple(T[:3,3]));world.exportStep(str(d/'assembly/diagnostic_original_coordinates.step'));r['step_path']=str(dest)
  object_rows.append(r);dump(d/'assembly/result.json',r)
 summary={'status':'NEW_DATA_EVALUATION_COMPLETE','objects':object_rows,'object_n':len(objects),'p3_part_n':len(parts),'cad_valid_n':sum(p.get('step_reload_pass',False) for p in parts),'strict_original_n':sum(p.get('strict_against_original',False) for p in parts),'strict_completed_n':sum(p.get('strict_against_completed',False) for p in parts),'full_strict_original_object_n':sum(r['full_strict_original'] for r in object_rows),'scope':'Three new source objects excluded by hash from the two previous 20-object batches. P3 and XPart rerun; no reuse of old case CAD.','pair_semantics':'CAD versus completed mesh and CAD versus original mesh reported separately; no original design GT claimed.'}
 dump(O/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
