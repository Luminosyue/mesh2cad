"""Unchanged V7A closed-profile loft behavior for the V7B closed branch."""

from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from .common import profile_points, smooth_closed_wire


class LoftBuilder:
    name = "LoftBuilder"

    def build(self, spec, profiles, plan):
        if len(profiles) < 2:
            raise RuntimeError("LOFT_PROFILE_CONTRACT_FAIL")
        maker = BRepOffsetAPI_ThruSections(True, False, float(plan.get("tolerance", 1e-5)))
        maker.CheckCompatibility(False)
        maker.SetMaxDegree(5)
        for profile in profiles:
            maker.AddWire(smooth_closed_wire(profile_points(spec, profile), plan.get("curve_tolerance", 1e-6)))
        maker.Build()
        if not maker.IsDone():
            raise RuntimeError("LOFT_BUILD_FAILED")
        return maker.Shape()
