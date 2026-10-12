import numpy as np,cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

def valid(shape):return bool(BRepCheck_Analyzer(shape.wrapped,True,True).IsValid())

def repair_patches(shape,center,scale):
 analyzer=BRepCheck_Analyzer(shape.wrapped,True,True);original_faces=shape.Faces();bad=[i for i,f in enumerate(original_faces) if not analyzer.IsValid(f.wrapped)]
 if not bad:return shape,[]
 if len(bad)>8:raise ValueError('Too many invalid faces for targeted STEP repair')
 big=shape.translate(tuple(-np.asarray(center))).scale(scale);faces=big.Faces();mapping=TopTools_IndexedDataMapOfShapeListOfShape();TopExp.MapShapesAndAncestors_s(big.wrapped,TopAbs_EDGE,TopAbs_FACE,mapping)
 replaced=set();fills=[];repairs=[]
 for index in bad:
  if index in replaced:continue
  f=faces[index];neighbors=[]
  for edge in f.Edges():
   for wrapped in mapping.FindFromKey(edge.wrapped):
    other=cq.Shape.cast(wrapped)
    if not other.isSame(f):neighbors.append(other)
  neighbor=max(neighbors,key=lambda x:x.Area());ni=next(i for i,x in enumerate(faces) if x.isSame(neighbor));group=[f,neighbor];outer=[]
  for face in group:
   for edge in face.Edges():
    if not any(edge.isSame(e) for other in group if other is not face for e in other.Edges()):outer.append(edge)
  wire=cq.Wire.assembleEdges(outer);fill=cq.Face.makeNSidedSurface([wire],[],degree=3,tol3d=1e-6,maxDeg=8,maxSegments=12)
  if fill.normalAt().dot(neighbor.normalAt())<0:fill=cq.Shape.cast(fill.wrapped.Reversed())
  fills.append(fill);replaced.update([index,ni]);repairs.append({'invalid_face_index':index,'merged_neighbor_index':ni,'boundary_edges':len(outer),'method':'refill adjacent triangular patches as one regular N-sided B-spline face; retain exterior 3D boundary'})
 sew=BRepBuilderAPI_Sewing(1e-5,True,True,True,False)
 for i,face in enumerate(faces):
  if i not in replaced:sew.Add(face.wrapped)
 for fill in fills:sew.Add(fill.wrapped)
 sew.Perform();s=cq.Shape.cast(sew.SewedShape());solids=[cq.Solid.makeSolid(sh) for sh in s.Shells()]
 if len(solids)!=1:raise ValueError('Targeted repair changed solid count')
 result=solids[0]
 if result.Volume()<0:result=cq.Shape.cast(result.wrapped.Reversed())
 if not valid(result):result=result.fix()
 if not valid(result):raise ValueError('Refilled BREP is invalid')
 return result.scale(1/scale).translate(tuple(center)),repairs
