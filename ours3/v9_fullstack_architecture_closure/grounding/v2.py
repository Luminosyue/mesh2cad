import hashlib,json
import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
def _box(s):b=Bnd_Box();BRepBndLib.Add_s(s,b);return list(b.Get())
def _fp(kind,box,size,direction,part):return hashlib.sha256(json.dumps([kind,[round(x,7) for x in box],round(size,7),[round(x,6) for x in direction],part]).encode()).hexdigest()[:24]
def _edge_descriptor(edge):
 c=BRepAdaptor_Curve(edge);a,b=c.FirstParameter(),c.LastParameter();m=(a+b)/2;p=c.Value(m);v=c.DN(m,1);d=np.array([v.X(),v.Y(),v.Z()]);d/=max(np.linalg.norm(d),1e-12);return [p.X(),p.Y(),p.Z()],d.tolist(),str(c.GetType()).split('.')[-1]
def build_entity_index(shape,part_id,surface_ids,primitive_membership,wireframe,feature_graph):
 faces=[];face_edges={};seen=set();ex=TopExp_Explorer(shape,TopAbs_FACE);fi=0
 while ex.More():
  face=TopoDS.Face_s(ex.Current());p=GProp_GProps();BRepGProp.SurfaceProperties_s(face,p);box=_box(face);center=[p.CentreOfMass().X(),p.CentreOfMass().Y(),p.CentreOfMass().Z()];direction=[0,0,1];sid=surface_ids[fi] if fi<len(surface_ids) else f'FACE_{fi}';fid=_fp('FACE',box,p.Mass(),direction,part_id);members=[x['feature_id'] for x in feature_graph['features'] if sid in x['support_faces'] or sid in x['affected_faces']];rec={'occ_entity_id':fid,'entity_type':'FACE','geometry_type':'OCC_FACE','bbox':box,'centroid':center,'area_or_length':float(p.Mass()),'orientation':direction,'principal_direction':direction,'adjacent_entity_ids':[],'surface_primitive_membership':[primitive_membership.get(sid)],'wireframe_semantic_membership':[],'feature_membership':members,'relative_object_position':None,'part_id':part_id,'surface_id':sid,'occ_shape':face};faces.append(rec);face_edges[fid]=[];seen.add(fid);fi+=1;ex.Next()
 edges={}
 for face in faces:
  ex=TopExp_Explorer(face['occ_shape'],TopAbs_EDGE)
  while ex.More():
   edge=TopoDS.Edge_s(ex.Current());p=GProp_GProps();BRepGProp.LinearProperties_s(edge,p);box=_box(edge);center,direction,gtype=_edge_descriptor(edge);eid=_fp('EDGE',box,p.Mass(),direction,part_id);face_edges[face['occ_entity_id']].append(eid)
   if eid not in edges:edges[eid]={'occ_entity_id':eid,'entity_type':'EDGE','geometry_type':gtype,'bbox':box,'centroid':center,'area_or_length':float(p.Mass()),'orientation':direction,'principal_direction':direction,'adjacent_entity_ids':[],'surface_primitive_membership':[],'wireframe_semantic_membership':[],'feature_membership':[],'relative_object_position':None,'part_id':part_id,'occ_shape':edge}
   ex.Next()
 for face in faces:
  for eid in face_edges[face['occ_entity_id']]:
   edge=edges[eid];edge['adjacent_entity_ids'].append(face['occ_entity_id']);edge['surface_primitive_membership']+=face['surface_primitive_membership'];edge['feature_membership']+=face['feature_membership'];face['adjacent_entity_ids'].append(eid)
 wtypes={}
 for w in wireframe['edges']:
  wtypes.setdefault(w['semantic_type'],[]).append(np.asarray(w['centroid']))
 for edge in edges.values():
  c=np.asarray(edge['centroid']);rank=sorted((float(np.linalg.norm(c-np.asarray(points).mean(0))),kind) for kind,points in wtypes.items());edge['wireframe_semantic_membership']=[rank[0][1]] if rank else []
 allrec=faces+list(edges.values());cent=np.asarray([x['centroid'] for x in allrec]);lo,hi=cent.min(0),cent.max(0)
 for rec in allrec:rec['relative_object_position']=((np.asarray(rec['centroid'])-lo)/np.maximum(hi-lo,1e-12)).tolist();rec['adjacent_entity_ids']=sorted(set(rec['adjacent_entity_ids']));rec['surface_primitive_membership']=sorted(set(x for x in rec['surface_primitive_membership'] if x));rec['feature_membership']=sorted(set(rec['feature_membership']))
 return {'FACE':faces,'EDGE':list(edges.values())}
def ground(index,query,entity_type):
 q=query.lower();rows=[]
 for rec in index[entity_type]:
  pos=rec['relative_object_position'];terms=[]
  if 'leading' in q:terms.append(pos[1])
  if 'trailing' in q:terms.append(1-pos[1])
  if 'upper' in q or 'highest' in q:terms.append(pos[2])
  if 'lower' in q:terms.append(1-pos[2])
  if 'tip' in q:terms.append(pos[0])
  position=float(np.mean(terms)) if terms else 0
  orientation=abs(rec['principal_direction'][0]) if 'boundary' in q or 'edge' in q else abs(rec['orientation'][2]);adjacency=min(len(rec['adjacent_entity_ids'])/4,1);wire=max([1.0 for x in rec['wireframe_semantic_membership'] if x.lower().replace('_',' ') in q] or [0.0]);feature=max([1.0 for x in rec['feature_membership'] if 'loft' in q or x.lower() in q] or [0.0]);primitive=max([1.0 for x in rec['surface_primitive_membership'] if 'bspline' in q or 'plane' in q] or [0.0]);score=.25*position+.15*orientation+.15*adjacency+.2*wire+.15*feature+.1*primitive;rows.append((score,rec,{'position':position,'orientation':orientation,'adjacency':adjacency,'wireframe_semantic_membership':wire,'feature_membership':feature,'primitive_membership':primitive}))
 rows.sort(key=lambda x:-x[0]);margin=rows[0][0]-rows[1][0] if len(rows)>1 else rows[0][0];status='RESOLVED' if rows[0][0]>=.42 and margin>=.03 else ('AMBIGUOUS' if rows[0][0]>=.3 else 'UNRESOLVED');return {'query':query,'entity_type':entity_type,'grounding_status':status,'occ_entity_id':rows[0][1]['occ_entity_id'] if status=='RESOLVED' else None,'confidence':rows[0][0],'margin':margin,'evidence':rows[0][2],'nearest_only_grounding':False,'real_occ_entity_returned':status=='RESOLVED'}
