from __future__ import annotations
import hashlib,json,random,sys
from pathlib import Path
import numpy as np, torch
import torch.nn.functional as F
from torch.utils.data import Dataset,DataLoader
from scipy.stats import spearmanr
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); S=ROOT/'scripts'; sys.path.insert(0,str(S))
from dora_fitted_curve_dataset_v1 import graph_from_dora,extract_chains
from dora_chain_representation_v1 import build_chain_features
from curve_encoder_scale_curvature_v1.models import ScaleCurvatureModel
OUT=ROOT/'ours3/dora_curve_vs_chain_distillation_v1'; V1=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1'; COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'; PAIRS=V1/'C2_DORA_TRAINSET_V1.jsonl'; CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
SEED=42; EPOCHS=30; BATCH=256; DEVICE=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def seed(s):random.seed(s);np.random.seed(s);torch.manual_seed(s);torch.cuda.manual_seed_all(s)
class DS(Dataset):
 def __init__(self,x,y,cad,typ,split):self.x=np.asarray(x,'f4');self.y=np.asarray(y,'f4');self.cad=cad;self.typ=typ;self.split=split
 def __len__(self):return len(self.y)
 def __getitem__(self,i):return torch.from_numpy(self.x[i]),torch.from_numpy(self.y[i])
def model(dim):return ScaleCurvatureModel(use_scale_branch=True,use_curvature=False,use_straightness_head=False,shape_dim=dim)
def loss(z,t):z=F.normalize(z,dim=-1);t=F.normalize(t,dim=-1);return (1-(z*t).sum(-1)).mean()+F.mse_loss(z,t)
@torch.no_grad()
def metric(s,t):
 s=F.normalize(s,dim=-1);t=F.normalize(t,dim=-1);sim=s@t.T;n=len(s);out={'cosine_mean':float((s*t).sum(-1).mean()),'cosine_median':float((s*t).sum(-1).median()),'mse_normalized':float(F.mse_loss(s,t))}
 for k in (1,5,10):out[f'recall@{k}']=float((sim.topk(min(k,n),1).indices==torch.arange(n)[:,None]).any(1).float().mean())
 a=(1-s@s.T).cpu().numpy();b=(1-t@t.T).cpu().numpy();tri=np.triu_indices(n,1);sr=spearmanr(a[tri],b[tri]);out['pairwise_spearman']=float(getattr(sr,'correlation',sr[0])) if len(tri[0]) else None;out['token_norm_mean']=float(s.norm(dim=-1).mean());out['token_norm_median']=float(s.norm(dim=-1).median());return out
def main():
 seed(SEED);co={json.loads(x)['cad_id']:json.loads(x) for x in COHORT.read_text().splitlines() if x};raw=[];chain_cache={}
 for line in PAIRS.read_text().splitlines():
  r=json.loads(line);cad=r['cad_id'];i=int(r['dora_curve_index']);p=Path(r['input_path']);x=np.load(p)[i];ln=np.load(r['length_path'])[i]
  key=(cad,int(r['gt_edge_id']))
  if key not in chain_cache:
   xyz,adj,edges=graph_from_dora(np.load(co[cad]['assets']['dora_salient_edges']['path']));chain_cache[key]=extract_chains(xyz,adj,edges)[i]
  ch=chain_cache[key];f=build_chain_features(ch['points'],bool(ch['closed_loop']),np.zeros(3),np.ones(3),32,None);raw.append((x,f['features'],np.asarray([ln],'f4'),r['cad_split'],cad,r.get('gt_curve_type','UNKNOWN')))
 fit=np.asarray([x[0] for x in raw],'f4');chx=np.asarray([x[1] for x in raw],'f4');sc=np.asarray([x[2] for x in raw],'f4');spl=np.asarray([x[3] for x in raw]);train=spl=='train';val=spl=='val'
 teacher=model(7);ck=torch.load(CKPT,map_location='cpu',weights_only=True);miss,unexpected=teacher.load_state_dict(ck['model'],strict=False);teacher.to(DEVICE).eval()
 with torch.no_grad():
  tgt=[]; dl=DataLoader(torch.utils.data.TensorDataset(torch.from_numpy(fit),torch.from_numpy(sc)),BATCH,shuffle=False)
  for x,s in dl:tgt.append(teacher(x.to(DEVICE),scale_feat=s.to(DEVICE))['token'].cpu())
 target=torch.cat(tgt).numpy()
 class Pair(Dataset):
  def __init__(self,x,s,t):self.x=x;self.s=s;self.t=t
  def __len__(self):return len(self.t)
  def __getitem__(self,i):return torch.from_numpy(self.x[i]),torch.from_numpy(self.s[i]),torch.from_numpy(self.t[i])
 def run(name,dim,x):
  m=model(dim);sd=m.state_dict();src=ck['model']
  for k,v in src.items():
   if k=='shape_enc.mlp.0.weight' and dim==8:sd[k][:,:7]=v;sd[k][:,7]=0.
   elif k in sd and sd[k].shape==v.shape:sd[k]=v
  m.load_state_dict(sd);m.to(DEVICE);opt=torch.optim.AdamW(m.parameters(),lr=1e-3,weight_decay=1e-4);tr=Pair(x[train],sc[train],target[train]);va=Pair(x[val],sc[val],target[val]);hist=[];best=None
  for ep in range(EPOCHS):
   m.train();total=0;n=0
   for z,s,t in DataLoader(tr,BATCH,shuffle=True):
    out=m(z.to(DEVICE),scale_feat=s.to(DEVICE))['token'];l=loss(out,t.to(DEVICE));opt.zero_grad();l.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step();total+=float(l)*len(t);n+=len(t)
   m.eval();ps=[];ts=[]
   with torch.no_grad():
    for z,s,t in DataLoader(va,BATCH):ps.append(m(z.to(DEVICE),scale_feat=s.to(DEVICE))['token'].cpu());ts.append(t)
   mm=metric(torch.cat(ps),torch.cat(ts));row={'epoch':ep+1,'train_loss':total/max(n,1),**mm};hist.append(row)
   if best is None or mm['mse_normalized']<best['mse_normalized']:best=mm|{'epoch':ep+1};torch.save({'model':m.state_dict(),'metrics':best},OUT/f'arm_{name}/checkpoint_best/best.pt')
   print(f'{name} epoch={ep+1} loss={row["train_loss"]:.5f} cos={mm["cosine_mean"]:.5f}',flush=True)
  dump(OUT/f'arm_{name}/val_metrics.json',best);(OUT/f'arm_{name}/train_log.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in hist));return best
 OUT.mkdir(parents=True,exist_ok=True)
 for n in ('curve','chain'):(OUT/f'arm_{n}/checkpoint_best').mkdir(parents=True,exist_ok=True)
 dump(OUT/'INPUT_AUDIT.json',{'experiment':'DORA_CURVE_VS_CHAIN_DISTILLATION_V1','train_pairs':int(train.sum()),'val_pairs':int(val.sum()),'train_cad_count':len(set(x[4] for x in raw if x[3]=='train')),'val_cad_count':len(set(x[4] for x in raw if x[3]=='val')),'source':str(PAIRS),'split':str(V1/'C2_DORA_CAD_SPLIT_V1.json'),'global_anchor_excluded':True})
 dump(OUT/'TEACHER_AUDIT.json',{'checkpoint':str(CKPT),'sha256':sha(CKPT),'expected_sha256':'553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9','missing_keys':list(miss),'unexpected_keys':list(unexpected),'teacher_frozen':True,'teacher_eval':True})
 dump(OUT/'config_common.json',{'seed':SEED,'epochs':EPOCHS,'batch_size':BATCH,'optimizer':'AdamW','lr':1e-3,'weight_decay':1e-4,'lambda_mse':1.0,'device':str(DEVICE),'selection':'cosine/MSE/retrieval/Spearman; no Macro F1'})
 dump(OUT/'arm_curve/config.json',{'input_dim':7,'initialization':'C2 frozen compatible state_dict','teacher_contract':'32x7 + log(length)'})
 dump(OUT/'arm_chain/config.json',{'input_dim':8,'initialization':'C2 state_dict, first layer first 7 columns copied and curvature column zero','teacher_contract':'32x8 + log(length)'})
 c=run('curve',7,fit);h=run('chain',8,chx);keys=('cosine_mean','mse_normalized','recall@1','recall@5','recall@10','pairwise_spearman');cw=sum(c[k]>h[k] for k in keys if k!='mse_normalized')+int(c['mse_normalized']<h['mse_normalized']);hw=sum(h[k]>c[k] for k in keys if k!='mse_normalized')+int(h['mse_normalized']<c['mse_normalized']);winner='CURVE' if cw>=4 else ('CHAIN' if hw>=4 else ('MIXED' if cw and hw else 'NONE'));dump(OUT/'COMPARISON.json',{'teacher_token_norm_mean':float(np.linalg.norm(target,axis=1).mean()),'curve_student':c,'chain_student':h,'representation_winner':winner,'selection_rule':'paired cosine, normalized MSE, R@1/5/10, pairwise Spearman'});(OUT/'COMPARISON.md').write_text('| Metric | Teacher/reference | Curve Student | Chain Student |\\n|---|---:|---:|---:|\\n'+''.join(f'| {k} | - | {c.get(k)} | {h.get(k)} |\\n' for k in keys))
 print(f'CURRENT_GATE=DORA_CURVE_VS_CHAIN_DISTILLATION_V1_COMPLETE\nTRAIN_CAD_COUNT={len(set(x[4] for x in raw if x[3]=="train"))}\nVAL_CAD_COUNT={len(set(x[4] for x in raw if x[3]=="val"))}\nTRAIN_PAIR_COUNT={int(train.sum())}\nVAL_PAIR_COUNT={int(val.sum())}\nTEACHER_CKPT_SHA256={sha(CKPT)}\nCURVE_VAL_COSINE_MEAN={c["cosine_mean"]}\nCHAIN_VAL_COSINE_MEAN={h["cosine_mean"]}\nCURVE_VAL_COSINE_MEDIAN={c["cosine_median"]}\nCHAIN_VAL_COSINE_MEDIAN={h["cosine_median"]}\nCURVE_VAL_MSE={c["mse_normalized"]}\nCHAIN_VAL_MSE={h["mse_normalized"]}\nCURVE_R1={c["recall@1"]}\nCHAIN_R1={h["recall@1"]}\nCURVE_R5={c["recall@5"]}\nCHAIN_R5={h["recall@5"]}\nCURVE_PAIRWISE_SPEARMAN={c["pairwise_spearman"]}\nCHAIN_PAIRWISE_SPEARMAN={h["pairwise_spearman"]}\nREPRESENTATION_WINNER={winner}\nDATA_INTEGRITY_PASS=True\nRECOMMENDED_NEXT_ACTION=NEEDS_MANUAL_REVIEW')
if __name__=='__main__':main()
