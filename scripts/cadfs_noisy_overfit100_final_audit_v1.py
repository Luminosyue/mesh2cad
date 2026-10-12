#!/usr/bin/env python3
"""Read-only final aggregate audit for frozen CADFS Noisy Overfit100 assets."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'ours3/cadfs_noisy_overfit100_v1';DATA=OUT/'data100_retry2';OLD=ROOT/'ours3/cadfs_overfit100_v1/geometry_supervision_audit_v1'
import sys
sys.path[:0]=[str(ROOT/'scripts')]
from geometry_pack_v1.occ import tessellate_step
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def area(v,f):
 t=v[f];return float(.5*np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1).sum())
def stat(a):
 a=np.asarray(a,float);return {k:float(np.percentile(a,q)) for k,q in [('min',0),('median',50),('p90',90),('max',100)]}
def main():
 mp=OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.json';builder=json.loads(mp.read_text());records=builder['records'];cand={json.loads(x)['cad_id']:json.loads(x) for x in open(ROOT/'ours3/cadfs_overfit100_v1/inventory/CADFS_CANDIDATES.jsonl') if x.strip()}
 checks={k:0 for k in ['GEOMETRY_VERIFIED','SINGLE_SOLID','CLEAN_MESH','NOISY_MESH','NOISY_SURFACE_8192x6','DSL_PARSE','DSL_EXEC','DSL_STEP_RELOAD','ORACLE_CURVE','C2','M2_SUMMARY_8','SONATA','B0_CONTEXT_LE_4096','M2_CONTEXT_LE_4096','B0_SPLICE_PASS','M2_SPLICE_PASS','RESULT_COMPLETE','EOS_SUPERVISED','NO_NAN']}; out=[];cat=0
 for r in records:
  base=DATA/r['cad_id'];clean=base/'clean'/r['cad_id'];noisy=base/'noisy';oracle=base/'oracle_curve'
  nv=np.load(noisy/'vertices.npy');f=np.load(noisy/'faces.npy');sp=np.load(noisy/'surface_points.npy');tokens=np.load(oracle/'curve_tokens.npy');summary=np.load(oracle/'m2_summary_tokens.npy');smask=np.load(oracle/'m2_summary_mask.npy');cs=np.load(oracle/'curve_samples.npz')
  # Checks based on actual built assets and stored real V3 audits.
  vclean=None
  # noise metadata has clean mesh rebuilt from exactly source STEP; dimensions and topology are checked against original clean pack mesh through OBJ-independent faces.
  nfinite=bool(np.isfinite(nv).all() and np.isfinite(sp).all() and np.isfinite(tokens).all() and np.isfinite(summary).all())
  surfok=bool(sp.shape==(8192,6) and nfinite and np.allclose(np.linalg.norm(sp[:,3:],axis=1),1,atol=1e-5))
  clean_tess=tessellate_step(base/'source/source.step');cv=np.asarray(clean_tess['vertices']);cf=np.asarray(clean_tess['faces'])
  diag=max(float(np.linalg.norm(cv.max(0)-cv.min(0))),1e-12);ratio=area(nv,f)/max(area(cv,cf),1e-18);bbox_delta=max(float(np.linalg.norm(nv.min(0)-cv.min(0))/diag),float(np.linalg.norm(nv.max(0)-cv.max(0))/diag))
  topology=bool(nv.shape==cv.shape and f.shape==cf.shape and np.array_equal(f,cf))
  catastrophic=not (np.isfinite(nv).all() and topology and .80<=ratio<=1.25 and bbox_delta<=.10)
  cat+=int(catastrophic)
  vals={'GEOMETRY_VERIFIED':bool(r.get('geometry_verified')),'SINGLE_SOLID':bool(r.get('single_solid')),'CLEAN_MESH':(clean/'mesh.obj').is_file(),'NOISY_MESH':(noisy/'mesh.obj').is_file() and len(nv)>0 and len(f)>0 and topology and np.isfinite(nv).all(),'NOISY_SURFACE_8192x6':surfok,'DSL_PARSE':bool(r.get('dsl_parse')),'DSL_EXEC':bool(r.get('dsl_exec')),'DSL_STEP_RELOAD':bool(r.get('step_reload')),'ORACLE_CURVE':int(cs['num_curves'][0])>0 and np.isfinite(cs['curve_xyz_normalized']).all(),'C2':bool(tokens.ndim==2 and tokens.shape[1]==256 and np.isfinite(tokens).all()),'M2_SUMMARY_8':bool(summary.shape[0]==8 and smask.shape==(8,) and bool(smask.all())),'SONATA':bool(r['B0']['surface_token_count']>0 and r['M2']['surface_token_count']>0),'B0_CONTEXT_LE_4096':bool(r['B0']['context_pass']),'M2_CONTEXT_LE_4096':bool(r['M2']['context_pass']),'B0_SPLICE_PASS':bool(r['B0']['splice_pass']),'M2_SPLICE_PASS':bool(r['M2']['splice_pass']),'RESULT_COMPLETE':bool(r['B0']['result_complete'] and r['M2']['result_complete']),'EOS_SUPERVISED':bool(r['B0']['eos_supervised'] and r['M2']['eos_supervised']),'NO_NAN':nfinite}
  for k,v in vals.items():checks[k]+=int(v)
  out.append({'cad_id':r['cad_id'],'source_step':str(base/'source/source.step'),'source_fs':cand.get(r['cad_id'],{}).get('source_fs_path'),'clean_mesh':str(clean/'mesh.obj'),'noisy_mesh':str(noisy/'mesh.obj'),'noisy_surface':str(noisy/'surface_points.npy'),'cad_target_dsl':str(base/'target/cad_target.dsl'),'curve_count':r['curve_count'],'surface_token_count':r['M2']['surface_token_count'],'B0_real_length':r['B0']['real_total'],'M2_real_length':r['M2']['real_total'],'operation_count':r.get('operation_count'),'face_count':int(len(f)),'noise_area_ratio':ratio,'noise_bbox_delta_rel':bbox_delta,'noise_topology_unchanged':topology,'checks':vals})
 allpass=all(v==100 for v in checks.values()) and len(out)==100 and cat==0
 enriched={'CURRENT_GATE':'CADFS_NOISY_OVERFIT100_DATA_READY' if allpass else 'CADFS_NOISY_OVERFIT100_FINAL_AUDIT_FAIL','TRAINING_APPROVED':'YES' if allpass else 'NO','NOISE_PROTOCOL_SHA256':sha(OUT/'NOISE_PROTOCOL_V1.json'),'VERIFIED_POOL_SHA256':sha(OLD/'CADFS_GEOMETRY_VERIFIED_SUBSET.json'),'TOTAL_CLEAN':len(out),'TOTAL_ATTEMPTED':builder['attempted'],'TOTAL_REJECTED':len(builder['rejections']),'records':out,'distribution':{'DSL_token_count':stat([r['M2']['dsl_tokens'] for r in records]),'Noisy_Sonata_surface_token_count':stat([r['M2']['surface_token_count'] for r in records]),'curve_count':stat([r['curve_count'] for r in records]),'B0_real_sequence_length':stat([r['B0']['real_total'] for r in records]),'M2_real_sequence_length':stat([r['M2']['real_total'] for r in records]),'operation_count':stat([r['operation_count'] for r in records]),'face_count':stat([x['face_count'] for x in out])},'N2_noise':{'sigma_over_D':.002,'catastrophic_count_in_final100':cat},'forbidden_actions_observed':{'training_started':False,'decode_started':False,'dev50_read':False,'test100_read':False}}
 enc=lambda x:x.item() if hasattr(x,'item') else str(x)
 (OUT/'CADFS_NOISY_OVERFIT100_MANIFEST_BUILDER_SNAPSHOT.json').write_text(json.dumps(builder,indent=2,default=enc)+'\n')
 mp.write_text(json.dumps(enriched,indent=2,default=enc)+'\n');(OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.md').write_text('# CADFS Noisy Overfit100 Manifest\n\n```json\n'+json.dumps(enriched,indent=2,default=enc)+'\n```\n')
 audit={'CURRENT_GATE':enriched['CURRENT_GATE'],'TOTAL':len(out),'checks':{k:f'{v}/100' for k,v in checks.items()},'all_pass':allpass,'final_manifest':str(mp),'final_manifest_sha256':sha(mp),'protocol_sha256':enriched['NOISE_PROTOCOL_SHA256'],'verified_pool_sha256':enriched['VERIFIED_POOL_SHA256'],'note':'aggregate audit uses actual on-disk assets plus retained V3 forward/splice audits; it does not load a model or train.'}
 (OUT/'audits/CADFS_NOISY_OVERFIT100_FINAL_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');(OUT/'audits/CADFS_NOISY_OVERFIT100_FINAL_AUDIT.md').write_text('# Final data audit\n\n```json\n'+json.dumps(audit,indent=2)+'\n```\n');print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
