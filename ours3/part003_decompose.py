import importlib.util,json,subprocess,shutil
from pathlib import Path
import numpy as np,trimesh
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V=O/'case05_residual_part003_recovery_v3';SRC=O/'batch_real_mesh2cad_v1/cases/CASE_05';OLD=O/'best_multipart_full_recovery_v2/parts/CADPART_003';ENV='/data/miniconda3/envs/multi_agent_cad/bin/python'
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def mod(p,n):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
hf=mod(O/'high_fidelity_part_recovery_v2/scripts/pipeline.py','hfdec');mesh=trimesh.load(SRC/'p3/part_003.obj',force='mesh',process=False);parent_transform=load(OLD/'local_to_global_transform.json')
feat=load(SRC/'cad_part_graph/CADPART_003/router/geometry_analysis/feature_hypotheses.json');g=load(SRC/'cad_part_graph/cad_part_graph_v1.json')['nodes'][3];rr={'REVOLUTION_LIKELIHOOD':g['REVOLUTION_LIKELIHOOD'],'CYLINDER_COVERAGE':g['CYLINDER_COVERAGE'],'EXTRUSION_LIKELIHOOD':g['EXTRUSION_LIKELIHOOD'],'PLANE_COVERAGE':g['PLANE_COVERAGE'],'ANALYTIC_COVERAGE':g['TOTAL_ANALYTIC_COVERAGE']};mode=hf.route(rr)
def cls(m):
 if not m.get('brep_valid'):return 'FAIL'
 a,b,c=m['symmetric_chamfer_normalized'],m['p95_symmetric'],m['coverage_02'];return 'Q1' if a<=.01 and b<=.02 and c>=.95 else 'Q2' if a<=.02 and b<=.05 and c>=.85 else 'S1' if a<=.03 and b<=.07 and c>=.80 else 'FAIL'
center=mesh.vertices.mean(0);_,_,vh=np.linalg.svd(mesh.vertices-center,full_matrices=False);axis=vh[0];fc=mesh.triangles_center@axis;fa=mesh.area_faces;order=np.argsort(fc);cum=np.cumsum(fa[order])/fa.sum()
all_configs=[];accepted_config=None
for bands in [2,3,4]:
 labels=np.zeros(len(mesh.faces),int)
 for j,idx in enumerate(order):labels[idx]=min(bands-1,int(cum[j]*bands))
 recs=[]
 for b in range(bands):
  ids=np.flatnonzero(labels==b);sub=mesh.submesh([ids],append=True,repair=False);d=V/f'parts/CADPART_003/subparts_b{bands}/SUBPART_{b:02d}';d.mkdir(parents=True,exist_ok=True);src=d/'source.obj';sub.export(src)
  try:
   c,B,scale=hf.frame(sub,mode,feat);rows=hf.measured_sections(sub,c,B,scale,120);secs=hf.select_build_sections(rows,40);c2s=np.eye(4);c2s[:3,:3]=B/scale;c2s[:3,3]=c;s2c=np.linalg.inv(c2s);dump(d/'local_to_global_transform.json',{'SOURCE_TO_CANONICAL':s2c.tolist(),'CANONICAL_TO_SOURCE':c2s.tolist(),'roundtrip_pass':bool(np.allclose(s2c@c2s,np.eye(4),atol=1e-12)),'ICP_USED':False});bd=d/'candidate_loft';bd.mkdir(exist_ok=True);code=hf.LOFT_TEMPLATE.replace('__SECTIONS__',repr(hf.clean(secs))).replace('__RULED__','True');(bd/'deterministic_program.py').write_text(code);r=subprocess.run([ENV,str(bd/'deterministic_program.py')],cwd=bd,text=True,capture_output=True,timeout=300);(bd/'build.log').write_text(r.stdout+'\n'+r.stderr);cand={'candidate_id':f'DECOMP_{bands}_{b}','backend':'MULTI_SECTION_LOFT_V3','directory':str(bd),'programmatic_simplicity_lower':True,'build_return_code':r.returncode};m=hf.qa_candidate({'source_obj':str(src),'transform':str(d/'local_to_global_transform.json')},cand) if r.returncode==0 else {};q=cls(m)
  except Exception as e:m={};q='FAIL'
  ar=float(fa[ids].sum()/fa.sum());rec={'subpart_id':f'SUBPART_{b:02d}','source_triangle_ids':ids.tolist(),'area_fraction_of_parent':ar,'quality':q,'metrics':m,'directory':str(d)};recs.append(rec);dump(d/'result.json',rec);print(bands,b,q,ar,m.get('p95_symmetric'),flush=True)
  if q!='FAIL':acc=d/'accepted';acc.mkdir(exist_ok=True);shutil.copy2(bd/'candidate.step',acc/'part.step');shutil.copy2(bd/'fresh_source_frame.obj',acc/'cad_mesh.obj');shutil.copy2(d/'local_to_global_transform.json',acc/'local_to_global_transform.json')
 accounting=sum(len(x['source_triangle_ids']) for x in recs)/len(mesh.faces);recovered=sum(x['area_fraction_of_parent'] for x in recs if x['quality']!='FAIL');cfg={'bands':bands,'subparts':recs,'SOURCE_TRIANGLE_ACCOUNTING':accounting,'recovered_fraction':recovered};all_configs.append(cfg)
 if recovered>=.431:accepted_config=cfg;break
dump(V/'metrics/decomposition_search.json',{'configurations':all_configs,'selected':accepted_config,'candidate_configurations_total':len(all_configs)+1})
print('SELECTED',None if accepted_config is None else accepted_config['bands'],None if accepted_config is None else accepted_config['recovered_fraction'])
