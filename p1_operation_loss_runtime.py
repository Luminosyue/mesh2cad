import hashlib,json,os
from collections import defaultdict
from pathlib import Path
import torch
import torch.nn.functional as F
EXP=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_operation_aware_structure_loss_v1');REG={};ACC=defaultdict(float);CALLS=defaultdict(int);LAST_BATCH_AUDIT={};RAW_MASK=None;SPLICED_MASKS=[];LAST={}
def load_registry():
 if REG:return
 for split in ('TRAIN','VAL'):
  for line in (EXP/'masks'/f'{split}_OPERATION_TOKEN_MASK_REGISTRY.jsonl').read_text().splitlines():
   r=json.loads(line);REG[r['response_sha256']]=r
def locate(seq,pat,start=0,valid=None):
 for i in range(start,len(seq)-len(pat)+1):
  if seq[i:i+len(pat)]==pat and (valid is None or all(valid[j] for j in range(i,i+len(pat)))):return i
 return -1
def response_text(x):
 if isinstance(x,str):return x
 if isinstance(x,list):
  for z in reversed(x):
   if isinstance(z,dict):
    for k in ('content','value','text'):
     if isinstance(z.get(k),str):return z[k]
 raise TypeError(type(x).__name__)
def install():
 load_registry()
 from spatiallm.tuner.data.collator import MultiModalDataCollatorForSeq2Seq
 old_call=MultiModalDataCollatorForSeq2Seq.__call__
 def call(self,features):
  responses=[response_text(x['_response']) for x in features];batch=old_call(self,features);mask=torch.zeros_like(batch['labels'],dtype=torch.bool)
  for bi,text in enumerate(responses):
   r=REG.get(hashlib.sha256(text.encode()).hexdigest())
   if r is None:raise RuntimeError('operation registry missing response hash')
   seq=batch['input_ids'][bi].tolist();valid=(batch['labels'][bi]!=-100).tolist();cursor=0
   for span in r['operation_spans']:
    pat=span['token_ids'];st=locate(seq,pat,cursor,valid)
    if st<0:raise RuntimeError(f"operation token span not found: {span['operation']}")
    for j in range(st,st+len(pat)):
     if batch['labels'][bi,j].item()==-100:raise RuntimeError('operation token maps to masked label')
     mask[bi,j]=True
    cursor=st+len(pat)
  batch['operation_mask']=mask
  global LAST_BATCH_AUDIT;LAST_BATCH_AUDIT={'batch_size':len(responses),'op_mask_n':int(mask.sum()),'all_supervised_n':int((batch['labels']!=-100).sum())}
  return batch
 MultiModalDataCollatorForSeq2Seq.__call__=call
 import spatiallm.model.spatiallm_llama as sl
 old_splice=sl._splice_labels;old_chunk=sl._chunked_lm_loss
 def splice(cur_labels,regions,target_len):
  out=old_splice(cur_labels,regions,target_len)
  if RAW_MASK is not None:
   idx=len(SPLICED_MASKS);raw=RAW_MASK[idx].to(cur_labels.device,dtype=torch.bool);pieces=[];cursor=0
   for start,num_tokens,end in regions:
    pieces.append(raw[cursor:start+1]);pieces.append(torch.zeros(num_tokens,dtype=torch.bool,device=raw.device));cursor=end
   pieces.append(raw[cursor:]);m=torch.cat(pieces,dim=0)
   if m.numel()<target_len:m=F.pad(m,(0,target_len-m.numel()),value=False)
   else:m=m[:target_len]
   SPLICED_MASKS.append(m)
  return out
 def chunk(lm_head,hidden_states,labels,chunk_size=256,ignore_index=-100):
  if RAW_MASK is None or len(SPLICED_MASKS)!=labels.shape[0]:return old_chunk(lm_head,hidden_states,labels,chunk_size,ignore_index)
  sh=hidden_states[:,:-1,:].contiguous();sy=labels[:,1:].contiguous();sm=torch.stack(SPLICED_MASKS)[:,1:].contiguous()&(sy!=ignore_index);base=hidden_states.new_zeros(());op=hidden_states.new_zeros(());nv=no=0
  for st in range(0,sh.shape[1],chunk_size):
   h=sh[:,st:st+chunk_size];y=sy[:,st:st+chunk_size];m=sm[:,st:st+chunk_size];logits=lm_head(h);fl=logits.reshape(-1,logits.size(-1)).float();fy=y.reshape(-1);fm=m.reshape(-1);base=base+F.cross_entropy(fl,fy,ignore_index=ignore_index,reduction='sum');nv+=int((fy!=ignore_index).sum())
   if bool(fm.any()):op=op+F.cross_entropy(fl[fm],fy[fm],reduction='sum');no+=int(fm.sum())
   del logits,fl
  if nv==0 or no==0:raise RuntimeError('empty base or operation supervision')
  base=base/nv;op=op/no;lam=float(os.environ.get('P1_ACTIVE_LAMBDA','0'));total=base+lam*op;LAST.update(base=base,op=op,total=total,op_n=no,valid_n=nv);return total
 sl._splice_labels=splice;sl._chunked_lm_loss=chunk
 import spatiallm.tuner.trainer as tm
 Base=tm.CustomSeq2SeqTrainer
 class OperationAwareTrainer(Base):
  def compute_loss(self,model,inputs,return_outputs=False,num_items_in_batch=None):
   global RAW_MASK,SPLICED_MASKS;RAW_MASK=inputs.pop('operation_mask');SPLICED_MASKS=[];os.environ['P1_ACTIVE_LAMBDA']=os.environ.get('P1_LAMBDA_OP','1.0') if model.training else '0';outputs=model(**inputs);loss=outputs.loss;phase='train' if model.training else 'eval'
   for k in ('base','op','total'):ACC[phase+'_'+k]+=float(LAST[k].detach())
   CALLS[phase]+=1
   if os.environ.get('P1_RUNTIME_STATS'):Path(os.environ['P1_RUNTIME_STATS']).write_text(json.dumps({'calls':dict(CALLS),'means':{k:ACC[k]/max(1,CALLS[k.split('_')[0]]) for k in ACC},'last_batch':LAST_BATCH_AUDIT,'last_loss':{k:float(v.detach()) if torch.is_tensor(v) else v for k,v in LAST.items()}},indent=2)+'\n')
   RAW_MASK=None;SPLICED_MASKS=[];return (loss,outputs) if return_outputs else loss
 tm.CustomSeq2SeqTrainer=OperationAwareTrainer;return OperationAwareTrainer
