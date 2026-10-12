#!/usr/bin/env python3
"""Read-only inspection of saved M2 train-self-decode metrics; no generation."""
from __future__ import annotations
import csv, json, statistics
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
RUN=ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1'
OUT=RUN/'epoch20_result_inspection'
OUT.mkdir(exist_ok=True)
report=json.loads((RUN/'TRAINING_REPORT.json').read_text())
curve=report['curve']; n=report['train_count']

fields=['epoch','train_ce','self_decode_ce','eos_count','runaway_count','parse_count','op_f1']
table=[]
for x in curve:
    table.append({'epoch':x['epoch'],'train_ce':x['train_ce'],'self_decode_ce':x['dev_ce'],
                  'eos_count':x['eos_n'],'runaway_count':x['unexpected_runaway_n'],
                  'parse_count':x['dsl_parse_n'],'op_f1':x['mean_op_f1']})
with (OUT/'M2_TRAINING_CURVE.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(table)
lines=['# M2 TRAIN SELF-DECODE curve','',f'Rows per epoch: {n}. These are train688 self-decode metrics, not held-out results.','',
       '| epoch | train CE | self-decode CE | EOS | runaway | parse | Op F1 |','|---:|---:|---:|---:|---:|---:|---:|']
lines += [f"| {x['epoch']} | {x['train_ce']:.6f} | {x['self_decode_ce']:.6f} | {x['eos_count']}/{n} | {x['runaway_count']}/{n} | {x['parse_count']}/{n} | {x['op_f1']:.6f} |" for x in table]
(OUT/'M2_TRAINING_CURVE.md').write_text('\n'.join(lines)+'\n')

ep=[x['epoch'] for x in table]
fig,ax=plt.subplots(1,3,figsize=(15,4))
ax[0].plot(ep,[x['train_ce'] for x in table],label='train CE');ax[0].plot(ep,[x['self_decode_ce'] for x in table],label='self-decode CE');ax[0].set(xlabel='epoch',ylabel='CE');ax[0].legend();ax[0].grid()
ax[1].plot(ep,[x['eos_count']/n for x in table],label='EOS rate');ax[1].plot(ep,[x['parse_count']/n for x in table],label='parse rate');ax[1].plot(ep,[x['runaway_count']/n for x in table],label='runaway rate');ax[1].set(xlabel='epoch',ylabel='rate');ax[1].legend();ax[1].grid()
ax[2].plot(ep,[x['op_f1'] for x in table],label='Op F1');ax[2].set(xlabel='epoch',ylabel='Op F1');ax[2].grid()
fig.suptitle('M2 train688 self-decode only');fig.tight_layout();fig.savefig(OUT/'M2_TRAINING_CURVE.png',dpi=180);plt.close(fig)

rows=[json.loads(x) for x in (RUN/'decode_dev_epoch_20.jsonl').read_text().splitlines() if x]
used=set(); selected=[]
def take(name, ordered, count):
    got=[]
    for r in ordered:
        if r['cad_id'] not in used:
            used.add(r['cad_id']);got.append(dict(r,selection_bucket=name))
            if len(got)==count:break
    selected.extend(got)
# The stored step_reload flag is known invalid because its old evaluator lacked CadQuery.
take('PARSE_PASS__STEP_STATUS_UNAVAILABLE_IN_SAVED_EPOCH20', [r for r in rows if r['dsl_parse_success']],6)
take('HIGH_OP_F1', sorted(rows,key=lambda r:(r['op_f1'],r['exact_match']),reverse=True),4)
take('LOW_OP_F1_OR_PARSE_FAIL', sorted(rows,key=lambda r:(r['dsl_parse_success'],r['op_f1'])),4)
take('NO_EOS_RUNAWAY', [r for r in rows if r['unexpected_runaway'] or not r['eos_emitted']],3)
take('COMPLEX_LONG_DSL', sorted(rows,key=lambda r:r['target_token_length'],reverse=True),3)
for r in selected:
    r['prediction_text_status']='UNAVAILABLE: epoch20 JSON stores metrics only; no generated DSL was persisted.'
    r['step_status_note']='UNAVAILABLE: saved step_reload is from the deprecated evaluator without CadQuery.'
(OUT/'M2_EPOCH20_CASES_20.json').write_text(json.dumps({'source':'saved epoch20 self-decode metrics only','case_count':len(selected),'cases':selected},indent=2)+'\n')
txt=['M2 epoch20 TRAIN_SELF_DECODE inspection','Prediction DSL and predicted STEP were not persisted by the epoch20 evaluator. This file deliberately does not fabricate them or re-decode.','']
for r in selected:
    txt += [f"[{r['selection_bucket']}] {r['cad_id']}",f"GT token count={r['target_token_length']} pred token count={r['generated_token_length']}",f"EOS={r['eos_emitted']} hit_cap={r['hit_max_new_tokens']} parse={r['dsl_parse_success']} saved_step_reload={r['step_reload']} OpF1={r['op_f1']:.6f} Exact={r['exact_match']}",f"PRED DSL: {r['prediction_text_status']}",'']
(OUT/'M2_EPOCH20_CASES_20.txt').write_text('\n'.join(txt))
(OUT/'VISUALIZATION_BLOCKER.md').write_text('# Visualization blocker\n\nThe saved epoch20 per-CAD file intentionally retains metrics only and discards generated DSL text. Its `step_reload` field is from the known missing-CadQuery environment. Therefore GT/predicted STEP galleries cannot be reconstructed without an additional frozen-checkpoint decode. That would violate the no-re-decode instruction. No gallery was created.\n')
print(json.dumps({'curve_rows':len(table),'selected_cases':len(selected),'epoch20_saved_step_reload':sum(r['step_reload'] for r in rows),'prediction_text_saved':False},indent=2))
