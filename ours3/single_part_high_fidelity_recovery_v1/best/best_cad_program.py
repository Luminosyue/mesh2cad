#!/usr/bin/env python3
"""Measured parametric loft for REAL_03/part_000; no mesh deformation or ICP."""
import json, math
from pathlib import Path

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.gp import gp_Pnt

HERE = Path(__file__).resolve().parent
PROFILE = HERE.parent / "case" / "REAL_03_part_000" / "revolve_profile_v1.json"
OUTPUT = HERE / "generated.step"

def add(a, b, scale=1.0):
    return [a[i] + scale * b[i] for i in range(3)]

def point(origin, u, v, axis, x, y, z):
    p = add(origin, axis, z)
    p = add(p, u, x)
    return add(p, v, y)

def section_wire(section, frame, count=72):
    a=float(section["half_width"]); b=float(section["half_thickness"])
    shape=section["shape"]
    exponent=2.0 if shape=="CIRCLE" else float(section.get("exponent", 7.0))
    mk=BRepBuilderAPI_MakePolygon()
    first=None
    for i in range(count):
        t=2*math.pi*i/count; ct=math.cos(t); st=math.sin(t)
        x=a*math.copysign(abs(ct)**(2.0/exponent),ct)
        y=b*math.copysign(abs(st)**(2.0/exponent),st)
        q=point(frame["axis_origin"],frame["basis_u"],frame["basis_v"],frame["axis_direction"],x,y,float(section["z"]))
        p=gp_Pnt(*q); mk.Add(p)
        if first is None:first=p
    mk.Add(first); mk.Close()
    return mk.Wire()

def build():
    frame=json.loads(PROFILE.read_text(encoding="utf-8"))
    # Ruled interpolation prevents spline overshoot between the circular shaft
    # and the strongly anisotropic blade sections.
    loft=BRepOffsetAPI_ThruSections(True,True,1e-7)
    loft.CheckCompatibility(True)
    for section in frame["ordered_sections"]:
        loft.AddWire(section_wire(section,frame))
    loft.Build()
    if not loft.IsDone(): raise RuntimeError("measured loft failed")
    shape=loft.Shape()
    if not BRepCheck_Analyzer(shape).IsValid(): raise RuntimeError("measured loft is invalid")
    writer=STEPControl_Writer(); writer.Transfer(shape,STEPControl_AsIs)
    status=writer.Write(str(OUTPUT))
    if status!=IFSelect_RetDone: raise RuntimeError(f"STEP write status={status}")
    return shape

if __name__=="__main__":
    build(); print(OUTPUT)
