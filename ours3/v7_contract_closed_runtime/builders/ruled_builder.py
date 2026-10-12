from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from .common import profile_points,polygon_wire
class RuledBuilder:
    name="RuledBuilder"
    def build(self,spec,profiles,plan):
        maker=BRepOffsetAPI_ThruSections(True,True,float(plan.get("tolerance",1e-5)));maker.CheckCompatibility(False)
        for p in profiles:maker.AddWire(polygon_wire(profile_points(spec,p)))
        maker.Build()
        if not maker.IsDone():raise RuntimeError("RULED_BUILD_FAILED")
        return maker.Shape()
