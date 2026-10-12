import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys,json,ast,argparse,hashlib,traceback
from pathlib import Path
import numpy as np,trimesh,cadquery as cq
from metric_runtime import evaluate
O=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False))
def tess(shape,tol,ang):
 v,f=shape.tessellate(tol,ang);return trimesh.Trimesh([x.toTuple() for x in v],f,process=True)
def exact(shape,eval_mesh,d):
 d.mkdir(exist_ok=True);m=tess(shape,.0002,.02);refined=False
 if len(m.faces)<=len(eval_mesh.faces):
  v,f=trimesh.remesh.subdivide(m.vertices,m.faces);m=trimesh.Trimesh(v,f,process=False);refined=True
 m.export(d/'mesh_high.obj')
 meta={'linear_deflection':.0002,'angular_deflection':.02,'triangle_count':len(m.faces),'evaluation_triangle_count':len(eval_mesh.faces),'higher_triangle_count':len(m.faces)>len(eval_mesh.faces),
  'extra_mesh_refinement':refined,'refinement_note':'If stricter OCC tessellation retained the same facet count, subdivide its triangles once; this adds samples, not CAD design detail.',
  'pair_type':'CAD_DERIVED_EXACT','geometry_source':'same reloaded CAD; tessellation is a tolerance-bounded mesh, not exact analytic surface','mesh_path':str(d/'mesh_high.obj'),'mesh_sha256':sha(d/'mesh_high.obj')}
 dump(d/'tessellation.json',meta);return meta
class Rename(ast.NodeTransformer):
 def __init__(self,prefix):self.prefix=prefix
 def visit_Name(self,node):return ast.copy_location(ast.Name(id=node.id if node.id=='cq' else self.prefix+node.id,ctx=node.ctx),node)
def assembly_code(parts,original=False):
 chunks=['import cadquery as cq'];items=[]
 for i,(p,r) in enumerate(parts):
  tree=ast.parse(Path(r['cad_program_path']).read_text());tree.body=[n for n in tree.body if not isinstance(n,ast.Import)];tree=Rename(f'p{i}_').visit(tree);ast.fix_missing_locations(tree);chunks.append(ast.unparse(tree))
  T=np.asarray(p['local_to_original_object'] if original else p['world_transform']);s=float(T[0,0]);translation=T[:3,3].tolist()
  items.append(f'p{i}_result.val().scale({s!r}).translate({translation!r})')
 chunks.append('assembly_shape = cq.Compound.makeCompound(['+', '.join(items)+'])');chunks.append('result = cq.Workplane("XY").newObject([assembly_shape])');return '\n'.join(chunks)+'\n'
def process(obj):
 d=O/'objects'/obj['object_id'];dest=d/'assembly';out={'object_id':obj['object_id'],'status':'ASSEMBLY_FAIL','accepted_part_n':0,'metrics':{},'pair_types_separated':True}
 pm=json.loads((d/'p3/parts_manifest.json').read_text());parts=pm['parts'];accepted=[];missing=[];trans_err=[]
 for p in parts:
  rec=d/'parts'/p['part_id']/'result.json'
  if rec.exists():
   r=json.loads(rec.read_text())
   if r['status']=='STRICT_ACCEPT':accepted.append((p,r))
   elif p['size_class']=='MAJOR_PART':missing.append(p['part_id'])
  elif p['size_class']=='MAJOR_PART':missing.append(p['part_id'])
  T=np.asarray(p['local_transform']);Ti=np.asarray(p['world_transform']);trans_err.append(float(np.max(np.abs(T@Ti-np.eye(4)))))
 out.update(accepted_part_n=len(accepted),total_part_n=len(parts),major_part_n=sum(p['size_class']=='MAJOR_PART' for p in parts),missing_major_parts=missing,max_transform_roundtrip_error=max(trans_err,default=0.))
 if not accepted:dump(dest/'assembly_metrics.json',out);return out
 try:
  for p,r in accepted:
   pd=d/'parts'/p['part_id'];shape=cq.importers.importStep(r['step_path']).val();em=trimesh.load(r['cad_mesh_path'],force='mesh',process=True)
   exact_meta=exact(shape,em,d/'exact_pairs'/p['part_id']);exact_meta.update(object_id=obj['object_id'],part_id=p['part_id'],cad_program_path=r['cad_program_path'],step_path=r['step_path'],step_sha256=sha(r['step_path']))
   dump(d/'exact_pairs'/p['part_id']/'pair.json',exact_meta)
   dump(d/'pseudo_pairs'/(p['part_id']+'.json'),{'pair_type':'REALISTIC_MESH_PSEUDO_CAD','object_id':obj['object_id'],'part_id':p['part_id'],'original_part_mesh':p['part_mesh_path'],'part_mesh_sha256':p['part_mesh_sha256'],'cad_program_path':r['cad_program_path'],'step_path':r['step_path'],'local_transform':p['local_transform'],'world_transform':p['world_transform'],'metrics':r['metrics'],'original_design_GT':False})
  code=assembly_code(accepted);(dest/'assembly.py').write_text(code);scope={};exec(compile(code,str(dest/'assembly.py'),'exec'),scope);shape=scope['result'].val()
  if not shape.isValid():raise ValueError('Invalid assembly compound')
  cq.exporters.export(shape,str(dest/'assembly.step'));loaded=cq.importers.importStep(str(dest/'assembly.step')).val()
  if not loaded.isValid() or len(loaded.Solids())!=sum(len(cq.importers.importStep(r['step_path']).val().Solids()) for p,r in accepted):raise ValueError('Assembly STEP component count mismatch')
  mesh=tess(loaded,.001,.05);mesh.export(dest/'assembly_mesh.obj');src=trimesh.load(obj['canonical_path'],force='mesh',process=True);metrics=evaluate(src,mesh,20261006+int(obj['object_id'].split('_')[-1]))
  Ti=np.array(obj['inverse_object_transform']);world=loaded.scale(float(Ti[0,0])).translate(Ti[:3,3].tolist());cq.exporters.export(world,str(dest/'object_reconstructed.step'));wreload=cq.importers.importStep(str(dest/'object_reconstructed.step')).val();wm=tess(wreload,.001*float(Ti[0,0]),.05);wm.export(dest/'object_reconstructed_mesh.obj')
  (dest/'object_reconstructed.py').write_text(assembly_code(accepted,True))
  full=not missing and out['major_part_n']>0;out.update(status='FULL_STRICT_ASSEMBLY' if full else 'PARTIAL_ASSEMBLY',metrics=metrics,step_path=str(dest/'assembly.step'),step_sha256=sha(dest/'assembly.step'),original_coordinate_step=str(dest/'object_reconstructed.step'),
   assembly_mesh_path=str(dest/'assembly_mesh.obj'),step_reload_pass=True,solid_count=len(loaded.Solids()),face_count=len(loaded.Faces()),edge_count=len(loaded.Edges()),accepted_part_ids=[p['part_id'] for p,r in accepted],
   accepted_surface_area_fraction=sum(p['area_fraction'] for p,r in accepted),partial_note='Any accepted subset is exported; missing major parts explicitly listed. Partial does not imply most of object recovered.')
  emeta=exact(loaded,mesh,d/'exact_pairs/object');emeta.update(object_id=obj['object_id'],cad_program_path=str(dest/'assembly.py'),step_path=str(dest/'assembly.step'),assembly_status=out['status']);dump(d/'exact_pairs/object/pair.json',emeta)
  if full:
   dump(d/'pseudo_pairs/object.json',{'pair_type':'REALISTIC_MESH_PSEUDO_CAD','object_id':obj['object_id'],'source_mesh':obj['source_object_path'],'source_sha256':obj['source_object_sha256'],'cad_program_path':str(dest/'object_reconstructed.py'),'step_path':str(dest/'object_reconstructed.step'),'metrics':metrics,'original_design_GT':False,'full_major_parts':True})
 except Exception as e:out.update(status='ASSEMBLY_FAIL',error=str(e),traceback=traceback.format_exc())
 dump(dest/'assembly_metrics.json',out);print(json.dumps({'object':obj['object_id'],'assembly':out['status'],'accepted_parts':len(accepted),'iou':out['metrics'].get('iou')}),flush=True);return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,required=True);a=ap.parse_args()
 for obj in json.loads((O/'manifests/objects_frozen.json').read_text())[:a.limit]:
  result=O/'objects'/obj['object_id']/'assembly/assembly_metrics.json'
  manifest=O/'objects'/obj['object_id']/'p3/parts_manifest.json'
  if not manifest.exists():continue
  pending=[p['part_id'] for p in json.loads(manifest.read_text())['parts'] if p['size_class']!='MICRO_PART' and p['part_quality']!='DEGENERATE' and not (O/'objects'/obj['object_id']/'parts'/p['part_id']/'result.json').exists()]
  if pending:
   print('ASSEMBLY_PENDING',obj['object_id'],len(pending),flush=True);continue
  if not result.exists():process(obj)
