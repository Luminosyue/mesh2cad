import os,sys,json,copy,hashlib,ast,subprocess,time,gzip,csv
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_tank_allparts_exact_overfit_v1'
sys.path[:0]=[str(ROOT/'SpatialLM'),str(ROOT/'scripts'),str(ROOT),str(EXP/'launch')]
os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_TOKEN_REGISTRY=str(EXP/'data/curve_registry.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',DISABLE_VERSION_CHECK='1',HF_DATASETS_CACHE=str(EXP/'cache'))
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector._DATASET_BY_PACK_DIR['XPart']='xpart';curve_token_injector.install()
import numpy as np,torch
from transformers import set_seed,AutoTokenizer
from spatiallm_curve_token_v1.decode_curve100 import _load_m2_checkpoint,_load_sepedge,set_deterministic_serialization
from separate_edge_tokens_v1.common import make_plugin
from cq54_protocol import prompt_for,END_MARKER

def save(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.tmp');temp.write_text(json.dumps(obj,indent=2,ensure_ascii=False));temp.replace(p)
def label_hash(ids):return hashlib.sha256(np.asarray(ids,dtype='<i8').tobytes()).hexdigest()
def gpu_batch(batch):return {k:v.cuda() if torch.is_tensor(v) else v for k,v in batch.items()}
def load(ckpt):
 set_seed(42);model,tok=_load_m2_checkpoint(Path(ckpt),'cuda',torch.bfloat16);model.eval();set_deterministic_serialization(model.point_backbone);return model,tok

def prepare():
 import yaml
 from spatiallm.tuner.hparams import get_train_args
 from spatiallm.tuner.framework.loader import load_tokenizer
 from spatiallm.tuner.data import get_dataset,get_template_and_fix_tokenizer,register_spatiallm_templates,SFTDataCollatorWith4DAttentionMask
 cfg=yaml.safe_load((EXP/'configs/train.yaml').read_text());ma,da,ta,fa,ga=get_train_args(cfg);tm=load_tokenizer(ma);tok=tm['tokenizer']
 register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=da.do_augmentation,random_rotation=da.random_rotation)
 template=get_template_and_fix_tokenizer(tok,da);ds=get_dataset(ma,da,ta)['train_dataset']
 col=SFTDataCollatorWith4DAttentionMask(template=template,model=None,pad_to_multiple_of=8,label_pad_token_id=-100,compute_dtype=torch.bfloat16,**tm)
 raw=json.loads((EXP/'data/train.json').read_text());batches=[];lookup={};rows=[]
 for i in range(len(ds)):
  set_seed(42);batch=col([copy.deepcopy(ds[i])]);labels=batch['labels'][0];active=labels[labels!=-100].tolist();key=label_hash(active);assert key not in lookup
  lookup[key]={'id':raw[i]['id'],'part':raw[i]['sample_id'].split('__')[-1],'block':int(raw[i]['id'].split('block')[-1])+1};batches.append(batch)
  assert active[-1]==tok.eos_token_id
  rows.append(dict(lookup[key],token_count=len(active),eos_label=active[-1],hash=key))
 torch.save(batches,EXP/'data/collated_batches.pt');save(EXP/'data/label_lookup.json',lookup);save(EXP/'data/block_inventory.json',rows)
 save(EXP/'audits/tokenizer.json',{k:getattr(tok,k) for k in ['eos_token','eos_token_id','pad_token','pad_token_id','bos_token','bos_token_id']})
 print('PREPARED',len(rows),'blocks',sum(r['token_count'] for r in rows),'supervised tokens',flush=True)

def teacher(model,tok,batches,out):
 import spatiallm.model.spatiallm_llama as lm
 original=lm._chunked_lm_loss;allrows=[]
 for bi,batch in enumerate(batches):
  records=[]
  def capture(head,hidden,labels,*args,**kw):
   positions=(labels[0,1:]!=-100).nonzero().flatten()+1;targets=labels[0,positions]
   for offset in range(0,len(positions),64):
    pp=positions[offset:offset+64];gt=targets[offset:offset+64];logits=head(hidden[0,pp-1]).float();lp=logits.log_softmax(-1);topv,topi=logits.topk(2,-1);top1=logits.argmax(-1)
    gtl=logits.gather(1,gt[:,None]).squeeze(1);gtp=lp.gather(1,gt[:,None]).squeeze(1);rival_i=torch.where(topi[:,0]==gt,topi[:,1],topi[:,0]);rival_v=torch.where(topi[:,0]==gt,topv[:,1],topv[:,0]);margin=gtl-rival_v
    arrays=[x.detach().cpu().tolist() for x in [gt,top1,rival_i,gtl,rival_v,margin,gtp.exp(),lp.gather(1,top1[:,None]).squeeze(1).exp(),-gtp,pp]]
    for j,values in enumerate(zip(*arrays)):
     g,p,r,gl,rl,m,gp,pb,nll,pos=values
     records.append({'block':bi+1,'token_in_block':offset+j+1,'gt_id':g,'gt_token':tok.decode([g],skip_special_tokens=False),'top1_id':p,'top1_token':tok.decode([p],skip_special_tokens=False),'second_best_id':r,'second_best_token':tok.decode([r],skip_special_tokens=False),'GT_LOGIT':gl,'SECOND_BEST_LOGIT':rl,'TOKEN_MARGIN':m,'GT_TOKEN_PROB':gp,'TOP1_PROB':pb,'NLL':nll,'CORRECT':g==p,'EOS':g==tok.eos_token_id,'expanded_position0':pos})
   return hidden.new_tensor(sum(r['NLL'] for r in records)/len(records))
  lm._chunked_lm_loss=capture
  try:
   with torch.inference_mode():model(**gpu_batch(batch),use_cache=False)
  finally:lm._chunked_lm_loss=original
  allrows+=records
 eos=[r for r in allrows if r['EOS']];margins=np.array([r['TOKEN_MARGIN'] for r in allrows]);worst=min(allrows,key=lambda r:r['TOKEN_MARGIN']);first=next((r for r in allrows if not r['CORRECT']),None)
 result={'TOKEN_ACC':sum(r['CORRECT'] for r in allrows)/len(allrows),'TOKEN_N':len(allrows),'EOS_ACC':sum(r['CORRECT'] for r in eos)/len(eos),'EOS_N':len(eos),'GT_SEQUENCE_NLL':sum(r['NLL'] for r in allrows),'MEAN_NLL':sum(r['NLL'] for r in allrows)/len(allrows),'FIRST_WRONG_TOKEN':first,'GT_TOKEN_PROB_AT_FIRST_ERROR':first['GT_TOKEN_PROB'] if first else None,'TOP1_PROB_AT_FIRST_ERROR':first['TOP1_PROB'] if first else None,'MIN_TOKEN_MARGIN':float(margins.min()),'P1_TOKEN_MARGIN':float(np.percentile(margins,1)),'P5_TOKEN_MARGIN':float(np.percentile(margins,5)),'MEDIAN_TOKEN_MARGIN':float(np.median(margins)),'MIN_MARGIN_TOKEN':worst,'MARGIN_DEFINITION':'GT_LOGIT minus strongest non-GT competitor; SECOND_BEST means alternative to GT, equals global runner-up when GT is top-1'}
 save(out/'teacher_forced.json',result)
 with gzip.open(out/'teacher_tokens.jsonl.gz','wt',encoding='utf-8') as f:
  for r in allrows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 return result,allrows

def decode(model,tok,part,out):
 plugin=make_plugin(separate_edge=True);target=Path(part['folder']);surface,edge=_load_sepedge(plugin,target/'surface_points.npy');prefix='';blocks=[];traces=[];ended=False;eos=model.generation_config.eos_token_id;eos=eos if isinstance(eos,list) else [eos];started=time.time()
 # A block-boundary resume uses only this model's saved predictions, never GT.
 if (out/'predicted_tokens.json').exists():
  traces=json.loads((out/'predicted_tokens.json').read_text());assert len(traces)<=64
  assert all(r['block']==i+1 for i,r in enumerate(traces))
  blocks=[tok.decode(r['token_ids'],skip_special_tokens=True).rstrip() for r in traces]
  prefix=''.join(b+'\n' for b in blocks);ended=bool(blocks) and END_MARKER in blocks[-1]
  if traces:
   bi=len(traces)-1;canary_prefix=''.join(b+'\n' for b in blocks[:bi])
   msg=plugin.process_messages([{'role':'user','content':prompt_for(tok,canary_prefix,bi)}],[{}]);ids=tok.apply_chat_template(msg,add_generation_prompt=True,return_tensors='pt').cuda()
   with torch.inference_mode():check=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surface.cuda(),edge_clouds=edge.cuda(),max_new_tokens=1280,do_sample=False,num_beams=1,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id)
   assert check[0,ids.shape[1]:].tolist()==traces[-1]['token_ids'],'Resume canary token mismatch; abort instead of splicing incompatible generations'
   resume={'resumed_after_block':len(traces),'last_block_independent_replay_exact':True,'prefix_source':'saved raw model prediction tokens only','timestamp':time.time()}
   with (out/'resume_audit.jsonl').open('a') as f:f.write(json.dumps(resume)+'\n')
   print('RESUME_VERIFIED',out.parent.name,part['part'],len(traces),flush=True)
 for bi in range(len(traces),64):
  if ended or (blocks and not blocks[-1]):break
  msg=plugin.process_messages([{'role':'user','content':prompt_for(tok,prefix,bi)}],[{}]);ids=tok.apply_chat_template(msg,add_generation_prompt=True,return_tensors='pt').cuda()
  with torch.inference_mode():pred=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surface.cuda(),edge_clouds=edge.cuda(),max_new_tokens=1280,do_sample=False,num_beams=1,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id)
  tokens=pred[0,ids.shape[1]:].tolist();text=tok.decode(tokens,skip_special_tokens=True).rstrip();blocks.append(text);natural=bool(tokens) and tokens[-1] in eos
  traces.append({'block':bi+1,'token_ids':tokens,'TOKEN_EOS_TERMINATED':natural,'TOKEN_CAP_HIT':len(tokens)>=1280 and not natural,'CAD_COMPLETE_PREDICTED':END_MARKER in text});prefix+=text+'\n'
  save(out/'predicted_blocks.json',blocks);save(out/'predicted_tokens.json',traces);(out/'prediction.py').write_text(prefix)
  print('BLOCK',out.parent.name,part['part'],bi+1,'EOS',natural,'COMPLETE',END_MARKER in text,flush=True)
  if END_MARKER in text:ended=True;break
  if not text:break
 # No GT code, length, or block count is used above; evaluation starts below.
 raw=json.loads((EXP/'data/train.json').read_text());gt=[r['conversations'][1]['value'] for r in raw if r['sample_id']=='airplane__'+part['part']];gtids=[tok.encode(x,add_special_tokens=False)+[tok.eos_token_id] for x in gt];predids=[r['token_ids'] for r in traces]
 save(out/'gt_blocks.json',gt);save(out/'gt_tokens.json',gtids);gflat=sum(gtids,[]);pflat=sum(predids,[])
 fd=next((i for i,(a,b) in enumerate(zip(gflat,pflat)) if a!=b),None)
 if fd is None and len(gflat)!=len(pflat):fd=min(len(gflat),len(pflat))
 fb=next((i for i in range(max(len(gtids),len(predids))) if i>=len(gtids) or i>=len(predids) or gtids[i]!=predids[i]),None);ft=None
 if fb is not None and fb<len(gtids) and fb<len(predids):ft=next((i for i,(a,b) in enumerate(zip(gtids[fb],predids[fb])) if a!=b),min(len(gtids[fb]),len(predids[fb])))
 bm=[i<len(blocks) and g==blocks[i] for i,g in enumerate(gt)];seqexact=gflat==pflat
 try:ast.parse(prefix);parse=True;err=None
 except SyntaxError as e:parse=False;err=str(e)
 execution=False;step=False
 if parse:
  try:
   run=subprocess.run(['/usr/bin/python3',str(EXP/'launch/cq54_evaluate.py'),str(out),str(target)],capture_output=True,text=True,timeout=240);(out/'execution.log').write_text(run.stdout+run.stderr);execution=run.returncode==0;step=(out/'prediction.step').exists()
  except subprocess.TimeoutExpired:(out/'execution.log').write_text('240-second CAD execution timeout')
 result={'PART_ID':part['part'],'GT_BLOCK_COUNT':len(gt),'PRED_BLOCK_COUNT':len(blocks),'GT_TOKEN_COUNT':len(gflat),'PRED_TOKEN_COUNT':len(pflat),'FIRST_DIVERGENCE_TOKEN':fd+1 if fd is not None else None,'FIRST_DIVERGENCE_BLOCK':fb+1 if fb is not None else None,'FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN':ft+1 if ft is not None else None,'BLOCK_COUNT_EXACT':len(gt)==len(blocks),'BLOCK_EXACT_MATCH':len(gt)==len(blocks) and all(bm),'BLOCK_EXACT_MATCH_N':sum(bm),'SEQUENCE_EXACT_MATCH':seqexact,'EOS_TERMINATED':ended and traces[-1]['TOKEN_EOS_TERMINATED'],'CAD_COMPLETE_PREDICTED':ended,'SAFETY_CAP_HIT':len(blocks)==64 and not ended,'CAD_PARSE_PASS':parse,'CAD_EXECUTION_PASS':execution,'STEP_EXPORT_PASS':step,'PARSE_ERROR':err,'DECODE_SECONDS':time.time()-started,'indexing':'1-based; full token sequence includes EOS at each block boundary'}
 if not seqexact:
  text=[f"FIRST_DIVERGENCE_TOKEN={result['FIRST_DIVERGENCE_TOKEN']}",f"FIRST_DIVERGENCE_BLOCK={result['FIRST_DIVERGENCE_BLOCK']}",f"FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN={result['FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN']}",'']
  if fb is not None:
   g=gtids[fb] if fb<len(gtids) else [];p=predids[fb] if fb<len(predids) else [];i=ft or 0
   text+=['GT CONTEXT ±30 tokens:',tok.decode(g[max(0,i-30):i+31],skip_special_tokens=False),'PRED CONTEXT ±30 tokens:',tok.decode(p[max(0,i-30):i+31],skip_special_tokens=False),'']
   for bi in sorted(set([max(0,fb-1),fb,min(fb+1,max(len(gt),len(blocks))-1)])):
    text += ['BLOCK '+str(bi+1),'GT:',gt[bi] if bi<len(gt) else '(GT ended)','PRED:',blocks[bi] if bi<len(blocks) else '(not generated)','MATCH='+str(bi<len(gt) and bi<len(blocks) and gt[bi]==blocks[bi]),'']
  (out/f"failure_diff_{part['part']}_{out.parent.name}.txt").write_text('\n'.join(text))
 return result

def evaluate(ckpt,partname):
 part=next(p for p in json.loads((EXP/'data/parts.json').read_text()) if p['part']==partname);out=EXP/'evaluations'/Path(ckpt).name/partname;out.mkdir(parents=True,exist_ok=True)
 assert not (out/'result.json').exists(),'Completed evidence must not be overwritten'
 model,tok=load(ckpt);batches=torch.load(EXP/'data/collated_batches.pt',weights_only=False);inv=json.loads((EXP/'data/block_inventory.json').read_text());batches=[b for b,r in zip(batches,inv) if r['part']==partname]
 tf,tokens=teacher(model,tok,batches,out);print('TF',Path(ckpt).name,partname,tf['TOKEN_ACC'],tf['MIN_TOKEN_MARGIN'],flush=True)
 result=decode(model,tok,part,out);result.update(TOKEN_ACC_TEACHER_FORCED=tf['TOKEN_ACC'],EOS_ACC=tf['EOS_ACC'],GT_SEQUENCE_NLL=tf['GT_SEQUENCE_NLL'],MEAN_NLL=tf['MEAN_NLL'],MIN_TOKEN_MARGIN=tf['MIN_TOKEN_MARGIN'],P1_TOKEN_MARGIN=tf['P1_TOKEN_MARGIN'],P5_TOKEN_MARGIN=tf['P5_TOKEN_MARGIN'],MEDIAN_TOKEN_MARGIN=tf['MEDIAN_TOKEN_MARGIN'])
 fb=result['FIRST_DIVERGENCE_BLOCK'];ft=result['FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN'];result['DIVERGENCE_TEACHER_CONTEXT']=next((r for r in tokens if r['block']==fb and r['token_in_block']==ft),None)
 result['PART_GATE_PASS']=all(result[k] for k in ['SEQUENCE_EXACT_MATCH','BLOCK_COUNT_EXACT','BLOCK_EXACT_MATCH','EOS_TERMINATED','CAD_PARSE_PASS','CAD_EXECUTION_PASS','STEP_EXPORT_PASS']) and not result['SAFETY_CAP_HIT'] and result['TOKEN_ACC_TEACHER_FORCED']>=.999 and result['EOS_ACC']==1
 save(out/'result.json',result);print('RESULT',json.dumps(result),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='evaluate':evaluate(sys.argv[2],sys.argv[3])
