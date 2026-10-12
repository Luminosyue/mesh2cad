import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,hashlib,shutil,datetime
from pathlib import Path
P=Path('/data/home/cuiyuehan/project/mesh2cad');V=P/'outputs/p3_high_detail_mesh2cad_factory_v1_smoke20';O=P/'outputs/part_cad_fitting_v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
if (O/'manifests/cases.json').exists():raise RuntimeError('Already prepared; resume stages, do not overwrite')
for s in ['config','manifests','near_pass','reject','cases','tables','reports','scripts','integrity','logs','visualizations','historical_readonly_copies']:(O/s).mkdir(parents=True,exist_ok=True)
guard=json.loads((V/'integrity/PROTECTED_BEFORE.json').read_text())
for p in V.rglob('*'):
 if p.is_file():guard[str(p)]={'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns}
for p in [P/'partsam_cad_iou_top1000_v1/scripts/pipeline.py',P/'build_partsam_p1.py']:
 guard[str(p)]={'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns};shutil.copyfile(p,O/'historical_readonly_copies'/p.name)
dump(O/'integrity/PROTECTED_BEFORE.json',guard)
for name in ['metric_runtime.py','fit_logic.py','historical_fit.py','cad_emit.py','execute_candidate.py']:
 shutil.copyfile(V/'scripts'/name,O/'scripts'/name)
shutil.copyfile(V/'config/factory_config.json',O/'config/factory_config.json')
rows=[]
for obj in json.loads((V/'manifests/objects_frozen.json').read_text()):
 for part in json.loads((V/'objects'/obj['object_id']/'p3/parts_manifest.json').read_text())['parts']:
  old=V/'objects'/obj['object_id']/'parts'/part['part_id'];r=json.loads((old/'result.json').read_text());cid=obj['object_id']+'/'+part['part_id'];d=O/'cases'/cid
  for name in ['source','features','diagnosis','candidates','optimization','cad','metrics','visualizations']:(d/name).mkdir(parents=True,exist_ok=True)
  shutil.copyfile(old/'source/part_local.ply',d/'source/part_local.ply');shutil.copyfile(old/'features/features.json',d/'source/v1_features.json');shutil.copyfile(old/'result.json',d/'source/v1_result.json');dump(d/'source/provenance.json',part)
  rec={'case_id':cid,'object_id':obj['object_id'],'part_id':part['part_id'],'size_class':part['size_class'],'v1_status':r['status'],'v1_family':r['cad_family'],'v1_kind':r['best_kind'],'v1_dir':str(old),'source_part_sha256':part['part_mesh_sha256'],'normalized_mesh_sha256':sha(d/'source/part_local.ply'),'seed':r['metrics']['source_seed'],'same_transforms':True};rows.append(rec)
dump(O/'manifests/cases.json',rows);dump(O/'manifests/objects.json',json.loads((V/'manifests/objects_frozen.json').read_text()))
cfg={'seed_policy':'original per-part source_seed and cad_seed, same 20000 samples; no input reselection or renormalization','max_candidates':8,'max_primitives':8,'max_booleans':6,'max_sketch_entities':96,'strict':{'iou':.9,'ncd':.01,'bbox':.03,'centroid':.02},'near':{'iou':.7,'ncd':.02},'ranking':'strict first, then 10*NCD + (1-IoU) + 2*centroid + bbox; retain baseline if no improvement','near_policy':'keep native structure; optimize numeric plane/sketch/depth/radius parameters; switch structure only with recorded WRONG_CAD_FAMILY evidence','proxy':'fixed-grid 64 affine occupancy and fixed subsets of original-seed 20000 samples, optimization proposals only; acceptance uses original STEP-reload IoU128 + full 20000 point protocol','candidate_budget_includes_baseline':True,'max_workers':8,'assembly_run':False,'no_p3_rerun':True,'no_training':True}
dump(O/'config/v2.json',cfg);print('PREPARED',len(rows),'PROTECTED',len(guard))
