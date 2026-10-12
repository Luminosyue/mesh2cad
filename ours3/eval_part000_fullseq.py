import os,sys,json,torch,hashlib,traceback,numpy as np
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/airplane_fullseq_14bit_ir_v1'; os.environ['CUDA_VISIBLE_DEVICES']='7'; os.environ['CAD_SECOND_STREAM']='curve_tokens'; os.environ['CAD_USE_SEPARATE_EDGE_TOKENS']='1'; os.environ['CURVE_TOKEN_REGISTRY']=str(EXP/'curve_registry.jsonl'); os.environ['REQUIRE_CURVE_TOKEN_REGISTRY']='1'; os.environ['C2_CHECKPOINT_PATH']=str(ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt')
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM'),str(EXP)]
from spatiallm_curve_token_v1 import curve_token_injector; curve_token_injector.install()
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
from transformers import Seq2SeqTrainingArguments
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
import spatiallm.model.spatiallm_llama as spatiallm_llama
# parse config
sys.argv=['x',str(EXP/'part000_overfit.yaml')]; args=read_args(); ma,da,ta,fa,ga=get_train_args(args)
ma.model_name_or_path=str(EXP/'runs/part000_overfit')
tm=load_tokenizer(ma); tokenizer=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False); template=get_template_and_fix_tokenizer(tokenizer,da); ds=get_dataset(ma,da,ta); model=load_model(tokenizer,da,ma,fa,False); DEVICE=torch.device('cuda'); model.to(DEVICE); model.eval();
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
# materialize one example and collate
train_keys=[k for k in ds.keys() if 'train' in str(k).lower()]
if not train_keys:
    raise KeyError(f'No training split found in dataset keys: {list(ds.keys())}')
train_split=ds[train_keys[0]]
ex=train_split[0]; batch=coll([dict(ex)])
def move_to_device(x):
    if torch.is_tensor(x): return x.to(DEVICE)
    if isinstance(x, np.ndarray): return torch.from_numpy(x).to(DEVICE)
    if isinstance(x, dict): return {k:move_to_device(v) for k,v in x.items()}
    if isinstance(x, (list, tuple)): return type(x)(move_to_device(v) for v in x)
    return x
batch=move_to_device(batch)
for _k in list(batch):
    if torch.is_tensor(batch[_k]): batch[_k]=batch[_k].to(DEVICE)
labels=batch['labels']; target_mask=labels[0].ne(IGNORE_INDEX); n=int(target_mask.sum())
tf_audit={}
def audit_loss(lm_head, hidden_states, aligned_labels, chunk_size=256, ignore_index=IGNORE_INDEX):
    total_loss=hidden_states.new_zeros(()); errors=[]; valid=0
    shifted_h=hidden_states[:,:-1,:]; shifted_y=aligned_labels[:,1:]
    for start in range(0, shifted_h.shape[1], chunk_size):
        h=shifted_h[:,start:start+chunk_size]
        y=shifted_y[:,start:start+chunk_size]
        logits=lm_head(h)
        mask=y.ne(ignore_index)
        if mask.any():
            pred=logits.argmax(-1)
            bad=(pred.ne(y) & mask).nonzero(as_tuple=False)
            errors.extend((int(start+i), int(y[b,i]), int(pred[b,i])) for b,i in bad.tolist())
            valid += int(mask.sum())
            total_loss = total_loss + torch.nn.functional.cross_entropy(logits[mask].float(), y[mask]) * int(mask.sum())
    tf_audit.update({'errors':errors,'valid':valid,'aligned_label_shape':list(aligned_labels.shape),'hidden_shape':list(hidden_states.shape)})
    return total_loss / max(valid,1)
spatiallm_llama._chunked_lm_loss=audit_loss
with torch.no_grad(): model(**batch)
err=len(tf_audit['errors']); first=tf_audit['errors'][0][0] if err else None; last=tf_audit['errors'][-1][0] if err else None
# prompt = prefix through source; generation receives conditioning tensors from batch
src_len=int((labels[0]==IGNORE_INDEX).sum()); prompt_ids=batch['input_ids'][:,:src_len]; gen_kwargs={k:v for k,v in batch.items() if k in ('point_clouds','edge_clouds')}; gen_kwargs.update({'input_ids':prompt_ids,'attention_mask':torch.ones_like(prompt_ids),'max_new_tokens':n+64,'do_sample':False,'num_beams':1,'use_cache':True,'eos_token_id':tokenizer.eos_token_id,'pad_token_id':tokenizer.pad_token_id})
with torch.no_grad(): generated=model.generate(**gen_kwargs)[0]
gen_new=generated[src_len:].tolist(); gt=labels[0,target_mask].tolist(); exact=(gen_new==gt); div=next((i for i,(a,b) in enumerate(zip(gen_new,gt)) if a!=b),min(len(gen_new),len(gt)) if len(gen_new)!=len(gt) else None)
generated_text=tokenizer.decode(gen_new, skip_special_tokens=False, clean_up_tokenization_spaces=False)
(EXP/'eval').mkdir(parents=True,exist_ok=True)
(EXP/'eval'/'part000_generated.ir').write_text(generated_text, encoding='utf-8')
report={'PART_ID':'PART_000','TARGET_TOKEN_N':n,'SUPERVISED_TARGET_TOKEN_N':n,'TF_TOKEN_ERROR_N':err,'TF_TOKEN_ACCURACY':1-err/max(tf_audit['valid'],1),'FIRST_ERROR_POSITION':first,'LAST_ERROR_POSITION':last,'TF_ALIGNED_LABEL_SHAPE':tf_audit['aligned_label_shape'],'TF_HIDDEN_SHAPE':tf_audit['hidden_shape'],'GENERATED_TOKEN_N':len(gen_new),'FREE_TOKEN_EXACT':exact,'FIRST_DIVERGENCE_POSITION':div,'NATURAL_EOS':bool(len(gen_new)>0 and gen_new[-1] in ([tokenizer.eos_token_id] if isinstance(tokenizer.eos_token_id,int) else tokenizer.eos_token_id)),'MODEL_PATH':str(EXP/'runs/part000_overfit'),'TF_LOGITS_NOTE':'Evaluation-only capture of model-native spliced labels and hidden states.'}
json.dump(report,open(EXP/'eval/part000_fullseq_eval.json','w'),indent=2); print(json.dumps(report,indent=2))
