"""Sole OCC construction entry for ThruSections and PointsToBSplineSurface.

Formal reconstruction must not call those APIs anywhere else.
"""
from __future__ import annotations

from typing import Any
from contextlib import contextmanager

import numpy as np

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt


STATS: dict[str, int] = {
    "thru_sections_calls": 0,
    "bspline_surface_calls": 0,
    "make_face_after_bspline": 0,
    "direct_bypass_attempts": 0,
}

_REGISTRY_DEPTH = 0


@contextmanager
def registry_authorized():
    """Capability token proving construction entered through BuilderRegistry."""
    global _REGISTRY_DEPTH
    _REGISTRY_DEPTH += 1
    try:
        yield
    finally:
        _REGISTRY_DEPTH -= 1


def _require_registry() -> None:
    if _REGISTRY_DEPTH < 1:
        STATS["direct_bypass_attempts"] += 1
        raise RuntimeError("DIRECT_OCC_BUILDER_BYPASS_DETECTED")


def reset_stats() -> None:
    for key in STATS:
        STATS[key] = 0


def polygon_wire(points) -> Any:
    maker = BRepBuilderAPI_MakePolygon()
    first = None
    for xyz in np.asarray(points, float):
        pnt = gp_Pnt(*map(float, xyz))
        maker.Add(pnt)
        first = pnt if first is None else first
    maker.Add(first)
    maker.Close()
    if not maker.IsDone():
        raise RuntimeError("wire failed")
    return maker.Wire()


def thru_sections(wires, *, preflight_passed: bool) -> Any:
    if not preflight_passed:
        raise RuntimeError("LOFT_PREFLIGHT_REJECTED_BUT_EXECUTED")
    _require_registry()
    STATS["thru_sections_calls"] += 1
    maker = BRepOffsetAPI_ThruSections(True, False, 1e-5)
    maker.CheckCompatibility(False)
    maker.SetMaxDegree(5)
    for wire in wires:
        maker.AddWire(wire)
    maker.Build()
    if not maker.IsDone():
        raise RuntimeError("thru_sections failed")
    return maker.Shape()


def points_to_bspline_surface(grid, tolerance: float, *, grid_preflight_passed: bool) -> Any:
    if not grid_preflight_passed:
        raise RuntimeError("BSPLINE_GRID_PREFLIGHT_REJECTED_BUT_EXECUTED")
    _require_registry()
    STATS["bspline_surface_calls"] += 1
    arr = TColgp_Array2OfPnt(1, len(grid), 1, len(grid[0]))
    for i, row in enumerate(grid, 1):
        for j, pnt in enumerate(row, 1):
            arr.SetValue(i, j, gp_Pnt(*map(float, pnt)))
    fit = GeomAPI_PointsToBSplineSurface(arr, 2, 3, GeomAbs_C1, float(tolerance))
    if not fit.IsDone():
        raise RuntimeError("bspline surface fit failed")
    return fit.Surface()


def poles_of(surface) -> np.ndarray:
    nu, nv = surface.NbUPoles(), surface.NbVPoles()
    poles = np.zeros((nu, nv, 3), float)
    for u in range(1, nu + 1):
        for v in range(1, nv + 1):
            pnt = surface.Pole(u, v)
            poles[u - 1, v - 1] = [pnt.X(), pnt.Y(), pnt.Z()]
    return poles


def make_face_from_surface(surface, *, control_net_passed: bool) -> Any:
    if not control_net_passed:
        raise RuntimeError("CONTROL_NET_GUARD_REJECTED_BUT_FACE_CREATED")
    _require_registry()
    STATS["make_face_after_bspline"] += 1
    face = BRepBuilderAPI_MakeFace(surface, 1e-6)
    if not face.IsDone():
        raise RuntimeError("MakeFace failed")
    return face.Face()
