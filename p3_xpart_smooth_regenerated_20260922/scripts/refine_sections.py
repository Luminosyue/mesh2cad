"""Adapt section topology: fit outer surface tracks and blind/through cavity tracks."""
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.ndimage import gaussian_filter1d
import trimesh
from regenerate_smooth import section,sketch,frame

def tracks_from_slices(slices,zs,holes=False):
    tracks=[];active=[]
    for si,(s,z) in enumerate(zip(slices,zs)):
        polys=[h for _,hs in s for h in hs] if holes else [p for p,_ in s]
        if polys:
            max_area=max(p.area for p in polys)
            polys=[p for p in polys if p.area>max(.0003,.0001*max_area)]
        current=[];used=set()
        if active and polys:
            costs=np.array([[np.linalg.norm(np.array(tracks[k][-1][2].centroid.coords[0])-np.array(p.centroid.coords[0]))+.05*abs(np.sqrt(tracks[k][-1][2].area)-np.sqrt(p.area)) for p in polys] for k in active])
            rows,cols=linear_sum_assignment(costs)
            for ri,ci in zip(rows,cols):
                if costs[ri,ci]>25:continue
                k=active[ri];tracks[k].append((si,float(z),polys[ci]));current.append(k);used.add(ci)
        for j,p in enumerate(polys):
            if j not in used:tracks.append([(si,float(z),p)]);current.append(len(tracks)-1)
        active=current
    return tracks

def fitted_track(track,zs,lo,hi):
    if len(track)<2:return None
    result=[];prev=None
    for si,z,p in track:
        sk=sketch(p,True,48)
        # All profiles of a loft must use the same periodic representation.
        if sk['kind']=='circle':
            ts=np.linspace(0,2*np.pi,48,endpoint=False);q=np.c_[np.cos(ts),np.sin(ts)]*sk['radius']+sk['center'];sk=dict(kind='spline',points=q.tolist())
        q=np.array(sk['points'])
        if prev is not None:q=min((np.roll(q,k,axis=0) for k in range(len(q))),key=lambda a:np.mean((a-prev)**2))
        prev=q;sk['points']=q.tolist();result.append(dict(z=z,outer=sk,holes=[]))
    # Bound each newly appearing region by the midpoint to the preceding section.
    first,last=track[0][0],track[-1][0]
    result[0]['z']=float(lo if first==0 else (zs[first-1]+zs[first])/2)
    result[-1]['z']=float(hi if last==len(zs)-1 else (zs[last]+zs[last+1])/2)
    # Suppress section-to-section scan noise before C2 interpolation; smooth
    # coordinates, not the source mesh. The actual new surface is distance-tested.
    points=np.array([s['outer']['points'] for s in result])
    points=gaussian_filter1d(points,.7,axis=0,mode='nearest')
    points=gaussian_filter1d(points,.45,axis=1,mode='wrap')
    for s,p in zip(result,points):s['outer']['points']=p.tolist()
    return result

def candidates(mesh):
    pts,_=trimesh.sample.sample_surface(mesh,6000,seed=805);_,_,v=np.linalg.svd(pts-pts.mean(0),full_matrices=False)
    axes=[*v,*np.eye(3)];seen=[]
    for axis in axes:
        if any(abs(axis@a)>.99 for a in seen):continue
        seen.append(axis);basis=frame(axis);m=trimesh.Trimesh(mesh.vertices@basis.T,mesh.faces,process=False);lo,hi=m.bounds[:,2]
        zs=lo+(hi-lo)*np.r_[.001,.005,.015,np.linspace(.04,.96,25),.985,.995,.999]
        slices=[section(m,z) for z in zs]
        outer=tracks_from_slices(slices,zs)
        hs=tracks_from_slices(slices,zs,True)
        features=[];holetracks=[]
        for tr in outer:
            fitted=fitted_track(tr,zs,lo,hi)
            if fitted:features.append(dict(sections=fitted))
        for tr in hs:
            fitted=fitted_track(tr,zs,lo,hi)
            if fitted:holetracks.append(fitted)
        if features and len(features)<=12 and len(holetracks)<=12:
            yield dict(method='tracked_smooth_loft',basis=basis.tolist(),features=features,hole_tracks=holetracks,section_count=len(zs),fitting='outer and cavity tracks independently fitted from fresh mesh sections; inferred transitions are checked against the source')
