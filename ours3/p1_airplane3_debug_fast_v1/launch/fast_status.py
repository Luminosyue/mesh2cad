from pathlib import Path
import json,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');read=lambda p:json.loads(p.read_text());s=read(E/'status.json');print(s['phase'],'elapsed_min',round(s['elapsed_seconds']/60,1),'errors',s['errors'])
for job in s['active']:
 folder=E/f"evaluations/{job['tag']}/{job['part']}";tf=read(folder/'teacher_forced.json') if (folder/'teacher_forced.json').exists() else {};tokens=read(folder/'predicted_tokens.json') if (folder/'predicted_tokens.json').exists() else []
 gt=read(E.parent/'p1_airplane3_exact_overfit_v1/audits/gt_supervised_tokens_for_status.json')[job['part']];pred=sum((r['token_ids'] for r in tokens),[]);first=next((i+1 for i,(a,b) in enumerate(zip(gt,pred)) if a!=b),None)
 print(job['tag'],job['part'],'GPU',job['gpu'],'TF_errors',tf.get('TOKEN_ERRORS'),'blocks',len(tokens),'first_divergence_proven',first,'last_END',tokens[-1]['CAD_COMPLETE_PREDICTED'] if tokens else None)
if (E/'audits/gpu_progress.json').exists():
 p=read(E/'audits/gpu_progress.json');print('TRAIN',p['global_step'],'loss',p['last_scaled_loss'],'microbatches',p['microbatches'],'part_exposures',p['part_exposures'])
if (E/'best_checkpoint.json').exists():print('BEST',read(E/'best_checkpoint.json'))
if (E/'diagnostics/path_gate.json').exists():print('DIAG_MIN',round((read(E/'diagnostics/path_gate.json')['timestamp']-read(E/'configs/budget.json')['created'])/60,1))
