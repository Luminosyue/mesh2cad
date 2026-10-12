#!/usr/bin/env python3
"""Build ANCHOR_EVAL_100_V1 from the frozen V3-compatible clean pool only.

This is a data/provenance gate.  It does not load an LLM, decode, or train.
"""
from __future__ import annotations

import hashlib, importlib.util, json, os, random, shutil, sys, tempfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
POOL = ROOT/'ours3/canonical_cad_data_v4/records'
OUT = ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/anchor_eval_100'
EXEC = ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
C2 = ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
SPLITS = [ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'/x for x in ('v3_1k_train.json','v3_decode_dev_50.json','v3_pilot_eval_150.json')]
EXEC_SHA='53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'
C2_SHA='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'

def sha(p: Path) -> str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def jwrite(p: Path, x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def cid(src,sid): return f'{src.lower()}__{sid.lower()}'
def anchor(samples: np.ndarray, mn: np.ndarray, mx: np.ndarray) -> np.ndarray:
 # [K,N,3] curve samples; object-wide scalar length normalization, Q-ablation contract.
 xyz=np.asarray(samples,dtype=np.float32); denom=max(float(np.max(mx-mn)),1e-8); ctr=(mn+mx)/2
 return np.concatenate([(xyz.mean(1)-ctr)/denom,(xyz.max(1)-xyz.min(1))/denom],axis=1).astype(np.float32)

def load_exec():
 spec=importlib.util.spec_from_file_location('frozen_placement_v3_cad_dsl',EXEC)
 mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
 return mod
def built_shape(mod, code):
 p=mod.parse_dsl(code); shapes={}
 for name,node in p.assignments.items():
  if name!='result': shapes[name]=mod._build_shape(node,shapes) if isinstance(node,dict) and 'op' in node else node
 node=p.assignments['result']; r=shapes[node] if isinstance(node,str) else (mod._build_shape(node,shapes) if isinstance(node,dict) and 'op' in node else node)
 return p, (r.val().wrapped if hasattr(r,'val') else r)

def main():
 OUT.mkdir(parents=True,exist_ok=True); (OUT/'records').mkdir(exist_ok=True)
 assert sha(EXEC)==EXEC_SHA, 'executor hash mismatch'; assert sha(C2)==C2_SHA, 'C2 hash mismatch'
 metas=[]; bycid={}
 for p in POOL.glob('*/metadata.json'):
  m=json.loads(p.read_text()); m['_root']=p.parent; m['_id']=cid(m['source'],m['source_id']); metas.append(m); bycid[m['_id']]=m
 # The only reads from pilot150 are fields in this loop: no predictions/metrics paths are opened.
 forbidden_ids=set(); forbidden_dsl=set(); forbidden_geo=set(); missing_split_metadata=[]
 for sp in SPLITS:
  for r in json.loads(sp.read_text())['records']:
   c=r['cad_id'].lower(); forbidden_ids.add(c); forbidden_dsl.add(r['target_dsl_sha256'])
   if c in bycid: forbidden_geo.add(bycid[c]['geometry_fingerprint'])
   else: missing_split_metadata.append(c)
 # Geometry fingerprints are a mandatory leakage key.  The split rows do not
 # carry them and a subset cannot be joined to the legacy clean-pool metadata;
 # do not silently substitute source-id or DSL hash for geometry identity.
 if missing_split_metadata:
  failure={'CURRENT_GATE':'ANCHOR_EVAL_100_V1_FREEZE_FAIL','FAILURE_REASON':'V3 split geometry_fingerprint metadata is unavailable for a complete strict cross-split audit; source/DSL identifiers are not a valid substitute.','MISSING_SPLIT_GEOMETRY_METADATA_COUNT':len(missing_split_metadata),'MISSING_EXAMPLES':missing_split_metadata[:20],'MODEL_INFERENCE_RUN':False,'TRAINING_STARTED':False,'PILOT150_METADATA_READ_FOR_LEAKAGE_AUDIT':True,'PILOT150_MODEL_RESULTS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False,'OFFICIAL_TEST_READ':False,'EXECUTOR_MODULE':str(EXEC),'EXECUTOR_SHA256':EXEC_SHA}
  leakage={'SOURCE_OVERLAP':'NOT_COMPUTED','DSL_HASH_OVERLAP':'NOT_COMPUTED','GEOMETRY_OVERLAP':'UNVERIFIABLE','INTERNAL_DUPLICATES':'NOT_COMPUTED','FAMILY_TEMPLATE_OVERLAP':'UNKNOWN','PILOT150_METADATA_READ_FOR_LEAKAGE_AUDIT':True,'PILOT150_MODEL_RESULTS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False,'reason':failure['FAILURE_REASON']}
  jwrite(OUT/'ANCHOR_EVAL_100_V1_FREEZE.json',failure); jwrite(OUT/'LEAKAGE_AUDIT.json',leakage); jwrite(OUT/'DISTRIBUTION_REPORT.json',{'status':'NOT_GENERATED_DUE_TO_STRICT_LEAKAGE_AUDIT_FAILURE'}); jwrite(OUT/'C2_PROVENANCE_REPORT.json',{'status':'NOT_RUN_DUE_TO_STRICT_LEAKAGE_AUDIT_FAILURE','C2_CHECKPOINT':str(C2),'C2_FROZEN':True,'C2_TRAINABLE_PARAMS':0})
  (OUT/'ANCHOR_EVAL_100_V1.jsonl').write_text(json.dumps({'status':'FREEZE_FAIL','reason':failure['FAILURE_REASON']})+'\n')
  mf={p.name:sha(p) for p in [OUT/'ANCHOR_EVAL_100_V1.jsonl',OUT/'ANCHOR_EVAL_100_V1_FREEZE.json',OUT/'LEAKAGE_AUDIT.json',OUT/'DISTRIBUTION_REPORT.json',OUT/'C2_PROVENANCE_REPORT.json']}; jwrite(OUT/'FILE_SHA256_MANIFEST.json',mf)
  print(json.dumps(failure,indent=2)); return
 eligible=[]; excluded=Counter()
 required=('canonical/program.dsl','canonical/model.step','geometry/surface_4096.npy','geometry/curves.json','geometry/curve_samples.npy','geometry/curve_tokens_c2.npy')
 for m in metas:
  if m['source'] not in ('DEEPCAD','FUSION360'): excluded['source']+=1; continue
  if not (m.get('status')=='clean' and m.get('fair_three_arm') and m.get('dsl_execute') and m.get('step_reload') and m.get('surface_valid') and m.get('curve_valid') and m.get('c2_valid')): excluded['legacy_gate']+=1; continue
  if m['_id'] in forbidden_ids or m['canonical_dsl_sha256'] in forbidden_dsl or m['geometry_fingerprint'] in forbidden_geo: excluded['overlap']+=1; continue
  if m.get('c2_checkpoint')!=str(C2) or m.get('c2_meta',{}).get('C2_CHECKPOINT_SHA256')!=C2_SHA: excluded['c2']+=1; continue
  if not all((m['_root']/x).is_file() for x in required): excluded['assets']+=1; continue
  eligible.append(m)
 chosen=[]
 for source,n in [('DEEPCAD',80),('FUSION360',20)]:
  a=sorted((x for x in eligible if x['source']==source),key=lambda x:hashlib.sha256(('ANCHOR_EVAL_100_V1|'+x['_id']).encode()).hexdigest())
  assert len(a)>=n, f'not enough {source}: {len(a)}'; chosen.extend(a[:n])
 assert len({x['_id'] for x in chosen})==100
 # internal duplicate check is strict across known key dimensions; family deliberately UNKNOWN.
 for key in ('source_id','canonical_dsl_sha256','geometry_fingerprint'):
  assert len({x[key] for x in chosen})==100, f'internal {key} duplicate'
 mod=load_exec(); stage=Counter(); records=[]; tmp=Path(tempfile.mkdtemp(prefix='anchor_eval_'))
 try:
  for ix,m in enumerate(chosen):
   rid=m['_id']; rr=OUT/'records'/rid; rr.mkdir(exist_ok=True)
   root=m['_root']; code=(root/'canonical/program.dsl').read_text()
   # verify all source assets and write an isolated anchor; source files are immutable inputs.
   s=np.load(root/'geometry/surface_4096.npy'); curves=json.loads((root/'geometry/curves.json').read_text()); samples=np.load(root/'geometry/curve_samples.npy'); tokens=np.load(root/'geometry/curve_tokens_c2.npy')
   mn=np.array(m['geometry_metrics']['bbox_min'],np.float32); mx=np.array(m['geometry_metrics']['bbox_max'],np.float32); a=anchor(samples,mn,mx)
   np.save(rr/'spatial_anchor_object_bbox_v1.npy',a)
   checks={'surface': bool(s.ndim==2 and s.shape[0]==4096 and s.shape[1]>=6), 'curve': bool(len(curves)==len(samples)>0), 'c2': bool(tokens.shape==(len(curves),256)), 'anchor': bool(a.shape==(len(curves),6) and np.isfinite(a).all())}
   for k,v in checks.items(): stage[k]+=int(v)
   parse=execute=nonnull=brep=stepreload=False; err=None
   try:
    _,shape=built_shape(mod,code); parse=execute=True; nonnull=not shape.IsNull()
    from OCP.BRepCheck import BRepCheck_Analyzer
    brep=bool(nonnull and BRepCheck_Analyzer(shape).IsValid())
    step=rr/'gt_replayed.step'; mod.execute_dsl(code,step); from OCP.STEPControl import STEPControl_Reader
    reader=STEPControl_Reader(); stepreload=reader.ReadFile(str(step))==1 and reader.TransferRoots()>0
   except Exception as e: err=f'{type(e).__name__}: {e}'
   for k,v in [('parse',parse),('execute',execute),('occ_non_null',nonnull),('brep_valid',brep),('step_reload',stepreload)]: stage[k]+=int(v)
   rec={'cad_id':rid,'source_dataset':m['source'].lower(),'source_id':m['source_id'],'family_id':'UNKNOWN','family_overlap_status':'UNKNOWN','canonical_dsl_sha256':m['canonical_dsl_sha256'],'geometry_fingerprint':m['geometry_fingerprint'],'assets':{k:str((root/x).resolve()) for k,x in {'canonical_gt_dsl':'canonical/program.dsl','canonical_gt_step':'canonical/model.step','surface':'geometry/surface_4096.npy','raw_curves':'geometry/curves.json','curve_samples':'geometry/curve_samples.npy','c2_tokens':'geometry/curve_tokens_c2.npy'}.items()},'spatial_anchor':str((rr/'spatial_anchor_object_bbox_v1.npy').resolve()),'anchor_definition':'[curve_centroid_xyz,curve_bbox_extent_xyz] / max(object_bbox_extent)','object_bbox_min':mn.tolist(),'object_bbox_max':mx.tolist(),'c2_provenance':m['c2_meta'],'validation':{**checks,'gt_parse':parse,'gt_execute':execute,'gt_occ_non_null':nonnull,'gt_brep_valid':brep,'gt_step_reload':stepreload,'error':err}}
   records.append(rec)
 finally: shutil.rmtree(tmp,ignore_errors=True)
 # direct C2 canary: exact codepath used by original exporter and source assets.
 sys.path.insert(0,str(ROOT/'scripts')); from canonical_cad_data_v4.geometry.c2_export import encode_curves
 rng=random.Random(20260829); canary=rng.sample(records,20); can=[]
 for r in canary:
  curves=json.loads(Path(r['assets']['raw_curves']).read_text()); direct,meta=encode_curves(curves,device='cpu'); disk=np.load(r['assets']['c2_tokens']);
  can.append({'cad_id':r['cad_id'],'exact':bool(np.array_equal(direct,disk)),'max_abs_diff':float(np.max(np.abs(direct-disk))) if direct.size else 0.0,'shape_equal':list(direct.shape)==list(disk.shape),'checkpoint':meta['C2_CHECKPOINT']})
 c2pass=all(x['exact'] for x in can)
 with (OUT/'ANCHOR_EVAL_100_V1.jsonl').open('w') as f:
  for r in records: f.write(json.dumps(r,sort_keys=True)+'\n')
 leakage={'SOURCE_OVERLAP':0,'DSL_HASH_OVERLAP':0,'GEOMETRY_OVERLAP':0,'INTERNAL_DUPLICATES':0,'FAMILY_TEMPLATE_OVERLAP':'UNKNOWN','FAMILY_TEMPLATE_REASON':'No reliable family/template identifier exists in V3 split or clean-pool metadata; UNKNOWN is not counted as zero.','PILOT150_METADATA_READ_FOR_LEAKAGE_AUDIT':True,'PILOT150_MODEL_RESULTS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False,'split_counts':{'train800':800,'decode_dev50':50,'pilot_eval150':150},'eligible_after_exclusion':len(eligible),'excluded':dict(excluded)}
 dist={'TOTAL':100,'DEEPCAD':80,'FUSION360':20,'complexity':dict(Counter(m['complexity'] for m in chosen)),'operations':dict(Counter(op for m in chosen for op in m['operations'])),'curve_count':{'min':min(len(json.loads((m['_root']/'geometry/curves.json').read_text())) for m in chosen),'max':max(len(json.loads((m['_root']/'geometry/curves.json').read_text())) for m in chosen)}}
 prov={'C2_CHECKPOINT':str(C2),'C2_CHECKPOINT_SHA256':C2_SHA,'C2_FROZEN':True,'C2_TRAINABLE_PARAMS':0,'DIRECT_VS_SAVED_CANARY':'%d/20'%sum(x['exact'] for x in can),'MAX_ABS_TOKEN_DIFF':max(x['max_abs_diff'] for x in can),'records':can}
 gate={'TOTAL':100,'DEEPCAD':80,'FUSION360':20,'SOURCE_OVERLAP':0,'DSL_HASH_OVERLAP':0,'GEOMETRY_OVERLAP':0,'INTERNAL_DUPLICATES':0,'FAMILY_TEMPLATE_OVERLAP':'UNKNOWN','GT_PARSE':'%d/100'%stage['parse'],'GT_EXECUTE':'%d/100'%stage['execute'],'GT_OCC_NON_NULL':'%d/100'%stage['occ_non_null'],'GT_BREP_VALID':'%d/100'%stage['brep_valid'],'GT_STEP_RELOAD':'%d/100'%stage['step_reload'],'SURFACE_VALID':'%d/100'%stage['surface'],'CURVE_VALID':'%d/100'%stage['curve'],'C2_VALID':'%d/100'%stage['c2'],'ANCHOR_VALID':'%d/100'%stage['anchor'],'C2_PROVENANCE_CANARY':'20/20' if c2pass else '%d/20'%sum(x['exact'] for x in can),'MODEL_INFERENCE_RUN':False,'TRAINING_STARTED':False,'PILOT150_MODEL_RESULTS_READ':False,'OFFICIAL_TEST_READ':False,'EXECUTOR_MODULE':str(EXEC),'EXECUTOR_SHA256':EXEC_SHA,'OCC_VALIDITY':'not shape.IsNull() + BRepCheck_Analyzer(shape).IsValid()'}
 passed=all(gate[k]=='100/100' for k in ('GT_PARSE','GT_EXECUTE','GT_OCC_NON_NULL','GT_BREP_VALID','GT_STEP_RELOAD','SURFACE_VALID','CURVE_VALID','C2_VALID','ANCHOR_VALID')) and c2pass
 gate['CURRENT_GATE']='ANCHOR_EVAL_100_V1_FREEZE_PASS' if passed else 'ANCHOR_EVAL_100_V1_FREEZE_FAIL'
 jwrite(OUT/'LEAKAGE_AUDIT.json',leakage); jwrite(OUT/'DISTRIBUTION_REPORT.json',dist); jwrite(OUT/'C2_PROVENANCE_REPORT.json',prov); jwrite(OUT/'ANCHOR_EVAL_100_V1_FREEZE.json',gate)
 manifest={p.name:sha(p) for p in [OUT/'ANCHOR_EVAL_100_V1.jsonl',OUT/'ANCHOR_EVAL_100_V1_FREEZE.json',OUT/'LEAKAGE_AUDIT.json',OUT/'DISTRIBUTION_REPORT.json',OUT/'C2_PROVENANCE_REPORT.json']}; jwrite(OUT/'FILE_SHA256_MANIFEST.json',manifest)
 print(json.dumps(gate,indent=2)); print('OUT='+str(OUT))
if __name__=='__main__': main()
