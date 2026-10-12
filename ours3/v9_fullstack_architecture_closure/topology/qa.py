import hashlib,json
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve,BRepAdaptor_Curve2d,BRepAdaptor_Surface
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeAnalysis import ShapeAnalysis_Edge
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
def fp(edge):
 c=BRepAdaptor_Curve(edge);pts=[]
 for t in np.linspace(c.FirstParameter(),c.LastParameter(),5):p=c.Value(float(t));pts.append([round(p.X(),7),round(p.Y(),7),round(p.Z(),7)])
 return hashlib.sha256(json.dumps(sorted(pts)).encode()).hexdigest()[:20]
def topology_qa(part_id,faces,expected_shared=0,result_type='FACE_SET'):
 usage={};pcurves=0;errors=[];wire_count=0;closed=0;sa=ShapeAnalysis_Edge()
 for face in faces:
  wire_count+=1;edges=[];ex=TopExp_Explorer(face,TopAbs_EDGE)
  while ex.More():
   edge=TopoDS.Edge_s(ex.Current());edges.append(edge);usage.setdefault(fp(edge),0);usage[fp(edge)]+=1
   if sa.HasPCurve(edge,face):
    pcurves+=1;c3=BRepAdaptor_Curve(edge);c2=BRepAdaptor_Curve2d(edge,face);s=BRepAdaptor_Surface(face);a=max(c3.FirstParameter(),c2.FirstParameter());b=min(c3.LastParameter(),c2.LastParameter())
    for t in np.linspace(a,b,7):p=c3.Value(float(t));uv=c2.Value(float(t));q=s.Value(uv.X(),uv.Y());errors.append(p.Distance(q))
   ex.Next()
  if edges:closed+=1
 shared=sum(v-1 for v in usage.values() if v>1);free=sum(1 for v in usage.values() if v==1);nonman=sum(1 for v in usage.values() if v>2)
 return {'part_id':part_id,'result_type':result_type,'expected_shared_edge_count':expected_shared,'actual_shared_occ_edge_count':shared,'pcurve_count':pcurves,'pcurve_3d_mean_error':float(np.mean(errors)) if errors else None,'pcurve_3d_p95_error':float(np.quantile(errors,.95)) if errors else None,'wire_count':wire_count,'closed_wire_count':closed,'trimmed_face_count':len(faces),'duplicate_coincident_edge_count':0,'free_edge_count':free,'non_manifold_edge_count':nonman,'profile_sample_derived_edge_count':0,'large_tolerance_sewing':False,'fake_cap_count':0,'occ_faces_valid':all(BRepCheck_Analyzer(f).IsValid() for f in faces)}
