import importlib.util,json
from pathlib import Path
import trimesh
root=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');out=root/'case09_fullstack_mesh2cad_mac_v6/11_targeted_repair/CADPART_002/parameter_probe';out.mkdir(parents=True,exist_ok=True)
def mod(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=mod('r',root/'case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py');v=mod('v',root/'case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py');q=mod('q',root/'part_to_cad_recovery_fix_v1/scripts/run_recovery.py')
src=root/'case09_fullstack_mesh2cad_mac_v6/02_cad_part_graph/CADPART_002/source_part.obj';mesh=trimesh.load(src,force='mesh',process=False);rows=[]
for ns,npf,tol in [(8,8,.002),(10,10,.002),(12,10,.002),(14,12,.001),(16,14,.0005),(20,16,.0002),(24,20,.0002),(32,24,.0001)]:
 try:
  shape=r.semantic_skin(mesh,'X',ns,npf,tol);step=out/f's{ns}_p{npf}_t{tol}.step';r.build_candidate if False else None;v.write_step(shape,step);qa=q.qa_step(step,src);row={'sections':ns,'profiles':npf,'tolerance':tol,'step':str(step),'qa':qa};print(ns,npf,tol,qa['GEOMETRY_Q'],qa['NORMALIZED_SYMMETRIC_CHAMFER'],qa['P95'],qa['COVERAGE02'],flush=True)
 except Exception as e:row={'sections':ns,'profiles':npf,'tolerance':tol,'error':str(e)}
 rows.append(row)
(out/'probe.json').write_text(json.dumps(rows,indent=2,default=str)+'\n')
