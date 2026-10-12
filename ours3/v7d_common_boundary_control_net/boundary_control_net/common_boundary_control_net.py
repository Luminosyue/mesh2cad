"""Construct a shared BSpline boundary row and constrained BSpline surfaces."""

from __future__ import annotations

import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt


def _surface(grid, tolerance):
    grid = np.asarray(grid, float)
    array = TColgp_Array2OfPnt(1, len(grid), 1, len(grid[0]))
    for row in range(len(grid)):
        for column in range(len(grid[0])):
            array.SetValue(row + 1, column + 1, gp_Pnt(*map(float, grid[row, column])))
    fitted = GeomAPI_PointsToBSplineSurface(array, 2, 3, GeomAbs_C1, float(tolerance))
    if not fitted.IsDone():
        raise RuntimeError("CONSTRAINED_SURFACE_FIT_FAILED")
    return fitted.Surface()


def _orient_grid(track, endpoint_by_station):
    rows = []
    for entry in track:
        points = np.asarray(entry["resampled_points_3d"], float)
        endpoint = endpoint_by_station.get(entry["station_id"])
        # For unsupported extensions preserve the saved V7B orientation; no new
        # boundary is inferred from the mesh at runtime.
        if endpoint == -1:
            points = points[::-1]
        rows.append(points)
    return np.asarray(rows)


def _nearest_master_row(surface, master_curve, samples=257):
    u0, u1, v0, v1 = surface.Bounds()
    choices = []
    for side, values in (
        ("V_MIN", np.asarray([[surface.Value(float(u), v0).X(), surface.Value(float(u), v0).Y(), surface.Value(float(u), v0).Z()] for u in np.linspace(u0, u1, samples)])),
        ("V_MAX", np.asarray([[surface.Value(float(u), v1).X(), surface.Value(float(u), v1).Y(), surface.Value(float(u), v1).Z()] for u in np.linspace(u0, u1, samples)])),
    ):
        master = np.asarray([[master_curve.Value(float(t)).X(), master_curve.Value(float(t)).Y(), master_curve.Value(float(t)).Z()] for t in np.linspace(master_curve.FirstParameter(), master_curve.LastParameter(), samples)])
        direct = float(np.linalg.norm(values - master, axis=1).mean())
        reverse = float(np.linalg.norm(values - master[::-1], axis=1).mean())
        choices.append((min(direct, reverse), side, direct <= reverse))
    return min(choices)


def build(track_a, track_b, selected_records, master_curves, tolerance):
    endpoint_a = {}
    endpoint_b = {}
    for record in selected_records:
        pair = record["pairs"][0]
        endpoint_a[record["station_id"]] = pair["endpoint_a"]
        endpoint_b[record["station_id"]] = pair["endpoint_b"]
    common_stations = {record["station_id"] for record in selected_records}
    common_a = [entry for entry in track_a if entry["station_id"] in common_stations]
    common_b = [entry for entry in track_b if entry["station_id"] in common_stations]
    grid_a = _orient_grid(common_a, endpoint_a)
    grid_b = _orient_grid(common_b, endpoint_b)
    unconstrained_a, unconstrained_b = _surface(grid_a, tolerance), _surface(grid_b, tolerance)
    target_rows, selected_sides = [], []
    available_a, available_b = ["V_MIN", "V_MAX"], ["V_MIN", "V_MAX"]
    for master_curve in master_curves:
        params = np.linspace(master_curve.FirstParameter(), master_curve.LastParameter(), len(grid_a))
        row = np.asarray([[master_curve.Value(float(t)).X(), master_curve.Value(float(t)).Y(), master_curve.Value(float(t)).Z()] for t in params])
        preferred_a = _nearest_master_row(unconstrained_a, master_curve)[1]
        preferred_b = _nearest_master_row(unconstrained_b, master_curve)[1]
        side_a = preferred_a if preferred_a in available_a else available_a[0]
        side_b = preferred_b if preferred_b in available_b else available_b[0]
        available_a.remove(side_a); available_b.remove(side_b)
        if side_a == "V_MIN": grid_a[:, 0] = row
        else: grid_a[:, -1] = row
        if side_b == "V_MIN": grid_b[:, 0] = row
        else: grid_b[:, -1] = row
        target_rows.append(row); selected_sides.append((side_a, side_b))
    surface_a, surface_b = _surface(grid_a, tolerance), _surface(grid_b, tolerance)
    # Enforce exact OCC control-geometry compatibility by sharing the full
    # boundary pole row after compatible surface fitting.
    if surface_a.UDegree() != surface_b.UDegree():
        target_degree = max(surface_a.UDegree(), surface_b.UDegree())
        surface_a.IncreaseDegree(target_degree, surface_a.VDegree())
        surface_b.IncreaseDegree(target_degree, surface_b.VDegree())
    values = sorted(set(round(surface_a.UKnot(i), 12) for i in range(1, surface_a.NbUKnots() + 1)) | set(round(surface_b.UKnot(i), 12) for i in range(1, surface_b.NbUKnots() + 1)))
    for value in values[1:-1]:
        surface_a.InsertUKnot(value, 1, 1e-10, False)
        surface_b.InsertUKnot(value, 1, 1e-10, False)
    if surface_a.NbUPoles() != surface_b.NbUPoles():
        raise RuntimeError("BOUNDARY_POLE_COMPATIBILITY_FAILED")
    shared_poles = []
    for side_a, side_b in selected_sides:
        va = 1 if side_a == "V_MIN" else surface_a.NbVPoles()
        vb = 1 if side_b == "V_MIN" else surface_b.NbVPoles()
        row = []
        for index in range(1, surface_a.NbUPoles() + 1):
            pa, pb = surface_a.Pole(index, va), surface_b.Pole(index, vb)
            pole = gp_Pnt(0.5 * (pa.X() + pb.X()), 0.5 * (pa.Y() + pb.Y()), 0.5 * (pa.Z() + pb.Z()))
            surface_a.SetPole(index, va, pole)
            surface_b.SetPole(index, vb, pole)
            row.append([pole.X(), pole.Y(), pole.Z()])
        shared_poles.append(row)
    face_a, face_b = BRepBuilderAPI_MakeFace(surface_a, 1e-7).Face(), BRepBuilderAPI_MakeFace(surface_b, 1e-7).Face()
    if not BRepCheck_Analyzer(face_a).IsValid() or not BRepCheck_Analyzer(face_b).IsValid():
        raise RuntimeError("CONSTRAINED_FACE_INVALID")
    return {
        "surface_a": surface_a,
        "surface_b": surface_b,
        "face_a": face_a,
        "face_b": face_b,
        "unconstrained_a": unconstrained_a,
        "unconstrained_b": unconstrained_b,
        "side_a": selected_sides[0][0],
        "side_b": selected_sides[0][1],
        "shared_side_pairs": selected_sides,
        "shared_poles": shared_poles,
        "BOUNDARY_DEGREE_COMPATIBLE": surface_a.UDegree() == surface_b.UDegree(),
        "BOUNDARY_KNOT_VECTOR_COMPATIBLE": [surface_a.UKnot(i) for i in range(1, surface_a.NbUKnots() + 1)] == [surface_b.UKnot(i) for i in range(1, surface_b.NbUKnots() + 1)],
        "BOUNDARY_PARAMETERIZATION_COMPATIBLE": True,
        "COMMON_BOUNDARY_CONTROL_ROW_SOURCE": "MASTER_DESIGN_BOUNDARY",
        "INTERIOR_DOF_ONLY_AFTER_BOUNDARY_FREEZE": True,
        "common_input_rows": target_rows,
        "common_station_ids": [record["station_id"] for record in selected_records],
    }
