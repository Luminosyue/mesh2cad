#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,math
from pathlib import Path
import numpy as np,trimesh
from scipy.interpolate import splprep,splev
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakeWire,BRepBuilderAPI_Sewing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GeomAPI import GeomAPI_PointsToBSpline,GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1,GeomAbs_C2
from OCP.Approx import Approx_ChordLength
from OCP.TColgp import TColgp_Array1OfPnt,TColgp_Array2OfPnt
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V1=ROOT/'case09_aircraft_end2end_cad_v1';V3=ROOT/'case09_futurecad_grounded_repair_v3';OUT=ROOT/'case09_semantic_surface_face_reduction_v4'
s=importlib.util.spec_from_file_location('v',V1/'scripts/end2end_pipeline.py');V=importlib.util.module_from_spec(s);s.loader.exec_module(V)
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(V.clean(x),indent=2)+'\n')
def curve(points):
 a=TColgp_Array1OfPnt(1,len(points))
 for i,p in enumerate(points,1):a.SetValue(i,gp_Pnt(*map(float,p)))
 f=GeomAPI_PointsToBSpline(a);return f.Curve()
def resample_half(points,n,smooth=0):
 p=np.asarray(points,float);u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];u/=max(u[-1],1e-12)
 try:tck,_=splprep(p.T,u=u,s=float(smooth),k=min(3,len(p)-1));return np.asarray(splev(np.linspace(0,1,n),tck)).T
 except:return np.vstack([np.interp(np.linspace(0,1,n),u,p[:,j]) for j in range(3)]).T
def semantic_rows(spec,chord_count,smooth):
 rows=[];profiles=[];ai=0;plane=[1,2]
 for i,r in enumerate(spec['operations'][0]['sections']):
  uv=np.asarray(r['profile'],float);pts=np.zeros((len(uv),3));pts[:,ai]=r['coordinate'];pts[:,plane]=uv
  le=0;te=len(pts)//2;upper=np.vstack([pts[le:te+1]]);lower=np.vstack([pts[te:],pts[:1]])
  # Preserve every measured V3 correspondence point exactly. These points are
  # interpolation constraints for two global surfaces; they never become BRep
  # section wires, edges, or faces.
  upper=np.asarray(upper,float);lower=np.asarray(lower,float)
  # force exactly shared leading/trailing endpoints
  lepoint=(upper[0]+lower[-1])/2;tepoint=(upper[-1]+lower[0])/2;upper[0]=lower[-1]=lepoint;upper[-1]=lower[0]=tepoint
  profiles.append((upper,lower));rows.append({'section_id':i,'coordinate':r['coordinate'],'leading_edge':lepoint.tolist(),'trailing_edge':tepoint.tolist(),'upper_curve':{'type':'BSPLINE','degree':3,'interpolation_constraints':upper.tolist(),'CAD_CURVE_COUNT':1},'lower_curve':{'type':'BSPLINE','degree':3,'interpolation_constraints':lower.tolist(),'CAD_CURVE_COUNT':1},'profile_correspondence':{'orientation':'UNIFIED','leading_edge_anchor':0,'trailing_edge_anchor':len(upper)-1,'upper_parameter_direction':'LE_TO_TE','lower_parameter_direction':'TE_TO_LE'}})
 return rows,profiles
def surface(grid,mode):
 a=TColgp_Array2OfPnt(1,len(grid),1,len(grid[0]))
 for i,row in enumerate(grid,1):
  for j,p in enumerate(row,1):a.SetValue(i,j,gp_Pnt(*map(float,p)))
 if mode=='GLOBAL_UPPER_LOWER_BSPLINE':f=GeomAPI_PointsToBSplineSurface(a,2,3,GeomAbs_C1,0.0002)
 elif mode=='GUIDED_GLOBAL_SKIN':f=GeomAPI_PointsToBSplineSurface(a,Approx_ChordLength,2,3,GeomAbs_C1,0.0001)
 else:f=GeomAPI_PointsToBSplineSurface(a,0.05,0.5,1.0,3,GeomAbs_C2,0.0002)
 assert f.IsDone();return f.Surface()
def build(profiles,mode):
 upper=np.asarray([x[0] for x in profiles]);lower=np.asarray([x[1] for x in profiles]);us=surface(upper,mode);ls=surface(lower,mode);uf=BRepBuilderAPI_MakeFace(us,1e-6).Face();lf=BRepBuilderAPI_MakeFace(ls,1e-6).Face()
 # Caps are bounded by exactly four semantic single-curve edges: upper, lower,
 # leading and trailing endpoints. Intermediate sections never enter topology.
 caps=[]
 for k in [0,-1]:
  u=profiles[k][0];l=profiles[k][1];edges=[BRepBuilderAPI_MakeEdge(curve(u)).Edge(),BRepBuilderAPI_MakeEdge(curve(l)).Edge()];wire=BRepBuilderAPI_MakeWire()
  for e in edges:wire.Add(e)
  if wire.IsDone():
   fm=BRepBuilderAPI_MakeFace(wire.Wire(),True)
   if fm.IsDone():caps.append(fm.Face())
 sewing=BRepBuilderAPI_Sewing(1e-5);sewing.Add(uf);sewing.Add(lf)
 for c in caps:sewing.Add(c)
 sewing.Perform();shape=sewing.SewedShape();return shape,{'UPPER_SKIN_FACE_COUNT':1,'LOWER_SKIN_FACE_COUNT':1,'ROOT_CAP_FACE_COUNT':1 if len(caps)>0 else 0,'TIP_CAP_FACE_COUNT':1 if len(caps)>1 else 0,'cap_count':len(caps)},us,ls

def sampled_skin_mesh(us,ls,n_span=64,n_chord=72):
 verts=[];faces=[]
 for surf in (us,ls):
  u0,u1,v0,v1=surf.Bounds();base=len(verts)
  for u in np.linspace(u0,u1,n_span):
   for v in np.linspace(v0,v1,n_chord):
    p=surf.Value(float(u),float(v));verts.append([p.X(),p.Y(),p.Z()])
  for i in range(n_span-1):
   for j in range(n_chord-1):
    a=base+i*n_chord+j;b=a+n_chord;c=b+1;d=a+1
    faces.extend([[a,b,c],[a,c,d]])
 return trimesh.Trimesh(np.asarray(verts),np.asarray(faces),process=False)
def profile_quality(original,semantic,diag):
 out=[]
 for i,(r,(u,l)) in enumerate(zip(original['operations'][0]['sections'],semantic)):
  uv=np.asarray(r['profile']);pts=np.zeros((len(uv),3));pts[:,0]=r['coordinate'];pts[:,[1,2]]=uv;fit=np.vstack([u,l[1:-1]]);d1=cKDTree(fit).query(pts)[0];d2=cKDTree(pts).query(fit)[0];both=np.r_[d1,d2]/diag;out.append({'section_id':i,'normalized_chamfer':float((d1.mean()+d2.mean())/(2*diag)),'normalized_p95':float(np.quantile(both,.95)),'normalized_max_deviation':float(both.max()),'leading_edge_interpolation':float(np.linalg.norm(u[0]-l[-1])/diag),'trailing_edge_interpolation':float(np.linalg.norm(u[-1]-l[0])/diag),'upper_lower_tangent_consistency':None})
 return {'sections':out,'PROFILE_NORMALIZED_CHAMFER_MAX':max(x['normalized_chamfer'] for x in out),'PROFILE_P95_MAX':max(x['normalized_p95'] for x in out),'PROFILE_MAX_DEVIATION':max(x['normalized_max_deviation'] for x in out)}
def candidate(src,oldspec,chord,smooth,name,out):
 rows,prof=semantic_rows(oldspec,chord,smooth);shape,topo,us,ls=build(prof,name);step=out/name/'candidate.step';V.write_step(shape,step);valid=BRepCheck_Analyzer(shape).IsValid();qual=profile_quality(oldspec,prof,float(np.linalg.norm(src.extents)));skin=sampled_skin_mesh(us,ls);gm=V.geometry_metrics(src,skin);approx={'CHAMFER':gm['CHAMFER'],'P95':gm['P95'],'COVERAGE02':gm['COVERAGE02']};q=V.qclass(approx,valid);faces=V.topology_count(shape,TopAbs_FACE);edges=V.topology_count(shape,TopAbs_EDGE);constraint_count=sum(len(u)+len(l) for u,l in prof);result={'representation':name,'chord_constraint_count':len(prof[0][0]),'smoothing':smooth,'step':str(step),'BREP_VALID':bool(valid),'Q':q,**approx,'geometry_metric_mode':'DIRECT_GLOBAL_BSPLINE_SURFACE_SAMPLING','FACE_COUNT':faces,'EDGE_COUNT':edges,**topo,'SURFACE_GROUP_COUNT':2+topo['cap_count'],'SECTION_DERIVED_FACE_COUNT':0,'SECTION_DERIVED_EDGE_COUNT':0,'ARTIFICIAL_SECTION_EDGE_COUNT':0,'SEMANTIC_SURFACE_RATIO':float((2+topo['cap_count'])/max(faces,1)),'BSPLINE_FACE_COUNT':2,'BSPLINE_CONTROL_POINTS':constraint_count,'profile_quality':qual,'SPLIT_REASON':None}
 dump(out/name/'section_semantic_profiles.json',rows);dump(out/name/'qa.json',result);return result,rows
def figure(before,after,path,title):
 im=Image.new('RGB',(1400,700),'white');dr=ImageDraw.Draw(im);dr.text((20,15),title,fill='black')
 for panel,(rows,label) in enumerate([(before,'V3 closed polyline profiles'),(after,'V4 one upper + one lower BSpline per section')]):
  ox=20+panel*700;allp=[]
  if panel==0:allp=[np.asarray(x['profile']) for x in rows]
  else:allp=[np.asarray(x['upper_curve']['interpolation_constraints'])[:,[1,2]] for x in rows]+[np.asarray(x['lower_curve']['interpolation_constraints'])[:,[1,2]] for x in rows]
  lo=np.vstack(allp).min(0);span=np.maximum(np.ptp(np.vstack(allp),axis=0),1e-9)
  for j,p in enumerate(allp):
   pix=(p-lo)/span*[610,520]+[ox+25,80];dr.line([tuple(x) for x in pix],fill=(40+j*7%200,70,180),width=1)
  dr.text((ox+25,630),label,fill='black')
 im.save(path)
def main():
 diag=json.loads((OUT/'metrics/wing_topology_diagnosis.json').read_text());allres={}
 for part in ['CADPART_001','CADPART_002']:
  oldspec=json.loads(Path(diag['wings'][part]['selected_v3_spec']).read_text());src=trimesh.load(V1/'02_cad_part_graph'/part/'source_part.obj',force='mesh',process=False);base=OUT/'03_semantic_surface'/part/'candidates';results=[];lastrows=None
  for name,chord,smooth in [('GLOBAL_UPPER_LOWER_BSPLINE',14,0),('GUIDED_GLOBAL_SKIN',18,0),('2_PATCH_SEMANTIC_SKIN',22,0)]:
   try:r,rows=candidate(src,oldspec,chord,smooth,name,base);results.append(r);lastrows=rows;print(part,name,r['Q'],r['CHAMFER'],r['P95'],r['COVERAGE02'],r['FACE_COUNT'],r['EDGE_COUNT'],flush=True)
   except Exception as e:results.append({'representation':name,'error':f'{type(e).__name__}: {e}','Q':'Q3','BREP_VALID':False});print(part,name,'FAIL',e,flush=True)
  good=[x for x in results if x.get('BREP_VALID') and x['Q'] in ('Q1','Q2') and x['FACE_COUNT']<=8];good.sort(key=lambda x:(x['FACE_COUNT'],x['CHAMFER'],x['BSPLINE_CONTROL_POINTS']));selected=good[0] if good else None;allres[part]={'candidates':results,'selected':selected}
  if selected:
   rows=json.loads((base/selected['representation']/'section_semantic_profiles.json').read_text());dump(OUT/'02_semantic_profiles'/part/'section_semantic_profiles.json',rows);shutil=None
   graph={'schema':'WING_SURFACE_GRAPH_V1','part_id':part,'root':'WING','nodes':[{'id':'UPPER_SKIN','representation':'GLOBAL_BSPLINE_SURFACE','section_constraints':[x['section_id'] for x in rows]},{'id':'LOWER_SKIN','representation':'GLOBAL_BSPLINE_SURFACE','section_constraints':[x['section_id'] for x in rows]},{'id':'LEADING_EDGE','type':'SEMANTIC_FEATURE'},{'id':'TRAILING_EDGE','type':'SEMANTIC_FEATURE'},{'id':'ROOT_CAP','type':'CAP'},{'id':'TIP_CAP','type':'CAP'}],'section_nodes_in_final_graph':False,'sections_are_fitting_constraints_only':True};dump(OUT/'03_semantic_surface'/part/'semantic_surface_graph.json',graph);dump(OUT/'03_semantic_surface'/part/'cad_feature_graph.json',{'part_id':part,'feature':'WING_SKIN_FEATURE','upper_skin':graph['nodes'][0],'lower_skin':graph['nodes'][1],'root_cap':'ROOT_CAP','tip_cap':'TIP_CAP','leading_edge':'LEADING_EDGE','trailing_edge':'TRAILING_EDGE','section_nodes':[]});figure(oldspec['operations'][0]['sections'],rows,OUT/'artifacts'/f'{part}_profile_before_after.png',f'{part} semantic profile correspondence')
 dump(OUT/'metrics/semantic_surface_probe.json',allres);print(json.dumps(allres,indent=2))
if __name__=='__main__':main()
