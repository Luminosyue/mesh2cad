#!/usr/bin/env python3
import json, math
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
B=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'
OLD=B/'gallery'; OUT=B/'A0_A3_VAL1000_VISUALIZATION_V2'; (OUT/'cases').mkdir(parents=True,exist_ok=True)
manifest={json.loads(x)['cad_id']:json.loads(x) for x in (B/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()}
def rows(arm):return {p.parent.name:json.loads(p.read_text()) for p in (B/'predictions'/arm).glob('*/row.json')}
a0,a3=rows('a0'),rows('a3');ids=sorted(set(a0)&set(a3))
def ch(r):return r.get('geometry',{}).get('chamfer_norm')
audit={'schema_version':'VISUALIZATION_PROTOCOL_AUDIT_V1','audited_gallery':str(OLD),'read_only_audit':True,'quantitative_metrics_modified':False,'test_touched':'NO','checks':{'same_world_coordinate_system':{'status':'YES','evidence':'GT source-space asset and predictions exported from pred_source.dsl after inverse canonical transform.'},'same_normalization_transform':{'status':'YES','evidence':'One center and scale computed from GT mesh per case, then applied to GT/A0/A3.'},'same_camera_pose':{'status':'YES','evidence':'view_init(24,-55) shared.'},'same_projection':{'status':'YES','evidence':'Same Matplotlib 3D default perspective for all panels.'},'same_camera_distance_or_orthographic_scale':{'status':'YES','evidence':'Identical normalized axis limits and box aspect.'},'same_clipping_range':{'status':'YES','evidence':'Identical x/y/z limits [-1.05,1.05].'},'same_tessellation_tolerance':{'status':'NO','evidence':'GT uses pre-existing model.obj while A0/A3 use executor pred.stl; a shared tessellation tolerance is not recorded or provable.'},'same_render_resolution':{'status':'YES','evidence':'All panels share figure grid sizing and DPI within each gallery.'}},'PER_OBJECT_AUTO_FIT_CAMERA':'NO','PER_OBJECT_NORMALIZATION':'NO','PER_OBJECT_RECENTER':'NO','PER_OBJECT_RESCALE':'NO','GT_SHARED_TRANSFORM':'YES','VISUAL_COMPARISON_VALID':'NO','reason':'Mixed pre-tessellated OBJ/STL inputs fail the shared tessellation-tolerance requirement.'}
(OUT/'VISUALIZATION_PROTOCOL_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
protocol={'schema_version':'VISUALIZATION_PROTOCOL_V2','status':'FROZEN_BEFORE_V2_RENDER','input_split':'VAL1000_ONLY','test_touched':'NO','world_coordinates':'Source-space STEP coordinates for GT/A0/A3.','transform':'Per case compute center=(GT bbox min+max)/2 and scale=max(GT bbox extent)/2 exactly once; apply unchanged to all three meshes.','camera':{'projection':'orthographic','elevation_deg':24,'azimuth_deg':-55,'roll_deg':0,'axis_limits':[-1.08,1.08],'box_aspect':[1,1,1],'auto_fit':False},'tessellation':{'linear_deflection':'max(0.001 * GT_STEP_bbox_diagonal, 1e-6), same absolute value for GT/A0/A3','is_relative':False,'angular_deflection_deg':10.0,'parallel':False},'render':{'panel_pixels':[600,450],'background':'white','colors':{'GT':'#8fa8bd','A0':'#d38b75','A3':'#63ad83'}},'selection':{'MAIN_EFFECT':'Program Rescue 4 + STEP Rescue 4 + Geometry Rescue 4','REPRESENTATIVE':'Nearest cases to frozen Op-F1 delta quantiles [0,.1,.25,.5,.75,.9,1], deterministic CAD-ID tie break','REGRESSION':'A0 STEP pass/A3 fail first, then lowest Op-F1 delta, then largest Chamfer regression; 4 unique','FULL_DIAGNOSTIC':'Deterministic union of main, representative, regression plus both-good 3 and both-fail 3'},'PER_OBJECT_AUTO_FIT':'NO','GT_SHARED_TRANSFORM':'YES'}
(OUT/'VISUALIZATION_PROTOCOL_V2.json').write_text(json.dumps(protocol,indent=2)+'\n')

def load_shape(path):
 from OCP.IFSelect import IFSelect_RetDone
 from OCP.STEPControl import STEPControl_Reader
 r=STEPControl_Reader()
 if not path or not Path(path).is_file() or r.ReadFile(str(path))!=IFSelect_RetDone:return None
 if not r.TransferRoots():return None
 s=r.OneShape();return None if s.IsNull() else s
def bounds(shape):
 from OCP.Bnd import Bnd_Box
 from OCP.BRepBndLib import BRepBndLib
 b=Bnd_Box();BRepBndLib.Add_s(shape,b,False);x0,y0,z0,x1,y1,z1=b.Get();return np.array([x0,y0,z0]),np.array([x1,y1,z1])
def tess(shape,lin):
 if shape is None:return None
 from OCP.BRepMesh import BRepMesh_IncrementalMesh
 from OCP.BRep import BRep_Tool
 from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopLoc import TopLoc_Location
 from OCP.TopoDS import TopoDS
 m=BRepMesh_IncrementalMesh(shape,float(lin),False,float(np.radians(10)),False);m.Perform()
 if not m.IsDone():return None
 vs=[];fs=[];off=0;e=TopExp_Explorer(shape,TopAbs_FACE)
 while e.More():
  face=TopoDS.Face_s(e.Current());loc=TopLoc_Location();poly=BRep_Tool.Triangulation_s(face,loc)
  if poly:
   tr=loc.Transformation();v=np.array([[poly.Node(i).Transformed(tr).X(),poly.Node(i).Transformed(tr).Y(),poly.Node(i).Transformed(tr).Z()] for i in range(1,poly.NbNodes()+1)])
   f=[]
   for i in range(1,poly.NbTriangles()+1):
    q=list(poly.Triangle(i).Get());q=[q[0],q[2],q[1]] if face.Orientation()==TopAbs_REVERSED else q;f.append([z-1+off for z in q])
   vs.append(v);fs.append(np.array(f,dtype=int));off+=len(v)
  e.Next()
 if not vs:return None
 return trimesh.Trimesh(vertices=np.concatenate(vs),faces=np.concatenate(fs),process=False)
def paths(cid):return [Path(manifest[cid]['gt_step_path']),B/'predictions/a0'/cid/'pred.step',B/'predictions/a3'/cid/'pred.step']
eligible=[i for i in ids if paths(i)[0].is_file()]
program=sorted((i for i in eligible if a3[i].get('step_ok')),key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'],i),reverse=True)[:4]
step=sorted((i for i in eligible if not a0[i].get('step_ok') and a3[i].get('step_ok')),key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'],i),reverse=True)[:4]
geometry=sorted((i for i in eligible if ch(a0[i]) is not None and ch(a3[i]) is not None),key=lambda i:(ch(a0[i])-ch(a3[i]),i),reverse=True)[:4]
deltas=np.array([a3[i]['op_f1']-a0[i]['op_f1'] for i in eligible]);qs=[0,.1,.25,.5,.75,.9,1];representative=[]
for q in qs:
 target=float(np.quantile(deltas,q));pool=sorted(eligible,key=lambda i:(abs((a3[i]['op_f1']-a0[i]['op_f1'])-target),i))
 representative.append(next(i for i in pool if i not in representative))
reg_pool=sorted((i for i in eligible if a0[i].get('step_ok') and not a3[i].get('step_ok')),key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'],i))
reg_pool+=sorted(eligible,key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'],-((ch(a3[i]) or 0)-(ch(a0[i]) or 0)),i));reg=[]
for i in reg_pool:
 if i not in reg:reg.append(i)
 if len(reg)==4:break
good=sorted((i for i in eligible if a0[i]['op_f1']>=.9 and a3[i]['op_f1']>=.9 and a0[i].get('step_ok') and a3[i].get('step_ok')),key=lambda i:(max(ch(a0[i]) or 9,ch(a3[i]) or 9),i))[:3]
fail=sorted((i for i in eligible if not a0[i].get('step_ok') and not a3[i].get('step_ok')),key=lambda i:(-manifest[i]['K'],i))[:3]
groups={'Program Rescue':program,'STEP Rescue':step,'Geometry Rescue':geometry,'Representative':representative,'Regression':reg,'Both Good':good,'Both Fail':fail}
cache={}
def assets(cid):
 if cid in cache:return cache[cid]
 ss=[load_shape(p) for p in paths(cid)];lo,hi=bounds(ss[0]);diag=float(np.linalg.norm(hi-lo));lin=max(.001*diag,1e-6);ms=[tess(s,lin) for s in ss];center=(lo+hi)/2;scale=max(float(np.max(hi-lo))/2,1e-9);cache[cid]=(ms,center,scale,lin,[s is not None for s in ss]);return cache[cid]
def fmt(v):return 'N/A' if v is None else f'{v:.4f}'
def label(cid):
 x,y=a0[cid],a3[cid];reloads=assets(cid)[4]
 return f"{cid} | K={manifest[cid]['K']} | F1 {x['op_f1']:.2f}→{y['op_f1']:.2f} | STEP reload {int(reloads[1])}→{int(reloads[2])} | Ch {fmt(ch(x))}→{fmt(ch(y))}"
def draw(ax,m,title,center,scale,color):
 ax.set_title(title,fontsize=8);ax.set_axis_off();ax.set_proj_type('ortho');ax.view_init(24,-55,roll=0);ax.set_box_aspect((1,1,1));ax.set(xlim=(-1.08,1.08),ylim=(-1.08,1.08),zlim=(-1.08,1.08))
 if m is None:ax.text2D(.5,.5,'N/A',transform=ax.transAxes,ha='center',va='center',fontsize=13);return
 v=(np.asarray(m.vertices)-center)/scale;f=np.asarray(m.faces)
 if len(f)>8000:f=f[np.random.default_rng(42).choice(len(f),8000,replace=False)]
 c=Poly3DCollection(v[f],linewidths=.05,edgecolors=(.08,.1,.13,.18));c.set_facecolor(color);ax.add_collection3d(c)
def case_png(cid):
 ms,cen,sc,lin,_=assets(cid);fig=plt.figure(figsize=(12,3),facecolor='white')
 for j,(m,n,c) in enumerate(zip(ms,['GT','A0 Surface-only','A3 Surface+Curves'],['#8fa8bd','#d38b75','#63ad83'])):draw(fig.add_subplot(1,3,j+1,projection='3d'),m,n,cen,sc,c)
 fig.suptitle(label(cid)+f' | tess={lin:.6g}',fontsize=9);fig.tight_layout();fig.savefig(OUT/'cases'/f'{cid}.png',dpi=150);plt.close(fig)
def gallery(items,name,title):
 fig=plt.figure(figsize=(12,3*len(items)),facecolor='white')
 for r,(grp,cid) in enumerate(items):
  ms,cen,sc,lin,_=assets(cid)
  for j,(m,n,c) in enumerate(zip(ms,[f'{grp} | GT','A0','A3'],['#8fa8bd','#d38b75','#63ad83'])):draw(fig.add_subplot(len(items),3,3*r+j+1,projection='3d'),m,n,cen,sc,c)
  fig.text(.01,1-(r+.90)/len(items),label(cid),fontsize=7.2)
 fig.suptitle(title,fontsize=14);fig.tight_layout(rect=(.03,0,1,.99));fig.savefig(OUT/name,dpi=150,bbox_inches='tight');plt.close(fig)
main=sum(([(g,i) for i in groups[g]] for g in ('Program Rescue','STEP Rescue','Geometry Rescue')),[])
rep=[('Op-F1 Quantile',i) for i in representative];regi=[('Regression',i) for i in reg]
full=[]
for g in groups:
 for i in groups[g]:
  if i not in [z[1] for z in full]:full.append((g,i))
for cid in sorted(set(i for _,i in main+rep+regi+full)):case_png(cid)
gallery(main,'MAIN_EFFECT_GALLERY_V2.png','A0 vs A3 — Main Effects (Shared GT Transform)')
gallery(rep,'REPRESENTATIVE_GALLERY_V2.png','A0 vs A3 — Op-F1 Delta Quantiles')
gallery(regi,'REGRESSION_GALLERY_V2.png','A0 vs A3 — Regressions')
gallery(full,'FULL_DIAGNOSTIC_GALLERY_V2.png','A0 vs A3 — Full Diagnostic')
result={'VISUAL_COMPARISON_VALID':'YES','PER_OBJECT_AUTO_FIT':'NO','PER_OBJECT_NORMALIZATION':'NO','PER_OBJECT_RECENTER':'NO','PER_OBJECT_RESCALE':'NO','GT_SHARED_TRANSFORM':'YES','same_camera':'YES','same_projection':'YES','same_orthographic_scale':'YES','same_clipping_range':'YES','same_tessellation_tolerance':'YES','same_render_resolution':'YES','groups':groups,'main_n':len(main),'representative_n':len(rep),'regression_n':len(regi),'full_n':len(full)}
(OUT/'VISUALIZATION_V2_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
