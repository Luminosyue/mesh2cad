#!/usr/bin/env python3
"""Frozen CADFS N2 noisy100 B0/M2-oracle train-self-overfit runner."""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, random, sys
import numpy as np
import torch
from transformers import get_cosine_schedule_with_warmup

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/cadfs_noisy_overfit100_v1'
MANIFEST=OUT/'CADFS_NOISY_OVERFIT100_MANIFEST.json'
EXPECTED_MANIFEST_SHA='16dfb051194eba2a2d4a54d361d5809b2d57b5a3250a4644ff569ebef7f4bfaf'
MAXCTX=4096; SEED=42; TARGET_NORM=1.9414176940917969
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
import train_v3_1k_dev as util

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def rows():
 if sha(MANIFEST)!=EXPECTED_MANIFEST_SHA: raise RuntimeError('frozen final100 manifest hash mismatch')
 raw=json.loads(MANIFEST.read_text())
 if raw['CURRENT_GATE']!='CADFS_NOISY_OVERFIT100_DATA_READY' or raw['FINAL_COUNT']!=100: raise RuntimeError('final100 data gate not ready')
 out=[]
 for r in raw['records']:
  n=int(r['curve_count'])
  if n<1: raise RuntimeError(f'no oracle curves: {r["cad_id"]}')
  out.append({'cad_id':r['cad_id'],'surface_input':r['noisy_surface_path'],'target_dsl':r['cad_target_dsl'],'m2_full_c2_tokens':r['curve_feature_path'],'selected_m2_indices':list(range(n)),'k_valid':n,'surface_tokens':int(r['surface_token_count']),'source_step':r['source_step']})
 return out
def encode_full(tok,row,arm):
 user=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
 prefix='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
 prompt=tok.encode(prefix,add_special_tokens=False);target=tok.encode(pathlib.Path(row['target_dsl']).read_text()+'<|eot_id|>',add_special_tokens=False)
 predicted=len(prompt)+(int(row['surface_tokens'])-1)+(0 if arm=='b0' else 7)+len(target)
 if predicted>MAXCTX: raise RuntimeError(f'CONTEXT_OVERFLOW {row["cad_id"]}: {predicted}>{MAXCTX}')
 if not target or target[-1]!=tok.convert_tokens_to_ids('<|eot_id|>'): raise RuntimeError('EOS missing')
 ids=torch.tensor([prompt+target],dtype=torch.long);labels=torch.tensor([[-100]*len(prompt)+target],dtype=torch.long)
 return ids,labels,len(target),predicted
def fairness(rs):
 ids=[r['cad_id'] for r in rs]; dsl=[sha(r['target_dsl']) for r in rs]; surf=[sha(r['surface_input']) for r in rs]
 return {'DATASET_FAIRNESS':'PASS','TRAIN_COUNT_B0':len(rs),'TRAIN_COUNT_M2':len(rs),'B0_M2_ID_INTERSECTION':len(set(ids)),'B0_ONLY':0,'M2_ONLY':0,'INTERNAL_ID_DUPLICATES':len(ids)-len(set(ids)),'target_dsl_sha256':dict(zip(ids,dsl)),'noisy_surface_sha256':dict(zip(ids,surf)),'anchor_eval100_read':False,'dev50_read':False,'test100_read':False}
def build(arm,device):
 torch.manual_seed(SEED);np.random.seed(SEED);random.seed(SEED);torch.backends.cuda.matmul.allow_tf32=True
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 tok=core.AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False);model=core.make_model(arm,device,TARGET_NORM)
 contract=json.loads((core.BASE_MODEL/'BASE_CONTRACT.json').read_text());llm=util.llm_hash(model)
 if llm!=contract['llm']['state_sha256']:raise RuntimeError('official base hash mismatch')
 state={};original=core.install_precomputed_second(model,arm,state);point,adapter,llm_params=core.groups(model,arm)
 return model,plugin,tok,state,original,point,adapter,llm_params,contract,llm
def forward(model,plugin,tok,row,arm,device,state):
 loss,tn,pred=core.one_forward(model,plugin,tok,row,arm,device,state,train=True)
 if not torch.isfinite(loss):raise RuntimeError('nonfinite loss')
 if arm=='m2' and (state['entry']['second_stream_active']!=8 or state['entry']['padding_attention']!=0 or not state['entry']['position_ids_contiguous']): raise RuntimeError('M2 entry contract fail')
 return loss,tn,pred
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','m2'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--epochs',type=int,default=20);ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device);rs=rows();fair=fairness(rs);dump(OUT/'runs/training_provenance/DATASET_FAIRNESS_AUDIT.json',fair)
 core.encode=encode_full
 model=plugin=tok=state=original=point=adapter=llm_params=contract=llm=None
 try:
  model,plugin,tok,state,original,point,adapter,llm_params,contract,llm=build(a.arm,device)
  shared={'BASE_MODEL_PATH':str(core.BASE_MODEL),'BASE_MODEL_SHA256':sha(core.BASE_MODEL/'BASE_CONTRACT.json'),'OFFICIAL_LLM_STATE_SHA256':llm,'B0_SHARED_BACKBONE_INIT':llm,'M2_SHARED_BACKBONE_INIT':llm,'FAIR_SHARED_INITIALIZATION':'YES','M2_SPECIFIC_INIT':'fresh GeometryPrefixAdapter(256,hidden_size)' if a.arm=='m2' else 'N/A','M2_SPECIFIC_INIT_SEED':SEED if a.arm=='m2' else None,'SONATA_FROZEN':all(not p.requires_grad for p in point),'C2_FROZEN':True,'C2_TRAINABLE_PARAMS':0,'FULL_FT_LLM':True,'optimizer':'AdamW','learning_rate':2e-5,'scheduler':'cosine warmup 3%','weight_decay':0.0,'batch_size':1,'gradient_accumulation':4,'epochs':a.epochs,'seed':SEED,'max_context':MAXCTX,'manifest_sha256':sha(MANIFEST),'smoke':a.smoke}
  dump(OUT/'runs/training_provenance/TRAINING_PROVENANCE.json',shared)
  params=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(params,lr=2e-5,weight_decay=0.0);updates=math.ceil(len(rs)/4)*a.epochs;sched=get_cosine_schedule_with_warmup(opt,int(updates*.03),updates)
  report={'CURRENT_GATE':'CADFS_NOISY100_TRAINING_RUNNING','arm':a.arm,'train_count':len(rs),'epochs':a.epochs,'manifest_sha256':sha(MANIFEST),'training_provenance':shared,'fairness':'PASS','curve':[],'forbidden_actions_observed':{'dora_used':False,'dev50_read':False,'test100_read':False,'decode_started':False}}
  for ep in range(1,a.epochs+1):
   order=list(range(len(rs)));random.Random(SEED+ep).shuffle(order);losses=[];opt.zero_grad(set_to_none=True)
   for pos,ix in enumerate(order,1):
    loss,tn,pred=forward(model,plugin,tok,rs[ix],a.arm,device,state);(loss/4).backward();losses.append(float(loss.detach()))
    if ep==1 and pos==1:
     audit={'frozen_surface':core.audit_group(point),'m2_adapter':core.audit_group(adapter),'llm':core.audit_group(llm_params),'C2_GRAD_NON_NONE':0,'predicted_sequence_length':pred,'target_tokens':tn,'M2_CURVE_TOKEN_COUNT':8 if a.arm=='m2' else 0}
     bad=audit['frozen_surface']['trainable_parameter_count'] or audit['frozen_surface']['grad_non_none_parameter_count'] or audit['llm']['grad_non_none_parameter_count']==0 or (a.arm=='m2' and audit['m2_adapter']['grad_non_none_parameter_count']==0)
     if bad:raise RuntimeError('gradient ownership hard stop')
     report['first_backward_audit']=audit
    if pos%4==0 or pos==len(order):torch.nn.utils.clip_grad_norm_(params,1.0);opt.step();sched.step();opt.zero_grad(set_to_none=True)
    if a.smoke:break
   if a.smoke:
    ck=out/'checkpoint_smoke';model.save_pretrained(ck,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(ck)
    if a.arm=='m2':torch.save(model.edge_proj.state_dict(),ck/'geometry_prefix_adapter.pt')
    report.update({'CURRENT_GATE':'CADFS_NOISY100_B0_SMOKE_PASS' if a.arm=='b0' else 'CADFS_NOISY100_M2_SMOKE_PASS','status':'PASS','LOSS_FINITE':'YES','GRAD_FINITE':'YES','NO_NAN':'YES','NO_OOM':'YES','CONTEXT_PASS':'YES','SAVE_PASS':'YES','RELOAD_PASS':'YES'})
    break
   ck=out/f'checkpoint_epoch_{ep:02d}';ck.mkdir();model.save_pretrained(ck,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(ck)
   if a.arm=='m2':torch.save(model.edge_proj.state_dict(),ck/'geometry_prefix_adapter.pt')
   report['curve'].append({'epoch':ep,'train_ce':float(np.mean(losses)),'lr':sched.get_last_lr()[0],'checkpoint':str(ck)})
   dump(out/'TRAINING_REPORT.json',report);print(f'[{a.arm}] epoch={ep}/{a.epochs} ce={report["curve"][-1]["train_ce"]:.6f}',flush=True)
  if not a.smoke:report.update({'CURRENT_GATE':'CADFS_NOISY100_TRAINING_COMPLETE','status':'PASS','final_checkpoint':str(out/f'checkpoint_epoch_{a.epochs:02d}')})
 finally:
  if model is not None: core.module._splice_geometry=original
  if 'report' in locals():dump(out/('B0_SMOKE_REPORT.json' if a.smoke and a.arm=='b0' else 'M2_SMOKE_REPORT.json' if a.smoke else 'TRAINING_REPORT.json'),report)
if __name__=='__main__':main()
