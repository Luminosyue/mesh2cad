import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import pathlib,json,hashlib,shutil,ast,datetime
import numpy as np,trimesh
P=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');O=P/'outputs/p3_high_detail_mesh2cad_factory_v1_smoke20'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((O/'manifests/source_candidates.json').read_text());out=[];protected={}
for i,r in enumerate(rows):
 p=pathlib.Path(r['path']);m=trimesh.load(p,force='mesh',process=True);cid=f'object_{i:05d}';d=O/'objects'/cid
 for x in ['source','p3','parts','assembly','exact_pairs','pseudo_pairs','logs']:(d/x).mkdir(parents=True,exist_ok=False)
 shutil.copyfile(p,d/'source/object_mesh.obj')
 center=m.bounds.mean(0);span=float(max(m.extents));T=np.eye(4);T[:3,:3]/=span;T[:3,3]=-center/span
 n=m.copy();n.apply_transform(T);n.export(d/'source/object_canonical.ply')
 rec=dict(r,object_id=cid,source_dataset='existing_ours3_object_mesh_snapshot',source_object_path=str(p),source_object_sha256=sha(p),
  source_provenance_scope='Existing full object OBJ bytes and hash; original acquisition/design history not inferred',
  vertex_count=len(m.vertices),face_count=len(m.faces),surface_area=float(m.area),watertight=bool(m.is_watertight),
  bbox=m.bounds.tolist(),object_normalization={'method':'bbox midpoint; longest extent=1; orientation preserved','scale':1/span,'center':center.tolist()},
  object_transform=T.tolist(),inverse_object_transform=np.linalg.inv(T).tolist(),canonical_path=str(d/'source/object_canonical.ply'))
 (d/'source/provenance.json').write_text(json.dumps(rec,indent=2));out.append(rec);protected[str(p)]={'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns}
 print(json.dumps({'object':cid,'name':r['name'],'faces':len(m.faces),'vertices':len(m.vertices)}),flush=True)
assert len(out)==20 and all(r['face_count']>=1000 for r in out)
(O/'manifests/objects_frozen.json').write_text(json.dumps(out,indent=2))
for folder in ['outputs/mesh2cad_data_factory_v1_smoke100','outputs/mesh2cad_reconstruction_diagnosis_v1','outputs/mesh2cad_reconstruction_improvement_v1','outputs/mesh2cad_resmoke100_v2']:
 for p in (P/folder).rglob('*'):
  if p.is_file():protected[str(p)]={'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns}
for rel in ['Hunyuan3D-Part/P3-SAM/model.py','Hunyuan3D-Part/P3-SAM/demo/auto_mask.py','Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors','Hunyuan3D-Part/XPart/partgen/config/sonata.json']:
 p=P/rel;protected[str(p)]={'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns}
(O/'integrity/PROTECTED_BEFORE.json').write_text(json.dumps(protected))
prior=P/'outputs/mesh2cad_reconstruction_improvement_v1'
for src,dst in [('v1_runtime.py','metric_runtime.py'),('fit_logic.py','fit_logic.py'),('historical_fit.py','historical_fit.py'),('execute_v2.py','execute_candidate.py')]:shutil.copyfile(prior/'scripts'/src,O/'scripts'/dst)
shutil.copyfile(P/'outputs/mesh2cad_data_factory_v1_smoke100/config/factory_config.json',O/'config/factory_config.json')
raw=(prior/'scripts/reconstruct_v2.py').read_text();tree=ast.parse(raw);names={'emit_profiles','emit_loft','score'}
(O/'scripts/cad_emit.py').write_text('import numpy as np\nfrom metric_runtime import plane\n\n'+'\n\n'.join(ast.get_source_segment(raw,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names))
cfg={'seed':20261006,'object_n':20,'p3':{'point_num':50000,'prompt_num':201,'prompt_batch':4,'threshold':.95,'post_process':False,'clean_mesh':False,'gpu':3},
 'micro_rule':'area_fraction<0.0002 AND bbox_volume_fraction<0.00001 AND triangle_count<50; preserve all labels/provenance',
 'major_rule':'nonmicro AND (surface_area_fraction>=0.02 OR bbox_volume_fraction>=0.01)',
 'max_candidates':8,'max_primitives':8,'max_booleans':6,'max_sketch_entities':96,'evaluation_points':20000,'iou_resolution':128,
 'strict':{'iou':.90,'ncd':.01,'bbox':.03,'centroid':.02},'near':{'iou':.70,'ncd':.02},
 'xpart':'only independent major missing geometry evidence + direct failure; segmentation boundaries insufficient',
 'assembly':'strict accepted parts only; full strict requires all major parts and at least one major; record residual omissions and whole-object metrics',
 'evaluation_tessellation':{'linear':.001,'angular':.05},'exact_tessellation':{'linear':.0002,'angular':.02},
 'object_metric_frame':'common canonical full-object frame','part_metric_frame':'part bbox midpoint longest extent1; inverse transform retained',
 'llm_planning':'Codex assistant structure plans from recorded geometry summaries; numeric parameters from deterministic fitting; no private API credentials required'}
(O/'config/smoke20.json').write_text(json.dumps(cfg,indent=2));print('PREPARE_COMPLETE',len(protected))
