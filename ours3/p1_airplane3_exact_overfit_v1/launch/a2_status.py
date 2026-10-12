from pathlib import Path
import json,time,sys
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1')
def read(p):return json.loads(p.read_text())
if '--compact' in sys.argv:
 o=read(E/'audits/orchestrator.json');results=list((E/'evaluations').glob('checkpoint-*/PART_*/result.json'))
 print('COMPLETE_CASE_EVALUATIONS',len(results),'/ 24','EXACT_PART_RESULTS',[(p.parent.parent.name,p.parent.name) for p in results if read(p)['PART_GATE_PASS']],'ERRORS',o['errors'])
 for j in o['active']:
  p=E/f"evaluations/checkpoint-{j['step']}/{j['part']}/predicted_blocks.json";blocks=len(read(p)) if p.exists() else 0
  print(j['step'],j['part'],'GPU',j.get('gpu','1'),'BLOCKS',blocks)
 print('GPU_RESERVATIONS_RESTORED',read(E/'audits/gpu_lease_restored.json') if (E/'audits/gpu_lease_restored.json').exists() else [])
 sys.exit(0)
t=read(E/'audits/gpu_progress.json');print('TRAIN',t['global_step'],'loss',t['last_scaled_loss'],'elapsed_min',round(t['elapsed_seconds']/60,1))
o=read(E/'audits/orchestrator.json');print('TRAIN_ALIVE',o['training_alive'],'READY',o['ready'],'ERRORS',o['errors'])
if o['ready']:
 step=max(o['ready']);history=read(E/f'runs/quick/checkpoint-{step}/trainer_state.json')['log_history']
 print('EVAL_LOSS',[(r['step'],round(r['eval_loss'],9)) for r in history if 'eval_loss' in r])
for s in o['summaries']:print('CHECKPOINT',s)
for j in o['active']:
 p=E/f"evaluations/checkpoint-{j['step']}/{j['part']}";tf=read(p/'teacher_forced.json') if (p/'teacher_forced.json').exists() else {}
 blocks=read(p/'predicted_blocks.json') if (p/'predicted_blocks.json').exists() else []
 div=None
 if (E/'audits/gt_supervised_tokens_for_status.json').exists() and (p/'predicted_tokens.json').exists():
  gt=read(E/'audits/gt_supervised_tokens_for_status.json')[j['part']];pred=sum((r['token_ids'] for r in read(p/'predicted_tokens.json')),[])
  div=next((i+1 for i,(a,b) in enumerate(zip(gt,pred)) if a!=b),None)
  if div is None and len(pred)>len(gt):div=len(gt)+1
 print('ACTIVE',j['step'],j['part'],'blocks',len(blocks),'tf_acc',tf.get('TOKEN_ACC'),'margin',tf.get('MIN_TOKEN_MARGIN'),'divergence_so_far',div,'last_block_age_s',round(time.time()-(p/'predicted_blocks.json').stat().st_mtime) if blocks else None)
