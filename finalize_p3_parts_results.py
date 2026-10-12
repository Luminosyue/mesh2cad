from pathlib import Path
import csv, json
from collections import defaultdict

OUT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_parts_cad_results')
rows = list(csv.DictReader((OUT/'all_manifest.csv').open()))
by = defaultdict(list)
for r in rows:
    by[r['source'].split('/')[0]].append(r)

def fnum(x):
    try: return float(x)
    except: return None

case_rows=[]
for case, rr in sorted(by.items()):
    vals=[fnum(r.get('surface_iou_64')) for r in rr if fnum(r.get('surface_iou_64')) is not None]
    case_rows.append({'case':case,'parts':len(rr),'kept':sum(r.get('status')=='kept' for r in rr),'rejected':sum(r.get('status')=='rejected' for r in rr),'errors':sum(r.get('status')=='error' for r in rr),'mean_surface_iou_64':sum(vals)/len(vals) if vals else None,'min_surface_iou_64':min(vals) if vals else None})
with (OUT/'CASE_SUMMARY.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(case_rows[0])); w.writeheader(); w.writerows(case_rows)

vals=[fnum(r.get('surface_iou_64')) for r in rows if fnum(r.get('surface_iou_64')) is not None]
summary={
 'source_root':'/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases',
 'source_subdirectory':'p3_parts',
 'source_mesh_formats':{'obj':sum(r['source'].lower().endswith('.obj') for r in rows),'stl':sum(r['source'].lower().endswith('.stl') for r in rows)},
 'case_count':len(by),'part_count':len(rows),'generated_cad_code_count':len(list((OUT/'samples').rglob('cad_model.py'))),
 'generated_step_count':len(list((OUT/'samples').rglob('model.step'))),'generated_rebuilt_stl_count':len(list((OUT/'samples').rglob('cad_rebuilt.stl'))),
 'kept_count':sum(r.get('status')=='kept' for r in rows),'rejected_count':sum(r.get('status')=='rejected' for r in rows),'error_count':sum(r.get('status')=='error' for r in rows),
 'surface_iou_threshold':0.90,'surface_iou_metric':'64-resolution world-aligned surface voxel IoU between source mesh and STEP roundtrip tessellation',
 'surface_iou_mean':sum(vals)/len(vals) if vals else None,'surface_iou_min':min(vals) if vals else None,'surface_iou_max':max(vals) if vals else None,
 'low_surface_iou_count':sum((fnum(r.get('surface_iou_64')) is not None and fnum(r.get('surface_iou_64'))<0.90) for r in rows),'invalid_cad_count':sum(r.get('cad_valid')=='False' for r in rows),
 'source_modified':False,'source_quarantined':False
}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
readme=f'''# p3_parts Mesh 鈫?CAD 鎵瑰鐞嗙粨鏋?
婧愮洰褰曪細`{summary['source_root']}/p3_parts`

鏈洰褰曞叡鍙戠幇 **{summary['case_count']} 涓?case銆亄summary['part_count']} 涓儴浠剁綉鏍?*銆傚疄闄呰緭鍏ユ牸寮忎负 **{summary['source_mesh_formats']['obj']} 涓?OBJ**锛堜笉鏄?STL锛涜剼鏈悓鏃舵敮鎸?STL锛夈€?
| 鎸囨爣 | 鏁伴噺 |
|---|---:|
| 閮ㄤ欢缃戞牸 | {summary['part_count']} |
| CAD code (`cad_model.py`) | {len(list((OUT/'samples').rglob('cad_model.py')))} |
| STEP | {summary['generated_step_count']} |
| STEP 鍥炶 CAD STL | {summary['generated_rebuilt_stl_count']} |
| 閫氳繃 IoU/鏈夋晥鎬?| {summary['kept_count']} |
| 闅旂 | {summary['rejected_count']} |
| 閿欒 | {summary['error_count']} |

IoU 浣跨敤婧愮綉鏍间笌 STEP 鍥炶鍚庝笁瑙掔綉鏍肩殑 64 鍒嗚鲸鐜囪〃闈綋绱?IoU锛岄槇鍊间负 0.90銆傚钩鍧?IoU 涓?`{summary['surface_iou_mean']:.6f}`锛屾渶灏?IoU 涓?`{summary['surface_iou_min']:.6f}`銆傛湰娆″彧鍐欏叆鏂拌緭鍑虹洰褰曪紝婧?`p3_parts` 娌℃湁绉诲姩銆佸垹闄ゆ垨淇敼銆?
姣忎釜閮ㄤ欢缁撴灉浣嶄簬 `samples/<case>/p3_parts/<part>/`锛屽寘鍚細

- `cad_model.py`锛氬彲鐙珛鎵ц鐨?CadQuery/OCP CAD 閲嶅缓浠ｇ爜
- `model.step`锛氫唬鐮佸鍑虹殑 STEP
- `cad_rebuilt.stl`锛歋TEP 鍥炶鍚庣殑 CAD 涓夎缃戞牸
- `metrics.json`锛欼oU銆佹嫇鎵戝拰閲嶅缓鎸囨爣
- `rebuild.log`锛氶噸寤烘棩蹇?
鎵归噺娓呭崟锛歚all_manifest.csv`銆乣kept_manifest.csv`銆乣rejected_manifest.csv`銆乣CASE_SUMMARY.csv`銆?'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))

