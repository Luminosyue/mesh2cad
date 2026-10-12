import math,numpy as np,cadquery as cq
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt,gp_Pnt2d
from OCP.Geom import Geom_BezierSurface
from OCP.GCE2d import GCE2d_MakeSegment
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_Sewing
from OCP.BRepLib import BRepLib

KEYS=[(i,j,3-i-j) for i in range(4) for j in range(4-i)]
def transform():
 M=np.zeros((16,10))
 for col,(i,j,k) in enumerate(KEYS):
  power=np.zeros((4,4));mult=math.factorial(3)/math.factorial(i)/math.factorial(j)/math.factorial(k)
  for a in range(k+1):
   for b in range(k-a+1):
    power[i+a,j+b]+=mult*math.factorial(k)/math.factorial(a)/math.factorial(b)/math.factorial(k-a-b)*(-1)**(a+b)
  for u in range(4):
   for v in range(4):
    for a in range(u+1):
     for b in range(v+1):M[u*4+v,col]+=power[a,b]*math.comb(u,a)/math.comb(3,a)*math.comb(v,b)/math.comb(3,b)
 return M
TRANSFORM=transform()

def patch_solid(mesh,beta=1.0,normals=None,max_normal_projection=None):
 p=mesh.vertices;n=mesh.vertex_normals if normals is None else normals;sew=BRepBuilderAPI_Sewing(1e-5,True,True,True,False)
 for ids in mesh.faces:
  a,b,c=p[ids];cp={(3,0,0):a,(0,3,0):b,(0,0,3):c}
  for i,j in [(0,1),(1,0),(0,2),(2,0),(1,2),(2,1)]:
   u,v=p[ids[i]],p[ids[j]];nn=n[ids[i]];k=[0,0,0];k[i]=2;k[j]=1;delta=np.dot(v-u,nn)*nn
   if max_normal_projection is not None:
    length=np.linalg.norm(delta);limit=max_normal_projection*np.linalg.norm(v-u)
    if length>limit:delta*=limit/length
   cp[tuple(k)]=(2*u+v-beta*delta)/3
  E=np.mean([v for k,v in cp.items() if 2 in k],axis=0);V=(a+b+c)/3;cp[(1,1,1)]=E+(E-V)*.5
  poles=TRANSFORM@np.array([cp[k] for k in KEYS]);arr=TColgp_Array2OfPnt(1,4,1,4)
  for i in range(4):
   for j in range(4):arr.SetValue(i+1,j+1,gp_Pnt(*poles[i*4+j]))
  surface=Geom_BezierSurface(arr);wire=BRepBuilderAPI_MakeWire()
  for aa,bb in [((0,0),(1,0)),((1,0),(0,1)),((0,1),(0,0))]:
   curve=GCE2d_MakeSegment(gp_Pnt2d(*aa),gp_Pnt2d(*bb)).Value();wire.Add(BRepBuilderAPI_MakeEdge(curve,surface).Edge())
  face=BRepBuilderAPI_MakeFace(surface,wire.Wire(),True).Face();BRepLib.BuildCurves3d_s(face);sew.Add(face)
 sew.Perform();shape=cq.Shape.cast(sew.SewedShape());sol=[]
 for shell in shape.Shells():
  s=cq.Solid.makeSolid(shell)
  if s.Volume()<0:s=cq.Shape.cast(s.wrapped.Reversed())
  sol.append(s)
 return (sol[0] if len(sol)==1 else cq.Compound.makeCompound(sol)) if sol else shape
