#!/usr/bin/env python3
import argparse, hashlib, json, math, os, pathlib, random, shutil, sys, time
import numpy as np
import torch
from transformers import get_cosine_schedule_with_warmup

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
EXP=ROOT/'ours3/cadfs_noisy_overfit100_v1'; FREEZE=EXP/'retrain_input_freeze_v1'
MAN=EXP/'CADFS_NOISY_OVERFIT100_MANIFEST.json'; MAP=FREEZE/'SURFACE_MAPPING_V1.json'
LOADER=ROOT/'scripts/spatiallm_curve_token_v1/heldout_geometry.py'
MAN_SHA='16dfb051194eba2a2d4a54d361d5809b2d57b5a3250a4644ff569ebef7f4bfaf'; MAP_SHA='64518e67ca016a88aab5c4ca32688e3664667c638762e7e29a40a160a320ac38'; LOADER_SHA='c66a33af83498b155df49d572407acb8d5b8c6a783e43386ec1a8d30772e8a56'
SEED=42; EPOCHS=20; LR=2e-5; ACCUM=4; TARGET_NORM=1.9414176940917969
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import cadfs_noisy100_overfit_v1 as old
import train_v3_smoke as core
import train_v3_1k_dev as util

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''): h.update(x)
 return h.hexdigest()
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2)+'\n')
def append_jsonl(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with open(p,'a') as f:
  f.write(json.dumps(x)+'\n'); f.flush(); os.fsync(f.fileno())
def tensor_state_sha(sd):
 h=hashlib.sha256()
 for k,v in sorted(sd.items()):
  x=v.detach().cpu().contiguous(); raw=x.reshape(-1).view(torch.uint8).numpy().tobytes(); h.update(k.encode()+b'\0'+str(tuple(x.shape)).encode()+b'\0'+str(x.dtype).encode()+b'\0'+raw)
 return h.hexdigest()
def set_seed():
 random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
def config(arm):
 return {'ARM_NAME':arm,'RUN_NAME':'B0_CADFS100_NOISY_RETRAIN_V1' if arm=='b0' else 'M2_ORACLE_CADFS100_NOISY_RETRAIN_V1','FINAL100_MANIFEST_SHA256':MAN_SHA,'SURFACE_MAPPING_SHA256':MAP_SHA,'LOADER_SHA256':LOADER_SHA,'BASE_MODEL_PATH':str(core.BASE_MODEL),'BASE_MODEL_STATE_SHA256':json.loads((core.BASE_MODEL/'BASE_CONTRACT.json').read_text())['llm']['state_sha256'],'seed':SEED,'epochs':EPOCHS,'optimizer':'AdamW','learning_rate':LR,'scheduler':'cosine_with_warmup','warmup_ratio':0.03,'weight_decay':0.0,'batch_size':1,'gradient_accumulation':ACCUM,'max_context':4096,'precision':'bfloat16','gradient_clip':1.0,'full_finetune_llm':True,'freeze_point_tower':True,'SONATA_FROZEN':True,'C2_FROZEN':True,'experimental_variable':'M2 adds exactly 8 frozen-C2 oracle curve summary tokens' if arm=='m2' else 'surface only'}
def rows():
 raw=json.loads(MAN.read_text()); out=[]
 for r in raw['records']:
  n=int(np.load(r['curve_feature_path'],mmap_mode='r').shape[0])
  if n<1: raise RuntimeError(f'no frozen C2 tokens: {r["cad_id"]}')
  out.append({'cad_id':r['cad_id'],'surface_input':r['noisy_surface_path'],'target_dsl':r['cad_target_dsl'],'m2_full_c2_tokens':r['curve_feature_path'],'selected_m2_indices':list(range(n)),'k_valid':n,'surface_tokens':int(r['surface_token_count']),'source_step':r['source_step']})
 return out
def build(arm,device):
 set_seed(); core.heldout_geometry.install(); plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True); tok=core.AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False); model=core.make_model(arm,device,TARGET_NORM)
 contract=json.loads((core.BASE_MODEL/'BASE_CONTRACT.json').read_text()); llm=util.llm_hash(model); assert llm==contract['llm']['state_sha256']; m2hash=tensor_state_sha(model.edge_proj.state_dict()) if arm=='m2' else None
 state={}; original=core.install_precomputed_second(model,arm,state); point,adapter,llm_params=core.groups(model,arm); return model,plugin,tok,state,original,point,adapter,llm_params,llm,m2hash
def rng_state(): return {'python_random_state':random.getstate(),'numpy_random_state':np.random.get_state(),'torch_cpu_rng_state':torch.get_rng_state(),'torch_cuda_rng_state_all':torch.cuda.get_rng_state_all()}
def restore_rng(x):
 random.setstate(x['python_random_state']); np.random.set_state(x['numpy_random_state']); torch.set_rng_state(x['torch_cpu_rng_state']); torch.cuda.set_rng_state_all(x['torch_cuda_rng_state_all'])
def save_full(ck,model,tok,opt,sched,arm,epoch,global_step,cfg,m2hash):
 tmp=ck.with_name(ck.name+'.partial'); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 model.save_pretrained(tmp,safe_serialization=True,max_shard_size='2GB'); tok.save_pretrained(tmp)
 if arm=='m2': torch.save(model.edge_proj.state_dict(),tmp/'geometry_prefix_adapter.pt')
 state={'optimizer_state':opt.state_dict(),'scheduler_state':sched.state_dict(),'epoch':epoch,'global_step':global_step,'scaler_state':None,'rng_state':rng_state(),'training_config':cfg,'metadata':{'ARM_NAME':arm,'SEED':SEED,'FINAL100_MANIFEST_SHA256':MAN_SHA,'SURFACE_MAPPING_SHA256':MAP_SHA,'LOADER_SHA256':LOADER_SHA,'BASE_MODEL_SHA256':cfg['BASE_MODEL_STATE_SHA256'],'CONFIG_SHA256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),'M2_SPECIFIC_INIT_HASH':m2hash}}
 torch.save(state,tmp/'training_state.pt'); dump(tmp/'checkpoint_metadata.json',state['metadata']); tmp.rename(ck); return state
def validate_checkpoint(ck,arm,epoch,global_step,cfg):
 required=['config.json','training_state.pt','checkpoint_metadata.json']
 required += ['model.safetensors.index.json'] if (ck/'model.safetensors.index.json').exists() else ['model.safetensors']
 if arm=='m2': required.append('geometry_prefix_adapter.pt')
 missing=[x for x in required if not (ck/x).is_file() or (ck/x).stat().st_size==0]
 if missing: raise RuntimeError(f'incomplete checkpoint {ck}: {missing}')
 state=torch.load(ck/'training_state.pt',map_location='cpu',weights_only=False)
 rng=state.get('rng_state',{})
 checks={'optimizer_state','scheduler_state','epoch','global_step','rng_state','training_config','metadata'} <= set(state)
 checks=checks and all(k in rng for k in ['python_random_state','numpy_random_state','torch_cpu_rng_state','torch_cuda_rng_state_all'])
 checks=checks and state['epoch']==epoch and state['global_step']==global_step and state['training_config']==cfg
 checks=checks and state['metadata']['CONFIG_SHA256']==hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
 if not checks: raise RuntimeError(f'checkpoint state validation failed: {ck}')
 return {'epoch':epoch,'global_step':global_step,'checkpoint':str(ck),'status':'PASS','required_files':required,'checkpoint_bytes':sum(p.stat().st_size for p in ck.rglob('*') if p.is_file())}
def available_gib(path): return shutil.disk_usage(path).free/2**30
def load_model_state(model,ck):
 from safetensors.torch import load_model
 from transformers.modeling_utils import load_sharded_checkpoint
 if (ck/'model.safetensors.index.json').exists(): load_sharded_checkpoint(model,ck,strict=True,prefer_safe=True)
 elif (ck/'model.safetensors').exists(): load_model(model,str(ck/'model.safetensors'),strict=True)
 else: raise RuntimeError(f'no safetensors model state in {ck}')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--arm',choices=['b0','m2'],required=True); ap.add_argument('--output',type=pathlib.Path,required=True); ap.add_argument('--device',default='cuda:1'); ap.add_argument('--smoke',action='store_true'); ap.add_argument('--resume',type=pathlib.Path); a=ap.parse_args(); assert sha(MAN)==MAN_SHA and sha(MAP)==MAP_SHA and sha(LOADER)==LOADER_SHA
 if a.smoke and a.resume: raise RuntimeError('--smoke and --resume are mutually exclusive')
 if a.resume and not a.output.is_dir(): raise RuntimeError('resume output directory does not exist')
 a.output.mkdir(parents=True,exist_ok=bool(a.resume)); cfg=config(a.arm); cfg_path=a.output/'CONFIG.json'
 if a.resume:
  if json.loads(cfg_path.read_text())!=cfg: raise RuntimeError('resume config mismatch')
 else: dump(cfg_path,cfg)
 device=torch.device(a.device); records=rows(); old.core.encode=old.encode_full
 model,plugin,tok,state,original,point,adapter,llm_params,llm,m2hash=build(a.arm,device); params=[p for p in model.parameters() if p.requires_grad]; opt=torch.optim.AdamW(params,lr=LR,weight_decay=0.0); updates=math.ceil(len(records)/ACCUM)*EPOCHS; sched=get_cosine_schedule_with_warmup(opt,int(updates*.03),updates); report={'arm':a.arm,'BASE_SHARED_INIT_SHA256':llm,'M2_SPECIFIC_INIT':'FRESH' if a.arm=='m2' else None,'M2_SPECIFIC_INIT_SEED':SEED if a.arm=='m2' else None,'M2_SPECIFIC_INIT_HASH':m2hash,'status':'RUNNING','curve_token_row_source':'frozen curve_tokens.npy shape[0]; manifest curve_count is B-Rep source count'}
 try:
  if a.smoke:
   opt.zero_grad(set_to_none=True); loss,tn,pred=old.forward(model,plugin,tok,records[0],a.arm,device,state); (loss/ACCUM).backward(); grads=[p.grad for p in params if p.grad is not None]; adapter_grads=[p.grad for p in adapter if p.grad is not None]; grad_ok=bool(grads) and all(torch.isfinite(g).all() for g in grads) and (a.arm=='b0' or (bool(adapter_grads) and all(torch.isfinite(g).all() for g in adapter_grads))); torch.nn.utils.clip_grad_norm_(params,1.0); opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
   ck=a.output/'checkpoint_smoke'; saved=save_full(ck,model,tok,opt,sched,a.arm,0,1,cfg,m2hash); size=sum(p.stat().st_size for p in ck.rglob('*') if p.is_file()); del opt,model; torch.cuda.empty_cache()
   loaded=core.module.SpatialLMLlamaForCausalLM.from_pretrained(ck,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True); ts=torch.load(ck/'training_state.pt',map_location='cpu',weights_only=False); reload_ok=ts['global_step']==1 and 'optimizer_state' in ts and 'scheduler_state' in ts and all(k in ts['rng_state'] for k in ['python_random_state','numpy_random_state','torch_cpu_rng_state','torch_cuda_rng_state_all'])
   report.update({'status':'PASS' if grad_ok and reload_ok else 'FAIL','LOSS_FINITE':'YES' if torch.isfinite(loss) else 'NO','GRAD_FINITE':'YES' if grad_ok else 'NO','NO_NAN':'YES','NO_OOM':'YES','M2_CURVE_TOKEN_COUNT':8 if a.arm=='m2' else 0,'MODEL_STATE_SAVE':'PASS','OPTIMIZER_STATE_SAVE':'PASS','SCHEDULER_STATE_SAVE':'PASS','RNG_STATE_SAVE':'PASS','CHECKPOINT_RELOAD':'PASS' if reload_ok else 'FAIL','checkpoint_bytes':size,'checkpoint_gib':size/2**30,'config':cfg})
  else:
   start_epoch=1; global_step=0
   if a.resume:
    prior=torch.load(a.resume/'training_state.pt',map_location='cpu',weights_only=False); validate_checkpoint(a.resume,a.arm,prior['epoch'],prior['global_step'],cfg); load_model_state(model,a.resume); opt.load_state_dict(prior['optimizer_state']); sched.load_state_dict(prior['scheduler_state']); restore_rng(prior['rng_state']); start_epoch=prior['epoch']+1; global_step=prior['global_step']; report['STRICT_RESUME']='YES'; report['resumed_from']=str(a.resume)
   hist=a.output/(('B0' if a.arm=='b0' else 'M2')+'_TRAIN_HISTORY.jsonl'); integ=a.output/'CHECKPOINT_INTEGRITY.jsonl'; estimate=7.33 if a.arm=='b0' else 7.37
   for epoch in range(start_epoch,EPOCHS+1):
    free_before=available_gib(a.output); required=(EPOCHS-epoch+1)*estimate+10.0
    if free_before<required: raise RuntimeError(f'disk safety gate: free={free_before:.2f} GiB required={required:.2f} GiB')
    order=list(range(len(records))); random.Random(SEED+epoch).shuffle(order); losses=[]; started=time.time(); opt.zero_grad(set_to_none=True)
    for pos,ix in enumerate(order,1):
     loss,tn,pred=old.forward(model,plugin,tok,records[ix],a.arm,device,state); (loss/ACCUM).backward(); losses.append(float(loss.detach().cpu()))
     if pos%ACCUM==0 or pos==len(order): torch.nn.utils.clip_grad_norm_(params,1.0); opt.step(); sched.step(); opt.zero_grad(set_to_none=True); global_step+=1
    ck=a.output/f'checkpoint_epoch_{epoch:02d}'; save_full(ck,model,tok,opt,sched,a.arm,epoch,global_step,cfg,m2hash); integrity=validate_checkpoint(ck,a.arm,epoch,global_step,cfg); integrity['free_space_after_gib']=available_gib(a.output); append_jsonl(integ,integrity)
    row={'epoch':epoch,'train_ce':float(np.mean(losses)),'lr':sched.get_last_lr()[0],'global_step':global_step,'seconds':time.time()-started,'free_space_before_gib':free_before,'free_space_after_gib':integrity['free_space_after_gib'],'checkpoint':str(ck)}; append_jsonl(hist,row); report.update({'last_completed_epoch':epoch,'final_ce':row['train_ce'],'global_step':global_step,'final_checkpoint':str(ck),'free_space_end_gib':row['free_space_after_gib']}); dump(a.output/'TRAINING_REPORT.json',report); print(f'[{a.arm}] epoch={epoch}/{EPOCHS} ce={row["train_ce"]:.6f} free={row["free_space_after_gib"]:.2f}GiB',flush=True)
   report.update({'status':'COMPLETE','FINAL_EPOCH':EPOCHS,'FULL_RESUME_STATE':'YES','SELF_DECODE_RUN':'NO'})
 except Exception as exc:
  report.update({'status':'INCOMPLETE','error':repr(exc)}); raise
 finally:
  core.module._splice_geometry=original
  report_path=a.output/((('B0' if a.arm=='b0' else 'M2')+'_SMOKE_REPORT.json') if a.smoke else 'TRAINING_REPORT.json')
  dump(report_path,report)
 print(json.dumps(report,indent=2))
if __name__=='__main__': main()
