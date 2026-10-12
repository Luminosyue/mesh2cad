import os,sys,json,time
from pathlib import Path
import torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; CFG=EXP/'demo5/p3_train_resume_v1.yaml'; frozen=EXP/'frozen_tf5_success_v1'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
sys.argv=['free_remaining',str(CFG)]; args=read_args(); ma,da,ta,fa,ga=get_train_args(args); ma.model_name_or_path=str(frozen)
tm=load_tokenizer(ma); tok=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False); template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta); split=ds[next(k for k in ds if 'train' in str(k).lower())]; model=load_model(tok,da,ma,fa,False); device=torch.device('cuda'); model.to(device).eval()
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
rows=[]
for i in [0,1,3,4]:
    row=split[i]; b=coll([dict(row)]); b={k:(v.to(device) if torch.is_tensor(v) else v) for k,v in b.items()}; valid=torch.where(b['labels'][0].ne(IGNORE_INDEX))[0]; start=int(valid[0]); target=b['labels'][0,valid].detach().cpu().tolist(); inp={'input_ids':b['input_ids'][:,:start],'attention_mask':b['attention_mask'][:,:start]};
    for k in ['point_clouds','edge_clouds']:
        if k in b: inp[k]=b[k]
    t=time.time()
    with torch.no_grad(): gen=model.generate(**inp,max_new_tokens=len(target)+64,do_sample=False,num_beams=1,use_cache=True,pad_token_id=128001,eos_token_id=[128001,128008,128009])
    elapsed=time.time()-t; generated=gen[0,start:].detach().cpu().tolist(); exact=generated[:len(target)]==target; first=next((j for j,(a,c) in enumerate(zip(target,generated)) if a!=c),None); eos=bool(generated and generated[-1] in [128001,128008,128009]); text=tok.decode(generated,skip_special_tokens=False); out=EXP/'eval'/f'generated_{i:02d}.v3'; out.write_text(text); rec={'case_id':row.get('id',f'case_{i:03d}'),'object_id':row.get('id',f'case_{i:03d}'),'gt_token_n':len(target),'generated_token_n':len(generated),'token_exact':exact,'first_divergence':first,'natural_eos':eos,'elapsed_s':elapsed}; rows.append(rec); (EXP/'eval'/f'FREE_{i:02d}_GATE.json').write_text(json.dumps(rec,indent=2)); print(json.dumps(rec),flush=True)
(EXP/'eval/FREE_REMAINING_GATE.json').write_text(json.dumps({'rows':rows,'free_exact_case_n':sum(x['token_exact'] for x in rows),'natural_eos_case_n':sum(x['natural_eos'] for x in rows)},indent=2))
