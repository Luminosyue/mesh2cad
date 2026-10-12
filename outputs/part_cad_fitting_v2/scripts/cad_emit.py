import numpy as np
from metric_runtime import plane

def score(m):return 10*m['normalized_chamfer']+(1-m['iou'])+2*m['centroid_l2_error']+m['bbox_error']

def emit_profiles(spec):
 B=np.asarray(spec['basis']);origin=np.asarray(spec['center'])+B[:,2]*spec['zmin'];h=spec['zmax']-spec['zmin'];ps=spec['profiles']
 if h<1e-6 or len(ps)>7 or sum(len(p['holes']) for p in ps)+len(ps)-1>6:raise ValueError('invalid depth or Boolean budget')
 if sum(len(p['outer'])+sum(map(len,p['holes'])) for p in ps)>96:raise ValueError('profile complexity budget')
 lines=['import cadquery as cq','plane = '+plane(origin,B)]
 for j,p in enumerate(ps):
  lines.append(f'p{j} = cq.Workplane(plane).polyline({p["outer"]!r}).close().extrude({h!r})')
  for k,hole in enumerate(p['holes']):
   lines.extend([f'h{j}_{k} = cq.Workplane(plane).polyline({hole!r}).close().extrude({h!r})',f'p{j} = p{j}.cut(h{j}_{k})'])
 lines.append('result = p0'+''.join(f'.union(p{j})' for j in range(1,len(ps))));return '\n'.join(lines)+'\n'

def emit_loft(spec):
 tracks=spec['outer_tracks'];holes=spec['hole_tracks']
 if holes or len(tracks)>1:raise ValueError('compact loft supports one outer track; no dropped holes')
 track=tracks[0]
 if sum(len(x) for x in track)>96:raise ValueError('loft sketch budget')
 B=np.asarray(spec['basis']);c=np.asarray(spec['center']);lines=['import cadquery as cq'];expr=None
 for i,pts in enumerate(track):
  q=(np.asarray(pts)-c)@B;z=float(q[:,2].mean());p=q[:,:2].tolist()
  if i==0:lines.append('plane = '+plane(c+B[:,2]*z,B));expr=f'cq.Workplane(plane).polyline({p!r}).close()';zprev=z
  else:expr+=f'.workplane(offset={z-zprev!r}).polyline({p!r}).close()';zprev=z
 lines.append('result = '+expr+'.loft(ruled=True)');return '\n'.join(lines)+'\n'