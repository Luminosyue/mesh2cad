import hashlib,json
import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_EDGE,TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

def _props(shape,kind):
 p=GProp_GProps();(BRepGProp.LinearProperties_s if kind=='EDGE' else BRepGProp.VolumeProperties_s)(shape,p);c=p.CentreOfMass();return float(p.Mass()),np.array([c.X(),c.Y(),c.Z()])
def _fp(kind,points,extra=''):
 canonical=sorted([tuple(round(float(x),7) for x in p) for p in points]);return hashlib.sha256(json.dumps([kind,canonical,extra],sort_keys=True).encode()).hexdigest()[:24]
def _vertices(edge):
 out=[];ex=TopExp_Explorer(edge,TopAbs_VERTEX)
 while ex.More():
  p=BRep_Tool.Pnt_s(TopoDS.Vertex_s(ex.Current()));out.append([p.X(),p.Y(),p.Z()]);ex.Next()
 return out
def build_surface_wireframe(part_id,role,surfaces,axis_direction):
 axis=np.asarray(axis_direction,float);axis/=np.linalg.norm(axis);edge_rows=[];node_map={};surface_rows=[];centers=[]
 for surface_id,primitive_id,face in surfaces:
  ex=TopExp_Explorer(face,TopAbs_EDGE);local=[]
  while ex.More():
   edge=TopoDS.Edge_s(ex.Current());verts=_vertices(edge);curve=BRepAdaptor_Curve(edge);mid=(curve.FirstParameter()+curve.LastParameter())/2;p=curve.Value(mid);center=np.array([p.X(),p.Y(),p.Z()]);tangent=np.array([curve.DN(mid,1).X(),curve.DN(mid,1).Y(),curve.DN(mid,1).Z()]);tangent/=max(np.linalg.norm(tangent),1e-12);length,_=_props(edge,'EDGE');eid=_fp('EDGE',verts,[round(length,7),surface_id]);centers.append(center);local.append((eid,center,tangent,length,verts));ex.Next()
  surface_rows.append({'surface_id':surface_id,'surface_type':'DESIGN_SURFACE','primitive_id':primitive_id,'evidence':{'normal_clustering':'FITTED_SURFACE_NORMAL_FIELD','curvature':'OCC_SURFACE_DIFFERENTIAL','primitive_ownership':primitive_id,'surface_support':'GEOMETRY_ANALYZER_MEASURED_PROFILES','boundary_support':'ACTUAL_OCC_FACE_BOUNDARY','surface_adjacency':'EDGE_FINGERPRINT_MATCHING'},'boundary_edge_ids':[x[0] for x in local]})
  for eid,center,tangent,length,verts in local:
   alignment=abs(float(tangent@axis));edge_rows.append({'edge_id':eid,'source_surface_ids':[surface_id],'primitive_owner_ids':[primitive_id],'curve':{'type':'ACTUAL_OCC_FACE_BOUNDARY','length':length,'principal_direction':tangent.tolist(),'smooth':True},'end_vertices':[],'semantic_type':'SHARED_LONGITUDINAL_BOUNDARY' if alignment>.65 else 'OTHER_OPEN_BOUNDARY','confidence':.9,'geometry_provenance':'FITTED_SURFACE_BOUNDARY','profile_sample_derived':False,'mesh_triangle_edge':False,'centroid':center.tolist(),'axis_alignment':alignment,'_verts':verts})
 allc=np.asarray(centers);lo,hi=float((allc@axis).min()),float((allc@axis).max());span=max(hi-lo,1e-9)
 for edge in edge_rows:
  t=float(np.asarray(edge['centroid'])@axis)
  if t-lo<.1*span:edge['semantic_type']='ROOT_BOUNDARY'
  elif hi-t<.1*span:edge['semantic_type']='TIP_BOUNDARY'
  for xyz in edge.pop('_verts'):
   nid=_fp('VERTEX',[xyz]);node_map.setdefault(nid,{'node_id':nid,'node_type':'DESIGN_VERTEX','point':xyz,'geometry_provenance':'ACTUAL_OCC_EDGE_ENDPOINT'});edge['end_vertices'].append(nid)
 by_geom={}
 for edge in edge_rows:
  key=_fp('GEOM',[[*edge['centroid']]],round(edge['curve']['length'],7));by_geom.setdefault(key,[]).append(edge)
 for group in by_geom.values():
  if len(group)>1:
   for edge in group:edge['semantic_type']='SHARED_SURFACE_BOUNDARY';edge['source_surface_ids']=sorted({sid for x in group for sid in x['source_surface_ids']})
 return {'part_id':part_id,'role':role,'semantic_surfaces':surface_rows,'nodes':list(node_map.values()),'edges':edge_rows,'loops':[{'loop_id':f'LOOP_{i:02d}','surface_id':s['surface_id'],'edge_ids':s['boundary_edge_ids']} for i,s in enumerate(surface_rows)],'semantic_surface_count':len(surface_rows),'real_design_edge_count':len(edge_rows),'mesh_triangle_edge_import_count':0,'profile_sample_design_edge_count':0,'station_iso_line_edge_count':0}
