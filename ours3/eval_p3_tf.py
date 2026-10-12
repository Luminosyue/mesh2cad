import os,sys,json,csv,time
from pathlib import Path
import numpy as np, torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'
os.environ['CAD_USE_EDGE_SCORE']='0'; sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
import spatiallm.model.spatiallm_llama as spatiallm_llama
sys.argv=['eval',str(EXP/'p3_train.yaml')]
args=read_args(); ma,da,ta,fa,ga=get_train_args(args); ma.low_cpu_mem_usage=False
tm=load_tokenizer(ma); tok=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False)
template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta); split=ds[next(k for k in ds if 'train' in str(k).lower())]
model=load_model(tok,da,ma,fa,False); device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); model.to(device).eval()
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
def move(x):
    if torch.is_tensor(x): return x.to(device)
    if isinstance(x,np.ndarray): return torch.from_numpy(x).to(device)
    if isinstance(x,dict): return {k:move(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return type(x)(move(v) for v in x)
    return x
rows=[]
for i in range(len(split)):
    capture={}
    def audit_loss(lm_head,hidden_states,labels,chunk_size=256,ignore_index=IGNORE_INDEX):
        errs=[]; valid=0; h=hidden_states[:,:-1,:]; y=labels[:,1:]
        for st in range(0,h.shape[1],chunk_size):
            logits=lm_head(h[:,st:st+chunk_size]); gold=y[:,st:st+chunk_size]; mask=gold.ne(ignore_index); pred=logits.argmax(-1)
            bad=(pred.ne(gold)&mask).nonzero(as_tuple=False); errs.extend((st+int(j),int(gold[b,j]),int(pred[b,j])) for b,j in bad.tolist()); valid+=int(mask.sum())
        capture.update(errors=errs,valid=valid,full_sequence=int(hidden_states.shape[1])); return hidden_states.new_zeros(())
    spatiallm_llama._chunked_lm_loss=audit_loss
    batch=coll([dict(split[i])])
    for key in list(batch):
        if torch.is_tensor(batch[key]): batch[key]=batch[key].to(device)
    with torch.no_grad(): model(**batch)
    e=capture['errors']; r={'CHECKPOINT':'init_step0','CASE_ID':split[i].get('id',f'case_{i:03d}'),'TARGET_TOKEN_N':capture['valid'],'FULL_SEQUENCE_TOKEN_N':capture['full_sequence'],'TF_ERROR_N':len(e),'TF_ACCURACY':1-len(e)/capture['valid'] if capture['valid'] else 0,'FIRST_ERROR':e[0][0] if e else None,'LAST_ERROR':e[-1][0] if e else None,'EOS_CORRECT':not any(p==capture['full_sequence']-2 for p,_,_ in e)}; rows.append(r); print(json.dumps(r),flush=True)
(EXP/'eval/initial_tf.json').write_text(json.dumps({'rows':rows,'ZERO_ERROR_CASE_N':sum(x['TF_ERROR_N']==0 for x in rows),'TOTAL_ERRORS':sum(x['TF_ERROR_N'] for x in rows)},indent=2))
with (EXP/'reports/20CASE_TF_ERROR_TRAJECTORY.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps({'zero_error_case_n':sum(x['TF_ERROR_N']==0 for x in rows),'total_errors':sum(x['TF_ERROR_N'] for x in rows)},indent=2))
