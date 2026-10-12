from pathlib import Path
import json, shutil, hashlib
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import cKDTree

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/tire_p1_canonical_visual_20260919')
OUT=ROOT/'deliverables'; OUT.mkdir(exist_ok=True)
pack=ROOT/'packs/PART_006'
tf=json.loads((pack/'coordinate_transform.json').read_text())
curves=json.loads((pack/'curve_fits.json').read_text())
src=trimesh.load(ROOT/'source.stl',force='mesh')
predpath=ROOT/'predictions/D/PART_006/global/pred.stl'
bg='#f4f7fb'; blue='#579cbd'; orange='#e17635'; ink='#21374e'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':ink,'axes.labelcolor':ink,'axes.titleweight':'semibold','savefig.facecolor':bg,'figure.facecolor':bg})

def frame(ax,bounds,elev=28,azim=-58):
    center=np.mean(bounds,axis=0); radius=np.max(bounds[1]-bounds[0])*0.55
    for setter,c in zip((ax.set_xlim,ax.set_ylim,ax.set_zlim),center): setter(c-radius,c+radius)
    ax.set_box_aspect([1,1,1]); ax.view_init(elev=elev,azim=azim); ax.set_axis_off(); ax.set_facecolor(bg)

def meshplot(ax,m,alpha=1):
    n=m.face_normals; light=np.array([-0.4,-0.6,0.7]); light/=np.linalg.norm(light)
    shade=0.52+0.48*np.maximum(n@light,0)
    base=np.array(matplotlib.colors.to_rgb(blue))
    colors=np.c_[shade[:,None]*base,np.full(len(n),alpha)]
    ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=colors,edgecolors='none',rasterized=True))

def original(p): return (np.asarray(p)-np.array(tf['translation']))/tf['scale']

# Mesh-coordinate views and retained geometric curves.
fig=plt.figure(figsize=(15,7.6))
for k in range(2):
    ax=fig.add_subplot(1,2,k+1,projection='3d')
    if k==0: meshplot(ax,src,0.18)
    for c in curves:
        raw=original(c['polyline']); fit=original(c['fitted_xyz'])
        ax.plot(*raw.T,color=blue,lw=1.2,alpha=0.75)
        ax.plot(*fit.T,color=orange,lw=1.5)
    frame(ax,src.bounds,28 if k==0 else 90,-58 if k==0 else -90)
    ax.set_title('Curves on input mesh' if k==0 else 'Top view: polyline vs fitted arc',pad=0)
fig.suptitle('P1 input curve fitting | 24 retained chains',fontsize=21,x=0.05,ha='left',y=.98)
fig.text(.05,.025,'Blue: extracted mesh polylines   |   Orange: analytic fits   |   30-degree sharp-edge threshold',fontsize=12)
fig.subplots_adjust(left=0,right=1,bottom=.06,top=.91,wspace=0)
fig.savefig(OUT/'curve_fit_overview.png',dpi=170); plt.close(fig)

rows=[]
fig,axes=plt.subplots(4,6,figsize=(18,12))
for i,(ax,c) in enumerate(zip(axes.flat,curves)):
    raw=np.array(c['polyline']); pts=np.array(c['encoder_xyz']); fit=np.array(c['fitted_xyz'])
    ctr=pts.mean(0); _,_,v=np.linalg.svd(pts-ctr,full_matrices=False)
    r=(raw-ctr)@v[:2].T; f=(fit-ctr)@v[:2].T; p=(pts-ctr)@v[:2].T
    ax.plot(*r.T,color=blue,lw=1.4); ax.plot(*f.T,color=orange,lw=1.5); ax.scatter(*p.T,s=7,color=blue,zorder=3)
    ax.set_aspect('equal',adjustable='datalim'); ax.margins(.15); ax.set_facecolor('white'); ax.grid(alpha=.15)
    measured=float(np.sqrt(np.mean(cKDTree(fit).query(pts)[0]**2)))
    rms=float(c['rms_fit']); pct=100*rms/6
    rows.append({'curve_id':i+1,'type':c['type'],'fit_rms_canonical':rms,'fit_rms_source_units':rms/tf['scale'],'fit_rms_percent_source_diagonal':pct,'sample_to_dense_fit_rms_canonical':measured,'n_polyline_vertices':len(raw)})
    ax.set_title(f"{i+1:02d}  {c['type']}\nRMS / diagonal = {pct:.3f}%",fontsize=10)
    ax.tick_params(labelsize=7); ax.locator_params(nbins=3)
fig.suptitle('All 24 curve fits | local PCA-plane views',fontsize=21,x=.04,ha='left',y=.99)
fig.text(.04,.015,'Blue line: source chain; blue dots: 32 encoder samples; orange: fitted curve. Axes use canonical units; RMS is the original fitter statistic.',fontsize=11)
fig.tight_layout(rect=(.015,.04,.99,.955)); fig.savefig(OUT/'curve_fit_gallery.png',dpi=160); plt.close(fig)
(OUT/'curve_fit_metrics.json').write_text(json.dumps(rows,indent=2))
shutil.copy2(pack/'curve_fits.json',OUT/'curve_fits.json')

if not predpath.exists():
    print('Curve figures complete; prediction not available yet.',flush=True)
    raise SystemExit(0)
pred=trimesh.load(predpath,force='mesh')
bounds=np.array([np.minimum(src.bounds[0],pred.bounds[0]),np.maximum(src.bounds[1],pred.bounds[1])])
fig=plt.figure(figsize=(13,11))
for row,(elev,azim) in enumerate([(28,-58),(90,-90)]):
    for col,m in enumerate([src,pred]):
        ax=fig.add_subplot(2,2,row*2+col+1,projection='3d'); meshplot(ax,m); frame(ax,bounds,elev,azim)
        if row==0: ax.set_title('Original STL' if col==0 else 'P1 predicted CAD',fontsize=19,pad=0)
fig.suptitle('Tire STL to CAD | P1 last checkpoint-39980',fontsize=21,x=.045,ha='left',y=.98)
fig.text(.045,.018,'Identical camera, scale and world coordinates in each pair. No post-fit alignment or geometry correction.',fontsize=11)
fig.subplots_adjust(left=0,right=1,bottom=.04,top=.92,hspace=-.06,wspace=-.05)
fig.savefig(OUT/'mesh_vs_p1_cad.png',dpi=170); plt.close(fig)
a,_=trimesh.sample.sample_surface(src,30000,seed=42)
b,_=trimesh.sample.sample_surface(pred,30000,seed=43)
da=cKDTree(b).query(a)[0]; db=cKDTree(a).query(b)[0]
diag=tf['source_diagonal']
metrics={'n_surface_samples_per_mesh':30000,'source_diagonal':diag,'coordinate_protocol':'original STL coordinates, no alignment','distance_definition':'symmetric sampled-surface nearest-neighbor distance (unsquared)','chamfer_mean_percent_diagonal':float(100*(da.mean()+db.mean())/2/diag),'hausdorff95_percent_diagonal':float(100*np.percentile(np.r_[da,db],95)/diag),'source_bbox':src.bounds.tolist(),'prediction_bbox':pred.bounds.tolist(),'source_extents':src.extents.tolist(),'prediction_extents':pred.extents.tolist(),'source_watertight':bool(src.is_watertight),'prediction_mesh_watertight':bool(pred.is_watertight),'source_volume':float(abs(src.volume)),'prediction_volume':float(abs(pred.volume)),'curve_count':len(rows),'curve_type_counts':{k:sum(r['type']==k for r in rows) for k in ['LINE','CIRCLE','ELLIPSE']},'curve_fitter_rms_median_percent_diagonal':float(np.median([r['fit_rms_percent_source_diagonal'] for r in rows])),'curve_fitter_rms_max_percent_diagonal':float(max(r['fit_rms_percent_source_diagonal'] for r in rows))}
(OUT/'geometry_metrics.json').write_text(json.dumps(metrics,indent=2))
for name,dest in [('pred.step','tire_p1.step'),('pred.stl','tire_p1_preview.stl'),('pred.dsl','tire_p1.dsl')]: shutil.copy2(predpath.parent/name,OUT/dest)
shutil.copy2(ROOT/'source.stl',OUT/'tire_input.stl')
shutil.copy2(ROOT/'predictions/D/PART_006/row.json',OUT/'inference_record.json')
print(json.dumps(metrics,indent=2),flush=True)

