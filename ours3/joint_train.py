import os,sys,json,time,shutil
from pathlib import Path
import torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_20case_v3_joint_overfit_v1'; CFG=EXP/'config/joint_train_v1.yaml'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
import spatiallm.model.spatiallm_llama as llama
sys.argv=['joint_train',str(CFG)]; args=read_args(); ma,da,ta,fa,ga=get_train_args(args)
tm=load_tokenizer(ma); tok=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False); template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta); split=ds[next(k for k in ds if 'train' in str(k).lower())]; model=load_model(tok,da,ma,fa,True); device=torch.device('cuda'); model.to(device).train()
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm); opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=5e-6); counts=[0]*len(split); schedule=[20,40,80,160,320,640]; records=[]; best=(-1,10**18,10**18)
def batch(i):
 b=coll([dict(split[i])]); return {k:(v.to(device) if torch.is_tensor(v) else v) for k,v in b.items()}
def scan():
 model.eval(); rows=[]
 def audit(lm_head,hidden_states,labels,chunk_size=256,ignore_index=IGNORE_INDEX):
  h=hidden_states[:,:-1,:]; y=labels[:,1:]; errs=[]; valid=0
  for st in range(0,h.shape[1],chunk_size):
   pred=lm_head(h[:,st:st+chunk_size]).argmax(-1); gold=y[:,st:st+chunk_size]; mask=gold.ne(ignore_index); errs.extend(st+int(j) for _,j in (pred.ne(gold)&mask).nonzero(as_tuple=False).tolist()); valid+=int(mask.sum())
  audit.last={'errors':errs,'valid':valid,'full':int(hidden_states.shape[1])}; return hidden_states.new_zeros(())
 llama._chunked_lm_loss=audit
 with torch.no_grad():
  for i,row in enumerate(split):
   b=batch(i); model(**b); a=audit.last; rows.append({'case_id':row.get('id',f'case_{i:03d}'),'tf_error_n':len(a['errors']),'tf_supervised_token_n':a['valid'],'tf_accuracy':1-len(a['errors'])/a['valid'],'full_sequence_token_n':a['full']})
 import importlib; importlib.reload(llama); model.train(); return rows
for step in range(1,641):
 i=(step-1)%len(split); counts[i]+=1; t=time.time(); b=batch(i); out=model(**b); out.loss.backward(); opt.step(); opt.zero_grad(set_to_none=True); rec={'update':step,'case_index':i,'input_len':int(b['input_ids'].shape[1]),'loss':float(out.loss.detach().cpu()),'step_s':time.time()-t}
 if step in schedule:
  rows=scan(); total=sum(x['tf_error_n'] for x in rows); zero=sum(x['tf_error_n']==0 for x in rows); mx=max(x['tf_error_n'] for x in rows); rec.update({'total_errors':total,'zero_error_case_n':zero,'max_case_error':mx,'demo5_zero_case_n':sum(x['tf_error_n']==0 for x in rows if x['case_id'] in ['case_018','case_009','case_014','case_010','case_005']),'free_disk_gb':shutil.disk_usage('/data').free/1e9}); (EXP/'tf_eval'/f'TF_SCAN_{step:04d}.json').write_text(json.dumps(rows,indent=2));
  score=(zero,total,mx)
  if score[:1] > best[:1] or (zero==best[0] and (total,mx)<(best[1],best[2])): best=score; rec['best']=True
  records.append(rec); (EXP/'logs/progress.json').write_text(json.dumps({'records':records,'exposure_counts':counts,'best':best},indent=2)); print(json.dumps(rec),flush=True)
  if zero==20:
   frozen=EXP/'frozen_tf20_success_v1'; frozen.mkdir(exist_ok=True); model.save_pretrained(frozen,safe_serialization=True,max_shard_size='4GB'); tok.save_pretrained(frozen); (EXP/'tf_eval/FIRST_20_OF_20_TF_ZERO.json').write_text(json.dumps({'update':step,'rows':rows},indent=2)); break
(EXP/'logs/final.json').write_text(json.dumps({'records':records,'exposure_counts':counts,'best':best},indent=2))
