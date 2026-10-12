import os,sys,json,torch
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
os.environ['CUDA_VISIBLE_DEVICES']=os.environ.get('CUDA_VISIBLE_DEVICES','1')
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
sys.argv=['smoke',str(EXP/'p3_train.yaml')]
args=read_args(); ma,da,ta,fa,ga=get_train_args(args)
ma.low_cpu_mem_usage=False
tm=load_tokenizer(ma); tok=tm['tokenizer']
register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False)
template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta)
split=ds[next(k for k in ds if 'train' in str(k).lower())]
model=load_model(tok,da,ma,fa,True)
device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); model.to(device).eval()
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
batch=coll([dict(split[0])])
for k,v in list(batch.items()):
 if torch.is_tensor(v): batch[k]=v.to(device)
with torch.no_grad(): out=model(**batch)
rec={'dataset_n':len(split),'input_shape':list(batch['input_ids'].shape),'loss':float(out.loss.detach().cpu()) if getattr(out,'loss',None) is not None else None,'device':str(device),'cutoff_len':da.cutoff_len}
(EXP/'context_audit/memory_smoke.json').write_text(json.dumps(rec,indent=2)); print(json.dumps(rec),flush=True)
