import os,sys,json,time,copy
from pathlib import Path
os.environ.update(CAD_USE_EDGE_SCORE='0',CAD_USE_SEPARATE_EDGE_TOKENS='0',DISABLE_VERSION_CHECK='1',OMP_NUM_THREADS='4',TOKENIZERS_PARALLELISM='false')
import torch
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1';sys.path[:0]=[str(R/'scripts'),str(R/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
sys.argv=['smoke',str(E/'data/pottery_large/train.yaml')];ma,da,ta,fa,ga=get_train_args(read_args());ma.model_name_or_path=json.loads((E/'runs/pottery_large/LATEST_CHECKPOINT.json').read_text())['path']
tm=load_tokenizer(ma);tok=tm['tokenizer'];register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False);template=get_template_and_fix_tokenizer(tok,da);ds=get_dataset(ma,da,ta);split=ds[next(k for k in ds if 'train' in str(k).lower())]
model=load_model(tok,da,ma,fa,True).to('cuda').eval();model.gradient_checkpointing_disable();model.config.use_cache=True
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
b=coll([copy.deepcopy(dict(split[0]))]);valid=b['labels'][0].ne(-100).nonzero().flatten();start=int(valid[0]);gold=b['labels'][0,valid].tolist()
inp={k:v for k,v in b.items() if k not in ['labels','position_ids']}
for k in ['input_ids','attention_mask','token_type_ids']:
 if k in inp:inp[k]=inp[k][:,:start]
inp={k:v.to('cuda') if torch.is_tensor(v) else v for k,v in inp.items()}
t=time.time()
with torch.inference_mode():out=model.generate(**inp,max_new_tokens=64,do_sample=False,num_beams=1,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id,eos_token_id=[128001,128008,128009])
ids=out[0,start:].tolist();record=dict(PASS=len(ids)>0,checkpoint=ma.model_name_or_path,prompt_tokens=start,gt_prefix_tokens=0,generated_tokens=len(ids),elapsed_seconds=time.time()-t,cached_greedy_generation_works=True,full_generation_success=False,reason='64-token runtime smoke only; never counted as natural EOS/full exact',decoded_prefix=tok.decode(ids,skip_special_tokens=False),prefix_matches=ids==gold[:len(ids)])
(E/'reports/GENERATION_RUNTIME_SMOKE.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
