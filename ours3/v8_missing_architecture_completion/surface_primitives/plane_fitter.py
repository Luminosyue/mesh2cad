import numpy as np
from .schemas import PrimitiveCandidate
def fit_plane(points,surface_id,source_mesh,quantile_evidence):
 p=np.asarray(points,float);c=p.mean(0);_,_,vh=np.linalg.svd(p-c,full_matrices=False);n=vh[-1];d=np.abs((p-c)@n)
 return PrimitiveCandidate(surface_id,"PLANE",{"origin":c.tolist(),"normal":n.tolist()},
  {"mean":float(d.mean()),"p95":float(np.quantile(d,.95)),"sample_count":len(p)},
  {"valid":bool(len(p)>=3 and np.linalg.norm(n)>.99)},
  {"source_mesh":str(source_mesh),"evidence":"EXTREME_QUANTILE_SURFACE_SAMPLES","quantile":quantile_evidence})
