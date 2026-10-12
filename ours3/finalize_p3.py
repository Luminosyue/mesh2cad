import json,csv,statistics,shutil
from pathlib import Path
EXP=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_20case_compact_ir_v1')
man=json.loads((EXP/'CASE_MANIFEST.json').read_text())
rows=list(csv.DictReader((EXP/'token_audit/PER_CASE_TOKEN_STATS.csv').open()))
for r in rows:
    for k in ['RAW_TOKEN_N','COMPACT_TOKEN_N','REDUCTION_PERCENT','FULL_SEQUENCE_TOKEN_N','TARGET_TOKEN_N','CONDITIONING_TOKEN_N']:
        r[k]=float(r[k])
rows.sort(key=lambda x:x['COMPACT_TOKEN_N'],reverse=True)
longest=rows[:5]
(EXP/'reports/TOP5_LONGEST_CASES.json').write_text(json.dumps(longest,indent=2))
g=json.loads((EXP/'reports/P3_XPART_20CASE_DATA_PREPARATION.json').read_text())
tf=json.loads((EXP/'eval/initial_tf.json').read_text())
status={'experiment':'P3_XPART_20CASE_COMPACT_IR_FULLSEQ_OVERFIT_V1','requested_case_n':20,'trainable_case_n':20,
 'warm_start_checkpoint':'/data/home/cuiyuehan/project/mesh2cad/ours3/airplane3_fullseq_14bit_ir_v1/runs/fast_refinement_v2_step80/checkpoint-40',
 'context_policy':{'max_full_sequence':max(x['FULL_SEQUENCE_TOKEN_N'] for x in rows),'safety_margin':0.05,'recommended_context':32768},
 'full_parameter_run':{'status':'OOM','failed_at_update':3,'gpu':'NVIDIA L20 46GB','log':'logs/train.log'},
 'frozen_language_fallback':{'status':'OOM','failed_at_update':0,'log':'logs/train_fallback.log'},
 'teacher_forced_init':{'zero_error_case_n':tf['ZERO_ERROR_CASE_N'],'total_errors':tf['TOTAL_ERRORS']},
 'free_generation':{'status':'NOT_RUN','reason':'requires 20/20 teacher-forced exact'},
 'generated_cad_step':{'status':'NOT_RUN','reason':'free generation gate not reached'},
 'ground_truth_compact_ir_step':{'pass_n':20}}
(EXP/'training/status.json').write_text(json.dumps(status,indent=2))
red=statistics.mean(x['REDUCTION_PERCENT'] for x in rows); med=statistics.median(x['REDUCTION_PERCENT'] for x in rows)
md=f'''# P3 X-Part 20-case full-sequence overfit\n\n## Configuration\n\n- Requested and frozen cases: **20** (one watertight part per sample, 20 different objects).\n- Initialization: Airplane3 full-sequence warm start, model weights loaded from `{status['warm_start_checkpoint']}`; optimizer, scheduler and global step were new.\n- Target: NEW20 only.\n- Context: max audited full sequence `{status['context_policy']['max_full_sequence']}`; 5% margin selects **32768** from the required candidates.\n- Learning rate: `5e-6`; micro batch `1`; gradient accumulation `1`; checkpoints requested at `20,40,80,160,320` updates.\n\n## Data gates\n\nRaw CAD, 14-bit dequantized CAD, Compact IR round-trip, Compact IR compiler, and STEP readback each passed **20/20**.\n\n## Token audit\n\nMean raw-to-compact reduction is **{red:.2f}%**, median **{med:.2f}%**. The five longest compact targets are `{', '.join(x['CASE_ID'] for x in longest)}`; the longest full sequence is `{max(x['FULL_SEQUENCE_TOKEN_N'] for x in rows)}` tokens.\n\n## Training result\n\nThe requested full-parameter run reached update 3 and stopped with CUDA out-of-memory during the backward pass on a roughly 30k-token sample. A second run freezing the language tower still stopped at update 0 because the full-sequence attention allocation exceeded the 46 GB GPU. No valid training checkpoint was produced. These failures are retained in `logs/train.log` and `logs/train_fallback.log`; no case or long sequence was truncated.\n\nThe teacher-forced scan at the warm-start model (step 0) completed for all 20 cases: **{tf['ZERO_ERROR_CASE_N']}/20** exact, **{tf['TOTAL_ERRORS']}** total token errors. Because the 20/20 TF gate was not reached, free generation and generated-CAD gates were not run.\n\nGround-truth Compact IR compilation and STEP readback remain **20/20**.\n'''
(EXP/'reports/P3_XPART_20CASE_FULLSEQ_OVERFIT.md').write_text(md)
prep=EXP/'reports/P3_XPART_20CASE_DATA_PREPARATION.md'
prep.write_text(prep.read_text()+'\n\n## Per-case token audit\n\n| CASE | Raw | Compact | Reduction | Full sequence |\n|---|---:|---:|---:|---:|\n'+'\n'.join(f"| {x['CASE_ID']} | {int(x['RAW_TOKEN_N'])} | {int(x['COMPACT_TOKEN_N'])} | {x['REDUCTION_PERCENT']:.2f}% | {int(x['FULL_SEQUENCE_TOKEN_N'])} |" for x in sorted(rows,key=lambda x:x['CASE_ID']))+'\n')
print(json.dumps(status,indent=2))
