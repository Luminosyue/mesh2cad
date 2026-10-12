from pathlib import Path
import sys,json,shutil,gzip,gc,subprocess,hashlib
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1');sys.path.insert(0,str(E/'launch'))
from a2_runtime import load,teacher,save,torch
base=E/'audits/argmax_teacher_verification';base.mkdir(exist_ok=True)
if len(sys.argv)==1:
 records=[]
 for step in [250,500,750,1000,1500,2000,2500,3000]:
  for part in ['PART_000','PART_001','PART_005']:
   subprocess.run([sys.executable,__file__,str(step),part],check=True)
   records.append(json.loads((base/f'checkpoint-{step}_{part}.json').read_text()))
   save(base/'progress.json',records)
 save(base/'complete.json',{'PASS':True,'case_n':len(records),'gate_unchanged':True,'free_decode_files_unchanged':True,'records':records})
 print('ARGMAX_AUDIT_COMPLETE',flush=True)
 sys.exit(0)
inv=json.loads((E/'data/block_inventory.json').read_text());batches=torch.load(E/'data/collated_batches.pt',weights_only=False);summary=[]
for checkpoint in sorted((E/'runs/quick').glob('checkpoint-*'),key=lambda p:int(p.name.split('-')[-1])):
 if checkpoint.name!='checkpoint-'+sys.argv[1]:continue
 model,tok=load(checkpoint)
 for part in ['PART_000','PART_001','PART_005']:
  if part!=sys.argv[2]:continue
  out=E/'evaluations'/checkpoint.name/part;backup=base/'original'/checkpoint.name/part;backup.mkdir(parents=True,exist_ok=True)
  for name in ['teacher_forced.json','teacher_tokens.jsonl.gz','result.json']:
   if not (backup/name).exists():shutil.copy2(out/name,backup/name)
  untouched={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file() and f.name not in ['teacher_forced.json','teacher_tokens.jsonl.gz','result.json']}
  old=json.loads((backup/'teacher_forced.json').read_text())
  with gzip.open(backup/'teacher_tokens.jsonl.gz','rt') as f:oldrows=[json.loads(line) for line in f]
  selected=[b for b,r in zip(batches,inv) if r['part']==part]
  stage=base/'recomputed'/checkpoint.name/part;stage.mkdir(parents=True,exist_ok=True)
  tf,rows=teacher(model,tok,selected,stage)
  assert len(rows)==len(oldrows)
  for a,b in zip(oldrows,rows):
   for k in ['block','token_in_block','gt_id','GT_LOGIT','SECOND_BEST_LOGIT','TOKEN_MARGIN','GT_TOKEN_PROB','NLL']:assert a[k]==b[k],(checkpoint.name,part,k,a[k],b[k])
  changes=[{'block':b['block'],'token_in_block':b['token_in_block'],'old_top1':a['top1_id'],'argmax_top1':b['top1_id'],'old_correct':a['CORRECT'],'argmax_correct':b['CORRECT'],'margin':b['TOKEN_MARGIN']} for a,b in zip(oldrows,rows) if a['top1_id']!=b['top1_id']]
  shutil.copy2(stage/'teacher_tokens.jsonl.gz',out/'teacher_tokens.jsonl.gz')
  tf['PREDICTION_RULE']='torch.argmax over logits; first (lowest-index) maximum on exact ties, matching greedy generation';save(out/'teacher_forced.json',tf)
  result=json.loads((backup/'result.json').read_text());oldgate=result['PART_GATE_PASS']
  result.update(TOKEN_ACC_TEACHER_FORCED=tf['TOKEN_ACC'],EOS_ACC=tf['EOS_ACC'],GT_SEQUENCE_NLL=tf['GT_SEQUENCE_NLL'],MEAN_NLL=tf['MEAN_NLL'],MIN_TOKEN_MARGIN=tf['MIN_TOKEN_MARGIN'],P1_TOKEN_MARGIN=tf['P1_TOKEN_MARGIN'],P5_TOKEN_MARGIN=tf['P5_TOKEN_MARGIN'],MEDIAN_TOKEN_MARGIN=tf['MEDIAN_TOKEN_MARGIN'])
  result['DIVERGENCE_TEACHER_CONTEXT']=next((r for r in rows if r['block']==result['FIRST_DIVERGENCE_BLOCK'] and r['token_in_block']==result['FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN']),None)
  result['PART_GATE_PASS']=all(result[k] for k in ['SEQUENCE_EXACT_MATCH','BLOCK_COUNT_EXACT','BLOCK_EXACT_MATCH','EOS_TERMINATED','CAD_PARSE_PASS','CAD_EXECUTION_PASS','STEP_EXPORT_PASS']) and not result['SAFETY_CAP_HIT'] and result['TOKEN_ACC_TEACHER_FORCED']>=.999 and result['EOS_ACC']==1
  assert result['PART_GATE_PASS']==oldgate
  result['TEACHER_ARGMAX_AUDITED']=True;save(out/'result.json',result)
  record={'checkpoint':checkpoint.name,'part':part,'old_token_acc':old['TOKEN_ACC'],'argmax_token_acc':tf['TOKEN_ACC'],'logits_probabilities_margins_identical':True,'gate_unchanged':True,'top1_tie_changes':changes};summary.append(record)
  assert all(hashlib.sha256((out/name).read_bytes()).hexdigest()==digest for name,digest in untouched.items())
  record['free_decode_file_hashes_unchanged']=untouched
  save(base/f'{checkpoint.name}_{part}.json',record)
  save(base/'progress.json',summary);print('ARGMAX_VERIFIED',checkpoint.name,part,len(changes),old['TOKEN_ACC'],tf['TOKEN_ACC'],flush=True)
 del model,tok;gc.collect();torch.cuda.empty_cache()
