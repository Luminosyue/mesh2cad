"""Additional fitting attempt with dense rings to resolve thin cross-sections."""
import inspect
import refine_sections as rs
from regenerate_smooth import *
exec(inspect.getsource(rs.fitted_track).replace('48','128').replace('points,.7','points,.4').replace('points,.45','points,.25'),rs.__dict__)
def dense_candidates(mesh):
    points,_=trimesh.sample.sample_surface(mesh,6000,seed=815);_,_,v=np.linalg.svd(points-points.mean(0),full_matrices=False)
    seen=[]
    for axis in [*np.eye(3),*v]:
        if any(abs(axis@a)>.995 for a in seen):continue
        seen.append(axis);basis=frame(axis);m=trimesh.Trimesh(mesh.vertices@basis.T,mesh.faces,process=False);lo,hi=m.bounds[:,2]
        zs=np.linspace(lo+.002*(hi-lo),hi-.002*(hi-lo),25);slices=[section(m,z) for z in zs]
        features=[];holes=[]
        for tr in rs.tracks_from_slices(slices,zs):
            fitted=rs.fitted_track(tr,zs,lo,hi)
            if fitted:features.append(dict(sections=fitted))
        for tr in rs.tracks_from_slices(slices,zs,True):
            fitted=rs.fitted_track(tr,zs,lo,hi)
            if fitted:holes.append(fitted)
        if features and len(features)<=12 and len(holes)<=12:yield dict(method='tracked_smooth_loft',basis=basis.tolist(),features=features,hole_tracks=holes,section_count=len(zs),fitting='128-point rings and uniform sections to resolve thin profiles')
rs.candidates=dense_candidates
if __name__=='__main__':process(ROOT/sys.argv[1],True)
