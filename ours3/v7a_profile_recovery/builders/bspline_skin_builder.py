"""Smooth measured-profile skin; retains V7 truthful non-solid semantics."""

import numpy as np
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
from OCP.TopoDS import TopoDS_Compound
from .common import profile_points


def surface(grid, tolerance):
    array = TColgp_Array2OfPnt(1, len(grid), 1, len(grid[0]))
    for i, row in enumerate(grid, 1):
        for j, point in enumerate(row, 1):
            array.SetValue(i, j, gp_Pnt(*map(float, point)))
    fit = GeomAPI_PointsToBSplineSurface(array, 2, 3, GeomAbs_C1, float(tolerance))
    if not fit.IsDone():
        raise RuntimeError("BSPLINE_SURFACE_FAILED")
    return fit.Surface()


class BSplineSkinBuilder:
    name = "BSplineSkinBuilder"

    def build(self, spec, profiles, plan):
        if len(profiles) < 2:
            raise RuntimeError("BSPLINE_PROFILE_CONTRACT_FAIL")
        grid = np.asarray([profile_points(spec, profile) for profile in profiles])
        half = grid.shape[1] // 2
        upper = grid[:, :half + 1]
        lower = np.concatenate([grid[:, half:], grid[:, :1]], axis=1)
        tolerance = plan.get("tolerance", .001)
        faces = [BRepBuilderAPI_MakeFace(surface(upper, tolerance), 1e-6).Face(),
                 BRepBuilderAPI_MakeFace(surface(lower, tolerance), 1e-6).Face()]
        compound = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(compound)
        for face in faces:
            builder.Add(compound, face)
        return compound
