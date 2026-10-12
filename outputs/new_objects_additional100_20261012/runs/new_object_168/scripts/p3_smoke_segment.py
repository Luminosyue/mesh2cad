import os,sys
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']=os.environ['BATCH_GPU'];os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_additional100_20261012/runs/new_object_168')
os.environ['NUMBA_CACHE_DIR']=str(O/'cache/numba');os.environ['TORCH_EXTENSIONS_DIR']=str(O/'cache/torch_extensions')
sys.path[:0]=[str(O/'runtime/p3'),str(O/'runtime/p3/demo')]
import json,argparse,time,hashlib,traceback
import numpy as np,trimesh
from auto_mask import AutoMask,set_seed,Timer
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False))
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,choices=[3,5,20],required=True);a=ap.parse_args()
cfg=json.loads((O/'config/smoke20.json').read_text());rows=json.loads((O/'manifests/objects_frozen.json').read_text())[:a.limit]
model=AutoMask('/data/home/cuiyuehan/project/mesh2cad/Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors');Timer.STATE=False
for r in rows:
 d=O/'objects'/r['object_id'];p=d/'p3';status=p/'segmentation.json'
 if status.exists():continue
 start=time.time();set_seed(cfg['seed'])
 try:
  m=trimesh.load(r['canonical_path'],force='mesh',process=True);before_v=m.vertices.copy();before_f=m.faces.copy()
  boxes,labels,returned=model.predict_aabb(m,point_num=50000,prompt_num=201,threshold=.95,post_process=False,save_path=str(p),save_mid_res=False,show_info=False,clean_mesh_flag=False,seed=cfg['seed'],is_parallel=False,prompt_bs=4)
  if not np.array_equal(returned.faces,before_f) or not np.array_equal(returned.vertices,before_v):raise RuntimeError('P3 mutated source topology/coordinates')
  np.save(p/'face_labels.npy',labels);np.save(p/'boxes.npy',np.asarray(boxes));parts=[];area=float(m.area);objvol=float(np.prod(m.extents))
  for j,label in enumerate(np.unique(labels)):
   ids=np.flatnonzero(labels==label);part=m.submesh([ids],append=True,repair=False);pid=f'part_{j:03d}';part.export(p/(pid+'.ply'));path=p/(pid+'.ply')
   c=part.bounds.mean(0);s=float(max(part.extents));T=np.eye(4);T[:3,:3]/=max(s,1e-12);T[:3,3]=-c/max(s,1e-12);Ti=np.linalg.inv(T)
   af=float(part.area/area);vf=float(np.prod(part.extents)/max(objvol,1e-15));micro=af<.0002 and vf<.00001 and len(ids)<50;major=not micro and (af>=.02 or vf>=.01)
   counts=np.bincount(part.edges_unique_inverse);finite=bool(np.isfinite(part.vertices).all());quality='DEGENERATE' if not finite or part.area<=1e-15 or s<=1e-12 else 'TOO_SMALL' if micro else 'GOOD'
   rec={'part_id':pid,'parent_object_id':r['object_id'],'p3_label':int(label),'unassigned_label':bool(label<0),'part_mesh_path':str(path),'part_mesh_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'local_transform':T.tolist(),'world_transform':Ti.tolist(),'inverse_transform':T.tolist(),'local_to_original_object':(np.asarray(r['inverse_object_transform'])@Ti).tolist(),
    'bbox':part.bounds.tolist(),'centroid':part.centroid.tolist(),'vertex_count':len(part.vertices),'face_count':len(part.faces),'finite_coordinates':finite,'connected_components':len(part.split(only_watertight=False)),
    'watertight':bool(part.is_watertight),'boundary_edges':int(np.sum(counts==1)),'surface_area':float(part.area),'volume_if_available':float(abs(part.volume)) if part.is_volume else None,
    'area_fraction':af,'bbox_volume_fraction':vf,'size_class':'MICRO_PART' if micro else 'MAJOR_PART' if major else 'MINOR_PART','part_quality':quality,'xpart_used':False,'xpart_reason':'No independent major missing-surface evidence; boundary alone is not incompleteness',
    'source_face_indices_path':str(p/(pid+'_face_indices.npy'))}
   np.save(p/(pid+'_face_indices.npy'),ids);parts.append(rec)
  coverage=sum(x['face_count'] for x in parts)==len(m.faces);success=len([x for x in parts if not x['unassigned_label']])>=2 and coverage
  dump(p/'parts_manifest.json',{'object_id':r['object_id'],'p3_used':True,'p3_version':'local P3-SAM checkpoint SHA recorded in integrity; copied model initialization patch','part_count':len(parts),'face_coverage_complete':coverage,'parts':parts})
  dump(status,{'success':success,'part_count':len(parts),'assigned_part_count':sum(not x['unassigned_label'] for x in parts),'unassigned_face_count':int(np.sum(labels<0)),'elapsed_seconds':time.time()-start,'source_topology_preserved':True})
  print(json.dumps({'object':r['object_id'],'p3_success':success,'parts':len(parts),'seconds':time.time()-start}),flush=True)
 except Exception as e:dump(status,{'success':False,'error':str(e),'traceback':traceback.format_exc()});print('FAILED',r['object_id'],str(e),flush=True)
