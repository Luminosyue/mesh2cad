import os,sys,json
from pathlib import Path
import torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; CFG=EXP/'demo5/p3_train_resume_v1.yaml'; frozen=EXP/'frozen_tf5_success_v1'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
import spatiallm.model.spatiallm_llama as llama
sys.argv=['verify',str(CFG)]; args=read_args(); ma,da,ta,fa,ga=get_train_args(args); ma.model_name_or_path=str(frozen)
tm=load_tokenizer(ma); tok=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False); template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta); split=ds[next(k for k in ds if 'train' in str(k).lower())]; model=load_model(tok,da,ma,fa,False); device=torch.device('cuda'); model.to(device).eval()
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
rows=[]
for i,row in enumerate(split):
    cap={}
    def audit_loss(lm_head,hidden_states,labels,chunk_size=256,ignore_index=IGNORE_INDEX):
        h=hidden_states[:,:-1,:]; y=labels[:,1:]; errs=[]; valid=0
        for st in range(0,h.shape[1],chunk_size):
            pred=lm_head(h[:,st:st+chunk_size]).argmax(-1); gold=y[:,st:st+chunk_size]; mask=gold.ne(ignore_index); errs.extend((st+int(j)) for _,j in (pred.ne(gold)&mask).nonzero(as_tuple=False).tolist()); valid+=int(mask.sum())
        cap.update(errors=errs,valid=valid,full=int(hidden_states.shape[1])); return hidden_states.new_zeros(())
    llama._chunked_lm_loss=audit_loss; b=coll([dict(row)]); b={k:(v.to(device) if torch.is_tensor(v) else v) for k,v in b.items()}
    with torch.no_grad(): model(**b)
    rows.append({'case_id':row.get('id',f'case_{i:03d}'),'tf_error_n':len(cap['errors']),'tf_supervised_token_n':cap['valid'],'tf_accuracy':1-len(cap['errors'])/cap['valid'],'full_sequence_token_n':cap['full']})
(EXP/'eval/FROZEN_CHECKPOINT_TF_AUDIT.json').write_text(json.dumps({'rows':rows,'zero_error_case_n':sum(x['tf_error_n']==0 for x in rows),'total_errors':sum(x['tf_error_n'] for x in rows)},indent=2)); print(json.dumps(rows))
