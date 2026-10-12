from pathlib import Path
import json,statistics
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1');PARTS=['PART_000','PART_001','PART_005'];STEPS=[2000,2500,3000]
def read(p):return json.loads(p.read_text())
completion={}
def evidence(s,p):
 d=E/f'evaluations/checkpoint-{s}/{p}'
 if (d/'result.json').exists():completion[f'{s}/{p}']=True;return read(d/'result.json')
 tf=read(d/'teacher_forced.json');pred=sum((r['token_ids'] for r in read(d/'predicted_tokens.json')),[]);gt=read(E/'audits/gt_supervised_tokens_for_status.json')[p]
 first=next((i+1 for i,(a,b) in enumerate(zip(gt,pred)) if a!=b),None)
 if first is None and len(pred)>len(gt):first=len(gt)+1
 assert first is not None,'A matching unfinished prefix cannot prove exact or failure'
 completion[f'{s}/{p}']=False
 return {'TOKEN_ACC_TEACHER_FORCED':tf['TOKEN_ACC'],'FIRST_DIVERGENCE_TOKEN':first,'GT_TOKEN_COUNT':len(gt),'MIN_TOKEN_MARGIN':tf['MIN_TOKEN_MARGIN'],'PART_GATE_PASS':False}
rows={s:{p:evidence(s,p) for p in PARTS} for s in STEPS}
history=read(E/'runs/quick/checkpoint-3000/trainer_state.json')['log_history'];loss={r['step']:r['eval_loss'] for r in history if 'eval_loss' in r}
loss_down=all(loss[a]>loss[b] for a,b in zip(STEPS,STEPS[1:]))
training=[json.loads(line) for line in (E/'audits/training_steps.jsonl').read_text().splitlines()]
train_loss={s:statistics.mean(r['last_scaled_loss'] for r in training if s-100<r['global_step']<=s) for s in STEPS}
train_loss_down=all(train_loss[a]>train_loss[b] for a,b in zip(STEPS,STEPS[1:]))
tf={p:[rows[s][p]['TOKEN_ACC_TEACHER_FORCED'] for s in STEPS] for p in PARTS}
div={p:[rows[s][p]['FIRST_DIVERGENCE_TOKEN'] if rows[s][p]['FIRST_DIVERGENCE_TOKEN'] is not None else rows[s][p]['GT_TOKEN_COUNT']+1 for s in STEPS] for p in PARTS}
mean_tf=[statistics.mean(tf[p][i] for p in PARTS) for i in range(3)]
tf_up=mean_tf[-1]>max(mean_tf[:-1])+1e-12
div_back=all(v[-1]>=max(v[:-1]) for v in div.values()) and any(v[-1]>max(v[:-1]) for v in div.values())
passed=all(r['PART_GATE_PASS'] for r in rows[3000].values())
decision={'STEPS_REVIEWED':STEPS,'EVAL_LOSS':loss,'TF_ACCURACY_BY_PART':tf,'MEAN_TF_ACCURACY':mean_tf,'FIRST_DIVERGENCE_BY_PART':div,'MIN_MARGIN_BY_PART':{p:[rows[s][p]['MIN_TOKEN_MARGIN'] for s in STEPS] for p in PARTS},'LOSS_CONTINUES_DOWN':loss_down,'TF_ACCURACY_CONTINUES_UP':tf_up,'DIVERGENCE_CONTINUES_LATER':div_back,'CHECKPOINT_3000_PASS':passed,'EXTEND_AUTHORIZED_BY_METRICS':not passed and loss_down and tf_up and div_back,'RESUME_STEP':3000,'NEW_MAX_STEPS':5000,'INTERPRETATION':'Predeclared before collecting checkpoint-2000 free decoding: loss must decline across all three late saved checkpoints; latest macro mean TF accuracy must exceed both preceding values; each latest first-divergence position must be no earlier than either preceding checkpoint and at least one must improve. Individual token-accuracy regressions and intermediate oscillations remain visible. Exact sequences are right-censored at GT token count + 1. This review does not start training.'}
decision['FULL_EVALUATION_COMPLETED']=completion
decision['TRAIN_LOSS_LAST100_MEAN']=train_loss
decision['TRAIN_LOSS_CONTINUES_DOWN']=train_loss_down
decision['ACTUAL_MAX_STEPS']=3000
decision['DECISION']='ELIGIBLE_FOR_CONDITIONAL_EXTENSION' if decision['EXTEND_AUTHORIZED_BY_METRICS'] else 'STOP_AT_3000; NO_EXTENSION'
decision['PARTIAL_EVIDENCE_NOTE']='A recorded raw-token divergence proves sequence failure permanently; unfinished matching prefixes are never classified. This budget decision never stops or truncates the pending full rollouts.'
(E/'audits/budget_decision.json').write_text(json.dumps(decision,indent=2))
if not all(completion.values()) and not (E/'audits/budget_decision_before_full_evaluation.json').exists():(E/'audits/budget_decision_before_full_evaluation.json').write_text(json.dumps(decision,indent=2))
print(json.dumps(decision,indent=2))
