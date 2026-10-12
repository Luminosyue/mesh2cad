#!/usr/bin/env python3
"""Read-only teacher-forced EOS and LLM-entry embedding norm diagnostics."""
from __future__ import annotations
import argparse,json,pathlib,sys
import numpy as np
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');CODE=ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2';sys.path.insert(0,str(CODE))
import train_canonical_smoke as core
import decode_canonical_pilot as dec
DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data'
EOS=128009

def stats(xs):
 a=np.asarray(xs,float)
 return {'count':int(a.size),'mean':float(a.mean()),'median':float(np.median(a)),'p10':float(np.percentile(a,10)),'p90':float(np.percentile(a,90)),'min':float(a.min()),'max':float(a.max())} if a.size else {'count':0}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');a=ap.parse_args()
 run=pathlib.Path(a.run);best=json.loads((run/'BEST_CHECKPOINT.json').read_text());ckpt=pathlib.Path(best['path']);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device)
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=core.AutoTokenizer.from_pretrained(ckpt,local_files_only=True,use_fast=False);model=dec.load_model(a.arm,ckpt,device);state={};original=core.install_precomputed_second(model,a.arm,state);rows=json.loads((DATA/'pilot_1k_val.json').read_text())['records']
 report={'arm':a.arm,'split':'pilot_1k_val','official_test_read':False,'read_only':True,'best_epoch':best['epoch'],'completed':0,'status':'RUNNING'};(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n');all_rows=[]
 try:
  with torch.no_grad(),(out/'per_cad.jsonl').open('w') as f:
   for i,row in enumerate(rows,1):
    ids,labels,target_used,allowance=core.encode(tok,row,a.arm);full_target=tok.encode(pathlib.Path(row['target_dsl']).read_text()+'<|eot_id|>',add_special_tokens=False);fits=len(full_target)<=allowance and int(ids[0,-1])==EOS
    ids=ids.to(device);att=torch.ones_like(ids);surface_np,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface_np,device=device);second,mask=core.second_input(row,a.arm);state['mask']=mask;edge=None if second is None else second.to(device)
    surface_tokens,second_tokens=model.forward_geometry(surface,edge,device,next(model.parameters()).dtype)
    text_emb=model.get_input_embeddings()(ids);special=torch.zeros_like(ids,dtype=torch.bool)
    for token_id in (128000,128001,128008,128009,128011,128012,128013,128014,128015,128016):special|=ids.eq(token_id)
    text_norm=text_emb.norm(dim=-1)[~special].float().cpu().numpy().tolist();surf_norm=surface_tokens.reshape(-1,surface_tokens.shape[-1]).norm(dim=-1).float().cpu().numpy().tolist();second_norm=[]
    if second_tokens is not None:
     flat=second_tokens.reshape(-1,second_tokens.shape[-1]);second_norm=flat[:int(row['k_valid'])].norm(dim=-1).float().cpu().numpy().tolist()
    eos_prob=eos_rank=termination_prob=None
    if fits:
     surf_batch=surface.unsqueeze(0);edge_batch=None if edge is None else edge.unsqueeze(0)
     result=model(input_ids=ids,attention_mask=att,point_clouds=surf_batch,edge_clouds=edge_batch);logits=result.logits[0,-2].float();probs=torch.softmax(logits,dim=-1);eos_prob=float(probs[EOS]);termination_prob=float(probs[[128001,128008,128009]].sum());eos_rank=int((logits>logits[EOS]).sum())+1
    rec={'cad_id':row['cad_id'],'k_valid':row['k_valid'],'target_fits_context':fits,'full_target_token_length_with_eos':len(full_target),'eos_probability_at_gt_end':eos_prob,'termination_probability_at_gt_end':termination_prob,'eos_rank_at_gt_end':eos_rank,'text_embedding_norm':stats(text_norm),'surface_embedding_norm':stats(surf_norm),'second_stream_embedding_norm':stats(second_norm)};all_rows.append(rec);f.write(json.dumps(rec)+'\n');f.flush();report['completed']=i;(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    if i%10==0:print(f'[{a.arm}] {i}/200',flush=True)
  valid=[r for r in all_rows if r['target_fits_context']];summary={'arm':a.arm,'count':200,'eos_valid_count':len(valid),'eos_probability_at_gt_end':stats([r['eos_probability_at_gt_end'] for r in valid]),'termination_probability_at_gt_end':stats([r['termination_probability_at_gt_end'] for r in valid]),'eos_rank_at_gt_end':stats([r['eos_rank_at_gt_end'] for r in valid]),'text_embedding_norm_mean_per_cad':stats([r['text_embedding_norm']['mean'] for r in all_rows]),'surface_embedding_norm_mean_per_cad':stats([r['surface_embedding_norm']['mean'] for r in all_rows]),'second_stream_embedding_norm_mean_per_cad':stats([r['second_stream_embedding_norm']['mean'] for r in all_rows if r['second_stream_embedding_norm']['count']]),'status':'PASS','official_test_read':False};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');report.update(status='PASS',summary=summary)
 finally:
  core.module._splice_geometry=original;(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
