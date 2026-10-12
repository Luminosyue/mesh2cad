#!/usr/bin/env python3
"""Autoregressive smoke gate for the frozen 192/48 V3 smoke checkpoints."""
from __future__ import annotations
import argparse, ast, json, pathlib, sys
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
from geometry_prefix_adapter import GeometryPrefixAdapter

def parse_success(text):
 try: ast.parse(text); return True
 except (SyntaxError,ValueError): return False

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--checkpoint',required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--target-norm',type=float,required=True);ap.add_argument('--max-new-tokens',type=int,default=512);a=ap.parse_args()
 ckpt=pathlib.Path(a.checkpoint);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device)
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 tok=core.AutoTokenizer.from_pretrained(ckpt,local_files_only=True,use_fast=False)
 model=core.module.SpatialLMLlamaForCausalLM.from_pretrained(ckpt,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
 if a.arm=='b1':model.edge_proj=GeometryPrefixAdapter(model.config.hidden_size,model.config.hidden_size,target_norm=a.target_norm).to(device=device,dtype=torch.bfloat16);model.edge_proj.load_state_dict(torch.load(ckpt/'geometry_prefix_adapter.pt',map_location=device))
 elif a.arm=='m2':model.edge_proj=GeometryPrefixAdapter(256,model.config.hidden_size,target_norm=a.target_norm).to(device=device,dtype=torch.bfloat16);model.edge_proj.load_state_dict(torch.load(ckpt/'geometry_prefix_adapter.pt',map_location=device))
 else:model.edge_proj=None
 if a.arm!='b0':model.config.separate_edge_tokens=True;model.separate_edge_tokens=True
 model.eval();model.config.use_cache=True;state={};original=core.install_precomputed_second(model,a.arm,state)
 rows=core.load_records('val');preds=[]
 try:
  with torch.no_grad():
   for i,row in enumerate(rows,1):
    ids,labels,_,_=core.encode(tok,row,a.arm);n=int((labels[0]==-100).sum());ids=ids[:,:n].to(device);att=torch.ones_like(ids)
    surface,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0)
    second,mask=core.second_input(row,a.arm);state['raw_mask']=mask;edge=None if second is None else second.to(device).unsqueeze(0)
    gen=model.generate(input_ids=ids,attention_mask=att,point_clouds=surface,edge_clouds=edge,max_new_tokens=a.max_new_tokens,do_sample=False,use_cache=True,eos_token_id=[128001,128008,128009],pad_token_id=128001)
    new=gen[0,ids.shape[1]:].cpu();txt=tok.decode(new,skip_special_tokens=True);target=tok.encode(pathlib.Path(row['target_dsl']).read_text(),add_special_tokens=False)
    hit=new.numel()>=a.max_new_tokens;eos=bool(new.numel() and int(new[-1]) in [128001,128008,128009])
    preds.append({'cad_id':row['cad_id'],'raw_k_valid':row['k_valid'],'second_stream_active':0 if a.arm=='b0' else state['entry']['second_stream_active'],'target_token_length':len(target),'generated_token_length':int(new.numel()),'generated_target_ratio':float(new.numel()/max(1,len(target))),'hit_max_new_tokens':bool(hit),'unexpected_runaway':bool(hit and len(target)<=a.max_new_tokens),'eos_emitted':eos,'dsl_parse_success':parse_success(txt),'last_100_tokens':tok.decode(new[-100:],skip_special_tokens=False),'prediction':txt})
    if i%8==0:print(f'{a.arm} {i}/48 hit={sum(x["hit_max_new_tokens"] for x in preds)}',flush=True)
 finally: core.module._splice_geometry=original
 report={'arm':a.arm,'n':len(preds),'max_new_tokens':a.max_new_tokens,'eos_n':sum(x['eos_emitted'] for x in preds),'hit_max_n':sum(x['hit_max_new_tokens'] for x in preds),'unexpected_runaway_n':sum(x['unexpected_runaway'] for x in preds),'dsl_parse_n':sum(x['dsl_parse_success'] for x in preds),'second_stream_active_values':sorted(set(x['second_stream_active'] for x in preds)),'official_test_read':False,'training_started':False,'status':'PASS'}
 (out/'predictions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in preds));(out/'SMOKE_DECODE_GATE.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
