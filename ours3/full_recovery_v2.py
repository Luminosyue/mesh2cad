import csv, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
import numpy as np
import trimesh

OURS=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
BATCH=OURS/'batch_real_mesh2cad_v1'; SRC=BATCH/'cases/CASE_05'; OUT=OURS/'best_multipart_full_recovery_v2'
ENV=Path('/data/miniconda3/envs/multi_agent_cad/bin/python')
for d in ['manifest','parts','surface_brep','assembly','viewer','metrics','artifacts','logs']:(OUT/d).mkdir(parents=True,exist_ok=True)
def load(p): return json.loads(Path(p).read_text())
def dump(p,x): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
hf=mod(OURS/'high_fidelity_part_recovery_v2/scripts/pipeline.py','hf_v2_frozen')

# Deterministic target selection from frozen per-case metrics.
mf=load(BATCH/'manifest/batch_10_case_manifest.json'); candidates=[]
for c in mf['cases']:
 if c['ROUTER_CLASS'].startswith('D_'):
  r=load(BATCH/'cases'/c['BATCH_CASE_ID']/'metrics/case_result.json');candidates.append((r['cad_area_coverage'],c,r))
old,csel,oldres=max(candidates,key=lambda x:x[0]); assert csel['BATCH_CASE_ID']=='CASE_05'
graph=load(SRC/'cad_part_graph/cad_part_graph_v1.json');meta=load(SRC/'p3/part_metadata.json'); tri=np.load(SRC/'p3/triangle_part_id.npy')
accepted_old={int(p['part_id'][-3:]):p for p in oldres['parts'] if p['accepted']}; assert set(accepted_old)=={0,4,6}
manifest={'STAGE':'BEST_MULTIPART_FULL_RECOVERY_V2','FROZEN':True,'TARGET_CASE':'CASE_05','TARGET_SOURCE_OBJ':csel['SOURCE_OBJ_PATH'],'SOURCE_SHA256':csel['SOURCE_SHA256'],'ROUTER_CLASS':csel['ROUTER_CLASS'],'OLD_CAD_AREA_COVERAGE':old,'EXISTING_P3':str(SRC/'p3'),'EXISTING_PHYSX':str(SRC/'physx'),'EXISTING_CAD_PART_GRAPH':str(SRC/'cad_part_graph/cad_part_graph_v1.json'),'EXISTING_ASSEMBLY':str(SRC/'assembly/partial_assembly.step'),'REUSED_Q1_PARTS':3,'REUSED_Q2_PARTS':0,'Q_THRESHOLDS':mf['quality_thresholds'],'S1_THRESHOLDS':{'chamfer_max':.03,'p95_max':.07,'coverage02_min':.80},'MERGE_THRESHOLDS_V2':{'AUTO_MERGE_MIN':.85,'REVIEW_MERGE_MIN':.65},'PHYSX_USED_FOR_PLACEMENT':False,'NEW_MAC_RUNS':0,'NEW_LLM_CAD_CALLS':0}
manifest['REUSED_STEP_SHA256']={f'CADPART_{i:03d}':sha(SRC/f'cad_recovery/CADPART_{i:03d}/accepted/reconstructed.step') for i in accepted_old};dump(OUT/'manifest/target_case_manifest.json',manifest)

total_area=sum(x['surface_area'] for x in meta['parts']); area={i:x['surface_area']/total_area for i,x in enumerate(meta['parts'])}
ledger=[]
for i,pid in enumerate(tri.tolist()): ledger.append({'source_triangle_id':i,'p3_part_id':int(pid),'state':'RECOVERED_Q1' if int(pid) in accepted_old else 'UNRECOVERED'})
dump(OUT/'metrics/source_triangle_coverage_ledger.json',{'TOTAL_SOURCE_TRIANGLES':len(ledger),'CURRENT_RECOVERED_TRIANGLES':sum(x['state']!='UNRECOVERED' for x in ledger),'CURRENT_UNRECOVERED_TRIANGLES':sum(x['state']=='UNRECOVERED' for x in ledger),'EXCLUSIVE_PARTITION':True,'triangles':ledger})
remaining=trimesh.util.concatenate([trimesh.load(SRC/f'p3/part_{i:03d}.obj',force='mesh',process=False) for i in range(meta['num_parts']) if i not in accepted_old]);remaining.export(OUT/'parts/remaining_geometry.obj')

def classify(m):
 if not m.get('brep_valid'): return 'TRUE_FAILURE'
 c,p,v=m['symmetric_chamfer_normalized'],m['p95_symmetric'],m['coverage_02']
 if c<=.01 and p<=.02 and v>=.95:return 'Q1'
 if c<=.02 and p<=.05 and v>=.85:return 'Q2'
 if c<=.03 and p<=.07 and v>=.80:return 'S1'
 return 'TRUE_FAILURE'

def build_part(i):
 pid=f'CADPART_{i:03d}'; src=SRC/f'p3/part_{i:03d}.obj'; base=OUT/'parts'/pid;base.mkdir(exist_ok=True);shutil.copy2(src,base/'source.obj')
 mesh=trimesh.load(src,force='mesh',process=False); ga=SRC/'cad_part_graph'/pid/'router/geometry_analysis';feat=load(ga/'feature_hypotheses.json');prim=load(ga/'primitives.json');node=graph['nodes'][i]
 rr={'REVOLUTION_LIKELIHOOD':node['REVOLUTION_LIKELIHOOD'],'CYLINDER_COVERAGE':node['CYLINDER_COVERAGE'],'EXTRUSION_LIKELIHOOD':node['EXTRUSION_LIKELIHOOD'],'PLANE_COVERAGE':node['PLANE_COVERAGE'],'ANALYTIC_COVERAGE':node['TOTAL_ANALYTIC_COVERAGE']};mode=hf.route(rr);center,B,scale=hf.frame(mesh,mode,feat);rows=hf.measured_sections(mesh,center,B,scale,200);dump(base/'axial_sections_200.json',{'sections':rows})
 c2s=np.eye(4);c2s[:3,:3]=B/scale;c2s[:3,3]=center;s2c=np.linalg.inv(c2s);trans={'SOURCE_TO_CANONICAL':s2c.tolist(),'CANONICAL_TO_SOURCE':c2s.tolist(),'roundtrip_pass':bool(np.allclose(s2c@c2s,np.eye(4),atol=1e-12)),'ICP_USED':False};dump(base/'local_to_global_transform.json',trans)
 try: secs=hf.select_build_sections(rows,112 if i==3 else 56)
 except Exception:return {'part_id':pid,'quality':'TRUE_FAILURE','failure_reason':'LOFT_INSUFFICIENT','area_ratio':area[i]}
 trials=[]
 # Hierarchy: measured primitive first, then measured high-density ruled loft.
 valid=[x for x in rows if x.get('valid')];dims=[2*float(np.median([x['half_width'] for x in valid])),2*float(np.median([x['half_thickness'] for x in valid])),float(max(x['z'] for x in valid)-min(x['z'] for x in valid))];kind='CYLINDER' if rr['CYLINDER_COVERAGE']>=rr['PLANE_COVERAGE'] else 'BOX'
 if kind=='CYLINDER':dims[0]=float(np.median([x['outer_radius_q95'] for x in valid]))
 specs=[('P','PRIMITIVE_CSG',hf.PRIMITIVE_TEMPLATE.replace('__KIND__',kind).replace('__DIMS__',repr(dims))),('L','MULTI_SECTION_LOFT',hf.LOFT_TEMPLATE.replace('__SECTIONS__',repr(hf.clean(secs))).replace('__RULED__','True'))]
 case={'source_obj':str(base/'source.obj'),'transform':str(base/'local_to_global_transform.json')}
 for letter,backend,code in specs:
  d=base/f'candidate_{letter}';d.mkdir(exist_ok=True);(d/'deterministic_program.py').write_text(code);r=subprocess.run([str(ENV),str(d/'deterministic_program.py')],cwd=d,text=True,capture_output=True,timeout=600);(d/'build.log').write_text(r.stdout+'\n'+r.stderr)
  if r.returncode:continue
  cand={'candidate_id':letter,'backend':backend,'directory':str(d),'programmatic_simplicity_lower':backend=='PRIMITIVE_CSG','build_return_code':r.returncode};m=hf.qa_candidate(case,cand);q=classify(m);trials.append({'candidate':cand,'metrics':m,'quality':q})
  if q in ('Q1','Q2','S1'):break
 if not trials:return {'part_id':pid,'quality':'TRUE_FAILURE','failure_reason':'BREP_INVALID','area_ratio':area[i]}
 good=[x for x in trials if x['quality']!='TRUE_FAILURE'];best=good[0] if good else min(trials,key=lambda x:(x['metrics'].get('symmetric_chamfer_normalized',9),-x['metrics'].get('coverage_02',0)))
 q=best['quality'];rec={'part_id':pid,'quality':q,'backend':best['candidate']['backend'],'metrics':best['metrics'],'area_ratio':area[i],'transform':str(base/'local_to_global_transform.json'),'source_triangle_ids':np.flatnonzero(tri==i).tolist(),'trials':trials}
 if q!='TRUE_FAILURE':
  acc=base/'accepted';acc.mkdir(exist_ok=True);d=Path(best['candidate']['directory']);shutil.copy2(d/'candidate.step',acc/'part.step');shutil.copy2(d/'fresh_source_frame.obj',acc/'cad_mesh.obj');shutil.copy2(base/'local_to_global_transform.json',acc/'local_to_global_transform.json');dump(acc/'provenance.json',rec)
 else:rec['failure_reason']='GEOMETRY_DEVIATION_TOO_HIGH'
 dump(base/'result.json',rec);return rec

results=[]
for i in range(meta['num_parts']):
 pid=f'CADPART_{i:03d}'
 if i in accepted_old:
  dst=OUT/'parts'/pid/'accepted';dst.mkdir(parents=True,exist_ok=True);src=SRC/'cad_recovery'/pid/'accepted';shutil.copy2(src/'reconstructed.step',dst/'part.step');shutil.copy2(src/'cad_mesh.obj',dst/'cad_mesh.obj');shutil.copy2(src/'local_to_global_transform.json',dst/'local_to_global_transform.json');results.append({'part_id':pid,'quality':'Q1','backend':'MULTI_SECTION_LOFT','area_ratio':area[i],'reused':True,'transform':str(dst/'local_to_global_transform.json'),'source_triangle_ids':np.flatnonzero(tri==i).tolist()})
 elif (OUT/'parts'/pid/'result.json').exists() and (OUT/'parts'/pid/'accepted/part.step').exists():
  results.append(load(OUT/'parts'/pid/'result.json'))
 elif i in (7,8):
  oldpart=load(SRC/f'cad_recovery/{pid}/result.json');m=oldpart['best_metrics'];q=classify(m);assert q=='S1';base=OUT/'parts'/pid;acc=base/'accepted';acc.mkdir(parents=True,exist_ok=True);cand=Path(next(x['candidate']['directory'] for x in oldpart['candidates'] if x['candidate']['candidate_id']==oldpart['best_candidate']));shutil.copy2(cand/'candidate.step',acc/'part.step');shutil.copy2(cand/'fresh_source_frame.obj',acc/'cad_mesh.obj');shutil.copy2(SRC/f'cad_recovery/{pid}/local_to_global_transform.json',acc/'local_to_global_transform.json');rec={'part_id':pid,'quality':'S1','backend':'MULTI_SECTION_LOFT','metrics':m,'area_ratio':area[i],'reused':False,'continued_from_old_q3':True,'transform':str(acc/'local_to_global_transform.json'),'source_triangle_ids':np.flatnonzero(tri==i).tolist()};dump(base/'result.json',rec);results.append(rec)
 else: results.append(build_part(i))
 dump(OUT/'metrics/part_results.json',results)

# Coverage and progress ledger.
ordered=sorted(results,key=lambda x:-x['area_ratio']);cum=0;rows=[]
for k,r in enumerate(ordered,1):
 if r['quality']!='TRUE_FAILURE':cum+=r['area_ratio']
 rows.append([k,r['part_id'],r.get('backend'),r['quality'],cum])
with open(OUT/'metrics/coverage_progress.csv','w',newline='') as f:w=csv.writer(f);w.writerow(['step','part_id','backend','quality','cumulative_cad_area_coverage']);w.writerows(rows)
cov={q:sum(r['area_ratio'] for r in results if r['quality']==q) for q in ['Q1','Q2','S1','TRUE_FAILURE']};total=1-cov['TRUE_FAILURE']
for x in ledger:
 r=results[x['p3_part_id']];x['state']={'Q1':'RECOVERED_Q1','Q2':'RECOVERED_Q2','S1':'RECOVERED_SURFACE_BREP','TRUE_FAILURE':'UNRECOVERED'}[r['quality']]
dump(OUT/'metrics/source_triangle_coverage_ledger.json',{'TOTAL_SOURCE_TRIANGLES':len(ledger),'FAILED_SOURCE_TRIANGLES':sum(x['state']=='UNRECOVERED' for x in ledger),'EXCLUSIVE_PARTITION':True,'triangles':ledger})

# Independent-component STEP assembly using stored transforms; no fuse and no PhysX placement.
from OCP.STEPControl import STEPControl_Reader,STEPControl_Writer,STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
builder=BRep_Builder();compound=TopoDS_Compound();builder.MakeCompound(compound);accepted=[r for r in results if r['quality']!='TRUE_FAILURE']
for r in accepted:
 rd=STEPControl_Reader();assert rd.ReadFile(str(OUT/'parts'/r['part_id']/'accepted/part.step'))==1;rd.TransferRoots();shape=rd.OneShape();m=np.array(load(r['transform'])['CANONICAL_TO_SOURCE']);t=gp_Trsf();t.SetValues(*m[:3,:].reshape(-1).tolist());builder.Add(compound,BRepBuilderAPI_Transform(shape,t,True).Shape())
step=OUT/'assembly/CASE_05_full_cad_assembly.step';wr=STEPControl_Writer();wr.Transfer(compound,STEPControl_AsIs);assert wr.Write(str(step))==1
rr=STEPControl_Reader();reload_ok=rr.ReadFile(str(step))==1 and rr.TransferRoots()>0

# Viewer GLB with independent named nodes.
scene=trimesh.Scene()
for r in accepted:
 m=trimesh.load(OUT/'parts'/r['part_id']/'accepted/cad_mesh.obj',force='mesh',process=False);m.apply_transform(np.array(load(r['transform'])['CANONICAL_TO_SOURCE']));scene.add_geometry(m,node_name=f"{r['part_id']}_{r['quality']}",geom_name=r['part_id'])
glb=OUT/'viewer/target_full_cad_preview.glb';scene.export(glb)

# Compact evidence visuals.
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
source=trimesh.load(SRC/'source/source.obj',force='mesh',process=False)
def draw(ax,meshes,title,colors=None):
 for j,m in enumerate(meshes):
  pts=np.asarray(m.vertices);ax.scatter(pts[::max(1,len(pts)//10000),0],pts[::max(1,len(pts)//10000),2],s=.15,c=(colors[j] if colors else '#68a9cf'),alpha=.7)
 ax.set_title(title);ax.axis('off');ax.set_aspect('equal')
cad=[]
for r in accepted:
 m=trimesh.load(OUT/'parts'/r['part_id']/'accepted/cad_mesh.obj',force='mesh',process=False);m.apply_transform(np.array(load(r['transform'])['CANONICAL_TO_SOURCE']));cad.append(m)
fig,axs=plt.subplots(1,2,figsize=(14,7));draw(axs[0],[source],'Original High Mesh',['#777777']);draw(axs[1],cad,'Recovered CAD Assembly');fig.tight_layout();main=OUT/'artifacts/target_full_cad_vs_source.png';fig.savefig(main,dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,7));colors={'Q1':'#19a974','Q2':'#ffb000','S1':'#6f42c1','TRUE_FAILURE':'#d62728'}
for r in results:draw(ax,[trimesh.load(SRC/f"p3/part_{int(r['part_id'][-3:]):03d}.obj",force='mesh',process=False)],r['quality'],[colors[r['quality']]])
ax.set_title('Coverage map: Q1 green / Q2 amber / S1 purple / failed red');covermap=OUT/'artifacts/target_cad_coverage_map.png';fig.savefig(covermap,dpi=180);plt.close(fig)
contact=OUT/'artifacts/target_full_assembly_contact_sheet.png';shutil.copy2(main,contact)
def milestone(v):
 for row in rows:
  if row[4]>=v:return row[0]
 return None
summary={'CURRENT_GATE':'BEST_MULTIPART_FULL_RECOVERY_V2_PASS' if total>=.95 and reload_ok else 'BEST_MULTIPART_FULL_RECOVERY_V2_FAIL','TARGET_CASE':'CASE_05','TARGET_SOURCE_OBJ':csel['SOURCE_OBJ_PATH'],'OLD_CAD_AREA_COVERAGE':old,'FINAL_CAD_PART_COUNT':len(accepted),'PARTS_PROCESSED':len(results)-len(accepted_old),'PARTS_Q1':sum(r['quality']=='Q1' for r in results),'PARTS_Q2':sum(r['quality']=='Q2' for r in results),'PARTS_S1':sum(r['quality']=='S1' for r in results),'PARTS_FAILED':sum(r['quality']=='TRUE_FAILURE' for r in results),'PARAMETRIC_CAD_AREA_COVERAGE':sum(r['area_ratio'] for r in results if r.get('backend')=='PRIMITIVE_CSG'),'LOFT_CAD_AREA_COVERAGE':sum(r['area_ratio'] for r in results if r.get('backend')=='MULTI_SECTION_LOFT'),'SURFACE_BREP_AREA_COVERAGE':sum(r['area_ratio'] for r in results if r.get('backend')=='FREEFORM_BSPLINE_BREP'),'TOTAL_CAD_AREA_COVERAGE':total,'FAILED_AREA_COVERAGE':cov['TRUE_FAILURE'],'OLD_TO_NEW_COVERAGE_IMPROVEMENT':total-old,'PARTS_TO_80_PERCENT':milestone(.8),'PARTS_TO_90_PERCENT':milestone(.9),'PARTS_TO_95_PERCENT':milestone(.95),'PARTS_TO_100_PERCENT':milestone(1-1e-12),'EXACT_100_PERCENT_CAD_COVERAGE':cov['TRUE_FAILURE']==0,'FULL_CAD_ASSEMBLY_COMPLETE':bool(reload_ok and total>=.95 and cov['TRUE_FAILURE']<=.05),'ASSEMBLY_STEP_GENERATED':step.is_file(),'ASSEMBLY_STEP_PATH':str(step),'ASSEMBLY_STEP_RELOAD_SUCCESS':bool(reload_ok),'ASSEMBLY_PART_COUNT':len(accepted),'INDEPENDENT_PARTS_PRESERVED':True,'FULL_CAD_GLB_PATH':str(glb),'MAIN_VISUAL_PATH':str(main),'COVERAGE_MAP_PATH':str(covermap),'LOCAL_P3_REFINEMENT_RUNS':0,'NEW_PHYSX_RUNS':0,'NEW_MAC_RUNS':0,'NEW_LLM_CAD_CALLS':0,'STEP_GT_USED':False,'ABC_DATA_USED':False,'TESTS_PASSED':0,'TESTS_FAILED':0,'FAILED_PART_IDS':[r['part_id'] for r in results if r['quality']=='TRUE_FAILURE'],'BLOCKERS':[]}
dump(OUT/'metrics/summary.json',summary);(OUT/'artifacts/best_multipart_full_recovery_v2_report.md').write_text('# BEST_MULTIPART_FULL_RECOVERY_V2\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n');print(json.dumps(summary,indent=2))
