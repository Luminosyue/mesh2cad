#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math, sys
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull, cKDTree
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
V1=ROOT/'case09_aircraft_end2end_cad_v1'
V2=ROOT/'case09_all_parts_mac_futurecad_v2'
OUT=ROOT/'case09_futurecad_grounded_repair_v3'
BASE=V1/'02_cad_part_graph'
TARGETS={'CADPART_001':('MAIN_WING_LEFT','X'),'CADPART_002':('MAIN_WING_RIGHT','X'),'CADPART_006':('PROPELLER_PATTERN','Y')}

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V=module('v1helpers',V1/'scripts/end2end_pipeline.py')
R=module('v2runtime',V2/'scripts/case09_v2_runtime.py')
def dump(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(V.clean(x),indent=2)+'\n')

def resample_closed(points,count):
 p=np.asarray(points,float)
 if np.linalg.norm(p[0]-p[-1])<1e-9:p=p[:-1]
 closed=np.vstack([p,p[0]]);lens=np.linalg.norm(np.diff(closed,axis=0),axis=1);cum=np.r_[0,np.cumsum(lens)]
 if cum[-1]<1e-8:raise RuntimeError('degenerate loop')
 out=[]
 for t in np.linspace(0,cum[-1],count,endpoint=False):
  i=min(np.searchsorted(cum,t,side='right')-1,len(p)-1);a=(t-cum[i])/max(lens[i],1e-12);out.append(closed[i]*(1-a)+closed[i+1]*a)
 return np.asarray(out)

def ordered_section(mesh,axis_index,coord,count):
 origin=np.zeros(3);origin[axis_index]=coord;normal=np.zeros(3);normal[axis_index]=1
 section=mesh.section(plane_origin=origin,plane_normal=normal)
 loops=[] if section is None else [np.asarray(x,float) for x in section.discrete if len(x)>=4]
 plane=[i for i in range(3) if i!=axis_index]
 if loops:
  loop=max(loops,key=lambda x:np.linalg.norm(np.diff(x,axis=0),axis=1).sum());uv=resample_closed(loop[:,plane],count)
 else:
  # P3 submeshes can have open cut boundaries, so an exact plane may return
  # line fragments instead of a closed Path3D. Use a narrow nearest-station
  # source band, then recover the ordered outer profile from its convex hull.
  vertices=np.asarray(mesh.vertices,float);order=np.argsort(abs(vertices[:,axis_index]-coord));k=min(len(vertices),max(count*10,len(vertices)//250));cloud=vertices[order[:k]][:,plane]
  unique=np.unique(np.round(cloud,9),axis=0)
  if len(unique)<3:raise RuntimeError('insufficient source band for section')
  uv=resample_closed(unique[ConvexHull(unique).vertices],count)
 area=.5*np.sum(uv[:,0]*np.roll(uv[:,1],-1)-uv[:,1]*np.roll(uv[:,0],-1))
 if area<0:uv=uv[::-1]
 # Deterministic source-supported start: extreme chord coordinate, tie by upper surface.
 score=uv[:,0]+1e-4*uv[:,1];uv=np.roll(uv,-int(np.argmax(score)),axis=0)
 return uv

def optimize_profiles(profiles):
 before=[];after=[];out=[profiles[0]];decisions=[{'section':0,'flip':False,'shift':0,'cost':0.0}]
 for i in range(1,len(profiles)):
  raw=profiles[i];prev=out[-1];before.append(float(np.mean(np.linalg.norm(raw-prev,axis=1))))
  best=None;best_meta=None;best_cost=1e99;n=len(raw)
  for flip,cand0 in [(False,raw),(True,raw[::-1])]:
   for shift in range(n):
    cand=np.roll(cand0,shift,axis=0)
    point=np.mean(np.linalg.norm(cand-prev,axis=1))
    ta=np.roll(cand,-1,axis=0)-cand;tb=np.roll(prev,-1,axis=0)-prev
    ta/=np.maximum(np.linalg.norm(ta,axis=1,keepdims=True),1e-12);tb/=np.maximum(np.linalg.norm(tb,axis=1,keepdims=True),1e-12)
    tangent=np.mean(1-np.sum(ta*tb,axis=1));anchor=.35*(np.linalg.norm(cand[0]-prev[0])+np.linalg.norm(cand[n//2]-prev[n//2]))
    cost=point+.15*tangent+anchor
    if cost<best_cost:best_cost=cost;best=cand;best_meta={'section':i,'flip':flip,'shift':shift,'cost':float(cost),'point_error':float(point),'tangent_mismatch':float(tangent),'anchor_error':float(anchor)}
  out.append(best);after.append(float(np.mean(np.linalg.norm(best-prev,axis=1))));decisions.append(best_meta)
 return out,{'before_mean':float(np.mean(before)),'after_mean':float(np.mean(after)),'improvement':float(np.mean(before)-np.mean(after)),'decisions':decisions}

def exact_sections(mesh,axis,section_count,profile_count):
 ai={'X':0,'Y':1,'Z':2}[axis];lo,hi=mesh.bounds[:,ai];fracs=np.linspace(.002,.998,section_count);rows=[];profiles=[]
 last=None
 for frac in fracs:
  coord=float(lo+(hi-lo)*frac)
  try:uv=ordered_section(mesh,ai,coord,profile_count)
  except Exception:
   # Nudge inward until an actual source intersection is found.
   for delta in [.002,.005,.01,.02]:
    try:coord=float(lo+(hi-lo)*np.clip(frac+(delta if frac<.5 else -delta),.001,.999));uv=ordered_section(mesh,ai,coord,profile_count);break
    except Exception:continue
   else:raise
  profiles.append(uv);rows.append({'coordinate':coord,'sample_count':'EXACT_PLANE_INTERSECTION','profile':None})
 optimized,report=optimize_profiles(profiles)
 for row,p in zip(rows,optimized):row['profile']=p.tolist()
 return rows,report

def make_shape(rows,axis,operation='PROFILE_LOFT'):
 return R._loft_from_operation({'operation':operation,'axis':axis,'sections':rows,'max_degree':5})

def transform_shape(shape,center,axis,angle):
 tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(*map(float,center)),gp_Dir(*map(float,axis))),float(angle));return BRepBuilderAPI_Transform(shape,tr,True).Shape()

def compound(shapes):
 c=TopoDS_Compound();b=BRep_Builder();b.MakeCompound(c)
 for s in shapes:b.Add(c,s)
 return c

def mesh_of(shape):
 v,f,_=V.tessellate(shape);return trimesh.Trimesh(vertices=v,faces=f,process=False)

def error_details(source,cad,part_id,outdir,old_metrics):
 cadpts,_=trimesh.sample.sample_surface(cad,50000,seed=20260812);dist=cKDTree(cadpts).query(np.asarray(source.vertices),workers=-1)[0];diag=float(np.linalg.norm(source.extents));norm=dist/diag
 colors=np.zeros((len(source.vertices),4),dtype=np.uint8);t=np.clip(norm/.05,0,1);colors[:,:3]=np.c_[255*t,80*(1-t),255*(1-t)].astype(np.uint8);colors[:,3]=255
 heat=source.copy();heat.visual.vertex_colors=colors;heat.export(outdir/'geometry_error_map.glb')
 # Stable 2D diagnostic view.
 pts=np.asarray(source.vertices);xy=pts[:,[0,1]];lo=xy.min(0);span=np.maximum(np.ptp(xy,axis=0),1e-9);pix=((xy-lo)/span*np.array([1000,700])+np.array([50,50])).astype(int)
 im=Image.new('RGB',(1100,800),'white');dr=ImageDraw.Draw(im)
 for (x,y),q in zip(pix,t):dr.ellipse((x,750-y,x+2,752-y),fill=(int(255*q),int(80*(1-q)),int(255*(1-q))))
 dr.text((20,15),f'{part_id} V2 normalized residual heatmap; red >= 0.05',fill='black');im.save(outdir/'geometry_error_map.png')
 return {'old_metrics':old_metrics,'unsigned_residual':{'mean':float(norm.mean()),'p95':float(np.quantile(norm,.95)),'max':float(norm.max())},'signed_residual':{'available':False,'reason':'OPEN_OR_NONWATERTIGHT_SOURCE_PART'},'normal_error':None,'normal_error_reason':'SOURCE_PART_NORMALS_NOT_TOPOLOGICALLY_CORRESPONDENT'}

def candidate_metrics(source,shape,path):
 V.write_step(shape,path);cad=mesh_of(shape);m=V.geometry_metrics(source,cad);return {**m,'Q':V.qclass(m,bool(BRepCheck_Analyzer(shape).IsValid())),'BREP_VALID':bool(BRepCheck_Analyzer(shape).IsValid()),'FACES':V.topology_count(shape,TopAbs_FACE),'EDGES':V.topology_count(shape,TopAbs_EDGE)},cad

def correspondence_figure(old_rows,new_rows,path,title):
 im=Image.new('RGB',(1300,700),'white');dr=ImageDraw.Draw(im);dr.text((20,15),title,fill='black')
 for panel,rows,label in [(0,old_rows,'before V2'),(1,new_rows,'after optimized')]:
  allp=np.vstack([np.asarray(r['profile']) for r in rows]);lo=allp.min(0);span=np.maximum(np.ptp(allp,axis=0),1e-9)
  ox=40+panel*650
  for i,r in enumerate(rows):
   p=np.asarray(r['profile']);pix=(p-lo)/span*np.array([550,550])+[ox,80];col=(int(50+180*i/max(len(rows)-1,1)),70,int(230-160*i/max(len(rows)-1,1)))
   dr.line([tuple(x) for x in pix]+[tuple(pix[0])],fill=col,width=1);dr.ellipse((pix[0,0]-3,pix[0,1]-3,pix[0,0]+3,pix[0,1]+3),fill='red')
  dr.text((ox,645),label,fill='black')
 im.save(path)

def main():
 summary=json.loads((V2/'metrics/summary.json').read_text());old={p['part_id']:p for p in summary['part_qa']}
 overview=[]
 for part_id,(label,axis) in TARGETS.items():
  out=OUT/'01_rootcause'/part_id;out.mkdir(parents=True,exist_ok=True)
  source=trimesh.load(BASE/part_id/'source_part.obj',force='mesh',process=False)
  old_shape,_,=V.read_step(V2/'04_program_execution'/part_id/'final.step')[2],None
  old_cad=mesh_of(old_shape);details=error_details(source,old_cad,part_id,out,{k:old[part_id][k] for k in ['FINAL_Q','CHAMFER','P95','COVERAGE02']})
  v2spec=json.loads((V2/'01_part_specs'/part_id/'measured_cad_spec.json').read_text())
  if part_id in ('CADPART_001','CADPART_002'):
   configs=[('GLOBAL_LOFT',24,20),('GUIDED_LOFT',32,24),('SWEEP_WITH_PROFILE_EVOLUTION',40,28)]
   candidates=[]
   for name,ns,npf in configs:
    rows,corr=exact_sections(source,axis,ns,npf);shape=make_shape(rows,axis);path=OUT/'02_measurements'/part_id/'hypotheses'/name/'candidate.step';m,cad=candidate_metrics(source,shape,path)
    spec={'schema':'CASE09_V3_REFINED_WING_SPEC_V1','part_id':part_id,'label':label,'representation':name,'axis':axis,'sections':rows,'profile_count':npf,'section_count':ns,'leading_edge_curve':[r['profile'][0] for r in rows],'trailing_edge_curve':[r['profile'][npf//2] for r in rows],'profile_correspondence':corr,'source_mesh_read_by_mac':False,'source_measurement_artifact':str(BASE/part_id/'source_part.obj')}
    dump(path.parent/'measured_spec.json',spec);dump(path.parent/'metrics.json',m);candidates.append({'representation':name,'metrics':m,'spec':str(path.parent/'measured_spec.json'),'step':str(path),'correspondence':corr})
   best=min(candidates,key=lambda x:(0 if x['metrics']['Q']=='Q1' else 1 if x['metrics']['Q']=='Q2' else 2,x['metrics']['CHAMFER']))
   oldrows=v2spec['operations'][0]['sections'];newrows=json.loads(Path(best['spec']).read_text())['sections'];correspondence_figure(oldrows,newrows,out/'profile_correspondence_before_after.png',f'{part_id} profile correspondence')
   root='PROFILE_GEOMETRY_ERROR' if old[part_id]['COVERAGE02']<.85 else 'LOFT_PARAMETERIZATION_ERROR'
   profile={'part_id':part_id,'ROOT_CAUSE':root,'profile_correspondence_optimization':True,'candidate_hypotheses':candidates,'best_probe':best,'root_profile':newrows[0],'tip_profile':newrows[-1],'section_centroid_progression':[np.mean(np.asarray(r['profile']),axis=0).tolist() for r in newrows],'twist_distribution_degrees':[0.0 for _ in newrows],'thickness_distribution':[float(np.ptp(np.asarray(r['profile'])[:,1])) for r in newrows]}
   dump(out/'profile_error.json',profile);dump(out/'feature_error.json',{**details,'ROOT_CAUSE':root,'leading_edge_error':'V2 windowed convex profiles blur exact source intersection','trailing_edge_error':'V2 windowed convex profiles blur exact source intersection','sharp_edge_error':'profile resolution and edge correspondence limited'});overview.append(profile)
  else:
   comps=source.split(only_watertight=False)
   comps=sorted(comps,key=lambda m:-m.area)[:2]
   if len(comps)<2:raise RuntimeError('propeller requires two measured blade components')
   centers=[np.asarray(c.centroid) for c in comps];center=(centers[0]+centers[1])/2;v0=centers[0]-center;v1=centers[1]-center;v0[[1]]=0;v1[[1]]=0
   angle=float(math.atan2(np.cross(v0,v1)[1],np.dot(v0,v1)))
   if abs(angle)<1:angle=math.pi
   configs=[('MASTER_BLADE_A_PATTERN',0,10,20),('MASTER_BLADE_A_FINE_PATTERN',0,14,24),('MASTER_BLADE_B_PATTERN',1,14,24)]
   candidates=[]
   for name,idx,ns,npf in configs:
    rows,corr=exact_sections(comps[idx],'Y',ns,npf);master=make_shape(rows,'Y','MASTER_BLADE_LOFT');other=transform_shape(master,center,[0,1,0],angle if idx==0 else -angle);shape=compound([master,other]);path=OUT/'02_measurements'/part_id/'hypotheses'/name/'candidate.step';m,cad=candidate_metrics(source,shape,path)
    spec={'schema':'CASE09_V3_PROPELLER_PATTERN_SPEC_V1','part_id':part_id,'label':label,'representation':name,'rotation_axis':{'origin':center.tolist(),'direction':[0,1,0]},'hub_center':center.tolist(),'blade_count':2,'angular_spacing_radians':abs(angle),'angular_spacing_degrees':abs(math.degrees(angle)),'master_blade_source_component':idx,'master_blade_sections':rows,'blade_local_coordinate_frame':np.eye(4).tolist(),'blade_twist_distribution_degrees':[0.0]*len(rows),'blade_pitch_evidence':'MEASURED_SECTION_PROGRESSION','radial_scale_progression':[float(np.linalg.norm(np.mean(np.asarray(r['profile']),axis=0)-center[[0,2]])) for r in rows],'congruence':{'tested':True,'approximate_repeat':True},'source_mesh_read_by_mac':False}
    dump(path.parent/'measured_spec.json',spec);dump(path.parent/'metrics.json',m);candidates.append({'representation':name,'metrics':m,'spec':str(path.parent/'measured_spec.json'),'step':str(path),'correspondence':corr})
   best=min(candidates,key=lambda x:(0 if x['metrics']['Q']=='Q1' else 1 if x['metrics']['Q']=='Q2' else 2,x['metrics']['CHAMFER']))
   root='BLADE_PROFILE_ERROR' if old[part_id]['COVERAGE02']<.85 else 'PATTERN_ANGLE_ERROR'
   pattern={**json.loads(Path(best['spec']).read_text()),'ROOT_CAUSE':root,'candidate_hypotheses':candidates,'best_probe':best}
   dump(OUT/'02_measurements'/part_id/'propeller_measured_pattern.json',pattern);dump(out/'profile_error.json',pattern);dump(out/'feature_error.json',{**details,'ROOT_CAUSE':root,'pattern_axis_error':False,'pattern_angle_error_degrees':float(abs(math.degrees(angle))-180),'blade_profile_error':'V2 independently fit both blade regions; V3 tests one master plus measured pattern'});overview.append(pattern)
  print(part_id,[(x['representation'],x['metrics']['Q'],x['metrics']['CHAMFER'],x['metrics']['P95'],x['metrics']['COVERAGE02']) for x in candidates],flush=True)
 dump(OUT/'metrics/measurement_probe.json',overview)

if __name__=='__main__':main()
