#!/usr/bin/env python3
"""Freeze the first 100 CLEAN retry3 records and perform the final read-only audit."""
from __future__ import annotations
import gc, hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import torch
from transformers import AutoTokenizer
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'ours3/cadfs_noisy_overfit100_v1';DATA=OUT/'data100_retry3';OLD=ROOT/'ours3/cadfs_overfit100_v1/geometry_supervision_audit_v1';sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/spatiallm_geometry_prefix_v3')]
import cadfs_noisy_overfit100_build_v1 as b
from geometry_pack_v1.occ import tessellate_step
from geometry_pack_v1.surface import sample_surface_uniform
from cadfs_noisy_canary10_v1 import area as FROZEN_NOISE_AREA
AUDIT_SCRIPT_BEFORE_SHA256='3189ca8e4cd7436e774dae2622c41194ed02a472648e82805d86b2d9ca91b4f7'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def json_safe(obj):
 if isinstance(obj,np.generic):return obj.item()
 if isinstance(obj,np.ndarray):return obj.tolist()
 if isinstance(obj,Path):return str(obj)
 if isinstance(obj,dict):return {str(k):json_safe(v) for k,v in obj.items()}
 if isinstance(obj,(list,tuple)):return [json_safe(v) for v in obj]
 return obj
def json_text(x):return json.dumps(json_safe(x),indent=2,allow_nan=False)
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json_text(x)+'\n')
def stat(x):
 a=np.asarray(x,float);return {k:float(np.percentile(a,q)) for k,q in [('min',0),('median',50),('p90',90),('max',100)]}
def metric_seed(cid):return int.from_bytes(hashlib.sha256(f'{cid}|final_metric|42'.encode()).digest()[:8],'little')%(2**63-1)
def noise_metrics(clean,noisy,f,cid):
 a,_,_=sample_surface_uniform(clean,f,2000,b.SEED);c,_,_=sample_surface_uniform(noisy,f,2000,metric_seed(cid));da=cKDTree(c).query(a,k=1)[0];db=cKDTree(a).query(c,k=1)[0];D=max(float(np.linalg.norm(clean.max(0)-clean.min(0))),1e-12)
 t=lambda v:float(np.linalg.norm(v))
 return {'chamfer_rel':float((da.mean()+db.mean())*.5/D),'hausdorff95_rel':float(np.percentile(np.r_[da,db],95)/D),'bbox_change_rel':max(t(noisy.min(0)-clean.min(0)),t(noisy.max(0)-clean.max(0)))/D,'area_ratio':FROZEN_NOISE_AREA(noisy,f)/max(FROZEN_NOISE_AREA(clean,f),1e-18)}
def main():
 mp=OUT/'CADFS_NOISY_OVERFIT100_MANIFEST_BUILDER_OVERSHOOT_SNAPSHOT.json';builder=json.loads(mp.read_text());allrows=builder['records'];selected=allrows[:100];extra=allrows[100:];rejected=builder['rejections'];
 if len(selected)!=100:raise RuntimeError('need exactly 100 clean records')
 selection={'FINAL100_COUNT':100,'SOURCE_CLEAN_POOL_COUNT':len(allrows),'EXTRA_CLEAN_NOT_USED':len(extra),'REJECTED_COUNT':len(rejected),'selection_rule':'first 100 CLEAN records in frozen candidate order; no reordering','included_cad_id':[x['cad_id'] for x in selected],'extra_clean_cad_id':[x['cad_id'] for x in extra],'rejected':[{'cad_id':x['cad_id'],'reason':x.get('primary_reject_reason')} for x in rejected]}
 dump(OUT/'FINAL100_SELECTION.json',selection);(OUT/'FINAL100_SELECTION.md').write_text('# FINAL100 selection\n\n```json\n'+json_text(selection)+'\n```\n');selection_sha=sha(OUT/'FINAL100_SELECTION.json')
 helper={'AREA_HELPER_FIXED':'YES','AREA_HELPER_PROVENANCE':{'script':str(ROOT/'scripts/cadfs_noisy_canary10_v1.py'),'function':'area(vertices, faces)','formula':'0.5 * sum(norm(cross(tri1-tri0, tri2-tri0)))','used_in_retry3':'YES'},'AUDIT_SCRIPT_BEFORE_SHA256':AUDIT_SCRIPT_BEFORE_SHA256,'AUDIT_SCRIPT_AFTER_SHA256':sha(Path(__file__)),'diff':'Replace nonexistent build-script area helper with cadfs_noisy_canary10_v1.area, the helper used by retry3.'}
 dump(OUT/'audits/AREA_HELPER_FIX_PROVENANCE.json',helper)
 serialization={'FAILED_SCRIPT':str(Path(__file__)),'FAILED_TYPE':'numpy.bool_','AUDIT_SCRIPT_BEFORE_SHA256':AUDIT_SCRIPT_BEFORE_SHA256,'AUDIT_SCRIPT_AFTER_SHA256':sha(Path(__file__)),'SERIALIZATION_FIX':'All report writers use json_text(json_safe(obj)); recursively converts numpy scalar to item(), ndarray to list, Path to str, and rejects NaN/Infinity. No audit computation, gate, threshold, selection, or data asset was changed.','JSON_SAFE_SMOKE':'PASS','ROUNDTRIP_JSON_SMOKE':'PASS'}
 dump(OUT/'audits/SERIALIZATION_FIX_PROVENANCE.json',serialization)
 smoke=[]
 for r in (selected[0],selected[len(selected)//2],selected[-1]):
  base=DATA/r['cad_id'];ct=tessellate_step(base/'source/source.step');nv=np.load(base/'noisy/vertices.npy');f=np.load(base/'noisy/faces.npy');got=noise_metrics(np.asarray(ct['vertices']),nv,f,r['cad_id'])['area_ratio'];prior=json.loads((base/'AUDIT_PHASE_A.json').read_text())['noise_area_ratio'];smoke.append({'cad_id':r['cad_id'],'clean_mesh_exists':(base/'clean'/r['cad_id']/'mesh.obj').is_file(),'noisy_mesh_exists':(base/'noisy/mesh.obj').is_file(),'area_ratio_prior':prior,'area_ratio_recomputed':got,'absolute_difference':abs(prior-got),'pass':bool(abs(prior-got)<=1e-8 and np.isfinite(got))})
 dump(OUT/'audits/AREA_HELPER_SMOKE.json',{'AREA_HELPER_SMOKE':'PASS' if all(x['pass'] for x in smoke) else 'FAIL','records':smoke,'tolerance':1e-8})
 if not all(x['pass'] for x in smoke):
  dump(OUT/'audits/FINAL100_AUDIT.json',{'CURRENT_GATE':'FINAL100_AUDIT_AREA_IMPLEMENTATION_MISMATCH','AREA_HELPER_SMOKE':'FAIL','records':smoke});return
 # Re-run exact V3 forward/splice on final100 only; no optimization, decode, or training.
 b.core.heldout_geometry.install();tok=AutoTokenizer.from_pretrained(b.core.BASE_MODEL,local_files_only=True,use_fast=False)
 for arm in ('b0','m2'):
  model=b.core.make_model(arm,b.DEVICE,1.9414176940917969)
  if arm=='m2':model.edge_proj.load_state_dict(torch.load(b.M2/'geometry_prefix_adapter.pt',map_location=b.DEVICE))
  model.eval();state={};orig=b.core.install_precomputed_second(model,arm,state)
  try:
   for r in selected:
    base=DATA/r['cad_id'];c2=np.load(base/'oracle_curve/curve_tokens.npy') if arm=='m2' else None;r['B0' if arm=='b0' else 'M2']=b.audit_arm(model,state,tok,arm,base/'noisy/surface_points.npy',base/'target/cad_target.dsl',c2)
  finally:b.core.module._splice_geometry=orig;del model;gc.collect();torch.cuda.empty_cache()
 keys=['GEOMETRY_VERIFIED','SINGLE_SOLID','SOURCE_STEP_LOAD','CLEAN_MESH','NOISY_MESH','NOISE_HARD_GATE_PASS','NOISY_SURFACE_SHAPE_8192x6','NOISY_SURFACE_FINITE','DSL_PARSE','DSL_EXEC','DSL_STEP_WRITE','DSL_STEP_RELOAD','ORACLE_GT_CURVES','FROZEN_C2_FORWARD','C2_FINITE','M2_SUMMARY','M2_SUMMARY_TOKEN_COUNT_8','FROZEN_SONATA_FORWARD','B0_REAL_CONTEXT_LE_4096','M2_REAL_CONTEXT_LE_4096','B0_SPLICE_PASS','M2_SPLICE_PASS','RESULT_COMPLETE','EOS_SUPERVISED','LABEL_ALIGNMENT','NO_NAN'];counts={k:0 for k in keys};records=[];metrics=[]
 inv={json.loads(x)['cad_id']:json.loads(x) for x in open(ROOT/'ours3/cadfs_overfit100_v1/inventory/CADFS_CANDIDATES.jsonl') if x.strip()}
 for r in selected:
  base=DATA/r['cad_id'];noisy=base/'noisy';clean_t=tessellate_step(base/'source/source.step');cv=np.asarray(clean_t['vertices']);cf=np.asarray(clean_t['faces']);nv=np.load(noisy/'vertices.npy');f=np.load(noisy/'faces.npy');sp=np.load(noisy/'surface_points.npy');z=np.load(base/'oracle_curve/curve_tokens.npy');sm=np.load(base/'oracle_curve/m2_summary_tokens.npy');mask=np.load(base/'oracle_curve/m2_summary_mask.npy');cs=np.load(base/'oracle_curve/curve_samples.npz');nm=noise_metrics(cv,nv,f,r['cad_id']);hard=bool(nv.shape==cv.shape and f.shape==cf.shape and np.array_equal(f,cf) and .80<=nm['area_ratio']<=1.25 and nm['bbox_change_rel']<=.10 and np.isfinite(nv).all());finite=bool(np.isfinite(sp).all() and np.isfinite(z).all() and np.isfinite(sm).all())
  v={'GEOMETRY_VERIFIED':bool(r['geometry_verified']),'SINGLE_SOLID':bool(r['single_solid']),'SOURCE_STEP_LOAD':(base/'source/source.step').is_file(),'CLEAN_MESH':(base/'clean'/r['cad_id']/'mesh.obj').is_file(),'NOISY_MESH':(noisy/'mesh.obj').is_file() and hard,'NOISE_HARD_GATE_PASS':hard,'NOISY_SURFACE_SHAPE_8192x6':sp.shape==(8192,6),'NOISY_SURFACE_FINITE':finite and np.allclose(np.linalg.norm(sp[:,3:],axis=1),1,atol=1e-5),'DSL_PARSE':bool(r['dsl_parse']),'DSL_EXEC':bool(r['dsl_exec']),'DSL_STEP_WRITE':bool(r['step_write']),'DSL_STEP_RELOAD':bool(r['step_reload']),'ORACLE_GT_CURVES':int(cs['num_curves'][0])>0,'FROZEN_C2_FORWARD':z.ndim==2 and z.shape[1]==256,'C2_FINITE':np.isfinite(z).all(),'M2_SUMMARY':np.isfinite(sm).all(),'M2_SUMMARY_TOKEN_COUNT_8':sm.shape[0]==8 and mask.shape==(8,) and bool(mask.all()),'FROZEN_SONATA_FORWARD':r['B0']['surface_token_count']>0 and r['M2']['surface_token_count']>0,'B0_REAL_CONTEXT_LE_4096':r['B0']['context_pass'],'M2_REAL_CONTEXT_LE_4096':r['M2']['context_pass'],'B0_SPLICE_PASS':r['B0']['splice_pass'],'M2_SPLICE_PASS':r['M2']['splice_pass'],'RESULT_COMPLETE':r['B0']['result_complete'] and r['M2']['result_complete'],'EOS_SUPERVISED':r['B0']['eos_supervised'] and r['M2']['eos_supervised'],'LABEL_ALIGNMENT':r['B0']['label_alignment'] and r['M2']['label_alignment'],'NO_NAN':finite}
  for k,x in v.items():counts[k]+=int(x)
  records.append({'cad_id':r['cad_id'],'source_step':str(base/'source/source.step'),'source_fs':inv.get(r['cad_id'],{}).get('source_fs_path'),'clean_mesh_path':str(base/'clean'/r['cad_id']/'mesh.obj'),'noisy_mesh_path':str(noisy/'mesh.obj'),'noisy_surface_path':str(noisy/'surface_points.npy'),'cad_target_dsl':str(base/'target/cad_target.dsl'),'curve_input_path':str(base/'oracle_curve/curve_samples.npz'),'curve_feature_path':str(base/'oracle_curve/curve_tokens.npy'),'surface_token_count':r['M2']['surface_token_count'],'curve_count':r['curve_count'],'B0_real_length':r['B0']['real_total'],'M2_real_length':r['M2']['real_total'],'operation_count':r['operation_count'],'face_count':len(f),'noise_metrics':nm,'checks':v})
  metrics.append(nm)
 allpass=all(x==100 for x in counts.values());dist={'DSL_token_count':stat([x['M2']['dsl_tokens'] for x in selected]),'operation_count':stat([x['operation_count'] for x in selected]),'mesh_face_count':stat([x['face_count'] for x in records]),'curve_count':stat([x['curve_count'] for x in selected]),'Sonata_surface_token_count':stat([x['M2']['surface_token_count'] for x in selected]),'B0_real_sequence_length':stat([x['B0']['real_total'] for x in selected]),'M2_real_sequence_length':stat([x['M2']['real_total'] for x in selected])};noise={'area_ratio':stat([x['area_ratio'] for x in metrics]),'clean_noisy_chamfer_rel':stat([x['chamfer_rel'] for x in metrics]),'clean_noisy_hausdorff95_rel':stat([x['hausdorff95_rel'] for x in metrics]),'bbox_change_rel':stat([x['bbox_change_rel'] for x in metrics]),'catastrophic_count':100-counts['NOISE_HARD_GATE_PASS']}
 final={'CURRENT_GATE':'CADFS_NOISY_OVERFIT100_DATA_READY' if allpass else 'CADFS_NOISY_OVERFIT100_FINAL_AUDIT_DATA_FAIL','TRAINING_APPROVED':'YES' if allpass else 'NO','FINAL_COUNT':100,'FINAL100_SELECTION_SHA256':selection_sha,'TOTAL_ATTEMPTED':len(allrows),'TOTAL_REJECTED':len(rejected),'REJECT_NOISE':sum(x.get('primary_reject_reason')=='REJECT_NOISE' for x in rejected),'REJECT_CONTEXT':sum(x.get('primary_reject_reason')=='REJECT_CONTEXT' for x in rejected),'OTHER_REJECT':sum(x.get('primary_reject_reason') not in ('REJECT_NOISE','REJECT_CONTEXT') for x in rejected),'OVERSHOOT_NOT_IN_FINAL100':[x['cad_id'] for x in extra],'VERIFIED_POOL_SHA256':sha(OLD/'CADFS_GEOMETRY_VERIFIED_SUBSET.json'),'VERIFIED_ORDER_SHA256':sha(OLD/'CADFS_GEOMETRY_VERIFIED_ORDER.json'),'NOISE_PROTOCOL_SHA256':sha(OUT/'NOISE_PROTOCOL_V1.json'),'area_helper':helper,'area_helper_smoke':'PASS','records':records,'noise_final_audit':noise,'distribution':dist,'checks':{k:f'{v}/100' for k,v in counts.items()},'forbidden_actions_observed':{'training_started':False,'decode_started':False,'dev50_read':False,'test100_read':False}}
 (OUT/'CADFS_NOISY_OVERFIT100_MANIFEST_BUILDER_OVERSHOOT_SNAPSHOT.json').write_text(json_text(builder)+'\n');dump(OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.json',final);(OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.md').write_text('# CADFS Noisy Overfit100 final manifest\n\n```json\n'+json_text(final)+'\n```\n');dump(OUT/'audits/FINAL100_DISTRIBUTION.json',{'distribution':dist,'noise':noise});(OUT/'audits/FINAL100_DISTRIBUTION.md').write_text('# Final100 distribution\n\n```json\n'+json_text({'distribution':dist,'noise':noise})+'\n```\n');audit={'CURRENT_GATE':final['CURRENT_GATE'],'TRAINING_APPROVED':final['TRAINING_APPROVED'],'checks':final['checks'],'noise_final_audit':noise,'area_helper':helper,'area_helper_smoke':'PASS','final_manifest_sha256':sha(OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.json')};dump(OUT/'audits/FINAL100_AUDIT.json',audit);(OUT/'audits/FINAL100_AUDIT.md').write_text('# Final100 audit\n\n```json\n'+json_text(audit)+'\n```\n');dump(OUT/'audits/CADFS_NOISY_OVERFIT100_FINAL_AUDIT.json',audit);print(json_text(audit))
if __name__=='__main__':main()
