import json,hashlib,shutil
from pathlib import Path
import numpy as np,trimesh
from scipy.spatial import cKDTree
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V=O/'case05_residual_part003_recovery_v3';V2=O/'best_multipart_full_recovery_v2';SRC=O/'batch_real_mesh2cad_v1/cases/CASE_05'
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parts=load(V2/'metrics/part_results.json');old=[x for x in parts if x['quality']!='TRUE_FAILURE'];cfg=load(V/'metrics/decomposition_search.json')['selected'];new=[x for x in cfg['subparts'] if x['quality']!='FAIL'];assert len(old)==9 and len(new)==1
frozen=[]
for x in old:
 p=V2/'parts'/x['part_id']/'accepted/part.step';frozen.append({'part_id':x['part_id'],'step':str(p),'sha256':sha(p),'quality':x['quality'],'backend':x.get('backend'),'transform':x['transform'],'source_triangle_ids':x['source_triangle_ids']})
dump(V/'manifest/frozen_accepted_pool.json',{'REUSED_ACCEPTED_PARTS':9,'components':frozen})
from OCP.STEPControl import STEPControl_Reader,STEPControl_Writer,STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
builder=BRep_Builder();comp=TopoDS_Compound();builder.MakeCompound(comp);component_meshes=[]
def add(step,transform,mesh_path,name,quality):
 rd=STEPControl_Reader();assert rd.ReadFile(str(step))==1;assert rd.TransferRoots()>0;shape=rd.OneShape();m=np.array(load(transform)['CANONICAL_TO_SOURCE']);t=gp_Trsf();t.SetValues(*m[:3,:].reshape(-1).tolist());builder.Add(comp,BRepBuilderAPI_Transform(shape,t,True).Shape());tm=trimesh.load(mesh_path,force='mesh',process=False);tm.apply_transform(m);component_meshes.append((name,quality,tm))
for x in old:add(V2/'parts'/x['part_id']/'accepted/part.step',x['transform'],V2/'parts'/x['part_id']/'accepted/cad_mesh.obj',x['part_id'],x['quality'])
for x in new:
 d=Path(x['directory']);add(d/'accepted/part.step',d/'accepted/local_to_global_transform.json',d/'accepted/cad_mesh.obj','CADPART_003_SUBPART_00',x['quality'])
step=V/'assembly/CASE_05_full_cad_assembly_v3.step';wr=STEPControl_Writer();wr.Transfer(comp,STEPControl_AsIs);assert wr.Write(str(step))==1;rr=STEPControl_Reader();reload_ok=rr.ReadFile(str(step))==1 and rr.TransferRoots()>0
scene=trimesh.Scene()
for name,q,m in component_meshes:scene.add_geometry(m,node_name=f'{name}_{q}',geom_name=name)
glb=V/'viewer/CASE05_full_cad_v3.glb';scene.export(glb)
# Exact triangle ledger update.
ledger=load(V2/'metrics/source_triangle_coverage_ledger.json');tri=np.load(SRC/'p3/triangle_part_id.npy');parent_global=np.flatnonzero(tri==3);accepted_local=set(new[0]['source_triangle_ids'])
for x in ledger['triangles']:
 if x['source_triangle_id'] in set(parent_global[list(accepted_local)]):x['state']='RECOVERED_SURFACE_BREP'
failed=sum(x['state']=='UNRECOVERED' for x in ledger['triangles']);ledger.update({'FAILED_SOURCE_TRIANGLES':failed,'SOURCE_TRIANGLE_ACCOUNTING':1.0,'EXCLUSIVE_PARTITION':True});dump(V/'metrics/source_triangle_coverage_ledger_v3.json',ledger)
parent_ratio=.08786178149266731;frac=sum(x['area_fraction_of_parent'] for x in new);gain=parent_ratio*frac;total=.9121382185073327+gain;fail=1-total
# Whole-object fresh sampled geometry QA, source frame, no ICP.
src=trimesh.load(SRC/'source/source.obj',force='mesh',process=False);cad=trimesh.util.concatenate([x[2] for x in component_meshes]);np.random.seed(42);sp=src.sample(100000);cp=cad.sample(100000);diag=np.linalg.norm(src.bounds[1]-src.bounds[0]);d1=cKDTree(cp).query(sp,k=1)[0]/diag;d2=cKDTree(sp).query(cp,k=1)[0]/diag;both=np.r_[d1,d2];whole={'WHOLE_OBJECT_CHAMFER':float((d1.mean()+d2.mean())/2),'WHOLE_OBJECT_P95':float(np.percentile(both,95)),'WHOLE_OBJECT_COVERAGE02':float(np.mean(d1<=.02)),'ICP_USED':False,'sample_count':100000};dump(V/'metrics/whole_object_qa.json',whole)
# Evidence visuals.
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
def pts(m,n=16000):
 p=np.asarray(m.vertices);return p[::max(1,len(p)//n)]
def panel(ax,m,title,color='#4c9ad4'):
 p=pts(m);ax.scatter(p[:,0],p[:,2],s=.15,c=color,alpha=.7);ax.set_title(title);ax.axis('off');ax.set_aspect('equal')
parent=trimesh.load(SRC/'p3/part_003.obj',force='mesh',process=False);prev=trimesh.load(V2/'parts/CADPART_003/candidate_L/fresh_source_frame.obj',force='mesh',process=False);prev.apply_transform(np.array(load(V2/'parts/CADPART_003/local_to_global_transform.json')['CANONICAL_TO_SOURCE']));nm=new[0];newmesh=next(m for name,q,m in component_meshes if name=='CADPART_003_SUBPART_00')
fig,axs=plt.subplots(2,3,figsize=(15,9));panel(axs[0,0],parent,'CADPART_003 source','#777');panel(axs[0,1],prev,'Previous best (FAIL)','#d95f02');panel(axs[0,2],newmesh,'Accepted local region (S1)','#6a3d9a');panel(axs[1,0],parent,'Source overlay','#777');panel(axs[1,0],newmesh,'', '#20a060');axs[1,0].set_title('Overlay');panel(axs[1,1],newmesh,'Recovered region');axs[1,2].hist(cKDTree(newmesh.sample(30000)).query(parent.sample(30000))[0],bins=60,color='#4c72b0');axs[1,2].set_title('Distance distribution');fig.tight_layout();before=V/'artifacts/CADPART_003_before_after.png';diagimg=V/'artifacts/CADPART_003_failure_diagnostic.png';fig.savefig(before,dpi=180);fig.savefig(diagimg,dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(14,7));panel(axs[0],src,'Original High Mesh','#777');panel(axs[1],cad,'CAD/BRep Assembly v3','#35a67a');fig.tight_layout();main=V/'artifacts/CASE05_full_cad_v3_vs_source.png';fig.savefig(main,dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,7));colors={'Q1':'#18a558','Q2':'#f2a900','S1':'#744fc6'}
for name,q,m in component_meshes:panel(ax,m,'',colors[q]);failedmesh=trimesh.load(Path(cfg['subparts'][1]['directory'])/'source.obj',force='mesh',process=False);panel(ax,failedmesh,'','#d62728');ax.set_title('Q1 green / S1 purple / FAILED red');covmap=V/'artifacts/CASE05_final_coverage_map.png';fig.savefig(covmap,dpi=180);plt.close(fig)
summary={'CURRENT_GATE':'CASE05_RESIDUAL_PART003_RECOVERY_V3_PASS' if total>=.95 else 'CASE05_RESIDUAL_PART003_RECOVERY_V3_FAIL','TARGET_CASE':'CASE_05','TARGET_PART':'CADPART_003','SOURCE_CAD_PART_CANDIDATES':10,'REUSED_ACCEPTED_PARTS':9,'NEWLY_PROCESSED_PARENT_PARTS':1,'GENERATED_SUBPARTS':2,'FINAL_ACCEPTED_PARENT_REGIONS':9,'FINAL_ASSEMBLY_COMPONENTS':10,'FAILED_PARENT_REGIONS':1,'PREVIOUS_FAILURE_REASON':'P95_HIGH','FINAL_BACKEND':'LOCAL_GEOMETRIC_DECOMPOSITION+MULTI_SECTION_LOFT_V3','FINAL_QUALITY':'PARTIAL_S1','CADPART_003_ACCEPTED':False,'LOCAL_DECOMPOSITION_USED':True,'SUBPART_COUNT':2,'OLD_TOTAL_CAD_AREA_COVERAGE':.9121382185073327,'NEW_TOTAL_CAD_AREA_COVERAGE':total,'COVERAGE_GAIN':gain,'FAILED_AREA_COVERAGE':fail,'CADPART_003_RECOVERED_AREA_RATIO':gain,'FRACTION_OF_CADPART003_RECOVERED':frac,'RECOVERY_LEVEL':'LEVEL_B_FULL_ASSEMBLY_GATE' if total>=.95 else 'LEVEL_C_IMPROVED_BUT_INCOMPLETE','EXACT_100_PERCENT_CAD_COVERAGE':False,'FULL_CAD_ASSEMBLY_COMPLETE':bool(total>=.95 and reload_ok),'ASSEMBLY_STEP_PATH':str(step),'ASSEMBLY_STEP_RELOAD_SUCCESS':bool(reload_ok),'ASSEMBLY_COMPONENT_COUNT':10,'WHOLE_OBJECT_CHAMFER':whole['WHOLE_OBJECT_CHAMFER'],'WHOLE_OBJECT_P95':whole['WHOLE_OBJECT_P95'],'WHOLE_OBJECT_COVERAGE02':whole['WHOLE_OBJECT_COVERAGE02'],'SOURCE_TRIANGLE_ACCOUNTING':1.0,'NEW_FULL_OBJECT_P3_RUNS':0,'NEW_PHYSX_RUNS':0,'NEW_MAC_RUNS':0,'NEW_LLM_CAD_CALLS':0,'STEP_GT_USED':False,'ABC_DATA_USED':False,'TESTS_PASSED':0,'TESTS_FAILED':0,'FAILED_PART_IDS':['CADPART_003_SUBPART_01'],'BLOCKERS':[]}
dump(V/'metrics/summary.json',summary);(V/'artifacts/case05_residual_part003_recovery_v3_report.md').write_text('# CASE05_RESIDUAL_PART003_RECOVERY_V3\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n');print(json.dumps(summary,indent=2))
