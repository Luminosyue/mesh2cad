import json
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import plotly.graph_objects as go
import plotly.express as px

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
SRC=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=ROOT/'visualizations'
PALETTE=px.colors.qualitative.Set3+px.colors.qualitative.Dark24

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=m.to_mesh()
    m.merge_vertices(); m.remove_unreferenced_vertices(); return m

def prep(m,max_faces):
    f=np.asarray(m.faces)
    if len(f)>max_faces: f=f[np.linspace(0,len(f)-1,max_faces).astype(int)]
    ids=np.unique(f); rem=-np.ones(len(m.vertices),dtype=int); rem[ids]=np.arange(len(ids))
    return np.asarray(m.vertices)[ids],rem[f]

def trace(name,m,color,opacity,max_faces):
    v,f=prep(m,max_faces)
    return go.Mesh3d(x=v[:,0],y=v[:,1],z=v[:,2],i=f[:,0],j=f[:,1],k=f[:,2],
        name=name,color=color,opacity=opacity,flatshading=True,
        lighting=dict(ambient=.42,diffuse=.78,specular=.28,roughness=.58),
        lightposition=dict(x=-400,y=-500,z=800),hovertemplate=name+'<extra></extra>')

def project(v,R): return np.asarray(v)@R

def static_case(case,source,rows):
    cam=np.array([2.4,-3.0,2.0]); cam/=np.linalg.norm(cam)
    right=np.cross([0,0,1],cam); right/=np.linalg.norm(right)
    up=np.cross(cam,right); R=np.stack([right,up,cam],axis=1)
    allmesh=[source]+[m for _,m in rows]
    lo=np.min([m.bounds[0] for m in allmesh],axis=0); hi=np.max([m.bounds[1] for m in allmesh],axis=0)
    # camera scale
    xy=np.concatenate([project(m.vertices,R)[:,:2] for m in allmesh]); mn=xy.min(0); mx=xy.max(0); pad=max(mx-mn)*.05
    fig,ax=plt.subplots(figsize=(11,8),facecolor='#f4f7fb')
    def add(m, color, alpha, maxfaces):
        v,f=prep(m,maxfaces); q=project(v,R); tri=q[f][:,:,:2]; z=project(v,R)[f][:,:,2].mean(1); order=np.argsort(z)
        if color=='gray': fc=np.column_stack([np.full(len(f),.55),np.full(len(f),.62),np.full(len(f),.68),np.full(len(f),alpha)])
        else:
            rgb=np.array(plt.matplotlib.colors.to_rgb(color)); n=np.abs((tri[:,1,0]-tri[:,0,0])*(tri[:,2,1]-tri[:,0,1])-(tri[:,1,1]-tri[:,0,1])*(tri[:,2,0]-tri[:,0,0])); n=(n/(n.max()+1e-12))*.42+.58
            fc=np.column_stack([np.clip(n[:,None]*rgb,0,1),np.full(len(f),alpha)])
        ax.add_collection(PolyCollection(tri[order],facecolors=fc[order],edgecolors='none',antialiased=False))
    add(source,'gray',.26,16000)
    for i,(pid,m) in enumerate(rows): add(m,plt.cm.tab20((i%20)/19),.88,2600)
    ax.set_xlim(mn[0]-pad,mx[0]+pad); ax.set_ylim(mn[1]-pad,mx[1]+pad); ax.set_aspect('equal'); ax.set_axis_off(); ax.set_facecolor('#f4f7fb')
    ax.set_title(f'{case.capitalize()} · X-Part CAD assembly · {len(rows)}/{len(rows)} parts + complete body',fontsize=19,fontweight='bold')
    fig.text(.5,.025,'Gray translucent = original complete case mesh; colored = reconstructed X-Part CAD components.',ha='center',fontsize=10)
    p=OUT/f'{case}_xpart_assembly.png'; fig.savefig(p,dpi=220,bbox_inches='tight'); plt.close(fig); return p

def html_case(case,source,rows):
    fig=go.Figure()
    fig.add_trace(trace(f'Complete original {case} body',source,'#8996a3',.22,18000))
    for i,(pid,m) in enumerate(rows): fig.add_trace(trace(pid,m,PALETTE[i%len(PALETTE)],.86,2400))
    n=1+len(rows); allv=[True]*n; cadv=[False]+[True]*len(rows); srcv=[True]+[False]*len(rows)
    fig.update_layout(template='plotly_dark',paper_bgcolor='#111b2c',plot_bgcolor='#111b2c',
      margin=dict(l=10,r=10,t=80,b=20),height=820,
      title=dict(text=f'{case.capitalize()} · X-Part CAD assembly · {len(rows)} parts + complete body',x=.5),
      scene=dict(aspectmode='data',xaxis_title='X',yaxis_title='Y',zaxis_title='Z',
                 camera=dict(eye=dict(x=1.55,y=-1.75,z=1.1),up=dict(x=0,y=0,z=1))),
      showlegend=False,updatemenus=[dict(type='buttons',direction='right',x=.02,y=1.06,buttons=[
        dict(label='CAD + body',method='update',args=[{'visible':allv},{'opacity':[.22]+[.86]*len(rows)}]),
        dict(label='CAD only',method='update',args=[{'visible':cadv},{'opacity':[.22]+[.86]*len(rows)}]),
        dict(label='Original body',method='update',args=[{'visible':srcv},{'opacity':[.55]+[.86]*len(rows)}])])])
    p=OUT/f'{case}_xpart_assembly.html'
    p.write_text(fig.to_html(full_html=True,include_plotlyjs=True,config={'responsive':True,'displaylogo':False,'scrollZoom':True,'toImageButtonOptions':{'filename':f'{case}_xpart_assembly','scale':2}}),encoding='utf-8')
    return p

def main():
    result={}
    for case in ('airplane','tank'):
        source=load(next((SRC/case/'source').glob('*')))
        rows=[]
        for p in sorted((ROOT/'cases'/case).glob('*/metrics.json')):
            d=json.loads(p.read_text())
            if '/xpart_parts/' in d.get('source_path',''):
                rows.append((d['part_id'],load(p.parent/'reconstructed.stl')))
        png=static_case(case,source,rows); html=html_case(case,source,rows)
        result[case]={'xpart_parts':len(rows),'png':str(png),'html':str(html)}
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()




