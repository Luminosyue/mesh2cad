import numpy as np
from shapely.geometry import Polygon
def section(mesh,z,tol=.12):
    sec=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if sec is None:return []
    polys=[]
    for loop in sec.discrete:
        if len(loop)<4 or np.linalg.norm(loop[0]-loop[-1])>1e-4:continue
        p=Polygon(loop[:,:2])
        if not p.is_valid:p=p.buffer(0)
        for x in (list(p.geoms) if hasattr(p,'geoms') else [p]):
            if x.geom_type=='Polygon' and x.area>.002:polys.append(x)
    polys.sort(key=lambda p:p.area,reverse=True)
    result=[]
    for i,p in enumerate(polys):
        depth=sum(q.contains(p.representative_point()) for q in polys[:i])
        if depth%2==0:
            holes=[q.exterior.coords for q in polys[i+1:] if p.contains(q.representative_point()) and sum(r.contains(q.representative_point()) for r in polys[:polys.index(q)])==depth+1]
            x=Polygon(p.exterior.coords,holes).simplify(tol,preserve_topology=True)
            if x.is_valid:result.append(x)
    return result

def coords(r):return np.round(np.asarray(r.coords)[:-1],6).tolist()

def resample(poly,count=40):
    ring=poly.exterior
    q=np.array([ring.interpolate(i/count,normalized=True).coords[0] for i in range(count)])
    # Align seam using rightmost radial point; preserve counterclockwise winding.
    if not poly.exterior.is_ccw:q=q[::-1]
    start=np.argmax(q[:,0]);return np.roll(q,-start,axis=0)