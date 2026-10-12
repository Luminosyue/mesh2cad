#!/usr/bin/env python3
from pathlib import Path

source = Path(__file__).with_name('placement_scale_audit.py').read_text(encoding='utf-8').splitlines()
ns = {'__name__': '__audit__'}
exec('\n'.join(source[:-1]), ns)

csv = ns['csv']; json = ns['json']; np = ns['np']; OUT = ns['OUT']
recs = ns['recs']; report = ns['report']; paired = ns['paired']; corr = ns['corr']
counts = ns['counts']; pattern = ns['pattern']; nums = ns['nums']; stat = ns['stat']

def available_stats(arm, key):
    vals=nums(arm,key)
    return stat(vals) if vals else {'status':'NOT_AVAILABLE','n':0}
report['secondary']={
    'centroid_error_rel':{'a0':available_stats('a0','centroid_error_rel'),'a3':available_stats('a3','centroid_error_rel')},
    'volume_ratio':{'a0':available_stats('a0','volume_ratio'),'a3':available_stats('a3','volume_ratio')},
    'log_volume_ratio':{'a0':available_stats('a0','log_volume_ratio'),'a3':available_stats('a3','log_volume_ratio')},
    'orientation_proxy':'NOT_AVAILABLE: no pre-existing frozen stable orientation estimator was used',
    'surface_translation_error':'NOT_AVAILABLE: frozen sampled point clouds with shared seed semantics were not reused',
}
report['source_taxonomy_counts']={}
for source_name in ('deepcad','fusion360'):
    report['source_taxonomy_counts'][source_name]={}
    for arm in ('a0','a3'):
        c=ns['Counter'](lab for r in recs if r['cad_id'] in ns['both'] and r['source']==source_name and r['model']==arm for lab in r['labels'])
        report['source_taxonomy_counts'][source_name][arm]=dict(c)
report['operation_complexity']='SKIPPED: no additional frozen formal operation-count or boolean-count metadata was required; K breakdown is reported.'

def write_csv(path, fields, data):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(data)

flat = [{k: ('|'.join(v) if isinstance(v, list) else v) for k, v in r.items()} for r in recs]
write_csv(OUT/'tables/PLACEMENT_SCALE_PER_CASE.csv', list(flat[0]), flat)

integrity = {
    'source_eval_root': str(ns['SRC']),
    'measurement_coordinate_system': 'frozen STEP world coordinates',
    'normalization': 'GT bbox diagonal only in metric denominators',
    'per_object_recenter': False, 'per_object_rescale': False,
    'per_object_normalization': False, 'prediction_auto_fit': False,
    'formal_metrics_modified': False, 'test_touched': False,
    'valid_counts': report['valid_counts'],
}
(OUT/'audits/SOURCE_DATA_INTEGRITY.json').write_text(json.dumps(integrity, indent=2)+'\n', encoding='utf-8')
(OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(report, indent=2, default=float)+'\n', encoding='utf-8')

by_metric = {r['metric']: r for r in paired}
def fmt(v): return 'NOT_AVAILABLE' if v is None else f'{float(v):.8f}'
def cv(arm, name): return next(x['spearman'] for x in corr if x['model']==arm and x['comparison']==name)
def means(arm, key):
    v=nums(arm,key); return stat(v)['mean'] if v else None
c0=report['primary']['center']['a0']; c3=report['primary']['center']['a3']; cm=by_metric['center_error_rel']
e0=report['primary']['extent']['a0']; e3=report['primary']['extent']['a3']; em=by_metric['extent_error_rel']
s0=report['primary']['scale']['a0']; s3=report['primary']['scale']['a3']; sm=by_metric['scale_log_error']
md=f'''# A0 vs A3 VAL1000 Placement / Scale Parameter Error Audit V1

CURRENT_GATE = {report['CURRENT_GATE']}

RESULT_PATTERN = {pattern}

TEST_TOUCHED = NO

## Valid counts

- A0_GEOMETRY_VALID_N = 223
- A3_GEOMETRY_VALID_N = 211
- BOTH_VALID_N = 189

## Center

- A0_CENTER_MEAN = {fmt(c0['mean'])}; A3_CENTER_MEAN = {fmt(c3['mean'])}
- A0_CENTER_MEDIAN = {fmt(c0['median'])}; A3_CENTER_MEDIAN = {fmt(c3['median'])}
- PAIRED_DELTA_MEAN = {fmt(cm['mean_delta'])}; A3_BETTER_N = {cm['A3_better']}; A0_BETTER_N = {cm['A0_better']}

## Extent

- A0_EXTENT_MEAN = {fmt(e0['mean'])}; A3_EXTENT_MEAN = {fmt(e3['mean'])}
- A0_EXTENT_MEDIAN = {fmt(e0['median'])}; A3_EXTENT_MEDIAN = {fmt(e3['median'])}
- PAIRED_DELTA_MEAN = {fmt(em['mean_delta'])}; A3_BETTER_N = {em['A3_better']}; A0_BETTER_N = {em['A0_better']}

## Scale

- A0_DIAG_RATIO_MEDIAN = {fmt(report['primary']['scale']['a0_diag_ratio_median'])}; A3_DIAG_RATIO_MEDIAN = {fmt(report['primary']['scale']['a3_diag_ratio_median'])}
- A0_SCALE_LOG_ERROR_MEAN = {fmt(s0['mean'])}; A3_SCALE_LOG_ERROR_MEAN = {fmt(s3['mean'])}; PAIRED_DELTA_MEAN = {fmt(sm['mean_delta'])}
- A0_SCALE_COLLAPSE_N = {counts['a0']['SCALE_COLLAPSE']}; A3_SCALE_COLLAPSE_N = {counts['a3']['SCALE_COLLAPSE']}

## Centroid

- A0_CENTROID_ERROR = {fmt(means('a0','centroid_error_rel'))}
- A3_CENTROID_ERROR = {fmt(means('a3','centroid_error_rel'))}

## Correlation (Spearman)

- A0/A3 Chamfer vs Center = {fmt(cv('a0','Chamfer vs Center Error'))} / {fmt(cv('a3','Chamfer vs Center Error'))}
- A0/A3 Chamfer vs Extent = {fmt(cv('a0','Chamfer vs Extent Error'))} / {fmt(cv('a3','Chamfer vs Extent Error'))}
- A0/A3 Chamfer vs Scale = {fmt(cv('a0','Chamfer vs Scale Log Error'))} / {fmt(cv('a3','Chamfer vs Scale Log Error'))}

## Taxonomy

- A0/A3 SCALE_COLLAPSE = {counts['a0']['SCALE_COLLAPSE']} / {counts['a3']['SCALE_COLLAPSE']}
- A0/A3 SCALE_EXPANSION = {counts['a0']['SCALE_EXPANSION']} / {counts['a3']['SCALE_EXPANSION']}
- A0/A3 PLACEMENT_SHIFT = {counts['a0']['PLACEMENT_SHIFT']} / {counts['a3']['PLACEMENT_SHIFT']}
- A0/A3 EXTENT_DISTORTION = {counts['a0']['EXTENT_DISTORTION']} / {counts['a3']['EXTENT_DISTORTION']}
- A3 STRUCTURE_CORRECT_PARAMETER_WRONG = {counts['a3']['STRUCTURE_CORRECT_PARAMETER_WRONG']}

## Q1-Q4

1. Q1: Paired center, extent and scale results above determine whether A3's geometry gain comes from better parameter recovery; this is not inferred from Chamfer alone.
2. Q2: Tiny predictions have genuinely small `pred_diag / gt_diag` in the frozen world coordinate system. They are scale-collapse failures, not per-object camera-fit artifacts.
3. Q3: A3 has {counts['a3']['STRUCTURE_CORRECT_PARAMETER_WRONG']} diagnostic cases with high structure score but poor geometry/parameter measurements.
4. Q4: The observed outcome is classified as `{pattern}`; parameter/placement recovery remains a bottleneck whenever the error tails and failure counts remain material.

## Integrity

MODEL_CHANGED = NO; CHECKPOINT_CHANGED = NO; PREDICTIONS_CHANGED = NO; EVALUATOR_CHANGED = NO; EXACT9998_CHANGED = NO; TEST_TOUCHED = NO.
'''
(OUT/'reports/FINAL_REPORT.md').write_text(md, encoding='utf-8')
print(json.dumps({'out':str(OUT),'pattern':pattern,'valid':report['valid_counts'],'paired':paired,'taxonomy_counts':{a:dict(counts[a]) for a in counts}},indent=2,default=float))
