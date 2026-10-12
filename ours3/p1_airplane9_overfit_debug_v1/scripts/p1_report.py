from pathlib import Path
import json,csv,hashlib,shutil,zipfile,time
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');D=ROOT/'ours3/p1_airplane9_overfit_debug_v1';O=ROOT/'ours3/p1_quick_overfit_airplane9_v1';S=ROOT/'ours3/p1_single_airplane_part_overfit_v1'
def read(p):return json.loads(Path(p).read_text())
def write(p,obj):Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False))
audit=read(D/'target_eos_audit.json');tf=read(D/'teacher_forced_case0.json');cfg=read(D/'generation_config_audit.json');all9=read(D/'teacher_all9_summary.json')
case=read(D/'case0/single_case_decode_diagnosis.json');checks=[read(D/f'single_checks/checkpoint-{n}/single_case_decode_diagnosis.json') for n in [100,200,500]]
for r in checks:
 r.update(SEQUENCE_EXACT_MATCH_RATE=float(r['SEQUENCE_EXACT_MATCH']),PARSE_PASS_RATE=float(r['PARSE_PASS']),EXEC_PASS_RATE=float(r['EXECUTION_PASS']),STEP_PASS_RATE=float(r['STEP_EXPORT_PASS']),TRAIN_CASE_N=1)
for f in ['single_case_decode_diagnosis.json','case0_block_diff.txt']:shutil.copy2(D/'case0'/f,D/f)
for folder in [D/'case0',*[D/f'single_checks/checkpoint-{n}' for n in [100,200,500]]]:
 gt=read(folder/'gt_token_sequence.json');pr=read(folder/'predicted_token_sequence.json')
 with (folder/'token_alignment.jsonl').open('w') as f:
  for bi in range(max(len(gt),len(pr))):
   g=gt[bi] if bi<len(gt) else [];p=pr[bi]['raw_generated_ids'] if bi<len(pr) else []
   for j in range(max(len(g),len(p))):
    a=g[j] if j<len(g) else None;b=p[j] if j<len(p) else None
    f.write(json.dumps({'block1':bi+1,'within_block_token1':j+1,'gt_id':a,'pred_id':b,'exact_match':a==b})+'\n')
fields=['TRAIN_STEP','TRAIN_LOSS','TOKEN_ACC','EOS_ACC','GT_BLOCK_COUNT','PRED_BLOCK_COUNT','SEQUENCE_EXACT_MATCH','BLOCK_EXACT_MATCH','BLOCK_EXACT_MATCH_RATE','PARSE_PASS','EXECUTION_PASS','STEP_EXPORT_PASS','SINGLE_PART_EXACT_OVERFIT','safety_cap_hit']
with (D/'single_checkpoint_metrics.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:r.get(k) for k in fields} for r in checks])
write(D/'single_checkpoint_metrics.json',checks)
# Verify frozen file contents after all diagnostics. No source experiment file may change.
manifest=read(D/'frozen_manifest.json');changed=[]
for r in manifest['files']:
 p=Path(r['path'])
 if not p.exists():changed.append({'path':str(p),'reason':'missing'});continue
 if p.stat().st_size!=r['size'] or p.stat().st_mtime_ns!=r['mtime_ns']:changed.append({'path':str(p),'reason':'stat changed'})
 if 'sha256' in r:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
  if h.hexdigest()!=r['sha256']:changed.append({'path':str(p),'reason':'hash changed'})
write(D/'freeze_verification.json',{'files':len(manifest['files']),'changed':changed,'PASS':not changed});assert not changed,changed
eos=tf['gt_final_eos'];passing=checks[-1];probe=read(D/'cache_ablation_block2.json');precision=read(D/'precision_probe/comparison.json');frozen=read(O/'decode/checkpoint-2000/summary.json')
summary={'PRIMARY_ROOT_CAUSE':'AUTOREGRESSIVE_ROLLOUT_FAILURE','SECONDARY_ISSUE':'No additional causal bug established; geometry dtype and cache-mask lengths differ, but the tested ablations reproduce the same initial error','AIRPLANE_PART_N':9,'CAD_BLOCK_N':134,'CHECKPOINT':'checkpoint-2000','REPORTED_TRAIN_MEMORIZATION_LOSS':.02148919180035591,'ACTUAL_RUN_AVG_TRAIN_LOSS':read(O/'runs/quick/train_results.json')['train_loss'],**audit['summary'],'TRAIN_EOS_ID':cfg['TRAIN_EOS_ID'],'GENERATION_EOS_ID':cfg['GENERATION_EOS_ID'],'EOS_ID_MATCH':cfg['EOS_ID_MATCH'],'TEACHER_FORCED_TOKEN_ACC':tf['token_acc'],'EOS_PROB_AT_GT_END':eos['probability'],'EOS_RANK_AT_GT_END':eos['rank'],'GT_BLOCK_COUNT_CASE0':6,'PRED_BLOCK_COUNT_CASE0':case['PRED_BLOCK_COUNT'],'FIRST_DIVERGENCE_TOKEN':case['FIRST_DIVERGENCE_TOKEN'],'FIRST_DIVERGENCE_BLOCK':case['FIRST_DIVERGENCE_BLOCK'],'FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN':case['FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN'],'DIAGNOSIS':'AUTOREGRESSIVE_ROLLOUT_FAILURE','SINGLE_PART_EXACT_OVERFIT':passing['SINGLE_PART_EXACT_OVERFIT'],'SINGLE_PART_PRED_BLOCK_COUNT':passing['PRED_BLOCK_COUNT'],'SINGLE_PART_EOS_ACC':passing['EOS_ACC'],'SINGLE_PART_SEQUENCE_EXACT':passing['SEQUENCE_EXACT_MATCH'],'NEXT_GATE':'A2: 3 airplane parts, require 3/3 exact free-decoding; not launched in this diagnosis','LIKELY_TERMINATION_SUPERVISION_FAILURE':'NO'}
summary['ROOT_CAUSE']=summary['PRIMARY_ROOT_CAUSE']
write(D/'diagnosis_summary.json',summary)
legacy={
 'TRAIN_CASE_N':9,'TOKEN_ACC':all9['TOKEN_ACC'],'EOS_ACC':all9['EOS_ACC'],
 'NEW_DIAGNOSTIC_FREE_EVALUATED_N':1,'FREE_UNEVALUATED_N':8,
 'BLOCK_COUNT_EXACT_N':f"{int(case['BLOCK_COUNT_EXACT_ACC'])}/9",'SEQUENCE_EXACT_N':f"{int(case['SEQUENCE_EXACT_MATCH'])}/9",'PARSE_PASS_N':f"{int(case['PARSE_PASS'])}/9",'EXEC_PASS_N':f"{int(case['EXECUTION_PASS'])}/9",'STEP_PASS_N':f"{int(case['STEP_EXPORT_PASS'])}/9",
 'denominator_note':'9 original parts retained. Numerators are confirmed successes from 1 newly evaluated part; remaining 8 NOT_EVALUATED, not counted as failures or silently removed. These are not complete 9-part free-decode accuracy estimates.',
 'original_frozen_free_decode':{k:v for k,v in frozen.items() if k!='results'}}
write(D/'airplane9_metric_summary.json',legacy)
lines=['# P1 airplane9 第一轮 overfit 严格诊断','',
'## 结论','',
'**PRIMARY_ROOT_CAUSE=C. AUTOREGRESSIVE_ROLLOUT_FAILURE**。原 airplane9 checkpoint-2000 并未实现逐 token 记忆。模型在第 2 个 block 内先写错坐标，错误前缀进入后续 block 后产生漂移；不是把正确的 6 个 block 写完才忘记 EOS。',
'',f"单样本实验的 **checkpoint-500 已通过 SINGLE_PART_EXACT_OVERFIT=PASS**：TOKEN_ACC=1.0、EOS_ACC=1.0、6/6 blocks 完全一致、5615/5615 生成 token（含各 block 的 EOS）一致，CAD 解析/执行/STEP 导出均通过。程序结束来自模型生成的 `# CAD_COMPLETE` 和 EOS，未使用 GT 长度或 block 数停止，也未修补预测。",'',
'## 实验冻结与范围','',
f'原目录：`{O}`。停止原 decoder 与最终状态监控后记录 SHA-256，诊断后复核 {len(manifest["files"])} 个文件无修改，详见 `frozen_manifest.json`、`freeze_verification.json`。未修改 checkpoint、原 prediction、log、GT 或原 evaluation result。',
'',f'独立诊断目录：`{D}`。单样本目录：`{S}`。训练继续使用原始 6 个 target block、同一 serializer、mesh/点云与曲线特征，没有更改目标程序。',
'', '本次是训练样本记忆测试。输入沿用原数据中的点云及 GT CAD 提取的曲线特征（oracle CAD curve inputs），不代表 held-out 泛化或从未知 mesh 重建的完整系统能力。',
'', '## loss 与 token 数口径','',
'历史字段 `TRAIN_LOSS=0.02149` 实际是 27 个训练集 block 的 eval memorization loss；全程平均 train loss 为 0.3872258。报告保留历史口径用于对照，但不将它误称为全 134 blocks 的最终训练误差。',
'',f"本次对全部 134 blocks 重新 teacher-force：TOKEN_ACC={all9['TOKEN_ACC']:.10f}，EOS_ACC={all9['EOS_ACC']:.1f}，总计 {all9['TOKEN_N']} 个有效 label，其中 {all9['TOKEN_N']-sum(r['CORRECT_N'] for r in all9['parts'])} 个 token 的 argmax 不等于 GT。",'',
'PART_000 原 inventory 的 full_target_tokens=5610 是整段程序字符串的分词口径；逐 block tokenization 后代码为 5609 tokens，另有 6 个受监督 block EOS，因此本诊断的 token denominator 为 5615。二者不混用。',
'','## Stage 1–3：EOS 与 label 证据','', '```text']
for k,v in audit['summary'].items():lines.append(f'{k}={v}')
lines+= [f"TRAIN_EOS_ID={cfg['TRAIN_EOS_ID']}",f"GENERATION_EOS_ID={cfg['GENERATION_EOS_ID']}",f"EOS_ID_MATCH={cfg['EOS_ID_MATCH']}",'```','',
'EOS 与 PAD 均为 `<|eot_id|>` / 128009。所有 9 个程序末 block 的 EOS label 均有效，134 个 block 也均有效；真正 padding 的 labels 是 -100。CSV/JSON 同时保存 BOS/PAD/EOS、末 30 个 token、EOS raw sequence position、label 值、最后有效 label、padding 起点。位置字段以 0 为起点。',
'','真实代码路径：`SpatialLM/spatiallm/tuner/data/collator.py::_encode_messages_example` 使用 `target_label = target_ids`；HF `DataCollatorForSeq2Seq.__call__` 为新增 padding 添加 -100，而不是按 `input_ids == pad_token_id` 全局抹除；`spatiallm/model/spatiallm_llama.py::_splice_labels` 只 mask 插入的几何位置与补齐位置。精确绝对路径、行号、源码和真实 input_ids/labels 见 `evidence/label_mask_and_generation_sources.json`、`evidence/actual_collator_case0.json`。',
'','训练 EOS 标量与推理 EOS 列表并非字面相等，但实际训练 token 128009 包含于推理停止集合 [128001,128008,128009]；因此 EOS 匹配含义为可被实际停止条件识别，不把列表多出的合法 token 误判为缺失 EOS。完整 runtime/saved/effective 配置见 `generation_config_audit.json`，有效 do_sample=False、num_beams=1、max_new_tokens=1280、use_cache=True。',
'','token EOS 结束一次 block 生成；`# CAD_COMPLETE` 结束整个 CAD program。**6 个训练 block 各自都有 EOS**，若把第一次 EOS 当成整程序结束，会人为只生成 1 个 block。本次保留原协议，不使用 GT block count；同时保存每个 block 的原始生成 token、EOS 位置和结束原因。',
'','## Stage 4：PART_000 teacher-forced 结果','',f"TOKEN_ACC={tf['token_acc']:.10f}; BLOCK_TOKEN_ACC="+str([r['token_acc'] for r in tf['blocks']]),f"STRUCTURE_CONTROL_TOKEN_ACC={tf['structure_control_token_acc']:.10f}; EOS_ACC={tf['eos_acc']}; SEQUENCE_NLL={tf['sequence_nll']:.10f}; MEAN_NLL={tf['mean_nll']:.10f}",
'','structure/control 定义：包含 ASCII 字母、语法标点、换行或 EOS 的 token。每个 GT token 的概率、NLL、预测 token 与对错均保存在 `teacher_forced_case0.json`。','', '```text',f"GT_EOS_POSITION=block 6; raw sequence index0 {eos['raw_sequence_position0']}; geometry-expanded index0 {eos['expanded_sequence_position0']}",f"GT_EOS_TOKEN={eos['gt_token']}",f"EOS_PROBABILITY={eos['probability']:.12f}",f"EOS_RANK={eos['rank']}"]
for j,r in enumerate(eos['top3'],1):lines += [f"TOP{j}_TOKEN={json.dumps(r['token'])}",f"TOP{j}_PROBABILITY={r['probability']:.12f}"]
lines+=['LIKELY_TERMINATION_SUPERVISION_FAILURE=NO','```','',
'首个 teacher-forced 错误在 block 2、第 98 个 token：GT=`33`，top-1=`32`，GT 概率约 0.16361。最终 EOS 的高概率是在完整正确 GT 前缀下得到的，不能推导出漂移前缀下也会正确结束。',
'','## Stage 5–6：真实自由解码与首次分叉','',f"新诊断生成 {case['PRED_BLOCK_COUNT']} blocks；安全 cap={case['max_generated_blocks']}，cap_hit={case['safety_cap_hit']}，自然程序结束={case['program_end_predicted']}。cap 到达只记为失败/未结束，不算正常完成。",'',
f"FIRST_DIVERGENCE_TOKEN={case['FIRST_DIVERGENCE_TOKEN']}（1-based，计入 block EOS）; FIRST_DIVERGENCE_BLOCK={case['FIRST_DIVERGENCE_BLOCK']}; WITHIN_BLOCK_TOKEN={case['FIRST_DIVERGENCE_WITHIN_BLOCK_TOKEN']}。第 1 个 block 一致；第 2 个 block 坐标中的 `[-33.09263, ...]` 首先变为 `[-32.09263, ...]`。这与 teacher-forced 首错相同。",'',
'逐 block 原始 GT/pred 和逐 token 原始 ID 全量保存。`case0_block_diff.txt` 展示前 10 个 block（第 7–10 个无 GT）；`case0/token_alignment.jsonl` 按 block 内位置逐 token 对照，缺失侧为 null，未删除任何多余 token。',
'','## 排除性检查：精度和缓存','',
'134 个训练/推理文本 prompt 的 token 序列相同。另观察到 collator 几何输入是 BF16、独立 decoder 是 FP32，且 cached generation 的原 attention mask 长度与几何展开后的 KV 长度不同。没有据此直接改代码或宣布 bug。',
'', '对原 checkpoint 的 block 2，用原 cache、无 cache、仅实例内对齐 cache mask 三种方式各生成 128 tokens：首次错误 token0 分别为 '+str({k:v['first_divergence_token0'] for k,v in probe['results'].items()})+'；均仍在原坐标位置分叉。单样本 checkpoint-100 将 teacher-forcing 几何替换为实际推理 FP32 输入后，准确率与首错不变。证据见 `cache_ablation_block2.json`、`geometry_input_precision_audit.json`、`precision_probe/comparison.json`。',
'','这些控制只支持“本次观察到的首错并未被上述变更消除”，不等于证明所有长序列或其他样本都不存在缓存/精度风险。本报告没有部署这些实验性改动。',
'','## Stage 7–9：单样本 exact-overfit Gate','',
'从与原 9-part 实验相同的 checkpoint-8000 初始化，只用 PART_000 的原始 6 个 block。保存并评估 100、200、500 steps。100-step 的高 token 准确率仍留下 5 个错误 token，因此不满足 exact gate；按 Stage 9 暂停追加训练并完成 EOS/输入/缓存审计。暂停时已存在 checkpoint-500，随后其原始自由解码通过全部 Gate，因此结束训练，未继续保存 1000/2000 steps。这两个更晚 checkpoint 不存在，不报告为已测。',
'','| Checkpoint | Train loss（日志四位小数） | TF token acc | EOS acc | Pred blocks | Token/Block exact | Parse/Exec/STEP | Gate |','|---|---:|---:|---:|---:|---|---|---|']
for r in checks:
 lines.append(f"| {r['TRAIN_STEP']} | {r['TRAIN_LOSS']} | {r['TOKEN_ACC']:.8f} | {r['EOS_ACC']:.1f} | {r['PRED_BLOCK_COUNT']} | {r['SEQUENCE_EXACT_MATCH']}/{r['BLOCK_EXACT_MATCH']} | {r['PARSE_PASS']}/{r['EXECUTION_PASS']}/{r['STEP_EXPORT_PASS']} | {r['SINGLE_PART_EXACT_OVERFIT']} |")
lines+=['',f"checkpoint-500 的日志 train loss 被四舍五入为 0.0，**不是数学上的零损失**；独立 teacher-forcing mean NLL={passing['TEACHER_NLL']:.10g}。训练侧 eval loss=2.110361856466625e-05。",'',
f"通过 checkpoint：`{S/'runs/quick/checkpoint-500'}`。新 checkpoint 实际存储于 `runs` 符号链接所指向的 `/tmp` 专用目录（因为 /data 当时仅余约 29 GiB），路径与存储说明见 `{S/'audits/setup.json'}`。长期保存时需将此专用 checkpoint 目录迁移至有空间的持久卷。",'',
'真实模型 STEP：`single_checks/checkpoint-500/prediction.step`；原坐标版本：`single_checks/checkpoint-500/prediction_original_coordinates.step`。两者均由原始 prediction.py 执行导出，未使用 GT program 替换。',
'','## Stage 11：保持原分母的指标','', '```text']
for k,v in legacy.items():
 if k not in ['denominator_note','original_frozen_free_decode']:lines.append(f'{k}={v}')
lines+=['```','',legacy['denominator_note'],'',f"冻结前原任务累计完成 {frozen['evaluated']}/9；这份旧快照保留在原目录，未用它代替本轮 1-case 诊断。新的完整 9-part free-decode 准确率为 NOT_MEASURED，8 个未重测样本不被宣称成功或失败。",'',
'','## 最终机器可读结论','', '```text','TRAIN_LOSS=0.02149  # 历史字段：实际为27-block memorization eval loss，不是全程平均train loss']
for k,v in summary.items():lines.append(f'{k}={v}')
lines+=['```','', '## 下一道 Gate','',
'A1 已通过。下一步为 A2：固定 3 个 airplane parts，要求 3/3 自由生成逐 token/逐 block exact match 且解析、执行、STEP 全通过；之后才允许回到 A3 的 9 parts/134 blocks。此次诊断没有启动 3-part 或重训 9-part。',
'', '主要复现入口：`scripts/p1_debug_runtime.py audit`、`scripts/p1_debug_runtime.py teacher`、`scripts/p1_evaluate_debug.py --checkpoint ... --out <new_directory> --teacher`。所有生成使用 greedy、每 block 1280-token cap、整程序 64-block 安全 cap，成功要求模型预测 END 与 EOS 且全序列一致。复现请选择新目录，保留本轮证据。','']
(D/'P1_AIRPLANE_OVERFIT_DEBUG_REPORT.md').write_text('\n'.join(lines))
print(json.dumps(summary,indent=2),flush=True)
print('REPORT',D/'P1_AIRPLANE_OVERFIT_DEBUG_REPORT.md')
