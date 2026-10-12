#!/usr/bin/env python3
"""Deterministic 500 raw-candidate selection with separate supported/advanced CADFS pools."""
from __future__ import annotations
import hashlib, json, random, sys
from collections import Counter, defaultdict
from pathlib import Path
from .config import DATA_ROOT, DEEPCAD_RAW_JSON, FUSION360_PASS, CADFS_FEATURESCRIPT, SEED
from .schema import new_record, validate_record

sys.path.insert(0, str(Path('/data/home/cuiyuehan/project/mesh2cad/scripts')))
from canonical_cad_data_v4.converters.cadfs_to_dsl import audit_featurescript

ADVANCED = ('revolve','loft','sweep','fillet','chamfer','shell','mirror','pattern','ellipse','bspline')

def stable_shuffle(items):
    return sorted(items, key=lambda p: hashlib.sha256((str(p) + f'|{SEED}').encode()).hexdigest())

def deepcad():
    files = stable_shuffle(DEEPCAD_RAW_JSON.glob('*.json'))[:100]
    return [new_record(cad_id=f'DEEPCAD_{p.stem}', source='DEEPCAD', source_id=p.stem, source_path=str(p)) for p in files]

def fusion():
    ids = json.loads(FUSION360_PASS.read_text())['cad_ids']
    chosen = stable_shuffle(ids)[:100]
    return [new_record(cad_id='FUSION360_' + x.removeprefix('fusion360__'), source='FUSION360', source_id=x.removeprefix('fusion360__'), source_path=x) for x in chosen]

def cadfs():
    paths = stable_shuffle(CADFS_FEATURESCRIPT.rglob('*.txt'))
    supported, advanced, represented = [], [], Counter()
    for p in paths:
        text = p.read_text(encoding='utf-8', errors='replace')
        a = audit_featurescript(text); ops = a['unsupported']
        rec = new_record(cad_id='CADFS_' + p.stem, source='CADFS', source_id=p.stem, source_path=str(p))
        rec['operations'] = a['present']; rec['num_operations'] = a['n_features']
        if not ops and a['lossless_candidate'] and len(supported) < 150:
            rec['status'] = 'candidate_supported'; supported.append(rec)
        elif ops and len(advanced) < 150:
            rec['status'] = 'unsupported_audit_candidate'; rec['failure_reason'] = 'UNSUPPORTED_OPERATION:' + ','.join(ops); advanced.append(rec)
            represented.update(ops)
        if len(supported) == 150 and len(advanced) == 150 and len(represented) >= 6: break
    if len(supported) != 150 or len(advanced) != 150:
        raise RuntimeError(f'insufficient CADFS strata: supported={len(supported)}, advanced={len(advanced)}')
    return supported + advanced, represented

def main():
    out = DATA_ROOT / 'manifests/canary_500_raw_candidates.jsonl'
    report = DATA_ROOT / 'reports/03_CANARY_500_SELECTION.json'
    if out.exists() or report.exists(): raise FileExistsError('refusing to overwrite existing canary selection')
    rows = deepcad() + fusion(); crows, represented = cadfs(); rows += crows
    if len(rows) != 500: raise RuntimeError(f'expected 500 candidates, got {len(rows)}')
    for r in rows: validate_record(r)
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))
    manifest_sha = hashlib.sha256(out.read_bytes()).hexdigest()
    counts = Counter(r['source'] for r in rows); status = Counter(r['status'] for r in rows)
    report.parent.mkdir(parents=True, exist_ok=True); report.write_text(json.dumps({'raw_total':len(rows),'source_counts':dict(counts),'status_counts':dict(status),'cadfs_supported_pool':150,'cadfs_advanced_unsupported_audit_pool':150,'advanced_operations_represented':dict(represented),'manifest':str(out),'manifest_sha256':manifest_sha,'deterministic_seed':SEED,'training_started':False,'official_test_read':False}, indent=2)+'\n')
    print(report)

if __name__ == '__main__': main()
