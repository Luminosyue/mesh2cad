#!/usr/bin/env python3
"""Fresh 500-step V3 convergence smoke with decode/EOS curves every 100 steps."""
from __future__ import annotations
import argparse, ast, json, math, pathlib, random, sys, time
import numpy as np
import torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core

EOS_IDS=(128001,128008,128009)

def parse_ok(text):
 try: ast.parse(text); return True
 except (SyntaxError,ValueError): return False

def save_checkpoint(model,tok,arm,path):
 path.mkdir(parents=True,exist_ok=False)
 model.save_pretrained(path,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(path)
 if arm!='b0':torch.save(model.edge_proj.state_dict(),path/'geometry_prefix_adapter.pt')

def set_row(state,row,arm,device):
 second,mask=core.second_input(row,arm);state['raw_mask']=mask
 return None if second is None else second.to(device).unsqueeze(0)

def decode_and_eos(model,plugin,tok,rows,arm,device,state,max_new,step,out):
 model.eval();pred=[];teacher=[]
 with torch.no_grad():
  for i,row in enumerate(rows,1):
   ids,labels,_,_=core.encode(tok,row,arm);prompt_n=int((labels[0]==-100).sum())
   surface,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0)
   edge=set_row(state,row,arm,device)
   full=model(input_ids=ids.to(device),attention_mask=torch.ones_like(ids,device=device),point_clouds=surface,edge_clouds=edge)
   target=labels[0][labels[0]!=-100]; eos_target=int(target[-1]) if target.numel() else -1
   if eos_target in EOS_IDS and full.logits.shape[1]>=2:
    logits=full.logits[0,-2].float();prob=float(torch.softmax(logits,dim=-1)[eos_target]);rank=int((logits>logits[eos_target]).sum().item()+1)
    teacher.append({'cad_id':row['cad_id'],'eos_probability':prob,'eos_rank':rank})
   pids=ids[:,:prompt_n].to(device);edge=set_row(state,row,arm,device)
   gen=model.generate(input_ids=pids,attention_mask=torch.ones_like(pids),point_clouds=surface,edge_clouds=edge,max_new_tokens=max_new,do_sample=False,use_cache=True,eos_token_id=list(EOS_IDS),pad_token_id=128001)
   new=gen[0,pids.shape[1]:].cpu();text=tok.decode(new,skip_special_tokens=True)
   gt_len=len(tok.encode(pathlib.Path(row['target_dsl']).read_text(),add_special_tokens=False));hit=bool(new.numel()>=max_new)
   pred.append({'cad_id':row['cad_id'],'raw_k_valid':row['k_valid'],'second_stream_active':0 if arm=='b0' else state['entry']['second_stream_active'],'generated_token_length':int(new.numel()),'target_token_length':gt_len,'generated_target_ratio':float(new.numel()/max(gt_len,1)),'hit_max_new_tokens':hit,'unexpected_runaway':bool(hit and gt_len<=max_new),'eos_emitted':bool(new.numel() and int(new[-1]) in EOS_IDS),'dsl_parse_success':parse_ok(text),'last_100_tokens':tok.decode(new[-100:],skip_special_tokens=False)})
   if i%8==0:print(f'[{arm}] step={step} decode={i}/{len(rows)} hit={sum(x["hit_max_new_tokens"] for x in pred)}',flush=True)
 model.train()
 summary={'step':step,'n':len(pred),'max_new_tokens':max_new,'eos_n':sum(x['eos_emitted'] for x in pred),'hit_max_n':sum(x['hit_max_new_tokens'] for x in pred),'unexpected_runaway_n':sum(x['unexpected_runaway'] for x in pred),'dsl_parse_n':sum(x['dsl_parse_success'] for x in pred),'second_stream_active_values':sorted(set(x['second_stream_active'] for x in pred)),'teacher_eos_n':len(teacher),'teacher_eos_probability_mean':float(np.mean([x['eos_probability'] for x in teacher])) if teacher else None,'teacher_eos_rank_mean':float(np.mean([x['eos_rank'] for x in teacher])) if teacher else None,'teacher_eos_rank1_n':sum(x['eos_rank']==1 for x in teacher)}
 (out/f'decode_step_{step}.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in pred));(out/f'teacher_eos_step_{step}.json').write_text(json.dumps(teacher,indent=2)+'\n');(out/f'DECODE_STEP_{step}.json').write_text(json.dumps(summary,indent=2)+'\n')
 return summary

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--steps',type=int,default=500);ap.add_argument('--target-norm',type=float,required=True);ap.add_argument('--max-new-tokens',type=int,default=512);a=ap.parse_args()
 if a.steps!=500:raise ValueError('protocol requires a fresh 500-step run')
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device);torch.manual_seed(42);np.random.seed(42);random.seed(42);torch.backends.cuda.matmul.allow_tf32=True
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=core.AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False)
 train,val=core.load_records('train'),core.load_records('val');model=core.make_model(a.arm,device,a.target_norm);state={};original=core.install_precomputed_second(model,a.arm,state);point,adapter,llm=core.groups(model,a.arm)
 optim=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=2e-5,weight_decay=0.0)
 report={'current_gate':'V3_CONVERGENCE_SMOKE_500','arm':a.arm,'fresh_from_official_base':True,'smoke_checkpoint_used':False,'steps':a.steps,'seed':42,'optimizer':'AdamW','lr':2e-5,'scheduler':'none','target_norm':a.target_norm,'summary_tokens':8,'official_test_read':False,'training_started':True,'decode_curve':[],'status':'RUNNING'}
 try:
  for step in range(1,a.steps+1):
   row=train[((step-1)*73)%len(train)];optim.zero_grad(set_to_none=True);loss,_,_=core.one_forward(model,plugin,tok,row,a.arm,device,state,train=True)
   if not torch.isfinite(loss):raise RuntimeError(f'non-finite loss at {step}')
   loss.backward()
   if step==1:
    audit={'SONATA_AND_SURFACE_PROJECTOR':core.audit_group(point),'GEOMETRY_PREFIX_ADAPTER':core.audit_group(adapter),'LLM':core.audit_group(llm),'C2_GRAD_NON_NONE':0,'B1_ENCODER_GRAD_NON_NONE':0}
    if audit['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count'] or audit['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count'] or audit['LLM']['grad_non_none_parameter_count']==0 or (a.arm!='b0' and audit['GEOMETRY_PREFIX_ADAPTER']['grad_non_none_parameter_count']==0):raise RuntimeError('first-backward frozen/gradient hard stop')
    report['first_backward_gradient_audit']=audit
   torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.0);optim.step();report.setdefault('losses',[]).append(float(loss.detach()))
   if a.arm!='b0' and (state['entry']['second_stream_active']!=8 or state['entry']['padding_attention']!=0 or not state['entry']['position_ids_contiguous']):raise RuntimeError('V3 interface hard stop')
   if step%100==0:
    ckpt=out/f'checkpoint_step_{step:03d}';save_checkpoint(model,tok,a.arm,ckpt)
    report['decode_curve'].append(decode_and_eos(model,plugin,tok,val,a.arm,device,state,a.max_new_tokens,step,out))
    report['loss_at_step_'+str(step)]=report['losses'][-1];(out/'CONVERGENCE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(f'[{a.arm}] checkpoint/decode step={step}',flush=True)
  report['loss_first20_mean']=float(np.mean(report['losses'][:20]));report['loss_last20_mean']=float(np.mean(report['losses'][-20:]));report['loss_trend_down']=report['loss_last20_mean']<report['loss_first20_mean'];report['status']='PASS'
 finally:
  core.module._splice_geometry=original;(out/'CONVERGENCE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='losses'},indent=2))
if __name__=='__main__':main()
