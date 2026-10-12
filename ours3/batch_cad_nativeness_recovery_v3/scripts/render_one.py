#!/usr/bin/env python3
import os,sys
from pathlib import Path
import numpy as np
import pyvista as pv
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED,TopAbs_EDGE
from OCP.TopExp import TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Curve

step,out,mode=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
r=STEPControl_Reader();assert r.ReadFile(str(step))==IFSelect_RetDone;r.TransferRoots();s=r.OneShape()
def idx(k):m=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(s,k,m);return m
BRepTools.Clean_s(s);BRepMesh_IncrementalMesh(s,0.01,False,.35,True).Perform();pts=[];faces=[];fm=idx(TopAbs_FACE)
for i in range(1,fm.Extent()+1):
 f=TopoDS.Face_s(fm.FindKey(i));loc=TopLoc_Location();t=BRep_Tool.Triangulation_s(f,loc)
 if t is None:continue
 o=len(pts);tr=loc.Transformation();pts += [[*(lambda p:(p.X(),p.Y(),p.Z()))(t.Node(j).Transformed(tr))] for j in range(1,t.NbNodes()+1)]
 for j in range(1,t.NbTriangles()+1):
  a,b,c=t.Triangle(j).Get();
  if f.Orientation()==TopAbs_REVERSED:b,c=c,b
  faces.append([3,o+a-1,o+b-1,o+c-1])
p=pv.Plotter(off_screen=True,window_size=(760,520));p.set_background('white');mesh=pv.PolyData(np.asarray(pts),np.asarray(faces))
if mode=='semantic':
 p.add_mesh(mesh,scalars=np.arange(mesh.n_cells)%12,cmap='tab20',show_edges=True,edge_color='#27465f',line_width=.3)
elif mode=='artificial':
 p.add_mesh(mesh,color='#dbe8f2',show_edges=True,edge_color='#e45756',line_width=.7)
elif mode=='edges':
 p.add_mesh(mesh,color='#f3f5f6',show_edges=True,edge_color='#18344f',line_width=.8)
else:p.add_mesh(mesh,color='#78b7d7',smooth_shading=True,show_edges=False)
p.view_isometric();p.camera.zoom(1.3);p.show(screenshot=str(out),auto_close=True)
os._exit(0)
