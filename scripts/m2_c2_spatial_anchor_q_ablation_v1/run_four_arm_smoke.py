#!/usr/bin/env python3
"""Unified Q-ablation smoke runner.  Phase 1 dry-run only; no optimizer step."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, types
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0]=[str(ROOT/'scripts/spatiallm_geometry_prefix_v3'),str(ROOT/'scripts/spatiallm_m2_spatial_anchor_v1'),str(ROOT/'scripts'),str(ROOT/'SpatialLM'),str(ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code')]
import numpy as np
import torch
from transformers import AutoTokenizer
import train_v3_smoke as v3
from geometry_prefix_adapter import GeometryPrefixAdapter
from spatiallm_m2_spatial_anchor_v1.m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1

BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
TRAIN=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json'
C2=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
ARMS={'A0_NOANCHOR_Q8':(False,8),'A1_ANCHOR_Q8':(True,8),'A2_ANCHOR_Q16':(True,16),'A3_ANCHOR_Q32':(True,32)}
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def anchor_for(row):
 z=np.load(row['m2_full_curves'],allow_pickle=True); xyz=z['curve_xyz'][np.asarray(row['selected_m2_indices'])]; vs=[]
 for s in (Path(row['target_dsl']).parent/'mesh.obj').read_text().splitlines():
  if s.startswith('v '):vs.append([float(v) for v in s.split()[1:4]])
 v=np.asarray(vs,np.float32); lo,hi=v.min(0),v.max(0); d=max(float(np.max(hi-lo)),1e-8); a=np.concatenate([(xyz.mean(1)-(lo+hi)/2)/d,(xyz.max(1)-xyz.min(1))/d],1).astype(np.float32); out=np.zeros((128,6),np.float32);out[:len(a)]=a;return torch.from_numpy(out)
def gstat(ps):
 ps=list(ps); gs=[p.grad.detach().float() for p in ps if p.grad is not None]; return {'trainable_param_count':sum(p.numel() for p in ps if p.requires_grad),'params_with_grad':len(gs),'grad_norm':float(torch.sqrt(sum((g*g).sum() for g in gs)).cpu()) if gs else 0.0,'max_abs_grad':max((float(g.abs().max().cpu()) for g in gs),default=0.0)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=ARMS,required=True);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--single-batch',action='store_true');ap.add_argument('--max-steps',type=int,default=0);ap.add_argument('--output');ap.add_argument('--device',default='cuda:0');a=ap.parse_args()
 if a.max_steps:
  if not a.output:raise SystemExit('--output is required with --max-steps')
  from run_four_arm_100step_impl import run
  run(a.arm,a.max_steps,a.device,a.output)
  return
 use_anchor,q=ARMS[a.arm]; rec=json.loads(TRAIN.read_text())['records']; row=rec[0]; device=torch.device(a.device)
 # C2 is offline/frozen: checkpoint is verified but never loaded into this runner.
 assert sha(C2)=='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
 model=v3.module.SpatialLMLlamaForCausalLM.from_pretrained(BASE,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
 for p in model.point_backbone.parameters():p.requires_grad_(False)
 for p in model.point_proj.parameters():p.requires_grad_(False)
 adapter=GeometryPrefixAdapter(256,model.config.hidden_size,num_queries=q,target_norm=1.9414).to(device=device,dtype=torch.bfloat16)
 # Explicitly assert/move every nested attention parameter; avoids silent CPU
 # placement when the base model was loaded through accelerate device_map.
 adapter.to(device=device,dtype=torch.bfloat16)
 branch=M2C2SpatialAnchorV1(adapter).to(device=device,dtype=torch.bfloat16) if use_anchor else adapter
 branch.to(device=device,dtype=torch.bfloat16)
 raw=np.load(row['m2_full_c2_tokens']);idx=np.asarray(row['selected_m2_indices'],np.int64);k=row['k_valid']; padded=np.zeros((128,256),np.float32);padded[:k]=raw[idx];mask=torch.zeros(128,dtype=torch.bool);mask[:k]=True
 # Anchor contract is assessed from raw curves under a frozen object-frame placeholder only in dry-run; no LLM call/optimizer occurs.
 anchors=anchor_for(row).unsqueeze(0).to(device=device,dtype=torch.bfloat16)
 x=torch.from_numpy(padded).unsqueeze(0).to(device=device,dtype=torch.bfloat16); mask=mask.to(device)
 with torch.no_grad():summary,smask=(branch(x,anchors,mask.unsqueeze(0)) if use_anchor else branch(x,mask.unsqueeze(0)))
 audit={'ARM':a.arm,'USE_ANCHOR':use_anchor,'NUM_QUERIES':q,'TRAIN_SPLIT_PATH':str(TRAIN),'TRAIN_COUNT':len(rec),'ANCHOR_EVAL_100_LOADED':False,'PILOT150_LOADED':False,'OFFICIAL_TEST_LOADED':False,'C2_FROZEN':True,'SONATA_FROZEN':True,'SURFACE_PROJECTOR_FROZEN':True,'RAW_CURVE_SHAPE':list(x.shape),'C2_TOKEN_SHAPE':list(x.shape),'ANCHOR_SHAPE':list(anchors.shape),'SUMMARY_TOKEN_SHAPE':list(summary.shape),'SUMMARY_MASK_SHAPE':list(smask.shape),'A0_ANCHOR_ABSENT':not use_anchor,'ANCHOR_PRESENT':use_anchor,'DRY_RUN_PASS':list(summary.shape)==[1,q,model.config.hidden_size]}
 if not a.single_batch:
  print(json.dumps(audit,indent=2))
  if not audit['DRY_RUN_PASS']:raise SystemExit(2)
  return
 state={'raw_mask':mask,'anchors':anchors[0]};original=v3.module._splice_geometry
 def forward_geometry(self,surface_points,edge_points=None,device=None,dtype=None):
  with torch.no_grad():surface=self.forward_point_cloud(surface_points,device,dtype,projector=self.point_proj)
  z=edge_points.to(device=device,dtype=next(branch.parameters()).dtype);z=z if z.ndim==3 else z.unsqueeze(0);vm=state['raw_mask'].to(device).unsqueeze(0)
  second,sm=(branch(z,state['anchors'].to(device=device,dtype=z.dtype).unsqueeze(0),vm) if use_anchor else branch(z,vm));state['summary']=second;state['summary_mask']=sm[0];return surface,second.to(dtype)
 def splice(e,m,regions):
  masks=[torch.ones(regions[0][1].shape[0],dtype=torch.bool,device=m.device),state['summary_mask'].to(m.device)];out,am=v3.splice_geometry_masked(e,m,regions,masks);state['attention']=am;return out,am
 model.edge_proj=branch;model.config.separate_edge_tokens=True;model.separate_edge_tokens=True;model.config.use_cache=False;model.gradient_checkpointing_enable();model.train();model.forward_geometry=types.MethodType(forward_geometry,model);v3.module._splice_geometry=splice
 try:
  tok=AutoTokenizer.from_pretrained(BASE,local_files_only=True,use_fast=False);plugin=v3.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);ids,labels,_,_=v3.encode(tok,row,'m2');ids,labels=ids.to(device),labels.to(device);att=torch.ones_like(ids);surface,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0);out=model(input_ids=ids,attention_mask=att,labels=labels,point_clouds=surface,edge_clouds=x);loss=out.loss;loss.backward()
  with torch.no_grad():probe=model(input_ids=ids,attention_mask=att,point_clouds=surface,edge_clouds=x,num_logits_to_keep=1)
 finally:v3.module._splice_geometry=original
 point=list(model.point_backbone.parameters());surfproj=list(model.point_proj.parameters());branchp=list(branch.parameters());exclude={id(p) for p in point+surfproj+branchp};llm=[p for p in model.parameters() if id(p) not in exclude];g={'SONATA':gstat(point),'SURFACE_PROJECTOR':gstat(surfproj),'C2':gstat([]),'GEOMETRY_PREFIX_ADAPTER':gstat(adapter.parameters()),'ANCHOR_MLP':gstat(branch.anchor_mlp.parameters()) if use_anchor else None,'LLAMA':gstat(llm)}
 audit.update({'REAL_LLM_FORWARD':True,'BACKWARD_COMPLETE':True,'LOSS':float(loss.detach()),'LOSS_FINITE':bool(torch.isfinite(loss)),'NAN_COUNT':int(torch.isnan(loss)),'INF_COUNT':int(torch.isinf(loss)),'LLM_LOGITS_FINITE':bool(torch.isfinite(probe.logits).all()),'SUMMARY_TOKEN_SHAPE':list(state['summary'].shape),'LLM_INPUT_SHAPE':list(ids.shape),'LABELS_SHAPE':list(labels.shape),'LLM_ATTENTION_MASK_SHAPE':list(state['attention'].shape),'GRADIENT':g,'ANCHOR_EVAL_100_MODEL_READ':False,'PILOT150_MODEL_READ':False,'OFFICIAL_TEST_READ':False});audit['MASK_CONTRACT_PASS']=state['summary'].shape[1]==q;audit['GRADIENT_OWNERSHIP_PASS']=g['SONATA']['grad_norm']==0 and g['SURFACE_PROJECTOR']['grad_norm']==0 and g['C2']['grad_norm']==0 and g['GEOMETRY_PREFIX_ADAPTER']['grad_norm']>0 and g['LLAMA']['grad_norm']>0 and (not use_anchor or g['ANCHOR_MLP']['grad_norm']>0);audit['SINGLE_BATCH_PASS']=audit['LOSS_FINITE'] and audit['LLM_LOGITS_FINITE'] and audit['MASK_CONTRACT_PASS'] and audit['GRADIENT_OWNERSHIP_PASS'];print(json.dumps(audit,indent=2))
 if a.output:Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(audit,indent=2)+'\n')
 if not audit['SINGLE_BATCH_PASS']:raise SystemExit(2)
if __name__=='__main__':main()
