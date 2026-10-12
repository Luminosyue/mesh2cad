import numpy as np
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakeWire,BRepBuilderAPI_Sewing
from OCP.GeomAPI import GeomAPI_PointsToBSpline,GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1
from OCP.TColgp import TColgp_Array1OfPnt,TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
from OCP.TopoDS import TopoDS_Compound
from .common import profile_points
def curve(points):
    a=TColgp_Array1OfPnt(1,len(points))
    for i,p in enumerate(points,1):a.SetValue(i,gp_Pnt(*map(float,p)))
    f=GeomAPI_PointsToBSpline(a)
    if not f.IsDone():raise RuntimeError("BSPLINE_CURVE_FAILED")
    return f.Curve()
def surface(grid,tol):
    a=TColgp_Array2OfPnt(1,len(grid),1,len(grid[0]))
    for i,row in enumerate(grid,1):
        for j,p in enumerate(row,1):a.SetValue(i,j,gp_Pnt(*map(float,p)))
    f=GeomAPI_PointsToBSplineSurface(a,2,3,GeomAbs_C1,float(tol))
    if not f.IsDone():raise RuntimeError("BSPLINE_SURFACE_FAILED")
    return f.Surface()
class BSplineSkinBuilder:
    name="BSplineSkinBuilder"
    def build(self,spec,profiles,plan):
        grid=np.asarray([profile_points(spec,p) for p in profiles]);n=grid.shape[1];half=n//2
        upper=grid[:,:half+1];lower=np.concatenate([grid[:,half:],grid[:,:1]],axis=1);tol=plan.get("tolerance",.001)
        faces=[BRepBuilderAPI_MakeFace(surface(upper,tol),1e-6).Face(),BRepBuilderAPI_MakeFace(surface(lower,tol),1e-6).Face()]
        # Root/tip caps are optional here. Adding two independently parameterized
        # spline edges as a wire may be topologically open even when endpoints
        # are geometrically close. V7 refuses that invalid cap instead of
        # reporting a pseudo-solid; the global upper/lower skins remain explicit.
        # A compound of explicitly generated semantic faces is the truthful
        # output here. Sewing is a cleanup operation and must not silently turn
        # a valid surface representation into an invalid pseudo-solid.
        compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
        for face in faces:builder.Add(compound,face)
        return compound
