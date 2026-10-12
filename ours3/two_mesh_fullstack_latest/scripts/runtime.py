#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Sewing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
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
    c=np.vstack([p,p[0]]);lengths=np.linalg.norm(np.diff(c,axis=0),axis=1);dist=np.r_[0,np.cumsum(lengths)]
    if dist[-1]<1e-10:raise RuntimeError("degenerate profile")
    out=[]
    for t in np.linspace(0,dist[-1],count,endpoint=False):
        i=min(np.searchsorted(dist,t,side="right")-1,len(p)-1);a=(t-dist[i])/max(lengths[i],1e-12);out.append(c[i]*(1-a)+c[i+1]*a)
    return np.asarray(out)


def axis_index(mesh):return int(np.argmax(mesh.extents))


def ordered_section(mesh,ai,coordinate,count):
    origin=np.zeros(3);origin[ai]=coordinate;normal=np.zeros(3);normal[ai]=1;plane=[i for i in range(3) if i!=ai]
    section=mesh.section(plane_origin=origin,plane_normal=normal);loops=[] if section is None else [np.asarray(x,float) for x in section.discrete if len(x)>=4]
    if loops:loop=max(loops,key=lambda x:np.linalg.norm(np.diff(x,axis=0),axis=1).sum());uv=resample_closed(loop[:,plane],count)
    else:
        vertices=np.asarray(mesh.vertices,float);order=np.argsort(abs(vertices[:,ai]-coordinate));k=min(len(vertices),max(count*12,len(vertices)//250));cloud=np.unique(np.round(vertices[order[:k]][:,plane],9),axis=0)
        if len(cloud)<3:raise RuntimeError("insufficient section")
        uv=resample_closed(cloud[ConvexHull(cloud).vertices],count)
    area=.5*np.sum(uv[:,0]*np.roll(uv[:,1],-1)-uv[:,1]*np.roll(uv[:,0],-1))
    if area<0:uv=uv[::-1]
    return np.roll(uv,-int(np.argmax(uv[:,0]+1e-4*uv[:,1])),axis=0)


def profiles(mesh,sections,count):
    ai=axis_index(mesh);lo,hi=mesh.bounds[:,ai];result=[];coords=[]
    for fraction in np.linspace(.003,.997,sections):
        coordinate=float(lo+(hi-lo)*fraction);result.append(ordered_section(mesh,ai,coordinate,count));coords.append(coordinate)
    aligned=[result[0]]
    for raw in result[1:]:
        prev=aligned[-1];best=None;cost=1e99
        for orient in (raw,raw[::-1]):
            for shift in range(len(raw)):
                candidate=np.roll(orient,shift,axis=0);value=float(np.mean(np.sum((candidate-prev)**2,axis=1)))
                if value<cost:cost=value;best=candidate
        aligned.append(best)
    return ai,coords,aligned


def polygon_wire(points):
    maker=BRepBuilderAPI_MakePolygon();first=None
    for xyz in points:
        p=gp_Pnt(*map(float,xyz));maker.Add(p);first=p if first is None else first
    maker.Add(first);maker.Close()
    if not maker.IsDone():raise RuntimeError("wire failed")
    return maker.Wire()


def loft(mesh,sections,count):
    ai,coords,rows=profiles(mesh,sections,count);plane=[i for i in range(3) if i!=ai];maker=BRepOffsetAPI_ThruSections(True,False,1e-5);maker.CheckCompatibility(False);maker.SetMaxDegree(5)
    for coordinate,uv in zip(coords,rows):
        pts=np.zeros((len(uv),3));pts[:,ai]=coordinate;pts[:,plane]=uv;maker.AddWire(polygon_wire(pts))
    maker.Build()
    if not maker.IsDone():raise RuntimeError("global loft failed")
    return maker.Shape()


def curve(points):
    arr=TColgp_Array1OfPnt(1,len(points))
    for i,p in enumerate(points,1):arr.SetValue(i,gp_Pnt(*map(float,p)))
    fit=GeomAPI_PointsToBSpline(arr)
    if not fit.IsDone():raise RuntimeError("curve fit failed")
    return fit.Curve()


def surface(grid,tolerance):
    arr=TColgp_Array2OfPnt(1,len(grid),1,len(grid[0]))
    for i,row in enumerate(grid,1):
        for j,p in enumerate(row,1):arr.SetValue(i,j,gp_Pnt(*map(float,p)))
    fit=GeomAPI_PointsToBSplineSurface(arr,2,3,GeomAbs_C1,float(tolerance))
    if not fit.IsDone():raise RuntimeError("surface fit failed")
    return fit.Surface()


def semantic_skin(mesh,sections,count,tolerance):
    if count%2:count+=1
    ai,coords,rows=profiles(mesh,sections,count);plane=[i for i in range(3) if i!=ai];grid=[]
    for coordinate,uv in zip(coords,rows):
        pts=np.zeros((len(uv),3));pts[:,ai]=coordinate;pts[:,plane]=uv;grid.append(pts)
    grid=np.asarray(grid);half=count//2;upper=grid[:,:half+1];lower=np.concatenate([grid[:,half:],grid[:,:1]],axis=1)
    sew=BRepBuilderAPI_Sewing(1e-5);sew.Add(BRepBuilderAPI_MakeFace(surface(upper,tolerance),1e-6).Face());sew.Add(BRepBuilderAPI_MakeFace(surface(lower,tolerance),1e-6).Face())
    for k in (0,-1):
        wire=BRepBuilderAPI_MakeWire();wire.Add(BRepBuilderAPI_MakeEdge(curve(upper[k])).Edge());wire.Add(BRepBuilderAPI_MakeEdge(curve(lower[k])).Edge())
        if wire.IsDone():
            face=BRepBuilderAPI_MakeFace(wire.Wire(),True)
            if face.IsDone():sew.Add(face.Face())
    sew.Perform();return sew.SewedShape()


def extrusion(mesh,max_vertices=16):
    ai=axis_index(mesh);plane=[i for i in range(3) if i!=ai];vertices=np.asarray(mesh.vertices,float);uv=np.unique(np.round(vertices[:,plane],9),axis=0);hull=uv[ConvexHull(uv).vertices]
    while len(hull)>max_vertices:
        costs=[abs(np.cross(hull[i]-hull[i-1],hull[(i+1)%len(hull)]-hull[i-1])) for i in range(len(hull))];hull=np.delete(hull,int(np.argmin(costs)),axis=0)
    lo,hi=mesh.bounds[:,ai];pts=np.zeros((len(hull),3));pts[:,ai]=lo;pts[:,plane]=hull;face=BRepBuilderAPI_MakeFace(polygon_wire(pts),True);vec=np.zeros(3);vec[ai]=hi-lo
    return BRepPrimAPI_MakePrism(face.Face(),gp_Vec(*map(float,vec)),True).Shape()


def compound(shapes):
    if len(shapes)==1:return shapes[0]
    result=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(result)
    for shape in shapes:builder.Add(result,shape)
    return result


def components(mesh):
    result=list(mesh.split(only_watertight=False));return sorted(result,key=lambda x:-x.area) if result else [mesh]


def build(source_mesh,representation,output,sections=14,profile_count=12,tolerance=.001):
    mesh=trimesh.load(source_mesh,force="mesh",process=False);label=representation.upper();parts=components(mesh)
    sections=min(max(sections,8),20);profile_count=min(max(profile_count,8),20)
    if "SUBFEATURE" in label or (len(parts)>1 and "HYBRID" in label):
        shapes=[]
        for part in parts[:16]:
            try:shapes.append(extrusion(part,16) if "EXTRUSION" in label else semantic_skin(part,10,10,tolerance))
            except Exception:shapes.append(loft(part,10,10))
        shape=compound(shapes)
    elif "EXTRUSION" in label or "REVOLUTION" in label:shape=extrusion(mesh,16 if "EXTRUSION" in label else 20)
    elif "LOFT" in label or "SWEEP" in label:shape=loft(mesh,sections,profile_count)
    else:shape=semantic_skin(mesh,sections,profile_count,tolerance)
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():raise RuntimeError("invalid candidate BRep")
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True);writer=STEPControl_Writer();writer.Transfer(shape,STEPControl_AsIs)
    if writer.Write(str(path))!=IFSelect_RetDone:raise RuntimeError("STEP export failed")


def main():
    p=argparse.ArgumentParser();p.add_argument("--source-mesh",required=True);p.add_argument("--representation",required=True);p.add_argument("--output",required=True);p.add_argument("--sections",type=int,default=14);p.add_argument("--profile-count",type=int,default=12);p.add_argument("--tolerance",type=float,default=.001);a=p.parse_args();build(a.source_mesh,a.representation,a.output,a.sections,a.profile_count,a.tolerance)


if __name__=="__main__":main()
