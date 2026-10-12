import csv
import json
from pathlib import Path
from statistics import mean, median
import numpy as np

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EXP = ROOT / 'ours3/p3_xpart_20case_v3_joint_overfit_v1'
OUT = EXP / 'paper_export'
for d in ['tables','figures','captions','numbers','latex','markdown']:
    (OUT/d).mkdir(parents=True, exist_ok=True)
manifest = json.loads((EXP/'manifests/CASE_MANIFEST_FROZEN.json').read_text())
scans = sorted((EXP/'tf_eval').glob('TF_SCAN_*.json'))
traj = []
for p in scans:
    rows = json.loads(p.read_text())
    traj.append({'UPDATE': int(p.stem.split('_')[-1]), 'TOTAL_ERRORS': sum(x['tf_error_n'] for x in rows), 'ZERO_ERROR_CASE_N': sum(x['tf_error_n']==0 for x in rows), 'MAX_CASE_ERROR': max(x['tf_error_n'] for x in rows)})
traj.sort(key=lambda x:x['UPDATE'])
rows = json.loads((EXP/'tf_eval/TF_SCAN_0640.json').read_text())
target = np.array([x['tf_supervised_token_n'] for x in rows])
full = np.array([x['full_sequence_token_n'] for x in rows])
def st(a): return {'mean':float(mean(a)), 'median':float(median(a)), 'p90':float(np.percentile(a,90)), 'p95':float(np.percentile(a,95)), 'max':int(max(a)), 'min':int(min(a))}
nums = {'target_token':st(target), 'full_sequence_token':st(full), 'v1_max_full_sequence':30992, 'v3_max_full_sequence':int(max(full)), 'v1_to_v3_max_reduction_percent':float((30992-max(full))/30992*100), 'context_cap':16384}
(OUT/'numbers/V3_TOKEN_STATS.json').write_text(json.dumps(nums,indent=2)+'\n')
with (OUT/'tables/fullseq_learnability.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['Setting','Cases','Objects','TF Exact','Free Exact','Natural EOS','CAD/BRep','STEP','Geometry Exact','Max Full Seq','Context']); w.writerow(['Airplane9',9,9,'9/9','9/9','9/9','9/9','9/9','9/9','--',16384]); w.writerow(['New-object Demo5',5,5,'5/5','5/5','5/5','5/5','5/5','5/5',6238,16384]); w.writerow(['New-object 20-case',20,20,'15/20','Pending','Pending','Pending','Pending','Pending',int(max(full)),16384])
with (OUT/'tables/compact_ir_compression.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['Metric','Compact IR V1','Compact IR V3','Reduction']); w.writerow(['Max full sequence tokens',30992,int(max(full)),f"{nums['v1_to_v3_max_reduction_percent']:.2f}%"])
with (OUT/'tables/quantization_validity.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['Bit precision','Valid cases']); [w.writerow([b,v]) for b,v in [(8,'3/54'),(10,'18/54'),(12,'37/54'),(14,'45/54'),(16,'45/54')]]
(OUT/'latex/fullseq_learnability.tex').write_text('\\begin{tabular}{lrrrrrrrrr}\nSetting & Cases & Objects & TF & Free & EOS & CAD/BRep & STEP & Geometry & Max seq \\\\\n\\hline\nAirplane9 & 9 & 9 & 9/9 & 9/9 & 9/9 & 9/9 & 9/9 & 9/9 & -- \\\\\nDemo5 & 5 & 5 & 5/5 & 5/5 & 5/5 & 5/5 & 5/5 & 5/5 & 6238 \\\\\n20-case & 20 & 20 & 15/20 & Pending & Pending & Pending & Pending & Pending & '+str(int(max(full)))+' \\\\\n\\end{tabular}\n')
with (EXP/'tf_eval/TF_ERROR_TRAJECTORY.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['UPDATE','TOTAL_ERRORS','ZERO_ERROR_CASE_N','MAX_CASE_ERROR']); [w.writerow([x['UPDATE'],x['TOTAL_ERRORS'],x['ZERO_ERROR_CASE_N'],x['MAX_CASE_ERROR']]) for x in traj]
(OUT/'CLAIM_BOUNDARY.md').write_text('# Claim Boundary\n\nEstablished: Compact IR V3 correctness on the frozen 20-case canonical set; exact full-sequence memorization for Airplane9 (9/9) and Demo5 (5/5); 20-case TF memorization reached 15/20 zero-error cases at update 640.\n\nNot established: 20-case free-generation or full-pipeline exactness (not run because 20/20 TF was not reached); held-out generalization; unseen-mesh-to-CAD generalization; end-to-end predicted curve extraction; global q14 safety; large-scale 10k generalization.\n')
red=nums['v1_to_v3_max_reduction_percent']; mx=int(max(full))
(OUT/'captions/results_paragraph_en.txt').write_text(f'Compact IR V3 reduces the maximum observed full-sequence length from 30,992 tokens in V1 to {mx} tokens ({red:.2f}% reduction). Airplane9 and Demo5 reach exact full-sequence memorization with natural EOS and executable STEP reconstruction. The joint 20-object run reaches 15/20 teacher-forced zero-error cases and 6 residual errors at update 640; the 20-case free-generation gate remains pending.\n')
(OUT/'captions/results_summary_zh.txt').write_text(f'Compact IR V3 全序列最大长度由 V1 的 30992 降至 {mx}，降幅 {red:.2f}%。Airplane9 为 9/9，Demo5 为 5/5，均达到完整序列记忆、自然 EOS 和可执行 STEP。20-case 联合记忆在 update 640 达到 TF zero 15/20、总剩余误差 6；因未达到 20/20，正式 free generation 和后续 CAD/STEP/geometry gate 保持 Pending。\n')
report = '# P3_XPART_20CASE_V3_JOINT_OVERFIT_FINAL\n\nThis is a joint memorization / learnability experiment across 20 diverse object cases, not a held-out generalization evaluation.\n\nTraining used Demo5 frozen model weights only, a new standard AdamW optimizer, LR 5e-6, context 16384, dynamic sequence length, micro-batch 1, SDPA, cache disabled, gradient checkpointing, and balanced round-robin sampling. Warm-start 20-case TF audit: 54,241 errors, 0/20 zero-error cases.\n\nTF trajectory: '+json.dumps(traj)+'\n\nAt update 640: total errors = 6, zero-error cases = 15/20, maximum case error = 2. The 20/20 TF gate was not reached.\n\n20-case free generation, natural EOS, generated-IR parser/compiler, CAD/BRep, STEP readback, and geometry comparison were not run because the required 20/20 TF gate was not reached.\n\nTarget token mean / median / P95 / max: '+f"{nums['target_token']['mean']:.2f} / {nums['target_token']['median']:.2f} / {nums['target_token']['p95']:.2f} / {nums['target_token']['max']}"+'\n\nFull-sequence token mean / median / P95 / max: '+f"{nums['full_sequence_token']['mean']:.2f} / {nums['full_sequence_token']['median']:.2f} / {nums['full_sequence_token']['p95']:.2f} / {nums['full_sequence_token']['max']}"+f'\n\nV1 to V3 maximum reduction: {red:.2f}%\n\nManifest SHA256: 8e9886566f1080c7cb11a4dda259a1c4b397d6e2e42928679d1269e2ee8de481\n\nP3_XPART_20CASE_MODEL_EXACT_PASS=FALSE\nP3_XPART_20CASE_FULL_PIPELINE_PASS=FALSE\nPAPER_20CASE_RESULT_READY=NO\nPAPER_CORE_DEMO_READY=YES\n'
(EXP/'reports/P3_XPART_20CASE_V3_JOINT_OVERFIT_FINAL.md').write_text(report)
art=sorted(str(p.relative_to(EXP)) for p in OUT.rglob('*') if p.is_file())
(EXP/'reports/PAPER_EXPORT_MANIFEST.md').write_text('# Paper Export Manifest\n\n'+json.dumps({'experiment':'P3_XPART_20CASE_V3_JOINT_OVERFIT_AND_PAPER_EXPORT_V1','source_experiment':str(EXP),'status':'20-case TF incomplete; core Airplane9 and Demo5 results ready','artifacts':art,'tf_scans':[str(p.relative_to(EXP)) for p in scans]+['tf_eval/INITIAL_20CASE_TF.json']},indent=2)+'\n')
print(json.dumps(nums,indent=2))
