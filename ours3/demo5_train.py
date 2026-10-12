import os,sys,json,time,shutil,traceback
from pathlib import Path
import torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; CFG=Path(os.environ.get('DEMO5_CONFIG',str(EXP/'demo5/p3_train_demo5_v1.yaml')))
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
os.environ['CAD_USE_EDGE_SCORE']='0'
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
import spatiallm.model.spatiallm_llama as spatiallm_llama
sys.argv=['demo5_train',str(CFG)]
args=read_args(); ma,da,ta,fa,ga=get_train_args(args)
tm=load_tokenizer(ma); tok=tm['tokenizer']; register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False)
template=get_template_and_fix_tokenizer(tok,da); ds=get_dataset(ma,da,ta); split=ds[next(k for k in ds if 'train' in str(k).lower())]
model=load_model(tok,da,ma,fa,True); device=torch.device('cuda'); model.to(device).train()
coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=5e-6)
counts=[0]*len(split); schedule=[20,40,80,160,320]; log=[]; START=int(os.environ.get('DEMO5_START_STEP','0'))
def batch_for(i):
    b=coll([dict(split[i])]); return {k:(v.to(device) if torch.is_tensor(v) else v) for k,v in b.items()}
def tf_scan():
    model.eval(); rows=[]
    def audit_loss(lm_head,hidden_states,labels,chunk_size=256,ignore_index=IGNORE_INDEX):
        h=hidden_states[:,:-1,:]; y=labels[:,1:]; errors=[]; valid=0
        for st in range(0,h.shape[1],chunk_size):
            pred=lm_head(h[:,st:st+chunk_size]).argmax(-1); gold=y[:,st:st+chunk_size]; mask=gold.ne(ignore_index)
            for b,j in (pred.ne(gold)&mask).nonzero(as_tuple=False).tolist(): errors.append(st+int(j))
            valid += int(mask.sum())
        audit_loss.last={'errors':errors,'valid':valid,'full_sequence':int(hidden_states.shape[1])}; return hidden_states.new_zeros(())
    spatiallm_llama._chunked_lm_loss=audit_loss
    with torch.no_grad():
        for i,row in enumerate(split):
            b=batch_for(i); model(**b); a=audit_loss.last; err=len(a['errors']); sup=a['valid']; rows.append({'case_id':row.get('id',f'case_{i:03d}'),'tf_supervised_token_n':sup,'tf_error_n':err,'tf_accuracy':(sup-err)/sup if sup else 0.0,'full_sequence_token_n':a['full_sequence'],'eos_correct':(a['full_sequence']-2) not in a['errors']})
    import importlib
    importlib.reload(spatiallm_llama)
    model.train(); return rows
def free_generate():
    model.eval(); outs=[]
    with torch.no_grad():
        for i,row in enumerate(split):
            full=batch_for(i); lab=full['labels']; valid=torch.where(lab[0].ne(IGNORE_INDEX))[0]; start=int(valid[0].item())
            inp={'input_ids':full['input_ids'][:,:start], 'attention_mask':full['attention_mask'][:,:start]}
            for k in ['point_clouds','edge_clouds']:
                if k in full: inp[k]=full[k]
            gen=model.generate(**inp,max_new_tokens=int(valid.numel()+64),do_sample=False,num_beams=1,use_cache=False)
            generated=gen[0,start:].detach().cpu().tolist(); target=lab[0,valid].detach().cpu().tolist(); exact=generated[:len(target)]==target
            natural_eos=bool(generated and generated[-1] in [tok.eos_token_id] if isinstance(tok.eos_token_id,int) else generated and generated[-1] in tok.eos_token_id)
            text=tok.decode(generated,skip_special_tokens=False); (EXP/'eval'/f'generated_{i:02d}.v3').write_text(text)
            outs.append({'case_id':row.get('id',f'case_{i:03d}'),'gt_token_n':len(target),'generated_token_n':len(generated),'free_token_exact':exact,'first_divergence':next((j for j,(a,b) in enumerate(zip(target,generated)) if a!=b),None),'natural_eos':natural_eos})
    (EXP/'eval/FREE_GENERATION_GATE.json').write_text(json.dumps({'rows':outs,'free_exact_case_n':sum(x['free_token_exact'] for x in outs)},indent=2)); model.train(); return outs
for step in range(START+1,321):
    i=(step-1)%len(split); counts[i]+=1; t=time.time(); b=batch_for(i); o=model(**b); o.loss.backward(); opt.step(); opt.zero_grad(set_to_none=True)
    rec={'step':step,'case_index':i,'case_id':split[i].get('id',f'case_{i:03d}'),'loss':float(o.loss.detach().cpu()),'input_len':int(b['input_ids'].shape[1]),'step_s':time.time()-t}
    if step in schedule:
        disk=shutil.disk_usage('/data'); rec['free_disk_gb_before']=disk.free/1e9
        ck=EXP/'checkpoints'/f'checkpoint-{step}'
        if disk.free/1e9 < float(os.environ.get('MIN_SAVE_GB','20.5')):
            rec['checkpoint_status']='SKIPPED_DISK_SAFETY_GATE'
        else:
            try:
                model.save_pretrained(ck,safe_serialization=True,max_shard_size='4GB'); tok.save_pretrained(ck); rec['checkpoint_status']='SAVED'
            except Exception as e: rec['checkpoint_status']=f'SAVE_ERROR:{type(e).__name__}:{e}'
        rows=tf_scan(); (EXP/'eval'/f'TF_SCAN_{step:03d}.json').write_text(json.dumps(rows,indent=2)); rec['tf_error_total']=sum(x['tf_error_n'] for x in rows); rec['tf_zero_case_n']=sum(x['tf_error_n']==0 for x in rows)
    log.append(rec); print(json.dumps(rec),flush=True); (EXP/'logs/demo5_train_progress.json').write_text(json.dumps({'records':log,'exposure_counts':counts},indent=2))
    if step in schedule and rec.get('tf_zero_case_n')==len(split):
        (EXP/'eval/FIRST_5_OF_5_TF_ZERO.json').write_text(json.dumps({'checkpoint':step,'rows':rows},indent=2))
        frozen=os.environ.get('SAVE_FROZEN_DIR')
        if frozen:
            Path(frozen).mkdir(parents=True,exist_ok=True); model.save_pretrained(frozen,safe_serialization=True,max_shard_size='4GB'); tok.save_pretrained(frozen)
        if os.environ.get('SKIP_FREE','0')!='1': free_generate()
        break
(EXP/'logs/demo5_train_final.json').write_text(json.dumps({'records':log,'exposure_counts':counts},indent=2))
