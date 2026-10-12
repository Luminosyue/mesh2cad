"""Fresh V7D3-construction OpenShellBuilder.

Consumes only resolved V11 references. It imports V7D3 construction modules but
does not read/copy the V7D3 final STEP. The two source surface primitives and
measured master boundary are referenced catalog values.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopoDS import TopoDS_Compound

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
V7D3=ROOT/'v7d3_vertical_tail_geometry_preserving_refit'
V7D=ROOT/'v7d_common_boundary_control_net'
sys.path[:0]=[str(V7D3),str(V7D)]
from geometry_preserving_refit.local_refitter import apply
from geometry_preserving_refit.master_compatibility import curve_from_three_poles,make_compatible
from geometry_preserving_refit.topology_identity import build as build_topology

def _val(resolved,key):return resolved['resolved'][key]['value']
def _consumed(resolved,keys):return [x for x in resolved.get('provenance') or [] if x['PARAMETER_NAME'] in keys]
def compound(shapes):
 out,b=TopoDS_Compound(),BRep_Builder();b.MakeCompound(out)
 for shape in shapes:b.Add(out,shape)
 return out
def split_surface(surface):
 knots=[surface.UKnot(i) for i in range(1,surface.NbUKnots()+1)];cut=knots[-2]
 extension,core=surface.Copy(),surface.Copy();u0,u1,v0,v1=surface.Bounds();extension.Segment(u0,cut,v0,v1);core.Segment(cut,u1,v0,v1)
 return extension,core
def open_shell(resolved,part_bbox,guard_cfg,counters):
 counters['OPEN_SHELL_REQUEST']=counters.get('OPEN_SHELL_REQUEST',0)+1
 surfaces_payload=_val(resolved,'surface_refs')[0]
 master_payload=_val(resolved,'master_boundary_refs')[0]
 wire_payload=_val(resolved,'wireframe_refs')[0]
 topology_payload=_val(resolved,'topology_refs')[0]
 surfaces=[BRep_Tool.Surface_s(face) for face in surfaces_payload['source_faces']]
 extensions=[];cores=[]
 for s in surfaces:
  e,c=split_surface(s);extensions.append(e);cores.append(c)
 master_curve=curve_from_three_poles(np.asarray(master_payload['shared_poles'],float))
 a,b,curve,master_poles=make_compatible(cores[0],cores[1],master_curve)
 strip_rows=int(wire_payload['boundary_strip_rows'])
 aa,ma,*_=apply(a,master_poles,'V_MIN',strip_rows,True);bb,mb,*_=apply(b,master_poles,'V_MIN',strip_rows,True)
 face_a=BRepBuilderAPI_MakeFace(aa,1e-8).Face();face_b=BRepBuilderAPI_MakeFace(bb,1e-8).Face()
 ext_faces=[BRepBuilderAPI_MakeFace(s,1e-8).Face() for s in extensions]
 precision=float(part_bbox['bbox_diag'])*float(topology_payload['precision_ratio'])
 topo=build_topology(aa,face_a,bb,face_b,'V_MIN','V_MIN',precision)
 shape=compound([topo['trimmed_face_a'],topo['trimmed_face_b'],*ext_faces])
 shared=int(topo['EDGE_OCC_VALID'] and topo['PCURVE_A_SUCCESS'] and topo['PCURVE_B_SUCCESS'])
 pc=int(topo['PCURVE_A_SUCCESS'])+int(topo['PCURVE_B_SUCCESS']);trim=int(topo['TRIMMED_FACE_A_VALID'])+int(topo['TRIMMED_FACE_B_VALID'])
 valid=bool(BRepCheck_Analyzer(shape).IsValid()) and shared>=1 and pc>=2 and trim>=2
 keys=['surface_refs','master_boundary_refs','wireframe_refs','topology_refs']
 return {'BUILDER_EXECUTED':True,'PLAN_STATUS':'PLAN_EXECUTION_SUCCESS' if valid else 'PLAN_EXECUTION_FAILED','shape':shape if valid else None,'consumed':_consumed(resolved,keys),'FRESH_BREP':valid,'OPEN_SHELL_SHARED_OCC_EDGE_COUNT':shared,'OPEN_SHELL_PCURVE_COUNT':pc,'OPEN_SHELL_TRIMMED_FACE_COUNT':trim,'OPEN_SHELL_HISTORICAL_STEP_REUSED':False,'V7D3_CONSTRUCTION_MODULES_USED':['local_refitter.apply','master_compatibility.make_compatible','topology_identity.build'],'V7D3_FINAL_STEP_READ':False,'metrics':{'MOVED_CONTROL_POINT_COUNT':ma['MOVED_CONTROL_POINT_COUNT']+mb['MOVED_CONTROL_POINT_COUNT'],'BOUNDARY_STRIP_ROWS':strip_rows}}
