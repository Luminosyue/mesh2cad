from pathlib import Path
import json,gzip,hashlib,zipfile,time,csv,statistics
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1';parts=['PART_000','PART_001','PART_005'];read=lambda p:json.loads(p.read_text())
rows=[]
for step in [2000,3000]:
 for p in parts:
  r=read(OLD/f'evaluations/checkpoint-{step}/{p}/result.json');rows.append({'experiment':f'original-{step}','part':p,'checkpoint':str(OLD/f'runs/quick/checkpoint-{step}'),'TF_errors':round((1-r['TOKEN_ACC_TEACHER_FORCED'])*r['GT_TOKEN_COUNT']),'first_divergence':r['FIRST_DIVERGENCE_TOKEN'],'blocks':f"{r['PRED_BLOCK_COUNT']}/{r['GT_BLOCK_COUNT']}",'raw_exact':r['SEQUENCE_EXACT_MATCH'],'END_EOS':r['EOS_TERMINATED'],'CAD_exec':r['CAD_EXECUTION_PASS'],'STEP_export':r['STEP_EXPORT_PASS'],'STEP_readback':'not measured in old run','complete':True})
for directory in sorted((E/'evaluations').iterdir()):
 if not directory.is_dir():continue
 for p in parts:
  folder=directory/p
  if (folder/'result.json').exists():
   r=read(folder/'result.json');rows.append({'experiment':directory.name,'part':p,'checkpoint':r['checkpoint'],'TF_errors':r['TOKEN_ERRORS'],'first_divergence':r['FIRST_DIVERGENCE_TOKEN'],'blocks':f"{r['PRED_BLOCK_COUNT']}/{r['GT_BLOCK_COUNT']}",'raw_exact':r['SEQUENCE_EXACT_MATCH'],'END_EOS':r['EOS_TERMINATED'],'CAD_exec':r['CAD_EXECUTION_PASS'],'STEP_export':r['STEP_EXPORT_PASS'],'STEP_readback':r['STEP_READBACK_PASS'],'complete':True})
  elif (folder/'teacher_forced.json').exists():
   tf=read(folder/'teacher_forced.json');traces=read(folder/'predicted_tokens.json') if (folder/'predicted_tokens.json').exists() else [];pred=sum((r['token_ids'] for r in traces),[]);gt=read(OLD/'audits/gt_supervised_tokens_for_status.json')[p];div=next((i+1 for i,(a,b) in enumerate(zip(gt,pred)) if a!=b),None)
   rows.append({'experiment':directory.name,'part':p,'checkpoint':'see run config','TF_errors':tf['TOKEN_ERRORS'],'first_divergence':div,'blocks':f'{len(traces)}/unfinished','raw_exact':False if div else 'unknown','END_EOS':'unknown','CAD_exec':'not completed','STEP_export':'not completed','STEP_readback':'not completed','complete':False})
with (E/'fast_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
error_history={}
for f in (E/'evaluations').glob('*/PART_*/teacher_tokens.jsonl.gz'):
 tag=f.parent.parent.name;p=f.parent.name
 with gzip.open(f,'rt') as z:
  for line in z:
   r=json.loads(line)
   if not r['CORRECT']:error_history.setdefault(f"{p}/{r['block']}/{r['token_in_block']}",[]).append({'evaluation':tag,'gt_token':r['gt_token'],'prediction':r['top1_token'],'margin':r['TOKEN_MARGIN'],'gt_id':r['gt_id'],'pred_id':r['top1_id']})
(E/'token_error_trajectory.json').write_text(json.dumps(error_history,indent=2,ensure_ascii=False))
frozen=read(E/'audits/frozen_sources.json');assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in frozen.items())
best=read(E/'best_checkpoint.json') if (E/'best_checkpoint.json').exists() else None;gate='PASS' if best and best['gate_n']==3 else 'FAIL';path=read(E/'diagnostics/path_gate.json')
lines=['# DEBUG_MULTI_SAMPLE_MEMORIZATION_FAST','',f'**FAST_GATE={gate}**',f'BEST_CHECKPOINT={best["checkpoint"] if best else "none completed"}',f'BEST_EVALUATION={best["tag"] if best else "none"}',f'NEXT_GATE={"AIRPLANE_9_PART_ELIGIBLE" if gate=="PASS" else "DEBUG_MULTI_SAMPLE_MEMORIZATION"}','', '## 执行边界','', '原有 24 项评估全部复用，未重跑。仅对修正推理后的 checkpoint-2000 做新的三件完整复评；该复评完成前没有追加训练。GT、词表、EOS/PAD、serializer、block grammar、几何源文件、executor 均保持冻结，SHA256 复核通过。','', '诊断预算 20 分钟；新增训练最多 300 次 optimizer updates、训练总预算 20 分钟；完整评估总墙钟预算 60 分钟。首轮低学习率 150 updates，保留 150 次给有证据支持的单因素加权尝试。预算中止的结果标为未完成，不能算通过。','', '## 诊断结论','', '训练 collator 的几何输入为 BF16，旧推理为 FP32。现推理先转为训练输入 dtype，确保送入 point backbone 的数值一致；源 mesh 和 curve 文件没有修改。BF16 decoder 的 cache 开关会改变舍入，PART_005 自由生成第 1200 token 出现 163/812 并列差异。这发生在原始首分叉 981 之后，不能解释或抹去原先的首错。','', f'关闭 TF32、改用 FP32 decoder/lm_head 后，核验位置的同前缀 logits 最大差异为 {path["same_prefix_FP32_max_diff"]:.8g}，argmax 一致。三件首块 use_cache=True/False 的全部生成 token 分别一致；这是首块诊断，不冒充整件 Gate。三件 END/EOS 末尾附近另做了同 GT 前缀逐 token 检查。','', '完整训练前向、无 cache 前缀前向、逐 token cache 推理均保留 logit 向量。完整目标 43680 tokens 含每块 EOS 参与 loss；prompt 的最近 384-token suffix 是原协议，两条路径一致；目标未截断，最大 collated length 小于 4096。','', '## 对照表','', '| Experiment | Part | TF errors | First divergence | Pred/GT blocks | Raw exact | END+EOS | CAD | STEP | STEP readback | Complete |','|---|---|---:|---:|---|---|---|---|---|---|---|']
for r in rows:lines.append('| '+' | '.join(str(r[k]) for k in ['experiment','part','TF_errors','first_divergence','blocks','raw_exact','END_EOS','CAD_exec','STEP_export','STEP_readback','complete'])+' |')
lines+=['','## 最佳点及训练','', '排序固定为 free-decoding raw exact 数 → CAD 执行且 STEP 回读成功数 → TF 错误数越少越好。只将三件均完成完整评估的 checkpoint 纳入排名，最后一步不自动视为最佳。','', '```json',json.dumps(best,indent=2,ensure_ascii=False),'```','', '低学习率阶段从原 checkpoint-2000 加载全部权重，AdamW 使用原配置和新状态（该 checkpoint 没有 optimizer state；未混用 checkpoint-3000 状态）。学习率 1e-5 constant；batch=1、梯度累积=3，每个 update 恰好一个 block 来自每件；part 内固定种子循环覆盖所有 blocks；seed=42，随机增强/旋转关闭。三件 block 采样等频，完整程序等效曝光因 6/13/25 blocks 而不同，曝光记录见 audits。','', '## 重复错误位置','', '| Part/block/token | Evaluation | GT | Prediction | Margin |','|---|---|---|---|---:|']
for key,history in error_history.items():
 if len(history)<2:continue
 for r in history:lines.append(f"| {key} | {r['evaluation']} | {r['gt_token']!r} | {r['prediction']!r} | {r['margin']:.6g} |")
if not any(len(v)>=2 for v in error_history.values()):lines+=['| 无重复错误位置 | — | — | — | — |']
lines+=['','完整错误轨迹见 token_error_trajectory.json；同前缀 GT 诊断数据仅用于定位和训练 loss，全部 Gate 自由生成从空程序开始、只使用模型自身已经生成的 block。未替换预测 token，未强制插入 END/EOS，也未依赖 GT 长度停止。','']
if (E/'audits/weighted_trial_decision.json').exists():lines+=['## 加权决策','','```json',json.dumps(read(E/'audits/weighted_trial_decision.json'),indent=2,ensure_ascii=False),'```']
lines+=['','EOS 审计：训练标签与 tokenizer EOS/PAD 均为 128009；原 generation_config 接受 [128001, 128008, 128009]，本轮保留该配置。没有 forced_eos、forced_bos、min-length 或 token suppression。即使生成其他终止 ID，也必须满足完整原始 token exact 才能通过，因此不会把替代 EOS 当作 exact。','']
if (E/'status.json').exists():lines+=['## 运行结束状态','','```json',json.dumps(read(E/'status.json'),indent=2),'```']
if best:
 lines+=['','## 最佳模型复现','', '下面命令通过本轮实际使用的评估入口，从空程序开始自由生成；替换 PART_000 为 PART_001/PART_005 可分别复现另外两件。使用新的输出 tag 避免复用已有结果。','', '```bash',f"CUDA_VISIBLE_DEVICES=1 /usr/bin/python3 {E}/launch/fast_evaluate.py {best['checkpoint']} PART_000 reproduce_best",'```','', '本轮没有增加 token 位置或 END/EOS 权重，除非 audits/weighted_trial_decision.json 明确记录已运行的加权试验。低学习率、三件等频与梯度累积共同构成这一短程配置；没有做独立消融，不能将成功唯一归因于其中某一个因素。','']
(E/'DEBUG_MULTI_SAMPLE_MEMORIZATION_FAST_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
zpath=E/'debug_multi_sample_fast_evidence.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in E.rglob('*'):
  if not f.is_file() or f==zpath or f.name=='evidence_manifest.json' or any(x in f.relative_to(E).parts for x in ['runs','data','__pycache__']):continue
  z.write(f,f.relative_to(E))
(E/'evidence_manifest.json').write_text(json.dumps({'sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'bytes':zpath.stat().st_size,'FAST_GATE':gate,'best':best,'frozen_sources_pass':True},indent=2))
print('REPORT_COMPLETE',gate,best,flush=True)
