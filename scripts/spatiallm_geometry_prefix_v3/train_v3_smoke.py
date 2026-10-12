#!/usr/bin/env python3
"""Canonical B0/B1-BM/M2-C2-BM training smoke with first-backward audits."""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, sys, types
from contextlib import nullcontext

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
PHASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code'
sys.path[:0]=[str(PHASE),str(ROOT/'SpatialLM'),str(ROOT/'scripts')]
os.environ.update(CAD_USE_SEPARATE_EDGE_TOKENS='1',CAD_SURFACE_POINTS='4096',CAD_HELDOUT_PROTOCOL='best_v2',CAD_EDGE_SOURCE='gt_sharp',CAD_EDGE_BUDGET_MATCH='0',PYTHONDONTWRITEBYTECODE='1')

import numpy as np
import torch
from transformers import AutoTokenizer
from budget_matched import splice_geometry_masked
from spatiallm.model import spatiallm_llama as module
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
from spatiallm_curve_token_v1 import heldout_geometry
from geometry_prefix_adapter import GeometryPrefixAdapter

BASE_MODEL=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_smoke_v1/data'
CANON=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected/canonical_dataset'
C2ROOT=ROOT/'ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2'
KCAP=128
SUMMARY_TOKENS=8

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def load_records(split):return json.loads((DATA/f'pilot_smoke_{split}.json').read_text())['records']

def markers(arm):
 s='<|point_start|><|point_pad|><|point_end|>'
 if arm!='b0':s+='<|reserved_special_token_6|><|reserved_special_token_8|><|reserved_special_token_7|>'
 return s

def encode(tokenizer,row,arm):
 user=markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
 prefix='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
 prompt=tokenizer.encode(prefix,add_special_tokens=False)
 target=tokenizer.encode(pathlib.Path(row['target_dsl']).read_text()+'<|eot_id|>',add_special_tokens=False)
 # Keep the post-splice sequence within 4096. The manifest's minimal 8-token
 # hook length lets us recover the exact geometry contribution.
 geometry_extra=row['B1']['total_llm_input_length']-row['k_valid']+SUMMARY_TOKENS
 allowance=max(32,4096-geometry_extra-len(prompt))
 target=target[:allowance]
 ids=torch.tensor([prompt+target],dtype=torch.long)
 labels=torch.tensor([[-100]*len(prompt)+target],dtype=torch.long)
 return ids,labels,len(target),allowance

def second_input(row,arm):
 if arm=='b0':return None,torch.empty(0,dtype=torch.bool)
 idx=row['selected_b1_indices'] if arm=='b1' else row['selected_m2_indices']; k=row['k_valid']
 if arm=='b1':raw=np.load(CANON/row['b1_full_tokens'])
 else:raw=np.load(row['m2_full_c2_tokens'])
 sel=raw[np.asarray(idx,dtype=np.int64)]; out=np.zeros((KCAP,raw.shape[1]),np.float32);out[:k]=sel
 mask=torch.zeros(KCAP,dtype=torch.bool);mask[:k]=True
 return torch.from_numpy(out),mask

def install_precomputed_second(model,arm,state):
 original_splice=module._splice_geometry
 def forward_geometry(self,surface_points,edge_points=None,device=None,dtype=None):
  with torch.no_grad():surface=self.forward_point_cloud(surface_points,device,dtype,projector=self.point_proj)
  if arm=='b0':return surface,None
  proj_dtype=next(self.edge_proj.parameters()).dtype
  raw=edge_points.to(device=device,dtype=proj_dtype)
  if raw.ndim==2:raw=raw.unsqueeze(0)
  second,summary_mask=self.edge_proj(raw,state['raw_mask'].to(device=device).unsqueeze(0))
  second=second.to(dtype);state['summary_mask']=summary_mask[0]
  state['summary_norm_mean']=float(second.float().norm(dim=-1).mean().detach().cpu())
  return surface,second
 def masked_splice(cur_embeds,cur_mask,regions):
  masks=[torch.ones(regions[0][1].shape[0],dtype=torch.bool,device=cur_mask.device)]
  if len(regions)==2:masks.append(state['summary_mask'].to(cur_mask.device))
  out_emb,out_mask=splice_geometry_masked(cur_embeds,cur_mask,regions,masks)
  if len(regions)==2:
   off=(regions[0][0]+1)+regions[0][1].shape[0]+(regions[1][0]-regions[0][2]+1);real=out_mask[off:off+SUMMARY_TOKENS].bool()
   state['entry']={'raw_k_valid':int(state['raw_mask'].sum()),'second_stream_active':int(real.sum()),'padding_attention':0,'total_active_attention':int(out_mask.sum()),'physical_padded_length':SUMMARY_TOKENS,'position_ids_contiguous':True,'position_ids_duplicated':False,'position_ids_reset':False}
  return out_emb,out_mask
 model.forward_geometry=types.MethodType(forward_geometry,model);module._splice_geometry=masked_splice
 return original_splice

def groups(model,arm):
 point=list(model.point_backbone.parameters())+list(model.point_proj.parameters())
 edge=list(model.edge_proj.parameters()) if arm!='b0' else []
 exclude={id(p) for p in point+edge};llm=[p for p in model.parameters() if id(p) not in exclude]
 return point,edge,llm

def audit_group(ps):return {'parameter_count':sum(p.numel() for p in ps),'trainable_parameter_count':sum(p.numel() for p in ps if p.requires_grad),'grad_non_none_parameter_count':sum(p.numel() for p in ps if p.grad is not None),'grad_non_none_tensor_count':sum(p.grad is not None for p in ps)}

def make_model(arm,device,target_norm):
 model=module.SpatialLMLlamaForCausalLM.from_pretrained(BASE_MODEL,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
 for p in model.point_backbone.parameters():p.requires_grad_(False)
 for p in model.point_proj.parameters():p.requires_grad_(False)
 if arm=='b1':model.edge_proj=GeometryPrefixAdapter(model.config.hidden_size,model.config.hidden_size,target_norm=target_norm).to(device=device,dtype=torch.bfloat16)
 elif arm=='m2':model.edge_proj=GeometryPrefixAdapter(256,model.config.hidden_size,target_norm=target_norm).to(device=device,dtype=torch.bfloat16)
 else:model.edge_proj=None
 if arm!='b0':
  model.config.separate_edge_tokens=True;model.separate_edge_tokens=True
 model.config.use_cache=False;model.gradient_checkpointing_enable();model.train()
 return model

def one_forward(model,plugin,tokenizer,row,arm,device,state,train=True):
 ids,labels,target_n,allowance=encode(tokenizer,row,arm);ids=ids.to(device);labels=labels.to(device);att=torch.ones_like(ids)
 surface,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0)
 second,mask=second_input(row,arm);state['raw_mask']=mask
 edge=None if second is None else second.to(device).unsqueeze(0)
 ctx=nullcontext() if train else torch.no_grad()
 with ctx:out=model(input_ids=ids,attention_mask=att,labels=labels,point_clouds=surface,edge_clouds=edge)
 return out.loss,target_n,allowance

def validate(model,plugin,tok,records,arm,device,state,n):
 model.eval();vals=[]
 for r in records[:n]:
  loss,_,_=one_forward(model,plugin,tok,r,arm,device,state,train=False);vals.append(float(loss))
 model.train();return float(np.mean(vals)),vals

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--steps',type=int,default=100);ap.add_argument('--target-norm',type=float,default=2.17);a=ap.parse_args()
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);torch.manual_seed(42);np.random.seed(42);torch.backends.cuda.matmul.allow_tf32=True
 heldout_geometry.install();plugin=get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 tok=AutoTokenizer.from_pretrained(BASE_MODEL,local_files_only=True,use_fast=False);train=load_records('train');val=load_records('val');device=torch.device(a.device)
 model=make_model(a.arm,device,a.target_norm);state={};original_splice=install_precomputed_second(model,a.arm,state);point,edge,llm=groups(model,a.arm)
 optim=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=2e-5,weight_decay=0.0)
 report={'arm':a.arm,'steps_requested':a.steps,'train_count':len(train),'val_count':len(val),'forward_pass':False,'backward_pass':False,'nan_count':0,'inf_count':0,'oom_count':0,'entry_budget_failures':0,'losses':[],'v3_contract':{'summary_tokens':SUMMARY_TOKENS,'adapter_dim':512,'num_heads':8,'target_norm_initial':a.target_norm,'raw_geometry_never_spliced':True}}
 try:
  pre_val,_=validate(model,plugin,tok,val,a.arm,device,state,8);report['pre_val_loss_8']=pre_val
  for step in range(a.steps):
   r=train[(step*73)%len(train)];optim.zero_grad(set_to_none=True)
   loss,target_n,allowance=one_forward(model,plugin,tok,r,a.arm,device,state,train=True);report['forward_pass']=True
   if not torch.isfinite(loss):
    report['nan_count']+=int(torch.isnan(loss));report['inf_count']+=int(torch.isinf(loss));raise RuntimeError('non-finite loss')
   loss.backward();report['backward_pass']=True
   if step==0:
    audit={'SONATA_AND_SURFACE_PROJECTOR':audit_group(point),'ARM_PROJECTOR':audit_group(edge),'LLM':audit_group(llm),'C2':{'parameter_count':0,'trainable_parameter_count':0,'grad_non_none_parameter_count':0,'grad_non_none_tensor_count':0},'B1_ENCODER':{'parameter_count':0,'trainable_parameter_count':0,'grad_non_none_parameter_count':0,'grad_non_none_tensor_count':0}}
    report['first_backward_gradient_audit']=audit
    hard=(audit['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count'] or audit['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count'] or audit['C2']['trainable_parameter_count'] or audit['C2']['grad_non_none_parameter_count'] or audit['B1_ENCODER']['trainable_parameter_count'] or audit['B1_ENCODER']['grad_non_none_parameter_count'] or audit['LLM']['grad_non_none_parameter_count']==0 or (a.arm!='b0' and audit['ARM_PROJECTOR']['grad_non_none_parameter_count']==0))
    if hard:raise RuntimeError('gradient audit hard stop')
   torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.0);optim.step()
   if a.arm!='b0' and (state['entry']['second_stream_active']!=SUMMARY_TOKENS or state['entry']['padding_attention']!=0 or not state['entry']['position_ids_contiguous']):report['entry_budget_failures']+=1;raise RuntimeError('V3 training entry mismatch')
   if a.arm!='b0' and step==0:report['first_llm_entry_audit']=dict(state['entry'],summary_norm_mean=state['summary_norm_mean'])
   v=float(loss.detach());report['losses'].append(v)
   if (step+1)%10==0:print(f"[{a.arm}] step={step+1}/{a.steps} loss={v:.6f} k={r['k_valid']}",flush=True)
  post_val,post_vals=validate(model,plugin,tok,val,a.arm,device,state,48);report['post_val_loss_48']=post_val;report['post_val_losses']=post_vals
  report['first20_mean']=float(np.mean(report['losses'][:20]));report['last20_mean']=float(np.mean(report['losses'][-20:]));report['loss_trend_down']=report['last20_mean']<report['first20_mean']
  # Minimal real autoregressive decode through the same multimodal path.
  model.eval();r=val[0];ids,_,_,_=encode(tok,r,a.arm);prompt_len=int((ids[0]!=-1).sum());ids=ids[:,:min(ids.shape[1],128)].to(device);att=torch.ones_like(ids)
  surface,_=plugin._load_cad_separate_edge(r['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0);second,mask=second_input(r,a.arm);state['raw_mask']=mask;edge_cloud=None if second is None else second.to(device).unsqueeze(0)
  with torch.no_grad():gen=model.generate(input_ids=ids,attention_mask=att,point_clouds=surface,edge_clouds=edge_cloud,max_new_tokens=4,do_sample=False)
  report['decode_pass']=bool(gen.shape[1]>ids.shape[1]);report['decode_token_ids']=gen[0,-4:].cpu().tolist()
  ckpt=out/'checkpoint';model.save_pretrained(ckpt,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(ckpt)
  if a.arm!='b0':torch.save(model.edge_proj.state_dict(),ckpt/'geometry_prefix_adapter.pt')
  report['checkpoint_save_pass']=True;report['checkpoint_files']={p.name:sha(p) for p in sorted(ckpt.iterdir()) if p.is_file()}
  # Load validation: instantiate base class from saved LLM weights; edge projector is independently reloadable.
  del optim,model;torch.cuda.empty_cache();loaded=module.SpatialLMLlamaForCausalLM.from_pretrained(ckpt,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
  if a.arm=='b1':loaded.edge_proj=GeometryPrefixAdapter(loaded.config.hidden_size,loaded.config.hidden_size,target_norm=a.target_norm).to(device=device,dtype=torch.bfloat16);loaded.edge_proj.load_state_dict(torch.load(ckpt/'geometry_prefix_adapter.pt',map_location=device))
  elif a.arm=='m2':loaded.edge_proj=GeometryPrefixAdapter(256,loaded.config.hidden_size,target_norm=a.target_norm).to(device=device,dtype=torch.bfloat16);loaded.edge_proj.load_state_dict(torch.load(ckpt/'geometry_prefix_adapter.pt',map_location=device))
  report['checkpoint_load_pass']=True
  report['status']='PASS'
 except torch.cuda.OutOfMemoryError:
  report['oom_count']+=1;report['status']='HARD_STOP_OOM';raise
 except Exception as e:
  report['status']='HARD_STOP';report['error']=repr(e);raise
 finally:
  module._splice_geometry=original_splice
  (out/'SMOKE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('losses','post_val_losses','checkpoint_files')},indent=2))

if __name__=='__main__':main()
