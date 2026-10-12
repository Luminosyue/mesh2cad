from p1_debug_runtime import *
from p1_debug_runtime import _load_sepedge
import argparse,ast,subprocess,time,gc

def rollout(model,tok,outdir,max_blocks=64):
 outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
 raw=json.loads((OLD/'data/train.json').read_text());gt=[r['conversations'][1]['value'] for r in raw if r['sample_id']=='airplane__PART_000']
 row=next(r for r in json.loads((OLD/'data/parts.json').read_text()) if r['part']=='PART_000');target=Path(row['folder'])
 plugin=make_plugin(separate_edge=True);surface,edge=_load_sepedge(plugin,target/'surface_points.npy');prefix='';blocks=[];trace=[];ended=False;eos_ids=model.generation_config.eos_token_id;eos_ids=eos_ids if isinstance(eos_ids,list) else [eos_ids]
 gtids=[tok.encode(x,add_special_tokens=False)+[tok.eos_token_id] for x in gt]
 save(outdir/'gt_blocks.json',gt);save(outdir/'gt_token_sequence.json',gtids)
 started=time.time()
 for i in range(max_blocks):
  messages=plugin.process_messages([{'role':'user','content':prompt_for(tok,prefix,i)}],[{}]);ids=tok.apply_chat_template(messages,add_generation_prompt=True,return_tensors='pt').cuda()
  with torch.inference_mode():pred=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surface.cuda(),edge_clouds=edge.cuda(),max_new_tokens=1280,do_sample=False,num_beams=1,use_cache=True,pad_token_id=tok.pad_token_id or tok.eos_token_id)
  generated=pred[0,ids.shape[1]:].tolist();text=tok.decode(generated,skip_special_tokens=True).rstrip();blocks.append(text)
  natural_eos=bool(generated) and generated[-1] in eos_ids
  trace.append({'block':i+1,'raw_generated_ids':generated,'eos_positions0':[j for j,t in enumerate(generated) if t in eos_ids],'natural_token_eos':natural_eos,'hit_token_cap':len(generated)>=1280 and not natural_eos,'cad_complete_predicted':END_MARKER in text})
  prefix+=text+'\n'
  save(outdir/'predicted_blocks.json',blocks);save(outdir/'predicted_token_sequence.json',trace);(outdir/'prediction.py').write_text(prefix)
  print('BLOCK',outdir.name,i+1,'tokens',len(generated),'EOS',natural_eos,'END',END_MARKER in text,flush=True)
  if END_MARKER in text:
   ended=True;break
  if not text:break
 # GT lengths are used only below, after generation has stopped, to score outputs.
 gtflat=[x for b in gtids for x in b];predflat=[x for b in trace for x in b['raw_generated_ids']]
 div=next((j for j,(a,b) in enumerate(zip(gtflat,predflat)) if a!=b),None)
 if div is None and len(gtflat)!=len(predflat):div=min(len(gtflat),len(predflat))
 blockdiv=next((i+1 for i in range(max(len(gtids),len(trace))) if i>=len(gtids) or i>=len(trace) or gtids[i]!=trace[i]['raw_generated_ids']),None)
 localdiv=None
 if blockdiv and blockdiv<=len(gtids) and blockdiv<=len(trace):
  g=gtids[blockdiv-1];p=trace[blockdiv-1]['raw_generated_ids'];localdiv=next((j for j,(a,b) in enumerate(zip(g,p)) if a!=b),min(len(g),len(p)))
 matches=[i<len(blocks) and blocks[i]==g for i,g in enumerate(gt)]
 seqexact=gtflat==predflat;blockexact=len(blocks)==len(gt) and all(matches)
 try:ast.parse(prefix);parse=True;parse_error=None
 except SyntaxError as e:parse=False;parse_error=str(e)
 execution=False;step=False;metrics=None
 if parse:
  try:
   p=subprocess.run(['/usr/bin/python3',str(DEBUG/'evidence/cq54_evaluate.py'),str(outdir),str(target)],capture_output=True,text=True,timeout=240)
   (outdir/'execution.log').write_text(p.stdout+p.stderr)
   execution=p.returncode==0;step=(outdir/'prediction.step').is_file()
   if (outdir/'metrics.json').exists():metrics=json.loads((outdir/'metrics.json').read_text())
  except subprocess.TimeoutExpired:(outdir/'execution.log').write_text('CAD execution timeout 240 seconds')
 result={'GT_BLOCK_COUNT':len(gt),'PRED_BLOCK_COUNT':len(blocks),'SEQUENCE_EXACT_MATCH':seqexact,'BLOCK_EXACT_MATCH':blockexact,'BLOCK_EXACT_MATCH_N':sum(matches),'BLOCK_EXACT_MATCH_RATE':sum(matches)/len(gt),'BLOCK_COUNT_EXACT_ACC':int(len(blocks)==len(gt)),'PARSE_PASS':parse,'parse_error':parse_error,'EXECUTION_PASS':execution,'STEP_EXPORT_PASS':step,'program_end_predicted':ended,'final_token_eos':trace[-1]['natural_token_eos'],'safety_cap_hit':len(blocks)==max_blocks and not ended,'FIRST_DIVERGENCE_TOKEN':None if div is None else div+1,'FIRST_DIVERGENCE_BLOCK':blockdiv,'FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN':None if localdiv is None else localdiv+1,'indexing':'1-based; sequence includes the trained EOS after each block','seconds':time.time()-started,'gt_token_count_with_block_eos':len(gtflat),'pred_token_count_with_block_eos':len(predflat),'max_generated_blocks':max_blocks,'DIAGNOSIS':'SINGLE_SAMPLE_OVERFIT_PASS' if seqexact and blockexact and parse and execution and step else 'AUTOREGRESSIVE_ROLLOUT_FAILURE','geometry_metrics':metrics}
 save(outdir/'single_case_decode_diagnosis.json',result)
 diff=[]
 for i in range(max(6,min(10,len(blocks)))):
  diff+=['BLOCK '+str(i+1),'GT:',gt[i] if i<len(gt) else '(GT has ended; no further block)','PRED:',blocks[i] if i<len(blocks) else '(model did not generate this block)','MATCH='+('YES' if i<len(gt) and i<len(blocks) and gt[i]==blocks[i] else 'NO'),'']
 (outdir/'case0_block_diff.txt').write_text('\n'.join(diff))
 print('RESULT',json.dumps(result),flush=True)
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',default=str(CKPT));ap.add_argument('--out',required=True);ap.add_argument('--teacher',action='store_true');a=ap.parse_args()
 model,tok=load(Path(a.checkpoint));tf=None
 if a.teacher:
  batches=torch.load(DEBUG/'collated_batches.pt',weights_only=False);ids=json.loads((DEBUG/'batch_ids.json').read_text());bs=[b for b,i in zip(batches,ids) if 'PART_000__' in i];tf=teacher(model,tok,bs,Path(a.out))
 result=rollout(model,tok,Path(a.out))
 if tf:
  result.update(TOKEN_ACC=tf['token_acc'],EOS_ACC=tf['eos_acc'],TEACHER_NLL=tf['mean_nll'])
  trainstate=Path(a.checkpoint)/'trainer_state.json'
  if trainstate.exists():
   state=json.loads(trainstate.read_text());hist=state['log_history'];result['TRAIN_LOSS']=next((x['loss'] for x in reversed(hist) if 'loss' in x),None);result['TRAIN_STEP']=state['global_step']
  result['SINGLE_PART_EXACT_OVERFIT']='PASS' if tf['token_acc']>=.999 and tf['eos_acc']==1 and all(result[k] for k in ['SEQUENCE_EXACT_MATCH','BLOCK_EXACT_MATCH','PARSE_PASS','EXECUTION_PASS','STEP_EXPORT_PASS','program_end_predicted','final_token_eos']) and result['PRED_BLOCK_COUNT']==6 else 'FAIL'
  save(Path(a.out)/'single_case_decode_diagnosis.json',result)
