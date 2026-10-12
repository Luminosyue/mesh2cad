#!/usr/bin/env python3
"""Read-only Phase-D inference variant decode on the frozen 50-CAD cohort."""
from __future__ import annotations
import argparse,ast,json,pathlib,sys,types
import numpy as np
import torch
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');CODE=ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2';sys.path.insert(0,str(CODE))
import train_canonical_smoke as core
import decode_canonical_pilot as dec
DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/phase_d_inference_diagnostic_v1/data/phase_d_50.json';KPAD=128
def parse_ok(s):
 try:ast.parse(s);return True
 except Exception:return False
def second(row,arm,kcap):
 idx=row['selected_b1_indices'] if arm=='b1' else row['selected_m2_indices'];k=min(row['k_valid'],kcap if kcap else row['k_valid']);raw=np.load(core.CANON/row['b1_full_tokens']) if arm=='b1' else np.load(row['m2_full_c2_tokens']);sel=raw[np.asarray(idx[:k],np.int64)];out=np.zeros((KPAD,raw.shape[1]),np.float32);out[:k]=sel;mask=torch.zeros(KPAD,dtype=torch.bool);mask[:k]=True;return torch.from_numpy(out),mask,k
def install(model,arm,state,mode,scale):
 original=core.module._splice_geometry
 def fg(self,surface_points,edge_points=None,device=None,dtype=None):
  with torch.no_grad():surface=self.forward_point_cloud(surface_points,device,dtype,projector=self.point_proj)
  if mode=='drop':return surface,None
  pd=next(self.edge_proj.parameters()).dtype;out=self.edge_proj(edge_points.to(device=device,dtype=pd)).unsqueeze(0).to(dtype)
  if mode=='zero_active':out=torch.zeros_like(out)
  else:out=out*scale
  return surface,out
 def splice(emb,mask,regions):
  masks=[torch.ones(regions[0][1].shape[0],dtype=torch.bool,device=mask.device)]
  if len(regions)==2:masks.append(state['mask'].to(mask.device))
  return core.splice_geometry_masked(emb,mask,regions,masks)
 model.forward_geometry=types.MethodType(fg,model);core.module._splice_geometry=splice;return original
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b1','m2'],required=True);ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--scale',type=float,default=1.0);ap.add_argument('--k-cap',type=int);ap.add_argument('--mode',choices=['correct','zero_active','drop'],default='correct');a=ap.parse_args();run=pathlib.Path(a.run);best=json.loads((run/'BEST_CHECKPOINT.json').read_text());ckpt=pathlib.Path(best['path']);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device)
 rows=json.loads(DATA.read_text())['records'];core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=core.AutoTokenizer.from_pretrained(ckpt,local_files_only=True,use_fast=False);model=dec.load_model(a.arm,ckpt,device);state={};original=install(model,a.arm,state,a.mode,a.scale);report={'arm':a.arm,'mode':a.mode,'scale':a.scale,'k_cap':a.k_cap,'count':50,'completed':0,'truncated':0,'max_new_tokens':4096,'greedy':True,'official_test_read':False,'training_started':False,'status':'RUNNING'};(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 try:
  with (out/'predictions.jsonl').open('w') as f,torch.no_grad():
   for i,row in enumerate(rows,1):
    prompt_arm='b0' if a.mode=='drop' else a.arm;ids=dec.prompt_ids(tok,row,prompt_arm).to(device);att=torch.ones_like(ids);surface_np,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface_np,device=device).unsqueeze(0);edge=None;k=0
    if a.mode!='drop':raw,mask,k=second(row,a.arm,a.k_cap);state['mask']=mask;edge=raw.to(device).unsqueeze(0)
    gen=model.generate(input_ids=ids,attention_mask=att,point_clouds=surface,edge_clouds=edge,max_new_tokens=4096,do_sample=False,use_cache=True,eos_token_id=[128001,128008,128009],pad_token_id=128001);new=gen[0,ids.shape[1]:].cpu();text=tok.decode(new,skip_special_tokens=True);hit=new.numel()>=4096;target=pathlib.Path(row['target_dsl']).read_text();target_len=len(tok.encode(target,add_special_tokens=False));tail=new[-100:].tolist();rec={'cad_id':row['cad_id'],'source_dataset':row['source_dataset'],'difficulty_bin':row['difficulty_bin'],'original_k_valid':row['k_valid'],'effective_k':k,'target_token_length':target_len,'generated_token_length':int(new.numel()),'generated_to_target_ratio':int(new.numel())/max(target_len,1),'hit_max_new_tokens':bool(hit),'eos_emitted':bool(new.numel() and int(new[-1]) in (128001,128008,128009)),'dsl_parse_success':parse_ok(text),'exact_match':text.strip()==target.strip(),'last_100_token_ids':tail,'last_100_tokens':tok.decode(tail,skip_special_tokens=False),'prediction':text,'target_dsl':row['target_dsl']};f.write(json.dumps(rec,ensure_ascii=False)+'\n');f.flush();report['completed']=i;report['truncated']+=int(hit);(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    if i%5==0:print(f'{a.arm} {a.mode} scale={a.scale} kcap={a.k_cap} {i}/50 trunc={report["truncated"]}',flush=True)
  report['status']='PASS'
 finally:core.module._splice_geometry=original;(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
