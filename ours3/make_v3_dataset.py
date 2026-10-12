import json
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
V1 = ROOT / 'ours3/p3_xpart_20case_compact_ir_v1'
EXP = ROOT / 'ours3/p3_xpart_20case_compact_ir_v3'
OUT = EXP / 'training20'
SURF = OUT / 'surface_points'
OUT.mkdir(parents=True, exist_ok=True)
SURF.mkdir(parents=True, exist_ok=True)
manifest = json.loads((V1 / 'CASE_MANIFEST.json').read_text())['cases']
rows = []
for c in manifest:
    cid = c['CASE_ID']
    mesh = trimesh.load_mesh(c['MESH_PATH'], process=False)
    if hasattr(mesh, 'geometry') and not hasattr(mesh, 'vertices'):
        mesh = trimesh.util.concatenate(list(mesh.geometry.values()))
    try:
        pts = mesh.sample(2048, seed=42)
    except TypeError:
        np.random.seed(42)
        pts = mesh.sample(2048)
    pts = np.asarray(pts, dtype=np.float32)
    if pts.shape[1] == 3:
        pts = np.concatenate([pts, np.zeros_like(pts)], axis=1)
    point_path = SURF / f'{cid}_surface_points.npy'
    np.save(point_path, pts)
    target = (EXP / 'compact_ir_v3' / f'{cid}.v3').read_text().strip()
    rows.append({'id': cid, 'dataset': 'p3_xpart_20case_v3',
                 'point_clouds': [str(point_path)],
                 'conversations': [
                     {'from': 'human', 'value': '<point_cloud>\nGenerate a CAD construction program from the point cloud.\nOutput only valid Compact IR V3 assignments ending with END.\n'},
                     {'from': 'gpt', 'value': target}]})
(OUT / 'train.json').write_text(json.dumps(rows, indent=2))
(OUT / 'val.json').write_text(json.dumps(rows, indent=2))
(OUT / 'dataset_info.json').write_text(json.dumps({'p3_xpart_20case_v3': {
    'file_name': 'train.json', 'formatting': 'sharegpt',
    'columns': {'messages': 'conversations', 'images': 'images', 'point_clouds': 'point_clouds'}}}, indent=2))
(OUT / 'p3_train_v3.yaml').write_text((V1 / 'p3_train.yaml').read_text().replace(str(V1 / 'dataset'), str(OUT)).replace('cutoff_len: 32768', 'cutoff_len: 16384'))
print(json.dumps({'samples': len(rows), 'points_per_sample': 2048, 'max_target_chars': max(len(x['conversations'][1]['value']) for x in rows)}))
