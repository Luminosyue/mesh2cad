#!/usr/bin/env python3
"""Bit-exact replay of canary PLACEMENT_DESCRIPTOR_V1 (17-D).

This is recovered from the frozen canary spec + 13 Complex15 npy files.
Do not redesign fields, order, or normalization.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
CANARY = ROOT / 'ours3/placement_aware_curve_token_canary_v1'
SPEC = CANARY / 'PLACEMENT_NORMALIZATION.json'

DESCRIPTOR_IMPLEMENTATION_SOURCE = str(CANARY)
DESCRIPTOR_FUNCTION = 'scripts/m2_placement_cadfs_v1/placement_descriptor_v1.py:build_placement_descriptor'
FIELD_DEFINITION = [
    'centroid_xyz',
    'bbox_extent_xyz',
    'endpoint_A_xyz',
    'endpoint_B_xyz',
    'endpoint_valid_mask',
    'canonical_plane_normal_xyz',
    'plane_valid_mask',
]
NORMALIZATION_RULE = {
    'CAD_bbox_source': 'curves.json source_bbox_min/max (clean B-Rep extractor)',
    'CAD_bbox_center': '(min+max)/2',
    'CAD_bbox_diagonal': 'max(L2(max-min), 1e-12)',
    'point': '(p - center) / diag',
    'extent': '(curve_bbox_max - curve_bbox_min) / diag',
    'normal': 'unit length; first xyz component attaining max |n_i| is forced positive',
}
PLACEMENT_SOURCE = 'clean B-Rep global curve samples + extracted exact parameters; never C2 local coordinates'
EPS = 1e-12


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def ids_sha256(ids: list[str]) -> str:
    return sha256_bytes(('\n'.join(ids) + '\n').encode())


def canonicalize_normal(n) -> np.ndarray | None:
    v = np.asarray(n, dtype=np.float64).reshape(-1)
    if v.size != 3:
        return None
    nrm = float(np.linalg.norm(v))
    if nrm < EPS:
        return None
    v = v / nrm
    idx = int(np.argmax(np.abs(v)))
    if v[idx] < 0:
        v = -v
    return v


def _norm_point(p, center, diag):
    return (np.asarray(p, dtype=np.float64).reshape(3) - center) / diag


def build_placement_descriptor(oracle_dir: pathlib.Path) -> tuple[np.ndarray, dict]:
    oracle_dir = pathlib.Path(oracle_dir)
    curves_pack = json.loads((oracle_dir / 'curves.json').read_text())
    meta = json.loads((oracle_dir / 'curve_tokens_meta.json').read_text())
    samples = np.load(oracle_dir / 'curve_samples.npz')
    tokens_path = oracle_dir / 'curve_tokens.npy'
    if not tokens_path.exists():
        tokens_path = oracle_dir / 'curve_tokens_c2.npy'
    c2 = np.load(tokens_path) if tokens_path.exists() else None

    bbox_min = np.asarray(curves_pack['source_bbox_min'], dtype=np.float64)
    bbox_max = np.asarray(curves_pack['source_bbox_max'], dtype=np.float64)
    center = (bbox_min + bbox_max) / 2.0
    diag = max(float(np.linalg.norm(bbox_max - bbox_min)), EPS)

    kept = meta['curves']
    if c2 is not None and int(c2.shape[0]) != len(kept):
        raise RuntimeError(f'C2/meta count mismatch {oracle_dir}: {c2.shape[0]} vs {len(kept)}')

    edge_to_sample = {int(e): i for i, e in enumerate(np.asarray(samples['curve_edge_id']).tolist())}
    brep_by_edge = {int(c['edge_id']): c for c in curves_pack['curves']}
    if len(brep_by_edge) != len(curves_pack['curves']):
        raise RuntimeError(f'duplicate B-Rep edge_id in {oracle_dir}')

    rows = []
    curve_ids = []
    source_indices = []
    details = []
    for token_i, mc in enumerate(kept):
        eid = int(mc['edge_id'])
        if eid not in edge_to_sample:
            raise RuntimeError(f'edge_id {eid} missing from curve_samples.npz in {oracle_dir}')
        if eid not in brep_by_edge:
            raise RuntimeError(f'edge_id {eid} missing from curves.json in {oracle_dir}')
        si = int(edge_to_sample[eid])
        brep = brep_by_edge[eid]
        xyz = np.asarray(samples['curve_xyz'][si], dtype=np.float32)
        mask = np.asarray(samples['curve_mask'][si]).astype(bool)
        pts = xyz[mask].astype(np.float64)
        if pts.shape[0] < 1:
            raise RuntimeError(f'empty samples for edge {eid} in {oracle_dir}')
        centroid = pts.mean(axis=0)
        extent = pts.max(axis=0) - pts.min(axis=0)
        is_closed = bool(brep['is_closed'])
        g = np.zeros(17, dtype=np.float64)
        g[0:3] = _norm_point(centroid, center, diag)
        g[3:6] = extent / diag
        if is_closed:
            endpoint_rule = 'closed_curve_zero_mask'
            plane = canonicalize_normal((brep.get('world_parameters') or {}).get('normal'))
            if plane is not None:
                g[13:16] = plane
                g[16] = 1.0
        else:
            g[6:9] = _norm_point(brep['start_point'], center, diag)
            g[9:12] = _norm_point(brep['end_point'], center, diag)
            g[12] = 1.0
            endpoint_rule = 'source_extractor_parameter_direction_u_start_to_u_end'
        rows.append(g)
        curve_ids.append(f'edge:{eid}')
        source_indices.append(si)
        details.append({
            'token_index': token_i,
            'edge_id': eid,
            'source_curve_index': si,
            'curve_type': brep.get('curve_type') or mc.get('type'),
            'is_closed': is_closed,
            'endpoint_ordering_rule': endpoint_rule,
            'endpoint_valid_mask': float(g[12]),
            'plane_valid_mask': float(g[16]),
        })

    desc = np.asarray(rows, dtype=np.float32)
    if not np.isfinite(desc).all():
        raise RuntimeError(f'non-finite descriptor in {oracle_dir}')
    order_payload = json.dumps(curve_ids, separators=(',', ':')).encode()
    meta_out = {
        'cad_id': None,
        'curve_count': int(desc.shape[0]),
        'curve_ids': curve_ids,
        'source_curve_indices': source_indices,
        'c2_token_path': str(tokens_path) if tokens_path.exists() else None,
        'c2_token_count': None if c2 is None else int(c2.shape[0]),
        'curve_order_hash': sha256_bytes(order_payload),
        'descriptor_hash': sha256_bytes(desc.tobytes()),
        'descriptor_shape': list(desc.shape),
        'descriptor_dtype': 'float32',
        'bbox_center': center.tolist(),
        'bbox_diagonal': diag,
        'details': details,
        'DESCRIPTOR_IMPLEMENTATION_SOURCE': DESCRIPTOR_IMPLEMENTATION_SOURCE,
        'DESCRIPTOR_FUNCTION': DESCRIPTOR_FUNCTION,
        '17D_FIELD_DEFINITION': FIELD_DEFINITION,
        'NORMALIZATION_RULE': NORMALIZATION_RULE,
        'PLACEMENT_SOURCE': PLACEMENT_SOURCE,
    }
    return desc, meta_out


def replay_canary() -> dict:
    spec = json.loads(SPEC.read_text())
    if spec['descriptor_order'] != FIELD_DEFINITION:
        raise RuntimeError('frozen field order mismatch')
    index = json.loads((CANARY / 'placement/PLACEMENT_DESCRIPTOR_INDEX.json').read_text())['records']
    rows = []
    for rec in index:
        oracle = pathlib.Path(rec['path']).parent
        pred, _ = build_placement_descriptor(oracle)
        gold = np.load(rec['path'])
        maxabs = float(np.max(np.abs(pred.astype(np.float64) - gold.astype(np.float64)))) if gold.shape == pred.shape else float('inf')
        rows.append({
            'cad_id': rec['cad_id'],
            'shape_match': list(pred.shape) == list(gold.shape),
            'gold_shape': list(gold.shape),
            'pred_shape': list(pred.shape),
            'maxabs': maxabs,
            'bit_exact': bool(maxabs == 0.0),
        })
    n = len(rows)
    n_ok = sum(r['bit_exact'] for r in rows)
    return {
        'CANARY_N': n,
        'CANARY_BIT_EXACT': n_ok,
        'PASS': n == 13 and n_ok == 13,
        'records': rows,
        'DESCRIPTOR_IMPLEMENTATION_SOURCE': DESCRIPTOR_IMPLEMENTATION_SOURCE,
        'DESCRIPTOR_FUNCTION': DESCRIPTOR_FUNCTION,
        '17D_FIELD_DEFINITION': FIELD_DEFINITION,
        'NORMALIZATION_RULE': NORMALIZATION_RULE,
        'PLACEMENT_SOURCE': PLACEMENT_SOURCE,
    }


if __name__ == '__main__':
    report = replay_canary()
    print(json.dumps({k: report[k] for k in report if k != 'records'}, indent=2))
    print('CANARY_BIT_EXACT', report['CANARY_BIT_EXACT'], '/', report['CANARY_N'], 'PASS' if report['PASS'] else 'FAIL')
    if not report['PASS']:
        raise SystemExit(1)
