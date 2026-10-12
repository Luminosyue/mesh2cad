from pathlib import Path
import sys,json,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');sys.path.insert(0,str(E/'launch'))
from a2_runtime import *
from a2_runtime import _load_sepedge
model,tok=load(E.parent/'p1_airplane3_exact_overfit_v1/runs/quick/checkpoint-2000');plugin=make_plugin(separate_edge=True)
part=next(r for r in json.loads((E/'data/parts.json').read_text()) if r['part']=='PART_005');s,e=_load_sepedge(plugin,Path(part['folder'])/'surface_points.npy');s=s.cuda().bfloat16();e=e.cuda().bfloat16()
msg=plugin.process_messages([{'role':'user','content':prompt_for(tok,'',0)}],[{}]);prompt=tok.apply_chat_template(msg,add_generation_prompt=True,return_tensors='pt').cuda()
probes=json.loads((E/'diagnostics/PART_005/cache_generation_probes.json').read_text());a,b=[r['tokens'] for r in probes];idx=next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y);assert a[:idx]==b[:idx]
results=[]
for dtype in [torch.bfloat16,torch.float32]:
 if dtype==torch.float32:model.float();torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 ids=prompt;past=None
 with torch.inference_mode():
  for j in range(idx+1):
   kw=model.prepare_inputs_for_generation(ids,past_key_values=past,attention_mask=torch.ones_like(ids),point_clouds=s,edge_clouds=e,use_cache=True)
   o=model(**kw,num_logits_to_keep=1);past=o.past_key_values
   if j<idx:ids=torch.cat([ids,ids.new_tensor([[a[j]]])],dim=1)
  cached=o.logits[0,-1].float();no=model(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=s,edge_clouds=e,use_cache=False,num_logits_to_keep=1).logits[0,-1].float()
 result={'dtype':str(dtype),'token_in_generated_block':idx+1,'prefix_source':'same unassisted model-generated prefix, no GT','max_abs_logit_diff':float((cached-no).abs().max()),'cache_argmax':int(cached.argmax()),'no_cache_argmax':int(no.argmax()),'candidate_ids':[a[idx],b[idx]],'candidate_tokens':[tok.decode([a[idx]]),tok.decode([b[idx]])],'cache_candidate_logits':[float(cached[x]) for x in [a[idx],b[idx]]],'no_cache_candidate_logits':[float(no[x]) for x in [a[idx],b[idx]]]}
 results.append(result);save(E/'diagnostics/cache_divergence_precision.json',results);print(result,flush=True)
