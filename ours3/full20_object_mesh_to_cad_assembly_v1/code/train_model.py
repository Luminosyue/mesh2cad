"""Object-specialist full-sequence training; no grammar or tokenizer changes."""
import os,sys,json,time,copy,hashlib,shutil,traceback,random
from pathlib import Path
os.environ['CAD_USE_EDGE_SCORE']='0'
os.environ['CAD_USE_SEPARATE_EDGE_TOKENS']='0'
os.environ['DISABLE_VERSION_CHECK']='1'
for k in ['CURVE_TOKEN_REGISTRY','CAD_SECOND_STREAM']:os.environ.pop(k,None)
import numpy as np,torch
from torch.utils.checkpoint import checkpoint as activation_checkpoint
from transformers import set_seed
R=Path('/data/home/cuiyuehan/project/mesh2cad'); E=R/'ours3/full20_object_mesh_to_cad_assembly_v1/model_v1'
name=sys.argv[1];D=E/'data'/name;OUT=E/'runs'/name;OUT.mkdir(parents=True,exist_ok=True)
STORE=Path(json.loads((E/'reports/EXPERIMENT_CONTRACT.json').read_text())['checkpoint_storage'])/name
sys.path[:0]=[str(R/'scripts'),str(R/'SpatialLM')]
from spatiallm.tuner.hparams.parser import read_args
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer,load_model
from spatiallm.tuner.data import register_spatiallm_templates,get_template_and_fix_tokenizer,get_dataset,SFTDataCollatorWith4DAttentionMask,IGNORE_INDEX
import spatiallm.model.spatiallm_llama as llama
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,indent=2)+'\n');q.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(x):
 print(json.dumps(x),flush=True)
 with (OUT/'events.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
def disk_gate():
 assert shutil.disk_usage('/data').free>15e9,'DATA_DISK_SAFETY_GATE'
 assert shutil.disk_usage(STORE.parent).free>30e9,'CHECKPOINT_DISK_SAFETY_GATE'
def loss_checkpointed(head,hidden_states,labels,chunk_size=128,ignore_index=IGNORE_INDEX):
 h=hidden_states[:,:-1,:]; y=labels[:,1:];valid=int(y.ne(ignore_index).sum());total=h.new_zeros(())
 def ce(a,b):return torch.nn.functional.cross_entropy(head(a).reshape(-1,head.out_features).float(),b.reshape(-1),ignore_index=ignore_index,reduction='sum')
 for start in range(0,h.shape[1],chunk_size):
  hh=h[:,start:start+chunk_size];yy=y[:,start:start+chunk_size]
  if not yy.ne(ignore_index).any():continue
  total=total+(activation_checkpoint(ce,hh,yy,use_reentrant=False) if torch.is_grad_enabled() else ce(hh,yy))
 return total/max(valid,1)
def validate_loss():
 torch.manual_seed(7);head=torch.nn.Linear(9,17,bias=False);h=torch.randn(1,21,9,requires_grad=True);y=torch.randint(0,17,(1,21));y[:,:4]=-100
 ref=torch.nn.functional.cross_entropy(head(h[:,:-1]).reshape(-1,17),y[:,1:].reshape(-1),ignore_index=-100)
 g=torch.autograd.grad(ref,[h,head.weight],retain_graph=True);got=loss_checkpointed(head,h,y,chunk_size=5);g2=torch.autograd.grad(got,[h,head.weight]);assert torch.allclose(ref,got,atol=1e-6) and all(torch.allclose(a,b,atol=1e-6) for a,b in zip(g,g2))
 return dict(loss=float(got),max_gradient_error=max(float((a-b).abs().max()) for a,b in zip(g,g2)))
def main():
 disk_gate();dump(OUT/'LOSS_IMPLEMENTATION_CHECK.json',validate_loss());set_seed(42)
 sys.argv=['train',str(D/'train.yaml')];ma,da,ta,fa,ga=get_train_args(read_args())
 tm=load_tokenizer(ma);tok=tm['tokenizer'];register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=False,random_rotation=False)
 template=get_template_and_fix_tokenizer(tok,da);ds=get_dataset(ma,da,ta);split=ds[next(k for k in ds if 'train' in str(k).lower())]
 raw=json.loads((D/'train.json').read_text());prov=json.loads((D/'provenance.json').read_text());assert len(split)==len(raw)
 assert all(not (name=='tank' and x['part']=='PART_029') for x in prov)
 model=load_model(tok,da,ma,fa,True);model.to('cuda');model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.config.use_cache=False
 if hasattr(model,'enable_input_require_grads'):model.enable_input_require_grads()
 llama._chunked_lm_loss=loss_checkpointed
 coll=SFTDataCollatorWith4DAttentionMask(template=template,model=model,pad_to_multiple_of=None,label_pad_token_id=IGNORE_INDEX,block_diag_attn=ma.block_diag_attn,attn_implementation=getattr(model.config,'_attn_implementation',None),compute_dtype=ma.compute_dtype,**tm)
 batches=[];audit=[]
 for i,row in enumerate(split):
  b=coll([copy.deepcopy(dict(row))]); assert not b.get('edge_clouds') is not None,'Unexpected curve/edge input'
  y=b['labels'][0];valid=y.ne(IGNORE_INDEX);ids=y[valid].tolist();decoded=tok.decode(ids,skip_special_tokens=True)
  assert decoded.strip()==raw[i]['conversations'][1]['value'].strip(),f'TARGET_TRUNCATION_OR_ORDER_MISMATCH {i}'
  assert b['input_ids'].shape[1]<da.cutoff_len and ids[-1] in [128001,128008,128009]
  assert sha(prov[i]['target_path'])==prov[i]['target_sha256'] and sha(prov[i]['point_cloud'])==prov[i]['point_sha256']
  batches.append(b);audit.append(dict(id=raw[i]['id'],supervised_tokens=len(ids),input_tokens=int(b['input_ids'].shape[1]),full_target_verified=True,curve_tokens_used=False))
 dump(OUT/'PREFLIGHT.json',dict(checkpoint=ma.model_name_or_path,object=name,parts=audit,trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad),dtype=str(next(model.parameters()).dtype),gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),gradient_checkpointing=model.is_gradient_checkpointing,chunked_ce='Recomputed CE with verified identical objective and gradient',context=da.cutoff_len,full_sequence=True,no_target_truncation=True))
 def batch(i):return {k:(v.to('cuda') if torch.is_tensor(v) else v) for k,v in batches[i].items()}
 def save(step,tag):
  disk_gate();p=STORE/f'checkpoint-{step}-{tag}';assert not p.exists(),f'Checkpoint exists {p}'
  model.save_pretrained(p,safe_serialization=True,max_shard_size='4GB');tok.save_pretrained(p)
  dump(p/'RUN_PROVENANCE.json',dict(object=name,step=step,warm_start=ma.model_name_or_path,dataset_sha256=sha(D/'train.json'),training_script_sha256=sha(__file__),representation='q14_COMPACT_IR_V3',full_sequence=True,optimizer='AdamW full language/projector training; point tower frozen',optimizer_state_saved=False))
  dump(OUT/'LATEST_CHECKPOINT.json',dict(path=str(p),step=step));emit(dict(event='checkpoint_saved',path=str(p),step=step));return p
 def tf_scan(step):
  model.eval();results=[]
  def tf_loss(head,hidden_states,labels,**kwargs):
   h=hidden_states[:,:-1];y=labels[:,1:];errors=0;sup=int(y.ne(-100).sum())
   for st in range(0,h.shape[1],128):
    yy=y[:,st:st+128];pred=head(h[:,st:st+128]).argmax(-1);errors+=int((pred.ne(yy)&yy.ne(-100)).sum())
   tf_loss.last=(errors,sup);return h.new_zeros(())
  llama._chunked_lm_loss=tf_loss
  with torch.no_grad():
   for i in range(len(batches)):
    model(**batch(i));err,n=tf_loss.last;results.append(dict(id=raw[i]['id'],errors=err,supervised_tokens=n))
  llama._chunked_lm_loss=loss_checkpointed;model.train();dump(OUT/f'TF_{step}.json',results);emit(dict(event='tf_scan',step=step,errors=sum(x['errors'] for x in results),zero_parts=sum(x['errors']==0 for x in results)));return all(x['errors']==0 for x in results)
 def free_generate(step,ck):
  model.eval();model.gradient_checkpointing_disable();model.config.use_cache=True;folder=OUT/f'free_{step}';folder.mkdir(exist_ok=True);results=[]
  for i in range(len(batches)):
   b=batch(i);valid=b['labels'][0].ne(-100).nonzero().flatten();start=int(valid[0]);gold=b['labels'][0,valid].tolist()
   # An empty assistant target: only the user prompt and input mesh cloud remain.
   inp={k:v for k,v in b.items() if k not in ['labels','position_ids']}
   for k in ['input_ids','attention_mask','token_type_ids']:
    if k in inp:inp[k]=inp[k][:,:start]
   assert inp['input_ids'].shape[1]==start and 'labels' not in inp
   t=time.time();budget=da.cutoff_len-start-512
   with torch.inference_mode():g=model.generate(**inp,max_new_tokens=budget,do_sample=False,num_beams=1,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id,eos_token_id=[128001,128008,128009])
   ids=g[0,start:].tolist();eos=bool(ids and ids[-1] in [128001,128008,128009]);text=tok.decode(ids[:-1] if eos else ids,skip_special_tokens=False)
   (folder/(prov[i]['part']+'.v3')).write_text(text);dump(folder/(prov[i]['part']+'_tokens.json'),ids)
   result=dict(id=raw[i]['id'],object=name,part=prov[i]['part'],checkpoint=str(ck),step=step,GT_PREFIX_TOKEN_N=0,EMPTY_TARGET=True,GREEDY=True,GENERATION_BUDGET=budget,GT_TOKEN_N=len(gold),GENERATED_TOKEN_N=len(ids),FREE_TOKEN_EXACT=ids==gold,NATURAL_EOS=eos,elapsed_seconds=time.time()-t,target_label_dir=prov[i]['label_dir'],generated_ir=str(folder/(prov[i]['part']+'.v3')))
   results.append(result);dump(folder/(prov[i]['part']+'_result.json'),result);emit(dict(event='free_generation',**result))
  summary=dict(object=name,checkpoint=str(ck),rows=results,free_exact_n=sum(r['FREE_TOKEN_EXACT'] for r in results),natural_eos_n=sum(r['NATURAL_EOS'] for r in results))
  dump(folder/'SUMMARY.json',summary);model.config.use_cache=False;model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.train();return all(r['FREE_TOKEN_EXACT'] and r['NATURAL_EOS'] for r in results)
 opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=5e-6)
 n=len(batches);counts=[0]*n;scans={min(160,max(40,n*8)),320,360,640};success=False
 # Exercise the longest full sequence first, to expose memory/context failures before a long run.
 order=sorted(range(n),key=lambda i:audit[i]['input_tokens'],reverse=True)
 for step in range(1,641):
  disk_gate();i=order[(step-1)%n];counts[i]+=1
  if step==321:
   for group in opt.param_groups:group['lr']=2e-6
  t=time.time();model.train();b=batch(i);o=model(**b);loss=o.loss;assert torch.isfinite(loss);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step();opt.zero_grad(set_to_none=True)
  rec=dict(event='train_step',step=step,id=raw[i]['id'],loss=float(loss.detach().cpu()),input_len=int(b['input_ids'].shape[1]),seconds=time.time()-t,lr=opt.param_groups[0]['lr'],gpu_peak_gb=torch.cuda.max_memory_allocated()/1e9)
  del o,loss,b;emit(rec);dump(OUT/'TRAIN_STATUS.json',dict(**rec,exposure_counts=counts,status='TRAINING'))
  if step==20:save(step,'initial')
  if step in scans:
   zero=tf_scan(step)
   if zero or step==640:
    ck=save(step,'free_eval');success=free_generate(step,ck)
    if success:break
 dump(OUT/'TRAIN_DONE.json',dict(object=name,step=step,free_exact_all_training_parts=success,full_object_claim=False if name=='tank' else success,canonical_cad_gate_pending=True,excluded_frozen_part='PART_029' if name=='tank' else None,checkpoint=str(ck),exposure_counts=counts))
 if not success:emit(dict(event='bounded_training_finished_without_full_free_exact',object=name))
if __name__=='__main__':
 try:main()
 except Exception:
  dump(OUT/'TRAIN_FAILED.json',dict(object=name,traceback=traceback.format_exc(),status='FAILED_NO_SUCCESS_CLAIM'));raise
