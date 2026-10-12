#!/usr/bin/env python3
import importlib.util,json
from pathlib import Path
import trimesh
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'case09_futurecad_grounded_repair_v3';V1=ROOT/'case09_aircraft_end2end_cad_v1'
s=importlib.util.spec_from_file_location('m',OUT/'scripts/measure_probe.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p3=V1/'01_part_discovery/p3';blades=[trimesh.load(p3/f'part_{i:03d}.obj',force='mesh',process=False) for i in [1,3]];source=trimesh.util.concatenate(blades);results=[]
for ns,npf in [(5,10),(7,12),(7,14),(9,12),(9,14),(11,14),(11,16)]:
 try:
  ops=[];shapes=[]
  for blade in blades:
   rows,corr=m.exact_sections(blade,'Y',ns,npf);shapes.append(m.make_shape(rows,'Y','BLADE_LOFT'));ops.append({'sections':rows,'correspondence':corr})
  shape=m.compound(shapes);path=OUT/'02_measurements/CADPART_006/independent_probe'/f'N{ns}_P{npf}.step';q,_=m.candidate_metrics(source,shape,path);results.append({'section_count':ns,'profile_count':npf,'metrics':q,'operations':ops,'step':str(path)});print(ns,npf,q,flush=True)
 except Exception as e:print('FAIL',ns,npf,e,flush=True)
(OUT/'02_measurements/CADPART_006/independent_probe/grid.json').write_text(json.dumps(m.V.clean(results),indent=2)+'\n')
