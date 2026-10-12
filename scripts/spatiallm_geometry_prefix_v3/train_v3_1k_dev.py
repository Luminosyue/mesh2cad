#!/usr/bin/env python3
"""Fresh V3-1k training with frozen decode-dev-only checkpoint selection."""
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, json, math, pathlib, random, sys, tempfile, time
from collections import Counter
import numpy as np
import torch
from transformers import get_cosine_schedule_with_warmup

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core

DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
EOS_IDS=(128001,128008,128009)
OPS=('Box','Cylinder','ExtrudePolygon','Extrude','Revolve','Union','Cut','Intersect','Circle','Rectangle','Polygon')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ops(s):
 import re
 return re.findall(r'\b('+ '|'.join(OPS) +r')\s*\(',s)
def f1(a,b):
 a,b=Counter(a),Counter(b);tp=sum((a&b).values())
 if not a and not b:return 1.0
 if not tp:return 0.0
 p,r=tp/max(sum(b.values()),1),tp/max(sum(a.values()),1);return 2*p*r/(p+r)
def parse_ok(s):
 try:ast.parse(s);return True
 except (SyntaxError,ValueError):return False
def llm_hash(model):
 h=hashlib.sha256()
 for k,t in sorted(model.state_dict().items()):
  if k.startswith(('point_backbone.','point_proj.','edge_proj.')):continue
  x=t.detach().cpu().contiguous();h.update(k.encode()+b'\0');h.update(str(tuple(x.shape)).encode()+b'\0');h.update(str(x.dtype).encode()+b'\0');h.update(x.view(torch.uint8).numpy().tobytes())
 return h.hexdigest()
def load(name):return json.loads((DATA/name).read_text())['records']
def exec_module():
 spec=importlib.util.spec_from_file_location('v3_cad_dsl',ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def step_metric(code,row,work_root):
 rec={'step_reload':False,'chamfer_norm':None}
 try:
  m=exec_module();clean=m.extract_dsl_code(code);m.parse_dsl(clean)
  with tempfile.TemporaryDirectory(dir=work_root) as d:
   d=pathlib.Path(d);step=d/'pred.step';stl=d/'pred.stl';m.execute_dsl(clean,step,stl)
   if not step.exists() or not stl.exists():return rec
   import cadquery as cq;cq.importers.importStep(str(step));rec['step_reload']=True
   import trimesh
   from scipy.spatial import cKDTree
   gt=trimesh.load(str(pathlib.Path(row['surface_input']).parent/'mesh.obj'),force='mesh');pr=trimesh.load(str(stl),force='mesh')
   if isinstance(gt,trimesh.Scene):gt=gt.dump(concatenate=True)
   if isinstance(pr,trimesh.Scene):pr=pr.dump(concatenate=True)
   diag=float(np.linalg.norm(gt.bounds[1]-gt.bounds[0]));
   if diag>1e-12:
    a,_=trimesh.sample.sample_surface(gt,3000,seed=42);b,_=trimesh.sample.sample_surface(pr,3000,seed=43)
    da=cKDTree(b).query(a,k=1)[0];db=cKDTree(a).query(b,k=1)[0];rec['chamfer_norm']=float((da.mean()+db.mean())/2/diag)
 except Exception as e:rec['error']=f'{type(e).__name__}: {e}'[-400:]
 return rec

def set_row(state,row,arm,device):
 x,m=core.second_input(row,arm);state['raw_mask']=m
 return None if x is None else x.to(device).unsqueeze(0)

def eval_dev(model,plugin,tok,rows,arm,device,state,max_new,epoch,out):
 model.eval();per=[];work=out/'tmp_exec';work.mkdir(exist_ok=True)
 with torch.no_grad():
  for i,row in enumerate(rows,1):
   ids,labels,_,_=core.encode(tok,row,arm);prompt=int((labels[0]==-100).sum());surface,_=plugin._load_cad_separate_edge(row['surface_input']);surface=torch.tensor(surface,device=device).unsqueeze(0);edge=set_row(state,row,arm,device)
   full=model(input_ids=ids.to(device),attention_mask=torch.ones_like(ids,device=device),labels=labels.to(device),point_clouds=surface,edge_clouds=edge);ce=float(full.loss)
   pids=ids[:,:prompt].to(device);edge=set_row(state,row,arm,device)
   gen=model.generate(input_ids=pids,attention_mask=torch.ones_like(pids),point_clouds=surface,edge_clouds=edge,max_new_tokens=max_new,do_sample=False,use_cache=True,eos_token_id=list(EOS_IDS),pad_token_id=128001)
   new=gen[0,pids.shape[1]:].cpu();text=tok.decode(new,skip_special_tokens=True);target=pathlib.Path(row['target_dsl']).read_text();gt_len=len(tok.encode(target,add_special_tokens=False));hit=bool(new.numel()>=max_new)
   metric=step_metric(text,row,work) if parse_ok(text) else {'step_reload':False,'chamfer_norm':None}
   per.append({'cad_id':row['cad_id'],'ce':ce,'target_token_length':gt_len,'generated_token_length':int(new.numel()),'generated_target_ratio':float(new.numel()/max(gt_len,1)),'hit_max_new_tokens':hit,'unexpected_runaway':bool(hit and gt_len<=max_new),'eos_emitted':bool(new.numel() and int(new[-1]) in EOS_IDS),'dsl_parse_success':parse_ok(text),'step_reload':metric['step_reload'],'op_f1':f1(ops(target),ops(text)),'exact_match':text.strip()==target.strip(),'chamfer_norm':metric.get('chamfer_norm'),'second_stream_active':0 if arm=='b0' else state['entry']['second_stream_active']})
   if i%10==0:print(f'[{arm}] epoch={epoch} dev={i}/50 runaway={sum(x["unexpected_runaway"] for x in per)}',flush=True)
 model.train();ch=[r['chamfer_norm'] for r in per if r['chamfer_norm'] is not None]
 summary={'epoch':epoch,'n':len(per),'dev_ce':float(np.mean([r['ce'] for r in per])),'eos_n':sum(r['eos_emitted'] for r in per),'hit_max_n':sum(r['hit_max_new_tokens'] for r in per),'unexpected_runaway_n':sum(r['unexpected_runaway'] for r in per),'dsl_parse_n':sum(r['dsl_parse_success'] for r in per),'step_reload_n':sum(r['step_reload'] for r in per),'mean_op_f1':float(np.mean([r['op_f1'] for r in per])),'exact_n':sum(r['exact_match'] for r in per),'mean_chamfer_norm':float(np.mean(ch)) if ch else None,'second_stream_active_values':sorted(set(r['second_stream_active'] for r in per))}
 (out/f'decode_dev_epoch_{epoch:02d}.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in per));(out/f'DECODE_DEV_EPOCH_{epoch:02d}.json').write_text(json.dumps(summary,indent=2)+'\n');return summary

def choose(curve):
 stable=[x for x in curve if x['unexpected_runaway_n']<=5]
 pool=stable or curve
 # Same lexicographic policy all arms; fallback picks lower runaway if no stable epoch.
 key=lambda x:(x['step_reload_n'],x['mean_op_f1'],-x['dev_ce']) if stable else (-x['unexpected_runaway_n'],x['step_reload_n'],x['mean_op_f1'],-x['dev_ce'])
 best=max(pool,key=key);return best, bool(stable)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['b0','b1','m2'],required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');ap.add_argument('--epochs',type=int,default=10);ap.add_argument('--target-norm',type=float,required=True);ap.add_argument('--max-new-tokens',type=int,default=4096);a=ap.parse_args()
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False);device=torch.device(a.device);torch.manual_seed(42);np.random.seed(42);random.seed(42);torch.backends.cuda.matmul.allow_tf32=True
 train,dev=load('v3_1k_train.json'),load('v3_decode_dev_50.json')
 if (len(train),len(dev))!=(800,50):raise RuntimeError('frozen split mismatch')
 core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=core.AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False);model=core.make_model(a.arm,device,a.target_norm)
 contract=json.loads((core.BASE_MODEL/'BASE_CONTRACT.json').read_text());initial=llm_hash(model)
 if initial!=contract['llm']['state_sha256']:raise RuntimeError('official parent LLM hash mismatch')
 state={};original=core.install_precomputed_second(model,a.arm,state);point,adapter,llm=core.groups(model,a.arm);params=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(params,lr=2e-5,weight_decay=0.0);updates=math.ceil(800/4)*a.epochs;sched=get_cosine_schedule_with_warmup(opt,int(updates*.03),updates)
 report={'current_gate':'V3_1K_TRAINING','arm':a.arm,'fresh_from_official_base':True,'smoke_checkpoint_used':False,'official_llm_hash':initial,'train_count':800,'decode_dev_count':50,'pilot_eval_read':False,'official_test_read':False,'epochs':a.epochs,'optimizer':'AdamW','scheduler':'cosine','selection_rule':['unexpected_runaway<=10%','max STEP reload','max Op F1','min decode-dev CE'],'curve':[],'status':'RUNNING'}
 try:
  for epoch in range(1,a.epochs+1):
   order=list(range(800));random.Random(42+epoch).shuffle(order);opt.zero_grad(set_to_none=True);losses=[]
   for pos,ix in enumerate(order,1):
    row=train[ix];loss,_,_=core.one_forward(model,plugin,tok,row,a.arm,device,state,train=True)
    if not torch.isfinite(loss):raise RuntimeError(f'nonfinite epoch={epoch}')
    (loss/4).backward();losses.append(float(loss.detach()))
    if epoch==1 and pos==1:
     audit={'SONATA_AND_SURFACE_PROJECTOR':core.audit_group(point),'GEOMETRY_PREFIX_ADAPTER':core.audit_group(adapter),'LLM':core.audit_group(llm),'C2_GRAD_NON_NONE':0,'B1_ENCODER_GRAD_NON_NONE':0}
     if audit['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count'] or audit['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count'] or audit['LLM']['grad_non_none_parameter_count']==0 or (a.arm!='b0' and audit['GEOMETRY_PREFIX_ADAPTER']['grad_non_none_parameter_count']==0):raise RuntimeError('gradient hard stop')
     report['first_backward_gradient_audit']=audit
    if a.arm!='b0' and (state['entry']['second_stream_active']!=8 or state['entry']['padding_attention']!=0 or not state['entry']['position_ids_contiguous']):raise RuntimeError('V3 interface hard stop')
    if pos%4==0 or pos==800:
     torch.nn.utils.clip_grad_norm_(params,1.0);opt.step();sched.step();opt.zero_grad(set_to_none=True)
   ckpt=out/f'checkpoint_epoch_{epoch:02d}';ckpt.mkdir();model.save_pretrained(ckpt,safe_serialization=True,max_shard_size='2GB');tok.save_pretrained(ckpt)
   if a.arm!='b0':torch.save(model.edge_proj.state_dict(),ckpt/'geometry_prefix_adapter.pt')
   devsum=eval_dev(model,plugin,tok,dev,a.arm,device,state,a.max_new_tokens,epoch,out);devsum.update({'train_ce':float(np.mean(losses)),'lr':sched.get_last_lr()[0],'checkpoint':str(ckpt)});report['curve'].append(devsum);(out/'TRAINING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
  best,stable=choose(report['curve']);report['best_checkpoint']=best;report['stability_gate_satisfied']=stable;report['status']='PASS';(out/'BEST_CHECKPOINT.json').write_text(json.dumps(best,indent=2)+'\n')
 finally:core.module._splice_geometry=original;(out/'TRAINING_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='curve'},indent=2))
if __name__=='__main__':main()
