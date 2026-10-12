import hashlib,json,numpy as np
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
def _box(shape):
 b=Bnd_Box();BRepBndLib.Add_s(shape,b);return list(b.Get())
def _fp(kind,box,size,semantic=None):return hashlib.sha256(json.dumps([kind,[round(x,7) for x in box],round(size,7),semantic],sort_keys=True).encode()).hexdigest()[:20]
def index_entities(shape,wireframe):
 out={"FACE":[],"EDGE":[]}
 for kind,top in (("FACE",TopAbs_FACE),("EDGE",TopAbs_EDGE)):
  seen=set()
  ex=TopExp_Explorer(shape,top)
  while ex.More():
   s=ex.Current();p=GProp_GProps();(BRepGProp.SurfaceProperties_s if kind=="FACE" else BRepGProp.LinearProperties_s)(s,p);box=_box(s);size=float(p.Mass());cent=[p.CentreOfMass().X(),p.CentreOfMass().Y(),p.CentreOfMass().Z()]
   entity_id=_fp(kind,box,size)
   if entity_id not in seen:out[kind].append({"occ_entity_id":entity_id,"entity_type":kind,"bbox":box,"centroid":cent,"area_or_length":size,"occ_shape":s});seen.add(entity_id)
   ex.Next()
 return out
def ground_query(index,query,semantic_targets,min_conf=.45):
 entity_type="FACE" if "surface" in query.lower() or "face" in query.lower() else "EDGE";words=set(query.lower().replace("_"," ").split());rows=[]
 for rec in index[entity_type]:
  geom=.5;position=0.;semantic=0.;membership=0.
  c=np.asarray(rec["centroid"]);allc=np.asarray([x["centroid"] for x in index[entity_type]]);lo,hi=allc.min(0),allc.max(0)
  if "leading" in words:position=(c[1]-lo[1])/max(hi[1]-lo[1],1e-9)
  if "trailing" in words:position=(hi[1]-c[1])/max(hi[1]-lo[1],1e-9)
  if "upper" in words:position=(c[2]-lo[2])/max(hi[2]-lo[2],1e-9)
  for label,target in semantic_targets.items():
   if label.lower().replace("_"," ") in query.lower():
    d=np.linalg.norm(c-np.asarray(target));semantic=max(semantic,float(np.exp(-5*d)));membership=semantic
  score=.25*geom+.35*position+.25*semantic+.15*membership;rows.append((score,rec))
 rows.sort(key=lambda x:-x[0]);margin=rows[0][0]-rows[1][0] if len(rows)>1 else rows[0][0];status="RESOLVED" if rows[0][0]>=min_conf and margin>=.03 else "UNRESOLVED"
 return {"query":query,"entity_type":entity_type,"occ_entity_id":rows[0][1]["occ_entity_id"] if status=="RESOLVED" else None,"confidence":rows[0][0],"margin":margin,"grounding_status":status,"nearest_only_grounding":False,"evidence":{"geometry":.5,"position_semantic_composite":rows[0][0],"candidate_count":len(rows),"deduplicated_by_geometry_fingerprint":True},"real_occ_entity_returned":status=="RESOLVED"}
