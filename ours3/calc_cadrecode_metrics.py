#!/usr/bin/env python3
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OURS3 = ROOT / 'ours3'
EXP = OURS3 / 'full20_object_mesh_to_cad_assembly_v1'
CADRILLE = OURS3 / 'cadrille_cadrecode_parts21_20260926_v2/cadrecode'
OUT = CADRILLE / 'cadrecode_quantitative_metrics_20'
SAMPLE_N = 20_000
SEED = 0
IOU_RESOLUTION = 64

sys.path.insert(0, str(ROOT / 'scripts'))


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force='mesh', process=False)
    if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
        raise ValueError(f'empty mesh: {path}')
    return mesh


def step_mesh(path: Path) -> trimesh.Trimesh:
    import cadquery as cq
    shape = cq.importers.importStep(str(path)).val()
    vertices, faces = shape.tessellate(0.0005, 0.1)
    return trimesh.Trimesh(
        np.asarray([[v.x, v.y, v.z] for v in vertices], dtype=float),
        np.asarray(faces, dtype=np.int64),
        process=False,
    )


def sample_surface(mesh: trimesh.Trimesh, n=SAMPLE_N, seed=SEED):
    from geometry_pack_v1.surface import sample_surface_uniform
    return sample_surface_uniform(mesh.vertices, mesh.faces, n, seed)[0]


def surface_iou(a, b, resolution=IOU_RESOLUTION):
    bounds = np.vstack([a.bounds, b.bounds])
    pitch = float(np.ptp(bounds, axis=0).max() / resolution)
    if not math.isfinite(pitch) or pitch <= 0:
        raise ValueError('invalid common voxel pitch')

    def occupied(mesh):
        indices = np.rint(mesh.voxelized(pitch).points / pitch).astype('int64')
        return set(map(tuple, indices.tolist()))

    sa, sb = occupied(a), occupied(b)
    union = len(sa | sb)
    if not union:
        raise ValueError('empty voxel union')
    return len(sa & sb) / union, pitch, len(sa), len(sb)


def metrics(reference, prediction):
    pa = sample_surface(reference)
    pb = sample_surface(prediction)
    da = cKDTree(pb).query(pa, workers=1)[0]
    db = cKDTree(pa).query(pb, workers=1)[0]
    diag = float(np.linalg.norm(reference.extents))
    iou, pitch, n_ref, n_pred = surface_iou(reference, prediction)
    return {
        'CD': float((da.mean() + db.mean()) * 0.5 / diag),
        'H95': float(np.percentile(np.r_[da, db], 95) / diag),
        'IOU64': float(iou),
        'BBOX_ERROR': float(np.max(np.abs(reference.bounds - prediction.bounds)) / diag),
        'CENTROID_ERROR': float(np.linalg.norm(reference.centroid - prediction.centroid) / diag),
        'IOU_PITCH': pitch,
        'REFERENCE_SURFACE_VOXELS': n_ref,
        'PREDICTION_SURFACE_VOXELS': n_pred,
    }


def mean(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in (None, '')]
    return float(np.mean(vals)) if vals else None


def median(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in (None, '')]
    return float(np.median(vals)) if vals else None


def stats(rows):
    return {
        'N': len(rows),
        'CD_mean': mean(rows, 'CD'),
        'CD_median': median(rows, 'CD'),
        'H95_mean': mean(rows, 'H95'),
        'H95_median': median(rows, 'H95'),
        'IOU64_mean': mean(rows, 'IOU64'),
        'IOU64_median': median(rows, 'IOU64'),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = EXP / 'manifests/FULL20_OBJECT_MANIFEST.csv'
    with manifest_path.open(newline='') as f:
        manifest = list(csv.DictReader(f))

    rows = []
    for i, item in enumerate(manifest, 1):
        object_id = item['OBJECT_ID']
        ref_path = Path(item['FULL_MESH_PATH'])
        pred_path = CADRILLE / object_id / 'assembled.step'
        summary_path = pred_path.parent / 'ASSEMBLY_SUMMARY.json'
        summary = json.loads(summary_path.read_text()) if summary_path.is_file() else {}
        row = {
            'case_index': i,
            'object_id': object_id,
            'status': summary.get('status', 'UNKNOWN'),
            'assembled_parts': summary.get('pass_parts'),
            'total_parts': summary.get('required_parts', int(item['PART_N'])),
            'coverage': ((summary.get('pass_parts') or 0) / float(summary.get('required_parts') or item['PART_N'])),
            'reference_path': str(ref_path),
            'prediction_path': str(pred_path),
            'failure_reason': '',
        }
        try:
            row.update(metrics(load_mesh(ref_path), step_mesh(pred_path)))
        except Exception as exc:
            row['failure_reason'] = f'{type(exc).__name__}: {exc}'
        rows.append(row)
        print(f'[{i:02d}/{len(manifest)}] {object_id} {row["status"]} {row.get("CD", "NA")}', flush=True)

    with (OUT / 'PER_CASE.csv').open('w', newline='') as f:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    complete = [r for r in rows if r['status'] == 'PASS' and not r['failure_reason']]
    previous_common = {
        '2_of_jenga_classic_game', 'android_figure_orange',
        'aroma_stainless_steel_milk_frother_2_cup', 'baby_car', 'birdhouse',
        'cube', 'mini_excavator', 'paintmaker', 'pottery_large', 'robot',
        'speaker_big', 'toaster',
    }
    common = [r for r in complete if r['object_id'] in previous_common]
    all_stats = stats(rows)
    complete_stats = stats(complete)
    common_stats = stats(common)
    summary = {
        'protocol': {
            'sample_n': SAMPLE_N,
            'seed': SEED,
            'CD': 'symmetric mean nearest-neighbor distance / full input bbox diagonal',
            'H95': '95th percentile of bidirectional nearest-neighbor distances / full input bbox diagonal',
            'IOU64': 'world-aligned surface voxel IoU; 64 cells along longest union-bounds axis',
            'registration': 'NONE',
        },
        'all_20': all_stats,
        'complete_only': complete_stats,
        'complete_on_previous_12_common_subset': common_stats,
        'complete_case_ids': [r['object_id'] for r in complete],
        'common_case_ids': [r['object_id'] for r in common],
        'partial_case_ids': [r['object_id'] for r in rows if r['status'] != 'PASS'],
        'failed_metric_cases': [r['object_id'] for r in rows if r['failure_reason']],
    }
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

