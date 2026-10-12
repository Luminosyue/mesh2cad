"""Smallest-valid-tolerance topological sewing after trimming only."""

from __future__ import annotations

from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer


def count(shape, kind):
    explorer, value = TopExp_Explorer(shape, kind), 0
    while explorer.More():
        value += 1
        explorer.Next()
    return value


def sew_smallest_valid(trimmed_faces, diagonal, relative_tolerances=(1e-7, 1e-6, 1e-5), large_limit=1e-5):
    attempts = []
    for relative in relative_tolerances:
        tolerance = relative * diagonal
        sewing = BRepBuilderAPI_Sewing(tolerance, True, True, True, False)
        for face in trimmed_faces:
            sewing.Add(face)
        sewing.Perform()
        shape = sewing.SewedShape()
        valid = not shape.IsNull() and bool(BRepCheck_Analyzer(shape).IsValid())
        shell_count = count(shape, TopAbs_SHELL) if not shape.IsNull() else 0
        attempts.append({"relative_tolerance": relative, "absolute_tolerance": tolerance, "valid": valid, "shell_count": shell_count, "face_count": count(shape, TopAbs_FACE) if not shape.IsNull() else 0})
        if valid and shell_count == 1:
            return shape, {"attempts": attempts, "minimum_valid_tolerance": tolerance, "large_tolerance_required": relative > large_limit}
    return None, {"attempts": attempts, "minimum_valid_tolerance": None, "large_tolerance_required": False}

