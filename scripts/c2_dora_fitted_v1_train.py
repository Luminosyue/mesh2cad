#!/usr/bin/env python3
"""Standalone C2_DORA_FITTED_V1; consumes only frozen Dora fitted train800 data."""
from __future__ import annotations
import argparse, hashlib, json, math, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path[:0]=[str(ROOT/'scripts')]
from curve_encoder_scale_curvature_v1.models import build_model
from curve_encoder_baseline_v1.losses import compute_losses, chamfer_l2
from dora_fitted_curve_dataset_v1 import sample_fit

DATA=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1'
OLD=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
OUT=ROOT/'ours3/c2_dora_fitted_v1'
TYPES=('LINE','CIRCLE','ELLIPSE','BSPLINE'); TID={x:i for i,x in enumerate(TYPES)}
SPEC={'frame':'curve_local','use_scale_branch':True,'use_curvature':False,'use_straightness_head':False,'desc':'C2 local + log-length'}

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def finite(x): return bool(np.isfinite(x).all())
def v(x): return np.asarray(x,dtype=np.float32)
def unit(x):
 x=v(x); return x/max(float(np.linalg.norm(x)),1e-12)
def fit_arrays(f):
 q=dict(f)
 for k in ('origin','direction','center','normal','x_axis','y_axis','major_axis','minor_axis'):
  if k in q:q[k]=v(q[k])
 if q.get('type')=='BSPLINE':q['tck']=[v(q['tck'][0]),v(q['tck'][1]),int(q['tck'][2])]
 return q

def prepare(out):
 out.mkdir(parents=True,exist_ok=True); cache=out/'prepared_cache.npz'; meta=out/'prepared_meta.json'
 if cache.exists() and meta.exists(): return np.load(cache,allow_pickle=False),json.loads(meta.read_text())
 entries=[json.loads(x) for x in (DATA/'C2_DORA_TRAINSET_V1.jsonl').read_text().splitlines() if x]
 groups=defaultdict(list)
 for e in entries:groups[e['cad_id']].append(e)
 X=[]; L=[]; Y=[]; M=[]; P=[]; CAD=[]; raw_family=[]
 for cad, es in groups.items():
  cdir=DATA/'cad'/cad; inp=np.load(cdir/'curve_c2/curve_inputs.npy'); length=np.load(cdir/'curve_c2/curve_lengths.npy')
  fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves']
  for e in es:
   i=int(e['dora_curve_index']); typ=e['gt_curve_type']; par=e['gt_world_parameters']; f=fit_arrays(fits[i]); xyz,_,_,_=sample_fit(f); center=xyz.mean(0); scale=max(float(np.ptp(xyz,axis=0).max()),1e-12)
   p=np.zeros(11,np.float32); m=np.zeros(11,np.float32)
   if typ=='LINE':p[:3]=unit(par['direction']);m[:3]=1
   elif typ=='CIRCLE':
    p[:3]=(v(par['center'])-center)/scale;p[3:6]=unit(par['normal']);p[6]=float(par['radius'])/scale;m[:7]=1
   elif typ=='ELLIPSE':
    p[:3]=(v(par['center'])-center)/scale;p[3:6]=unit(par['major_axis']);p[6:9]=unit(par['minor_axis']);p[9]=float(par['major_radius'])/scale;p[10]=float(par['minor_radius'])/scale;m[:11]=1
   X.append(inp[i]);L.append(length[i]);Y.append(TID[typ]);P.append(p);M.append(m);CAD.append(cad);raw_family.append(e['fit_type'])
 a={'x':np.asarray(X,'f4'),'loglen':np.asarray(L,'f4').reshape(-1,1),'y':np.asarray(Y,'i8'),'param':np.asarray(P,'f4'),'mask':np.asarray(M,'f4'),'cad':np.asarray(CAD),'raw_family':np.asarray(raw_family)}
 if not all(finite(a[k]) for k in ('x','loglen','param','mask')):raise RuntimeError('NaN/Inf in prepared cache')
 np.savez_compressed(cache,**a)
 m={'source_npz_sha256':sha(DATA/'C2_DORA_TRAINSET_V1.npz'),'source_jsonl_sha256':sha(DATA/'C2_DORA_TRAINSET_V1.jsonl'),'n':len(X),'type_counts':dict(Counter(TYPES[int(z)] for z in a['y'])),'raw_fitted_family_counts':dict(Counter(raw_family)),'arc_mapped_to_circle_geometry_family':True,'cache_sha256':sha(cache)};dump(meta,m);return np.load(cache,allow_pickle=False),m

class DS(Dataset):
 def __init__(self,a,idx):self.a=a;self.idx=np.asarray(idx); self.type_id=a['y'][self.idx]
 def __len__(self):return len(self.idx)
 def __getitem__(self,n):
  i=self.idx[n]; x=self.a['x'][i]
  return {'feats_local':torch.from_numpy(x),'xyz_local':torch.from_numpy(x[:,:3]),'scale_feat':torch.from_numpy(self.a['loglen'][i]),'type_id':torch.tensor(int(self.a['y'][i])),'param':torch.from_numpy(self.a['param'][i]),'param_mask':torch.from_numpy(self.a['mask'][i]),'has_param':torch.tensor(float(self.a['y'][i]!=TID['BSPLINE'])),'cad':self.a['cad'][i]}
def collate(b):return {k:(torch.stack([z[k] for z in b]) if k!='cad' else [z[k] for z in b]) for k in b[0]}
def loader(ds,train=False,batch=256,seed=0):
 # The frozen source is an NPZ archive; keep worker count at zero so a shared
 # ZipFile handle cannot be inherited by workers and corrupt a read.
 if train:
  c=Counter(ds.type_id.tolist()); w=np.asarray([1/c[int(x)] for x in ds.type_id],dtype='f8');sam=WeightedRandomSampler(torch.as_tensor(w),num_samples=65536,replacement=True,generator=torch.Generator().manual_seed(seed));return DataLoader(ds,batch_size=batch,sampler=sam,num_workers=0,pin_memory=True,drop_last=True,collate_fn=collate)
 return DataLoader(ds,batch_size=batch,shuffle=False,num_workers=0,pin_memory=True,collate_fn=collate)
def model_load(device):
 model=build_model(SPEC).to(device); ck=torch.load(OLD,map_location='cpu',weights_only=True); state=ck['model']; missing,unexpected=model.load_state_dict(state,strict=False); audit={'checkpoint':str(OLD),'checkpoint_sha256':sha(OLD),'loaded_keys':len(state)-len(unexpected),'checkpoint_keys':len(state),'model_keys':len(model.state_dict()),'missing_keys':list(missing),'unexpected_keys':list(unexpected),'strict_compatible':not missing and not unexpected}
 if not audit['strict_compatible']:raise RuntimeError(json.dumps(audit))
 return model,audit
def direction_deg(a,b):
 a=torch.nn.functional.normalize(a,dim=-1);b=torch.nn.functional.normalize(b,dim=-1);return torch.rad2deg(torch.acos((a.mul(b).sum(-1).abs()).clamp(-1,1)))
@torch.no_grad()
def evaluate(model,ld,device):
 model.eval(); ys=[];ps=[];ch=[];dirs=[];rad=[];cen=[];norm=[];lnerr=[]
 for b in ld:
  d={k:(z.to(device) if torch.is_tensor(z) else z) for k,z in b.items()};o=model(d['feats_local'],scale_feat=d['scale_feat']); pred=o['type_logits'].argmax(-1);ys.extend(d['type_id'].cpu().tolist());ps.extend(pred.cpu().tolist());ch.extend(chamfer_l2(o['recon_xyz'],d['xyz_local']).cpu().tolist())
  line=d['type_id']==0; circ=d['type_id']==1
  if line.any():dirs.extend(direction_deg(o['param'][line,:3],d['param'][line,:3]).cpu().tolist())
  if circ.any():
   rad.extend(((o['param'][circ,6]-d['param'][circ,6]).abs()/d['param'][circ,6].abs().clamp_min(1e-3)).cpu().tolist());cen.extend(torch.linalg.vector_norm(o['param'][circ,:3]-d['param'][circ,:3],dim=-1).cpu().tolist());norm.extend(direction_deg(o['param'][circ,3:6],d['param'][circ,3:6]).cpu().tolist())
  pl=torch.linalg.vector_norm(torch.diff(o['recon_xyz'],dim=1),dim=-1).sum(1); gl=torch.linalg.vector_norm(torch.diff(d['xyz_local'],dim=1),dim=-1).sum(1);lnerr.extend(((pl-gl).abs()/gl.clamp_min(1e-6)).cpu().tolist())
 def avg(a):return float(np.mean(a)) if a else None
 f1={}
 for t in range(4):
  tp=sum(a==t and b==t for a,b in zip(ys,ps));fp=sum(a!=t and b==t for a,b in zip(ys,ps));fn=sum(a==t and b!=t for a,b in zip(ys,ps));f1[TYPES[t]]=float(2*tp/max(2*tp+fp+fn,1))
 return {'n':len(ys),'type_macro_f1':float(np.mean(list(f1.values()))),'type_f1':f1,'line_direction_error_deg':avg(dirs),'circle_radius_relative_error':avg(rad),'circle_center_error_local':avg(cen),'circle_normal_angle_deg':avg(norm),'length_relative_error':avg(lnerr),'reconstruction_chamfer':avg(ch)}
def run_epoch(model,ld,opt,dev):
 model.train();tot=Counter();n=0
 for b in ld:
  d={k:(z.to(dev) if torch.is_tensor(z) else z) for k,z in b.items()};o=model(d['feats_local'],scale_feat=d['scale_feat']); loss=compute_losses(o,{**d,'xyz':d['xyz_local']},lambda_type=1,lambda_recon=1,lambda_param=1)
  if not torch.isfinite(loss['loss']):raise RuntimeError('non-finite loss')
  opt.zero_grad(set_to_none=True);loss['loss'].backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step();bs=len(d['type_id']);n+=bs
  for k in ('loss','loss_type','loss_recon','loss_param'):tot[k]+=float(loss[k])*bs
 return {k:tot[k]/n for k in tot}
def cosine(opt,e,E,lr):
 warm=2; z=lr*(e+1)/warm if e<warm else lr*.5*(1+math.cos(math.pi*(e-warm)/max(E-warm,1)))
 for g in opt.param_groups:g['lr']=z
 return z
def split_indices(a):
 spl=json.loads((DATA/'C2_DORA_CAD_SPLIT_V1.json').read_text());tr=set(spl['train_cad_ids']);return np.asarray([i for i,c in enumerate(a['cad']) if c in tr]),np.asarray([i for i,c in enumerate(a['cad']) if c not in tr])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=('audit','baseline','overfit','train'),required=True);ap.add_argument('--out',type=Path,default=OUT);ap.add_argument('--device',default='cuda');ap.add_argument('--epochs',type=int,default=30);args=ap.parse_args(); random.seed(0);np.random.seed(0);torch.manual_seed(0);torch.cuda.manual_seed_all(0);args.out.mkdir(parents=True,exist_ok=True)
 a,m=prepare(args.out);tr,va=split_indices(a);train,val=DS(a,tr),DS(a,va);audit={'train':{'cad':720,'curve':len(train),'type_counts':dict(Counter(TYPES[int(x)] for x in train.type_id))},'val':{'cad':80,'curve':len(val),'type_counts':dict(Counter(TYPES[int(x)] for x in val.type_id))},'input_shape':list(a['x'].shape[1:]),'nan':False,'inf':False,'log_length_train':{'min':float(a['loglen'][tr].min()),'median':float(np.median(a['loglen'][tr])),'max':float(a['loglen'][tr].max())},'log_length_val':{'min':float(a['loglen'][va].min()),'median':float(np.median(a['loglen'][va])),'max':float(a['loglen'][va].max())},'arc_raw_count_train':int((a['raw_family'][tr]=='ARC').sum()),'arc_raw_count_val':int((a['raw_family'][va]=='ARC').sum()),'arc_geometry_family':'CIRCLE'};dump(args.out/'INPUT_AUDIT.json',audit)
 dev=torch.device(args.device);model,load_audit=model_load(dev);dump(args.out/'INITIALIZATION_AUDIT.json',{**load_audit,'all_parameters_trainable':all(p.requires_grad for p in model.parameters()),'trainable_params':sum(p.numel() for p in model.parameters())})
 vl=loader(val)
 if args.stage=='audit':return
 if args.stage=='baseline':dump(args.out/'OLD_C2_ON_DORA_VAL866.json',evaluate(model,vl,dev));return
 if args.stage=='overfit':
  by=defaultdict(list)
  for i in tr:by[a['cad'][i]].append(i)
  # coverage-first then hash fill, deterministic and CAD-level
  selected=[];seen=set()
  for fam in TYPES:
   candidates=sorted((c for c,ii in by.items() if any(a['y'][j]==TID[fam] for j in ii)),key=lambda c:hashlib.sha256(c.encode()).hexdigest())
   if candidates and candidates[0] not in seen:selected.append(candidates[0]);seen.add(candidates[0])
  for c in sorted(by,key=lambda c:hashlib.sha256(c.encode()).hexdigest()):
   if len(selected)>=20:break
   if c not in seen:selected.append(c);seen.add(c)
  oi=np.asarray([j for c in selected for j in by[c]]);ds=DS(a,oi);ld=loader(ds,True,128,0);opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4);hist=[]
  for e in range(25):cosine(opt,e,25,1e-3);hist.append(run_epoch(model,ld,opt,dev))
  ok=all(hist[-1][k]<.9*hist[0][k] for k in ('loss_type','loss_recon','loss_param'));dump(args.out/'OVERFIT_20CAD.json',{'cad_ids':selected,'curve_count':len(ds),'history':hist,'pass':ok,'nan':False,'inf':False,'CURRENT_GATE':'C2_DORA_FITTED_V1_OVERFIT_PASS' if ok else 'C2_DORA_FITTED_V1_OVERFIT_FAIL'});return
 opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4);tl=loader(train,True,256,0);history=[];best={'f1':-1,'epoch':None}
 for e in range(args.epochs):
  lr=cosine(opt,e,args.epochs,1e-3);loss=run_epoch(model,tl,opt,dev);met=evaluate(model,vl,dev);row={'epoch':e+1,'lr':lr,'train':loss,'val':met};history.append(row);torch.save({'model':model.state_dict(),'epoch':e+1,'val':met,'spec':SPEC},args.out/f'epoch_{e+1:02d}.pt')
  if met['type_macro_f1']>best['f1']:best={'f1':met['type_macro_f1'],'epoch':e+1};torch.save(torch.load(args.out/f'epoch_{e+1:02d}.pt',map_location='cpu',weights_only=True),args.out/'best.pt')
  print(json.dumps({'epoch':e+1,'macro_f1':met['type_macro_f1'],'loss':loss['loss']}),flush=True)
 bestp=args.out/'best.pt';b=torch.load(bestp,map_location='cpu',weights_only=True);final={'CURRENT_GATE':'C2_DORA_FITTED_V1_COMPLETE_PENDING_COMPARISON','best_epoch':best['epoch'],'best_checkpoint':str(bestp),'best_checkpoint_sha256':sha(bestp),'best_val':b['val'],'history':history,'training_started':True,'forbidden_reads':{'decode_dev50_predictions':False,'pilot150':False,'anchor_eval100':False,'official_test':False}};dump(args.out/'TRAINING_RESULT.json',final)
if __name__=='__main__':main()
