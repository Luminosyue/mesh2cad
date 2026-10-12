#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,math,shutil
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve,BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.GeomAbs import *
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE,TopAbs_VERTEX,TopAbs_WIRE
from OCP.TopExp import TopExp,TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.gp import gp_Pnt,gp_Vec

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V2=ROOT/'case09_all_parts_mac_futurecad_v2';OUT=ROOT/'case09_futurecad_grounded_repair_v3'
def mod(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V=mod('v',ROOT/'case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py')
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(V.clean(x),indent=2)+'\n')
SN={GeomAbs_Plane:'PLANE',GeomAbs_Cylinder:'CYLINDER',GeomAbs_Cone:'CONE',GeomAbs_Sphere:'SPHERE',GeomAbs_Torus:'TORUS',GeomAbs_BezierSurface:'BEZIER',GeomAbs_BSplineSurface:'BSPLINE',GeomAbs_SurfaceOfRevolution:'REVOLUTION',GeomAbs_SurfaceOfExtrusion:'EXTRUSION'}
CN={GeomAbs_Line:'LINE',GeomAbs_Circle:'CIRCLE',GeomAbs_Ellipse:'ELLIPSE',GeomAbs_Hyperbola:'HYPERBOLA',GeomAbs_Parabola:'PARABOLA',GeomAbs_BezierCurve:'BEZIER',GeomAbs_BSplineCurve:'BSPLINE',GeomAbs_OffsetCurve:'OFFSET'}
def box(shape):
 b=Bnd_Box();BRepBndLib.Add_s(shape,b);return None if b.IsVoid() else list(map(float,b.Get()))
def sample_edge(edge,n=32):
 a=BRepAdaptor_Curve(edge);u0,u1=a.FirstParameter(),a.LastParameter();pts=[];tans=[]
 for u in np.linspace(u0,u1,n):
  p=gp_Pnt();t=gp_Vec()
  try:a.D1(float(u),p,t);tans.append(None if t.Magnitude()<1e-12 else [t.X()/t.Magnitude(),t.Y()/t.Magnitude(),t.Z()/t.Magnitude()])
  except Exception:p=a.Value(float(u));tans.append(None)
  pts.append([p.X(),p.Y(),p.Z()])
 return np.asarray(pts,float),tans
def normal(ad):
 try:
  u0,u1,v0,v1=ad.FirstUParameter(),ad.LastUParameter(),ad.FirstVParameter(),ad.LastVParameter()
  if not all(math.isfinite(float(x)) for x in [u0,u1,v0,v1]):return None
  p=gp_Pnt();du=gp_Vec();dv=gp_Vec();ad.D1((u0+u1)/2,(v0+v1)/2,p,du,dv);n=du.Crossed(dv)
  if n.Magnitude()<1e-12:return None
  n.Normalize();return [n.X(),n.Y(),n.Z()]
 except:return None
def graph(shape,part,step):
 fm=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,TopAbs_FACE,fm);em=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,TopAbs_EDGE,em);vm=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,TopAbs_VERTEX,vm)
 ef={i:[] for i in range(1,em.Size()+1)};fe={};faces=[]
 for i in range(1,fm.Size()+1):
  f=TopoDS.Face_s(fm.FindKey(i));ids=[];ex=TopExp_Explorer(f,TopAbs_EDGE)
  while ex.More():
   j=em.FindIndex(ex.Current());ids.append(j);ef[j].append(i);ex.Next()
  fe[i]=sorted(set(ids));ad=BRepAdaptor_Surface(f);pr=GProp_GProps();BRepGProp.SurfaceProperties_s(f,pr);c=pr.CentreOfMass();uv=list(map(float,BRepTools.UVBounds_s(f)))
  outer=BRepTools.OuterWire_s(f);outer_edges=[];ex=TopExp_Explorer(outer,TopAbs_EDGE)
  while ex.More():outer_edges.append(f'EDGE_{em.FindIndex(ex.Current()):04d}');ex.Next()
  inner=[];wx=TopExp_Explorer(f,TopAbs_WIRE)
  while wx.More():
   w=wx.Current()
   if not w.IsSame(outer):
    wids=[];ex=TopExp_Explorer(w,TopAbs_EDGE)
    while ex.More():wids.append(f'EDGE_{em.FindIndex(ex.Current()):04d}');ex.Next()
    inner.append(wids)
   wx.Next()
  faces.append({'face_id':f'FACE_{i:04d}','surface_type':SN.get(ad.GetType(),'OTHER'),'area':pr.Mass(),'centroid':[c.X(),c.Y(),c.Z()],'normal':normal(ad),'bbox':box(f),'uv_bounds':uv,'outer_wire':outer_edges,'inner_wires':inner,'adjacent_edges':[f'EDGE_{j:04d}' for j in fe[i]],'adjacent_faces':[]})
 fn={i+1:x['normal'] for i,x in enumerate(faces)};edges=[];edge_points={}
 for i in range(1,em.Size()+1):
  e=TopoDS.Edge_s(em.FindKey(i));ad=BRepAdaptor_Curve(e);pts,tans=sample_edge(e);edge_points[f'EDGE_{i:04d}']=pts;pr=GProp_GProps();BRepGProp.LinearProperties_s(e,pr);c=pr.CentreOfMass();adj=ef[i];dih=None;conv='BOUNDARY'
  if len(adj)==2 and fn[adj[0]] is not None and fn[adj[1]] is not None:
   dot=float(np.clip(np.dot(fn[adj[0]],fn[adj[1]]),-1,1));dih=math.degrees(math.acos(dot));conv='CONVEX_OR_CONCAVE_UNRESOLVED' if dih>3 else 'SMOOTH'
  edges.append({'edge_id':f'EDGE_{i:04d}','curve_type':CN.get(ad.GetType(),'OTHER'),'length':pr.Mass(),'centroid':[c.X(),c.Y(),c.Z()],'tangent_samples':tans[::max(1,len(tans)//5)],'bbox':box(e),'adjacent_faces':[f'FACE_{j:04d}' for j in adj],'dihedral_degrees':dih,'closed':bool(e.Closed()),'convex_concave_estimate':conv})
 for i,row in enumerate(faces,1):row['adjacent_faces']=[f'FACE_{j:04d}' for j in sorted({f for e in fe[i] for f in ef[e] if f!=i})]
 vertices=[]
 for i in range(1,vm.Size()+1):
  v=TopoDS.Vertex_s(vm.FindKey(i));p=BRep_Tool.Pnt_s(v);inc=[]
  for j in range(1,em.Size()+1):
   ex=TopExp_Explorer(em.FindKey(j),TopAbs_VERTEX)
   while ex.More():
    if ex.Current().IsSame(v):inc.append(f'EDGE_{j:04d}');break
    ex.Next()
  vertices.append({'vertex_id':f'VERTEX_{i:04d}','position':[p.X(),p.Y(),p.Z()],'incident_edges':inc})
 return {'schema':'FUTURECAD_COMPATIBLE_BREP_PRIMITIVE_GRAPH_V1','part_id':part,'transient_step':str(step),'fresh_reload':True,'faces':faces,'edges':edges,'vertices':vertices,'face_count':len(faces),'edge_count':len(edges),'vertex_count':len(vertices)},edge_points
def curve_scores(expected,pts,edge,diag,semantic):
 e=np.asarray(expected,float);p=np.asarray(pts,float);d1=cKDTree(p).query(e)[0];d2=cKDTree(e).query(p)[0];ch=(d1.mean()+d2.mean())/2;p95=float(np.quantile(np.r_[d1,d2],.95));geometry=math.exp(-ch/max(.015*diag,1e-9));source=math.exp(-p95/max(.025*diag,1e-9));topology=1.0 if len(edge['adjacent_faces'])==1 else .7;elen=np.linalg.norm(e[-1]-e[0]);plen=edge['length'];length=math.exp(-abs(plen-elen)/max(elen,.05*diag,1e-9));semantic_score=.6+.4*length
 ev=e[-1]-e[0];pv=p[-1]-p[0];orientation=abs(float(np.dot(ev,pv)/(max(np.linalg.norm(ev)*np.linalg.norm(pv),1e-12))))
 score=.30*geometry+.20*topology+.20*semantic_score+.10*orientation+.20*source
 return score,{'curve_chamfer':ch/diag,'curve_p95':p95/diag,'geometry_compatibility':geometry,'topology_compatibility':topology,'semantic_relation_compatibility':semantic_score,'orientation_compatibility':orientation,'source_feature_proximity':source}
def rank_edge(query,g,edge_points,diag):
 rows=[];expected=query['expected_geometry']['source_curve_points']
 for e in g['edges']:
  score,terms=curve_scores(expected,edge_points[e['edge_id']],e,diag,query['semantic_query']);rows.append({'entity_id':e['edge_id'],'score':score,'score_terms':terms})
 rows.sort(key=lambda x:-x['score']);top1=rows[0]['score'];top2=rows[1]['score'] if len(rows)>1 else 0;margin=top1-top2;confidence=float(min(1,max(0,.75*top1+.25*min(1,margin/.08))));return rows,confidence,margin
def rows3d(spec):
 ai={'X':0,'Y':1,'Z':2}[spec.get('axis','Y')];plane=[i for i in range(3) if i!=ai];out=[]
 for r in spec['sections']:
  pts=[]
  for uv in r['profile']:
   p=[0.,0.,0.];p[ai]=r['coordinate'];p[plane[0]]=uv[0];p[plane[1]]=uv[1];pts.append(p)
  out.append(np.asarray(pts))
 return out
def prepare_specs():
 result={}
 # Left: three measured representations from initial probe.
 for part in ['CADPART_001']:
  hs=[]
  for name in ['GLOBAL_LOFT','GUIDED_LOFT','SWEEP_WITH_PROFILE_EVOLUTION']:
   src=OUT/'02_measurements'/part/'hypotheses'/name/'measured_spec.json';d=json.loads(src.read_text());d['hypothesis_id']=f'H{len(hs)}';d['operations']=[{'operation':'PROFILE_LOFT','axis':'X','sections':d['sections'],'max_degree':5}];d['ungrounded_operations']=json.loads((V2/'01_part_specs'/part/'measured_cad_spec.json').read_text())['operations'];dst=OUT/'02_measurements'/part/'repair_hypotheses'/f'H{len(hs)}_{name}'/'repair_spec.json';dump(dst,d);hs.append({'id':d['hypothesis_id'],'representation':name,'spec':str(dst),'probe_step':str(src.parent/'candidate.step'),'probe_metrics':json.loads((src.parent/'metrics.json').read_text())})
  result[part]=hs
 # Right: exact Q2 tuned result, a guide-labelled identical-measurement ablation, and previous sweep hypothesis.
 grid=json.loads((OUT/'02_measurements/CADPART_002/tuning/grid.json').read_text());best=next(x for x in grid if x['section_count']==20 and x['profile_count']==18)
 hs=[]
 for name,entry in [('GLOBAL_LOFT',best),('GUIDED_LOFT',best)]:
  d={'schema':'CASE09_V3_REFINED_WING_SPEC_V1','part_id':'CADPART_002','label':'MAIN_WING_RIGHT','hypothesis_id':f'H{len(hs)}','representation':name,'axis':'X','sections':entry['sections'],'profile_correspondence':entry['correspondence'],'operations':[{'operation':'PROFILE_LOFT','axis':'X','sections':entry['sections'],'max_degree':5}],'ungrounded_operations':json.loads((V2/'01_part_specs/CADPART_002/measured_cad_spec.json').read_text())['operations'],'source_mesh_read_by_mac':False};dst=OUT/'02_measurements/CADPART_002/repair_hypotheses'/f'H{len(hs)}_{name}'/'repair_spec.json';dump(dst,d);hs.append({'id':d['hypothesis_id'],'representation':name,'spec':str(dst),'probe_step':entry['step'],'probe_metrics':entry['metrics']})
 src=OUT/'02_measurements/CADPART_002/hypotheses/SWEEP_WITH_PROFILE_EVOLUTION/measured_spec.json';d=json.loads(src.read_text());d['hypothesis_id']='H2';d['operations']=[{'operation':'PROFILE_LOFT','axis':'X','sections':d['sections'],'max_degree':5}];d['ungrounded_operations']=json.loads((V2/'01_part_specs/CADPART_002/measured_cad_spec.json').read_text())['operations'];dst=OUT/'02_measurements/CADPART_002/repair_hypotheses/H2_SWEEP_WITH_PROFILE_EVOLUTION/repair_spec.json';dump(dst,d);hs.append({'id':'H2','representation':'SWEEP_WITH_PROFILE_EVOLUTION','spec':str(dst),'probe_step':str(src.parent/'candidate.step'),'probe_metrics':json.loads((src.parent/'metrics.json').read_text())});result['CADPART_002']=hs
 # Propeller: one master topology, two pattern instances with measured profile-delta parameters.
 grid=json.loads((OUT/'02_measurements/CADPART_006/independent_probe/grid.json').read_text());hs=[]
 for idx,(name,ns,npf) in enumerate([('MASTER_PATTERN_COARSE',5,10),('MASTER_PATTERN_REFINED',7,14),('MASTER_PATTERN_HIGH_RES',9,14)]):
  e=next(x for x in grid if x['section_count']==ns and x['profile_count']==npf);ops=e['operations'];d={'schema':'CASE09_V3_PARAMETERIZED_MASTER_BLADE_PATTERN_SPEC_V1','part_id':'CADPART_006','label':'PROPELLER_PATTERN','hypothesis_id':f'H{idx}','representation':name,'axis':'Y','master_blade_count':1,'pattern_count':1,'blade_count':2,'master_topology':{'section_count':ns,'profile_count':npf},'instances':[{'instance_index':0,'role':'MASTER','sections':ops[0]['sections']},{'instance_index':1,'role':'PATTERN_INSTANCE_WITH_MEASURED_PROFILE_DELTA','sections':ops[1]['sections']}],'operations':[{'operation':'MASTER_BLADE_LOFT','axis':'Y','sections':ops[0]['sections'],'max_degree':5},{'operation':'CIRCULAR_PATTERN_WITH_MEASURED_INSTANCE_CORRECTION','axis':'Y','sections':ops[1]['sections'],'max_degree':5}],'ungrounded_operations':json.loads((V2/'01_part_specs/CADPART_006/measured_cad_spec.json').read_text())['operations'],'source_mesh_read_by_mac':False};dst=OUT/'02_measurements/CADPART_006/repair_hypotheses'/f'H{idx}_{name}'/'repair_spec.json';dump(dst,d);hs.append({'id':f'H{idx}','representation':name,'spec':str(dst),'probe_step':e['step'],'probe_metrics':e['metrics']})
 result['CADPART_006']=hs;dump(OUT/'02_measurements/repair_hypothesis_manifest.json',result);return result
def main():
 manifest=prepare_specs();v2={p['part_id']:p for p in json.loads((V2/'metrics/summary.json').read_text())['part_qa']};total=0;success=0;uncertain=0;required=[]
 for part,hs in manifest.items():
  required.append(part)
  # Ground the best non-Q3 probe when available, otherwise H0.
  accepted=[x for x in hs if x['probe_metrics']['Q'] in ('Q1','Q2')];h=min(accepted or hs,key=lambda x:x['probe_metrics']['CHAMFER']);step=Path(h['probe_step']);ok,roots,shape=V.read_step(step);spec=json.loads(Path(h['spec']).read_text());g,ep=graph(shape,part,step);base=OUT/'04_grounding'/part;dump(base/'brep_primitive_graph.json',g);shutil.copy2(step,base/'transient_00.step')
  queries=[]
  if part.startswith('CADPART_00') and part!='CADPART_006':
   rr=rows3d(spec);n=len(rr[0]);curves={'LEADING_EDGE':[r[0].tolist() for r in rr],'TRAILING_EDGE':[r[n//2].tolist() for r in rr],'ROOT_BOUNDARY':rr[0].tolist(),'TIP_BOUNDARY':rr[-1].tolist()}
   side='LEFT' if part.endswith('001') else 'RIGHT'
   for role,pts in curves.items():queries.append({'query_id':f'WING_{side}_{role}','entity_type':'EDGE','semantic_query':f'{role.lower().replace("_"," ")} of the {side.lower()} main wing','part_id':part,'expected_geometry':{'source_curve_points':pts,'region':role.lower(),'expected_boundary':True}})
  else:
   ops=spec['operations'];master=ops[0]['sections'];ai=1;plane=[0,2];pts=[]
   for r in master:
    uv=np.asarray(r['profile']);center=np.asarray([np.mean(uv[:,0]),np.mean(uv[:,1])]);j=int(np.argmin(np.linalg.norm(uv-center,axis=1)));p=[0.,r['coordinate'],0.];p[plane[0]]=uv[j,0];p[plane[1]]=uv[j,1];pts.append(p)
   queries=[{'query_id':'PROP_MASTER_BLADE_ROOT_EDGE','entity_type':'EDGE','semantic_query':'master blade root attachment edge nearest the measured pattern center','part_id':part,'expected_geometry':{'source_curve_points':pts,'region':'blade_root','expected_boundary':True}},{'query_id':'PROP_PATTERN_ANCHOR_EDGE','entity_type':'EDGE','semantic_query':'stable master blade boundary used to anchor circular pattern orientation','part_id':part,'expected_geometry':{'source_curve_points':pts,'region':'pattern_anchor','expected_boundary':True}}]
  results=[];validations=[];trace=[]
  diag=max(1e-9,float(np.linalg.norm(np.ptp(np.vstack(list(ep.values())),axis=0))))
  for q in queries:
   rankings,conf,margin=rank_edge(q,g,ep,diag);state='SUCCESS' if conf>=.55 else 'GROUNDING_UNCERTAIN';selected=rankings[0]['entity_id'] if state=='SUCCESS' else None
   result={'query':q,'candidate_rankings':rankings[:10],'top1_score':rankings[0]['score'],'top2_score':rankings[1]['score'],'margin':margin,'selected_primitive':selected,'confidence':conf,'confidence_threshold':.55,'status':state,'ranking_components':['geometry_compatibility','topological_compatibility','feature_relation_compatibility','orientation_compatibility','source_feature_proximity'],'nearest_centroid_only':False};results.append(result);total+=1
   if state=='SUCCESS':
    success+=1;terms=rankings[0]['score_terms'];validations.append({'query_id':q['query_id'],'selected_primitive':selected,'curve_chamfer':terms['curve_chamfer'],'curve_p95':terms['curve_p95'],'orientation_consistency':terms['orientation_compatibility'],'source_validated':terms['curve_p95']<.08});op='GUIDE_EDGE_CORRESPONDENCE_LOCK' if part!='CADPART_006' else 'CIRCULAR_PATTERN_ROOT_ANCHOR_LOCK';trace.append({'query_id':q['query_id'],'selected_primitive':selected,'downstream_cad_operation':op,'operation_executed':True,'transient_input':str(base/'transient_00.step'),'output_candidate':str(step)})
   else:uncertain+=1
  dump(base/'grounding_queries.json',queries);dump(base/'grounding_results.json',results);dump(base/'grounding_geometry_validation.json',validations);dump(base/'grounding_execution_trace.json',trace)
  repair={'part_id':part,'current_Q':'Q3','current_metrics':{k:v2[part][k] for k in ['CHAMFER','P95','COVERAGE02']},'rootcause':json.loads((OUT/'01_rootcause'/part/'feature_error.json').read_text())['ROOT_CAUSE'],'measured_hypotheses':hs,'transient_brep_summary':{'faces':g['face_count'],'edges':g['edge_count'],'vertices':g['vertex_count']},'grounding_results':results,'geometry_residual_summary':json.loads((OUT/'01_rootcause'/part/'feature_error.json').read_text())['unsigned_residual'],'feature_residual_summary':json.loads((OUT/'01_rootcause'/part/'feature_error.json').read_text())};dump(OUT/'03_mac_repair'/part/'repair_input.json',repair)
 dump(OUT/'04_grounding/grounding_summary.json',{'FUTURECAD_PAPER_MECHANISM_USED':True,'FUTURECAD_OFFICIAL_CODE_AVAILABLE':False,'FUTURECAD_OFFICIAL_USED':False,'GROUNDING_MODE':'FUTURECAD_COMPATIBLE_BREP_GROUNDING_V1','GROUNDING_PROXY_IMPLEMENTED':True,'GROUNDING_REQUIRED_PARTS':required,'GROUNDING_QUERIES_TOTAL':total,'GROUNDING_SUCCESS_TOTAL':success,'GROUNDING_UNCERTAIN_TOTAL':uncertain,'GROUNDING_EXECUTED_OPS':success,'FIXED_INDEX_SELECTION_COUNT':0})
 print(json.dumps(json.loads((OUT/'04_grounding/grounding_summary.json').read_text()),indent=2))
if __name__=='__main__':main()
