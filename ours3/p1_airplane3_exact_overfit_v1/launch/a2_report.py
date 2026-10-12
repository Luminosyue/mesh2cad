from pathlib import Path
import json,csv,hashlib,zipfile,statistics,os,yaml,gzip,ast
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'
PARTS=['PART_000','PART_001','PART_005'];BLOCKS=dict(zip(PARTS,[6,13,25]))
def read(p):return json.loads(p.read_text())
def save(p,data):p.write_text(json.dumps(data,indent=2,ensure_ascii=False))
def main():
 done=read(EXP/'control/evaluation_complete.json');assert not done['errors'],done['errors']
 steps=sorted(int(p.name.split('-')[1]) for p in (EXP/'runs/quick').glob('checkpoint-*'))
 rows=[];by={}
 for s in steps:
  by[s]=[]
  for p in PARTS:
   folder=EXP/f'evaluations/checkpoint-{s}/{p}';r=read(folder/'result.json');r.update(checkpoint=f'checkpoint-{s}',step=s)
   tf=read(folder/'teacher_forced.json');r.update(FIRST_WRONG_TOKEN=tf['FIRST_WRONG_TOKEN'],GT_TOKEN_PROB_AT_FIRST_ERROR=tf['GT_TOKEN_PROB_AT_FIRST_ERROR'],TOP1_PROB_AT_FIRST_ERROR=tf['TOP1_PROB_AT_FIRST_ERROR'],MIN_MARGIN_TOKEN=tf['MIN_MARGIN_TOKEN'])
   # Independent evidence consistency check; do not infer exact from printed text.
   gt=sum(read(folder/'gt_tokens.json'),[]);traces=read(folder/'predicted_tokens.json');pred=sum((x['token_ids'] for x in traces),[])
   assert gt==read(EXP/'audits/gt_supervised_tokens_for_status.json')[p]
   blocks=read(folder/'predicted_blocks.json');assert len(blocks)==len(traces)==r['PRED_BLOCK_COUNT']
   assert (folder/'prediction.py').read_text()==''.join(b+'\n' for b in blocks),'Prediction was modified after token decoding'
   try:ast.parse((folder/'prediction.py').read_text());parse=True
   except SyntaxError:parse=False
   assert parse==r['CAD_PARSE_PASS']
   with gzip.open(folder/'teacher_tokens.jsonl.gz','rt') as f:teacher_rows=[json.loads(line) for line in f]
   assert [t['gt_id'] for t in teacher_rows]==gt
   assert abs(sum(t['gt_id']==t['top1_id'] for t in teacher_rows)/len(teacher_rows)-r['TOKEN_ACC_TEACHER_FORCED'])<1e-12
   if not r['SEQUENCE_EXACT_MATCH']:assert (folder/f'failure_diff_{p}_checkpoint-{s}.txt').exists()
   assert r['SEQUENCE_EXACT_MATCH']==(gt==pred)
   assert r['GT_TOKEN_COUNT']==len(gt)==tf['TOKEN_N'];assert r['PRED_TOKEN_COUNT']==len(pred)
   assert r['STEP_EXPORT_PASS']==(folder/'prediction.step').exists()
   rows.append(r);by[s].append(r)
  rr=by[s]
  summary={'checkpoint':f'checkpoint-{s}','step':s,'TRAIN_CASE_N':3,'SEQUENCE_EXACT_N':sum(r['SEQUENCE_EXACT_MATCH'] for r in rr),'PART_GATE_PASS_N':sum(r['PART_GATE_PASS'] for r in rr),'MEAN_TOKEN_ACC':statistics.mean(r['TOKEN_ACC_TEACHER_FORCED'] for r in rr),'MIN_TOKEN_ACC':min(r['TOKEN_ACC_TEACHER_FORCED'] for r in rr),'EOS_ACC_ALL':sum(r['EOS_ACC']*r['GT_BLOCK_COUNT'] for r in rr)/sum(r['GT_BLOCK_COUNT'] for r in rr),'P1_A2_GATE':'PASS' if all(r['PART_GATE_PASS'] for r in rr) else 'FAIL'}
  save(EXP/f'evaluations/checkpoint-{s}/summary.json',summary)
 passes=[s for s in steps if all(r['PART_GATE_PASS'] for r in by[s])]
 exactpasses=[s for s in steps if all(r['SEQUENCE_EXACT_MATCH'] for r in by[s])];first=exactpasses[0] if exactpasses else None
 stable=any(a in exactpasses and b in exactpasses for a,b in zip(steps,steps[1:]));confirmation=steps[steps.index(first)+1] if first is not None and steps.index(first)+1<len(steps) else None
 assert not exactpasses or confirmation is not None,'First exact pass requires next checkpoint confirmation'
 best=passes[0] if passes else max(steps,key=lambda s:(sum(r['PART_GATE_PASS'] for r in by[s]),sum(r['SEQUENCE_EXACT_MATCH'] for r in by[s]),min(r['TOKEN_ACC_TEACHER_FORCED'] for r in by[s]),sum(r['FIRST_DIVERGENCE_TOKEN'] or r['GT_TOKEN_COUNT']+1 for r in by[s])))
 chosen=by[best];gate='PASS' if passes else 'FAIL'
 marginfields=['checkpoint','PART_ID','TOKEN_ACC_TEACHER_FORCED','EOS_ACC','MIN_TOKEN_MARGIN','P1_TOKEN_MARGIN','P5_TOKEN_MARGIN','MEDIAN_TOKEN_MARGIN','MIN_MARGIN_BLOCK','MIN_MARGIN_TOKEN_IN_BLOCK','GT_TOKEN','SECOND_BEST_TOKEN','GT_LOGIT','SECOND_BEST_LOGIT']
 with (EXP/'token_margin_analysis.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=marginfields);w.writeheader()
  for r in rows:
   m=r['MIN_MARGIN_TOKEN'];v={k:r[k] for k in marginfields if k in r};v.update(MIN_MARGIN_BLOCK=m['block'],MIN_MARGIN_TOKEN_IN_BLOCK=m['token_in_block'],GT_TOKEN=m['gt_token'],SECOND_BEST_TOKEN=m['second_best_token'],GT_LOGIT=m['GT_LOGIT'],SECOND_BEST_LOGIT=m['SECOND_BEST_LOGIT']);w.writerow(v)
 fields=['checkpoint','PART_ID','GT_BLOCK_COUNT','PRED_BLOCK_COUNT','GT_TOKEN_COUNT','PRED_TOKEN_COUNT','TOKEN_ACC_TEACHER_FORCED','EOS_ACC','GT_SEQUENCE_NLL','MEAN_NLL','FIRST_DIVERGENCE_TOKEN','FIRST_DIVERGENCE_BLOCK','FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN','BLOCK_COUNT_EXACT','BLOCK_EXACT_MATCH','SEQUENCE_EXACT_MATCH','EOS_TERMINATED','SAFETY_CAP_HIT','CAD_PARSE_PASS','CAD_EXECUTION_PASS','STEP_EXPORT_PASS','PART_GATE_PASS']
 with (EXP/'checkpoint_metrics.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 frozen=read(EXP/'audits/frozen_inputs.json');changes=[]
 for row in frozen['pipeline_and_gt']:
  p=Path(row['path'])
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:changes.append(row['path'])
 for row in frozen['original_experiment_files']:
  p=Path(row['path'])
  if not p.exists() or p.stat().st_size!=row['size'] or p.stat().st_mtime_ns!=row['mtime_ns']:changes.append(row['path'])
 for name in ['cq54_protocol.py','cq54_evaluate.py']:
  original=ROOT/'ours3/p1_quick_overfit_airplane9_v1/launch'/name;copy=EXP/'launch'/name
  if hashlib.sha256(original.read_bytes()).digest()!=hashlib.sha256(copy.read_bytes()).digest():changes.append(str(copy))
 original_data=read(ROOT/'ours3/p1_quick_overfit_airplane9_v1/data/train.json');selected={'airplane__'+p for p in PARTS}
 assert read(EXP/'data/train.json')==[r for r in original_data if r['sample_id'] in selected]
 assert read(EXP/'data/eval_memorization.json')==read(EXP/'data/train.json')
 assert read(EXP/'audits/checkpoint_tokenizer_verification.json')['PASS']
 assert read(EXP/'audits/gpu_restore_verification.json')['PASS']
 argmax_audit=read(EXP/'audits/argmax_teacher_verification/complete.json')
 assert argmax_audit['PASS'] and argmax_audit['case_n']==24 and argmax_audit['gate_unchanged'] and argmax_audit['free_decode_files_unchanged']
 save(EXP/'audits/frozen_verification.json',{'PASS':not changes,'changed_paths':changes,'checked_pipeline_assets':len(frozen['pipeline_and_gt']),'checked_original_experiment_files':len(frozen['original_experiment_files'])});assert not changes,changes
 train=[json.loads(l) for l in (EXP/'audits/training_steps.jsonl').read_text().splitlines()];last=train[-1]
 assert sum(last['part_exposures'].values())==last['global_step']
 firstex=read(EXP/f'audits/exposure_checkpoint-{first}.json') if first else None
 result={'TRAIN_CASE_N':3,'MAX_TRAIN_STEPS':3000,'TOTAL_OPTIMIZER_STEPS':last['global_step'],'FIRST_3_OF_3_EXACT_CHECKPOINT':f'checkpoint-{first}' if first else None,'FIRST_3_OF_3_EXACT_STEP':first,'TRAIN_LOSS_AT_FIRST_PASS':firstex['last_loss'] if firstex else None,'TRAIN_LOSS_LAST10_MEAN_AT_FIRST_PASS':firstex['last_10_mean_loss'] if firstex else None,'BEST_CHECKPOINT':f'checkpoint-{best}','EXACT_MEMORIZATION_STABLE':'YES' if stable else 'NO','EXACT_MEMORIZATION_UNSTABLE':'YES' if first and confirmation and confirmation not in passes else 'NO','P1_A2_GATE':gate,'NEXT_GATE':'P1-A3: AIRPLANE 9-PART EXACT MEMORIZATION (next round only)' if gate=='PASS' else 'DEBUG_MULTI_SAMPLE_MEMORIZATION','FROZEN_INPUTS_PASS':True}
 for name,field in [('SEQUENCE_EXACT_N','SEQUENCE_EXACT_MATCH'),('BLOCK_COUNT_EXACT_N','BLOCK_COUNT_EXACT'),('EOS_TERMINATED_N','EOS_TERMINATED'),('PARSE_PASS_N','CAD_PARSE_PASS'),('EXEC_PASS_N','CAD_EXECUTION_PASS'),('STEP_PASS_N','STEP_EXPORT_PASS'),('SAFETY_CAP_HIT_N','SAFETY_CAP_HIT')]:result[name]=sum(r[field] for r in chosen)
 for tag,r in zip('ABC',chosen):
  result.update({f'PART_{tag}':r['PART_ID'],f'PART_{tag}_BLOCKS':r['GT_BLOCK_COUNT'],f'PART_{tag}_TOKENS':r['GT_TOKEN_COUNT'],f'TOKEN_ACC_{tag}':r['TOKEN_ACC_TEACHER_FORCED'],f'EOS_ACC_{tag}':r['EOS_ACC'],f'MIN_TOKEN_MARGIN_{tag}':r['MIN_TOKEN_MARGIN'],f'PART_{tag}_EXPOSURES':last['part_exposures'][r['PART_ID']]})
 result['SAMPLING_BALANCE']='Unchanged uniform shuffled block sampling; unequal part block exposures, approximately equal full-program equivalents'
 result['EFFECTIVE_EXPOSURE_PER_SAMPLE']={p:last['part_exposures'][p]/BLOCKS[p] for p in PARTS}
 result['FIRST_FULL_GATE_PASS_CHECKPOINT']=f'checkpoint-{passes[0]}' if passes else None
 result['EXACT_MEMORIZATION_UNSTABLE']='YES' if first and confirmation and confirmation not in exactpasses else 'NO'
 if first is None:result.pop('EXACT_MEMORIZATION_UNSTABLE',None)
 latest=by[steps[-1]]
 result['DIAGNOSIS_AT_FINAL_CHECKPOINT']='EXACT_GATE_PASS' if all(r['PART_GATE_PASS'] for r in latest) else ('MULTI_SAMPLE_ROLLOUT_INSTABILITY' if all(r['TOKEN_ACC_TEACHER_FORCED']>=.999 for r in latest) else 'MULTI_SAMPLE_MEMORIZATION_INCOMPLETE')
 regressions=[{'part':p,'from_step':a,'to_step':b} for a,b in zip(steps,steps[1:]) for p in PARTS if next(r for r in by[a] if r['PART_ID']==p)['PART_GATE_PASS'] and not next(r for r in by[b] if r['PART_ID']==p)['PART_GATE_PASS']]
 result['PART_SPECIFIC_EXACT_REGRESSION']='YES' if regressions else 'NO';save(EXP/'audits/part_exact_regressions.json',regressions)
 result['BORROWED_GPU_RESERVATIONS_RESTORED']=True
 trajectory=[]
 for r in latest:
  anchor=r['DIVERGENCE_TEACHER_CONTEXT']
  if not anchor:continue
  for s in steps:
   with gzip.open(EXP/f"evaluations/checkpoint-{s}/{r['PART_ID']}/teacher_tokens.jsonl.gz",'rt') as f:
    for line in f:
     token=json.loads(line)
     if (token['block'],token['token_in_block'])==(anchor['block'],anchor['token_in_block']):
      trajectory.append({'checkpoint':s,'part':r['PART_ID'],'block':token['block'],'token_in_block':token['token_in_block'],'gt_token':token['gt_token'],'top1_token':token['top1_token'],'correct':token['CORRECT'],'gt_probability':token['GT_TOKEN_PROB'],'token_margin':token['TOKEN_MARGIN']});break
 if trajectory:
  with (EXP/'divergence_token_margin_trajectory.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(trajectory[0]));w.writeheader();w.writerows(trajectory)
 save(EXP/'gate_result.json',result)
 if (EXP/'configs/train_extension.yaml').exists():
  result['MAX_TRAIN_STEPS']=yaml.safe_load((EXP/'configs/train_extension.yaml').read_text())['max_steps'];save(EXP/'gate_result.json',result)
 lines=['# P1-A2 airplane 3-part exact memorization','',f'**P1_A2_GATE={gate}**。独立实验，固定分母 3 个训练零件。所有结果来自对应 checkpoint 的实际 greedy 自由生成。',f'实验目录：`{EXP}`。模型位于 `runs/quick/checkpoint-*`。','', '## 最终 Gate','', '```text']
 count_fields={'SEQUENCE_EXACT_N','BLOCK_COUNT_EXACT_N','EOS_TERMINATED_N','PARSE_PASS_N','EXEC_PASS_N','STEP_PASS_N'}
 lines += [f'{k}={v}'+('/3' if k in count_fields else '') for k,v in result.items()];lines+=['```','','主表的 N/3、token accuracy、margin 指标统一取 BEST_CHECKPOINT；曝光量字段取全部训练步骤。各 checkpoint 的完整指标逐行列在后面。','','## 数据与冻结协议','','A 为已通过单样本验证的 PART_000；B 为 block/token 中位数附近的 PART_001；C 为原九件中程序最长的 PART_005。三个 GT 均通过原 executor 执行和 STEP 导出。','', 'TOKEN_COUNT 采用每个训练 block 的原始目标 token 加 EOS 的总和；selected_3parts.json 中另保留原 inventory whole-program 计数。二者分块边界定义不同。','', 'GT、serializer、词表、EOS/PAD、block grammar、mesh preprocessing、executor 均冻结，原实验文件大小与修改时间、pipeline 与 GT SHA256 复核通过。','', '初始化仍为原 checkpoint-8000，未用单样本 checkpoint-500 热启动。batch=1，gradient accumulation=1，lr=5e-5 constant，seed=42；full fine-tuning，冻结 point tower。训练日志保存每步未舍入 loss。','','## 每个 checkpoint 的自由生成与 teacher-forcing','','| Checkpoint | Part | TF token acc | EOS acc | Pred/GT blocks | Raw token exact | END+EOS | Cap | Parse/Exec/STEP | First divergence block/token |','|---|---|---:|---:|---:|---|---|---|---|---|']
 for r in rows:lines.append(f"| {r['checkpoint']} | {r['PART_ID']} | {r['TOKEN_ACC_TEACHER_FORCED']:.9f} | {r['EOS_ACC']:.6f} | {r['PRED_BLOCK_COUNT']}/{r['GT_BLOCK_COUNT']} | {r['SEQUENCE_EXACT_MATCH']} | {r['EOS_TERMINATED']} | {r['SAFETY_CAP_HIT']} | {r['CAD_PARSE_PASS']}/{r['CAD_EXECUTION_PASS']}/{r['STEP_EXPORT_PASS']} | {r['FIRST_DIVERGENCE_BLOCK']}/{r['FIRST_DIVERGENCE_TOKEN']} |")
 lines+=['','| Checkpoint | Macro mean token acc | Min token acc | EOS acc all | Strict Gate count |','|---|---:|---:|---:|---:|']
 for s in steps:
  v=read(EXP/f'evaluations/checkpoint-{s}/summary.json');lines.append(f"| {s} | {v['MEAN_TOKEN_ACC']:.9f} | {v['MIN_TOKEN_ACC']:.9f} | {v['EOS_ACC_ALL']:.6f} | {v['PART_GATE_PASS_N']}/3 |")
 lines+=['','每块通过 EOS 结束，完整程序必须由模型输出 `# CAD_COMPLETE`，最后仍要求自然 EOS。do_sample=False、num_beams=1、max_new_tokens=1280/块、64 blocks 安全上限；未按 GT 长度/块数截断，也没有删除多余 block。完整原始 token 数组（含每块 EOS）独立复核 exact。','','## 首次 PASS 与稳定性','',f'首次通过：{first}；紧接的保存 checkpoint：{confirmation}；连续两次严格 Gate 通过：{stable}。best 优先取首次严格通过，若没有通过则依次按通过数、exact 数、最低 TF accuracy、首次分叉位置选择。','', '## Token margin','', 'TOKEN_MARGIN = GT logit − 最强非 GT 竞争 token logit。SECOND_BEST 指相对 GT 的最强替代项；当 GT 为 top-1 时它也是全局第二名。错误 token 的 margin 可以为负。','', '| Part at best checkpoint | Min | P1 | P5 | Median | Worst block/token | GT / competitor |','|---|---:|---:|---:|---:|---|---|']
 for r in chosen:
  m=r['MIN_MARGIN_TOKEN'];lines.append(f"| {r['PART_ID']} | {r['MIN_TOKEN_MARGIN']:.6g} | {r['P1_TOKEN_MARGIN']:.6g} | {r['P5_TOKEN_MARGIN']:.6g} | {r['MEDIAN_TOKEN_MARGIN']:.6g} | {m['block']}/{m['token_in_block']} | {m['gt_token']!r} / {m['second_best_token']!r} |")
 lines+=['','所有 checkpoint 的统计见 token_margin_analysis.csv；每个监督 token 的 logit、概率、margin、NLL 见 teacher_tokens.jsonl.gz。正 margin 只证明本次确定性 teacher-forcing 的 top-1 领先，不等于对扰动稳健。','','## 实际训练曝光','','保持原 block 级 shuffled sampling，没有改成 part 均衡 sampler。一个训练 step 只监督一个 block。复杂零件 block 更多，因此 PART_EXPOSURES 不相等；完整程序等效次数用 block 曝光数除以该零件 block 数。单样本 500 steps 对 6 blocks，等效 83.333 次完整程序曝光，不能解释为每个 token 看过 500 次。','','| Checkpoint | Part | Block exposures | Full-program equivalents | Relative to single-500 |','|---|---|---:|---:|---:|']
 exposures=[]
 for s in steps:
  ex=read(EXP/f'audits/exposure_checkpoint-{s}.json')
  for p in PARTS:
   n=ex['part_exposures'].get(p,0);eq=n/BLOCKS[p];row={'checkpoint':s,'part':p,'block_exposures':n,'program_equivalent':eq,'single500_relative':eq/(500/6)};exposures.append(row);lines.append(f'| {s} | {p} | {n} | {eq:.4f} | {eq/(500/6):.4f} |')
 save(EXP/'audits/exposure_comparison.json',exposures)
 lines+=['','逐 block 曝光计数在 audits/exposure_checkpoint-*.json，可检查实际 sampler 覆盖与离散误差。','','## 失败诊断与原始证据','']
 lines+=['单样本 500-step 是曝光量参照，不是多样本成功所需的硬阈值。PART_000 在联合训练的 2000-step 已严格通过，说明曝光次数不能单独解释全部失败。','',f'单件 exact 回退记录：`{json.dumps(regressions,ensure_ascii=False)}`。这些单件回退不等于曾经达到过 3/3；本轮 3/3 稳定性只根据完整 Gate 单独判断。','']
 if 2000 in by and 3000 in by:
  aa=next(r for r in by[2000] if r['PART_ID']=='PART_000');bb=next(r for r in by[3000] if r['PART_ID']=='PART_000')
  lines+=[f"PART_000 的 GT sequence NLL 从 checkpoint-2000 的 {aa['GT_SEQUENCE_NLL']:.6f} 降到 checkpoint-3000 的 {bb['GT_SEQUENCE_NLL']:.6f}，但 raw token exact 从 {aa['SEQUENCE_EXACT_MATCH']} 变为 {bb['SEQUENCE_EXACT_MATCH']}，最小 margin 从 {aa['MIN_TOKEN_MARGIN']} 变为 {bb['MIN_TOKEN_MARGIN']}。平均损失改善不保证最薄弱 token 继续保持 top-1。固定分叉 token 的跨 checkpoint margin 轨迹见 divergence_token_margin_trajectory.csv。",'']
 for r in chosen:
  if not r['PART_GATE_PASS']:
   classification='MULTI_SAMPLE_ROLLOUT_INSTABILITY' if r['TOKEN_ACC_TEACHER_FORCED']>=.999 else 'MULTI_SAMPLE_MEMORIZATION_INCOMPLETE'
   lines+=[f"- {r['PART_ID']}: {classification}; blocks={r['GT_BLOCK_COUNT']}, tokens={r['GT_TOKEN_COUNT']}, mean NLL={r['MEAN_NLL']:.9g}, first divergence={r['FIRST_DIVERGENCE_BLOCK']}/{r['FIRST_DIVERGENCE_TOKEN']}, min margin={r['MIN_TOKEN_MARGIN']:.9g}.",f"  GT-prefix token diagnostics at divergence: `{json.dumps(r['DIVERGENCE_TEACHER_CONTEXT'],ensure_ascii=False)}`"]
 lines+=['','## 预算终点诊断','',f"最终 checkpoint-{steps[-1]}：{result['DIAGNOSIS_AT_FINAL_CHECKPOINT']}。该分类单独针对预算终点，不能与按完整 Gate 表现选择的 best checkpoint 混用。",'', '| Part | TF errors | TF token acc | Mean NLL | Free first divergence | Min margin | Exact |','|---|---:|---:|---:|---:|---:|---|']
 for r in latest:lines.append(f"| {r['PART_ID']} | {round((1-r['TOKEN_ACC_TEACHER_FORCED'])*r['GT_TOKEN_COUNT'])} | {r['TOKEN_ACC_TEACHER_FORCED']:.9f} | {r['MEAN_NLL']:.9g} | {r['FIRST_DIVERGENCE_TOKEN']} | {r['MIN_TOKEN_MARGIN']:.6g} | {r['SEQUENCE_EXACT_MATCH']} |")
 if all(s in by for s in [2000,2500,3000]):
  worst={s:min(by[s],key=lambda r:r['TOKEN_ACC_TEACHER_FORCED'])['PART_ID'] for s in [2000,2500,3000]}
  lines+=['',f'后期三个 checkpoint 的最低 TF accuracy 所属零件分别为 `{worst}`；最弱样本发生轮换，本轮不支持把失败统一归结为单一持续落后的 CASE_SPECIFIC_HARD_SAMPLE。','']
 lines+=['','接近 100% 的 TF accuracy 仍允许残余 token 错误；本报告不会把近满分描述为已经完全记忆。Case-specific hard sample 需跨 checkpoint 持续落后，不能只按程序最长或一次最早分叉判定。完整逐件轨迹保留在上表与 CSV 中。','','每个失败结果目录含 failure_diff_<part>_<checkpoint>.txt，展示首次分叉前后至少 ±30 tokens 及相邻完整 block。teacher_forced.json 记录 FIRST_WRONG_TOKEN、GT/top1 概率；result.json 记录全部 Gate 字段。首分叉处 TF 诊断基于 GT prefix；发生 cascade 后不得将其当作预测 prefix 下的概率。','', 'checkpoint_metrics.csv 提供完整逐件指标；evaluations/checkpoint-*/summary.json 提供每个 checkpoint 的固定分母汇总。可执行预测另有 metrics.json、prediction.step、原坐标 STEP。','', '本轮不启动 9-part 或 held-out benchmark。','']
 if (EXP/'audits/budget_decision.json').exists():lines+=['## 预算决定','', '```json',json.dumps(read(EXP/'audits/budget_decision.json'),indent=2,ensure_ascii=False),'```']
 lines+=['','## 评估恢复与 CAD 图','', '部分评估为调度 GPU 在 block 边界恢复：prefix 仅从该模型已保存的原始预测 token 重建，不使用 GT prefix。每次恢复都独立重放最后一个已保存 block，并要求原始 token 完全一致，见各结果目录的 resume_audit.jsonl。DECODE_SECONDS 是最终工作进程中的测量区间，不用于不同 checkpoint 的速度比较。','', 'CAD 对照图使用已导出的真实 STEP：p1_a2_checkpoint2000_cad_comparison.png 与 p1_a2_checkpoint3000_cad_comparison.png。上排为 GT，下排为对应 checkpoint 的实际预测；不可执行的程序明确显示无 CAD，不以 GT 代替。','', '下一轮建议仍限定这三个零件，优先检验降低学习率、增加梯度累积能否减少已通过样本的回退；当前证据尚不能确定干扰的唯一原因。本轮未执行这些新训练，也未启动 9-part Gate。','']
 changed_cases=sum(r['old_token_acc']!=r['argmax_token_acc'] for r in argmax_audit['records'])
 changed_top1=sum(len(r['top1_tie_changes']) for r in argmax_audit['records'])
 lines+=['','## Teacher-forcing 并列值核验','',f'TF top-1 统一采用 torch.argmax，与 greedy decoding 的并列规则一致。24 项在独立进程中从对应 checkpoint 重新加载、重置 seed 后复核；GT logits、最强竞争 logits、概率、margin 与 NLL 均与原始统计逐 token 完全一致。共 {changed_top1} 个 top-1 token ID 因并列值规则改变，{changed_cases} 项 accuracy 发生变化；全部 Gate 判定不变。原 topk 统计备份与逐项差异保留在 audits/argmax_teacher_verification/。自由生成文件 SHA256 前后一致，最终 checkpoint-3000 指标不变。','']
 (EXP/'P1_AIRPLANE3_EXACT_OVERFIT_REPORT.md').write_text('\n'.join(lines))
 zip_path=EXP/'p1_airplane3_exact_evidence.zip'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in EXP.rglob('*'):
   if not f.is_file() or f==zip_path or f==EXP/'status.json' or f==EXP/'evidence_manifest.json' or any(x in f.relative_to(EXP).parts for x in ['runs','cache','__pycache__','recomputed']):continue
   z.write(f,f.relative_to(EXP))
 status=read(EXP/'status.json');status.update(state='COMPLETE',P1_A2_GATE=gate,completed_case_evaluations=len(rows),best_checkpoint=f'checkpoint-{best}',gpu_reservations_restored=True);save(EXP/'status.json',status)
 save(EXP/'evidence_manifest.json',{'zip_file':zip_path.name,'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'checkpoint_n':len(steps),'case_evaluation_n':len(rows),'failure_diff_n':len(list((EXP/'evaluations').glob('checkpoint-*/PART_*/failure_diff_*.txt'))),'P1_A2_GATE':gate})
 print(json.dumps(result,indent=2));print('ZIP',zip_path,zip_path.stat().st_size)
if __name__=='__main__':main()
