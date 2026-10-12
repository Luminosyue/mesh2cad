"""Fresh mesh-only candidate fitting. No CAD, learned weights or old programs read.
Inputs: closed component OBJ meshes. General rules use PCA, sections and error gates.
Run with the supplied CadQuery environment; writes candidates and a STEP assembly.
"""
from pathlib import Path
import argparse, json, time, hashlib, traceback
import numpy as np
import trimesh, cadquery as cq, vtk
from scipy.ndimage import gaussian_filter1d
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT.parents[1]/'outputs/airplane_fresh'
SCALE=100.0

def vtkpoly(mesh):
    p=vtk.vtkPolyData(); pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices),deep=True));p.SetPoints(pts)
    c=vtk.vtkCellArray();c.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(mesh.faces),3),mesh.faces].ravel().astype(np.int64),deep=True));p.SetPolys(c)
    return p

def surface_distance(points,mesh):
    d=vtk.vtkImplicitPolyDataDistance();d.SetInput(vtkpoly(mesh))
    return np.array([abs(d.EvaluateFunction(p)) for p in points])

def tessellate(shape):
    v,f=shape.tessellate(.035,.2)
    return trimesh.Trimesh(np.array([p.toTuple() for p in v])/SCALE,np.array(f),process=True)

def score(shape,mesh,points,diag):
    if not shape.isValid() or len(shape.Solids())!=1:raise ValueError('Invalid or non-single-solid candidate')
    tm=tessellate(shape)
    q,_=trimesh.sample.sample_surface(tm,4500,seed=83)
    a=surface_distance(points,tm);b=surface_distance(q,mesh)
    return dict(mean_pct=float((a.mean()+b.mean())*.5/diag*100),p95_pct=float(np.percentile(np.r_[a,b],95)/diag*100),max_sample_pct=float(max(a.max(),b.max())/diag*100),faces=len(shape.Faces()),volume_ratio=float(abs(shape.Volume()/SCALE**3)/abs(mesh.volume)),preview_triangles=len(tm.faces)),tm

def basis(mesh,mode):
    points,_=trimesh.sample.sample_surface(mesh,15000,seed=62)
    center=points.mean(0)
    _,_,axes=np.linalg.svd(points-center,full_matrices=False)
    axis=axes[0] if mode=='pca' else np.eye(3)[np.argmax(mesh.extents)]
    if axis[np.argmax(abs(axis))]<0:axis=-axis
    other=axes[1]-axis*np.dot(axes[1],axis)
    if np.linalg.norm(other)<.1:other=np.eye(3)[np.argmin(abs(axis))];other-=axis*np.dot(other,axis)
    other/=np.linalg.norm(other)
    B=np.stack([axis,other,np.cross(axis,other)])
    return center,B

def get_sections(mesh,mode,n):
    center,B=basis(mesh,mode)
    verts=(mesh.vertices-center)@B.T
    local=trimesh.Trimesh(verts,mesh.faces,process=False)
    lo,hi=local.bounds[:,0];span=hi-lo
    # Cosine spacing preserves thin tips without zero-area end wires.
    u=.003+.994*(1-np.cos(np.linspace(0,np.pi,n)))/2
    stations=lo+span*u
    result=[];multi=0
    theta=np.arange(64)*2*np.pi/64
    for x in stations:
        sec=local.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
        if sec is None:continue
        lines=[line[:,1:] for line in sec.discrete if len(line)>=4]
        if not lines:continue
        lines.sort(key=lambda z: abs(np.cross(z[1]-z[0],z[-1]-z[0])).sum(),reverse=True)
        raw=lines[0]
        c=raw.mean(0);sc=np.maximum(np.ptp(raw,axis=0),span*1e-5)
        radii=[]
        for t in theta:
            direction=np.array([np.cos(t),np.sin(t)])
            rr=np.linalg.norm((raw-c),axis=1);ang=np.arctan2(raw[:,1]-c[1],raw[:,0]-c[0]);delta=np.angle(np.exp(1j*(ang-t)))
            sel=np.abs(delta)<(2*np.pi/64*1.8)
            if not np.any(sel):raise ValueError('Missing section boundary')
            radii.append(float(np.max(rr[sel])))
        radii=gaussian_filter1d(np.array(radii),.6,mode='wrap')
        yz=c+np.c_[np.cos(theta),np.sin(theta)]*radii[:,None]*sc
        result.append(np.c_[np.full(64,x),yz])
    if len(result)<6:raise ValueError('Too few usable sections')
    return np.array(result),center,B,dict(axis=B[0].tolist(),section_count=len(result),significant_multi_loop_sections=multi,trim_fraction_each_end=.003)

def wire_from_points(points):
    e=cq.Edge.makeSpline([cq.Vector(*p) for p in points],periodic=True,tol=1e-5)
    return cq.Wire.assembleEdges([e])

def make_candidate(sections,center,B,kind):
    data=sections.copy()
    if kind=='extrude':
        yz=np.median(data[:,:,1:],axis=0)
        data=data[[0,-1]];data[:,:,1:]=yz
    if kind=='revolve':
        # Circle sections are rotationally symmetric about one fitted straight axis.
        yzcenter=np.median(np.mean(data[:,:,1:],axis=1),axis=0)
        radii=np.median(np.linalg.norm(data[:,:,1:]-yzcenter,axis=2),axis=1)
        x=data[:,0,0]
        wp=cq.Workplane('XY').moveTo(float(x[0]*SCALE),0).lineTo(float(x[0]*SCALE),float(radii[0]*SCALE))
        wp=wp.spline([(float(xx*SCALE),float(rr*SCALE)) for xx,rr in zip(x[1:],radii[1:])],includeCurrent=True)
        wp=wp.lineTo(float(x[-1]*SCALE),0).close()
        s=wp.revolve(360,(0,0),(1,0)).val()
        # Transform local xyz into world basis, with the profile's radial center.
        origin=(center+np.array([0,*yzcenter])@B)*SCALE
        plane=cq.Plane(origin=tuple(origin),xDir=tuple(B[0]),normal=tuple(B[2]))
        return s.moved(plane.location)
    world=(data@B+center)*SCALE
    wires=[wire_from_points(p) for p in world]
    return cq.Solid.makeLoft(wires,ruled=kind=='extrude')

def run_part(idx):
    t0=time.time();pid=f'PART_{idx:03d}';out=OUTPUT/'parts'/pid;out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'meshes/xpart'/pid/f'complete_part_{idx:03d}.obj'
    mesh=trimesh.load(source,force='mesh');diag=float(np.linalg.norm(mesh.extents))
    points,_=trimesh.sample.sample_surface(mesh,4500,seed=82)
    candidates=[];best=None;best_score=float('inf')
    for mode,n,kind in [('pca',21,'extrude'),('pca',21,'revolve'),('pca',21,'loft'),('world',25,'loft')]:
        name=f'{kind}_{mode}_{n}';r={'name':name}
        try:
            sec,center,B,meta=get_sections(mesh,mode,n)
            shape=make_candidate(sec,center,B,kind)
            metrics,tm=score(shape,mesh,points,diag);r.update(metrics,valid=True,**meta)
            # Penalize tails and excessively complicated topology as well as mean distance.
            rank=metrics['mean_pct']+.15*metrics['p95_pct']+.0005*metrics['faces']
            if rank<best_score:
                best=(shape,tm,sec,center,B,r.copy());best_score=rank
            print(pid,name,json.dumps(r),flush=True)
        except Exception as e:
            r.update(valid=False,error=str(e));print(pid,name,'FAILED',str(e),flush=True)
        candidates.append(r)
    if best is None:raise RuntimeError(f'{pid}: no valid CAD candidate')
    shape,tm,sec,center,B,chosen=best
    # Refine section density when the coarse geometry gate is not met.
    if chosen['mean_pct']>.45 or chosen['p95_pct']>1.5:
        mode='pca' if 'pca' in chosen['name'] else 'world';r={'name':f'loft_{mode}_41'}
        try:
            ss,cc,bb,meta=get_sections(mesh,mode,41);sh=make_candidate(ss,cc,bb,'loft')
            mm,tt=score(sh,mesh,points,diag);r.update(mm,valid=True,**meta)
            rank=mm['mean_pct']+.15*mm['p95_pct']+.0005*mm['faces']
            if rank<best_score:shape,tm,sec,center,B,chosen=sh,tt,ss,cc,bb,r.copy()
        except Exception as e:r.update(valid=False,error=str(e))
        candidates.append(r);print(pid,'refine',json.dumps(r),flush=True)
    final=shape.scale(1/SCALE)
    final.exportStep(str(out/'part.step'))
    check=cq.importers.importStep(str(out/'part.step')).val()
    if not check.isValid() or len(check.Solids())!=1:raise RuntimeError('STEP roundtrip failed')
    tm.export(out/'preview.stl')
    np.savez(out/'fitted_sections.npz',sections_local=sec,center=center,basis=B)
    report=dict(part_id=pid,input_mesh=str(source),input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_watertight=bool(mesh.is_watertight),candidates=candidates,selected=chosen,step_reimport_valid=check.isValid(),solid_count=len(check.Solids()),face_count=len(check.Faces()),triangular_brep_fallback=False,old_cad_used=False,elapsed_seconds=time.time()-t0)
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print('DONE',pid,chosen['name'],flush=True)

def assemble():
    assembly=cq.Assembly(name='Airplane_Fresh_Mesh_Fit')
    rows=[];shapes=[]
    for i in range(9):
        folder=OUTPUT/'parts'/f'PART_{i:03d}'
        s=cq.importers.importStep(str(folder/'part.step')).val();shapes.append(s)
        assembly.add(s,name=f'PART_{i:03d}',color=cq.Color(.38,.66,.8))
        rows.append(json.loads((folder/'report.json').read_text()))
    assembly.save(str(OUTPUT/'airplane_fresh.step'))
    compound=cq.Compound.makeCompound(shapes)
    compound.exportBrep(str(OUTPUT/'airplane_fresh.brep'))
    reopened=cq.importers.importStep(str(OUTPUT/'airplane_fresh.step')).val()
    metrics=dict(valid=reopened.isValid(),solids=len(reopened.Solids()),faces=len(reopened.Faces()),parts=rows,old_cad_used=False,learned_cad_model_used=False,mesh_segmentation_reused=True,mesh_completion_reused=True,triangular_brep_fallback=False)
    (OUTPUT/'assembly_report.json').write_text(json.dumps(metrics,indent=2))
    print('ASSEMBLY',metrics['valid'],metrics['solids'],metrics['faces'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--part',type=int);ap.add_argument('--assemble',action='store_true');a=ap.parse_args()
    if a.assemble:assemble()
    elif a.part is not None:run_part(a.part)
    else:
        for i in range(9):run_part(i)
        assemble()
