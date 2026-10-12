import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import json,csv,hashlib,statistics,ast,shutil
from pathlib import Path
import numpy as np,trimesh
R=Path('/data/home/cuiyuehan/project/mesh2cad'); S=R/'p3_xpart_open_cases'; O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'
for n in ['selection','manifests','objects','logs','reports','tables','paper_demo','code']:(O/n).mkdir(parents=True,exist_ok=True)
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def csvout(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mesh(p):return trimesh.load(str(p),force='mesh',process=False)
def params(p):
 t=ast.parse(p.read_text(encoding='utf-8-sig'))
 for n in t.body:
  if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='PARAMETERS' for a in n.targets):return json.loads(ast.literal_eval(n.value.args[0]))
 raise ValueError('No PARAMETERS')
def floats(x):
 if isinstance(x,dict):return sum((floats(v) for v in x.values()),[])
 if isinstance(x,list):return sum((floats(v) for v in x),[])
 return [x] if isinstance(x,float) else []
old=json.loads((R/'ours3/p3_xpart_20case_compact_ir_v1/CASE_MANIFEST.json').read_text())['cases']; oldmap={(x['OBJECT_ID'],x['PART_ID'].upper()):x['CASE_ID'] for x in old}
rows=[]; detail={}
for c in sorted(S.iterdir()):
 if not (c/'meta.json').exists():continue
 meta=json.loads((c/'meta.json').read_text()); files=sorted(p for p in (c/'xpart_parts').rglob('*') if p.suffix.lower() in ['.obj','.stl','.ply']); full=sorted(p for p in (c/'source').glob('*') if p.suffix.lower() in ['.obj','.stl','.ply']); n=int(meta.get('n_xpart_parts',0))
 ps=[]
 for f in files:
  pid=f.stem.upper() if f.parent.name=='xpart_parts' else f.parent.name.upper();d=c/'xpart_parts_cadquery_features'/pid; rp=d/'report.json';r=json.loads(rp.read_text()) if rp.exists() else {};cid=oldmap.get((c.name,pid)); v3=R/'ours3/p3_xpart_20case_compact_ir_v3'
  valid=bool(r.get('step_valid') and (d/f'{pid}.step').exists() and (d/f'{pid}.py').exists())
  ps.append(dict(PART_ID=pid,PART_MESH_PATH=str(f),RAW_CAD_READY=valid,Q14_READY=bool(cid and (R/f'ours3/p3_xpart_20case_compact_ir_v1/quantization/{cid}.json').exists()),V3_READY=bool(cid and (v3/f'compact_ir_v3/{cid}.v3').exists()),STEP_READY=valid,GENERATED_PROGRAM_READY=c.name=='tank' and pid=='PART_029',GENERATED_STEP_READY=c.name=='tank' and pid=='PART_029',NORMALIZATION_READY=valid,INVERSE_TRANSFORM_READY=valid,SOURCE='EXISTING_VALID_GENERATED' if c.name=='tank' and pid=='PART_029' else 'EXISTING_VALID_CANONICAL' if valid else 'NEED_NEW_CAD_GENERATION',STATUS='AUDITED_HISTORICAL_PASS' if valid else 'MISSING',CAD_PATH=str(d/f'{pid}.py'),STEP_PATH=str(d/f'{pid}.step'),HISTORICAL_CASE_ID=cid or '',QUALITY_STATUS=r.get('status','UNKNOWN')))
 m=mesh(full[0]) if len(full)==1 else None
 row=dict(OBJECT_ID=c.name,FULL_MESH_PATH=str(full[0]) if len(full)==1 else '',FULL_MESH_VERTEX_N=len(m.vertices) if m is not None else 0,FULL_MESH_FACE_N=len(m.faces) if m is not None else 0,FULL_MESH_WATERTIGHT=bool(m.is_watertight) if m is not None else False,PART_N=n,PART_MESH_N=len(ps),ALL_PARTS_PRESENT=n==len(ps) and len({p['PART_ID'] for p in ps})==n,COMMON_COORDINATE_EVIDENCE='Standalone build_model restores local basis/construction_scale/center to original object coordinates',EXISTING_CAD_PART_N=sum(p['RAW_CAD_READY'] for p in ps),EXISTING_Q14_PART_N=sum(p['Q14_READY'] for p in ps),EXISTING_V3_PART_N=sum(p['V3_READY'] for p in ps),EXISTING_STEP_PART_N=sum(p['STEP_READY'] for p in ps),CATEGORY=c.name,NOTES='Historical validity; live STEP readback follows. Quality refinement flags retained.')
 rows.append(row);detail[c.name]=(row,ps,m.bounds.tolist() if m is not None else None)
csvout(O/'selection/ALL_FULL_OBJECT_CANDIDATES.csv',rows)
chosen=['tank','airplane','robot','toaster','android_figure_orange','3d_dollhouse_sofa','winerack','pottery_large','mini_fire_engine','fire_truck','mini_excavator','pressure_cooker','speaker_big','dvd_player','cube','2_of_jenga_classic_game','assorted_vegetable_set','baby_car','birdhouse','aroma_stainless_steel_milk_frother_2_cup']
manifest=[];allparts=[]
for i,name in enumerate(chosen):
 r,ps,bounds=detail[name];assert r['ALL_PARTS_PRESENT'] and r['PART_N']>=2 and r['FULL_MESH_PATH'],name
 manifest.append(dict(OBJECT_INDEX=i,OBJECT_ID=name,CATEGORY=name,FULL_MESH_PATH=r['FULL_MESH_PATH'],PART_N=r['PART_N'],PART_DIRECTORY=str(S/name/'xpart_parts'),SELECTION_REASON='Priority named object with all parts and existing feature CAD' if i<4 else 'Complete multi-part object; existing feature CAD; visual category diversity; manageable part count'))
 out=O/'objects'/name;out.mkdir(exist_ok=True);csvout(out/'PART_MANIFEST.csv',ps);allparts+=ps
 b=np.array(bounds);center=b.mean(0);scale=1/np.ptp(b,axis=0).max();mat=np.eye(4);mat[:3,:3]*=scale;mat[:3,3]=-center*scale
 values=[]
 for p in ps:
  if p['RAW_CAD_READY']:values+=floats(params(Path(p['CAD_PATH'])))
 dump(out/'OBJECT_FRAME.json',dict(bbox_min=b[0].tolist(),bbox_max=b[1].tolist(),center=center.tolist(),scale=scale,rotation=np.eye(3).tolist(),normalization_matrix=mat.tolist(),inverse_matrix=np.linalg.inv(mat).tolist(),program_output_frame='ORIGINAL_OBJECT_COORDINATES',local_feature_frame_policy='Existing feature-local center/scale/basis retained with explicit inverse in executable program; no independent recentering of assembly.',common_q14_lo=min(values),common_q14_hi=max(values),q14_scope='All new parts share object-wide parameter range; historical q14 artifacts retained unchanged with their original inverse transforms.'))
for ext in ['json','csv']:
 p=O/f'manifests/FULL20_OBJECT_MANIFEST.{ext}'
 if p.exists():
  if ext=='json':assert json.loads(p.read_text())==manifest,'Frozen selection differs'
 else:
  if ext=='json':dump(p,manifest)
  else:csvout(p,manifest)
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'manifests').glob('FULL20_OBJECT_MANIFEST.*')};dump(O/'manifests/SHA256.json',hashes)
ns=[m['PART_N'] for m in manifest];summary=dict(SELECTED_OBJECT_N=len(manifest),TOTAL_PART_N=sum(ns),MIN_PARTS_PER_OBJECT=min(ns),MEAN_PARTS_PER_OBJECT=statistics.mean(ns),MEDIAN_PARTS_PER_OBJECT=statistics.median(ns),MAX_PARTS_PER_OBJECT=max(ns),EXISTING_VALID_CAD_PART_N=sum(p['RAW_CAD_READY'] for p in allparts),MISSING_CAD_PART_N=sum(not p['RAW_CAD_READY'] for p in allparts),EXISTING_Q14_PART_N=sum(p['Q14_READY'] for p in allparts),TANK_PART_N=detail['tank'][0]['PART_N'],FIRST_FIVE_EXPECTED=['winerack','pottery_large','3d_dollhouse_sofa','android_figure_orange','airplane'],FREE_DISK_GB=shutil.disk_usage('/data').free/1e9,validation_note='Existing valid CAD counts based on historical per-part STEP_VALID reports, to be rechecked live.')
dump(O/'reports/SELECTION_AUDIT.json',summary)
(O/'reports/PROGRESS.md').write_text(f'FULL OBJECTS:\ncompleted 0/20\n\nTOTAL PARTS:\ncompleted 0/{sum(ns)}\n\nFULL ASSEMBLY PASS:\n0/20\n\nCURRENT:\nSelection frozen; live CAD/q14/V3 audit starting\n\nFAILED PARTS:\nNone evaluated yet\n')
print(json.dumps(summary,indent=2));print('\n'.join(f"{m['OBJECT_ID']} | {m['PART_N']}" for m in manifest))
