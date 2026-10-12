#!/usr/bin/env python3
"""Build CADFS_NOISY_OVERFIT100_V1 assets only; never train or decode."""
from __future__ import annotations
import gc, hashlib, importlib.util, json, shutil, sys
from collections import Counter
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/cadfs_noisy_overfit100_v1'
DATA=OUT/'data100_retry3'
OLD=ROOT/'ours3/cadfs_overfit100_v1/geometry_supervision_audit_v1'
ORDER=OLD/'CADFS_GEOMETRY_VERIFIED_ORDER.json'
C2=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
C2_SHA='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
M2=ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_20'
DEVICE=torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
LIMIT=4096; N=100; LEVEL='N2'; SEED=42
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/spatiallm_geometry_prefix_v3')]
from geometry_pack_v1 import pack
from geometry_pack_v1.occ import tessellate_step
from geometry_pack_v1.surface import sample_surface_uniform
from deepcad.cad_canonical import compute_transform
import curve_token_v1.build_dataset as curves
import spatiallm_curve_token_c2_frozen_v2.export_curve_tokens as exporter
import train_v3_smoke as core
from v3_canary_surface_adapter import load_surface_for_encoder

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True,default=str)+'\n')
def execute(dsl,work):
 r={'dsl_parse':False,'dsl_exec':False,'step_write':False,'step_reload':False,'error':None}
 try:
  p=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py';s=importlib.util.spec_from_file_location('cadfs_noisy_exec',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
  code=m.extract_dsl_code(dsl);m.parse_dsl(code);r['dsl_parse']=True
  import cadquery as cq
  st,sl=work/'target_replay.step',work/'target_replay.stl';m.execute_dsl(code,st,sl);r['dsl_exec']=True;r['step_write']=st.is_file() and sl.is_file()
  if r['step_write']:cq.importers.importStep(str(st));r['step_reload']=True
 except Exception as e:r['error']=(type(e).__name__+': '+str(e))[-500:]
 return r
def prompt(tok,arm):
 u=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
 return tok.encode('<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+u+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n',add_special_tokens=False)
def raw_c2(c2):
 if c2.ndim!=2 or c2.shape[1]!=256 or len(c2)>128 or not np.isfinite(c2).all():raise ValueError('C2_INPUT')
 x=np.zeros((128,256),np.float32);x[:len(c2)]=c2;m=torch.zeros(128,dtype=torch.bool,device=DEVICE);m[:len(c2)]=True
 return torch.tensor(x,device=DEVICE).unsqueeze(0),m
def capture(fn):
 captured=[];orig=core.module._splice_labels
 def wrap(labels,regions,target_len):
  x=orig(labels,regions,target_len);captured.append(x.detach().cpu());return x
 core.module._splice_labels=wrap
 try:return fn(),captured[-1] if captured else None
 finally:core.module._splice_labels=orig
def audit_arm(model,state,tok,arm,surface_path,target_path,c2):
 plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 sid=surface_path.parent.parent.name;surface,_=load_surface_for_encoder(plugin,surface_path,'deepcad',sid);surface_t=torch.tensor(surface,device=DEVICE)
 target=tok.encode(target_path.read_text()+'<|eot_id|>',add_special_tokens=False);p=prompt(tok,arm);eos=tok.convert_tokens_to_ids('<|eot_id|>')
 edge=None;summary_count=0;summary_active=0;summary_valid=True
 if arm=='m2':
  edge,mask=raw_c2(c2);state['raw_mask']=mask
  with torch.no_grad():summary,smask=model.edge_proj(edge.to(dtype=next(model.edge_proj.parameters()).dtype),mask.unsqueeze(0))
  summary_count=int(summary.shape[1]);summary_active=int(smask.sum());summary_valid=bool(summary.shape==(1,8,model.config.hidden_size) and torch.isfinite(summary).all() and summary_active==8)
 else:state['raw_mask']=torch.empty(0,dtype=torch.bool,device=DEVICE)
 with torch.no_grad():S=int(model.forward_point_cloud(surface_t,DEVICE,torch.bfloat16,projector=model.point_proj).shape[1])
 total=len(p)+(S-1)+(7 if arm=='m2' else 0)+len(target)
 out={'surface_token_count':S,'prompt_tokens':len(p),'dsl_tokens':len(target)-1,'eos_tokens':1,'real_total':total,'context_pass':total<=LIMIT,'summary_token_count':summary_count,'summary_active_count':summary_active,'curve_summary_valid':summary_valid,'splice_pass':False,'eos_supervised':False,'result_complete':False}
 if not out['context_pass']:return out
 ids=torch.tensor([p+target],device=DEVICE);labels=torch.tensor([[-100]*len(p)+target],device=DEVICE);actual={}
 h=model.model.register_forward_pre_hook(lambda mod,args,kwargs:actual.update({'length':int(kwargs['inputs_embeds'].shape[1]),'attention':int(kwargs['attention_mask'].shape[1])}),with_kwargs=True)
 try:
  with torch.no_grad():z,sl=capture(lambda:model(input_ids=ids,attention_mask=torch.ones_like(ids),labels=labels,point_clouds=surface_t.unsqueeze(0),edge_clouds=edge))
 finally:h.remove()
 valid=sl[sl!=-100] if sl is not None else torch.empty(0,dtype=torch.long);rid=tok.encode('result =',add_special_tokens=False)
 out.update({'splice_pass':bool(torch.isfinite(z.loss)) and actual.get('length')==total and actual.get('attention')==total,'label_alignment':bool(valid.tolist()==target),'eos_supervised':bool(len(valid) and int(valid[-1])==eos),'result_complete':any(valid[i:i+len(rid)].tolist()==rid for i in range(max(0,len(valid)-len(rid)+1))),'embedding_length':actual.get('length'),'attention_length':actual.get('attention')})
 return out
def pct(vals):
 a=np.asarray(vals,float);return {k:float(np.percentile(a,q)) for k,q in [('min',0),('median',50),('p90',90),('max',100)]}

def phase_a(row,c2model):
 cid,sid=row['cad_id'],row['source_id'];base=DATA/cid;base.mkdir(parents=True,exist_ok=False);source=base/'source';source.mkdir();stage_parent=base/'_stage_parent';stage=stage_parent/cid;stage.mkdir(parents=True);cleanroot=base/'clean';noisy=base/'noisy';targetdir=base/'target';oracle=base/'oracle_curve'
 audit={**row,'clean_status':'CLEAN_REJECT','phase_a_pass':False,'primary_reject_reason':None,'secondary_reject_reasons':[],'geometry_verified':True,'single_solid':row.get('solid_count')==1}
 try:
  steps=list((ROOT/'CADFS'/'step'/sid[:4]).glob(sid+'.step'))
  if len(steps)!=1:raise RuntimeError('SOURCE_STEP_RESOLUTION')
  step=steps[0];shutil.copy2(step,source/'source.step');st=tessellate_step(step);raw,_,_=sample_surface_uniform(st['vertices'],st['faces'],8192,SEED);tf=compute_transform(raw)
  # Stage exactly the V3 pack input; target is frozen from the prior geometry screen.
  (stage/'model.step').symlink_to(source/'source.step');(stage/'source.json').write_text('{}\n');(stage/'coordinate_transform.json').write_text(json.dumps({'scale':float(tf.scale),'translation':np.asarray(tf.translation).tolist()})+'\n')
  dsl=(OLD/'screen_work'/cid/'cad_target.dsl').read_text();(stage/'program_canonical.dsl').write_text(dsl);(stage/'program.dsl').write_text(dsl)
  pack.build_one(stage,cleanroot,overwrite=False);gp=cleanroot/cid
  # Preserve clean V3 artifacts in the requested public layout.
  noisy.mkdir();cleanmesh=gp/'mesh.obj';shutil.copy2(cleanmesh,cleanroot/'mesh.obj');shutil.copy2(gp/'surface_points.npy',cleanroot/'surface_points.npy');targetdir.mkdir();shutil.copy2(gp/'cad_target.dsl',targetdir/'cad_target.dsl')
  nsrc=OUT/'noise_canary10/noisy_mesh'/LEVEL/cid
  # Noise canary only has ten IDs; this build deterministically regenerates the already frozen protocol for all candidates.
  if nsrc.exists():
   # This branch is retained only for candidate identity; actual regenerated assets must match protocol metadata.
   pass
  # import noise helper exactly from the frozen canary code, without changing its protocol.
  import importlib.util as iu
  q=iu.spec_from_file_location('cadfs_noise_impl',ROOT/'scripts/cadfs_noisy_canary10_v1.py');noise=iu.module_from_spec(q);sys.modules[q.name]=noise;q.loader.exec_module(noise)
  v=np.asarray(st['vertices'],np.float64);f=np.asarray(st['faces'],np.int64);diag=float(np.linalg.norm(v.max(0)-v.min(0)));adj=noise.mesh_adjacency(len(v),f);vn,nmeta=noise.noisy_vertices(v,f,cid,LEVEL,diag,adj)
  area_ratio=noise.area(vn,f)/max(noise.area(v,f),1e-18);bbox_delta=max(float(np.linalg.norm(vn.min(0)-v.min(0))/max(diag,1e-12)),float(np.linalg.norm(vn.max(0)-v.max(0))/max(diag,1e-12)))
  audit.update({'noise_area_ratio':area_ratio,'noise_bbox_delta_rel':bbox_delta,'noise_topology_unchanged':bool(vn.shape==v.shape and f.shape==f.shape)})
  if not (.80<=area_ratio<=1.25 and bbox_delta<=.10 and audit['noise_topology_unchanged']): raise RuntimeError('REJECT_NOISE')
  noise.obj_write(noisy/'mesh.obj',vn,f);rawn,nrm,_=sample_surface_uniform(vn,f,8192,noise.seed_for(cid,LEVEL+'_surface'));sp=np.concatenate([pack.apply_canonical(rawn,tf.scale,np.asarray(tf.translation)),nrm],axis=1).astype(np.float32);np.save(noisy/'surface_points.npy',sp);np.save(noisy/'vertices.npy',vn);np.save(noisy/'faces.npy',f);dump(noisy/'noise_meta.json',{'level':LEVEL,'sigma_over_D':.002,'protocol':str(OUT/'NOISE_PROTOCOL_V1.json'),'noise':nmeta,'clean_transform':json.loads((stage/'coordinate_transform.json').read_text())})
  # Replay final clean DSL with canonical executor, independently of old screen state.
  audit.update(execute(dsl,base/'target')); 
  if not audit['step_reload']:raise RuntimeError('GT_STEP_RELOAD')
  # Use exact C2 curve extraction / sharp-only exporter contract, but isolate all outputs.
  oldcad,oldsplit=curves.cad_dir,dict(curves.SPLITS['deepcad_train']);oldpack=exporter.PACK_ROOT['deepcad']
  try:
   curves.cad_dir=lambda split,x:oracle;curves.SPLITS['deepcad_train']['step_root']=stage_parent;curves.SPLITS['deepcad_train']['track_a_pack']=cleanroot;exporter.PACK_ROOT['deepcad']=cleanroot
   cr=curves.build_one('deepcad_train',cid,overwrite=False)
   if not cr.get('ok'):raise RuntimeError('GT_CURVES')
   ex=exporter.process_cad('deepcad',cid,oracle,c2model,DEVICE,True)
  finally:
   curves.cad_dir=oldcad;curves.SPLITS['deepcad_train'].update(oldsplit);exporter.PACK_ROOT['deepcad']=oldpack
  if ex is None:raise RuntimeError('C2_EXPORT')
  np.save(oracle/'curve_tokens.npy',ex['tokens']);dump(oracle/'curve_tokens_meta.json',ex['meta']);z=np.load(oracle/'curve_samples.npz');n=int(z['num_curves'][0]);tok=ex['tokens']
  audit.update({'source_step_sha256':sha(step),'clean_mesh_valid':bool((gp/'mesh.obj').is_file()),'noisy_mesh_valid':bool(np.isfinite(vn).all()),'noisy_surface_valid':bool(sp.shape==(8192,6) and np.isfinite(sp).all() and np.allclose(np.linalg.norm(sp[:,3:],axis=1),1,atol=1e-5)),'curve_count':n,'c2_shape':list(tok.shape),'c2_valid':bool(tok.ndim==2 and tok.shape[1]==256 and np.isfinite(tok).all()),'anchor_unused':'M2_ORACLE_NO_SPATIAL_ANCHOR'})
  if not all([audit['clean_mesh_valid'],audit['noisy_mesh_valid'],audit['noisy_surface_valid'],audit['c2_valid']]):raise RuntimeError('ASSET')
  audit['phase_a_pass']=True
 except Exception as e:audit['primary_reject_reason']=str(e).split(':',1)[0];audit['error']=(type(e).__name__+': '+str(e))[-500:]
 dump(base/'AUDIT_PHASE_A.json',audit);return audit

def phase_b(rows):
 good=[r for r in rows if r['phase_a_pass']]
 if not good:return rows
 core.heldout_geometry.install();tok=AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False)
 for arm in ('b0','m2'):
  model=core.make_model(arm,DEVICE,1.9414176940917969)
  if arm=='m2':model.edge_proj.load_state_dict(torch.load(M2/'geometry_prefix_adapter.pt',map_location=DEVICE))
  model.eval();state={};orig=core.install_precomputed_second(model,arm,state)
  try:
   for r in good:
    base=DATA/r['cad_id'];c2=np.load(base/'oracle_curve/curve_tokens.npy') if arm=='m2' else None
    r['B0' if arm=='b0' else 'M2']=audit_arm(model,state,tok,arm,base/'noisy/surface_points.npy',base/'target/cad_target.dsl',c2)
    if arm=='m2' and r['M2']['curve_summary_valid']:
     edge,mask=raw_c2(c2)
     with torch.no_grad():summary,smask=model.edge_proj(edge.to(dtype=next(model.edge_proj.parameters()).dtype),mask.unsqueeze(0))
     np.save(base/'oracle_curve/m2_summary_tokens.npy',summary.float().cpu().numpy()[0]);np.save(base/'oracle_curve/m2_summary_mask.npy',smask.cpu().numpy()[0])
  finally:core.module._splice_geometry=orig;del model;gc.collect();torch.cuda.empty_cache()
 for r in good:
  b,m=r['B0'],r['M2'];passed=all([b['context_pass'],m['context_pass'],b['splice_pass'],m['splice_pass'],b['eos_supervised'],m['eos_supervised'],b['result_complete'],m['result_complete'],m['curve_summary_valid']])
  r['clean_status']='CLEAN_PASS' if passed else 'CLEAN_REJECT'
  if not passed:r['primary_reject_reason']='V3_CONTEXT_OR_SPLICE'
  dump(DATA/r['cad_id']/'AUDIT.json',r)
 return rows

def main():
 if sha(C2)!=C2_SHA:raise RuntimeError('C2_SHA_MISMATCH')
 protocol={'NOISE_PROTOCOL_VERSION':'V1','status':'FROZEN_BY_USER','chosen_level':LEVEL,'type':'smoothed scalar field along clean vertex normals','sigma_over_bbox_diagonal':.002,'global_seed':42,'per_mesh_seed':'sha256(cad_id|N2|42)','clip':'plus_or_minus_3_sigma','smoothing_rounds':2,'connectivity':'unchanged','surface':'sampled from noisy mesh with recomputed noisy face normals','clean_target_and_oracle':'unaltered clean canonical DSL and clean final B-Rep curves','canary_report':str(OUT/'noise_canary10/audits/NOISE_CANARY10_REPORT.json')}
 dump(OUT/'NOISE_PROTOCOL_V1.json',protocol)
 dump(OUT/'audits/ATTEMPT0_INVALID_IMPLEMENTATION_EVIDENCE.json',{'status':'INVALID_ENGINEERING_ATTEMPT','data_root':str(OUT/'data100'),'reason':'pack output path was incorrectly assumed to be clean/<cad_id>, while the staging directory name was _stage; all 127 records failed before C2/context checks','candidate_or_protocol_conclusion':'NONE','legacy_data100_preserved':True})
 dump(OUT/'audits/ATTEMPT1_INVALID_IMPLEMENTATION_EVIDENCE.json',{'status':'INVALID_ENGINEERING_ATTEMPT','data_root':str(OUT/'data100_retry1'),'reason':'V3 explicit surface adapter was called with unsupported dataset label cadfs; build stopped before any CAD could receive a V3 context result','candidate_or_protocol_conclusion':'NONE','legacy_data100_retry1_preserved':True,'retry_data_root':str(DATA)})
 dump(OUT/'audits/ATTEMPT2_FINAL_AUDIT_FAILURE_EVIDENCE.json',{'status':'PROTOCOL_AUDIT_FAILURE','data_root':str(OUT/'data100_retry2'),'reason':'cadfs__00753066 has N2 area_ratio=1.4622116284198488; initial builder lacked the explicit REJECT_NOISE catastrophe gate. No training occurred.','candidate_or_protocol_conclusion':'NONE','legacy_data100_retry2_preserved':True,'retry_data_root':str(DATA)})
 rec=json.loads(ORDER.read_text())['records'];allrows=[];idx=0
 while idx<len(rec) and sum(x.get('clean_status')=='CLEAN_PASS' for x in allrows)<N:
  batch=rec[idx:idx+10];idx+=len(batch);model,_=exporter.load_backbone(C2,DEVICE);phase=[phase_a(x,model) for x in batch];del model;gc.collect();torch.cuda.empty_cache();phase=phase_b(phase);allrows.extend(phase)
  dump(OUT/'audits/PROGRESS.json',{'attempted':len(allrows),'clean':sum(x.get('clean_status')=='CLEAN_PASS' for x in allrows),'rejected':sum(x.get('clean_status')=='CLEAN_REJECT' for x in allrows),'next_frozen_order_index':idx})
  (OUT/'CADFS_NOISY100_PER_CAD.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in allrows));print(f'PROGRESS attempted={len(allrows)} clean={sum(x.get("clean_status")=="CLEAN_PASS" for x in allrows)}',flush=True)
 clean=[x for x in allrows if x.get('clean_status')=='CLEAN_PASS']
 dist={'dsl_token':pct([x['M2']['dsl_tokens'] for x in clean]),'surface_token':pct([x['M2']['surface_token_count'] for x in clean]),'curve_count':pct([x['curve_count'] for x in clean]),'m2_real_length':pct([x['M2']['real_total'] for x in clean])} if clean else {}
 manifest=OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.json';manifest.write_text(json.dumps({'protocol':protocol,'records':clean,'attempted':len(allrows),'clean':len(clean),'rejections':[x for x in allrows if x.get('clean_status')!='CLEAN_PASS'],'distribution':dist},indent=2)+'\n')
 final={'CURRENT_GATE':'CADFS_NOISY_OVERFIT100_DATA_READY' if len(clean)==100 else 'CADFS_NOISY_OVERFIT100_DATA_INSUFFICIENT','TRAINING_APPROVED':'YES' if len(clean)==100 else 'NO','training_started':False,'decode_started':False,'count':len(clean),'attempted':len(allrows),'distribution':dist,'manifest':str(manifest),'manifest_sha256':sha(manifest),'MAIN_BLOCKER':None if len(clean)==100 else 'frozen verified pool exhausted before 100 complete V3 samples','NEXT_STEP':'stop; no automatic training'}
 dump(OUT/'FINAL_REPORT.json',final);print(json.dumps(final,indent=2))
if __name__=='__main__':main()
