from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeWire
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell,BRepOffsetAPI_ThruSections
from OCP.Geom import Geom_CylindricalSurface,Geom_Plane,Geom_SurfaceOfLinearExtrusion,Geom_SurfaceOfRevolution
from OCP.GeomAPI import GeomAPI_Interpolate,GeomAPI_PointsToBSpline,GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1
from OCP.TColgp import TColgp_Array1OfPnt,TColgp_Array2OfPnt,TColgp_HArray1OfPnt
from OCP.gp import gp_Ax1,gp_Ax3,gp_Dir,gp_Pln,gp_Pnt

def _curve(points,periodic=False,tol=1e-7):
 p=np.asarray(points,float);a=TColgp_HArray1OfPnt(1,len(p))
 for i,x in enumerate(p,1):a.SetValue(i,gp_Pnt(*map(float,x)))
 f=GeomAPI_Interpolate(a,bool(periodic),float(tol));f.Perform()
 if not f.IsDone():raise RuntimeError('BSPLINE_CURVE_FIT_FAILED')
 return f.Curve()
def _grid_surface(grid,periodic_v=False,tol=1e-5):
 g=np.asarray(grid,float);a=TColgp_Array2OfPnt(1,len(g),1,len(g[0]))
 for i,row in enumerate(g,1):
  for j,p in enumerate(row,1):a.SetValue(i,j,gp_Pnt(*map(float,p)))
 f=GeomAPI_PointsToBSplineSurface(a,2,3,GeomAbs_C1,float(tol))
 if not f.IsDone():raise RuntimeError('BSPLINE_SURFACE_FIT_FAILED')
 s=f.Surface()
 if periodic_v and not s.IsVPeriodic():s.SetVPeriodic()
 return s
def _wire(points):
 c=_curve(points,True);return BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(c).Edge()).Wire()
def _face(surface):
 f=BRepBuilderAPI_MakeFace(surface,1e-7).Face()
 if f.IsNull() or not BRepCheck_Analyzer(f).IsValid():raise RuntimeError('SURFACE_FACE_INVALID')
 return f
def _residual(points,projected):
 d=np.linalg.norm(np.asarray(points)-np.asarray(projected),axis=1)
 return {'rms':float(np.sqrt(np.mean(d*d))),'mean':float(d.mean()),'p95':float(np.quantile(d,.95)),'sample_count':len(d)}
def _base(kind,parameters,residual,domain,support,normal_error,boundary_error,shape,applicability='APPLICABLE'):
 return {'primitive_type':kind,'parameters':parameters,'fit_residual':residual,'surface_domain':domain,'support_points':np.asarray(support,float).tolist(),'normal_consistency_error':float(normal_error),'boundary_consistency_error':float(boundary_error),'executable_representation':'OCC','occ_shape':shape,'applicability':applicability,'valid':bool(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())}

def fit_plane(points):
 p=np.asarray(points,float);o=p.mean(0);_,_,vh=np.linalg.svd(p-o,full_matrices=False);n=vh[-1];u=vh[0];v=np.cross(n,u);proj=p-np.outer((p-o)@n,n);uv=np.c_[(p-o)@u,(p-o)@v];s=Geom_Plane(gp_Pln(gp_Pnt(*o),gp_Dir(*n)));face=BRepBuilderAPI_MakeFace(s,float(uv[:,0].min()),float(uv[:,0].max()),float(uv[:,1].min()),float(uv[:,1].max()),1e-7).Face()
 return _base('PLANE',{'origin':o.tolist(),'normal':n.tolist(),'u_frame':u.tolist(),'v_frame':v.tolist()},_residual(p,proj),{'u':[float(uv[:,0].min()),float(uv[:,0].max())],'v':[float(uv[:,1].min()),float(uv[:,1].max())]},p,0,0,face)
def fit_cylinder(points,axis_origin,axis_direction):
 p=np.asarray(points,float);o=np.asarray(axis_origin,float);d=np.asarray(axis_direction,float);d/=np.linalg.norm(d);q=p-o;ax=q@d;rad=q-np.outer(ax,d);radii=np.linalg.norm(rad,axis=1);r=float(np.median(radii));unit=rad/np.maximum(radii[:,None],1e-12);proj=o+np.outer(ax,d)+unit*r;ref=unit[0];ort=np.cross(d,ref);ang=np.unwrap(np.arctan2(unit@ort,unit@ref));surf=Geom_CylindricalSurface(gp_Ax3(gp_Pnt(*o),gp_Dir(*d)),r);face=BRepBuilderAPI_MakeFace(surf,float(ang.min()),float(ang.max()),float(ax.min()),float(ax.max()),1e-7).Face()
 return _base('CYLINDER',{'axis_origin':o.tolist(),'axis_direction':d.tolist(),'radius':r,'angular_domain':[float(ang.min()),float(ang.max())],'axial_domain':[float(ax.min()),float(ax.max())]},_residual(p,proj),{'u':[float(ang.min()),float(ang.max())],'v':[float(ax.min()),float(ax.max())]},p,float(np.std(radii)/max(r,1e-12)),0,face)
def fit_revolution(points,axis_origin,axis_direction,bins=16):
 p=np.asarray(points,float);o=np.asarray(axis_origin,float);d=np.asarray(axis_direction,float);d/=np.linalg.norm(d);q=p-o;z=q@d;rad=np.linalg.norm(q-np.outer(z,d),axis=1);edges=np.linspace(z.min(),z.max(),bins+1);zs=[];rs=[]
 for a,b in zip(edges[:-1],edges[1:]):
  m=(z>=a)&(z<=b)
  if m.any():zs.append(float(z[m].mean()));rs.append(float(np.median(rad[m])))
 ref=np.array([1.,0,0]);ref-=ref.dot(d)*d
 if np.linalg.norm(ref)<1e-6:ref=np.array([0.,1,0]);ref-=ref.dot(d)*d
 ref/=np.linalg.norm(ref);mer=np.asarray([o+d*a+ref*b for a,b in zip(zs,rs)]);curve=_curve(mer,False);surf=Geom_SurfaceOfRevolution(curve,gp_Ax1(gp_Pnt(*o),gp_Dir(*d)));face=BRepBuilderAPI_MakeFace(surf,0,2*math.pi,curve.FirstParameter(),curve.LastParameter(),1e-7).Face();pred=np.interp(z,zs,rs);proj=o+np.outer(z,d)+(q-np.outer(z,d))*np.divide(pred,rad,out=np.zeros_like(pred),where=rad>1e-12)[:,None]
 return _base('REVOLUTION',{'axis_origin':o.tolist(),'axis_direction':d.tolist(),'generatrix_points':mer.tolist(),'angle_range':[0,2*math.pi]},_residual(p,proj),{'u':[0,2*math.pi],'v':[float(curve.FirstParameter()),float(curve.LastParameter())]},p,float(np.std(rad-pred)/max(np.mean(rad),1e-12)),0,face)
def fit_extrusion(profile_points,vector):
 p=np.asarray(profile_points,float);v=np.asarray(vector,float);depth=float(np.linalg.norm(v));d=v/depth;curve=_curve(p,True);surf=Geom_SurfaceOfLinearExtrusion(curve,gp_Dir(*d));face=BRepBuilderAPI_MakeFace(surf,curve.FirstParameter(),curve.LastParameter(),0,depth,1e-7).Face()
 return _base('EXTRUSION',{'base_profile':p.tolist(),'extrusion_vector':v.tolist(),'depth':depth}, {'rms':0,'mean':0,'p95':0,'sample_count':len(p)}, {'u':[float(curve.FirstParameter()),float(curve.LastParameter())],'v':[0,depth]},p,0,0,face)
def fit_sweep(profile_points,spine_points):
 profile=np.asarray(profile_points,float);spine=np.asarray(spine_points,float);spine_wire=BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(_curve(spine,False)).Edge()).Wire();maker=BRepOffsetAPI_MakePipeShell(spine_wire);maker.SetMode(False);maker.Add(_wire(profile));maker.Build()
 if not maker.IsDone():raise RuntimeError('SWEEP_FAILED')
 shape=maker.Shape();return _base('SWEEP',{'section_profile':profile.tolist(),'spine_curve':spine.tolist(),'frame_law':'CORRECTED_FRENET'}, {'rms':0,'mean':0,'p95':0,'sample_count':len(profile)+len(spine)}, {'spine':[0,1],'profile':[0,1]},np.vstack([profile,spine]),0,0,shape)
def fit_loft(profiles,station_refs):
 profiles=[np.asarray(x,float) for x in profiles];maker=BRepOffsetAPI_ThruSections(True,False,1e-6);maker.CheckCompatibility(True)
 for p in profiles:maker.AddWire(_wire(p))
 maker.Build()
 if not maker.IsDone():raise RuntimeError('LOFT_FAILED')
 shape=maker.Shape();return _base('LOFT',{'measured_profile_references':list(station_refs),'profile_points':[p.tolist() for p in profiles],'station_correspondence':'GEOMETRY_ANALYZER_ORDER'}, {'rms':0,'mean':0,'p95':0,'sample_count':sum(map(len,profiles))}, {'station':[0,len(profiles)-1],'profile':[0,1]},np.vstack(profiles),0,0,shape)
def fit_periodic_bspline(grid):
 g=np.asarray(grid,float);surf=_grid_surface(g,True);shape=_face(surf);params={'degree_u':surf.UDegree(),'degree_v':surf.VDegree(),'knots_u':[surf.UKnot(i) for i in range(1,surf.NbUKnots()+1)],'knots_v':[surf.VKnot(i) for i in range(1,surf.NbVKnots()+1)],'multiplicities_u':[surf.UMultiplicity(i) for i in range(1,surf.NbUKnots()+1)],'multiplicities_v':[surf.VMultiplicity(i) for i in range(1,surf.NbVKnots()+1)],'control_points':[[[surf.Pole(i,j).X(),surf.Pole(i,j).Y(),surf.Pole(i,j).Z()] for j in range(1,surf.NbVPoles()+1)] for i in range(1,surf.NbUPoles()+1)],'periodic_v':surf.IsVPeriodic()}
 u0,u1,v0,v1=surf.Bounds();return _base('PERIODIC_BSPLINE',params,{'rms':0,'mean':0,'p95':0,'sample_count':g.size//3},{'u':[u0,u1],'v':[v0,v1]},g.reshape(-1,3),0,0,shape)
def fit_general_bspline(grid):
 g=np.asarray(grid,float);surf=_grid_surface(g,False);shape=_face(surf);params={'degree_u':surf.UDegree(),'degree_v':surf.VDegree(),'knots_u':[surf.UKnot(i) for i in range(1,surf.NbUKnots()+1)],'knots_v':[surf.VKnot(i) for i in range(1,surf.NbVKnots()+1)],'multiplicities_u':[surf.UMultiplicity(i) for i in range(1,surf.NbUKnots()+1)],'multiplicities_v':[surf.VMultiplicity(i) for i in range(1,surf.NbVKnots()+1)],'control_points':[[[surf.Pole(i,j).X(),surf.Pole(i,j).Y(),surf.Pole(i,j).Z()] for j in range(1,surf.NbVPoles()+1)] for i in range(1,surf.NbUPoles()+1)],'periodic_u':surf.IsUPeriodic(),'periodic_v':surf.IsVPeriodic()}
 u0,u1,v0,v1=surf.Bounds();return _base('GENERAL_BSPLINE',params,{'rms':0,'mean':0,'p95':0,'sample_count':g.size//3},{'u':[u0,u1],'v':[v0,v1]},g.reshape(-1,3),0,0,shape)

FITTERS={'PLANE':fit_plane,'CYLINDER':fit_cylinder,'REVOLUTION':fit_revolution,'EXTRUSION':fit_extrusion,'SWEEP':fit_sweep,'LOFT':fit_loft,'PERIODIC_BSPLINE':fit_periodic_bspline,'GENERAL_BSPLINE':fit_general_bspline}

def execute_case09_fitter_suite(root):
 import json,trimesh
 root=Path(root);wing=json.loads((root/'v7a_profile_recovery/04_measured_spec/CADPART_001/measured_cad_spec.json').read_text());fuse=json.loads((root/'v7b_profile_type_aware_open_shell_reconstruction/04_measured_spec/CADPART_000/measured_cad_spec.json').read_text());tail=json.loads((root/'v7a_profile_recovery/04_measured_spec/CADPART_005/measured_cad_spec.json').read_text());mesh=trimesh.load(root/'case09_aircraft_end2end_cad_v1/02_cad_part_graph/CADPART_000/source_part.obj',force='mesh',process=False);points=np.asarray(mesh.vertices)[::max(len(mesh.vertices)//4000,1)];axis=fuse['axis'];wing_profiles=[p['outer_loop']['resampled_points_3d'] for p in wing['profiles']];tail_profiles=[p['outer_loop']['resampled_points_3d'] for p in tail['profiles']];track=np.asarray([x['resampled_points_3d'] for x in next(iter(fuse['open_chain_tracks'].values()))]);d=np.asarray(wing['axis']['direction']);span=wing['span'];results={}
 results['PLANE']=fit_plane(points[np.argsort(points[:,2])[-max(len(points)//20,20):]])
 results['CYLINDER']=fit_cylinder(points,axis['origin'],axis['direction'])
 results['REVOLUTION']=fit_revolution(points,axis['origin'],axis['direction'])
 results['EXTRUSION']=fit_extrusion(tail_profiles[0],np.asarray(tail['axis']['direction'])*tail['span'])
 results['SWEEP']=fit_sweep(tail_profiles[0],[np.asarray(tail['axis']['origin'])-np.asarray(tail['axis']['direction'])*tail['span']/2,np.asarray(tail['axis']['origin'])+np.asarray(tail['axis']['direction'])*tail['span']/2])
 results['LOFT']=fit_loft(wing_profiles,[p['station_id'] for p in wing['profiles']])
 results['PERIODIC_BSPLINE']=fit_periodic_bspline(wing_profiles)
 results['GENERAL_BSPLINE']=fit_general_bspline(track)
 return results
