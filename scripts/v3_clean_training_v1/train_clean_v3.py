#!/usr/bin/env python3
"""Isolated B0/M2 clean V3 SFT: full target+EOS only, no allowance slicing."""
from __future__ import annotations
import argparse,json,math,pathlib,random,sys
import numpy as np
import torch
from transformers import get_cosine_schedule_with_warmup
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
import train_v3_1k_dev as util
DATA=ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
MAXCTX=4096

def encode_full(tok,row,arm):
    user=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
    prefix='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
    prompt=tok.encode(prefix,add_special_tokens=False)
    target=tok.encode(pathlib.Path(row['target_dsl']).read_text()+'<|eot_id|>',add_special_tokens=False)
    # The manifest is calculated from actual M2 splicing. B0 is shorter; both must retain EOS.
    s=int(row['clean_contract']['actual_surface_tokens']); exp=(s-1)+(0 if arm=='b0' else 7)
    predicted=len(prompt)+exp+len(target)
    if predicted>MAXCTX: raise RuntimeError(f'CONTEXT_OVERFLOW {row["cad_id"]} {predicted}>{MAXCTX}')
    if not target or target[-1]!=tok.convert_tokens_to_ids('<|eot_id|>'): raise RuntimeError('EOS missing')
    ids=torch.tensor([prompt+target],dtype=torch.long)
    labels=torch.tensor([[-100]*len(prompt)+target],dtype=torch.long)
    return ids,labels,len(target),predicted

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','m2'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--epochs',type=int,default=20);ap.add_argument('--target-norm',type=float,default=1.9414176940917969);ap.add_argument('--single-batch',action='store_true');a=ap.parse_args()
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device)
 torch.manual_seed(42);np.random.seed(42);random.seed(42);torch.backends.cuda.matmul.allow_tf32=True
 rows=json.loads(DATA.read_text())['records']; assert rows and all(r['clean_contract']['no_silent_truncation'] for r in rows)
 core.encode=encode_full # util.eval_dev and core.one_forward now share the hard no-trunc contract.
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 tok=core.AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False);model=core.make_model(a.arm,device,a.target_norm)
 contract=json.loads((core.BASE_MODEL/'BASE_CONTRACT.json').read_text());initial=util.llm_hash(model)
 if initial!=contract['llm']['state_sha256']:raise RuntimeError('official base hash mismatch')
 state={};original=core.install_precomputed_second(model,a.arm,state);point,adapter,llm=core.groups(model,a.arm);params=[p for p in model.parameters() if p.requires_grad]
 updates=math.ceil(len(rows)/4)*a.epochs;opt=torch.optim.AdamW(params,lr=2e-5,weight_decay=0.0);sched=get_cosine_schedule_with_warmup(opt,int(updates*.03),updates)
 report={'current_gate':'V3_CLEAN_SFT_RUNNING','arm':a.arm,'fresh_official_base':True,'old_v3_checkpoint_used':False,'train_count':len(rows),'epochs':a.epochs,'max_context':MAXCTX,'silent_target_truncate':False,'decode_dev50_read':False,'pilot150_read':False,'anchor_eval100_read':False,'official_test_read':False,'actual_sequence_length_assertion':'per batch: predicted full sequence <=4096; LLM hook equality at first batch each epoch','curve':[],'status':'RUNNING'}
 # Actual LLM-entry capture without altering the frozen V3 splicer.
 actual={}
 def hook(mod,args,kwargs): actual['len']=int(kwargs['inputs_embeds'].shape[1]);actual['att']=int(kwargs['attention_mask'].shape[1])
 handle=model.model.register_forward_pre_hook(hook,with_kwargs=True)
 try:
  for ep in range(1,a.epochs+1):
   order=list(range(len(rows)));random.Random(42+ep).shuffle(order);losses=[];opt.zero_grad(set_to_none=True)
   for pos,ix in enumerate(order,1):
    row=rows[ix];loss,_,pred=core.one_forward(model,plugin,tok,row,a.arm,device,state,train=True)
    # The CausalLM loss path splices labels with exactly the same regions as embeds;
    # audit the public labels contract from the original full target here as well.
    if actual.get('len')!=pred or actual.get('att')!=pred:raise RuntimeError(f'BUDGET_ACCOUNTING_FAIL {row["cad_id"]} predicted={pred} actual={actual}')
    if not torch.isfinite(loss):raise RuntimeError('nonfinite')
    (loss/4).backward();losses.append(float(loss.detach()))
    if ep==1 and pos==1:
     audit={'frozen_surface':core.audit_group(point),'adapter':core.audit_group(adapter),'llm':core.audit_group(llm),'predicted_vs_actual_sequence_length':dict(actual),'predicted':pred,'full_target_label_length':pred,'eos_supervised':True}
     if audit['frozen_surface']['trainable_parameter_count'] or audit['frozen_surface']['grad_non_none_parameter_count'] or audit['llm']['grad_non_none_parameter_count']==0 or (a.arm=='m2' and audit['adapter']['grad_non_none_parameter_count']==0):raise RuntimeError('gradient contract fail')
     report['first_backward_audit']=audit
    if a.arm=='m2' and (state['entry']['second_stream_active']!=8 or state['entry']['padding_attention']!=0):raise RuntimeError('m2 entry contract fail')
    if a.single_batch:
     report['status']='SINGLE_BATCH_PASS';report['current_gate']='V3_CLEAN_SINGLE_BATCH_PASS';break
    if pos%4==0 or pos==len(rows):torch.nn.utils.clip_grad_norm_(params,1.0);opt.step();sched.step();opt.zero_grad(set_to_none=True)
   if a.single_batch: break
   ckpt=out/f'checkpoint_epoch_{ep:02d}';ckpt.mkdir();model.save_pretrained(ckpt,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(ckpt)
   if a.arm=='m2':torch.save(model.edge_proj.state_dict(),ckpt/'geometry_prefix_adapter.pt')
   # This is train-self evaluation by protocol; no held-out record is loaded.
   ev=util.eval_dev(model,plugin,tok,rows,a.arm,device,state,4096,ep,out);ev.update({'train_ce':float(np.mean(losses)),'lr':sched.get_last_lr()[0],'checkpoint':str(ckpt)});report['curve'].append(ev)
   (out/'TRAINING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(f'[{a.arm}] epoch={ep}/{a.epochs} train_ce={ev["train_ce"]:.5f} exact={ev["exact_n"]}/{len(rows)} step={ev["step_reload_n"]}/{len(rows)}',flush=True)
  if not a.single_batch: report['status']='PASS';report['current_gate']='V3_CLEAN_SFT_COMPLETE'
 finally:
  handle.remove();core.module._splice_geometry=original;(out/'TRAINING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
