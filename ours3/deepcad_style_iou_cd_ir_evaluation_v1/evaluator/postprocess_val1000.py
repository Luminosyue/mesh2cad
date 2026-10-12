import csv, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

BASE=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/deepcad_style_iou_cd_ir_evaluation_v1')
P=list(csv.DictReader((BASE/'per_case/P1_DEEPCAD_STYLE_METRICS.csv').open()))
C=list(csv.DictReader((BASE/'per_case/CAD_RECODE_DEEPCAD_STYLE_METRICS.csv').open()))
def b(x): return x.lower()=='true'
def f(x): return float(x)
def boot(a,bv,higher=True):
    d=np.array([f(x)-f(y) for x,y in zip(a,bv)],float); rng=np.random.default_rng(20260915); means=np.empty(10000); meds=np.empty(10000)
    for i in range(10000):
        z=rng.choice(d,len(d),replace=True); means[i]=z.mean(); meds[i]=np.median(z)
    wins=(d>1e-12) if higher else (d < -1e-12); ties=~((d>1e-12)|(d < -1e-12))
    return {'n':len(d),'mean_p1_minus_cad_recode':float(d.mean()),'median_p1_minus_cad_recode':float(np.median(d)),'ci95_mean':[float(np.percentile(means,2.5)),float(np.percentile(means,97.5))],'ci95_median':[float(np.percentile(meds,2.5)),float(np.percentile(meds,97.5))],'p1_win_n':int(wins.sum()),'tie_n':int(ties.sum()),'cad_recode_win_n':int((~wins & ~ties).sum())}
def write_csv(path, obj):
    path.parent.mkdir(exist_ok=True)
    with path.open('w',newline='') as h:
        w=csv.writer(h); w.writerow(['metric','value']);
        for k,v in obj.items(): w.writerow([k,json.dumps(v) if isinstance(v,(list,dict)) else v])
def tax(rows):
    out={}
    for r in rows:
        if not b(r['deepcad_invalid']): continue
        reason=r['invalid_reason'] or 'other'; out[reason]=out.get(reason,0)+1
    return out
BASE.joinpath('audit').mkdir(exist_ok=True)
matrix={'both_valid':0,'P1_valid_CAD_RECODE_invalid':0,'CAD_RECODE_valid_P1_invalid':0,'both_invalid':0,'P1_step_pass_CAD_RECODE_invalid':0,'P1_step_fail_CAD_RECODE_valid':0,'CAD_RECODE_step_pass_invalid':0,'CAD_RECODE_step_fail_valid':0}
for p,c in zip(P,C):
    pv=not b(p['deepcad_invalid']); cv=not b(c['deepcad_invalid'])
    if pv and cv: matrix['both_valid']+=1
    elif pv: matrix['P1_valid_CAD_RECODE_invalid']+=1
    elif cv: matrix['CAD_RECODE_valid_P1_invalid']+=1
    else: matrix['both_invalid']+=1
    if b(p['step_reload_success']) and b(c['deepcad_invalid']): matrix['P1_step_pass_CAD_RECODE_invalid']+=1
    if not b(p['step_reload_success']) and not b(c['deepcad_invalid']): matrix['P1_step_fail_CAD_RECODE_valid']+=1
    if b(c['step_reload_success']) and b(c['deepcad_invalid']): matrix['CAD_RECODE_step_pass_invalid']+=1
    if not b(c['step_reload_success']) and not b(c['deepcad_invalid']): matrix['CAD_RECODE_step_fail_valid']+=1
with (BASE/'audit/IR_VS_STEP_RELOAD_MATRIX.csv').open('w',newline='') as h:
    w=csv.writer(h); w.writerow(['category','count']); w.writerows(matrix.items())
common=[(p,c) for p,c in zip(P,C) if not b(p['deepcad_invalid']) and not b(c['deepcad_invalid']) and b(p['gt_valid']) and b(c['gt_valid']) and b(p['iou_valid']) and b(c['iou_valid']) and b(p['cd_valid']) and b(c['cd_valid'])]
iv=boot([x['iou'] for x,y in common],[y['iou'] for x,y in common],True); cd=boot([x['cd_deepcad'] for x,y in common],[y['cd_deepcad'] for x,y in common],False)
write_csv(BASE/'stats/P1_VS_CAD_RECODE_IOU_BOOTSTRAP.csv',iv); write_csv(BASE/'stats/P1_VS_CAD_RECODE_CD_BOOTSTRAP.csv',cd)
both_invalid=matrix['both_invalid']; p_only=matrix['P1_valid_CAD_RECODE_invalid']; c_only=matrix['CAD_RECODE_valid_P1_invalid']; discord=p_only+c_only; pval=float(binomtest(min(p_only,c_only),discord,0.5).pvalue) if discord else 1.0
write_csv(BASE/'stats/P1_VS_CAD_RECODE_IR_MCNEMAR.csv',{'P1_IR':sum(b(x['deepcad_invalid']) for x in P)/1000,'CAD_RECODE_IR':sum(b(x['deepcad_invalid']) for x in C)/1000,'IR_DELTA_PP':(sum(b(x['deepcad_invalid']) for x in P)-sum(b(x['deepcad_invalid']) for x in C))/10,'P1_VALID_ONLY_N':p_only,'CAD_RECODE_VALID_ONLY_N':c_only,'BOTH_VALID_N':matrix['both_valid'],'BOTH_INVALID_N':both_invalid,'MCNEMAR_P':pval})
for name,rows in [('P1',P),('CAD_RECODE',C)]:
    write_csv(BASE/f'failure_analysis/{name}_IR_FAILURE_TAXONOMY.csv',tax(rows))
    write_csv(BASE/f'failure_analysis/{name}_CD_FAILURES.csv',{(r['cd_failure_reason'] or 'none'):sum(1 for x in rows if (x['cd_failure_reason'] or 'none')==(r['cd_failure_reason'] or 'none')) for r in rows})
    write_csv(BASE/f'failure_analysis/{name}_IOU_BOOLEAN_FAILURES.csv',{(r['iou_failure_reason'] or 'none'):sum(1 for x in rows if (x['iou_failure_reason'] or 'none')==(r['iou_failure_reason'] or 'none')) for r in rows})
summary=json.load((BASE/'tables/P1_VS_CAD_RECODE_DEEPCAD_STYLE_CORE.json').open()); summary.update({'GT_INVALID_N':sum(not b(x['gt_valid']) for x in P),'IR_MATRIX':matrix,'IOU_BOOTSTRAP':iv,'CD_BOOTSTRAP':cd,'IR_MCNEMAR':{'P1_IR':sum(b(x['deepcad_invalid']) for x in P)/1000,'CAD_RECODE_IR':sum(b(x['deepcad_invalid']) for x in C)/1000,'P_VALUE':pval}}); (BASE/'tables/P1_VS_CAD_RECODE_DEEPCAD_STYLE_CORE.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
with (BASE/'tables/P1_VS_CAD_RECODE_DEEPCAD_STYLE_CORE.csv').open('w',newline='') as h:
    w=csv.writer(h); w.writerow(['Method','IoU_mean_common','IoU_median_common','CD_DeepCAD_mean_common','CD_DeepCAD_median_common','IR_full1000','IoU_valid_N','CD_valid_N']); w.writerow(['P1',summary['P1_COMMON_IOU']['mean'],summary['P1_COMMON_IOU']['median'],summary['P1_COMMON_CD']['mean'],summary['P1_COMMON_CD']['median'],summary['P1_IR'],summary['P1_IOU_VALID_N'],summary['P1_CD_VALID_N']]); w.writerow(['CAD-Recode',summary['CAD_RECODE_COMMON_IOU']['mean'],summary['CAD_RECODE_COMMON_IOU']['median'],summary['CAD_RECODE_COMMON_CD']['mean'],summary['CAD_RECODE_COMMON_CD']['median'],summary['CAD_RECODE_IR'],summary['CAD_RECODE_IOU_VALID_N'],summary['CAD_RECODE_CD_VALID_N']])
with (BASE/'tables/P1_VS_CAD_RECODE_DEEPCAD_STYLE_FULLSET.csv').open('w',newline='') as h:
    w=csv.writer(h); w.writerow(['Method','FULL_N','GT_invalid_N','prediction_invalid_N','IR','IoU_valid_N','CD_valid_N']); w.writerow(['P1',1000,summary['GT_INVALID_N'],summary['P1_INVALID_N'],summary['P1_IR'],summary['P1_IOU_VALID_N'],summary['P1_CD_VALID_N']]); w.writerow(['CAD-Recode',1000,summary['GT_INVALID_N'],summary['CAD_RECODE_INVALID_N'],summary['CAD_RECODE_IR'],summary['CAD_RECODE_IOU_VALID_N'],summary['CAD_RECODE_CD_VALID_N']])
with (BASE/'tables/P1_VS_CAD_RECODE_DEEPCAD_STYLE_COMMON_VALID.csv').open('w',newline='') as h:
    w=csv.writer(h); w.writerow(['COMMON_VALID_N','P1_IoU_mean','CAD_Recode_IoU_mean','P1_CD_mean','CAD_Recode_CD_mean','IoU_delta_P1_minus_CAD_Recode','CD_delta_P1_minus_CAD_Recode','IoU_CI95','CD_CI95']); w.writerow([len(common),summary['P1_COMMON_IOU']['mean'],summary['CAD_RECODE_COMMON_IOU']['mean'],summary['P1_COMMON_CD']['mean'],summary['CAD_RECODE_COMMON_CD']['mean'],iv['mean_p1_minus_cad_recode'],cd['mean_p1_minus_cad_recode'],iv['ci95_mean'],cd['ci95_mean']])
with (BASE/'tables/P1_VS_CAD_RECODE_ALL_METRICS.csv').open('w',newline='') as h:
    w=csv.writer(h); w.writerow(['Metric','P1','CAD-Recode','Notes']); w.writerow(['IR',summary['P1_IR'],summary['CAD_RECODE_IR'],'full denominator 1000']); w.writerow(['IoU',summary['P1_COMMON_IOU']['mean'],summary['CAD_RECODE_COMMON_IOU']['mean'],'strict common-valid N='+str(len(common))]); w.writerow(['CD_DeepCAD',summary['P1_COMMON_CD']['mean'],summary['CAD_RECODE_COMMON_CD']['mean'],'strict common-valid N='+str(len(common))]); w.writerow(['GT_invalid_N',summary['GT_INVALID_N'],summary['GT_INVALID_N'],'GT denominator retained separately'])
report=f'''# P1 vs CAD-Recode DeepCAD-style IoU/CD/IR VAL1000

FULL_N=1000\nGT_INVALID_N={summary['GT_INVALID_N']}\nP1_INVALID_N={summary['P1_INVALID_N']}\nP1_IR={summary['P1_IR']}\nCAD_RECODE_INVALID_N={summary['CAD_RECODE_INVALID_N']}\nCAD_RECODE_IR={summary['CAD_RECODE_IR']}\nCOMMON_VALID_N={len(common)}\n
P1_COMMON_IOU_MEAN={summary['P1_COMMON_IOU']['mean']}\nCAD_RECODE_COMMON_IOU_MEAN={summary['CAD_RECODE_COMMON_IOU']['mean']}\nIOU_PAIRED_DELTA={iv['mean_p1_minus_cad_recode']}\nIOU_95CI={iv['ci95_mean']}\n
P1_COMMON_CD_MEAN={summary['P1_COMMON_CD']['mean']}\nCAD_RECODE_COMMON_CD_MEAN={summary['CAD_RECODE_COMMON_CD']['mean']}\nCD_PAIRED_DELTA={cd['mean_p1_minus_cad_recode']}\nCD_95CI={cd['ci95_mean']}\n
IR_MCNEMAR_P={pval}\n
Interpretation: on strict common-valid cases, P1 has higher IoU and lower DeepCAD-style CD. The full-set IR denominator is 1000. GT-invalid cases are reported separately and are not silently removed from the full set. Existing STEP Reload, Chamfer_V2, H95, and Volume metrics remain separate.

PREDICTIONS_CHANGED=NO\nSTEP_FILES_CHANGED=NO\nINFERENCE_RERUN=NO\nEVALUATOR_CHANGED=NO\nCURRENT_GATE=P1_CAD_RECODE_DEEPCAD_STYLE_IOU_CD_IR_VAL1000_COMPLETE\n'''
(BASE/'reports').mkdir(exist_ok=True); (BASE/'reports/FINAL_REPORT.md').write_text(report)
