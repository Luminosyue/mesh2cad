#!/usr/bin/env python3
"""LLM-synthesized parametric CAD; deliberately independent of source mesh."""
from pathlib import Path
import math
import cadquery as cq

CASE_ID = "CADPART_000"
VERSION = "v1"
AXIS_ORIGIN = (-0.911122115, 0.111734430, -0.301673560)
AXIS_DIRECTION = (0.020500331, -0.008606524, 0.999752802)
Z_MIN, Z_MAX = -0.452251978, 0.452690637
BARREL_RADIUS = 0.08365
NECK_RADIUS = 0.0505
SHOULDER_BOTTOM = -0.382
SHOULDER_TOP = -0.302
CAP_START = 0.407

def build():
    # Profile coordinates are (radius, axial position) on the global XZ plane.
    outer = [
        (0.0, Z_MIN),
        (NECK_RADIUS * 0.78, Z_MIN),
        (NECK_RADIUS, Z_MIN + 0.018),
        (NECK_RADIUS, SHOULDER_BOTTOM),
        (BARREL_RADIUS * 0.92, SHOULDER_TOP - 0.025),
        (BARREL_RADIUS, SHOULDER_TOP),
        (BARREL_RADIUS, CAP_START),
        (BARREL_RADIUS * 0.96, CAP_START + 0.022),
        (BARREL_RADIUS * 0.72, Z_MAX - 0.010),
        (0.0, Z_MAX),
    ]
    solid = cq.Workplane("XZ").moveTo(*outer[0]).spline(outer[1:]).lineTo(0.0, Z_MIN).close().revolve(360.0, (0, Z_MIN), (0, Z_MAX))
    axis = cq.Vector(*AXIS_DIRECTION); z = cq.Vector(0,0,1); cross = z.cross(axis)
    dot = max(-1.0, min(1.0, z.dot(axis))); angle = math.degrees(math.acos(dot))
    if cross.Length > 1e-12: solid = solid.rotate((0,0,0), cross.toTuple(), angle)
    return solid.translate(AXIS_ORIGIN)

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = build()
    val = result.val()
    if val is None or val.Volume() <= 0 or not val.isValid(): raise RuntimeError("empty or invalid solid")
    cq.exporters.export(result, str(root / "step" / f"{CASE_ID}_{VERSION}.step"))
    cq.exporters.export(result, str(root / "recon_mesh" / f"{CASE_ID}_{VERSION}.stl"), tolerance=1e-4, angularTolerance=0.1)
    print(f"SOLID_VALID volume={val.Volume():.12g}")

