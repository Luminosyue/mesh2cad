import os,sys,json,torch
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; V3=ROOT/'ours3/p3_xpart_20case_compact_ir_v3'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
sys.argv=['formal_audit',str(V3/'training20/p3_train_v3.yaml')]
args=read_args(); ma,da,ta,fa,ga=get_train_args(args)
tm=load_tokenizer(ma); tok=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False)
template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta); split=ds[next(k for k in ds if 'train' in str(k).lower())]
model=load_model(tok,da,ma,fa,True)
cats={}
for n,p in model.named_parameters():
    top=n.split('.')[0]
    if any(x in n.lower() for x in ['point_backbone','surface','sonata']): top='surface_encoder'
    elif any(x in n.lower() for x in ['curve','edge_proj']): top='curve_encoder'
    elif 'projector' in n.lower(): top='projector'
    elif any(x in n.lower() for x in ['fusion','point_proj','curve_proj']): top='fusion'
    elif any(x in n.lower() for x in ['lm_head','embed_tokens']): top='lm_head'
    elif any(x in n.lower() for x in ['model','layers','norm']): top='language_tower'
    else: top='other'
    d=cats.setdefault(top,{'total':0,'trainable':0,'frozen':0,'dtypes':{}}); num=p.numel(); d['total']+=num; d['trainable' if p.requires_grad else 'frozen']+=num; d['dtypes'][str(p.dtype)]=d['dtypes'].get(str(p.dtype),0)+num
total=sum(p.numel() for p in model.parameters()); train=sum(p.numel() for p in model.parameters() if p.requires_grad)
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
lengths=[]
for i,row in enumerate(split):
    b=coll([dict(row)]); inp=int(b['input_ids'].shape[1]); labels=b['labels']; sup=int((labels!=IGNORE_INDEX).sum().item()); lengths.append({'index':i,'case_id':row.get('id',row.get('case_id',f'case_{i:03d}')),'target_token_n':sup,'actual_model_input_token_n':inp,'overhead':inp-sup})
out={'parameter_audit':{'total_parameter_n':total,'trainable_parameter_n':train,'frozen_parameter_n':total-train,'modules':cats,'trainable_dtype_counts':{}},'sequence_accounting':{'rows':lengths,'max_target_token_n':max(x['target_token_n'] for x in lengths),'max_model_input_token_n':max(x['actual_model_input_token_n'] for x in lengths),'longest_case_id':max(lengths,key=lambda x:x['actual_model_input_token_n'])['case_id']}}
for p in model.parameters():
    if p.requires_grad: out['parameter_audit']['trainable_dtype_counts'][str(p.dtype)]=out['parameter_audit']['trainable_dtype_counts'].get(str(p.dtype),0)+p.numel()
(EXP/'memory_audit/TRAINABLE_PARAMETER_AUDIT.json').write_text(json.dumps(out['parameter_audit'],indent=2)); (EXP/'memory_audit/SEQUENCE_LENGTH_ACCOUNTING.json').write_text(json.dumps(out['sequence_accounting'],indent=2)); print(json.dumps(out))
