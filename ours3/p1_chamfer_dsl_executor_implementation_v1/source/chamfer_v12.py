"""Minimal isolated V12 Chamfer DSL, parser, serializer, and OCC executor."""
from __future__ import annotations
import json, re
from dataclasses import dataclass
from pathlib import Path
from OCP.BRepFilletAPI import BRepFilletAPI_MakeChamfer
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.gp import gp_Vec
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.STEPControl import STEPControl_Writer, STEPControl_Reader, STEPControl_AsIs

@dataclass(frozen=True)
class Box:
    width: float; height: float; depth: float

@dataclass(frozen=True)
class Chamfer:
    body: str; distance: float

@dataclass(frozen=True)
class ExtrudePolygon:
    points: tuple; height: float

def parse(text: str):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    env={}
    for line in lines:
        m=re.fullmatch(r"(body\d+)\s*=\s*Box\(width\s*=\s*([0-9.eE+-]+),\s*height\s*=\s*([0-9.eE+-]+),\s*depth\s*=\s*([0-9.eE+-]+)\)",line)
        if m: env[m.group(1)]=Box(float(m.group(2)),float(m.group(3)),float(m.group(4))); continue
        m=re.fullmatch(r"(body\d+)\s*=\s*Chamfer\((body\d+),\s*distance\s*=\s*([0-9.eE+-]+)\)",line)
        if m: env[m.group(1)]=Chamfer(m.group(2),float(m.group(3))); continue
        m=re.fullmatch(r"(body\d+)\s*=\s*ExtrudePolygon\(points\s*=\s*(\[.*\]),\s*height\s*=\s*([0-9.eE+-]+)\)",line)
        if m:
            pts=tuple(tuple(float(z) for z in p) for p in json.loads(m.group(2)))
            env[m.group(1)]=ExtrudePolygon(pts,float(m.group(3))); continue
        raise ValueError(f"unsupported syntax: {line}")
    if not env: raise ValueError('empty program')
    return env

def serialize(env):
    out=[]
    for name,node in env.items():
        if isinstance(node,Box): out.append(f"{name} = Box(width={node.width:g}, height={node.height:g}, depth={node.depth:g})")
        elif isinstance(node,Chamfer): out.append(f"{name} = Chamfer({node.body}, distance={node.distance:g})")
        elif isinstance(node,ExtrudePolygon): out.append(f"{name} = ExtrudePolygon(points={json.dumps(node.points,separators=(',',':'))}, height={node.height:g})")
    return "\n".join(out)

def _edges(shape):
    ex=TopExp_Explorer(shape,TopAbs_EDGE); out=[]
    while ex.More(): out.append(TopoDS.Edge_s(ex.Current())); ex.Next()
    return out

def _stats(shape):
    bb=Bnd_Box(); BRepBndLib.Add_s(shape,bb); vals=bb.Get()
    props=GProp_GProps(); BRepGProp.VolumeProperties_s(shape,props)
    faces=0; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More(): faces+=1; ex.Next()
    return {'is_null':shape.IsNull(),'brep_valid':BRepCheck_Analyzer(shape).IsValid(),'face_count':faces,'edge_count':len(_edges(shape)),'volume':props.Mass(),'bbox':list(vals)}

def execute(env):
    shapes={}
    for name,node in env.items():
        if isinstance(node,Box):
            if min(node.width,node.height,node.depth)<=0: raise ValueError('Box extents must be positive')
            shapes[name]=BRepPrimAPI_MakeBox(node.width,node.height,node.depth).Shape()
        elif isinstance(node,ExtrudePolygon):
            if node.height<=0 or len(node.points)<3: raise ValueError('invalid ExtrudePolygon')
            pts=[tuple(p) for p in node.points]
            if any(len(p)!=2 for p in pts): raise ValueError('ExtrudePolygon points must be 2D')
            wire=[(p[0],p[1],0.0) for p in pts]
            face=BRepBuilderAPI_MakeFace(_polygon_wire(wire), True).Face()
            shapes[name]=BRepPrimAPI_MakePrism(face,gp_Vec(0,0,node.height),True).Shape()
        elif isinstance(node,Chamfer):
            if node.body not in shapes: raise ValueError('missing body reference')
            if node.distance<=0: raise ValueError('distance must be positive')
            body=shapes[node.body]; edges=_edges(body)
            if not edges: raise ValueError('no eligible sharp edges')
            maker=BRepFilletAPI_MakeChamfer(body)
            for edge in edges: maker.Add(node.distance,edge)
            maker.Build()
            if not maker.IsDone(): raise RuntimeError('OCC chamfer Build failed')
            result=maker.Shape()
            if result.IsNull() or not BRepCheck_Analyzer(result).IsValid(): raise RuntimeError('invalid chamfer BRep')
            shapes[name]=result
    return shapes

def _polygon_wire(points):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt
    m=BRepBuilderAPI_MakePolygon()
    for p in points: m.Add(gp_Pnt(*map(float,p)))
    m.Close(); return m.Wire()

def step_roundtrip(shape, path: str):
    w=STEPControl_Writer(); w.Transfer(shape,STEPControl_AsIs); w.Write(path)
    r=STEPControl_Reader(); status=r.ReadFile(path)
    if status != 1: raise RuntimeError(f'STEP read status {status}')
    r.TransferRoots(); loaded=r.OneShape()
    return loaded

if __name__=='__main__':
    p='body0 = Box(width=10, height=8, depth=6)\nbody1 = Chamfer(body0, distance=0.2)'
    e=parse(p); assert parse(serialize(e))==e
    shapes=execute(e); print(json.dumps({'program':serialize(e),'before':_stats(shapes['body0']),'after':_stats(shapes['body1'])}))
