import csv
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OURS3 = ROOT / 'ours3'
EXP = OURS3 / 'full20_object_mesh_to_cad_assembly_v1'
CADRE = OURS3 / 'cadrille_cadrecode_parts21_20260926_v2' / 'cadrecode'
CADRILLE = OURS3 / 'cadrille_full20_20260926' / 'results'
OUT = OURS3 / 'cadrecode_cadrille_metrics_12_20260926'
SAMPLE_N = 20000
SEED = 0
RESOLUTION = 64
CASE_IDS = [
    '2_of_jenga_classic_game', 'android_figure_orange',
    'aroma_stainless_steel_milk_frother_2_cup', 'baby_car', 'birdhouse',
    'cube', 'mini_excavator', 'paintmaker', 'pottery_large', 'robot',
    'speaker_big', 'toaster',
]


def load_mesh(path):
    mesh = trimesh.load(str(path), force='mesh', process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
        raise ValueError(f'empty mesh: {path}')
    return mesh


def mesh_from_steps(paths):
    import cadquery as cq
    verts, faces = [], []
    offset = 0
    readable = 0
    for path in paths:
        try:
            shape = cq.importers.importStep(str(path)).val()
            if not shape.isValid():
                continue
            v, f = shape.tessellate(0.0005, 0.1)
        except Exception:
            continue
        if not v or not f:
            continue
        readable += 1
        verts.extend([x.toTuple() for x in v])
        faces.extend((np.asarray(f, dtype=np.int64) + offset).tolist())
        offset += len(v)
    if not faces:
        raise ValueError('no tessellated successful parts')
    return trimesh.Trimesh(np.asarray(verts, dtype=float), np.asarray(faces, dtype=np.int64), process=False), readable


def prediction(method, case):
    if method == 'CAD-Recode':
        base = CADRE / case
        paths = []
        for status_path in sorted(base.glob('PART_*/STATUS.json')):
            status = json.loads(status_path.read_text())
            if status.get('status') == 'PASS':
                folder = Path(status.get('folder', ''))
                if (folder / 'world.step').is_file():
                    paths.append(folder / 'world.step')
        mesh, readable = mesh_from_steps(paths)
        return mesh, readable, len(list(base.glob('PART_*/STATUS.json')))
    base = CADRILLE / case
    summary = json.loads((base / 'SUMMARY.json').read_text())
    paths = [Path(x['world_step']) for x in summary.get('parts', []) if x.get('status') == 'PASS']
    mesh, readable = mesh_from_steps(paths)
    return mesh, readable, int(summary.get('required_parts', len(paths)))


def sample_surface(mesh, seed):
    import sys
    sys.path.insert(0, str(ROOT / 'scripts'))
    from geometry_pack_v1.surface import sample_surface_uniform
    return sample_surface_uniform(mesh.vertices, mesh.faces, SAMPLE_N, seed)[0]


def surface_iou(a, b):
    bounds = np.vstack([a.bounds, b.bounds])
    pitch = float(np.ptp(bounds, axis=0).max() / RESOLUTION)
    if not math.isfinite(pitch) or pitch <= 0:
        raise ValueError('invalid voxel pitch')
    def occupied(mesh):
        pts = np.rint(mesh.voxelized(pitch).points / pitch).astype(np.int64)
        return set(map(tuple, pts.tolist()))
    sa, sb = occupied(a), occupied(b)
    union = len(sa | sb)
    return len(sa & sb) / union


def metrics(ref, pred):
    pa = sample_surface(ref, SEED)
    pb = sample_surface(pred, SEED + 1)
    da = cKDTree(pb).query(pa, workers=1)[0]
    db = cKDTree(pa).query(pb, workers=1)[0]
    diag = float(np.linalg.norm(ref.extents))
    return {
        'CD': float((da.mean() + db.mean()) * 0.5 / diag),
        'H95': float(np.percentile(np.r_[da, db], 95) / diag),
        'IOU64': float(surface_iou(ref, pred)),
    }


def avg(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (EXP / 'manifests/FULL20_OBJECT_MANIFEST.csv').open(newline='') as f:
        manifest = {r['OBJECT_ID']: r for r in csv.DictReader(f)}
    rows = []
    for case in CASE_IDS:
        ref = load_mesh(Path(manifest[case]['FULL_MESH_PATH']))
        for method in ['CAD-Recode', 'Cadrille']:
            rec = {'case': case, 'method': method}
            try:
                pred, passed, total = prediction(method, case)
                rec.update({'status': 'METRIC_VALID', 'passed_parts': passed, 'required_parts': total, 'coverage': passed / total, **metrics(ref, pred)})
            except Exception as exc:
                rec.update({'status': 'METRIC_FAILED', 'failure': f'{type(exc).__name__}: {exc}'})
            rows.append(rec)
            print(case, method, rec.get('status'), rec.get('CD'), flush=True)
    with (OUT / 'PER_CASE.csv').open('w', newline='') as f:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    summary = {
        'protocol': {'N_selected': 12, 'case_ids': CASE_IDS, 'surface_samples': SAMPLE_N, 'seed': SEED, 'CD': 'symmetric mean nearest-neighbor / full input bbox diagonal', 'H95': '95th percentile bidirectional NN / full input bbox diagonal', 'IOU64': 'world-aligned surface voxel IoU at resolution 64', 'registration': 'NONE'},
        'methods': {},
    }
    for method in ['CAD-Recode', 'Cadrille']:
        valid = [r for r in rows if r['method'] == method and r['status'] == 'METRIC_VALID']
        summary['methods'][method] = {'selected_N': 12, 'metric_valid_N': len(valid), 'CD_mean': avg(valid, 'CD'), 'H95_mean': avg(valid, 'H95'), 'IOU64_mean': avg(valid, 'IOU64'), 'mean_coverage': avg(valid, 'coverage')}
    summary['per_case'] = rows
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary['methods'], indent=2))


if __name__ == '__main__':
    main()
