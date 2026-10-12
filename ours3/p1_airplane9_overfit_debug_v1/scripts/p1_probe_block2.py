from p1_debug_runtime import *
import types
model,tok=load();batches=torch.load(DEBUG/'collated_batches.pt',weights_only=False);b=batches[1];start=int((b['labels'][0]!=-100).nonzero()[0]);prompt=b['input_ids'][:,:start].cuda();gt=b['labels'][0,start:][b['labels'][0,start:]!=-100].tolist();geometry={k:v.cuda() for k,v in b.items() if k in ['point_clouds','edge_clouds']}
traces=[];current=['']
def trace(mod,args,kwargs):
 past=kwargs.get('past_key_values');n=past.get_seq_length() if past is not None else 0
 if len([r for r in traces if r['mode']==current[0]])<4:
  traces.append({'mode':current[0],'mask_len':int(kwargs['attention_mask'].shape[-1]),'embedding_len':int(kwargs['inputs_embeds'].shape[1]),'past_len':int(n)})
hook=model.model.register_forward_pre_hook(trace,with_kwargs=True)
results={}
def run(mode,cache):
 current[0]=mode
 with torch.inference_mode():p=model.generate(input_ids=prompt,attention_mask=torch.ones_like(prompt),**geometry,max_new_tokens=128,do_sample=False,num_beams=1,use_cache=cache,pad_token_id=tok.pad_token_id)
 ids=p[0,prompt.shape[1]:].tolist();div=next((i for i,(g,x) in enumerate(zip(gt,ids)) if g!=x),None)
 results[mode]={'first_divergence_token0':div,'ids':ids,'text':tok.decode(ids),'prefix_match_n':len(ids) if div is None else div}
 print(mode,results[mode]['first_divergence_token0'],results[mode]['text'][:80],flush=True)
run('baseline_cached',True)
run('no_cache',False)
original=model._update_model_kwargs_for_generation
def corrected(self,outputs,kwargs,*args,**kw):
 result=original(outputs,kwargs,*args,**kw)
 past=result.get('past_key_values');mask=result.get('attention_mask')
 if past is not None and mask is not None:
  want=past.get_seq_length()+1
  if want>mask.shape[-1]:
   assert bool((mask==1).all()),'Only unpadded single-case inference is supported'
   result['attention_mask']=torch.ones((mask.shape[0],want),dtype=mask.dtype,device=mask.device)
 return result
model._update_model_kwargs_for_generation=types.MethodType(corrected,model)
run('geometry_cache_mask_aligned',True)
hook.remove();save(DEBUG/'cache_ablation_block2.json',{'prompt_length':start,'results':results,'traces':traces,'gt_first96_ids':gt[:96],'change':'instance-local generation attention_mask length follows multimodal KV cache length; no token, CAD target, or stop rule changes'})
