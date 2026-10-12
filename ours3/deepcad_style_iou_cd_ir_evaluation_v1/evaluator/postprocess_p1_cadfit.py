import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/deepcad_style_iou_cd_ir_evaluation_v1/cadfit_comparison_v1')
P=list(csv.DictReader((B/'P1_val1000.csv').open())); C=list(csv.DictReader((B/'CADFIT_val1000.csv').open()))
M=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl')
manifest=[json.loads(x) for x in M.read_text().splitlines() if x.strip()]
frozen_gt_ok={r['cad_id']:Path(r['gt_step_path']).exists() for r in manifest}
def b(x): return x.lower()=='true'
def valid_iou(r):
    if not b(r['iou_valid']) or not r['iou']: return False
    v=float(r['iou']); return np.isfinite(v) and -1e-9 <= v <= 1+1e-9
def valid_cd(r): return b(r['cd_valid']) and bool(r['cd_deepcad']) and np.isfinite(float(r['cd_deepcad']))
for r in P+C:
    if r.get('iou') and not valid_iou(r):
        r['iou_valid']='False'; r['iou_failure_reason']='out_of_range_iou:'+r['iou']; r['iou']=''
common=[(p,c) for p,c in zip(P,C) if frozen_gt_ok[p['case_id']] and not b(p['deepcad_invalid']) and not b(c['deepcad_invalid']) and valid_iou(p) and valid_iou(c) and valid_cd(p) and valid_cd(c)]
def stats(vals):
    a=np.asarray(vals,float); return {'n':len(a),'mean':float(a.mean()),'median':float(np.median(a)),'p25':float(np.percentile(a,25)),'p75':float(np.percentile(a,75)),'p95':float(np.percentile(a,95))}
pi=[float(p['iou']) for p,c in common]; ci=[float(c['iou']) for p,c in common]
pc=[float(p['cd_deepcad']) for p,c in common]; cc=[float(c['cd_deepcad']) for p,c in common]
def boot(a,b):
    d=np.asarray(a)-np.asarray(b); rng=np.random.default_rng(20260915); z=np.empty(10000)
    for i in range(len(z)): z[i]=rng.choice(d,len(d),replace=True).mean()
    return {'mean_delta':float(d.mean()),'ci95':[float(np.percentile(z,2.5)),float(np.percentile(z,97.5))]}
p_invalid=sum(b(x['deepcad_invalid']) for x in P); c_invalid=sum(b(x['deepcad_invalid']) for x in C)
pv=[not b(x['deepcad_invalid']) for x in P]; cv=[not b(x['deepcad_invalid']) for x in C]
p_only=int(sum(a and not d for a,d in zip(pv,cv))); c_only=int(sum(d and not a for a,d in zip(pv,cv))); discord=p_only+c_only
summary={'N':1000,'FROZEN_GT_VALID_N':sum(frozen_gt_ok.values()),'P1_INVALID_N':p_invalid,'P1_IR':p_invalid/1000,'CADFIT_INVALID_N':c_invalid,'CADFIT_IR':c_invalid/1000,'P1_IOU_VALID_N_ON_FROZEN_GT':sum(frozen_gt_ok[x['case_id']] and valid_iou(x) for x in P),'CADFIT_IOU_VALID_N_ON_FROZEN_GT':sum(frozen_gt_ok[x['case_id']] and valid_iou(x) for x in C),'P1_CD_VALID_N_ON_FROZEN_GT':sum(frozen_gt_ok[x['case_id']] and valid_cd(x) for x in P),'CADFIT_CD_VALID_N_ON_FROZEN_GT':sum(frozen_gt_ok[x['case_id']] and valid_cd(x) for x in C),'COMMON_VALID_N':len(common),'P1_COMMON_IOU':stats(pi),'CADFIT_COMMON_IOU':stats(ci),'P1_COMMON_CD':stats(pc),'CADFIT_COMMON_CD':stats(cc),'IOU_PAIRED':boot(pi,ci),'CD_PAIRED':boot(pc,cc),'IR_MCNEMAR':{'P1_valid_CADFit_invalid':p_only,'CADFit_valid_P1_invalid':c_only,'p_value':float(binomtest(min(p_only,c_only),discord,.5).pvalue) if discord else 1.0},'IOU_RANGE_FAILURES':{'P1':sum(bool(x.get('iou_failure_reason','').startswith('out_of_range')) for x in P),'CADFit':sum(bool(x.get('iou_failure_reason','').startswith('out_of_range')) for x in C)}}
(B/'P1_VS_CADFIT_COMMON_VALID.csv').write_text('case_id,P1_IoU,CADFit_IoU,P1_CD,CADFit_CD\n'+'\n'.join(f"{p['case_id']},{p['iou']},{c['iou']},{p['cd_deepcad']},{c['cd_deepcad']}" for p,c in common)+'\n')
(B/'P1_VS_CADFIT_FINAL.json').write_text(json.dumps(summary,indent=2,default=lambda x:x.item())+'\n')
with (B/'P1_VS_CADFIT_FINAL.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['Method','IR_full1000','invalid_N','IoU_mean_common','IoU_median_common','CD_mean_common','CD_median_common','IoU_valid_N','CD_valid_N','common_valid_N'])
    w.writerow(['P1',summary['P1_IR'],p_invalid,summary['P1_COMMON_IOU']['mean'],summary['P1_COMMON_IOU']['median'],summary['P1_COMMON_CD']['mean'],summary['P1_COMMON_CD']['median'],summary['P1_IOU_VALID_N_ON_FROZEN_GT'],summary['P1_CD_VALID_N_ON_FROZEN_GT'],len(common)])
    w.writerow(['CADFit',summary['CADFIT_IR'],c_invalid,summary['CADFIT_COMMON_IOU']['mean'],summary['CADFIT_COMMON_IOU']['median'],summary['CADFIT_COMMON_CD']['mean'],summary['CADFIT_COMMON_CD']['median'],summary['CADFIT_IOU_VALID_N_ON_FROZEN_GT'],summary['CADFIT_CD_VALID_N_ON_FROZEN_GT'],len(common)])
report=f'''# P1 vs CADFit DeepCAD-style IoU/CD/IR VAL1000

FULL_N=1000
FROZEN_GT_VALID_N={summary['FROZEN_GT_VALID_N']}
COMMON_VALID_N={len(common)}

| Method | IR | Invalid N | IoU mean | IoU median | CD mean | CD median |
|---|---:|---:|---:|---:|---:|---:|
| P1 | {summary['P1_IR']:.6f} | {p_invalid} | {summary['P1_COMMON_IOU']['mean']:.6f} | {summary['P1_COMMON_IOU']['median']:.6f} | {summary['P1_COMMON_CD']['mean']:.6f} | {summary['P1_COMMON_CD']['median']:.6f} |
| CADFit | {summary['CADFIT_IR']:.6f} | {c_invalid} | {summary['CADFIT_COMMON_IOU']['mean']:.6f} | {summary['CADFIT_COMMON_IOU']['median']:.6f} | {summary['CADFIT_COMMON_CD']['mean']:.6f} | {summary['CADFIT_COMMON_CD']['median']:.6f} |

IOU_DELTA_P1_MINUS_CADFIT={summary['IOU_PAIRED']['mean_delta']}
IOU_95CI={summary['IOU_PAIRED']['ci95']}
CD_DELTA_P1_MINUS_CADFIT={summary['CD_PAIRED']['mean_delta']}
CD_95CI={summary['CD_PAIRED']['ci95']}
IR_MCNEMAR_P={summary['IR_MCNEMAR']['p_value']}

CADFit STL outputs were inverse-normalized using input-only center and scale. IoU uses OCC solids and Booleans. CD uses 2000 deterministic surface samples, squared bidirectional directional means summed. Out-of-range Boolean IoU values are classified as IoU failures and excluded from strict common-valid comparison, not clamped.
'''
(B/'FINAL_REPORT.md').write_text(report)
print(json.dumps(summary,indent=2,default=lambda x:x.item()))
