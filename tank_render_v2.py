import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json, zipfile
from collections import Counter
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results')
OUT=ROOT/'visualization/tank_edges_v2'
(OUT/'parts').mkdir(parents=True,exist_ok=True)
BG='#f4f7fb'
camera=np.array([2.4,-3.0,2.0]); camera/=np.linalg.norm(camera)
right=np.cross([0,0,1],camera); right/=np.linalg.norm(right)
up=np.cross(camera,right)
R=np.stack([right,up,camera],axis=1)
parts=[]; stats=[]
for p in sorted((ROOT/'samples/tank/xpart_parts').glob('PART_*')):
    m=trimesh.load(p/'cad_rebuilt.stl',force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=trimesh.util.concatenate(tuple(m.geometry.values()))
    m.merge_vertices()
    m.remove_unreferenced_vertices()
    v=np.array(m.vertices).copy(); f=np.array(m.faces).copy()
    edge=np.array(m.face_adjacency_edges)[m.face_adjacency_angles>np.deg2rad(25)]
    counts=np.bincount(m.edges_unique_inverse,minlength=len(m.edges_unique))
    boundary=np.array(m.edges_unique)[counts==1]
    n=np.array(m.face_normals)
    light=np.array([.2,-.5,.85]); light/=np.linalg.norm(light)
    shade=.48+.52*np.abs(n@light)
    parts.append(dict(id=p.name,v=v,f=f,e=edge,b=boundary,shade=shade))
    stats.append(dict(part=p.name,faces=len(f),sharp_edges=len(edge),boundary_edges=len(boundary)))
    print('loaded',p.name,flush=True)
(OUT/'geometry_types.json').write_text(json.dumps(stats,indent=2))

def draw(ax,items,mode='surface',labels=False,frame=True):
    polys=[]; depths=[]; colors=[]; lines=[]; bounds=[]; centers=[]
    for idx,(p,offset) in enumerate(items):
        xyz=(p['v']+offset)@R
        tri=xyz[p['f']]
        polys.append(tri[:,:,:2]); depths.append(tri[:,:,2].mean(axis=1))
        base=np.array(plt.cm.tab20((int(p['id'][-3:])*7%20)/19)[:3]) if labels else np.array([.31,.65,.80])
        colors.append(np.clip(p['shade'][:,None]*base,0,1))
        bounds.append(xyz[:,:2]); centers.append((p['id'],xyz[:,:2].mean(axis=0)))
        es=p['e'] if mode!='topology' else np.vstack([p['f'][:,[0,1]],p['f'][:,[1,2]],p['f'][:,[2,0]]])
        lines.extend(xyz[es][:,:,:2])
    tri=np.concatenate(polys); z=np.concatenate(depths); cols=np.concatenate(colors); order=np.argsort(z)
    if mode=='topology':
        ax.add_collection(PolyCollection(tri[order],facecolors=cols[order]*.35+.65,edgecolors='#435469',linewidths=.13))
    else:
        ax.add_collection(PolyCollection(tri[order],facecolors=cols[order],edgecolors='none',antialiased=False))
    if mode=='features':
        ax.add_collection(LineCollection(lines,colors='#db442d',linewidths=.48,alpha=.8))
    if labels:
        for name,c in centers:
            ax.annotate(name.replace('PART_','P'),c,xytext=(5,8),textcoords='offset points',fontsize=8,fontweight='bold',bbox=dict(boxstyle='round,pad=.2',fc='white',ec='#bac5d1',alpha=.95))
    xy=np.concatenate(bounds); lo=xy.min(axis=0); hi=xy.max(axis=0); pad=max(hi-lo)*.045
    ax.set_xlim(lo[0]-pad,hi[0]+pad); ax.set_ylim(lo[1]-pad,hi[1]+pad)
    ax.set_aspect('equal'); ax.set_axis_off(); ax.set_facecolor(BG)

zero=np.zeros(3)
for p in parts:
    fig,axes=plt.subplots(1,3,figsize=(13,4.6),facecolor=BG)
    for ax,mode,title in zip(axes,['surface','features','topology'],['Complete CAD surface','Sharp edges (>25 deg), X-ray overlay','All faceted face boundaries']):
        draw(ax,[(p,zero)],mode); ax.set_title(title,fontsize=10)
    fig.suptitle(p['id']+' | STEP geometry',fontsize=17,fontweight='bold')
    fig.text(.5,.025,'Planar facets + straight edges. Red edges include hidden edges (X-ray); no fitted smooth curves.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.02,right=.98,top=.83,bottom=.10,wspace=.08)
    fig.savefig(OUT/'parts'/f"{p['id']}.png",dpi=160); plt.close(fig)

for page in range(3):
    fig,axes=plt.subplots(3,5,figsize=(16,10),facecolor=BG)
    for ax,p in zip(axes.flat,parts[page*15:(page+1)*15]):
        draw(ax,[(p,zero)],'features'); ax.set_title(p['id'],fontsize=11)
    fig.suptitle(f'Tank | surfaces + sharp edges | {page+1}/3',fontsize=20,fontweight='bold')
    fig.text(.5,.018,'All faces rendered. Red: sharp edges (>25 deg), including hidden edges. Each part fitted independently.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.025,right=.975,top=.91,bottom=.065,hspace=.24,wspace=.15)
    fig.savefig(OUT/f'parts_sheet_{page+1}.png',dpi=180); plt.close(fig)

# Rigid translations only: amplify each centroid's displacement from the assembly center.
vs=np.concatenate([p['v'] for p in parts]); center=(vs.min(axis=0)+vs.max(axis=0))/2
exploded=[]
for p in parts:
    c=(p['v'].min(axis=0)+p['v'].max(axis=0))/2
    offset=(c-center)*2.7
    exploded.append((p,offset))
fig,axes=plt.subplots(1,2,figsize=(18,10),facecolor=BG)
draw(axes[0],[(p,zero) for p in parts],labels=False)
draw(axes[1],exploded,labels=True)
axes[0].set_title('Assembled CAD',fontsize=18); axes[1].set_title('Exploded CAD | 45 numbered parts',fontsize=18)
fig.suptitle('Tank | assembly and exploded view',fontsize=24,fontweight='bold')
fig.text(.5,.035,'Exploded display uses rigid translations only. P000 = PART_000. Panels fitted independently.',ha='center',fontsize=12)
fig.subplots_adjust(left=.02,right=.98,top=.9,bottom=.09,wspace=.10)
fig.savefig(OUT/'tank_exploded.png',dpi=200); plt.close(fig)
fig,ax=plt.subplots(figsize=(15,11),facecolor=BG)
draw(ax,exploded,'features',labels=True)
ax.set_title('Tank | exploded surfaces + sharp edges',fontsize=22,fontweight='bold')
fig.text(.5,.025,'Red: sharp edges (>25 deg), X-ray overlay. Surfaces are planar facets; all part numbers retained.',ha='center',fontsize=11)
fig.subplots_adjust(left=.025,right=.975,top=.93,bottom=.065)
fig.savefig(OUT/'tank_exploded_edges.png',dpi=200); plt.close(fig)
(OUT/'README.txt').write_text('Rendered directly from 45 STEP files. All triangles rendered. Red lines are tessellated face adjacency edges with dihedral angle >25 degrees, including hidden edges (X-ray overlay), not recovered analytic curves. Topology panels show all planar face boundaries. Exploded view applies rigid translations only. Original CAD files unchanged.\n')
with zipfile.ZipFile(OUT/'tank_images.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file() and p.suffix!='.zip': z.write(p,p.relative_to(OUT))
print('DONE',OUT,flush=True)

