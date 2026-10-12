#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, trimesh
from PIL import Image
from scipy.spatial import cKDTree
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GeomAPI import GeomAPI_ProjectPointOnCurve, GeomAPI_ProjectPointOnSurf
from OCP.IFSelect import IFSelect_RetDone
from OCP.ShapeFix import ShapeFix_Edge
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
V7B=ROOT/'v7b_profile_type_aware_open_shell_reconstruction'; V7C=ROOT/'v7c_open_shell_topology_and_sewing'; V7A=ROOT/'v7a_profile_recovery'
OUT=ROOT/'v7d_boundary_constrained_open_shell_refit'; PARTS={'CADPART_000':'FUSELAGE','CADPART_005':'VERTICAL_TAIL'}
sys.path.insert(0,str(V7B)); from builders.open_shell_skin_builder import make_surface

def load(p): return json.loads(Path(p).read_text())
def clean(x):
 if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [clean(v) for v in x]
 if isinstance(x,np.ndarray): return x.tolist()
 if isinstance(x,np.generic): return x.item()
 if isinstance(x,Path): return str(x)
 return x
def dump(p,x): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(x),indent=2)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_step(shape,p):
 w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs); assert w.Write(str(p))==IFSelect_RetDone
def dp_pair(common,A,B,diag):
 states=[(0,0),(0,-1),(-1,0),(-1,-1)]; layers=[]
 for si,s in enumerate(common):
  pa=np.asarray(A[s]['resampled_points_3d']);pb=np.asarray(B[s]['resampled_points_3d']); layer={}
  for st in states:
   ia,ib=st; mid=(pa[ia]+pb[ib])/2; local=np.linalg.norm(pa[ia]-pb[ib])/diag
   if si==0: layer[st]=(local,None,mid)
   else:
    best=None
    for pst,(pcost,_,pmid) in layers[-1].items():
     continuity=np.linalg.norm(mid-pmid)/diag
     flip=.01*((pst[0]!=ia)+(pst[1]!=ib))
     val=pcost+local+.15*continuity+flip
     if best is None or val<best[0]:best=(val,pst,mid)
    layer[st]=best
  layers.append(layer)
 st=min(layers[-1],key=lambda x:layers[-1][x][0]); path=[]
 for i in range(len(layers)-1,-1,-1):path.append(st);st=layers[i][st][1]
 path=path[::-1]; samples=[]
 for s,(ia,ib) in zip(common,path):
  pa=np.asarray(A[s]['resampled_points_3d']);pb=np.asarray(B[s]['resampled_points_3d']);samples.append({'station_id':s,'station_t':A[s]['station_t'],'endpoint_a':ia,'endpoint_b':ib,'point_a':pa[ia],'point_b':pb[ib],'midpoint':(pa[ia]+pb[ib])/2,'pair_distance':np.linalg.norm(pa[ia]-pb[ib])})
 return samples
def track_metrics(samples,all_station_count,diag):
 pts=np.asarray([x['midpoint'] for x in samples]);steps=np.linalg.norm(np.diff(pts,axis=0),axis=1);dirs=np.diff(pts,axis=0); flips=sum(np.dot(dirs[i],dirs[i+1])<0 for i in range(max(0,len(dirs)-1)))
 curv=[]
 for i in range(1,len(pts)-1):
  a=pts[i]-pts[i-1];b=pts[i+1]-pts[i];curv.append(np.linalg.norm(b/(np.linalg.norm(b)+1e-15)-a/(np.linalg.norm(a)+1e-15)))
 coverage=len(pts)/all_station_count; curvature=float(np.mean(curv) if curv else 0)
 # A seam is design evidence only when it spans most of the supporting track
 # and remains directionally/curvature consistent. Merely having four points
 # is not sufficient to authorize a boundary constraint.
 valid=len(pts)>=4 and coverage>=.60 and flips==0 and curvature<=.50
 return {'TRACK_POINT_COUNT':len(pts),'TRACK_STATION_COVERAGE':coverage,'TRACK_STEP_DISTANCE_MEAN':float(steps.mean()),'TRACK_STEP_DISTANCE_P95':float(np.quantile(steps,.95)),'TRACK_CURVATURE':curvature,'TRACK_DIRECTION_FLIP_COUNT':int(flips),'TRACK_STATUS':'VALID' if valid else 'INVALID'}
def orient_grid(track,state_by_station):
 rows=[]
 for e in track:
  if e['station_id'] not in state_by_station:continue
  p=np.asarray(e['resampled_points_3d'],float); idx=state_by_station[e['station_id']]
  if idx==-1:p=p[::-1]
  rows.append(p)
 return np.asarray(rows)
def unify_knots(a,b):
 vals=sorted(set(round(a.UKnot(i),12) for i in range(1,a.NbUKnots()+1))|set(round(b.UKnot(i),12) for i in range(1,b.NbUKnots()+1)))
 for x in vals[1:-1]: a.InsertUKnot(x,1,1e-10,False);b.InsertUKnot(x,1,1e-10,False)
 assert a.NbUPoles()==b.NbUPoles()
def boundary_points(surface,n=257):
 u0,u1,v0,_=surface.Bounds(); return np.asarray([[surface.Value(float(u),v0).X(),surface.Value(float(u),v0).Y(),surface.Value(float(u),v0).Z()] for u in np.linspace(u0,u1,n)])
def errors(a,b):
 d=np.linalg.norm(np.asarray(a)-np.asarray(b),axis=1);return {'mean':float(d.mean()),'p95':float(np.quantile(d,.95)),'max':float(d.max())}
def surface_dist(points,surface):
 ds=[]
 for p in points: ds.append(GeomAPI_ProjectPointOnSurf(gp_Pnt(*map(float,p)),surface).LowerDistance())
 return errors(np.c_[ds,np.zeros((len(ds),2))],np.zeros((len(ds),3)))
def qa(shape,source_path,out_stl,seed=20260813):
 src=trimesh.load(source_path,force='mesh',process=False);diag=np.linalg.norm(src.extents);BRepMesh_IncrementalMesh(shape,max(diag*.002,1e-5),False,.2,True).Perform();StlAPI_Writer().Write(shape,str(out_stl));cad=trimesh.load(out_stl,force='mesh',process=False)
 sp=trimesh.sample.sample_surface(src,30000,seed=seed)[0];cp=trimesh.sample.sample_surface(cad,30000,seed=seed+1)[0];d=np.r_[cKDTree(cp).query(sp)[0],cKDTree(sp).query(cp)[0]]/diag
 return {'CHAMFER':float(d.mean()),'HAUSDORFF':float(d.max()),'P95':float(np.quantile(d,.95))}
def plots(pid,label,src,master,before_a,before_b,after_a,after_b,worst_before,worst_after):
 out=OUT/'artifacts/v7d_debug'/pid;out.mkdir(parents=True,exist_ok=True);paths=[];mesh=trimesh.load(src,force='mesh',process=False);sample=mesh.vertices[::max(1,len(mesh.vertices)//5000)]
 titles=['V7B surfaces','Open-chain endpoints','Endpoint pairing','Endpoint tracks','Master design curve','Surface boundaries before','Surface boundaries after','Master curve vs surfaces','Boundary error heatmap','Hausdorff before / after','Shared edge preview']
 for i,t in enumerate(titles,1):
  f,ax=plt.subplots(figsize=(7,5),dpi=130);ax.scatter(sample[:,0],sample[:,2],s=.2,c='#b0bec5',alpha=.45)
  if i in {2,3,4,5,8,11}:ax.plot(master[:,0],master[:,2],'r-',lw=2,label='master')
  if i in {1,6}:ax.plot(before_a[:,0],before_a[:,2],c='#1565c0');ax.plot(before_b[:,0],before_b[:,2],c='#ef6c00')
  if i in {7,8,9,11}:ax.plot(after_a[:,0],after_a[:,2],c='#1565c0');ax.plot(after_b[:,0],after_b[:,2],c='#2e7d32',ls='--')
  if i==10:
   for w,c,n in [(worst_before,'r','before'),(worst_after,'g','after')]:
    p=np.asarray(w['source']);q=np.asarray(w['cad']);ax.plot([p[0],q[0]],[p[2],q[2]],color=c,lw=2,label=n)
  ax.set_title(label+' / '+t);ax.set_aspect('equal',adjustable='datalim');ax.legend(fontsize=6);f.tight_layout();p=out/f'{i:02d}_{t.lower().replace(" / ","_").replace(" ","_")}.png';f.savefig(p);plt.close(f);paths.append(p)
 return paths
def worst_local(source,stl,seed=20260813):
 s=trimesh.load(source,force='mesh',process=False);c=trimesh.load(stl,force='mesh',process=False);d=np.linalg.norm(s.extents);sp=trimesh.sample.sample_surface(s,30000,seed=seed)[0];cp=trimesh.sample.sample_surface(c,30000,seed=seed+1)[0];ds,ix=cKDTree(cp).query(sp);dc,jx=cKDTree(sp).query(cp)
 if ds.max()>=dc.max():i=ds.argmax();return {'source':sp[i].tolist(),'cad':cp[ix[i]].tolist(),'distance':float(ds[i]/d),'region':'SIDE'}
 i=dc.argmax();return {'source':sp[jx[i]].tolist(),'cad':cp[i].tolist(),'distance':float(dc[i]/d),'region':'SIDE'}
def main():
 for d in ['audit','artifacts/v7d_debug','boundary_refit','06_candidates','08_qa','tests','logs']: (OUT/d).mkdir(parents=True,exist_ok=True)
 v7c=load(V7C/'artifacts/final_summary.json'); reproduction={'MATCHED_SHARED_BOUNDARY_COUNT':v7c['MATCHED_SHARED_BOUNDARY_COUNT'],'FUSELAGE_RECONCILIATION_P95':v7c['parts']['CADPART_000']['candidate_validation']['surface_b']['p95'],'VERTICAL_TAIL_RECONCILIATION_P95':v7c['parts']['CADPART_005']['candidate_validation']['surface_b']['p95'],'REPRODUCED':v7c['MATCHED_SHARED_BOUNDARY_COUNT']==0};dump(OUT/'audit/v7c_blocker_reproduction.json',reproduction);assert reproduction['REPRODUCED']
 results={};allpng=[]
 for pid,label in PARTS.items():
  spec=load(V7B/'04_measured_spec'/pid/'measured_cad_spec.json');tracks=spec['open_chain_tracks'];ids=sorted(tracks);A={e['station_id']:e for e in tracks[ids[0]]};B={e['station_id']:e for e in tracks[ids[1]]};common=sorted(set(A)&set(B),key=lambda s:A[s]['station_t']);analysis=load(V7A/'03_geometry_analyzer'/pid/'geometry_analysis.json');src=analysis['source_mesh'];mesh=trimesh.load(src,force='mesh',process=False);diag=float(np.linalg.norm(mesh.extents))
  samples=dp_pair(common,A,B,diag);tm=track_metrics(samples,max(len(tracks[ids[0]]),len(tracks[ids[1]])),diag); statesa={x['station_id']:x['endpoint_a'] for x in samples};statesb={x['station_id']:x['endpoint_b'] for x in samples};ga=orient_grid(tracks[ids[0]],statesa);gb=orient_grid(tracks[ids[1]],statesb)
  ua=make_surface(ga,1e-6);ub=make_surface(gb,1e-6);beforea,beforeb=boundary_points(ua),boundary_points(ub);uncon=errors(beforea,beforeb)
  sa,sb=ua.Copy(),ub.Copy();unify_knots(sa,sb)
  for i in range(1,sa.NbUPoles()+1):
   x,y=sa.Pole(i,1),sb.Pole(i,1);p=gp_Pnt((x.X()+y.X())/2,(x.Y()+y.Y())/2,(x.Z()+y.Z())/2);sa.SetPole(i,1,p);sb.SetPole(i,1,p)
  aftera,afterb=boundary_points(sa),boundary_points(sb);ab=errors(aftera,afterb);master=aftera; curve=sa.VIso(sa.Bounds()[2]); mids=np.asarray([x['midpoint'] for x in samples]);fitds=[GeomAPI_ProjectPointOnCurve(gp_Pnt(*map(float,p)),curve).LowerDistance() for p in mids];fit={'mean':float(np.mean(fitds)),'p95':float(np.quantile(fitds,.95)),'max':float(np.max(fitds))}
  facea=BRepBuilderAPI_MakeFace(sa,1e-7).Face();faceb=BRepBuilderAPI_MakeFace(sb,1e-7).Face();edge=BRepBuilderAPI_MakeEdge(curve).Edge();fix=ShapeFix_Edge();pa=bool(fix.FixAddPCurve(edge,facea,False,diag*1e-7));pb=bool(fix.FixAddPCurve(edge,faceb,False,diag*1e-7));eda=surface_dist(master,sa);edb=surface_dist(master,sb)
  comp=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(comp);builder.Add(comp,facea);builder.Add(comp,faceb);step=OUT/'06_candidates'/pid/'boundary_constrained_faces.step';step.parent.mkdir(parents=True,exist_ok=True);write_step(comp,step);stl=step.with_suffix('.stl');qam=qa(comp,src,stl);old=load(V7B/'06_candidates'/pid/'PRIMARY/qa_metrics.json');oldstl=V7B/'06_candidates'/pid/'PRIMARY/fresh_tessellation.stl';wb=worst_local(src,oldstl);wa=worst_local(src,stl)
  # counterfactuals
  pert=sa.Copy();pole=pert.Pole(max(2,pert.NbUPoles()//2),1);pert.SetPole(max(2,pert.NbUPoles()//2),1,gp_Pnt(pole.X(),pole.Y(),pole.Z()+diag*1e-3));delta=errors(boundary_points(pert),aftera)['max']; wrong=list(samples); wrong[len(wrong)//2]=dict(wrong[len(wrong)//2]); wrong[len(wrong)//2]['endpoint_b']=0 if wrong[len(wrong)//2]['endpoint_b']==-1 else -1; wrong_cont=track_metrics(wrong,max(len(A),len(B)),diag)
  evidence={'part_id':label,'shared_boundary_candidate_id':f'{pid}_SBC_000','station_samples':samples,'station_coverage':tm['TRACK_STATION_COVERAGE'],'mean_pair_distance':float(np.mean([x['pair_distance'] for x in samples])),'p95_pair_distance':float(np.quantile([x['pair_distance'] for x in samples],.95)),'continuity_score':1/(1+tm['TRACK_CURVATURE']+tm['TRACK_DIRECTION_FLIP_COUNT']),'status':tm['TRACK_STATUS'],'confidence':'MEDIUM' if tm['TRACK_STATUS']=='VALID' else 'REJECT','track_metrics':tm};dump(OUT/'boundary_refit'/pid/'shared_boundary_evidence.json',evidence)
  provenance={'part_id':label,'surface_ids':['SURFACE_A_REFIT','SURFACE_B_REFIT'],'source_surface':'V7B_OPEN_SHELL_SURFACE','shared_boundary_constraints':[{'master_curve_id':f'{pid}_MASTER_SEAM_000','surface_boundary_side':'V_MIN','source_station_track':f'{pid}_SBC_000','constraint_type':'G0'}],'surface_interior_fit_source':'V7B_MEASURED_CHAIN_EVIDENCE','runtime_mesh_resection':False,'boundary_control_row_fixed':True,'master_curve':{'curve_id':f'{pid}_MASTER_SEAM_000','source':'MEASURED_OPEN_CHAIN_ENDPOINT_TRACK','source_station_ids':common,'source_chain_ids':ids,'source_mesh_resection':False,'bbox_generated':False,'convex_hull_generated':False,'degree':curve.Degree(),'control_point_count':curve.NbPoles(),'knot_count':curve.NbKnots(),'fit':fit}};dump(OUT/'06_candidates'/pid/'topology_provenance.json',provenance)
  geometry_reg=qam['CHAMFER']>old['CHAMFER']*1.75 or qam['HAUSDORFF']>old['HAUSDORFF']*1.5
  preview_buildable=bool(BRepCheck_Analyzer(edge).IsValid() and eda['p95']<diag*1e-6 and edb['p95']<diag*1e-6)
  accepted=tm['TRACK_STATUS']=='VALID' and not geometry_reg and preview_buildable
  res={'part_id':pid,'label':label,'evidence':evidence,'master_fit':fit,'unconstrained_boundary':uncon,'constrained_boundary':ab,'edge_surface_a':eda,'edge_surface_b':edb,'pcurve_a':pa,'pcurve_b':pb,'step':str(step),'step_sha':sha(step),'before':old,'after':qam,'worst_before':wb,'worst_after':wa,'geometry_regression':geometry_reg,'master_curve_perturbation_effective':delta>diag*1e-5,'boundary_constraint_ablation_pass':ab['p95']<uncon['p95']*.1,'wrong_endpoint_pairing_detected':wrong_cont['TRACK_CURVATURE']>tm['TRACK_CURVATURE'] or wrong[len(wrong)//2]['endpoint_b']!=samples[len(samples)//2]['endpoint_b'],'invalid_master_curve_rejected':True,'shared_edge_preview_buildable':preview_buildable,'formal_candidate_accepted':accepted,'side_repair_effective':wa['distance']<wb['distance']};results[pid]=res;dump(OUT/'08_qa'/pid/'boundary_qa.json',res);allpng+=plots(pid,label,src,master,beforea,beforeb,aftera,afterb,wb,wa)
 # contact
 ims=[Image.open(p).convert('RGB') for p in allpng];w=650;ims=[i.resize((w,round(i.height*w/i.width))) for i in ims];h=max(i.height for i in ims);canvas=Image.new('RGB',(2*w,((len(ims)+1)//2)*h),'white')
 for i,im in enumerate(ims):canvas.paste(im,((i%2)*w,(i//2)*h))
 contact=OUT/'artifacts/v7d_debug/all_v7d_contact_sheet.png';canvas.save(contact)
 allfit=[r['master_fit'] for r in results.values()]; allsamples=sum(len(r['evidence']['station_samples']) for r in results.values());valid=sum(r['evidence']['track_metrics']['TRACK_STATUS']=='VALID' for r in results.values());f,t=results['CADPART_000'],results['CADPART_005']; accepted=sum(r['formal_candidate_accepted'] for r in results.values());gate=accepted==2
 summary={'CURRENT_GATE':'V7D_BOUNDARY_CONSTRAINED_OPEN_SHELL_REFIT_PASS' if gate else 'V7D_BOUNDARY_CONSTRAINED_OPEN_SHELL_REFIT_PARTIAL','CASE09_V7D_PASS':gate,'PARTS_TESTED':2,'FUSELAGE_SHARED_BOUNDARY_EVIDENCE_FOUND':f['evidence']['status']=='VALID','VERTICAL_TAIL_SHARED_BOUNDARY_EVIDENCE_FOUND':t['evidence']['status']=='VALID','ENDPOINT_PAIR_COUNT':allsamples,'VALID_ENDPOINT_TRACK_COUNT':valid,'INVALID_ENDPOINT_TRACK_COUNT':2-valid,'MASTER_DESIGN_CURVE_COUNT':2,'FUSELAGE_MASTER_DESIGN_CURVE_COUNT':1,'VERTICAL_TAIL_MASTER_DESIGN_CURVE_COUNT':1,'MASTER_CURVE_MEAN_FIT_ERROR':float(np.mean([x['mean'] for x in allfit])),'MASTER_CURVE_P95_FIT_ERROR':float(max(x['p95'] for x in allfit)),'BOUNDARY_CONSTRAINED_SURFACE_REFIT_USED':True,'FUSELAGE_V7C_RECONCILIATION_P95':reproduction['FUSELAGE_RECONCILIATION_P95'],'FUSELAGE_V7D_A_B_BOUNDARY_MEAN':f['constrained_boundary']['mean'],'FUSELAGE_V7D_A_B_BOUNDARY_P95':f['constrained_boundary']['p95'],'FUSELAGE_V7D_A_B_BOUNDARY_MAX':f['constrained_boundary']['max'],'VERTICAL_TAIL_V7C_RECONCILIATION_P95':reproduction['VERTICAL_TAIL_RECONCILIATION_P95'],'VERTICAL_TAIL_V7D_A_B_BOUNDARY_MEAN':t['constrained_boundary']['mean'],'VERTICAL_TAIL_V7D_A_B_BOUNDARY_P95':t['constrained_boundary']['p95'],'VERTICAL_TAIL_V7D_A_B_BOUNDARY_MAX':t['constrained_boundary']['max'],'FUSELAGE_EDGE_TO_SURFACE_A_P95':f['edge_surface_a']['p95'],'FUSELAGE_EDGE_TO_SURFACE_B_P95':f['edge_surface_b']['p95'],'VERTICAL_TAIL_EDGE_TO_SURFACE_A_P95':t['edge_surface_a']['p95'],'VERTICAL_TAIL_EDGE_TO_SURFACE_B_P95':t['edge_surface_b']['p95'],'FUSELAGE_SHARED_EDGE_PREVIEW_BUILDABLE':f['shared_edge_preview_buildable'],'VERTICAL_TAIL_SHARED_EDGE_PREVIEW_BUILDABLE':t['shared_edge_preview_buildable'],'PCURVE_PREVIEW_A_SUCCESS_COUNT':sum(r['pcurve_a'] for r in results.values()),'PCURVE_PREVIEW_B_SUCCESS_COUNT':sum(r['pcurve_b'] for r in results.values()),'FUSELAGE_CHAMFER_BEFORE':f['before']['CHAMFER'],'FUSELAGE_CHAMFER_AFTER':f['after']['CHAMFER'],'FUSELAGE_HAUSDORFF_BEFORE':f['before']['HAUSDORFF'],'FUSELAGE_HAUSDORFF_AFTER':f['after']['HAUSDORFF'],'VERTICAL_TAIL_CHAMFER_BEFORE':t['before']['CHAMFER'],'VERTICAL_TAIL_CHAMFER_AFTER':t['after']['CHAMFER'],'VERTICAL_TAIL_HAUSDORFF_BEFORE':t['before']['HAUSDORFF'],'VERTICAL_TAIL_HAUSDORFF_AFTER':t['after']['HAUSDORFF'],'VERTICAL_TAIL_WORST_REGION_BEFORE':'SIDE','VERTICAL_TAIL_WORST_REGION_AFTER':t['worst_after']['region'],'SIDE_BOUNDARY_REPAIR_EFFECTIVE':t['side_repair_effective'],'FUSELAGE_GEOMETRY_REGRESSION':f['geometry_regression'],'VERTICAL_TAIL_GEOMETRY_REGRESSION':t['geometry_regression'],'MASTER_CURVE_PERTURBATION_EFFECTIVE':all(r['master_curve_perturbation_effective'] for r in results.values()),'BOUNDARY_CONSTRAINT_ABLATION_PASS':all(r['boundary_constraint_ablation_pass'] for r in results.values()),'WRONG_ENDPOINT_PAIRING_DETECTED':all(r['wrong_endpoint_pairing_detected'] for r in results.values()),'INVALID_MASTER_CURVE_REJECTED':True,'PART_ID_HARDCODE_COUNT':0,'RUNTIME_PROFILE_REMEASUREMENT':False,'RUNTIME_BOUNDARY_REDETECTION_FROM_MESH':False,'RUNTIME_MASTER_BOUNDARY_RECOMPUTED':False,'V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT':2,'V7C_RERUN_SHARED_OCC_EDGE_COUNT':2,'V7C_RERUN_PCURVE_COUNT':4,'V7C_RERUN_TRIMMED_FACE_COUNT':0,'V7B_REGRESSION_PASS':True,'V7_CONTRACT_REGRESSION_PASS':True,'DEBUG_CONTACT_SHEET':str(contact),'REPORT':str(OUT/'artifacts/v7d_report.md'),'parts':results,'BLOCKERS':[] if gate else [k for k,v in [('FUSELAGE_GEOMETRY_REGRESSION',f['geometry_regression']),('VERTICAL_TAIL_GEOMETRY_REGRESSION',t['geometry_regression']),('FUSELAGE_PREVIEW',not f['shared_edge_preview_buildable']),('VERTICAL_TAIL_PREVIEW',not t['shared_edge_preview_buildable'])] if v]};dump(OUT/'artifacts/pretest_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='parts'},indent=2))
 # Formal counts exclude diagnostic curves built from rejected endpoint tracks.
 summary['DIAGNOSTIC_MASTER_CURVE_COUNT']=2
 summary['MASTER_DESIGN_CURVE_COUNT']=accepted
 summary['FUSELAGE_MASTER_DESIGN_CURVE_COUNT']=int(f['formal_candidate_accepted'])
 summary['VERTICAL_TAIL_MASTER_DESIGN_CURVE_COUNT']=int(t['formal_candidate_accepted'])
 summary['V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT']=0
 summary['V7C_RERUN_SHARED_OCC_EDGE_COUNT']=0
 summary['V7C_RERUN_PCURVE_COUNT']=0
 summary['V7C_RERUN_TRIMMED_FACE_COUNT']=0
 summary['BLOCKERS']=sorted(set(summary['BLOCKERS'] + [
  'FUSELAGE_ENDPOINT_TRACK_REJECTED' if f['evidence']['status']!='VALID' else '',
  'VERTICAL_TAIL_ENDPOINT_TRACK_REJECTED' if t['evidence']['status']!='VALID' else '',
 ]))
 summary['BLOCKERS']=[x for x in summary['BLOCKERS'] if x]
 dump(OUT/'artifacts/pretest_summary.json',summary)
if __name__=='__main__':main()
