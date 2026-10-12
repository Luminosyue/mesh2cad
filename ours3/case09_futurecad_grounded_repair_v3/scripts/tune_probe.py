#!/usr/bin/env python3
import importlib.util, json, math
from pathlib import Path
import numpy as np
import trimesh

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'case09_futurecad_grounded_repair_v3';V1=ROOT/'case09_aircraft_end2end_cad_v1'
s=importlib.util.spec_from_file_location('m',OUT/'scripts/measure_probe.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(m.V.clean(x),indent=2)+'\n')

right=trimesh.load(V1/'02_cad_part_graph/CADPART_002/source_part.obj',force='mesh',process=False);results=[]
for ns,npf in [(20,14),(20,16),(20,18),(24,14),(24,16),(24,18),(28,14),(28,16),(32,14)]:
 try:
  rows,corr=m.exact_sections(right,'X',ns,npf);shape=m.make_shape(rows,'X');path=OUT/'02_measurements/CADPART_002/tuning'/f'N{ns}_P{npf}.step';q,_=m.candidate_metrics(right,shape,path);results.append({'section_count':ns,'profile_count':npf,'metrics':q,'sections':rows,'correspondence':corr,'step':str(path)});print('RIGHT',ns,npf,q,flush=True)
 except Exception as e:print('RIGHT_FAIL',ns,npf,type(e).__name__,e,flush=True)
dump(OUT/'02_measurements/CADPART_002/tuning/grid.json',results)

p3=V1/'01_part_discovery/p3';blade0=trimesh.load(p3/'part_001.obj',force='mesh',process=False);blade1=trimesh.load(p3/'part_003.obj',force='mesh',process=False);source=trimesh.util.concatenate([blade0,blade1]);centers=[np.asarray(blade0.centroid),np.asarray(blade1.centroid)];center=(centers[0]+centers[1])/2;v0=centers[0]-center;v1=centers[1]-center;v0[1]=0;v1[1]=0;angle=float(math.atan2(np.cross(v0,v1)[1],np.dot(v0,v1)));angle=angle if abs(angle)>1 else math.pi
prop=[]
for idx,blade in enumerate([blade0,blade1]):
 for ns,npf in [(7,12),(9,14),(11,16),(13,18)]:
  try:
   rows,corr=m.exact_sections(blade,'Y',ns,npf);master=m.make_shape(rows,'Y','MASTER_BLADE_LOFT');other=m.transform_shape(master,center,[0,1,0],angle if idx==0 else -angle);shape=m.compound([master,other]);path=OUT/'02_measurements/CADPART_006/tuning'/f'B{idx}_N{ns}_P{npf}.step';q,_=m.candidate_metrics(source,shape,path);prop.append({'master':idx,'section_count':ns,'profile_count':npf,'metrics':q,'sections':rows,'correspondence':corr,'step':str(path),'center':center.tolist(),'angle':angle});print('PROP',idx,ns,npf,q,flush=True)
  except Exception as e:print('PROP_FAIL',idx,ns,npf,type(e).__name__,e,flush=True)
dump(OUT/'02_measurements/CADPART_006/tuning/grid.json',prop)
