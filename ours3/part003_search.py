import importlib.util,json,subprocess,shutil
from pathlib import Path
import numpy as np,trimesh
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=O/'case05_residual_part003_recovery_v3';SRC=O/'batch_real_mesh2cad_v1/cases/CASE_05';OLD=O/'best_multipart_full_recovery_v2/parts/CADPART_003';ENV='/data/miniconda3/envs/multi_agent_cad/bin/python'
for x in ['manifest','parts','assembly','viewer','metrics','artifacts','logs']:(OUT/x).mkdir(parents=True,exist_ok=True)
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def mod(p,n):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
hf=mod(O/'high_fidelity_part_recovery_v2/scripts/pipeline.py','hf')
src=SRC/'p3/part_003.obj';base=OUT/'parts/CADPART_003';base.mkdir(parents=True,exist_ok=True);shutil.copy2(src,base/'CADPART_003_source.obj');shutil.copy2(OLD/'local_to_global_transform.json',base/'local_to_global_transform.json')
mesh=trimesh.load(src,force='mesh',process=False);feat=load(SRC/'cad_part_graph/CADPART_003/router/geometry_analysis/feature_hypotheses.json');prim=load(SRC/'cad_part_graph/CADPART_003/router/geometry_analysis/primitives.json');g=load(SRC/'cad_part_graph/cad_part_graph_v1.json')['nodes'][3]
rr={'REVOLUTION_LIKELIHOOD':g['REVOLUTION_LIKELIHOOD'],'CYLINDER_COVERAGE':g['CYLINDER_COVERAGE'],'EXTRUSION_LIKELIHOOD':g['EXTRUSION_LIKELIHOOD'],'PLANE_COVERAGE':g['PLANE_COVERAGE'],'ANALYTIC_COVERAGE':g['TOTAL_ANALYTIC_COVERAGE']};mode=hf.route(rr);center,B,scale=hf.frame(mesh,mode,feat);rows=hf.measured_sections(mesh,center,B,scale,200)
forensic={'PREVIOUS_BACKENDS_ATTEMPTED':['PRIMITIVE_CSG','MULTI_SECTION_LOFT_V2'],'PREVIOUS_BEST_BACKEND':'MULTI_SECTION_LOFT_V2','PREVIOUS_BEST_BREP_VALID':True,'PREVIOUS_BEST_CHAMFER':.017676366871566627,'PREVIOUS_BEST_P95':.08864308769040843,'PREVIOUS_BEST_COVERAGE02':1.0,'PREVIOUS_FAILURE_STAGE':'GEOMETRY_QA','PREVIOUS_FAILURE_REASON':'P95_HIGH','geometry_family':{'IS_SINGLE_BODY':len(mesh.split(only_watertight=False))==1,'IS_MULTI_COMPONENT':len(mesh.split(only_watertight=False))>1,'IS_REVOLUTION_LIKE':rr['REVOLUTION_LIKELIHOOD']>=.65,'IS_EXTRUSION_LIKE':rr['EXTRUSION_LIKELIHOOD']>=.65,'IS_SWEEP_LIKE':False,'IS_LOFT_LIKE':True,'IS_FREEFORM':rr['ANALYTIC_COVERAGE']<.5,'HAS_THIN_SHELL':False,'HAS_MULTIPLE_SURFACE_FAMILIES':True},'connected_components':len(mesh.split(only_watertight=False)),'CADPART_003_AREA_RATIO':.08786178149266731,'candidate_budget':16,'thresholds':{'Q1':[.01,.02,.95],'Q2':[.02,.05,.85],'S1':[.03,.07,.80]}}
dump(OUT/'metrics/failure_forensic.json',forensic);dump(base/'measured_cross_sections_200.json',{'sections':rows})
def classify(m):
 if not m.get('brep_valid'):return 'FAIL'
 a,b,c=m['symmetric_chamfer_normalized'],m['p95_symmetric'],m['coverage_02']
 return 'Q1' if a<=.01 and b<=.02 and c>=.95 else 'Q2' if a<=.02 and b<=.05 and c>=.85 else 'S1' if a<=.03 and b<=.07 and c>=.80 else 'FAIL'
results=[];case={'source_obj':str(src),'transform':str(OLD/'local_to_global_transform.json')}
for n in [12,16,20,24,32]:
 secs=hf.select_build_sections(rows,n);d=base/f'candidate_smooth_{n:03d}';d.mkdir(exist_ok=True);code=hf.LOFT_TEMPLATE.replace('__SECTIONS__',repr(hf.clean(secs))).replace('__RULED__','False');(d/'deterministic_program.py').write_text(code);r=subprocess.run([ENV,str(d/'deterministic_program.py')],cwd=d,text=True,capture_output=True,timeout=300);(d/'build.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:results.append({'id':f'SMOOTH_{n}','quality':'FAIL','reason':'BUILD_FAILED'});continue
 cand={'candidate_id':f'SMOOTH_{n}','backend':'BOUNDARY_CONSTRAINED_BSPLINE_BREP_V3','directory':str(d),'programmatic_simplicity_lower':False,'build_return_code':0};m=hf.qa_candidate(case,cand);q=classify(m);rec={'id':cand['candidate_id'],'backend':cand['backend'],'section_count':n,'quality':q,'metrics':m};results.append(rec);dump(d/'v3_result.json',rec);print(n,q,m['symmetric_chamfer_normalized'],m['p95_symmetric'],m['coverage_02'],flush=True)
 if q!='FAIL':break
dump(OUT/'metrics/candidate_search.json',{'CANDIDATES_RUN':len(results),'results':results})
good=[x for x in results if x['quality']!='FAIL']
if good:
 order={'Q1':0,'Q2':1,'S1':2};best=min(good,key=lambda x:(order[x['quality']],x['metrics']['p95_symmetric'],x['metrics']['symmetric_chamfer_normalized']));d=base/f"candidate_smooth_{best['section_count']:03d}";acc=base/'accepted';acc.mkdir(exist_ok=True);shutil.copy2(d/'candidate.step',acc/'part.step');shutil.copy2(d/'fresh_source_frame.obj',acc/'cad_mesh.obj');shutil.copy2(OLD/'local_to_global_transform.json',acc/'local_to_global_transform.json');dump(acc/'result.json',best);print('ACCEPTED',best['id'],best['quality'])
else:print('NO_ACCEPTED_CANDIDATE')
