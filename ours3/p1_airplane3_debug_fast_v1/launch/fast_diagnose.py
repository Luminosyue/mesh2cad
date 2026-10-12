from pathlib import Path
import sys,json,time,gzip,types
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1';sys.path.insert(0,str(E/'launch'))
from a2_runtime import *
from a2_runtime import _load_sepedge
import spatiallm.model.spatiallm_llama as lm
from transformers import StoppingCriteria,StoppingCriteriaList
partname=sys.argv[1];started=time.time();out=E/'diagnostics'/partname;out.mkdir(exist_ok=True)
model,tok=load(OLD/'runs/quick/checkpoint-2000');plugin=make_plugin(separate_edge=True)
part=next(p for p in json.loads((E/'data/parts.json').read_text()) if p['part']==partname)
surface,edge=_load_sepedge(plugin,Path(part['folder'])/'surface_points.npy')
surface=surface.cuda();edge=edge.cuda()
batches=torch.load(E/'data/collated_batches.pt',weights_only=False);inv=json.loads((E/'data/block_inventory.json').read_text())
selected=[b for b,r in zip(batches,inv) if r['part']==partname]
original_surface,original_edge=surface,edge
surface=surface.to(selected[0]['point_clouds'].dtype);edge=edge.to(selected[0]['edge_clouds'].dtype)
save(out/'geometry_dtype_mismatch.json',{'training_surface_dtype':str(surface.dtype),'old_inference_surface_dtype':str(original_surface.dtype),'cast_to_training_dtype_equals':torch.equal(surface.cpu(),selected[0]['point_clouds']),'surface_max_abs_difference':float((original_surface-surface.float()).abs().max()),'grid_entries_changed':int((original_surface[...,:3].int()!=surface[...,:3].int()).sum()),'grid_entries_total':original_surface[...,:3].numel(),'training_edge_dtype':str(edge.dtype),'old_inference_edge_dtype':str(original_edge.dtype),'fix':'cast both inference geometry inputs to the existing training collator dtype before the point backbone; source assets unchanged'})
raw=[r for r in json.loads((E/'data/train.json').read_text()) if r['sample_id']=='airplane__'+partname]
checks=[];gtblocks=[];prompts=[]
for bi,(batch,row) in enumerate(zip(selected,raw)):
 ids=batch['input_ids'][0];labels=batch['labels'][0];positions=(labels!=-100).nonzero().flatten();gt=tok.encode(row['conversations'][1]['value'],add_special_tokens=False)+[tok.eos_token_id]
 prefix=''.join(b+'\n' for b in gtblocks)
 msg=plugin.process_messages([{'role':'user','content':prompt_for(tok,prefix,bi)}],[{}]);prompt=tok.apply_chat_template(msg,add_generation_prompt=True,return_tensors='pt').cuda();prompts.append(prompt)
 check={'block':bi+1,'all_target_labels_including_EOS':labels[positions].tolist()==gt,'input_target_same':ids[positions].tolist()==gt,'prompt_ids_equal':ids[:positions[0]].tolist()==prompt[0].tolist(),'target_contiguous':positions.tolist()==list(range(int(positions[0]),int(positions[-1])+1)),'raw_length':len(ids),'active_length':int(batch['attention_mask'].sum()),'target_tokens':len(gt),'END_in_target':END_MARKER in row['conversations'][1]['value'],'surface_equal':torch.equal(batch['point_clouds'].cpu(),surface.cpu()),'curve_equal':torch.equal(batch['edge_clouds'].cpu(),edge.cpu()),'padding_masked':bool((labels[batch['attention_mask'][0]==0]==-100).all())}
 checks.append(check);gtblocks.append(row['conversations'][1]['value'])
save(out/'data_prompt_audit.json',checks)
assert all(all(r[k] for k in ['all_target_labels_including_EOS','input_target_same','prompt_ids_equal','target_contiguous','surface_equal','curve_equal','padding_masked']) for r in checks),checks
save(out/'generation_config.json',{'generation_config':model.generation_config.to_dict(),'tokenizer_EOS':tok.eos_token_id,'tokenizer_PAD':tok.pad_token_id,'END_ids':tok.encode(END_MARKER,add_special_tokens=False),'context_limit':model.config.max_position_embeddings,'attention_implementation':model.config._attn_implementation,'block_cap':64,'token_cap':1280,'stopping':'model generated CAD_COMPLETE and natural EOS; cap is failure'})
queryblocks=sorted(set([0,len(selected)-1]));comparisons=[];vectors={};decoder_meta=[]
def decoder_hook(mod,args,kw):
 if len(decoder_meta)<3:
  decoder_meta.append({k:(list(v.shape) if torch.is_tensor(v) else str(v)[:100]) for k,v in kw.items() if k!='past_key_values'})
hook=model.model.register_forward_pre_hook(decoder_hook,with_kwargs=True)
for bi in queryblocks:
 batch=selected[bi];gt=batch['labels'][0];gt=gt[gt!=-100].tolist();queries=set(range(max(0,len(gt)-8),len(gt)))
 if bi==0 and partname in ['PART_001','PART_005']:queries.update(range((207 if partname=='PART_001' else 981)-2,(207 if partname=='PART_001' else 981)+1))
 full={};old_loss=lm._chunked_lm_loss
 def capture(head,h,labels,*a,**kw):
  pp=(labels[0,1:]!=-100).nonzero().flatten()+1
  for offset in range(0,len(pp),64):
   logits=head(h[0,pp[offset:offset+64]-1]).float()
   for j in range(len(logits)):
    if offset+j in queries:full[offset+j]=logits[j].detach().cpu()
  return h.new_zeros(())
 lm._chunked_lm_loss=capture
 with torch.inference_mode():model(**gpu_batch(batch),use_cache=False)
 lm._chunked_lm_loss=old_loss
 ids=prompts[bi];past=None;mask=torch.ones_like(ids)
 with torch.inference_mode():
  for j in range(len(gt)):
   kw=model.prepare_inputs_for_generation(ids,past_key_values=past,attention_mask=mask,point_clouds=surface,edge_clouds=edge,use_cache=True)
   output=model(**kw,num_logits_to_keep=1);past=output.past_key_values
   if j in queries:
    cached=output.logits[0,-1].float().cpu()
    no=model(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surface,edge_clouds=edge,use_cache=False,num_logits_to_keep=1).logits[0,-1].float().cpu()
    old=model(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=original_surface,edge_clouds=original_edge,use_cache=False,num_logits_to_keep=1).logits[0,-1].float().cpu()
    vals={'full_GT_forward':full[j],'prefix_no_cache':no,'prefix_incremental_cache':cached,'old_fp32_geometry_prefix':old}
    entry={'block':bi+1,'token_in_block':j+1,'gt_id':gt[j],'gt_token':tok.decode([gt[j]]),'prefix_token_count':ids.shape[1],'cache_length':past.get_seq_length() if hasattr(past,'get_seq_length') else past[0][0].shape[-2],'raw_mask_length':mask.shape[1]}
    for name,v in vals.items():
     rival=v.clone();rival[gt[j]]=-torch.inf;entry[name]={'argmax_id':int(v.argmax()),'argmax_token':tok.decode([int(v.argmax())]),'gt_logit':float(v[gt[j]]),'margin':float(v[gt[j]]-rival.max())};vectors[f'{bi+1}_{j+1}_{name}']=v
    entry['max_abs_full_vs_no_cache']=float((full[j]-no).abs().max());entry['max_abs_cache_vs_no_cache']=float((cached-no).abs().max());entry['argmax_all_equal']=len({int(vals[k].argmax()) for k in ['full_GT_forward','prefix_no_cache','prefix_incremental_cache']})==1
    entry['max_abs_old_geometry_vs_aligned']=float((old-no).abs().max())
    comparisons.append(entry)
   ids=torch.cat([ids,ids.new_tensor([[gt[j]]])],dim=1);mask=torch.ones_like(ids)
 save(out/'same_prefix_comparisons.json',comparisons);torch.save(vectors,out/'logit_vectors.pt')
 print('PREFIX_DONE',partname,bi+1,'maxdiff',max(r['max_abs_cache_vs_no_cache'] for r in comparisons),'argmax_same',all(r['argmax_all_equal'] for r in comparisons),flush=True)
hook.remove();save(out/'decoder_metadata.json',decoder_meta)
class BudgetStop(StoppingCriteria):
 def __init__(self,seconds):self.deadline=time.time()+seconds
 def __call__(self,input_ids,scores,**kw):return time.time()>self.deadline
generations=[]
# These fixed-length smoke probes are diagnostics, never full-program Gate results.
for cache in [True,False]:
 set_seed(42);ids=prompts[0];deadline=BudgetStop(180);captured=[]
 with torch.inference_mode():
  pred=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surface,edge_clouds=edge,do_sample=False,num_beams=1,use_cache=cache,max_new_tokens=1280,stopping_criteria=StoppingCriteriaList([deadline]),pad_token_id=tok.pad_token_id)
 tokens=pred[0,ids.shape[1]:].tolist();generations.append({'use_cache':cache,'tokens':tokens,'natural_EOS':bool(tokens) and tokens[-1]==tok.eos_token_id,'wall_budget_hit':time.time()>deadline.deadline,'scope':'first block only; no GT prefix; not a full-program gate'})
 save(out/'cache_generation_probes.json',generations);print('GEN_PROBE',partname,cache,len(tokens),generations[-1]['wall_budget_hit'],flush=True)
a,b=[r['tokens'] for r in generations];first=next((i+1 for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)
save(out/'summary.json',{'part':partname,'same_prefix_argmax_all_equal':all(r['argmax_all_equal'] for r in comparisons),'max_abs_logit_diff':max(r['max_abs_cache_vs_no_cache'] for r in comparisons),'generation_first_divergence':first,'generation_common_prefix_equal':first is None,'generation_lengths':[len(a),len(b)],'elapsed_seconds':time.time()-started,'data_prompt_audit_pass':True,'diagnostic_GT_prefix_never_used_for_GATE':True})
print('DIAG_COMPLETE',partname,flush=True)
