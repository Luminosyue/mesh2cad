import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
SRC=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=ROOT/'visualizations'

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=m.to_mesh()
    m.merge_vertices();m.remove_unreferenced_vertices();return m

camera=np.array([2.4,-3.0,2.0]); camera/=np.linalg.norm(camera)
right=np.cross([0,0,1],camera); right/=np.linalg.norm(right)
up=np.cross(camera,right); R=np.stack([right,up,camera],axis=1)
colors=plt.cm.tab20(np.linspace(0,1,20))

def prep(m,max_faces=5000):
    if len(m.faces)>max_faces:
        ids=np.linspace(0,len(m.faces)-1,max_faces).astype(int)
        faces=m.faces[ids]
    else: faces=m.faces
    ids=np.unique(faces); rem=-np.ones(len(m.vertices),dtype=int); rem[ids]=np.arange(len(ids))
    return m.vertices[ids],rem[faces],m.face_normals[np.linspace(0,len(m.face_normals)-1,len(faces)).astype(int)]

def draw(ax,items,source=None,colors_on=True,labels=False):
    polys=[];depth=[];facecols=[];allxy=[]
    if source is not None:
        v,f,n=prep(source,16000); xyz=v@R; tri=xyz[f]
        polys.append(tri[:,:,:2]); depth.append(tri[:,:,2].mean(axis=1))
        light=np.array([.2,-.5,.85]); light/=np.linalg.norm(light)
        shade=.28+.30*np.abs(n@light)
        facecols.append(np.column_stack([shade,shade,shade, np.full(len(f),.20)]))
        allxy.append(xyz[:,:2])
    for idx,(pid,m) in enumerate(items):
        v,f,n=prep(m,4200); xyz=v@R; tri=xyz[f]
        polys.append(tri[:,:,:2]); depth.append(tri[:,:,2].mean(axis=1))
        base=colors[idx%20][:3] if colors_on else np.array([.16,.48,.68])
        light=np.array([.2,-.5,.85]); light/=np.linalg.norm(light)
        shade=.46+.54*np.abs(n@light)
        fc=np.clip(shade[:,None]*base[None,:],0,1)
        facecols.append(np.column_stack([fc,np.full(len(f),.88)]))
        allxy.append(xyz[:,:2])
    if not polys: raise RuntimeError('no polygons; items='+str(len(items)))
    polys=np.concatenate(polys); depth=np.concatenate(depth); facecols=np.concatenate(facecols)
    order=np.argsort(depth)
    ax.add_collection(PolyCollection(polys[order],facecolors=facecols[order],edgecolors='none',antialiased=False))
    xy=np.concatenate(allxy); lo=xy.min(axis=0); hi=xy.max(axis=0); pad=max(hi-lo)*.05
    ax.set_xlim(lo[0]-pad,hi[0]+pad);ax.set_ylim(lo[1]-pad,hi[1]+pad);ax.set_aspect('equal');ax.set_axis_off();ax.set_facecolor('#f4f7fb')
    if labels:
        for i,(pid,m) in enumerate(items):
            xyz=m.vertices@R; c=xyz[:,:2].mean(axis=0)
            ax.annotate(pid.replace('PART_','P'),c,xytext=(3,4),textcoords='offset points',fontsize=5,
                        bbox=dict(boxstyle='round,pad=.15',fc='white',ec='#adb8c5',alpha=.8))

def main():
    rows=[]
    for p in sorted((ROOT/'cases'/'tank').glob('*/metrics.json')):
        d=json.loads(p.read_text())
        if '/xpart_parts/' in d.get('source_path',''):
            rows.append((d['part_id'],load(p.parent/'reconstructed.stl')))
    source=load(next((SRC/'tank'/'source').glob('*'))); print('ROWS',len(rows), 'SRCF',len(source.faces), flush=True)
    fig,axes=plt.subplots(1,3,figsize=(18,6),facecolor='#f4f7fb')
    draw(axes[0],rows,source=None,colors_on=False)
    axes[0].set_title('45-part X-Part CAD assembly',fontsize=16,fontweight='bold')
    draw(axes[1],rows,source=source,colors_on=False)
    axes[1].set_title('45-part CAD + complete tank body',fontsize=16,fontweight='bold')
    draw(axes[2],rows,source=source,colors_on=True,labels=False)
    axes[2].set_title('45-part component colors + tank body',fontsize=16,fontweight='bold')
    fig.suptitle('Tank | X-Part complete assembly (45 / 45 CAD components)',fontsize=22,fontweight='bold')
    fig.text(.5,.025,'Gray translucent surface = original complete tank body; colored/blue surfaces = reconstructed X-Part CAD. All 45 X-Part parts are included.',ha='center',fontsize=11)
    fig.subplots_adjust(left=.015,right=.985,top=.85,bottom=.08,wspace=.04)
    out=OUT/'tank_xpart_45_assembled_shaded.png'; fig.savefig(out,dpi=220); plt.close(fig)
    print(out)
if __name__=='__main__': main()




