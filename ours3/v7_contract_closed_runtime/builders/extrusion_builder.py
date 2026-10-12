import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from .common import profile_points,polygon_wire
class ExtrusionBuilder:
    name="ExtrusionBuilder"
    def build(self,spec,profiles,plan):
        p=min(profiles,key=lambda x:abs(float(x["t"])))
        pts=profile_points(spec,p);face=BRepBuilderAPI_MakeFace(polygon_wire(pts),True)
        if not face.IsDone():raise RuntimeError("EXTRUSION_PROFILE_INVALID")
        d=np.asarray(spec["axis"]["direction"],float);d/=np.linalg.norm(d);vec=d*float(spec["span"])
        return BRepPrimAPI_MakePrism(face.Face(),gp_Vec(*map(float,vec)),True).Shape()
