#!/usr/bin/env python3
import argparse, json, math, shutil
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

FRACTIONS = [0.05, 0.20, 0.35, 0.50, 0.65, 0.80, 0.95]

def js(v):
    if isinstance(v, np.ndarray): return v.tolist()
    if isinstance(v, (np.floating, np.integer)): return v.item()
    raise TypeError(type(v).__name__)

def render(mesh, out, elev, azim):
    verts = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    er, ar = math.radians(elev), math.radians(azim)
    view=np.array([math.cos(er)*math.cos(ar),math.cos(er)*math.sin(ar),math.sin(er)])
    up=np.array([0.,0.,1.]) if abs(view[2])<.95 else np.array([0.,1.,0.])
    right=np.cross(view,up); right/=np.linalg.norm(right); up=np.cross(right,view)
    center=(verts.min(0)+verts.max(0))/2; q=verts-center
    xy=np.column_stack((q@right,q@up)); depth=q@view
    span=max(float(np.ptp(xy[:,0])),float(np.ptp(xy[:,1])),1e-12); scale=900*.86/span
    px=xy*scale+500; order=np.argsort(depth[faces].mean(1))
    normals=np.asarray(mesh.face_normals); light=np.array([.35,-.45,.82]); light/=np.linalg.norm(light)
    intensity=np.clip(.45+.5*np.abs(normals@light),0,1)
    im=Image.new('RGB',(1000,1000),'white'); draw=ImageDraw.Draw(im)
    for fi in order:
        col=int(110+120*intensity[fi]); poly=[tuple(px[j]) for j in faces[fi]]
        draw.polygon(poly,fill=(int(col*.86),int(col*.92),col),outline=(80,90,105))
    im.save(out)

def section_record(mesh, axis, fraction):
    lo, hi = mesh.bounds[:,axis]
    pos = float(lo + fraction*(hi-lo)); normal=np.zeros(3); normal[axis]=1
    sec=mesh.section(plane_origin=normal*pos, plane_normal=normal)
    if sec is None: return {'fraction':fraction,'position':pos,'success':False,'reason':'no intersection'}
    try: loops=sec.discrete
    except Exception as e: return {'fraction':fraction,'position':pos,'success':False,'reason':str(e)}
    contours=[]
    for loop in loops:
        pts=np.asarray(loop); dims=[i for i in range(3) if i!=axis]; q=pts[:,dims]
        if len(q)<2: continue
        perimeter=float(np.linalg.norm(np.diff(q,axis=0),axis=1).sum())
        closed=np.linalg.norm(q[0]-q[-1]) < max(1e-9, perimeter*1e-5)
        area=0.0
        if closed:
            x,y=q[:,0],q[:,1]; area=abs(float(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/2)
        sample=q[np.linspace(0,len(q)-1,min(64,len(q))).astype(int)]
        contours.append({'closed':bool(closed),'area':area,'perimeter':perimeter,'bbox':[q.min(0).tolist(),q.max(0).tolist()], 'centroid':q.mean(0).tolist(),'sample_points':sample.tolist()})
    return {'fraction':fraction,'position':pos,'success':bool(contours),'contour_count':len(contours),'total_area':sum(c['area'] for c in contours),'total_perimeter':sum(c['perimeter'] for c in contours),'contours':contours}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('root'); args=ap.parse_args()
    root=Path(args.root); src=Path(args.source); case='CADPART_000'
    for d in ['inputs','geometry','renders','logs','prompts','cad_code','step','recon_mesh','metrics','reports','scripts']:(root/d).mkdir(parents=True,exist_ok=True)
    dst=root/'inputs'/f'{case}_source.obj'
    if not dst.exists(): shutil.copy2(src,dst)
    mesh=trimesh.load(src,force='mesh',process=False)
    if not isinstance(mesh,trimesh.Trimesh): raise RuntimeError('input is not a single mesh')
    comps=mesh.split(only_watertight=False)
    v=np.asarray(mesh.vertices); centered=v-v.mean(0); cov=np.cov(centered.T); vals,vecs=np.linalg.eigh(cov); order=np.argsort(vals)[::-1]; vals=vals[order]; vecs=vecs[:,order]
    # Deterministic axis signs.
    for i in range(3):
        j=np.argmax(np.abs(vecs[:,i])); vecs[:,i]*=1 if vecs[j,i]>=0 else -1
    ext=mesh.extents; ratios=vals/max(vals.sum(),1e-30)
    # Facet normal concentration gives a conservative planar-area proxy.
    normals=np.asarray(mesh.face_normals); areas=np.asarray(mesh.area_faces); q=np.round(np.abs(normals),1)
    _, inv=np.unique(q,axis=0,return_inverse=True); bins=np.bincount(inv,weights=areas); planar=float(np.sort(bins)[-min(6,len(bins)):].sum()/max(mesh.area,1e-30))
    adj=mesh.face_adjacency
    angles=[]
    if len(adj):
        dots=np.clip((normals[adj[:,0]]*normals[adj[:,1]]).sum(1),-1,1); angles=np.arccos(dots)
    curv={'adjacent_dihedral_mean_deg':float(np.degrees(np.mean(angles))) if len(angles) else None,'adjacent_dihedral_p95_deg':float(np.degrees(np.quantile(angles,.95))) if len(angles) else None}
    symmetry=[]
    sample=mesh.sample(min(20000,max(2000,len(mesh.faces))))
    from scipy.spatial import cKDTree
    tree=cKDTree(sample)
    c=mesh.bounding_box.centroid
    for i in range(3):
        n=vecs[:,i]; mirrored=sample-2*np.outer((sample-c)@n,n); d=tree.query(mirrored,k=1)[0]; symmetry.append({'plane_normal':n.tolist(),'mean_nn_error':float(d.mean()),'relative_error':float(d.mean()/max(ext))})
    # Radius profile around primary PCA axis for revolve hypothesis.
    axis=vecs[:,0]; t=(v-c)@axis; radial=v-c-np.outer(t,axis); r=np.linalg.norm(radial,axis=1)
    profile=[]
    for f in np.linspace(0,1,25):
        tc=float(t.min()+f*(t.max()-t.min())); w=max((t.max()-t.min())*.035,1e-9); sel=np.abs(t-tc)<=w
        profile.append({'fraction':float(f),'axis_position':tc,'radius_p95':float(np.quantile(r[sel],.95)) if sel.any() else None,'radius_median':float(np.median(r[sel])) if sel.any() else None,'count':int(sel.sum())})
    radial_cv=float(np.std([x['radius_p95'] for x in profile if x['radius_p95']])/max(np.mean([x['radius_p95'] for x in profile if x['radius_p95']]),1e-30))
    elong=float(math.sqrt(vals[0]/max(vals[1],1e-30)))
    route='REVOLVE' if elong>1.7 else ('BOX' if planar>.75 else 'MIXED')
    scale_up=np.diag([1000.,1000.,1000.,1.]); scale_down=np.diag([.001,.001,.001,1.])
    report={'case_id':case,'source_path':str(src),'source_copy':str(dst),'vertices':len(mesh.vertices),'faces':len(mesh.faces),'components':len(comps),'watertight':bool(mesh.is_watertight),'volume_valid':bool(mesh.is_watertight and abs(mesh.volume)>1e-12),'bbox_min':mesh.bounds[0],'bbox_max':mesh.bounds[1],'bbox_size':mesh.extents,'bbox_center':mesh.bounding_box.centroid,'surface_area':float(mesh.area),'volume':float(abs(mesh.volume)) if mesh.is_watertight else None,'principal_axes':vecs.T,'principal_variance_ratio':ratios,'symmetry_candidates':symmetry,'planar_face_ratio':planar,'curvature_summary':curv,'primitive_hypotheses':[{'type':'REVOLVE','score':min(1.0,elong/4),'evidence':{'pca_elongation':elong,'radius_profile_cv':radial_cv}},{'type':'BOX','score':planar,'evidence':{'planar_face_ratio':planar}}],'recommended_modeling_route':route,'normalization':{'applied':True,'reason':'STEP kernel tolerance: source units to CAD millimetres','transform_source_to_cad_work':scale_up,'inverse_transform_cad_work_to_source':scale_down},'revolve_fit':{'axis_origin':c,'axis_direction':axis,'axis_min':float(t.min()),'axis_max':float(t.max()),'profile':profile}}
    (root/'geometry'/'geometry_report.json').write_text(json.dumps(report,indent=2,default=js))
    for name,axis_i in [('yz',0),('xz',1),('xy',2)]:
        rec=[section_record(mesh,axis_i,f) for f in FRACTIONS]; (root/'geometry'/f'{name}_sections.json').write_text(json.dumps({'axis_index':axis_i,'fractions':FRACTIONS,'sections':rec},indent=2))
    summary=f"case={case}\nvertices={len(mesh.vertices)} faces={len(mesh.faces)} components={len(comps)}\nwatertight={mesh.is_watertight}\nbbox={mesh.extents.tolist()}\narea={mesh.area:.9g} volume={abs(mesh.volume) if mesh.is_watertight else None}\nroute={route}\n"
    (root/'geometry'/'source_summary.txt').write_text(summary)
    views={'iso':(25,35),'front':(0,-90),'back':(0,90),'left':(0,180),'right':(0,0),'top':(90,-90),'bottom':(-90,-90)}
    for name,(el,az) in views.items(): render(mesh,root/'renders'/f'{name}.png',el,az)
    print(json.dumps({'case_id':case,'route':route,'report':str(root/'geometry'/'geometry_report.json')}))
if __name__=='__main__': main()
