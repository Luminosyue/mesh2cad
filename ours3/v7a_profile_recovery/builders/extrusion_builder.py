import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from .common import profile_points, smooth_closed_wire


class ExtrusionBuilder:
    name = "ExtrusionBuilder"

    def build(self, spec, profiles, plan):
        if not profiles:
            raise RuntimeError("EXTRUSION_PROFILE_CONTRACT_FAIL")
        profile = min(profiles, key=lambda value: abs(float(value["t"]) - .5))
        face = BRepBuilderAPI_MakeFace(smooth_closed_wire(profile_points(spec, profile),
                                                          plan.get("curve_tolerance", 1e-6)), True)
        if not face.IsDone():
            raise RuntimeError("EXTRUSION_PROFILE_INVALID")
        direction = np.asarray(spec["axis"]["direction"], float)
        direction /= np.linalg.norm(direction)
        vector = direction * float(spec["span"])
        return BRepPrimAPI_MakePrism(face.Face(), gp_Vec(*map(float, vector)), True).Shape()
