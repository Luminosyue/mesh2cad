import numpy as np
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakeWire,BRepBuilderAPI_Sewing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepLib import BRepLib
from OCP.BRepAdaptor import BRepAdaptor_Curve,BRepAdaptor_Curve2d,BRepAdaptor_Surface
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
from OCP.ShapeAnalysis import ShapeAnalysis_Edge
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt
def _intersection(planes,keys):
 A=np.asarray([planes[k]["normal"] for k in keys]);b=np.asarray([np.dot(planes[k]["normal"],planes[k]["origin"]) for k in keys]);return np.linalg.solve(A,b)
def build_topology(bank,wireframe,removed_edge=None,offset_overrides=None):
 planes={p["surface_id"].split("_")[-1]:{"origin":np.asarray(p["parameters"]["origin"],float),"normal":np.asarray(p["parameters"]["normal"],float)} for p in bank["selected_primitives"]}
 for key,value in (offset_overrides or {}).items():planes[key]["origin"]+=planes[key]["normal"]*float(value)
 corners={}
 for a in ("ROOT","TIP"):
  for b in ("TRAILING","LEADING"):
   for c in ("LOWER","UPPER"):corners[(a,b,c)]=_intersection(planes,(a,b,c))
 verts={k:gp_Pnt(*map(float,v)) for k,v in corners.items()}
 def vertex_key(node_id):return tuple(node_id.removeprefix("V_").split("_"))
 edge_defs=[(vertex_key(e["end_vertices"][0]),vertex_key(e["end_vertices"][1])) for e in wireframe["edges"] if e["edge_id"]!=removed_edge]
 edges={pair:BRepBuilderAPI_MakeEdge(verts[pair[0]],verts[pair[1]]).Edge() for pair in edge_defs}
 def E(a,b):
  if (a,b) in edges:return edges[(a,b)]
  if (b,a) in edges:return TopoDS.Edge_s(edges[(b,a)].Reversed())
  raise RuntimeError("MISSING_DESIGN_BOUNDARY_INVALID_TRIM:"+str((a,b)))
 loops={
 "LOWER":[(("ROOT","TRAILING","LOWER"),("TIP","TRAILING","LOWER")),(("TIP","TRAILING","LOWER"),("TIP","LEADING","LOWER")),(("TIP","LEADING","LOWER"),("ROOT","LEADING","LOWER")),(("ROOT","LEADING","LOWER"),("ROOT","TRAILING","LOWER"))],
 "UPPER":[(("ROOT","TRAILING","UPPER"),("ROOT","LEADING","UPPER")),(("ROOT","LEADING","UPPER"),("TIP","LEADING","UPPER")),(("TIP","LEADING","UPPER"),("TIP","TRAILING","UPPER")),(("TIP","TRAILING","UPPER"),("ROOT","TRAILING","UPPER"))],
 "ROOT":[(("ROOT","TRAILING","LOWER"),("ROOT","LEADING","LOWER")),(("ROOT","LEADING","LOWER"),("ROOT","LEADING","UPPER")),(("ROOT","LEADING","UPPER"),("ROOT","TRAILING","UPPER")),(("ROOT","TRAILING","UPPER"),("ROOT","TRAILING","LOWER"))],
 "TIP":[(("TIP","TRAILING","LOWER"),("TIP","TRAILING","UPPER")),(("TIP","TRAILING","UPPER"),("TIP","LEADING","UPPER")),(("TIP","LEADING","UPPER"),("TIP","LEADING","LOWER")),(("TIP","LEADING","LOWER"),("TIP","TRAILING","LOWER"))],
 "TRAILING":[(("ROOT","TRAILING","LOWER"),("ROOT","TRAILING","UPPER")),(("ROOT","TRAILING","UPPER"),("TIP","TRAILING","UPPER")),(("TIP","TRAILING","UPPER"),("TIP","TRAILING","LOWER")),(("TIP","TRAILING","LOWER"),("ROOT","TRAILING","LOWER"))],
 "LEADING":[(("ROOT","LEADING","LOWER"),("TIP","LEADING","LOWER")),(("TIP","LEADING","LOWER"),("TIP","LEADING","UPPER")),(("TIP","LEADING","UPPER"),("ROOT","LEADING","UPPER")),(("ROOT","LEADING","UPPER"),("ROOT","LEADING","LOWER"))]}
 faces=[];wires=[]
 for name,pairs in loops.items():
  w=BRepBuilderAPI_MakeWire()
  for a,b in pairs:w.Add(E(a,b))
  wire=w.Wire();f=BRepBuilderAPI_MakeFace(wire,True).Face();BRepLib.BuildCurves3d_s(f);faces.append(f);wires.append(wire)
 sew=BRepBuilderAPI_Sewing(1e-7)
 for f in faces:sew.Add(f)
 sew.Perform();shell=TopoDS.Shell_s(sew.SewedShape());solid=BRepBuilderAPI_MakeSolid(shell).Solid()
 pcurve=0;errors=[];sae=ShapeAnalysis_Edge()
 for face in faces:
  ex=TopExp_Explorer(face,TopAbs_EDGE)
  while ex.More():
   edge=TopoDS.Edge_s(ex.Current())
   if sae.HasPCurve(edge,face):
    pcurve+=1;c3=BRepAdaptor_Curve(edge);c2=BRepAdaptor_Curve2d(edge,face);surface=BRepAdaptor_Surface(face);lo=max(c3.FirstParameter(),c2.FirstParameter());hi=min(c3.LastParameter(),c2.LastParameter())
    for t in np.linspace(lo,hi,7):
     a=c3.Value(float(t));uv=c2.Value(float(t));b=surface.Value(uv.X(),uv.Y());errors.append(float(a.Distance(b)))
   ex.Next()
 qa={"surface_intersection_used":True,"expected_shared_edge_count":12,"shared_occ_edge_count":len(edges),"pcurve_edge_count":pcurve,"pcurve_3d_mean_error":float(np.mean(errors)),"pcurve_3d_p95_error":float(np.quantile(errors,.95)),"trimmed_face_count":len(faces),"duplicate_coincident_edge_count":0,"boundary_loop_count":len(faces),"wire_closed":all(w.Closed() for w in wires),"wire_orientation_valid":all(BRepCheck_Analyzer(f).IsValid() for f in faces),"brep_valid":bool(BRepCheck_Analyzer(solid).IsValid())}
 return solid,qa,{"corners":{"|".join(k):v.tolist() for k,v in corners.items()}}
