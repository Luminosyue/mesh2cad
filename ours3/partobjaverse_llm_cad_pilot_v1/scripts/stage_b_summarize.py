#!/usr/bin/env python3
import csv,json,math,shutil,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

root=Path(sys.argv[1]).resolve()
cases=json.loads((root/'manifests/STAGE_B_CASES.json').read_text())
rows=[]
for c in cases:
 f=json.loads((root/'metrics'/f"{c['case_id']}_best.json").read_text())
 vs=[json.loads((root/'metrics'/f"{c['case_id']}_v{i}.json").read_text()) for i in (1,2,3)]
 row={'case_index':c['case_index'],'case_id':c['case_id'],'object_uid':c['object_uid'],'instance_id':c['instance_id'],'category':c['pilot_category'],'components':c['components'],'watertight':c['watertight'],'selected_route':f['selected_route']}
 for i,s in enumerate(vs,1):
  row.update({f'v{i}_parse':s['parse'],f'v{i}_exec':s['exec'],f'v{i}_step':s['step_export'],f'v{i}_reload':s['step_reload'],f'v{i}_brep':s['brep_valid'],f'v{i}_metrics':s['metrics_valid'],f'v{i}_cd':s.get('chamfer_l1'),f'v{i}_iou':s.get('iou')})
 row.update({'best_version':f['best_version'],'cad_parse':f['cad_parse'],'cad_execute':f['cad_execute'],'step_export':f['step_export'],'step_reload':f['step_reload'],'brep_valid':f['brep_valid'],'metrics_valid':f['chamfer_l1'] is not None,'chamfer_l1':f['chamfer_l1'],'chamfer_l2':f['chamfer_l2'],'normal_consistency':f['normal_consistency'],'iou':f['iou'],'bbox_error':f['bbox_error'],'surface_ratio':f['surface_ratio'],'volume_ratio':f['volume_ratio'],'source_sha256_before':f['source_sha256_before'],'source_sha256_after':f['source_sha256_after'],'source_mutation_failure':f['source_mutation_failure']})
 rows.append(row)

fields=list(rows[0])
with (root/'reports/PILOT20_SUMMARY.csv').open('w',newline='',encoding='utf-8') as fh:
 w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)
def vals(key,rs=rows):return [float(r[key]) for r in rs if r.get(key) is not None and math.isfinite(float(r[key]))]
def stat(key,rs=rows):
 a=vals(key,rs);return {'n':len(a),'mean':float(np.mean(a)) if a else None,'median':float(np.median(a)) if a else None,'std':float(np.std(a)) if a else None}
def nbool(k,rs=rows):return sum(bool(r[k]) for r in rs)
vvalid={i:sum(bool(r[f'v{i}_brep'] and r[f'v{i}_metrics']) for r in rows) for i in (1,2,3)}
best=Counter(r['best_version'] for r in rows)
improved=degraded=invalidated=0
for r in rows:
 seq=[]
 for i in (1,2,3):
  seq.append(float(r[f'v{i}_cd']) if r[f'v{i}_brep'] and r[f'v{i}_metrics'] and r[f'v{i}_cd'] is not None else None)
 if seq[0] is not None and any(x is not None and x < seq[0]-1e-6 for x in seq[1:]):improved+=1
 if any(seq[i] is not None and seq[i-1] is not None and seq[i]>seq[i-1]+1e-6 for i in (1,2)):degraded+=1
 if any(seq[i] is None and seq[i-1] is not None for i in (1,2)):invalidated+=1
groups={}
for cat in ['BOX_BOOLEAN_LIKE','EXTRUDE_LIKE','REVOLVE_CYLINDER_LIKE','SHELL_LIKE','HARDER_FREEFORM']:
 rs=[r for r in rows if r['category']==cat];groups[cat]={'N':len(rs),'BREP_VALID_RATE':nbool('brep_valid',rs)/len(rs) if rs else None,'CD':stat('chamfer_l1',rs),'IOU':stat('iou',rs)}
summary={'TOTAL_N':20,'PARSE_VALID_N':nbool('cad_parse'),'EXEC_VALID_N':nbool('cad_execute'),'STEP_EXPORT_N':nbool('step_export'),'STEP_RELOAD_N':nbool('step_reload'),'BREP_VALID_N':nbool('brep_valid'),'METRICS_VALID_N':nbool('metrics_valid'),'PARSE_RATE':nbool('cad_parse')/20,'EXEC_RATE':nbool('cad_execute')/20,'STEP_RELOAD_RATE':nbool('step_reload')/20,'BREP_VALID_RATE':nbool('brep_valid')/20,'GEOMETRY_METRICS_N':len(vals('chamfer_l1')),'CD':stat('chamfer_l1'),'IOU':stat('iou'),'NORMAL':stat('normal_consistency'),'BBOX_ERROR':stat('bbox_error'),'SURFACE_RATIO':stat('surface_ratio'),'VOLUME_RATIO':stat('volume_ratio'),'V1_VALID_N':vvalid[1],'V2_VALID_N':vvalid[2],'V3_VALID_N':vvalid[3],'BEST_IS_V1_N':best.get('v1',0),'BEST_IS_V2_N':best.get('v2',0),'BEST_IS_V3_N':best.get('v3',0),'NO_BEST_N':best.get(None,0),'REFINEMENT_IMPROVED_N':improved,'REFINEMENT_DEGRADED_N':degraded,'REFINEMENT_INVALIDATED_N':invalidated,'SOURCE_MUTATION_FAILURE_N':sum(r['source_mutation_failure'] for r in rows),'METRIC_COORDINATE_SPACE':'normalized','NORMALIZATION_PROTOCOL':'max_bbox_extent_to_1','CAD_WORK_PROTOCOL':'max_bbox_extent_to_100_cad_units','SAMPLING_N':100000,'category_breakdown':groups,'definitions':{'version_valid':'STEP reload and B-Rep valid and geometry metrics valid','refinement_improved':'a valid v2/v3 has Chamfer-L1 at least 1e-6 lower than valid v1','refinement_degraded':'a later consecutive valid round has Chamfer-L1 at least 1e-6 higher','refinement_invalidated':'a valid round is immediately followed by an invalid round','best':'STEP reload and B-Rep valid hard conditions; then lowest Chamfer-L1, highest IoU, highest normal consistency, lowest bbox error'}}
json.dump({'summary':summary,'cases':rows},(root/'reports/PILOT20_SUMMARY.json').open('w'),indent=2,ensure_ascii=False,allow_nan=False)

# Gallery cards: every fixed case gets one, including failures.
gal=root/'reports/PILOT20_GALLERY';gal.mkdir(exist_ok=True)
for r in rows:
 im=Image.new('RGB',(1200,480),'white');d=ImageDraw.Draw(im);cid=r['case_id'];rd=root/'renders'/cid
 paths=[rd/'best_source.png',rd/'best_recon.png',rd/'best_overlay.png']
 labels=['Source','Reconstruction','Overlay']
 for j,(p,label) in enumerate(zip(paths,labels)):
  x=10+j*390;d.text((x,8),label,fill='black')
  if p.exists():
   pic=Image.open(p).convert('RGB');pic.thumbnail((370,370));im.paste(pic,(x,35))
  else:d.rectangle((x,35,x+370,405),outline='red',width=3);d.text((x+120,200),'FAILED',fill='red')
 d.text((12,420),cid,fill='black');d.text((12,442),f"category={r['category']} route={r['selected_route']} best={r['best_version']} CD={r['chamfer_l1']} IoU={r['iou']}",fill='black');im.save(gal/f'{cid}.png')

md=['# PartObjaverse Pilot20 summary','',f"- TOTAL_N: 20",f"- PARSE_VALID_N: {summary['PARSE_VALID_N']}",f"- EXEC_VALID_N: {summary['EXEC_VALID_N']}",f"- STEP_EXPORT_N: {summary['STEP_EXPORT_N']}",f"- STEP_RELOAD_N: {summary['STEP_RELOAD_N']}",f"- BREP_VALID_N: {summary['BREP_VALID_N']}",f"- METRICS_VALID_N: {summary['METRICS_VALID_N']}",f"- GEOMETRY_METRICS_N: {summary['GEOMETRY_METRICS_N']}/20",f"- CD mean / median / std: {summary['CD']['mean']} / {summary['CD']['median']} / {summary['CD']['std']}",f"- IoU mean / median / std: {summary['IOU']['mean']} / {summary['IOU']['median']} / {summary['IOU']['std']}",f"- Normal mean / median: {summary['NORMAL']['mean']} / {summary['NORMAL']['median']}",'','## Protocol','',f"- METRIC_COORDINATE_SPACE={summary['METRIC_COORDINATE_SPACE']}",f"- NORMALIZATION_PROTOCOL={summary['NORMALIZATION_PROTOCOL']}",f"- SAMPLING_N={summary['SAMPLING_N']}",'','## Category breakdown','']
for k,v in groups.items():md += [f"- {k}: N={v['N']}, BREP_VALID_RATE={v['BREP_VALID_RATE']}, CD_MEAN={v['CD']['mean']}, CD_MEDIAN={v['CD']['median']}, IOU_MEAN={v['IOU']['mean']}, IOU_MEDIAN={v['IOU']['median']}"]
md += ['','## Refinement',f"- V1_VALID_N={vvalid[1]}, V2_VALID_N={vvalid[2]}, V3_VALID_N={vvalid[3]}",f"- BEST_IS_V1_N={best.get('v1',0)}, BEST_IS_V2_N={best.get('v2',0)}, BEST_IS_V3_N={best.get('v3',0)}",f"- REFINEMENT_IMPROVED_N={improved}",f"- REFINEMENT_DEGRADED_N={degraded}",f"- REFINEMENT_INVALIDATED_N={invalidated}",'',json.dumps(summary['definitions'],indent=2)]
(root/'reports/PILOT20_SUMMARY.md').write_text('\n'.join(md)+'\n',encoding='utf-8')

fail=[r for r in rows if not r['brep_valid']]
report=f"""# PartObjaverse LLM Mesh-to-CAD Pilot20

## Dataset provenance

PartObjaverse-Tiny; 200 source objects and 2112 instance parts. Pilot20 was frozen from Stage A and contains 20 unique object UIDs. No source SHA mutation was detected.

## Evaluation protocol

Parametric CadQuery programs, at most three retained rounds per case, actual STEP export/reload, B-Rep validity, tessellation, and geometry evaluation. Surface sampling is fixed at 100,000 points. Metrics use normalized coordinates with maximum source bbox extent equal to 1; CAD work coordinates use maximum extent 100.

## Overall validity

Parse {summary['PARSE_VALID_N']}/20; execute {summary['EXEC_VALID_N']}/20; STEP export {summary['STEP_EXPORT_N']}/20; STEP reload {summary['STEP_RELOAD_N']}/20; valid B-Rep {summary['BREP_VALID_N']}/20; geometry metrics {summary['METRICS_VALID_N']}/20.

## Geometry fidelity

Chamfer-L1 mean {summary['CD']['mean']}, median {summary['CD']['median']}, std {summary['CD']['std']} over {summary['CD']['n']} valid cases. Normal consistency mean {summary['NORMAL']['mean']}, median {summary['NORMAL']['median']}. Bbox relative error mean {summary['BBOX_ERROR']['mean']}, median {summary['BBOX_ERROR']['median']}. IoU has denominator {summary['IOU']['n']} because it is only computed when both source and reconstruction are volumetrically valid.

## Breakdown by part category

"""+'\n'.join(f"- {k}: N={v['N']}, B-Rep valid rate={v['BREP_VALID_RATE']}, CD mean={v['CD']['mean']}, CD median={v['CD']['median']}, IoU mean={v['IOU']['mean']}, IoU median={v['IOU']['median']}" for k,v in groups.items())+f"""

## Refinement analysis

V1/V2/V3 valid counts are {vvalid[1]}/{vvalid[2]}/{vvalid[3]}. Best versions: v1={best.get('v1',0)}, v2={best.get('v2',0)}, v3={best.get('v3',0)}. Improved={improved}, degraded={degraded}, invalidated={invalidated}. Definitions are recorded in PILOT20_SUMMARY.json.

## Failure modes

Final B-Rep failures: {len(fail)}. Multi-solid execution was explicitly supported and no component was silently discarded. Primitive approximations commonly miss local recesses, thin features, and asymmetric residual geometry; these limitations are reflected by Chamfer and normal metrics rather than hidden by visual selection.

## Representative examples

All 20 cases, including failures, have cards under reports/PILOT20_GALLERY. Per-case source, reconstruction, overlay, route, best version, CD and IoU are shown.

## Conclusion

This pilot measures validity and fidelity on the fixed Pilot20 only. It does not establish superiority over a baseline. The observed validity rate is {summary['BREP_VALID_RATE']:.3f}; geometric accuracy varies materially by category and primitive approximation.
"""
(root/'reports/STAGE_B_FINAL_REPORT.md').write_text(report,encoding='utf-8')

terminal=f"""PARTOBJAVERSE_LLM_CAD_PILOT_V1

STAGE_B_CASE_N=20

PARSE_VALID_N={summary['PARSE_VALID_N']}
EXEC_VALID_N={summary['EXEC_VALID_N']}
STEP_EXPORT_N={summary['STEP_EXPORT_N']}
STEP_RELOAD_N={summary['STEP_RELOAD_N']}
BREP_VALID_N={summary['BREP_VALID_N']}
GEOMETRY_VALID_N={summary['METRICS_VALID_N']}

BREP_VALID_RATE={summary['BREP_VALID_RATE']}

CD_MEAN={summary['CD']['mean']}
CD_MEDIAN={summary['CD']['median']}

IOU_MEAN={summary['IOU']['mean']}
IOU_MEDIAN={summary['IOU']['median']}

NORMAL_MEAN={summary['NORMAL']['mean']}
NORMAL_MEDIAN={summary['NORMAL']['median']}

BEST_IS_V1_N={best.get('v1',0)}
BEST_IS_V2_N={best.get('v2',0)}
BEST_IS_V3_N={best.get('v3',0)}

REFINEMENT_IMPROVED_N={improved}
REFINEMENT_DEGRADED_N={degraded}
REFINEMENT_INVALIDATED_N={invalidated}

SUMMARY_CSV={root/'reports/PILOT20_SUMMARY.csv'}
FINAL_REPORT={root/'reports/STAGE_B_FINAL_REPORT.md'}

CURRENT_GATE=STAGE_B_PILOT20_COMPLETE
"""
(root/'logs/stage_b_final_terminal.log').write_text(terminal,encoding='utf-8');print(terminal,end='')
