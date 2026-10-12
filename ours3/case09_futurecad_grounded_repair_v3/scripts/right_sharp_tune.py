import importlib.util,json
from pathlib import Path
import numpy as np,trimesh
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V1=ROOT/'case09_aircraft_end2end_cad_v1';OUT=ROOT/'case09_futurecad_grounded_repair_v3';SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
s=importlib.util.spec_from_file_location('m',OUT/'scripts/measure_probe.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);V=m.V
source=trimesh.load(SOURCE,force='mesh',process=False);right=trimesh.load(V1/'02_cad_part_graph/CADPART_002/source_part.obj',force='mesh',process=False);labels=np.load(OUT/'00_frozen_v2/p3_triangle_part_id.npy');boundary,sharp=V.source_feature_points(source,labels);diag=float(np.linalg.norm(source.extents));base=[]
for i in range(8):
 p=f'CADPART_{i:03d}'
 if p=='CADPART_002':base.append(None)
 elif p in ['CADPART_001','CADPART_006']:base.append(V.read_step(OUT/'03_mac_repair'/p/'selected.step')[2])
 else:base.append(V.read_step(OUT/'00_frozen_v2'/p/'final.step')[2])
results=[]
for npf in [20,22,24,26,28,30]:
 try:
  rows,corr=m.exact_sections(right,'X',20,npf);shape=m.make_shape(rows,'X');path=OUT/'02_measurements/CADPART_002/sharp_tuning'/f'N20_P{npf}.step';part,_=m.candidate_metrics(right,shape,path);shapes=list(base);shapes[2]=shape;whole=V.compound(shapes);edges,rec=V.true_edges(whole,diag);sre=V.recall(sharp,rec,diag);fre=V.recall(boundary,rec,diag);row={'section_count':20,'profile_count':npf,'part_metrics':part,'whole_sharp':sre,'whole_feature':fre,'whole_faces':V.topology_count(whole,TopAbs_FACE),'whole_edges':V.topology_count(whole,TopAbs_EDGE),'sections':rows,'correspondence':corr,'step':str(path)};results.append(row);print('P',npf,'PART',part['Q'],part['CHAMFER'],part['P95'],part['COVERAGE02'],'SHARP',sre,'FEAT',fre,flush=True)
 except Exception as e:print('FAIL',npf,type(e).__name__,e,flush=True)
(OUT/'02_measurements/CADPART_002/sharp_tuning/grid.json').write_text(json.dumps(m.V.clean(results),indent=2)+'\n')
