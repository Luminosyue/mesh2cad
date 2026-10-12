from pathlib import Path
import sys,json
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1';sys.path.insert(0,str(E/'launch'))
from a2_runtime import *
import spatiallm.model.spatiallm_llama as lm
model,tok=load(OLD/'runs/quick/checkpoint-2000');model.float();torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
batches=torch.load(E/'data/collated_batches.pt',weights_only=False);inv=json.loads((E/'data/block_inventory.json').read_text());rows=[]
for p,block,token in [('PART_001',1,207),('PART_005',1,981),('PART_000',6,-1),('PART_001',13,-1),('PART_005',25,-1)]:
 b=next(b for b,r in zip(batches,inv) if r['part']==p and r['block']==block);b=gpu_batch(b);pos=(b['labels'][0]!=-100).nonzero().flatten();idx=len(pos)-1 if token<0 else token-1;gt=int(b['labels'][0,pos[idx]]);full=[];old=lm._chunked_lm_loss
 def capture(head,h,labels,*a,**kw):
  q=(labels[0,1:]!=-100).nonzero().flatten()+1;full.append(head(h[0,q[idx]-1:q[idx]]).float().detach());return h.new_zeros(())
 lm._chunked_lm_loss=capture
 with torch.inference_mode():model(**b,use_cache=False)
 lm._chunked_lm_loss=old
 ids=b['input_ids'][:,:pos[idx]];geo={k:b[k] for k in ['point_clouds','edge_clouds']}
 with torch.inference_mode():
  no=model(input_ids=ids,attention_mask=torch.ones_like(ids),**geo,use_cache=False,num_logits_to_keep=1).logits[0,-1:]
  pre=model(input_ids=ids[:,:-1],attention_mask=torch.ones_like(ids[:,:-1]),**geo,use_cache=True,num_logits_to_keep=1)
  cached=model(input_ids=ids[:,-1:],attention_mask=torch.ones_like(ids),past_key_values=pre.past_key_values,use_cache=True,num_logits_to_keep=1).logits[0,-1:]
 row={'part':p,'block':block,'token_in_block':idx+1,'precision':'FP32; TF32 disabled; same quantized geometry values','max_abs_full_vs_prefix':float((full[0]-no).abs().max()),'max_abs_prefix_vs_cached':float((no-cached).abs().max()),'argmax_ids':[int(v.argmax()) for v in [full[0],no,cached]],'gt_id':gt}
 row['PASS']=max(row['max_abs_full_vs_prefix'],row['max_abs_prefix_vs_cached'])<1e-3 and len(set(row['argmax_ids']))==1
 rows.append(row);save(E/'diagnostics/fp32_numeric_checks.json',rows);print(row,flush=True)
save(E/'diagnostics/fp32_numeric_summary.json',{'PASS':all(r['PASS'] for r in rows),'records':rows})
