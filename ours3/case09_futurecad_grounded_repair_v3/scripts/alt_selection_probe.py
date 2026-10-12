#!/usr/bin/env python3
import importlib.util,json
from pathlib import Path
import numpy as np,trimesh
from OCP.BRepCheck import BRepCheck_Analyzer
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V1=ROOT/'case09_aircraft_end2end_cad_v1';V2=ROOT/'case09_all_parts_mac_futurecad_v2';OUT=ROOT/'case09_futurecad_grounded_repair_v3';SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
s=importlib.util.spec_from_file_location('v',V1/'scripts/end2end_pipeline.py');V=importlib.util.module_from_spec(s);s.loader.exec_module(V)
source=trimesh.load(SOURCE,force='mesh',process=False);labels=np.load(OUT/'00_frozen_v2/p3_triangle_part_id.npy');boundary,sharp=V.source_feature_points(source,labels);diag=float(np.linalg.norm(source.extents));results=[]
for left in [0,1]:
 shapes=[]
 for i in range(8):
  p=f'CADPART_{i:03d}'
  if p=='CADPART_001':step=OUT/'03_mac_repair'/p/f'candidate_{left:02d}'/'candidate.step'
  elif p in ['CADPART_002','CADPART_006']:step=OUT/'03_mac_repair'/p/'selected.step'
  else:step=OUT/'00_frozen_v2'/p/'final.step'
  ok,r,x=V.read_step(step);shapes.append(x)
 shape=V.compound(shapes);edges,records=V.true_edges(shape,diag);sre=V.recall(sharp,records,diag);fre=V.recall(boundary,records,diag);v,f,_=V.tessellate(shape);cad=trimesh.Trimesh(vertices=v,faces=f,process=False);m=V.geometry_metrics(source,cad,diag);row={'left_candidate':left,'left_qa':json.loads((OUT/'03_mac_repair/CADPART_001'/f'candidate_{left:02d}'/'qa.json').read_text()),'SHARP_EDGE_RECALL':sre,'FEATURE_BOUNDARY_RECALL':fre,'whole_metrics':m,'whole_Q':V.qclass(m,True),'faces':V.topology_count(shape,__import__('OCP.TopAbs',fromlist=['TopAbs_FACE']).TopAbs_FACE),'edges':V.topology_count(shape,__import__('OCP.TopAbs',fromlist=['TopAbs_EDGE']).TopAbs_EDGE)};results.append(row);print(json.dumps(row,indent=2))
(OUT/'metrics/alternative_selection_probe.json').write_text(json.dumps(results,indent=2)+'\n')
