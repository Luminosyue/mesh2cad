import json, traceback
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'
man=json.loads((EXP/'CASE_MANIFEST.json').read_text())['cases']; d=EXP/'dataset'; d.mkdir(exist_ok=True)
train=[]
for c in man:
    cid=c['CASE_ID']; mesh=trimesh.load_mesh(c['MESH_PATH'],process=False)
    if hasattr(mesh,'geometry') and not hasattr(mesh,'vertices'):
        mesh=trimesh.util.concatenate(list(mesh.geometry.values()))
    # Surface samples are conditioning only; keep them compact and deterministic.
    try: pts=mesh.sample(2048,seed=42)
    except TypeError:
        np.random.seed(42); pts=mesh.sample(2048)
    pts=np.asarray(pts,dtype=np.float32)
    # SpatialLM's CAD point plugin expects xyz plus three auxiliary channels
    # (normals/features).  The X-Part mesh provides geometry only here; zeros
    # preserve the validated xyz conditioning without inventing edge labels.
    if pts.shape[1] == 3: pts=np.concatenate([pts,np.zeros_like(pts)],axis=1)
    np.save(d/f'{cid}_surface_points.npy',pts)
    ir=(EXP/'compact_ir'/f'{cid}.ir').read_text()
    human=(f'<point_cloud>\nGenerate a CAD construction program from the point cloud.\n'
           'Output only valid Compact IR assignments ending with END.\n')
    train.append({'id':cid,'dataset':'p3_xpart_20case','point_clouds':[str(d/f'{cid}_surface_points.npy')],
      'conversations':[{'from':'human','value':human},{'from':'gpt','value':ir}]})
(d/'train.json').write_text(json.dumps(train,indent=2)); (d/'val.json').write_text(json.dumps(train,indent=2))
(d/'dataset_info.json').write_text(json.dumps({'p3_xpart_20case':{'file_name':'train.json','formatting':'sharegpt','columns':{'messages':'conversations','images':'images','point_clouds':'point_clouds'}}},indent=2))
print({'samples':len(train),'points_per_sample':2048})
