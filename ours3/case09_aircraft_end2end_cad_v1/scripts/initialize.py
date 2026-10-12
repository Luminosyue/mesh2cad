#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import socket
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT = ROOT / 'case09_aircraft_end2end_cad_v1'
SOURCE = ROOT / 'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
OLD = ROOT / 'batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/reconstructed.step'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main() -> int:
    if OUT.exists():
        raise RuntimeError(f'refusing to overwrite existing output root: {OUT}')
    for rel in (
        '00_source', '01_part_discovery/p3', '01_part_discovery/physx',
        '02_cad_part_graph', '03_geometry_analyzer', '04_feature_graph',
        '05_backend_recovery', '06_part_qa', '07_assembly', '08_final_qa',
        'artifacts', 'metrics', 'scripts', 'tests', 'logs'
    ):
        (OUT / rel).mkdir(parents=True, exist_ok=True)
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    loaded = trimesh.load(SOURCE, force='mesh', process=False)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise TypeError(f'not a non-empty Trimesh: {type(loaded)!r}')
    vertices = np.asarray(loaded.vertices, dtype=float)
    faces = np.asarray(loaded.faces, dtype=np.int64)
    normals = np.asarray(loaded.face_normals, dtype=float)
    edges = np.sort(np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
    _, edge_counts = np.unique(edges, axis=0, return_counts=True)
    components = loaded.split(only_watertight=False)
    bbox = np.asarray(loaded.bounds, dtype=float)
    diag = float(np.linalg.norm(bbox[1] - bbox[0]))
    audit = {
        'CASE_ID': 'CASE_09_AIRCRAFT_REBUILD',
        'SOURCE_OBJ': str(SOURCE),
        'SOURCE_SHA256': sha256(SOURCE),
        'vertices': int(len(vertices)),
        'triangles': int(len(faces)),
        'connected_components': int(len(components)),
        'bbox': bbox.tolist(),
        'bbox_diagonal': diag,
        'centroid': np.asarray(loaded.centroid, dtype=float).tolist(),
        'mesh_area': float(loaded.area),
        'watertight': bool(loaded.is_watertight),
        'manifold': bool(np.all(edge_counts <= 2)),
        'boundary_edges': int(np.sum(edge_counts == 1)),
        'nonmanifold_edges': int(np.sum(edge_counts > 2)),
        'normal_status': 'FINITE_UNIT' if bool(np.isfinite(normals).all() and np.allclose(np.linalg.norm(normals, axis=1), 1.0, atol=1e-5)) else 'REQUIRES_SAFE_NORMAL_NORMALIZATION',
        'scale': diag,
        'geometry_modified': False,
    }
    dump(OUT / '00_source/source_audit.json', audit)
    shutil.copy2(SOURCE, OUT / '00_source/source_frozen.obj')
    identity = np.eye(4).tolist()
    dump(OUT / '00_source/coordinate_frame.json', {
        'SOURCE_TO_WORLD': identity,
        'WORLD_TO_SOURCE': identity,
        'LOCAL_TO_GLOBAL': identity,
        'GLOBAL_TO_LOCAL': identity,
        'scale': 1.0,
        'frame_policy': 'SOURCE_WORLD_FRAME_FROZEN',
        'aggressive_repair_used': False,
    })
    manifest = {
        'experiment': 'CASE09_AIRCRAFT_END2END_CAD_V1',
        'created_unix': time.time(),
        'execution_host': socket.gethostname(),
        'python': sys.version,
        'source_obj': str(SOURCE),
        'source_sha256': audit['SOURCE_SHA256'],
        'old_baseline_step': str(OLD),
        'old_baseline_exists': OLD.is_file(),
        'old_baseline_role': 'FINAL_EVALUATION_ONLY',
        'old_step_used_for_reconstruction': False,
        'old_compact_role': 'FINAL_EVALUATION_ONLY_IF_PROVENANCE_RESOLVES',
        'output_root': str(OUT),
        'historical_outputs_overwritten': False,
        'frozen_quality_thresholds': {
            'Q1': {'chamfer_max': 0.01, 'p95_max': 0.02, 'coverage02_min': 0.95},
            'Q2': {'chamfer_max': 0.02, 'p95_max': 0.05, 'coverage02_min': 0.85},
        },
    }
    dump(OUT / '00_source/provenance_manifest.json', manifest)
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
