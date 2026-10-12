import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys,json,hashlib,tarfile,platform
from pathlib import Path
import numpy as np,trimesh,cadquery,OCP,scipy
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');D=O/'mesh2cad_reconstruction_diagnosis_v1';I=O/'mesh2cad_reconstruction_improvement_v1';R=O/'mesh2cad_resmoke100_v2'
sys.path.insert(0,str(I/'scripts'))
from v1_runtime import evaluate
from execute_v2 import run
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[json.loads(p.read_text()) for p in sorted((R/'cases').glob('*/manifest.json'))]
# Representative replay selection is diagnostic only, never a generation rule.
chosen=[]
for kind in ['planar_region_assembly','compact_section_loft','normal_axis_extrusion']:
 candidates=[r for r in rows if r.get('best_kind')==kind]
 if candidates:chosen.append(candidates[0])
checks=[]
for r in chosen:
 p=R/'cases'/r['case_id'];out=R/'integrity'/('replay_'+r['case_id'])
 ex=run(p/'cad/cad.py',out)
 if not ex.get('tessellation_pass'):raise RuntimeError('Independent program replay failed')
 src=trimesh.load(p/'normalized/normalized_mesh.ply',force='mesh',process=True)
 cad=trimesh.load(out/'cad_mesh_from_reloaded_step.ply',force='mesh',process=True)
 m=evaluate(src,cad,20261006+int(r['case_id'].split('_')[1])*10)
 delta={k:abs(m[k]-r['metrics'][k]) for k in ['normalized_chamfer','iou','centroid_l2_error','bbox_error']}
 checks.append({'case_id':r['case_id'],'kind':r['best_kind'],'metric_differences':delta,'pass':max(delta.values())<1e-9})
if not all(c['pass'] for c in checks):raise RuntimeError('Metric replay differs')
versions={'python':sys.version,'cadquery':cadquery.__version__,'OCP':OCP.__version__,'trimesh':trimesh.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'seed':20261006,'git_commit':None,'code_identity':'SHA256 inventory; standalone output artifacts'}
(R/'reports/software_versions.json').write_text(json.dumps(versions,indent=2))
(R/'reports/independent_replay_checks.json').write_text(json.dumps(checks,indent=2))
status=json.loads((R/'reports/status.json').read_text())
assert status['factory_gate']=='PASS' and len(rows)==100
for root in [D,I,R]:
 files={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file() and p.name!='DELIVERY_SHA256.json'}
 (root/'integrity/DELIVERY_SHA256.json').write_text(json.dumps(files,indent=2))
archive=O/'MESH2CAD_RECONSTRUCTION_V2_DELIVERY.tar.gz'
with tarfile.open(archive,'x:gz') as t:
 for root in [D,I,R]:t.add(root,arcname=root.name)
digest=sha(archive)
archive.with_suffix('.gz.sha256').write_text(digest+'  '+archive.name+'\n')
print(json.dumps({'archive':str(archive),'sha256':digest,'bytes':archive.stat().st_size,'replay_checks':checks}))
