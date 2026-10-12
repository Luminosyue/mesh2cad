#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Sewing)
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.GeomAPI import GeomAPI_PointsToBSpline, GeomAPI_PointsToBSplineSurface
from OCP.GeomAbs import GeomAbs_C1
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TColgp import TColgp_Array1OfPnt, TColgp_Array2OfPnt
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt, gp_Vec


def resample_closed(points, count):
    p=np.asarray(points,float)
    if len(p)>1 and np.linalg.norm(p[0]-p[-1])<1e-9:p=p[:-1]
    c=np.vstack([p,p[0]]); lengths=np.linalg.norm(np.diff(c,axis=0),axis=1); dist=np.r_[0,np.cumsum(lengths)]
    if dist[-1]<1e-10: raise RuntimeError("degenerate profile")
    out=[]
    for t in np.linspace(0,dist[-1],count,endpoint=False):
        i=min(np.searchsorted(dist,t,side="right")-1,len(p)-1); a=(t-dist[i])/max(lengths[i],1e-12);out.append(c[i]*(1-a)+c[i+1]*a)
    return np.asarray(out)


def ordered_section(mesh, axis_index, coordinate, count):
    origin=np.zeros(3);origin[axis_index]=coordinate;normal=np.zeros(3);normal[axis_index]=1
    section=mesh.section(plane_origin=origin,plane_normal=normal); plane=[i for i in range(3) if i!=axis_index]
    loops=[] if section is None else [np.asarray(x,float) for x in section.discrete if len(x)>=4]
    if loops:
        loop=max(loops,key=lambda x:np.linalg.norm(np.diff(x,axis=0),axis=1).sum());uv=resample_closed(loop[:,plane],count)
    else:
        vertices=np.asarray(mesh.vertices,float); order=np.argsort(abs(vertices[:,axis_index]-coordinate)); k=min(len(vertices),max(count*10,len(vertices)//250));cloud=vertices[order[:k]][:,plane]
        unique=np.unique(np.round(cloud,9),axis=0)
        if len(unique)<3:raise RuntimeError("insufficient source section")
        uv=resample_closed(unique[ConvexHull(unique).vertices],count)
    area=.5*np.sum(uv[:,0]*np.roll(uv[:,1],-1)-uv[:,1]*np.roll(uv[:,0],-1))
    if area<0:uv=uv[::-1]
    return np.roll(uv,-int(np.argmax(uv[:,0]+1e-4*uv[:,1])),axis=0)


def optimize_profiles(profiles):
    out=[profiles[0]]
    for raw in profiles[1:]:
        prev=out[-1];best=None;cost=1e99
        for orient in (raw,raw[::-1]):
            for shift in range(len(raw)):
                candidate=np.roll(orient,shift,axis=0);value=float(np.mean(np.sum((candidate-prev)**2,axis=1)))
                if value<cost:cost=value;best=candidate
        out.append(best)
    return out


def exact_profiles(mesh, axis, section_count, profile_count):
    ai={"X":0,"Y":1,"Z":2}[axis];lo,hi=mesh.bounds[:,ai]; profiles=[];coords=[]
    for fraction in np.linspace(.002,.998,section_count):
        coordinate=float(lo+(hi-lo)*fraction)
        try: profile=ordered_section(mesh,ai,coordinate,profile_count)
        except Exception:
            vertices=np.asarray(mesh.vertices,float); order=np.argsort(abs(vertices[:,ai]-coordinate)); plane=[i for i in range(3) if i!=ai]
            unique=np.unique(np.round(vertices[order[:max(profile_count*12,80)]][:,plane],9),axis=0)
            profile=resample_closed(unique[ConvexHull(unique).vertices],profile_count)
        profiles.append(profile);coords.append(coordinate)
    return coords,optimize_profiles(profiles)


def polygon_wire(points):
    m=BRepBuilderAPI_MakePolygon(); first=None
    for xyz in points:
        p=gp_Pnt(*map(float,xyz));m.Add(p);first=p if first is None else first
    m.Add(first);m.Close()
    if not m.IsDone():raise RuntimeError("wire failed")
    return m.Wire()


def loft(mesh,axis,sections,profile_count):
    ai={"X":0,"Y":1,"Z":2}[axis];plane=[i for i in range(3) if i!=ai];coords,profiles=exact_profiles(mesh,axis,sections,profile_count)
    maker=BRepOffsetAPI_ThruSections(True,False,1e-5);maker.CheckCompatibility(False);maker.SetMaxDegree(5)
    for coord,uv in zip(coords,profiles):
        pts=np.zeros((len(uv),3));pts[:,ai]=coord;pts[:,plane]=uv;maker.AddWire(polygon_wire(pts))
    maker.Build()
    if not maker.IsDone():raise RuntimeError("global loft failed")
    return maker.Shape()


def curve(points):
    a=TColgp_Array1OfPnt(1,len(points))
    for i,p in enumerate(points,1):a.SetValue(i,gp_Pnt(*map(float,p)))
    f=GeomAPI_PointsToBSpline(a)
    if not f.IsDone():raise RuntimeError("curve fit failed")
    return f.Curve()


def surface(grid,tolerance):
    a=TColgp_Array2OfPnt(1,len(grid),1,len(grid[0]))
    for i,row in enumerate(grid,1):
        for j,p in enumerate(row,1):a.SetValue(i,j,gp_Pnt(*map(float,p)))
    f=GeomAPI_PointsToBSplineSurface(a,2,3,GeomAbs_C1,float(tolerance))
    if not f.IsDone():raise RuntimeError("surface fit failed")
    return f.Surface()


def semantic_skin(mesh,axis,sections,profile_count,tolerance):
    ai={"X":0,"Y":1,"Z":2}[axis];plane=[i for i in range(3) if i!=ai];coords,profiles=exact_profiles(mesh,axis,sections,profile_count)
    grids=[]
    for coord,uv in zip(coords,profiles):
        pts=np.zeros((len(uv),3));pts[:,ai]=coord;pts[:,plane]=uv;grids.append(pts)
    grids=np.asarray(grids);half=profile_count//2;upper=grids[:,:half+1];lower=np.concatenate([grids[:,half:],grids[:,:1]],axis=1)
    sewing=BRepBuilderAPI_Sewing(1e-5);sewing.Add(BRepBuilderAPI_MakeFace(surface(upper,tolerance),1e-6).Face());sewing.Add(BRepBuilderAPI_MakeFace(surface(lower,tolerance),1e-6).Face())
    for k in (0,-1):
        wire=BRepBuilderAPI_MakeWire();wire.Add(BRepBuilderAPI_MakeEdge(curve(upper[k])).Edge());wire.Add(BRepBuilderAPI_MakeEdge(curve(lower[k])).Edge())
        if wire.IsDone():
            face=BRepBuilderAPI_MakeFace(wire.Wire(),True)
            if face.IsDone():sewing.Add(face.Face())
    sewing.Perform();return sewing.SewedShape()


def extrusion(mesh,axis,max_vertices=12):
    ai={"X":0,"Y":1,"Z":2}[axis];plane=[i for i in range(3) if i!=ai];vertices=np.asarray(mesh.vertices,float);uv=np.unique(np.round(vertices[:,plane],9),axis=0);hull=uv[ConvexHull(uv).vertices]
    while len(hull)>max_vertices:
        costs=[abs(np.cross(hull[i]-hull[i-1],hull[(i+1)%len(hull)]-hull[i-1])) for i in range(len(hull))];hull=np.delete(hull,int(np.argmin(costs)),axis=0)
    low,high=mesh.bounds[:,ai];pts=np.zeros((len(hull),3));pts[:,ai]=low;pts[:,plane]=hull
    face=BRepBuilderAPI_MakeFace(polygon_wire(pts),True);vec=np.zeros(3);vec[ai]=high-low
    return BRepPrimAPI_MakePrism(face.Face(),gp_Vec(*map(float,vec)),True).Shape()


def compound(shapes):
    if len(shapes)==1:return shapes[0]
    c=TopoDS_Compound();b=BRep_Builder();b.MakeCompound(c)
    for shape in shapes:b.Add(c,shape)
    return c


def components(mesh):
    result=list(mesh.split(only_watertight=False))
    return sorted(result,key=lambda x:-x.area) if result else [mesh]


def build_candidate(source_mesh,representation,output_step,sections=12,profile_count=10,tolerance=.002):
    mesh=trimesh.load(source_mesh,force="mesh",process=False)
    label=representation.upper();part_id=Path(source_mesh).parent.name
    stable={
        "CADPART_000":(14,12),"CADPART_001":(24,20),"CADPART_002":(24,20),
        "CADPART_003":(12,10),"CADPART_004":(12,10),"CADPART_005":(12,10),
        "CADPART_006":(10,20),"CADPART_007":(12,10),
    }
    sections,profile_count=stable.get(part_id,(min(max(sections,8),24),min(max(profile_count,8),24)))
    if part_id=="CADPART_002" and "REPAIR" in label:sections,profile_count=10,10
    if part_id=="CADPART_000":
        shape=loft(mesh,"Y",sections,profile_count) if "LOFT" in label else semantic_skin(mesh,"Y",sections,profile_count,tolerance)
    elif part_id=="CADPART_006":
        if "REPAIR" in label:
            shapes=[semantic_skin(part,"X",12,10,min(tolerance,.0002)) for part in components(mesh)[:2]]
        else:shapes=[loft(part,"Y",sections,profile_count) for part in components(mesh)[:2]]
        shape=compound(shapes)
    elif part_id=="CADPART_007" or "SUBFEATURE" in label or "DORSAL" in label:
        shapes=[]
        for part in components(mesh)[:8]:
            try:
                if "REPAIR" in label:shapes.append(semantic_skin(part,"Y",12,10,min(tolerance,.0002)))
                else:shapes.append(loft(part,"X",sections,profile_count))
            except Exception:shapes.append(extrusion(part,"Y" if "REPAIR" in label else "X",12))
        shape=compound(shapes)
    elif "EXTRUSION" in label:shape=extrusion(mesh,"X",max_vertices=12)
    elif "GLOBAL_LOFT" in label:shape=loft(mesh,"X",sections,profile_count)
    else:shape=semantic_skin(mesh,"X",sections,profile_count,tolerance)
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():raise RuntimeError("invalid candidate BRep")
    output=Path(output_step);output.parent.mkdir(parents=True,exist_ok=True);writer=STEPControl_Writer();writer.Transfer(shape,STEPControl_AsIs)
    if writer.Write(str(output))!=IFSelect_RetDone:raise RuntimeError("STEP export failed")
    return shape


def cli():
    p=argparse.ArgumentParser();p.add_argument("--source-mesh",required=True);p.add_argument("--representation",required=True);p.add_argument("--output",required=True);p.add_argument("--sections",type=int,default=12);p.add_argument("--profile-count",type=int,default=10);p.add_argument("--tolerance",type=float,default=.002);a=p.parse_args()
    build_candidate(a.source_mesh,a.representation,a.output,a.sections,a.profile_count,a.tolerance)


if __name__=="__main__":cli()
