#!/usr/bin/env python3
import json, os, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import torch

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/m2_exact9998_curve_token_cache_completion_v1'
CKPT = ROOT / 'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
sys.path.insert(0, str(ROOT / 'scripts'))
from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import load_backbone, curve_inputs, TYPE_TO_ID, OCC_ID_TO_TYPE, MAX_CURVE_TOKENS

def process_row(row, original, model, device):
    z = np.load(row['curve_source_path'], allow_pickle=False)
    brep_path = Path(original[row['cad_id']]['surface_path']).parent / 'brep_edges.json'
    brep = json.load(open(brep_path))
    sharp = {int(e['edge_index']): bool(e.get('is_sharp', False)) for e in brep['edges']}
    feats, scales, kept = [], [], []
    for i in range(int(z['num_curves'][0])):
        ctype = OCC_ID_TO_TYPE.get(int(z['curve_type_id'][i])); edge_id = int(z['curve_edge_id'][i])
        if ctype not in TYPE_TO_ID or not sharp.get(edge_id, False):
            continue
        xyz = np.asarray(z['curve_xyz_normalized'][i], dtype=np.float64)
        tangent = np.asarray(z['curve_tangent'][i], dtype=np.float32)
        feat, scale = curve_inputs(xyz, tangent)
        feats.append(feat); scales.append(scale)
        kept.append(float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()))
    order = np.argsort([-x for x in kept])[:MAX_CURVE_TOKENS]
    if not len(order):
        return None
    with torch.no_grad():
        return model(torch.from_numpy(np.stack([feats[i] for i in order])).to(device), torch.from_numpy(np.stack([scales[i] for i in order])).to(device))['token'].float().cpu().numpy().astype(np.float32)

def write_json(name, value):
    path = OUT / name
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)

def main():
    torch.cuda.set_device(5)
    device = torch.device('cuda:5')
    model, _ = load_backbone(CKPT, device)
    reg = OUT / 'EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'
    rows = [json.loads(x) for x in reg.open() if json.loads(x)['split'] in ('train', 'val')]
    original = {r['cad_id']: r for r in (json.loads(x) for x in (ROOT/'ours3/exact9998_v1/EXACT9998_ASSET_REGISTRY_V1.jsonl').open())}
    by = defaultdict(list)
    for row in rows:
        by[row['dataset']].append(row)
    chosen = []
    for dataset, group in sorted(by.items()):
        group = sorted(group, key=lambda r: (r['K'], r['cad_id']))
        n = min(50, len(group))
        indices = sorted(set(round(i * (len(group) - 1) / (n - 1)) for i in range(n))) if n > 1 else [0]
        chosen.extend(group[i] for i in indices)
    if len(chosen) < 100:
        used = {r['cad_id'] for r in chosen}
        chosen.extend([r for r in rows if r['cad_id'] not in used][:100-len(chosen)])
    chosen = chosen[:100]
    results = []
    for i, row in enumerate(chosen, 1):
        got = process_row(row, original, model, device)
        expected = np.load(row['curve_token_path'], allow_pickle=False)
        exact = got is not None and got.shape == expected.shape and np.array_equal(got, expected)
        diff = None if got is None or got.shape != expected.shape else float(np.max(np.abs(got - expected)))
        results.append({'cad_id': row['cad_id'], 'dataset': row['dataset'], 'K': row['K'], 'expected_shape': list(expected.shape), 'actual_shape': None if got is None else list(got.shape), 'exact_equal': exact, 'max_abs_diff': diff})
        if i % 10 == 0:
            print(f'canary {i}/100', flush=True)
    det = []
    successful_ids = {x['cad_id'] for x in results if x['exact_equal']}
    for row in [r for r in chosen if r['cad_id'] in successful_ids][:10]:
        a = process_row(row, original, model, device)
        b = process_row(row, original, model, device)
        det.append({'cad_id': row['cad_id'], 'shape_equal': a.shape == b.shape, 'exact_equal': np.array_equal(a, b), 'max_abs_diff': float(np.max(np.abs(a-b)))})
    write_json('C2_TOKEN_CANARY100.json', {'device': 'cuda:5', 'count': len(results), 'pass': sum(x['exact_equal'] for x in results), 'all_pass': all(x['exact_equal'] for x in results), 'dataset_counts': dict(Counter(x['dataset'] for x in results)), 'K_min': min(x['K'] for x in results), 'K_median': float(np.median([x['K'] for x in results])), 'K_max': max(x['K'] for x in results), 'K128_present': any(x['K'] == 128 for x in results), 'cases': results})
    write_json('C2_TOKEN_DETERMINISM_AUDIT.json', {'repeated_cases': 10, 'exact_pass': sum(x['exact_equal'] for x in det), 'all_pass': all(x['exact_equal'] for x in det), 'tolerance': {'rtol': 0, 'atol': 0}, 'cases': det})
    print(json.dumps({'canary_exact_pass': sum(x['exact_equal'] for x in results), 'determinism_exact_pass': sum(x['exact_equal'] for x in det)}, indent=2))

if __name__ == '__main__':
    main()
