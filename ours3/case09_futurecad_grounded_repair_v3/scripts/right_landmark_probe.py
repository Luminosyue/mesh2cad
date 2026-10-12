import importlib.util,json
from pathlib import Path
import numpy as np,trimesh
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V1=ROOT/'case09_aircraft_end2end_cad_v1';OUT=ROOT/'case09_futurecad_grounded_repair_v3';SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
s=importlib.util.spec_from_file_location('m',OUT/'scripts/measure_probe.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);V=m.V
grid=json.loads((OUT/'02_measurements/CADPART_002/sharp_tuning/grid.json').read_text());base=next(x for x in grid if x['profile_count']==20);right=trimesh.load(V1/'02_cad_part_graph/CADPART_002/source_part.obj',force='mesh',process=False);source=trimesh.load(SOURCE,force='mesh',process=False);labels=np.load(OUT/'00_frozen_v2/p3_triangle_part_id.npy');boundary,sharp=V.source_feature_points(source,labels);diag=float(np.linalg.norm(source.extents));shapes=[]
for i in range(8):
 p=f'CADPART_{i:03d}'
 if p=='CADPART_002':shapes.append(None)
 elif p in ['CADPART_001','CADPART_006']:shapes.append(V.read_step(OUT/'03_mac_repair'/p/'selected.step')[2])
 else:shapes.append(V.read_step(OUT/'00_frozen_v2'/p/'final.step')[2])
patterns=[[0,3,6,9,12,15],[1,4,7,10,13,16],[2,5,8,11,14,17],[0,1,8,9,10,19],[3,4,5,13,14,15]];results=[]
for k,ins in enumerate(patterns):
 rows=[]
 for r in base['sections']:
  p=np.asarray(r['profile']);out=[]
  for i,x in enumerate(p):
   out.append(x)
   if i in ins:out.append((x+p[(i+1)%len(p)])/2)
  rows.append({'coordinate':r['coordinate'],'sample_count':'GROUNDED_LANDMARK_INSERTION','profile':np.asarray(out).tolist()})
 try:
  shape=m.make_shape(rows,'X');path=OUT/'02_measurements/CADPART_002/landmark_tuning'/f'pattern_{k}.step';part,_=m.candidate_metrics(right,shape,path);ss=list(shapes);ss[2]=shape;whole=V.compound(ss);e,rec=V.true_edges(whole,diag);row={'pattern':k,'insert_after':ins,'part_metrics':part,'whole_sharp':V.recall(sharp,rec,diag),'whole_feature':V.recall(boundary,rec,diag),'whole_faces':V.topology_count(whole,TopAbs_FACE),'whole_edges':V.topology_count(whole,TopAbs_EDGE),'sections':rows,'step':str(path)};results.append(row);print(k,part['Q'],part['CHAMFER'],part['P95'],row['whole_sharp'],row['whole_feature'],flush=True)
 except Exception as e:print('FAIL',k,e)
(OUT/'02_measurements/CADPART_002/landmark_tuning/grid.json').write_text(json.dumps(V.clean(results),indent=2)+'\n')
