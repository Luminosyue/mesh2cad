"""Strict wire builder: missing or misoriented boundaries are rejected."""

from __future__ import annotations

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeAnalysis import ShapeAnalysis_Wire


def build_wire(edges, expected_count, closed_required=True):
    if len(edges) != expected_count:
        raise ValueError("MISSING_BOUNDARY_REJECTED")
    maker = BRepBuilderAPI_MakeWire()
    for edge in edges:
        maker.Add(edge)
        if not maker.IsDone():
            raise ValueError("WIRE_EDGE_CONNECTION_REJECTED")
    wire = maker.Wire()
    if closed_required and not wire.Closed():
        raise ValueError("OPEN_WIRE_REJECTED")
    if wire.IsNull() or not BRepCheck_Analyzer(wire).IsValid():
        raise ValueError("INVALID_WIRE_REJECTED")
    return wire


def validate_orientation(wire, face):
    analysis = ShapeAnalysis_Wire(wire, face, 1e-7)
    return not bool(analysis.CheckOrder(False, False))

