"""Build genuine CAD faces from measured open B-spline chain tracks."""

import numpy as np
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GeomAbs import GeomAbs_C1
from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt


def _validate_track(track):
    if len(track) < 2:
        raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
    stations = [entry.get("station_id") for entry in track]
    if len(stations) != len(set(stations)):
        raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
    for entry in track:
        points = np.asarray(entry.get("resampled_points_3d"), float)
        if points.ndim != 2 or points.shape[1] != 3 or len(points) < 4:
            raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
        if not entry.get("ordering_valid") or not entry.get("smooth_curve", {}).get("valid"):
            raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")


def make_surface(grid, tolerance):
    grid = np.asarray(grid, float)
    array = TColgp_Array2OfPnt(1, grid.shape[0], 1, grid.shape[1])
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            array.SetValue(row + 1, col + 1, gp_Pnt(*map(float, grid[row, col])))
    fit = GeomAPI_PointsToBSplineSurface(array, 2, 3, GeomAbs_C1, float(tolerance))
    if not fit.IsDone():
        raise RuntimeError("OPEN_SHELL_BSPLINE_SURFACE_FAILED")
    return fit.Surface()


class OpenShellSkinBuilder:
    name = "OpenShellSkinBuilder"

    def build(self, measured_spec, construction_plan):
        if construction_plan.get("profile_source") != "GEOMETRY_ANALYZER":
            raise ValueError("OPEN_SHELL_PROFILE_CONTRACT_BYPASSED")
        if construction_plan.get("runtime_profile_remeasurement"):
            raise ValueError("OPEN_SHELL_PROFILE_CONTRACT_BYPASSED")
        tracks = measured_spec.get("open_chain_tracks", {})
        faces, provenance = [], []
        for track_id, track in sorted(tracks.items()):
            _validate_track(track)
            grid = np.asarray([entry["resampled_points_3d"] for entry in track], float)
            if len({len(row) for row in grid}) != 1:
                raise ValueError("INVALID_OPEN_CHAIN_RUNTIME_REJECTED")
            face = BRepBuilderAPI_MakeFace(
                make_surface(grid, construction_plan.get("surface_tolerance", 1e-4)), 1e-7
            ).Face()
            if face.IsNull() or not BRepCheck_Analyzer(face).IsValid():
                raise RuntimeError("OPEN_SHELL_FACE_INVALID")
            faces.append(face)
            provenance.append({
                "surface_id": f"SURF_{len(faces)-1:02d}",
                "builder": self.name,
                "source_track": track_id,
                "station_ids": [entry["station_id"] for entry in track],
                "profile_source": "GEOMETRY_ANALYZER",
                "runtime_remeasurement": False,
                "forced_closure": False,
                "fallback_used": False,
                "surface_type": "BSPLINE",
                "profile_sample_polyline_preserved_as_edges": False,
            })
        if not faces:
            raise RuntimeError("NO_VALID_OPEN_SHELL_SURFACE")
        compound, builder = TopoDS_Compound(), BRep_Builder()
        builder.MakeCompound(compound)
        for face in faces:
            builder.Add(compound, face)
        return compound, provenance
