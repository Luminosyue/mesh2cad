import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.gp import gp_Pnt

def frame(direction):
    d=np.asarray(direction,float);d/=np.linalg.norm(d)
    ref=np.array([0.,0.,1.]) if abs(d[2])<.9 else np.array([0.,1.,0.])
    e1=np.cross(d,ref);e1/=np.linalg.norm(e1);e2=np.cross(d,e1)
    return d,e1,e2

def profile_points(spec, profile):
    d,e1,e2=frame(spec["axis"]["direction"]);o=np.asarray(spec["axis"]["origin"],float)
    center=o+d*((float(profile["t"])-.5)*float(spec["span"]))
    uv=np.asarray(profile["points_2d"],float)
    return center+uv[:,0,None]*e1+uv[:,1,None]*e2

def polygon_wire(points):
    maker=BRepBuilderAPI_MakePolygon();first=None
    for xyz in points:
        p=gp_Pnt(*map(float,xyz));maker.Add(p);first=p if first is None else first
    maker.Add(first);maker.Close()
    if not maker.IsDone():raise RuntimeError("profile wire failed")
    return maker.Wire()
