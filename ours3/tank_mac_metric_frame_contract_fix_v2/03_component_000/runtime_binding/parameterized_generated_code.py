#!/usr/bin/env python3
"""Parameterized MAC construction. Metrics come from RuntimeGeometryParameters."""
from __future__ import annotations
from pathlib import Path

def gen_step(params, output):
    import cadquery as cq
    length = float(params.x_max - params.x_min)
    solid = cq.Workplane("YZ").ellipse(max(params.radius_y, 1e-6), max(params.radius_z, 1e-6)).extrude(length)
    solid = solid.translate((params.x_min, 0.0, 0.0))
    cq.exporters.export(solid, str(output))
    return {"shape": solid, "builder_family": "PROFILE_EXTRUSION"}
