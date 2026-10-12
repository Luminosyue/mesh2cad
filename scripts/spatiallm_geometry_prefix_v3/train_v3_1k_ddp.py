#!/usr/bin/env python3
"""Two-GPU DDP V3-1k, fresh from the official frozen parent per arm."""
from __future__ import annotations
import argparse, json, math, os, pathlib, random, sys
import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from transformers import get_cosine_schedule_with_warmup

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
import train_v3_1k_dev as dev

DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'

def load(name):return json.loads((DATA/name).read_text())['records']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--epochs',type=int,default=10);ap.add_argument('--target-norm',type=float,required=True);ap.add_argument('--max-new-tokens',type=int,default=4096);a=ap.parse_args()
 dist.init_process_group('nccl');rank=dist.get_rank();world=dist.get_world_size();local=int(os.environ['LOCAL_RANK']);torch.cuda.set_device(local);device=torch.device('cuda',local)
 if world!=2:raise RuntimeError('V3 DDP contract requires exactly two GPUs per arm')
 out=pathlib.Path(a.output)
 if rank==0:out.mkdir(parents=True,exist_ok=False)
 dist.barrier();torch.manual_seed(42);np.random.seed(42);random.seed(42);torch.backends.cuda.matmul.allow_tf32=True
 train,decode_dev=load('v3_1k_train.json'),load('v3_decode_dev_50.json')
 if (len(train),len(decode_dev))!=(800,50):raise RuntimeError('split mismatch')
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=core.AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False)
 base=core.make_model(a.arm,device,a.target_norm);contract=json.loads((core.BASE_MODEL/'BASE_CONTRACT.json').read_text());initial=dev.llm_hash(base)
 if initial!=contract['llm']['state_sha256']:raise RuntimeError('official parent hash mismatch')
 state={};original=core.install_precomputed_second(base,a.arm,state);point,adapter,llm=core.groups(base,a.arm);model=DDP(base,device_ids=[local],output_device=local,broadcast_buffers=False);params=[p for p in model.parameters() if p.requires_grad]
 opt=torch.optim.AdamW(params,lr=2e-5,weight_decay=0.0);updates=200*a.epochs;sched=get_cosine_schedule_with_warmup(opt,int(updates*.03),updates)
 report={'current_gate':'V3_1K_DDP_TRAINING','arm':a.arm,'world_size':world,'fresh_from_official_base':True,'smoke_checkpoint_used':False,'official_llm_hash':initial,'train_count':800,'decode_dev_count':50,'pilot_eval_read':False,'official_test_read':False,'epochs':a.epochs,'global_effective_batch':4,'gradient_accumulation_per_rank':2,'optimizer':'AdamW','scheduler':'cosine','selection_rule':['unexpected_runaway<=10%','max STEP reload','max Op F1','min decode-dev CE'],'curve':[],'status':'RUNNING'} if rank==0 else None
 try:
  for epoch in range(1,a.epochs+1):
   order=list(range(800));random.Random(42+epoch).shuffle(order);local_order=order[rank::world];opt.zero_grad(set_to_none=True);losses=[]
   for pos,ix in enumerate(local_order,1):
    row=train[ix];loss,_,_=core.one_forward(model,plugin,tok,row,a.arm,device,state,train=True)
    if not torch.isfinite(loss):raise RuntimeError(f'nonfinite loss e{epoch}')
    (loss/2).backward();losses.append(float(loss.detach()))
    if epoch==1 and pos==1:
     audit={'SONATA_AND_SURFACE_PROJECTOR':core.audit_group(point),'GEOMETRY_PREFIX_ADAPTER':core.audit_group(adapter),'LLM':core.audit_group(llm),'C2_GRAD_NON_NONE':0,'B1_ENCODER_GRAD_NON_NONE':0}
     if audit['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count'] or audit['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count'] or audit['LLM']['grad_non_none_parameter_count']==0 or (a.arm!='b0' and audit['GEOMETRY_PREFIX_ADAPTER']['grad_non_none_parameter_count']==0):raise RuntimeError('gradient hard stop')
     if rank==0:report['first_backward_gradient_audit']=audit
    if a.arm!='b0' and (state['entry']['second_stream_active']!=8 or state['entry']['padding_attention']!=0 or not state['entry']['position_ids_contiguous']):raise RuntimeError('V3 interface hard stop')
    if pos%2==0:
     torch.nn.utils.clip_grad_norm_(params,1.0);opt.step();sched.step();opt.zero_grad(set_to_none=True)
   dist.barrier()
   if rank==0:
    ckpt=out/f'checkpoint_epoch_{epoch:02d}';ckpt.mkdir();base.save_pretrained(ckpt,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(ckpt)
    if a.arm!='b0':torch.save(base.edge_proj.state_dict(),ckpt/'geometry_prefix_adapter.pt')
    ds=dev.eval_dev(base,plugin,tok,decode_dev,a.arm,device,state,a.max_new_tokens,epoch,out);ds.update({'train_ce_rank0':float(np.mean(losses)),'lr':sched.get_last_lr()[0],'checkpoint':str(ckpt)});report['curve'].append(ds);(out/'TRAINING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(f'[{a.arm}] DDP epoch={epoch} dev runaway={ds["unexpected_runaway_n"]}',flush=True)
   dist.barrier()
  if rank==0:
   best,stable=dev.choose(report['curve']);report['best_checkpoint']=best;report['stability_gate_satisfied']=stable;report['status']='PASS';(out/'BEST_CHECKPOINT.json').write_text(json.dumps(best,indent=2)+'\n')
 finally:
  if rank==0 and report is not None:(out/'TRAINING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
  core.module._splice_geometry=original;dist.barrier();dist.destroy_process_group()
if __name__=='__main__':main()
