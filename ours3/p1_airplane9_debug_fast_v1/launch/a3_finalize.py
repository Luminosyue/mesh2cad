from pathlib import Path
import json,hashlib,gzip,csv,statistics,zipfile
import numpy as np
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1')
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2))
assert (E/'outcome.json').exists() or (E/'failure.json').exists()
checks=[]
for r in read(E/'audits/frozen_inputs.json'):
 h=hashlib.sha256()
 with Path(r['path']).open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
 checks.append({'path':r['path'],'unchanged':h.hexdigest()==r['sha256']})
assert all(x['unchanged'] for x in checks)
steps=[json.loads(l) for l in (E/'audits/training_steps.jsonl').read_text().splitlines()];parts=[f'PART_{i:03d}' for i in range(9)]
for s in steps:
 counts=[s['part_exposures'].get(p,0) for p in parts];assert max(counts)-min(counts)<=1
 if s['microbatches']%9==0:assert len(set(counts))==1
cases=[]
import cadquery as cq
for f in sorted((E/'evaluations').glob('*/PART_*/result.json')):
 r=read(f);out=f.parent;gt=read(out/'gt_tokens.json');pred=read(out/'predicted_tokens.json');pids=[p['token_ids'] for p in pred]
 assert r['SEQUENCE_EXACT_MATCH']==(sum(gt,[])==sum(pids,[]));assert r['GT_TOKEN_COUNT']==len(sum(gt,[])) and r['PRED_TOKEN_COUNT']==len(sum(pids,[]))
 assert r['BLOCK_COUNT_EXACT']==(len(gt)==len(pids));assert r['BLOCK_EXACT_MATCH']==(gt==pids)
 tf=[json.loads(l) for l in gzip.open(out/'teacher_tokens.jsonl.gz','rt')];assert sum(not t['CORRECT'] for t in tf)==r['TOKEN_ERRORS']
 if r['STEP_READBACK_PASS']:
  shape=cq.importers.importStep(str(out/'prediction.step')).val();assert shape.isValid() and shape.Solids()
 if r['PART_GATE_PASS']:assert gt==pids and r['TOKEN_ERRORS']==0 and all(p['TOKEN_EOS_TERMINATED'] and not p['TOKEN_CAP_HIT'] for p in pred)
 cases.append({'path':str(f),'independently_verified':True,'gate':r['PART_GATE_PASS']})
save(E/'audits/final_independent_audit.json',{'frozen':checks,'balanced_microsteps':len(steps),'balanced_optimizer_updates':len(steps)//9,'cases':cases})
trajectory=read(E/'trajectory.json') if (E/'trajectory.json').exists() else []
with (E/'checkpoint_trajectory.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['checkpoint',*parts,'total_TF_errors','zero_error_parts','free_exact_N']);
 for r in trajectory:w.writerow([r['step'],*r['errors'],r['total_tf_errors'],r['zero_parts'],r['free_exact_n']])
if trajectory:
 tag='checkpoint-'+str(trajectory[-1]['step']);condition=[read(E/'scans'/tag/p/'conditioning.json') for p in parts]
 surface=np.array([c['mean_projected_tokens']['surface'] for c in condition]);curve=np.array([c['mean_projected_tokens']['curve'] for c in condition]);fused=(surface+curve)/2
 for name,arr in [('surface',surface),('curve',curve),('fused',fused)]:
  arr=arr/np.linalg.norm(arr,axis=1,keepdims=True);sim=arr@arr.T
  with (E/(name+'_condition_cosine.csv')).open('w',newline='') as f:
   w=csv.writer(f);w.writerow(['part',*parts]);w.writerows([[p,*r] for p,r in zip(parts,sim)])
 save(E/'audits/conditioning_definition.json',{'checkpoint':tag,'pooling':'surface/curve: arithmetic mean of projected tokens of first block; fused: equal-weight mean of the two branch means, not an extra learned fusion layer','interpretation':'pooled cosine is diagnostic only, cannot prove conditioning collision','dtype':condition[0]['dtype']})
audit=read(E/'airplane9_dataset_audit.json');outcome=read(E/'outcome.json') if (E/'outcome.json').exists() else {'P1_A3_GATE':'FAIL','failure':read(E/'failure.json')};best=outcome.get('best')
if best is None and trajectory:
 selected=min(trajectory,key=lambda r:(r['total_tf_errors'],-r['zero_parts'],r['step']));best={'checkpoint':selected['checkpoint'],'step':selected['step'],'selection':'TF-only candidate; no full exact verified'}
 if not (E/'best_checkpoint.json').exists():save(E/'best_checkpoint.json',best)
rows=[read(p) for p in (E/f"evaluations/checkpoint-{best['step']}").glob('PART_*/result.json')] if best else []
metrics={key:sum(bool(r.get(field)) for r in rows) for key,field in [('RAW_TOKEN_EXACT_N','SEQUENCE_EXACT_MATCH'),('BLOCK_EXACT_N','BLOCK_EXACT_MATCH'),('BLOCK_COUNT_EXACT_N','BLOCK_COUNT_EXACT'),('EOS_N','EOS_TERMINATED'),('PARSE_PASS_N','CAD_PARSE_PASS'),('EXEC_PASS_N','CAD_EXECUTION_PASS'),('STEP_EXPORT_PASS_N','STEP_EXPORT_PASS'),('STEP_ROUNDTRIP_PASS_N','STEP_READBACK_PASS'),('SAFETY_CAP_HIT_N','SAFETY_CAP_HIT')]}
first_tf=outcome.get('FIRST_9_OF_9_TF_ZERO_CHECKPOINT');first_exact=outcome.get('FIRST_9_OF_9_EXACT_CHECKPOINT')
lines=['# P1 AIRPLANE9 FAST EXACT REPORT','',f"P1_A3_GATE={outcome['P1_A3_GATE']}",f"EXACT_MEMORIZATION_STABLE={'YES' if outcome.get('EXACT_MEMORIZATION_STABLE') else 'NO'}",'', 'This is a training-set memorization gate, not evidence of held-out generalization.','', '## Provenance and frozen protocol','',f"BASE_CHECKPOINT={E.parent/'p1_quick_overfit_airplane9_v1/runs/quick/checkpoint-2000'}",'Original9 weights loaded; fresh AdamW because optimizer.pt was absent. No weights were initialized from FAST3. Prior FAST3 actually began from initial airplane3 checkpoint-2000; the request’s original9 attribution for that earlier run was corrected.','Frozen GT, tokenizer, grammar, serializer, geometry assets, model implementation and CAD executor hashes verified unchanged.','', '## Data and training','',f"TRAIN_PART_N=9; TOTAL_BLOCK_N=134; TOTAL_TOKEN_N={audit['TOTAL_TOKEN_N']} (includes every per-block EOS)",f"MIN_TOKEN_N={audit['MIN_TOKEN_N']}; MAX_TOKEN_N={audit['MAX_TOKEN_N']}; MEDIAN_TOKEN_N={audit['MEDIAN_TOKEN_N']}",'All9 GT parse/execute/STEP roundtrips passed. Every134 target sequence was checked against active labels, including EOS; no truncation.','LR=1e-5; SCHEDULER=constant; WARMUP=0; WEIGHT_DECAY=0; SEED=42','MICRO_BATCH_SIZE=1; GRAD_ACCUM_STEPS=9; PARTS_PER_EFFECTIVE_UPDATE=9','SAMPLER=deterministic part round-robin, shuffled cyclic block queues within each part; no augmentation','BALANCED_EXPOSURE=YES; max-min<=1 at every microstep, exactly equal after each update',f"ACTUAL_UPDATES={len(steps)//9}; MAX_EXTRA_UPDATES=500; WALL_BUDGET=4h",f"FINAL_EXPOSURES={steps[-1]['part_exposures'] if steps else {}}",'', '## Numerical path','', 'GEOMETRY_DTYPE_ALIGNED=YES; surface and curve inputs quantized to BF16 in both training and gate. Training uses FP32 stored parameters with BF16 autocast and TF32 enabled, matching FAST. Projector prehook input/weight dtype is FP32; autocast enabled. Gate loads checkpoint with the established BF16 loader then model.float(), FP32 projectors/decoder, autocast disabled, TF32 disabled. This includes the same BF16 weight quantization as successful FAST; it is not an unquantized FP32 checkpoint loader.','GATE_EVAL_FP32=YES; do_sample=False; num_beams=1. Fresh seeded model per part for TF scans.','Free decode begins with empty program, uses only own generated prefix (protocol recent384 suffix), fixed1280 token/block and64 block caps. Natural CAD_COMPLETE plus final block EOS required. EOS/PAD128009 unchanged; generation EOS list unchanged. No GT stopping, repair, clipping, or GT prefix.','', '## Trajectory','', '| Extra optimizer updates | Total TF errors | TF zero parts | Free exact |','|---:|---:|---:|---:|']
for r in trajectory:lines.append(f"| +{r['step']} | {r['total_tf_errors']} | {r['zero_parts']}/9 | {str(r['free_exact_n'])+'/9' if r['free_exact_n'] is not None else 'Not run'} |")
lines+=['',f"FIRST_9_OF_9_TF_ZERO_CHECKPOINT={str(E/f'runs/quick/checkpoint-{first_tf}') if first_tf else 'NONE'}",f"FIRST_9_OF_9_EXACT_CHECKPOINT={str(E/f'runs/quick/checkpoint-{first_exact}') if first_exact else 'NONE'}",f"BEST_CHECKPOINT={best['checkpoint'] if best else 'NONE'}",'Best exact checkpoint ranked by raw exact count, CAD/STEP success, fewer TF errors, then earliest update. TF-only fallback is explicitly not a free-decoding success.','', '## Best checkpoint per-part evidence','', '| Part | GT / pred blocks | GT / pred tokens | TF errors | Raw exact | Natural end | CAD execute | STEP readback |','|---|---:|---:|---:|---|---|---|---|']
for r in sorted(rows,key=lambda r:r['PART_ID']):lines.append(f"| {r['PART_ID']} | {r['GT_BLOCK_COUNT']} / {r['PRED_BLOCK_COUNT']} | {r['GT_TOKEN_COUNT']} / {r['PRED_TOKEN_COUNT']} | {r['TOKEN_ERRORS']} | {r['SEQUENCE_EXACT_MATCH']} | {r['EOS_TERMINATED']} | {r['CAD_EXECUTION_PASS']} | {r['STEP_READBACK_PASS']} |")
lines+=['',f"FREE_CASES_EVALUATED_AT_BEST={len(rows)}/9"]+[f'{k}={v}/9' if k!='SAFETY_CAP_HIT_N' else f'{k}={v}' for k,v in metrics.items()]
if rows:lines.append(f"TF_ZERO_ERROR_N={sum(r['TOKEN_ERRORS']==0 for r in rows)}/9")
if outcome['P1_A3_GATE']=='PASS':lines+=['','NEXT_GATE=P1-A4 GENERALIZATION / HELD-OUT','Memorization training stopped; no held-out experiment launched.']
else:
 last=trajectory[-1] if trajectory else None
 diagnosis='RESIDUAL_MULTI_SAMPLE_OPTIMIZATION_INSTABILITY' if last and max(last['errors'])<=2 else 'HARD_PART_OR_CONDITIONING_FAILURE'
 lines+=['',f'FAILURE_CLASSIFICATION={diagnosis} (provisional; inspect token margins across scans)','No extension to1000/3000 updates. Per-token GT, argmax, and margins are preserved in scans/*/PART_*/teacher_tokens.jsonl.gz. Conditioning cosine matrices are pooled diagnostics only.','NEXT_GATE=diagnose residual token evidence before any additional training',json.dumps(outcome)]
lines+=['','## Evidence','', 'Dataset audit, full checkpoint trajectory, all raw prediction and GT tokens, per-token TF logits/margins, execution logs, exported STEP, config, scripts, sampler indices/exposures, checkpoint weight loading evidence, and immutable source hashes are preserved under this experiment. Independent validation rechecked raw sequence equality, token counts, EOS/caps, STEP readback and all frozen hashes.','Conditioning matrices use mean projected tokens from the last scanned checkpoint; fused means an equal-weight mean of branch summaries, not a modified architecture.']
(E/'P1_AIRPLANE9_FAST_EXACT_REPORT.md').write_text('\n'.join(lines)+'\n')
archive=E/'p1_airplane9_fast_evidence.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for folder in ['launch','configs','audits','control','gt_preflight','scans','evaluations']:
  for p in (E/folder).rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts:z.write(p,str(p.relative_to(E)))
 for p in E.iterdir():
  if p.is_file() and p.suffix in ['.md','.json','.csv']:z.write(p,p.name)
print('FINALIZED',str(archive),archive.stat().st_size,flush=True)
