#!/usr/bin/env python3
"""PHASE B+C: generate CADFS train100/heldout25 placement descriptors and audit alignment."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts/m2_placement_cadfs_v1'))
import placement_descriptor_v1 as desc

EXP = ROOT / 'ours3/m2_placement_cadfs_v1'
TRAIN_MAN = ROOT / 'ours3/cadfs_noisy_overfit100_v1/CADFS_NOISY_OVERFIT100_MANIFEST.json'
HOLD_MAN = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/data/HOLDOUT_FINAL_MANIFEST.json'
WANT_TRAIN_SHA = '46b71f35c57c5e8caef6df9bdc22bca092f1c89016a3d5dfb88b101682614285'
WANT_HOLD_SHA = '2e1dc01bf4e7084b7066de986fdb37a650aa94f7069b72a6c48062c6959cdc0b'


def dump(path: pathlib.Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def oracle_dir(curve_feature_path: str) -> pathlib.Path:
    return pathlib.Path(curve_feature_path).parent


def generate_split(name: str, records: list[dict], out_root: pathlib.Path) -> list[dict]:
    rows = []
    for rec in records:
        cad_id = rec['cad_id']
        if name == 'train100':
            oracle = oracle_dir(rec['curve_feature_path'])
            c2_path = pathlib.Path(rec['curve_feature_path'])
        else:
            c2_path = pathlib.Path(rec['oracle_curve'])
            oracle = c2_path.parent
        arr, meta = desc.build_placement_descriptor(oracle)
        c2 = np.load(c2_path)
        if int(c2.shape[0]) != int(arr.shape[0]):
            raise RuntimeError(f'{cad_id}: C2 {c2.shape} vs descriptor {arr.shape}')
        meta['cad_id'] = cad_id
        meta['split'] = name
        meta['c2_token_path'] = str(c2_path)
        meta['c2_token_count'] = int(c2.shape[0])
        cad_dir = out_root / cad_id
        cad_dir.mkdir(parents=True, exist_ok=True)
        npy = cad_dir / 'placement_descriptor.npy'
        np.save(npy, arr)
        dump(cad_dir / 'placement_meta.json', meta)
        rows.append({
            'cad_id': cad_id,
            'oracle_dir': str(oracle),
            'c2_token_path': str(c2_path),
            'placement_descriptor': str(npy),
            'placement_meta': str(cad_dir / 'placement_meta.json'),
            'curve_count': int(arr.shape[0]),
            'curve_ids': meta['curve_ids'],
            'source_curve_indices': meta['source_curve_indices'],
            'curve_order_hash': meta['curve_order_hash'],
            'descriptor_hash': meta['descriptor_hash'],
        })
    return rows


def audit_split(name: str, rows: list[dict]) -> dict:
    n = len(rows)
    checks = {
        'CAD_ID_ALIGNMENT': 0,
        'CURVE_COUNT_ALIGNMENT': 0,
        'CURVE_ID_ALIGNMENT': 0,
        'CURVE_ORDER_ALIGNMENT': 0,
        'DESCRIPTOR_DIM_17': 0,
        'FINITE_DESCRIPTOR': 0,
        'DUPLICATE_CURVE_ID': 0,
    }
    failures = []
    for row in rows:
        cad_id = row['cad_id']
        arr = np.load(row['placement_descriptor'])
        meta = json.loads(pathlib.Path(row['placement_meta']).read_text())
        c2 = np.load(row['c2_token_path'])
        c2_meta = json.loads((pathlib.Path(row['oracle_dir']) / 'curve_tokens_meta.json').read_text())
        meta_ids = [f"edge:{int(c['edge_id'])}" for c in c2_meta['curves']]
        ok = {
            'CAD_ID_ALIGNMENT': meta['cad_id'] == cad_id,
            'CURVE_COUNT_ALIGNMENT': int(c2.shape[0]) == int(arr.shape[0]) == int(meta['curve_count']) == len(c2_meta['curves']) == len(meta['curve_ids']),
            'CURVE_ID_ALIGNMENT': meta['curve_ids'] == meta_ids,
            'CURVE_ORDER_ALIGNMENT': meta['curve_ids'] == meta_ids and meta['curve_order_hash'] == desc.sha256_bytes(json.dumps(meta_ids, separators=(',', ':')).encode()),
            'DESCRIPTOR_DIM_17': list(arr.shape) == [int(c2.shape[0]), 17] and arr.dtype == np.float32,
            'FINITE_DESCRIPTOR': bool(np.isfinite(arr).all()),
            'DUPLICATE_CURVE_ID': len(meta['curve_ids']) == len(set(meta['curve_ids'])),
        }
        for k, v in ok.items():
            if k == 'DUPLICATE_CURVE_ID':
                if v:
                    checks[k] += 1
            elif v:
                checks[k] += 1
        if not all(ok.values()):
            failures.append({'cad_id': cad_id, 'ok': ok})
    pct = {k: (100.0 * v / n if n else 0.0) for k, v in checks.items() if k != 'DUPLICATE_CURVE_ID'}
    pass_n = n - len(failures)
    return {
        'split': name,
        'TOTAL': n,
        'PASS': pass_n,
        'FAIL': len(failures),
        'checks': checks,
        'percent': pct,
        'DUPLICATE_CURVE_ID_CASES': n - checks['DUPLICATE_CURVE_ID'],
        'failures': failures,
    }


def main():
    EXP.mkdir(parents=True, exist_ok=True)
    for sub in ['data/train100', 'data/heldout25', 'audits', 'provenance', 'checkpoints', 'eval']:
        (EXP / sub).mkdir(parents=True, exist_ok=True)

    canary = desc.replay_canary()
    dump(EXP / 'provenance/CANARY_DESCRIPTOR_REPLAY.json', canary)
    if not canary['PASS']:
        dump(EXP / 'audits/ALIGNMENT_GATE.json', {
            'CURRENT_GATE': 'PLACEMENT_DATA_ALIGNMENT_FAIL',
            'TRAINING_READY': 'NO',
            'TRAINING_STARTED': 'NO',
            'reason': 'canary 17-D replay failed',
        })
        raise SystemExit('CURRENT_GATE=PLACEMENT_DATA_ALIGNMENT_FAIL')

    train = json.loads(TRAIN_MAN.read_text())['records']
    hold = json.loads(HOLD_MAN.read_text())['records']
    train_ids = [r['cad_id'] for r in train]
    hold_ids = [r['cad_id'] for r in hold]
    train_sha = desc.ids_sha256(train_ids)
    hold_sha = desc.ids_sha256(hold_ids)
    inter = sorted(set(train_ids) & set(hold_ids))
    freeze = {
        'EXPERIMENT': 'M2_PLACEMENT_CADFS_V1',
        'TRAIN_MANIFEST': str(TRAIN_MAN),
        'TRAIN_CAD_COUNT': len(train_ids),
        'TRAIN_ID_SHA256': train_sha,
        'HELDOUT_MANIFEST': str(HOLD_MAN),
        'HELDOUT_CAD_COUNT': len(hold_ids),
        'HELDOUT_ID_SHA256': hold_sha,
        'TRAIN_HELDOUT_INTERSECTION': len(inter),
        'intersection_ids': inter,
        'V3_TRAIN800_USED': False,
        'TANK_CASE_USED': False,
        'RESAMPLED': False,
        'DESCRIPTOR_IMPLEMENTATION_SOURCE': desc.DESCRIPTOR_IMPLEMENTATION_SOURCE,
        'DESCRIPTOR_FUNCTION': desc.DESCRIPTOR_FUNCTION,
        '17D_FIELD_DEFINITION': desc.FIELD_DEFINITION,
        'NORMALIZATION_RULE': desc.NORMALIZATION_RULE,
        'PLACEMENT_SOURCE': desc.PLACEMENT_SOURCE,
    }
    dump(EXP / 'provenance/COHORT_FREEZE.json', freeze)
    if (len(train_ids), train_sha, len(hold_ids), hold_sha, len(inter)) != (100, WANT_TRAIN_SHA, 25, WANT_HOLD_SHA, 0):
        dump(EXP / 'audits/ALIGNMENT_GATE.json', {
            'CURRENT_GATE': 'PLACEMENT_DATA_ALIGNMENT_FAIL',
            'TRAINING_READY': 'NO',
            'TRAINING_STARTED': 'NO',
            'reason': 'frozen cohort hash/count mismatch',
            'freeze': freeze,
        })
        raise SystemExit('CURRENT_GATE=PLACEMENT_DATA_ALIGNMENT_FAIL')

    train_rows = generate_split('train100', train, EXP / 'data/train100')
    hold_rows = generate_split('heldout25', hold, EXP / 'data/heldout25')
    dump(EXP / 'data/TRAIN100_INDEX.json', {'count': len(train_rows), 'records': train_rows})
    dump(EXP / 'data/HELDOUT25_INDEX.json', {'count': len(hold_rows), 'records': hold_rows})

    train_audit = audit_split('train100', train_rows)
    hold_audit = audit_split('heldout25', hold_rows)
    dump(EXP / 'audits/TRAIN100_ALIGNMENT.json', train_audit)
    dump(EXP / 'audits/HELDOUT25_ALIGNMENT.json', hold_audit)

    leakage = len(set(train_ids) & set(hold_ids))
    pass_ok = (
        train_audit['TOTAL'] == 100 and train_audit['PASS'] == 100
        and hold_audit['TOTAL'] == 25 and hold_audit['PASS'] == 25
        and all(v == 100.0 for v in train_audit['percent'].values())
        and all(v == 100.0 for v in hold_audit['percent'].values())
        and leakage == 0
        and train_audit['DUPLICATE_CURVE_ID_CASES'] == 0
        and hold_audit['DUPLICATE_CURVE_ID_CASES'] == 0
    )
    gate = {
        'CURRENT_GATE': 'PLACEMENT_DATA_ALIGNMENT_PASS' if pass_ok else 'PLACEMENT_DATA_ALIGNMENT_FAIL',
        'TRAINING_READY': 'YES' if pass_ok else 'NO',
        'TRAINING_STARTED': 'NO',
        'TRAIN_TOTAL': train_audit['TOTAL'],
        'TRAIN_PASS': train_audit['PASS'],
        'HELDOUT_TOTAL': hold_audit['TOTAL'],
        'HELDOUT_PASS': hold_audit['PASS'],
        'CAD_ID_ALIGNMENT': '100%' if pass_ok else 'FAIL',
        'CURVE_COUNT_ALIGNMENT': '100%' if pass_ok else 'FAIL',
        'CURVE_ID_ALIGNMENT': '100%' if pass_ok else 'FAIL',
        'CURVE_ORDER_ALIGNMENT': '100%' if pass_ok else 'FAIL',
        'DESCRIPTOR_DIM_17': '100%' if pass_ok else 'FAIL',
        'FINITE_DESCRIPTOR': '100%' if pass_ok else 'FAIL',
        'TRAIN_HELDOUT_LEAKAGE': leakage,
        'train_percent': train_audit['percent'],
        'heldout_percent': hold_audit['percent'],
    }
    dump(EXP / 'audits/ALIGNMENT_GATE.json', gate)
    print(json.dumps(gate, indent=2))
    if not pass_ok:
        raise SystemExit('CURRENT_GATE=PLACEMENT_DATA_ALIGNMENT_FAIL')


if __name__ == '__main__':
    main()
