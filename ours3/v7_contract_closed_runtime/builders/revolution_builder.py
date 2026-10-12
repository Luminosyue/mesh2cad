import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.gp import gp_Ax1,gp_Dir,gp_Pnt
from .common import profile_points,polygon_wire
class RevolutionBuilder:
    name="RevolutionBuilder"
    def build(self,spec,profiles,plan):
        if not plan.get("revolution_applicable",False):raise RuntimeError("REVOLUTION_NOT_APPLICABLE")
        pts=profile_points(spec,profiles[0]);face=BRepBuilderAPI_MakeFace(polygon_wire(pts),True)
        d=np.asarray(spec["axis"]["direction"],float);o=np.asarray(spec["axis"]["origin"],float)
        return BRepPrimAPI_MakeRevol(face.Face(),gp_Ax1(gp_Pnt(*o),gp_Dir(*d)),float(plan.get("angle",2*np.pi)),True).Shape()
