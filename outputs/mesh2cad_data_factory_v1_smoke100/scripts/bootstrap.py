import os,pathlib,json,hashlib,ast,datetime,sys,platform,subprocess
import argparse,shutil
parser=argparse.ArgumentParser();parser.add_argument('--output-root',required=True);args=parser.parse_args()
R=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');O=pathlib.Path(args.output_root).resolve()
if O.parent != (R/'outputs').resolve():raise SystemExit('New output must be a direct child of project outputs')
if O.exists():raise SystemExit('REFUSE_EXISTING_OUTPUT '+str(O))
O.mkdir(parents=True)
for d in ['config','manifests','cases','tables','reports','scripts','integrity','logs','stages','runtime_tmp']:(O/d).mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
donor=R/'partsam_cad_iou_top1000_v1/scripts/pipeline.py';raw=donor.read_text();tree=ast.parse(raw)
names={'normalize','basis_for_axis','candidate_axes','projected_profile','_scan_fill','voxel_occupancy'}
parts=['"""Pure fitting/occupancy utilities copied from historical pipeline; no historical module imported.\nVoxel occupancy is approximate majority-axis scan-fill, not exact volumetric IoU.\n"""','from typing import Any','import numpy as np']
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in names:parts.append(ast.get_source_segment(raw,n))
(O/'scripts/fit_logic.py').write_text('\n\n'.join(parts)+'\n')
(O/'integrity/REUSED_CODE.json').write_text(json.dumps({'source':str(donor),'source_sha256':sha(donor),'copied_functions':sorted(names),'new_file':'scripts/fit_logic.py','new_sha256':sha(O/'scripts/fit_logic.py'),'historical_code_modified':False},indent=2))
# Inventory source metadata only; no historical geometry execution.
src=R/'partsam/PartObjaverse-Tiny_instance_stl';reports=R/'partsam/PartObjaverse-Tiny_instance_cad';pool=[];protected={}
def protect(p):
 s=p.stat();protected[str(p)]={'sha256':sha(p),'size':s.st_size,'mtime_ns':s.st_mtime_ns}
for p in sorted(src.glob('*/*.stl')):
 q=reports/p.parent.name/(p.stem+'_report.json')
 if not q.is_file():continue
 d=json.load(open(q));b=d.get('input_bounds',[])
 if len(b)!=2:continue
 ext=[b[1][i]-b[0][i] for i in range(3)];maxe=max(ext)
 if maxe<=0 or min(ext)/maxe<.005:continue
 if d.get('source_path')!=str(p) or not d.get('source_sha256'):continue
 parent=R/'partsam/PartObjaverse-Tiny_stl'/(p.parent.name+'.stl')
 if not parent.is_file():continue
 key=hashlib.sha256((p.parent.name+'/'+p.stem).encode()).hexdigest()
 pool.append({'source_dataset':'PartObjaverse-Tiny_instance_stl','source_object_id':p.parent.name,'source_part_id':p.stem,'source_mesh_path':str(p),'source_mesh_sha256':d['source_sha256'],'source_evidence_path':str(q),'parent_mesh_path':str(parent),'historical_watertight':d.get('input_watertight',False),'historical_faces':d.get('input_faces',0),'min_extent_ratio':min(ext)/maxe,'selection_hash':key})
# Prefer already closed/simple parts; no CAD results/acceptance used in ranking.
pool.sort(key=lambda x:(not x['historical_watertight'],x['historical_faces'],x['selection_hash']))
selected=[];seen=set();skipped=[]
for row in pool:
 p=pathlib.Path(row['source_mesh_path']);actual=sha(p)
 if actual!=row['source_mesh_sha256']:skipped.append({'path':str(p),'reason':'HISTORICAL_SOURCE_HASH_MISMATCH'});continue
 if actual in seen:continue
 seen.add(actual);row['case_id']=f'case_{len(selected):05d}';row['parent_object_id']=row['source_object_id'];row['split_group_id']=row['source_dataset']+':'+row['source_object_id'];row['source_evidence_sha256']=sha(pathlib.Path(row['source_evidence_path']));row['parent_mesh_sha256']=sha(pathlib.Path(row['parent_mesh_path']));selected.append(row)
 for k in ['source_mesh_path','source_evidence_path','parent_mesh_path']:protect(pathlib.Path(row[k]))
 if len(selected)==100:break
protect(donor)
audit=R/'ours3/historical_mesh2cad_data_generation_audit_v1'
for p in audit.rglob('*'):
 if p.is_file() and p.stat().st_size<2000000:protect(p)
# Snapshot metadata for source directories and old fitting tree, rather than re-auditing all historical outputs.
meta=[]
for root in [src,R/'partsam/PartObjaverse-Tiny_stl',reports,R/'partsam_cad_iou_top1000_v1',audit]:
 for b,ds,fs in os.walk(root):
  for name in fs:
   p=pathlib.Path(b)/name;s=p.lstat();meta.append([str(p),s.st_size,s.st_mtime_ns,s.st_mode])
(O/'integrity/HISTORICAL_METADATA_BEFORE.json').write_text(json.dumps(meta))
(O/'integrity/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(protected,indent=2))
(O/'manifests/selection_frozen.json').write_text(json.dumps({'requested_n':100,'metadata_eligible_pool_n':len(pool),'located_n':len(selected),'selection_policy':'historical watertight first, ascending face count, sha256(object/part); exact-byte duplicate source hashes removed; min bbox extent/max >=0.005; no previous CAD metrics used','skipped':skipped,'cases':selected},indent=2))
config={'factory':'MESH2CAD_DATA_FACTORY_V1_SMOKE100','output_root':str(O),'target_input_n':100,'random_seed':20261006,'normalization':'source bbox midpoint translation, longest extent=1, orientation unchanged','normalization_formula':'canonical=(original-center)/longest_extent','evaluation_frame':'canonical source frame; no separate CAD alignment','n_points':20000,'iou_resolution':128,'iou_protocol':'APPROXIMATE_VOXEL_SCAN_FILL_IOU_V1','occupancy_method':'shared union-bbox grid; triangle subdivision surface rasterization; majority XYZ scan fill + binary_fill_holes; same method for all meshes; NOT exact solid IoU','tessellation_tolerance':0.001,'tessellation_angular_tolerance':0.05,'max_candidates':4,'timeout_seconds_per_candidate':120,'workers':4,'llm_used':False,'completion_default':False,'fallback_policy':'Only after direct failure, and independent evidence of missing major surfaces; non-watertight alone does not establish incompleteness','source_provenance_scope':'Existing real PartObjaverse part STL snapshot + historical exact SHA + present parent whole-object STL + geometric subset verification; not original download chain or design history','training':False,'largescale_generation':False,'loss_optimization':False}
(O/'config/factory_config.json').write_text(json.dumps(config,indent=2))
thresholds={'version':'SMOKE_REFERENCE_THRESHOLDS_V1_NOT_FINAL_TRAINING_THRESHOLDS','strict':{'iou_min':.90,'ncd_max':.01,'bbox_extent_error_max':.03,'bbox_center_error_max':.03,'centroid_error_max':.02},'relaxed':'all native/execute/STEP reload/mesh/evaluator gates pass but strict metric thresholds not all passed','reject':'source, native-code, execution, reload, invalid mesh or evaluator failure'}
(O/'config/thresholds.json').write_text(json.dumps(thresholds,indent=2))
print(json.dumps({'root':str(O),'located_n':len(selected),'eligible_pool_n':len(pool),'watertight_selected_n':sum(x['historical_watertight'] for x in selected),'selected_face_range':[min(x['historical_faces'] for x in selected),max(x['historical_faces'] for x in selected)],'protected_hash_n':len(protected),'metadata_n':len(meta)}))

for name in ['factory.py','execute_program.py','validate_and_report.py','bootstrap.py']:
 shutil.copyfile(pathlib.Path(__file__).parent/name,O/'scripts'/name)
