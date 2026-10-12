import importlib.util,json
from pathlib import Path
import numpy as np,trimesh
from scipy.spatial import cKDTree
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V1=ROOT/'case09_aircraft_end2end_cad_v1';OUT=ROOT/'case09_futurecad_grounded_repair_v3';SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
s=importlib.util.spec_from_file_location('v',V1/'scripts/end2end_pipeline.py');V=importlib.util.module_from_spec(s);s.loader.exec_module(V)
source=trimesh.load(SOURCE,force='mesh',process=False);labels=np.load(OUT/'00_frozen_v2/p3_triangle_part_id.npy');graph=json.loads((OUT/'00_frozen_v2/cad_part_graph.json').read_text());seg={x:{n['part_id'] for n in graph['nodes'] if x in n.get('segments',n.get('source_segment_ids',[]))} for x in range(10)}
shape=V.read_step(OUT/'06_assembly/CASE09_futurecad_grounded_repair_v3.step')[2];diag=float(np.linalg.norm(source.extents));edges,rec=V.true_edges(shape,diag);cad=np.vstack([x['points'][::max(1,len(x['points'])//20)] for x in rec]);tree=cKDTree(cad);rows=[]
for (a,b),ang in zip(source.face_adjacency,source.face_adjacency_angles):
 if ang<=np.radians(30):continue
 point=source.triangles_center[[a,b]].mean(0);la,lb=int(labels[a]),int(labels[b]);owners=sorted(seg[la]|seg[lb]);d=float(tree.query(point)[0]/diag);rows.append({'point':point.tolist(),'segment_labels':[la,lb],'part_ids':owners,'distance':d,'recovered':d<=.02})
summary={}
for p in [f'CADPART_{i:03d}' for i in range(8)]:
 r=[x for x in rows if p in x['part_ids']];summary[p]={'count':len(r),'recovered':sum(x['recovered'] for x in r),'recall':sum(x['recovered'] for x in r)/len(r) if r else None,'missed':sorted([x for x in r if not x['recovered']],key=lambda x:-x['distance'])[:20]}
(OUT/'metrics/sharp_edge_residual_by_part.json').write_text(json.dumps({'threshold':.02,'overall':sum(x['recovered'] for x in rows)/len(rows),'parts':summary},indent=2)+'\n');print(json.dumps(summary,indent=2))
