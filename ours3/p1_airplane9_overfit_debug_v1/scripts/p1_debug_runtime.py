import os,sys,json,copy,csv,hashlib,re,math
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OLD=ROOT/'ours3/p1_quick_overfit_airplane9_v1'
DEBUG=ROOT/'ours3/p1_airplane9_overfit_debug_v1'
CKPT=OLD/'runs/quick/checkpoint-2000'
sys.path[:0]=[str(ROOT/'SpatialLM'),str(ROOT/'scripts'),str(ROOT),str(OLD/'launch')]
os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_TOKEN_REGISTRY=str(OLD/'data/curve_registry.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',DISABLE_VERSION_CHECK='1',HF_DATASETS_CACHE=str(DEBUG/'cache'))
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector._DATASET_BY_PACK_DIR['XPart']='xpart';curve_token_injector.install()
import torch,numpy as np
from transformers import AutoTokenizer,set_seed
from spatiallm.tuner.hparams import get_train_args
from spatiallm.tuner.framework.loader import load_tokenizer
from spatiallm.tuner.data import get_dataset,get_template_and_fix_tokenizer,register_spatiallm_templates,SFTDataCollatorWith4DAttentionMask
from spatiallm_curve_token_v1.decode_curve100 import _load_m2_checkpoint,_load_sepedge,set_deterministic_serialization
from separate_edge_tokens_v1.common import make_plugin
from cq54_protocol import prompt_for,END_MARKER

def save(p,obj):
 p=Path(p);p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False))

def setup_data():
 import yaml
 cfg=yaml.safe_load((OLD/'configs/train.yaml').read_text());cfg['output_dir']=str(DEBUG/'unused_training_output');cfg['logging_dir']=str(DEBUG/'logs')
 ma,da,ta,fa,ga=get_train_args(cfg)
 tm=load_tokenizer(ma);tok=tm['tokenizer']
 register_spatiallm_templates(cutoff_len=da.cutoff_len,num_bins=da.num_bins,do_augmentation=da.do_augmentation,random_rotation=da.random_rotation)
 template=get_template_and_fix_tokenizer(tok,da)
 ds=get_dataset(ma,da,ta)['train_dataset']
 col=SFTDataCollatorWith4DAttentionMask(template=template,model=None,pad_to_multiple_of=8,label_pad_token_id=-100,compute_dtype=torch.bfloat16,**tm)
 return tok,template,ds,col

def load(ckpt=CKPT):
 set_seed(42)
 model,tok=_load_m2_checkpoint(Path(ckpt),'cuda',torch.bfloat16)
 model.eval();set_deterministic_serialization(model.point_backbone)
 return model,tok

def device_batch(batch):return {k:v.cuda() if torch.is_tensor(v) else v for k,v in batch.items()}

def teacher(model,tok,batches,outdir):
 import spatiallm.model.spatiallm_llama as mod
 outdir=Path(outdir);outdir.mkdir(exist_ok=True,parents=True)
 original=mod._chunked_lm_loss
 reports=[];all_tokens=[];EOS=tok.eos_token_id
 for bi,batch in enumerate(batches):
  raw_pos=(batch['labels'][0]!=-100).nonzero().flatten().tolist(); rows=[]
  def capture(head,hidden,labels,*args,**kwargs):
   pos=(labels[0,1:]!=-100).nonzero().flatten()+1
   targets=labels[0,pos]
   for offset in range(0,len(pos),64):
    pp=pos[offset:offset+64];yy=targets[offset:offset+64]
    logits=head(hidden[0,pp-1]).float();lp=logits.log_softmax(-1);pred=logits.argmax(-1)
    for j in range(len(pp)):
     n=offset+j;tid=int(yy[j]);pid=int(pred[j]);token=tok.decode([tid],skip_special_tokens=False)
     row={'block':bi+1,'target_index0':n,'raw_sequence_position0':raw_pos[n],'expanded_sequence_position0':int(pp[j]),'gt_id':tid,'gt_token':token,'pred_id':pid,'pred_token':tok.decode([pid],skip_special_tokens=False),'probability':float(lp[j,tid].exp()),'nll':float(-lp[j,tid]),'correct':tid==pid,'is_eos':tid==EOS,'is_control':tid==EOS or bool(re.search(r'[A-Za-z_#=()\[\]{},\n]',token))}
     if tid==EOS or n>=len(pos)-8:
      vals,inds=lp[j].topk(3);row['rank']=int((logits[j]>logits[j,tid]).sum())+1
      row['top3']=[{'id':int(t),'token':tok.decode([int(t)],skip_special_tokens=False),'probability':float(v.exp())} for v,t in zip(vals,inds)]
     rows.append(row)
   return torch.tensor(sum(r['nll'] for r in rows)/len(rows),device=hidden.device)
  mod._chunked_lm_loss=capture
  try:
   with torch.inference_mode():model(**device_batch(batch),use_cache=False)
  finally:mod._chunked_lm_loss=original
  eos=[r for r in rows if r['is_eos']];control=[r for r in rows if r['is_control']]
  reports.append({'block':bi+1,'tokens':len(rows),'token_acc':sum(r['correct'] for r in rows)/len(rows),'mean_nll':sum(r['nll'] for r in rows)/len(rows),'eos':eos,'first_error':next((r for r in rows if not r['correct']),None)})
  all_tokens+=rows
  print('TEACHER',bi+1,reports[-1]['token_acc'],reports[-1]['mean_nll'],flush=True)
 eos=[r for r in all_tokens if r['is_eos']];control=[r for r in all_tokens if r['is_control']]
 result={'token_acc':sum(r['correct'] for r in all_tokens)/len(all_tokens),'token_n':len(all_tokens),'structure_control_token_acc':sum(r['correct'] for r in control)/len(control),'control_definition':'token contains ASCII letter, syntax punctuation, newline, or EOS','eos_acc':sum(r['correct'] for r in eos)/len(eos),'sequence_nll':sum(r['nll'] for r in all_tokens),'mean_nll':sum(r['nll'] for r in all_tokens)/len(all_tokens),'first_error':next((r for r in all_tokens if not r['correct']),None),'blocks':reports,'gt_final_eos':eos[-1],'all_gt_tokens':all_tokens}
 save(outdir/'teacher_forced_case0.json',result)
 return result

def audit():
 tok,template,ds,col=setup_data();raw=json.loads((OLD/'data/train.json').read_text());parts=json.loads((OLD/'data/parts.json').read_text())
 batches=[];records=[];detail=[];prompts=[]
 infer_tok=AutoTokenizer.from_pretrained(str(CKPT));plugin=make_plugin(separate_edge=True)
 for i in range(len(ds)):
  set_seed(42);batch=col([copy.deepcopy(ds[i])]);batches.append(batch)
  ids=batch['input_ids'][0].tolist();lab=batch['labels'][0].tolist();mask=batch['attention_mask'][0].tolist();active=[j for j,x in enumerate(lab) if x!=-100];target=[lab[j] for j in active];eos=[j for j in range(len(ids)) if ids[j]==tok.eos_token_id and mask[j]==1 and j>=active[0]]
  row={'id':raw[i]['id'],'case_id':'airplane','part_id':raw[i]['sample_id'],'gt_token_count_block':len(target),'bos_token':tok.bos_token,'bos_token_id':tok.bos_token_id,'eos_token':tok.eos_token,'eos_token_id':tok.eos_token_id,'pad_token':tok.pad_token,'pad_token_id':tok.pad_token_id,'target_last30_ids':target[-30:],'target_last30_tokens':tok.convert_ids_to_tokens(target[-30:]),'eos_positions0':eos,'eos_labels':[lab[j] for j in eos],'eos_masked':[lab[j]==-100 for j in eos],'last_valid_label':lab[active[-1]],'last_valid_label_token':tok.decode([lab[active[-1]]]),'padding_start0':next((j for j,m in enumerate(mask) if not m),None),'padding_length':mask.count(0),'active_label_n':len(active)}
  detail.append(row)
  msgs=plugin.process_messages([{'role':'user','content':raw[i]['conversations'][0]['value']}],[{}]);inf=infer_tok.apply_chat_template(msgs,add_generation_prompt=True)
  pr={'id':row['id'],'train_ids':ids[:active[0]],'inference_ids':inf,'match':ids[:active[0]]==inf,'train_text':tok.decode(ids[:active[0]],skip_special_tokens=False),'inference_text':infer_tok.decode(inf,skip_special_tokens=False)}
  if i==0 or not pr['match']:prompts.append(pr)
  if i%20==0:print('AUDIT',i,len(ds),'prompt_match',pr['match'],flush=True)
 for p in parts:
  rows=[r for r in detail if r['part_id']=='airplane__'+p['part']];last=rows[-1]
  records.append(dict(last,part_id=p['part'],gt_block_count=p['blocks'],gt_token_count=p['full_target_tokens'],supervised_token_count=sum(r['active_label_n'] for r in rows),all_blocks=rows))
 summary={'TARGET_N':len(records),'TARGET_WITH_EOS_N':sum(bool(r['eos_positions0']) for r in records),'TARGET_WITHOUT_EOS_N':sum(not r['eos_positions0'] for r in records),'EOS_LABEL_ACTIVE_N':sum(any(v==tok.eos_token_id for v in r['eos_labels']) for r in records),'EOS_LABEL_MASKED_N':sum(any(r['eos_masked']) for r in records),'PAD_EQUALS_EOS':'YES' if tok.pad_token_id==tok.eos_token_id else 'NO','BLOCK_TARGET_N':len(detail),'BLOCK_WITH_EOS_N':sum(bool(r['eos_positions0']) for r in detail),'BLOCK_EOS_ACTIVE_N':sum(any(v==tok.eos_token_id for v in r['eos_labels']) for r in detail),'EOS_MASK_BUG_FOUND':'YES' if any(any(r['eos_masked']) for r in detail) else 'NO'}
 save(DEBUG/'target_eos_audit.json',{'summary':summary,'parts':records});save(DEBUG/'prompt_parity.json',prompts)
 fields=[k for k in records[0] if k!='all_blocks']
 with (DEBUG/'target_eos_audit.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows([{k:json.dumps(v) if isinstance(v,list) else v for k,v in r.items() if k!='all_blocks'} for r in records])
 save(DEBUG/'evidence/actual_collator_case0.json',{'input_ids':batches[0]['input_ids'][0].tolist(),'labels':batches[0]['labels'][0].tolist(),'attention_mask':batches[0]['attention_mask'][0].tolist()})
 torch.save(batches,DEBUG/'collated_batches.pt');save(DEBUG/'batch_ids.json',[r['id'] for r in raw]);print(json.dumps(summary),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='audit':audit()
 elif sys.argv[1]=='teacher':
  model,tok=load();batches=torch.load(DEBUG/'collated_batches.pt',weights_only=False);ids=json.loads((DEBUG/'batch_ids.json').read_text());bs=[b for b,i in zip(batches,ids) if 'PART_000__' in i];teacher(model,tok,bs,DEBUG)
  gen=model.generation_config.to_dict();effective=dict(gen,do_sample=False,num_beams=1,max_new_tokens=1280,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id)
  save(DEBUG/'generation_config_audit.json',{'tokenizer':{k:getattr(tok,k) for k in ['eos_token','eos_token_id','pad_token','pad_token_id','bos_token','bos_token_id']},'saved':json.loads((CKPT/'generation_config.json').read_text()),'runtime':gen,'effective':effective,'stopping_criteria':['MaxLengthCriteria(prompt_length+1280)','EosTokenCriteria(runtime eos ids)'],'program_termination':'outer block loop tests generated literal # CAD_COMPLETE; token EOS ends each individual block, not the whole program','TRAIN_EOS_ID':tok.eos_token_id,'GENERATION_EOS_ID':effective['eos_token_id'],'EOS_ID_MATCH':'YES' if tok.eos_token_id in (effective['eos_token_id'] if isinstance(effective['eos_token_id'],list) else [effective['eos_token_id']]) else 'NO','match_definition':'training EOS must belong to actual generation stop set; exact scalar/list equality reported separately','EXACT_EOS_CONFIG_EQUAL':tok.eos_token_id==effective['eos_token_id']})
