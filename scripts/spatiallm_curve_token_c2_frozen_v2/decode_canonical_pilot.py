#!/usr/bin/env python3
"""Greedy decode the frozen pilot val split from a best-val checkpoint only."""
from __future__ import annotations
import argparse,ast,json,pathlib,sys,types
import numpy as np
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
CODE=ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2';sys.path.insert(0,str(CODE))
import train_canonical_smoke as core

DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data'

def prompt_ids(tok,row,arm):
 ids,labels,_,_=core.encode(tok,row,arm); n=int((labels[0]==-100).sum());return ids[:,:n]

def load_model(arm,ckpt,device):
 model=core.module.SpatialLMLlamaForCausalLM.from_pretrained(ckpt,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
 if arm=='b1':model.edge_proj=torch.nn.Linear(model.config.hidden_size,model.config.hidden_size,bias=False,dtype=torch.bfloat16,device=device);model.edge_proj.load_state_dict(torch.load(ckpt/'arm_projector.pt',map_location=device))
 elif arm=='m2':model.edge_proj=core.build_curve_projector(256,model.config.hidden_size).to(device=device,dtype=torch.bfloat16);model.edge_proj.load_state_dict(torch.load(ckpt/'arm_projector.pt',map_location=device))
 if arm!='b0':model.config.separate_edge_tokens=True;model.separate_edge_tokens=True
 model.eval();model.config.use_cache=True;return model

def parse_success(text):
 cleaned=text.strip()
 if cleaned.startswith('```'):
  lines=cleaned.splitlines();lines=lines[1:];
  if lines and lines[-1].strip().startswith('```'):lines=lines[:-1]
  cleaned='\n'.join(lines)
 try:ast.parse(cleaned);return True
 except (SyntaxError,ValueError):return False

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--max-new-tokens',type=int,default=2048);a=ap.parse_args()
 run=pathlib.Path(a.run);best=json.loads((run/'BEST_CHECKPOINT.json').read_text());ckpt=pathlib.Path(best['path']);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False)
 report={'arm':a.arm,'split':'pilot_1k_val','official_test_read':False,'val_count':200,'best_epoch':best['epoch'],'best_val_ce':best['val_ce'],'checkpoint':str(ckpt),'max_new_tokens':a.max_new_tokens,'do_sample':False,'eos_token_id':[128001,128008,128009],'pad_token_id':128001,'completed':0,'truncated':0,'status':'RUNNING'}
 (out/'DECODE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=core.AutoTokenizer.from_pretrained(ckpt,local_files_only=True,use_fast=False);device=torch.device(a.device);model=load_model(a.arm,ckpt,device);state={};original=core.install_precomputed_second(model,a.arm,state)
 rows=json.loads((DATA/'pilot_1k_val.json').read_text())['records'];jsonl=out/'predictions.jsonl'
 try:
  with jsonl.open('w') as f:
   for i,row in enumerate(rows,1):
    ids=prompt_ids(tok,row,a.arm).to(device);att=torch.ones_like(ids);surface,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0);second,mask=core.second_input(row,a.arm);state['mask']=mask;edge=None if second is None else second.to(device).unsqueeze(0)
    with torch.no_grad():gen=model.generate(input_ids=ids,attention_mask=att,point_clouds=surface,edge_clouds=edge,max_new_tokens=a.max_new_tokens,do_sample=False,use_cache=True,eos_token_id=[128001,128008,128009],pad_token_id=128001)
    new=gen[0,ids.shape[1]:].cpu();text=tok.decode(new,skip_special_tokens=True);truncated=int(new.numel()>=a.max_new_tokens);report['truncated']+=truncated
    target_text=pathlib.Path(row['target_dsl']).read_text();target_len=len(tok.encode(target_text,add_special_tokens=False));tail=new[-100:].tolist();eos=bool(new.numel() and int(new[-1]) in (128001,128008,128009))
    rec={'cad_id':row['cad_id'],'source_dataset':row['source_dataset'],'difficulty_bin':row['difficulty_bin'],'k_valid':row['k_valid'],'target_token_length':target_len,'generated_token_length':int(new.numel()),'hit_max_new_tokens':bool(truncated),'eos_emitted':eos,'dsl_parse_success':parse_success(text),'last_100_token_ids':tail,'last_100_tokens':tok.decode(tail,skip_special_tokens=False),'prediction':text,'target_dsl':row['target_dsl']};f.write(json.dumps(rec,ensure_ascii=False)+'\n');f.flush();report['completed']=i
    (out/'DECODE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    if i%10==0:print(f'[{a.arm}] decoded={i}/200 truncated={report["truncated"]}',flush=True)
  report['status']='PASS'
 finally:
  core.module._splice_geometry=original;(out/'DECODE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
