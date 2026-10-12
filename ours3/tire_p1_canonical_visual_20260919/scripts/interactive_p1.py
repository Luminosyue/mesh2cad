from pathlib import Path
import json
import numpy as np
import trimesh
import plotly.graph_objects as go
from plotly.subplots import make_subplots
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/tire_p1_canonical_visual_20260919')
out=ROOT/'deliverables'
tf=json.loads((ROOT/'packs/PART_006/coordinate_transform.json').read_text())
curves=json.loads((out/'curve_fits.json').read_text())
src=trimesh.load(out/'tire_input.stl',force='mesh')
pred=trimesh.load(out/'tire_p1_preview.stl',force='mesh')
fig=make_subplots(rows=1,cols=2,specs=[[{'type':'scene'},{'type':'scene'}]],subplot_titles=['Input STL and fitted curves','P1 predicted CAD: original coordinates'])
def mesh(m,name,color,opacity):
    return go.Mesh3d(x=m.vertices[:,0],y=m.vertices[:,1],z=m.vertices[:,2],i=m.faces[:,0],j=m.faces[:,1],k=m.faces[:,2],name=name,color=color,opacity=opacity,showlegend=True,flatshading=True,lighting=dict(ambient=.5,diffuse=.8))
fig.add_trace(mesh(src,'Input STL','#71a6c0',.25),row=1,col=1)
for key,name,color in [('polyline','Mesh curves','#237db0'),('fitted_xyz','Fitted curves','#ef762c')]:
    for i,c in enumerate(curves):
        xyz=(np.array(c[key])-tf['translation'])/tf['scale']
        fig.add_trace(go.Scatter3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],mode='lines',line=dict(color=color,width=5),name=name,legendgroup=key,showlegend=i==0,text=f"Curve {i+1}: {c['type']}",hovertemplate='%{text}<extra></extra>'),row=1,col=1)
fig.add_trace(mesh(pred,'P1 CAD','#71a6c0',1),row=1,col=2)
fig.add_trace(mesh(src,'Input overlay (click to show)','#e98b43',.2),row=1,col=2)
fig.data[-1].visible='legendonly'
bounds=np.array([np.minimum(src.bounds[0],pred.bounds[0]),np.maximum(src.bounds[1],pred.bounds[1])])
scene=dict(aspectmode='cube',camera=dict(eye=dict(x=1.3,y=-1.8,z=1.2)))
for j,k in enumerate(['xaxis','yaxis','zaxis']):
    mid=bounds[:,j].mean(); r=(bounds[1]-bounds[0]).max()*.55
    scene[k]=dict(range=[mid-r,mid+r],title=k[0],backgroundcolor='#f3f6fa',gridcolor='#dce2ea')
fig.update_layout(title='Tire STL to P1 CAD | checkpoint-39980',scene=scene,scene2=scene,height=750,margin=dict(l=10,r=10,b=20,t=80),paper_bgcolor='#f4f7fb',font=dict(family='Arial',color='#21374e'),legend=dict(orientation='h',y=-.04))
html=fig.to_html(full_html=False,include_plotlyjs=True)
prefix='''<!DOCTYPE html><html lang="zh-CN"><meta charset="UTF-8"><title>P1 轮胎 CAD 与曲线拟合</title><style>body{margin:24px;background:#f4f7fb;color:#21374e;font:16px Arial;line-height:1.7}h1{font-size:26px}p{max-width:1150px}</style><h1>P1 轮胎重建与曲线拟合</h1><p>拖动旋转，滚轮缩放，点击图例显示或隐藏曲线、网格及叠加层。两视图使用相同坐标范围；相机可独立操作。蓝色为输入曲线，橙色为拟合曲线。24 条局部锐边链并未组成完整闭合轮廓。</p><p>流程：STL → 8192 个表面点及法向 → 30° 锐边提取 → 24 条链、每条 32 点 → C2 编码 → P1 → DSL → STEP。C2 编码的是重采样网格曲线；解析拟合用于诊断展示，没有替换模型输入。</p><p>正式 checkpoint-8000 生成至 4096 token 上限后程序截断，导出失败。本页展示末步 checkpoint-39980 的实际输出：STEP 有效，但形状和尺寸偏差明显，平均双向表面距离为输入对角线的 15.56%。</p>'''
(out/'interactive_viewer.html').write_text(prefix+html+'</html>',encoding='utf-8')
print('Wrote standalone interactive viewer')
