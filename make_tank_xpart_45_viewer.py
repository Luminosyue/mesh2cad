from pathlib import Path
import json
import numpy as np
import trimesh
import plotly.graph_objects as go
import plotly.express as px

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
SRC=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=ROOT/'visualizations'

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=m.to_mesh()
    m.merge_vertices();m.remove_unreferenced_vertices();return m

def reduce_mesh(m,max_faces):
    f=np.asarray(m.faces)
    if len(f)>max_faces:
        f=f[np.linspace(0,len(f)-1,max_faces).astype(int)]
    ids=np.unique(f); rem=-np.ones(len(m.vertices),dtype=int); rem[ids]=np.arange(len(ids))
    return np.asarray(m.vertices)[ids],rem[f]

def trace(name,m,color,opacity,max_faces):
    v,f=reduce_mesh(m,max_faces)
    return go.Mesh3d(x=v[:,0],y=v[:,1],z=v[:,2],i=f[:,0],j=f[:,1],k=f[:,2],
        name=name,color=color,opacity=opacity,flatshading=True,
        lighting=dict(ambient=.42,diffuse=.78,specular=.28,roughness=.58),
        lightposition=dict(x=-400,y=-500,z=800),hovertemplate=name+'<extra></extra>')

def main():
    source=load(next((SRC/'tank'/'source').glob('*')))
    fig=go.Figure()
    fig.add_trace(trace('Complete original tank body',source,'#8996a3',0.22,18000))
    rows=[]
    palette=px.colors.qualitative.Set3+px.colors.qualitative.Dark24
    for p in sorted((ROOT/'cases'/'tank').glob('*/metrics.json')):
        d=json.loads(p.read_text())
        if '/xpart_parts/' in d.get('source_path',''):
            rows.append((d['part_id'],load(p.parent/'reconstructed.stl')))
    for idx,(pid,m) in enumerate(rows):
        fig.add_trace(trace(pid,m,palette[idx%len(palette)],0.86,2200))
    cad_n=len(rows); n=1+cad_n
    vis_all=[True]*n; vis_cad=[False]+[True]*cad_n; vis_src=[True]+[False]*cad_n
    fig.update_layout(template='plotly_dark',paper_bgcolor='#111b2c',plot_bgcolor='#111b2c',
      margin=dict(l=10,r=10,t=80,b=20),height=820,
      title=dict(text='Tank · X-Part complete assembly · 45 / 45 CAD parts + body',x=.5),
      scene=dict(aspectmode='data',xaxis_title='X',yaxis_title='Y',zaxis_title='Z',
                 camera=dict(eye=dict(x=1.55,y=-1.75,z=1.1),up=dict(x=0,y=0,z=1))),
      showlegend=False,
      updatemenus=[dict(type='buttons',direction='right',x=.02,y=1.06,
        buttons=[
          dict(label='45 CAD + body',method='update',args=[{'visible':vis_all},{'opacity':[.22]+[.86]*cad_n}]),
          dict(label='45 CAD only',method='update',args=[{'visible':vis_cad},{'opacity':[.22]+[.86]*cad_n}]),
          dict(label='Original body',method='update',args=[{'visible':vis_src},{'opacity':[.55]+[.86]*cad_n}])
        ])])
    html=fig.to_html(full_html=True,include_plotlyjs=True,config={'responsive':True,'displaylogo':False,'scrollZoom':True,'toImageButtonOptions':{'filename':'tank_xpart_45_assembly','scale':2}})
    (OUT/'tank_xpart_45_assembly.html').write_text(html,encoding='utf-8')
    print(OUT/'tank_xpart_45_assembly.html', 'traces',n)
if __name__=='__main__': main()

