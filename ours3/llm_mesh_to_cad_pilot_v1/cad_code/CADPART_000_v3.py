#!/usr/bin/env python3
"""V3 parameter refinement: bounded barrel/shoulder profile, no source-mesh access."""
from pathlib import Path
import math
import cadquery as cq
import trimesh

CASE_ID="CADPART_000"; VERSION="v3"; CAD_WORK_SCALE=1000.0
AXIS_ORIGIN=(-0.911122115,0.111734430,-0.301673560); AXIS_DIRECTION=(0.020500331,-0.008606524,0.999752802)
Z_MIN,Z_MAX=-0.452251978,0.452690637
BARREL_RADIUS=.0796; NECK_RADIUS=.0478; SHOULDER_BOTTOM=-.382; SHOULDER_TOP=-.302; CAP_START=.402

def build():
    s=CAD_WORK_SCALE
    wp=(cq.Workplane("XZ").moveTo(0,Z_MIN*s)
        .lineTo(NECK_RADIUS*.82*s,Z_MIN*s)
        .spline([(NECK_RADIUS*s,(Z_MIN+.018)*s),(NECK_RADIUS*s,SHOULDER_BOTTOM*s)])
        .lineTo(BARREL_RADIUS*.92*s,(SHOULDER_TOP-.025)*s)
        .lineTo(BARREL_RADIUS*s,SHOULDER_TOP*s)
        .lineTo(BARREL_RADIUS*s,CAP_START*s)
        .spline([(BARREL_RADIUS*.96*s,(CAP_START+.020)*s),(BARREL_RADIUS*.72*s,(Z_MAX-.010)*s),(0,Z_MAX*s)])
        .lineTo(0,Z_MIN*s).close())
    solid=wp.revolve(360.,(0,Z_MIN*s),(0,Z_MAX*s))
    axis=cq.Vector(*AXIS_DIRECTION); z=cq.Vector(0,0,1); cross=z.cross(axis); angle=math.degrees(math.acos(max(-1.,min(1.,z.dot(axis)))))
    if cross.Length>1e-12: solid=solid.rotate((0,0,0),cross.toTuple(),angle)
    return solid.translate(tuple(x*s for x in AXIS_ORIGIN))

if __name__=="__main__":
    root=Path(__file__).resolve().parents[1]; result=build(); val=result.val()
    if val is None or val.Volume()<=0 or not val.isValid(): raise RuntimeError("empty or invalid solid")
    step=root/"step"/f"{CASE_ID}_{VERSION}.step"; stl=root/"recon_mesh"/f"{CASE_ID}_{VERSION}.stl"
    cq.exporters.export(result,str(step)); cq.exporters.export(result,str(stl),tolerance=.1,angularTolerance=.1)
    recon=trimesh.load(stl,force="mesh",process=False); recon.apply_scale(1/CAD_WORK_SCALE); recon.export(stl)
    print(f"SOLID_VALID volume={val.Volume():.12g}")
