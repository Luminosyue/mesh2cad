
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
import trimesh
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.GC import GC_MakeCircle
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs

def pca_local(mesh):
    vertices=np.asarray(mesh.vertices,dtype=float)
    centroid=vertices.mean(axis=0)
    centered=vertices-centroid
    values,vectors=np.linalg.eigh((centered.T@centered)/max(len(vertices),1))
    order=np.argsort(values)[::-1]
    axes=vectors[:,order]
    local=centered@axes
    return centroid,axes,local

def build_profile_loft(mesh, output, measurements_path, quantile=0.5, section_count=64):
    centroid,axes,local=pca_local(mesh)
    x=local[:,0]
    uv=local[:,1:]
    uv_center=uv.mean(axis=0)
    radial=np.linalg.norm(uv-uv_center,axis=1)
    edges=np.linspace(float(x.min()), float(x.max()), int(section_count))
    sections=[]
    runtime_sections=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(x>=lo)&(x<=hi)
        if int(mask.sum()) < 8:
            continue
        xi=float((lo+hi)*0.5)
        ri=float(np.quantile(radial[mask], quantile))
        if ri <= 1e-8:
            continue
        origin=(np.array([xi,uv_center[0],uv_center[1]],dtype=float)@axes.T + centroid).tolist()
        axis=axes[:,0].tolist()
        circle=GC_MakeCircle(gp_Ax2(gp_Pnt(*map(float,origin)), gp_Dir(*map(float,axis))), ri).Value()
        edge=BRepBuilderAPI_MakeEdge(circle).Edge()
        wire=BRepBuilderAPI_MakeWire(edge).Wire()
        sections.append(wire)
        runtime_sections.append({"station": xi, "radius": ri, "support_vertex_count": int(mask.sum())})
    if len(sections) < 2:
        raise RuntimeError("INSUFFICIENT_RUNTIME_SECTIONS")
    loft=BRepOffsetAPI_ThruSections(False, True, 1e-4)
    for wire in sections:
        loft.AddWire(wire)
    loft.CheckCompatibility(False)
    loft.Build()
    shape=loft.Shape()
    writer=STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status=writer.Write(str(output))
    measurements={
        "source_part_reread": True,
        "source_part_path": str(args.source_part),
        "builder_family": "PROFILE_LOFT_OPEN_SHELL",
        "quantile": quantile,
        "section_count_requested": int(section_count),
        "section_count_used": len(runtime_sections),
        "principal_axes": axes.tolist(),
        "centroid": centroid.tolist(),
        "sections": runtime_sections,
        "dimension_provenance": "runtime reread source_part.obj; MAC selected how, not dimensions",
        "step_write_status": str(status),
        "step_success": bool(status == IFSelect_RetDone and output.is_file() and output.stat().st_size > 0),
    }
    measurements_path.write_text(json.dumps(measurements, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if measurements["step_success"] else 2

parser=argparse.ArgumentParser()
parser.add_argument("--source-part", type=Path, required=True)
parser.add_argument("--hypothesis", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--runtime-measurements", type=Path, required=True)
args=parser.parse_args()
hypothesis=json.loads(args.hypothesis.read_text(encoding="utf-8"))
mesh=trimesh.load(args.source_part, force="mesh", process=False)
quantile=float(hypothesis.get("quantile", 0.5))
section_count=int(hypothesis.get("section_count", 64))
raise SystemExit(build_profile_loft(mesh, args.output, args.runtime_measurements, quantile, section_count))
