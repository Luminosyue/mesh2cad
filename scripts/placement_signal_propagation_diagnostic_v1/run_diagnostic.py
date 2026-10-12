#!/usr/bin/env python3
"""PLACEMENT_SIGNAL_PROPAGATION_DIAGNOSTIC_V1

Locate the first layer where global placement information cannot be recovered.
Does not retrain the LLM / C2 / PlacementMLP. Linear probes only.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
import torch
import torch.nn as nn

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'))
sys.path.insert(0, str(ROOT / 'scripts/m2_placement_cadfs_v1'))
from geometry_prefix_adapter import GeometryPrefixAdapter
import placement_descriptor_v1 as descmod

OUT = ROOT / 'ours3/placement_signal_propagation_diagnostic_v1'
M2P_CKPT = ROOT / 'ours3/m2_placement_cadfs_v1/checkpoints/M2_PLACEMENT_CADFS_V1/checkpoint_epoch_20'
OLD_M2_CKPT = ROOT / 'ours3/cadfs_noisy_overfit100_v1/runs_retrain_v1/M2_ORACLE_CADFS100_NOISY_RETRAIN_V1/checkpoint_epoch_20'
TRAIN_INDEX = ROOT / 'ours3/m2_placement_cadfs_v1/data/TRAIN100_INDEX.json'
HOLD_INDEX = ROOT / 'ours3/m2_placement_cadfs_v1/data/HELDOUT25_INDEX.json'
OLD_M2_DEC = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2'
M2P_DEC = ROOT / 'ours3/m2_placement_cadfs_v1/eval/heldout25/M2_PLACEMENT'
GT_DSL = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/data'
TARGET_NORM = 1.9414176940917969
SEED = 42
KCAP = 128
HIGH = 0.50
LOW = 0.20
FIELDS = [
    ('centroid_xyz', 0, 3),
    ('bbox_extent_xyz', 3, 6),
    ('endpoint_A_xyz', 6, 9),
    ('endpoint_B_xyz', 9, 12),
    ('endpoint_valid_mask', 12, 13),
    ('canonical_plane_normal_xyz', 13, 16),
    ('plane_valid_mask', 16, 17),
]


class PlacementMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(17, 64), nn.GELU(), nn.Linear(64, 256))

    def forward(self, g):
        return self.net(g)


def dump(path: pathlib.Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def load_index(path: pathlib.Path):
    return json.loads(path.read_text())['records']


def stats_1d(x):
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {'n': 0, 'mean': None, 'median': None, 'p10': None, 'p90': None, 'max': None, 'min': None}
    return {
        'n': int(x.size),
        'mean': float(x.mean()),
        'median': float(np.median(x)),
        'p10': float(np.quantile(x, 0.10)),
        'p90': float(np.quantile(x, 0.90)),
        'max': float(x.max()),
        'min': float(x.min()),
        'p01': float(np.quantile(x, 0.01)),
        'p50': float(np.median(x)),
        'p99': float(np.quantile(x, 0.99)),
        'std': float(x.std()),
    }


def r2_mae_rmse(y, yhat):
    y = np.asarray(y, dtype=np.float64)
    yhat = np.asarray(yhat, dtype=np.float64)
    if y.ndim == 1:
        y = y[:, None]
        yhat = yhat[:, None]
    err = yhat - y
    mae = np.mean(np.abs(err), axis=0)
    rmse = np.sqrt(np.mean(err ** 2, axis=0))
    ss_res = np.sum(err ** 2, axis=0)
    ss_tot = np.sum((y - y.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide='ignore', invalid='ignore'):
        r2 = np.where(ss_tot > 1e-18, 1.0 - ss_res / ss_tot, 0.0)
    r2 = np.nan_to_num(r2, nan=0.0, posinf=0.0, neginf=0.0)
    out = {
        'n': int(y.shape[0]),
        'dim': int(y.shape[1]),
        'R2': [float(v) for v in r2],
        'R2_mean': float(np.mean(r2)),
        'MAE': [float(v) for v in mae],
        'MAE_mean': float(np.mean(mae)),
        'RMSE': [float(v) for v in rmse],
        'RMSE_mean': float(np.mean(rmse)),
        'y_std': [float(v) for v in y.std(axis=0)],
    }
    if y.shape[1] == 3:
        out.update({'R2_x': out['R2'][0], 'R2_y': out['R2'][1], 'R2_z': out['R2'][2],
                    'MAE_x': out['MAE'][0], 'MAE_y': out['MAE'][1], 'MAE_z': out['MAE'][2]})
    return out


RIDGE = 1.0


def fit_linear(X, Y, ridge=RIDGE):
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    if Y.ndim == 1:
        Y = Y[:, None]
    mu = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    Xs = (X - mu) / std
    Xb = np.concatenate([Xs, np.ones((X.shape[0], 1))], axis=1)
    d = Xb.shape[1]
    A = Xb.T @ Xb
    A[:d - 1, :d - 1] = A[:d - 1, :d - 1] + ridge * np.eye(d - 1)
    W = np.linalg.solve(A, Xb.T @ Y)
    return {'W': W, 'mu': mu, 'std': std, 'ridge': float(ridge)}


def pred_linear(model, X):
    X = np.asarray(X, dtype=np.float64)
    Xs = (X - model['mu']) / model['std']
    Xb = np.concatenate([Xs, np.ones((X.shape[0], 1))], axis=1)
    return Xb @ model['W']


def fit_pca(X, k):
    X = np.asarray(X, dtype=np.float64)
    mu = X.mean(axis=0)
    xc = X - mu
    _, _, vt = np.linalg.svd(xc, full_matrices=False)
    k = int(max(1, min(k, vt.shape[0], X.shape[0] - 1)))
    return mu, vt[:k]


def apply_pca(X, mu, comp):
    return (np.asarray(X, dtype=np.float64) - mu) @ comp.T


def angular_mae(a, b):
    a = np.asarray(a, dtype=np.float64).reshape(-1, 3)
    b = np.asarray(b, dtype=np.float64).reshape(-1, 3)
    na = np.linalg.norm(a, axis=1)
    nb = np.linalg.norm(b, axis=1)
    ok = (na > 1e-12) & (nb > 1e-12)
    if not np.any(ok):
        return None
    c = np.clip(np.sum(a[ok] / na[ok, None] * b[ok] / nb[ok, None], axis=1), -1.0, 1.0)
    return float(np.mean(np.degrees(np.arccos(c))))


def level(r2):
    if r2 is None:
        return 'NA'
    if r2 >= HIGH:
        return 'HIGH'
    if r2 >= LOW:
        return 'MED'
    return 'LOW'


def load_split(records):
    cads = []
    for rec in records:
        D = np.load(rec['placement_descriptor']).astype(np.float32)
        C = np.load(rec['c2_token_path']).astype(np.float32)
        meta = json.loads(pathlib.Path(rec['placement_meta']).read_text())
        if D.shape[0] != C.shape[0]:
            raise RuntimeError(f'curve mismatch {rec["cad_id"]}')
        cads.append({
            'cad_id': rec['cad_id'],
            'oracle_dir': rec['oracle_dir'],
            'curve_ids': list(meta['curve_ids']),
            'D': D,
            'C': C,
        })
    return cads


def adapter_summary(adapter, tokens_kcap, mask):
    """Hook the real 8-token GeometryPrefixAdapter. tokens_kcap is [KCAP, 256]."""
    x = torch.from_numpy(np.asarray(tokens_kcap, dtype=np.float32)).unsqueeze(0)
    return adapter(x, mask)[0][0].cpu().numpy().astype(np.float32)


def hook_placement_tokens(mlp, C, D):
    """Replay training: pad to KCAP, residual *= mask, enhanced = C2 + P."""
    n = int(C.shape[0])
    c_pad = np.zeros((KCAP, C.shape[1]), np.float32)
    d_pad = np.zeros((KCAP, 17), np.float32)
    c_pad[:n] = C
    d_pad[:n] = D
    mask = torch.zeros(1, KCAP, dtype=torch.bool)
    mask[0, :n] = True
    residual = mlp(torch.from_numpy(d_pad))
    residual = residual * mask[0].to(dtype=residual.dtype).unsqueeze(-1)
    e_pad = torch.from_numpy(c_pad) + residual
    P = residual[:n].cpu().numpy().astype(np.float32)
    E = e_pad[:n].cpu().numpy().astype(np.float32)
    return P, E, c_pad, e_pad.cpu().numpy().astype(np.float32), mask


def export_split(name, cads, mlp, adapter_place, adapter_old, out_root: pathlib.Path, shuffle=False, zero=False, seed=SEED):
    rng = np.random.RandomState(seed)
    curve_rows = []
    cad_rows = []
    with torch.no_grad():
        for cad in cads:
            D = cad['D'].copy()
            C = cad['C']
            n = int(C.shape[0])
            perm = np.arange(n)
            if shuffle and n > 1:
                perm = rng.permutation(n)
                D = D[perm]
            if zero:
                D = np.zeros_like(D)
            P, E, c_pad, e_pad, mask = hook_placement_tokens(mlp, C, D)
            S_place = adapter_summary(adapter_place, e_pad, mask)
            S_old = adapter_summary(adapter_old, c_pad, mask)
            cad_dir = out_root / 'curve_level' / name / cad['cad_id']
            cad_dir.mkdir(parents=True, exist_ok=True)
            meta = {
                'cad_id': cad['cad_id'],
                'n_curves': n,
                'curve_id': cad['curve_ids'],
                'curve_order': list(range(n)),
                'perm': perm.tolist(),
                'shuffle': bool(shuffle),
                'zero': bool(zero),
                'KCAP': KCAP,
            }
            if not shuffle and not zero:
                np.save(cad_dir / 'L0_descriptor.npy', cad['D'])
                np.save(cad_dir / 'L1_c2.npy', C)
                np.save(cad_dir / 'L2_residual.npy', P)
                np.save(cad_dir / 'L3_enhanced.npy', E)
                np.save(cad_dir / 'L4_enhanced_set.npy', E)
                np.save(cad_dir / 'L5_summary_m2_placement.npy', S_place)
                np.save(cad_dir / 'L5_summary_old_m2.npy', S_old)
                dump(cad_dir / 'L4_curve_index.json', meta)
                sum_dir = OUT / 'representations/summary_level' / name / cad['cad_id']
                sum_dir.mkdir(parents=True, exist_ok=True)
                np.save(sum_dir / 'S_m2_placement.npy', S_place)
                np.save(sum_dir / 'S_old_m2.npy', S_old)
                dump(sum_dir / 'meta.json', meta)
            elif shuffle or zero:
                dump(cad_dir / 'control_meta.json', meta)
                np.save(cad_dir / 'L5_summary.npy', S_place)
            c_norm = np.linalg.norm(C.astype(np.float64), axis=1)
            p_norm = np.linalg.norm(P.astype(np.float64), axis=1)
            e_norm = np.linalg.norm(E.astype(np.float64), axis=1)
            ratio = p_norm / np.maximum(c_norm, 1e-12)
            cos = np.sum(C.astype(np.float64) * P.astype(np.float64), axis=1) / np.maximum(c_norm * p_norm, 1e-12)
            cad_rows.append({
                'cad_id': cad['cad_id'],
                'n_curves': n,
                'curve_ids': cad['curve_ids'],
                'perm': perm.tolist(),
                'D_original': cad['D'],
                'D': D, 'C': C, 'P': P, 'E': E,
                'S_place': S_place, 'S_old': S_old,
                'c_norm': c_norm, 'p_norm': p_norm, 'e_norm': e_norm, 'ratio': ratio, 'cosine': cos,
            })
            for i in range(n):
                curve_rows.append({
                    'cad_id': cad['cad_id'],
                    'curve_index': i,
                    'curve_order': i,
                    'curve_id': cad['curve_ids'][i],
                    'source_curve_index_after_perm': int(perm[i]) if shuffle else i,
                    'D': D[i], 'C': C[i], 'P': P[i], 'E': E[i],
                    'c_norm': float(c_norm[i]), 'p_norm': float(p_norm[i]),
                    'ratio': float(ratio[i]), 'cosine': float(cos[i]),
                })
    return curve_rows, cad_rows


def stack_curves(rows, key):
    return np.stack([r[key] for r in rows], axis=0)


def cad_placement_target(D):
    """Frozen 12-D CAD-level placement statistic from the same 17-D descriptor."""
    c = D[:, 0:3].astype(np.float64)
    return np.concatenate([c.mean(axis=0), c.std(axis=0), c.min(axis=0), c.max(axis=0)], axis=0)


def cad_extent_mean(D):
    return D[:, 3:6].astype(np.float64).mean(axis=0)


def subset_mask(rows, col, val=1.0):
    d = stack_curves(rows, 'D')
    return d[:, col] >= 0.5 if val == 1.0 else d[:, col] < 0.5


def probe_xyz(train_X, train_Y, hold_X, hold_Y, name):
    model = fit_linear(train_X, train_Y)
    yhat_tr = pred_linear(model, train_X)
    yhat = pred_linear(model, hold_X)
    rec = {'name': name, 'train': r2_mae_rmse(train_Y, yhat_tr), 'heldout': r2_mae_rmse(hold_Y, yhat),
           'solver': 'zscore_train_only + ridge=1.0 linear (no intercept penalty)'}
    rec['heldout_R2_mean'] = rec['heldout']['R2_mean']
    rec['heldout_MAE_mean'] = rec['heldout']['MAE_mean']
    return rec, model, yhat


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ['representations/curve_level', 'representations/summary_level',
                'probes/centroid', 'probes/bbox', 'probes/endpoint', 'probes/normal', 'probes/cad_level',
                'controls/zero', 'controls/shuffle', 'outlier_cadfs__00982874']:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    train_rec = load_index(TRAIN_INDEX)
    hold_rec = load_index(HOLD_INDEX)
    if len(train_rec) != 100 or len(hold_rec) != 25:
        raise RuntimeError('frozen cohort count mismatch')
    train_cads = load_split(train_rec)
    hold_cads = load_split(hold_rec)
    dump(OUT / 'config.json', {
        'EXPERIMENT': 'PLACEMENT_SIGNAL_PROPAGATION_DIAGNOSTIC_V1',
        'TRAIN': 'train100', 'EVAL': 'heldout25',
        'M2_PLACEMENT_CHECKPOINT': str(M2P_CKPT),
        'OLD_M2_CHECKPOINT': str(OLD_M2_CKPT),
        'C2_FROZEN': True, 'LLM_RETRAINED': False, 'V3_TRAIN800': False,
        'probe': 'train-only z-score + ridge=1.0 linear with intercept; CAD-level uses flatten 8x2048 then PCA(32) fit on train100 then same ridge linear',
        'summary_hook': 'real GeometryPrefixAdapter from checkpoint; KCAP=128 pad+mask identical to training',
        'seed': SEED,
        'KCAP': KCAP,
    })

    print('PHASE D1 integrity...', flush=True)
    integrity = []
    for cad in train_cads + hold_cads:
        rebuilt, _ = descmod.build_placement_descriptor(pathlib.Path(cad['oracle_dir']))
        saved = cad['D']
        err = np.abs(rebuilt.astype(np.float64) - saved.astype(np.float64))
        integrity.append({
            'cad_id': cad['cad_id'],
            'maxabs': float(err.max()),
            'mae_centroid': float(err[:, 0:3].mean()),
            'mae_extent': float(err[:, 3:6].mean()),
            'mae_endpoint': float(err[:, 6:12].mean()),
            'mae_normal': float(err[:, 13:16].mean()),
            'mae_mask': float(err[:, [12, 16]].mean()),
        })
    integ = {
        'n': len(integrity),
        'maxabs_all': max(x['maxabs'] for x in integrity),
        'centroid_MAE': float(np.mean([x['mae_centroid'] for x in integrity])),
        'bbox_extent_MAE': float(np.mean([x['mae_extent'] for x in integrity])),
        'endpoint_MAE': float(np.mean([x['mae_endpoint'] for x in integrity])),
        'normal_MAE': float(np.mean([x['mae_normal'] for x in integrity])),
        'PASS': max(x['maxabs'] for x in integrity) < 1e-5,
    }
    dump(OUT / 'probes/DESCRIPTOR_FIELD_INTEGRITY.json', {'summary': integ, 'records': integrity})
    if not integ['PASS']:
        dump(OUT / 'PLACEMENT_SIGNAL_DIAGNOSTIC.json', {
            'FINAL_DIAGNOSIS': 'DESCRIPTOR_CONSTRUCTION_OR_STORAGE_BUG',
            'FINAL_GATE': 'PLACEMENT_PIPELINE_MULTIPLE_FAILURES',
            'integrity': integ,
        })
        raise SystemExit('DESCRIPTOR_CONSTRUCTION_OR_STORAGE_BUG')

    # PHASE D2 variance
    all_D = np.concatenate([c['D'] for c in train_cads + hold_cads], axis=0).astype(np.float64)
    dim_stats = []
    zero_var = []
    near_zero = []
    names = []
    for name, a, b in FIELDS:
        for j, axis in enumerate(['x', 'y', 'z'][: b - a] if b - a > 1 else ['']):
            col = a + j
            label = name if b - a == 1 else f'{name}_{axis}'
            names.append(label)
            s = all_D[:, col]
            rec = {
                'dim': col, 'name': label,
                'mean': float(s.mean()), 'std': float(s.std()),
                'min': float(s.min()), 'max': float(s.max()),
                'P01': float(np.quantile(s, 0.01)), 'P50': float(np.quantile(s, 0.50)), 'P99': float(np.quantile(s, 0.99)),
                'nan': int(np.isnan(s).sum()), 'inf': int(np.isinf(s).sum()),
            }
            dim_stats.append(rec)
            if rec['std'] < 1e-12:
                zero_var.append(label)
            elif rec['std'] < 1e-4:
                near_zero.append(label)
    variance = {
        'n_curves_train_heldout': int(all_D.shape[0]),
        'per_dimension': dim_stats,
        'zero_variance_dimensions': zero_var,
        'near_zero_variance_dimensions': near_zero,
        'centroid_xyz_std': [float(all_D[:, i].std()) for i in range(3)],
        'bbox_extent_xyz_std': [float(all_D[:, i].std()) for i in range(3, 6)],
        'endpoint_A_xyz_std': [float(all_D[:, i].std()) for i in range(6, 9)],
        'endpoint_B_xyz_std': [float(all_D[:, i].std()) for i in range(9, 12)],
        'plane_normal_std': [float(all_D[:, i].std()) for i in range(13, 16)],
        'endpoint_mask_positive_rate': float((all_D[:, 12] >= 0.5).mean()),
        'plane_mask_positive_rate': float((all_D[:, 16] >= 0.5).mean()),
        'NaN': int(np.isnan(all_D).sum()),
        'Inf': int(np.isinf(all_D).sum()),
    }
    dump(OUT / 'probes/DESCRIPTOR_VARIANCE.json', variance)

    device = torch.device('cpu')
    mlp = PlacementMLP()
    mlp.load_state_dict(torch.load(M2P_CKPT / 'placement_mlp.pt', map_location='cpu', weights_only=True))
    mlp.eval()
    adapter_place = GeometryPrefixAdapter(256, 2048, target_norm=TARGET_NORM)
    adapter_place.load_state_dict(torch.load(M2P_CKPT / 'geometry_prefix_adapter.pt', map_location='cpu', weights_only=True))
    adapter_place.eval()
    adapter_old = GeometryPrefixAdapter(256, 2048, target_norm=TARGET_NORM)
    adapter_old.load_state_dict(torch.load(OLD_M2_CKPT / 'geometry_prefix_adapter.pt', map_location='cpu', weights_only=True))
    adapter_old.eval()
    for p in list(mlp.parameters()) + list(adapter_place.parameters()) + list(adapter_old.parameters()):
        p.requires_grad_(False)

    print('export representations...', flush=True)
    tr_curve, tr_cad = export_split('train100', train_cads, mlp, adapter_place, adapter_old, OUT / 'representations')
    print('train100 exported', len(tr_curve), 'curves', flush=True)
    ho_curve, ho_cad = export_split('heldout25', hold_cads, mlp, adapter_place, adapter_old, OUT / 'representations')
    ho_shuf_curve, ho_shuf_cad = export_split('heldout25_shuffle', hold_cads, mlp, adapter_place, adapter_old, OUT / 'controls/shuffle', shuffle=True)
    ho_zero_curve, ho_zero_cad = export_split('heldout25_zero', hold_cads, mlp, adapter_place, adapter_old, OUT / 'controls/zero', zero=True)

    def residual_report(cads, tag):
        c = np.concatenate([x['c_norm'] for x in cads])
        p = np.concatenate([x['p_norm'] for x in cads])
        e = np.concatenate([x['e_norm'] for x in cads])
        r = np.concatenate([x['ratio'] for x in cads])
        cos = np.concatenate([x['cosine'] for x in cads])
        return {
            'split': tag,
            '||C2||': stats_1d(c),
            '||P||': stats_1d(p),
            '||C2+P||': stats_1d(e),
            '||P||/||C2||': stats_1d(r),
            'cosine(C2,P)': stats_1d(cos),
        }

    residual = {
        'train100': residual_report(tr_cad, 'train100'),
        'heldout25': residual_report(ho_cad, 'heldout25'),
        'per_cad_heldout': [
            {'cad_id': x['cad_id'], 'mean_ratio': float(x['ratio'].mean()), 'max_ratio': float(x['ratio'].max()),
             'mean_c': float(x['c_norm'].mean()), 'mean_p': float(x['p_norm'].mean())}
            for x in ho_cad
        ],
    }
    dump(OUT / 'RESIDUAL_RATIO_DISTRIBUTION.json', residual)

    # Curve-level probes
    tr_C, tr_P, tr_E, tr_D = stack_curves(tr_curve, 'C'), stack_curves(tr_curve, 'P'), stack_curves(tr_curve, 'E'), stack_curves(tr_curve, 'D')
    ho_C, ho_P, ho_E, ho_D = stack_curves(ho_curve, 'C'), stack_curves(ho_curve, 'P'), stack_curves(ho_curve, 'E'), stack_curves(ho_curve, 'D')
    sh_E = stack_curves(ho_shuf_curve, 'E')
    z_E, z_P = stack_curves(ho_zero_curve, 'E'), stack_curves(ho_zero_curve, 'P')

    def run_target(slice_, mask_tr=None, mask_ho=None, label='xyz'):
        Ytr = tr_D[:, slice_]
        Yho = ho_D[:, slice_]
        if mask_tr is not None:
            Ytr = Ytr[mask_tr]
            Xspec = {
                'C2_ONLY': (tr_C[mask_tr], ho_C[mask_ho], Ytr, Yho[mask_ho] if False else ho_D[:, slice_][mask_ho]),
            }
        reps = {
            'C2_ONLY': (tr_C, ho_C),
            'PLACEMENT_RESIDUAL_ONLY': (tr_P, ho_P),
            'C2_PLUS_PLACEMENT': (tr_E, ho_E),
        }
        if mask_tr is not None:
            Ytr_m = tr_D[mask_tr][:, slice_]
            Yho_m = ho_D[mask_ho][:, slice_]
            out = {}
            for k, (Xtr, Xho) in reps.items():
                rec, _, _ = probe_xyz(Xtr[mask_tr], Ytr_m, Xho[mask_ho], Yho_m, k)
                out[k] = rec
            return out
        out = {}
        for k, (Xtr, Xho) in reps.items():
            rec, W, yhat = probe_xyz(Xtr, Ytr, Xho, Yho, k)
            out[k] = rec
        rec_sh, _, _ = probe_xyz(tr_E, Ytr, sh_E, Yho, 'SHUFFLE_E')
        rec_z, _, _ = probe_xyz(tr_E, Ytr, z_E, Yho, 'ZERO_E')
        out['SHUFFLED_DESCRIPTOR'] = rec_sh
        out['ZERO_DESCRIPTOR'] = rec_z
        return out

    tr_ep = tr_D[:, 12] >= 0.5
    ho_ep = ho_D[:, 12] >= 0.5
    tr_pl = tr_D[:, 16] >= 0.5
    ho_pl = ho_D[:, 16] >= 0.5

    centroid = run_target(slice(0, 3))
    bbox = run_target(slice(3, 6))
    endA = run_target(slice(6, 9), tr_ep, ho_ep) if tr_ep.sum() >= 10 and ho_ep.sum() >= 3 else {'note': 'insufficient open curves'}
    endB = run_target(slice(9, 12), tr_ep, ho_ep) if tr_ep.sum() >= 10 and ho_ep.sum() >= 3 else {'note': 'insufficient open curves'}
    normal = run_target(slice(13, 16), tr_pl, ho_pl) if tr_pl.sum() >= 10 and ho_pl.sum() >= 3 else {'note': 'insufficient plane curves'}
    dump(OUT / 'probes/centroid/LINEAR_PROBE.json', centroid)
    dump(OUT / 'probes/bbox/LINEAR_PROBE.json', bbox)
    dump(OUT / 'probes/endpoint/LINEAR_PROBE.json', {'endpoint_A': endA, 'endpoint_B': endB, 'train_open': int(tr_ep.sum()), 'heldout_open': int(ho_ep.sum())})
    dump(OUT / 'probes/normal/LINEAR_PROBE.json', {'probe': normal, 'train_plane': int(tr_pl.sum()), 'heldout_plane': int(ho_pl.sum())})

    Ytr_c = tr_D[:, 0:3]
    Yho_c = ho_D[:, 0:3]
    _, model_p, _ = probe_xyz(tr_P, Ytr_c, ho_P, Yho_c, 'P')
    transfer = {
        'note': 'W fitted on PlacementMLP residual -> centroid (train100 only), applied to other reps without refitting',
        'on_residual': r2_mae_rmse(Yho_c, pred_linear(model_p, ho_P)),
        'on_enhanced': r2_mae_rmse(Yho_c, pred_linear(model_p, ho_E)),
        'on_c2': r2_mae_rmse(Yho_c, pred_linear(model_p, ho_C)),
        'on_shuffled_enhanced': r2_mae_rmse(Yho_c, pred_linear(model_p, sh_E)),
        'on_zero_enhanced': r2_mae_rmse(Yho_c, pred_linear(model_p, z_E)),
    }
    dump(OUT / 'probes/centroid/TRANSFER_RESIDUAL_READOUT.json', transfer)

    def fit_mlp_probe(Xtr, Ytr, Xho, Yho, name):
        torch.manual_seed(SEED)
        mu = Xtr.mean(axis=0)
        std = np.where(Xtr.std(axis=0) < 1e-8, 1.0, Xtr.std(axis=0))
        net = nn.Sequential(nn.Linear(int(Xtr.shape[1]), 32), nn.ReLU(), nn.Linear(32, int(Ytr.shape[1])))
        opt = torch.optim.Adam(net.parameters(), lr=1e-2)
        xt = torch.from_numpy(((Xtr - mu) / std).astype(np.float32))
        yt = torch.from_numpy(np.asarray(Ytr, dtype=np.float32))
        xh = torch.from_numpy(((Xho - mu) / std).astype(np.float32))
        net.train()
        for _ in range(500):
            opt.zero_grad()
            loss = ((net(xt) - yt) ** 2).mean()
            loss.backward()
            opt.step()
        with torch.no_grad():
            yhat_tr = net(xt).numpy()
            yhat = net(xh).numpy()
        rec = {
            'name': name,
            'train': r2_mae_rmse(Ytr, yhat_tr),
            'heldout': r2_mae_rmse(Yho, yhat),
            'solver': '2-layer MLP din-32-ReLU-dout, Adam 500 steps, train-only zscore',
        }
        rec['heldout_R2_mean'] = rec['heldout']['R2_mean']
        rec['heldout_MAE_mean'] = rec['heldout']['MAE_mean']
        return rec

    mlp_centroid = {
        'C2_ONLY': fit_mlp_probe(tr_C, Ytr_c, ho_C, Yho_c, 'C2_ONLY'),
        'PLACEMENT_RESIDUAL_ONLY': fit_mlp_probe(tr_P, Ytr_c, ho_P, Yho_c, 'PLACEMENT_RESIDUAL_ONLY'),
        'C2_PLUS_PLACEMENT': fit_mlp_probe(tr_E, Ytr_c, ho_E, Yho_c, 'C2_PLUS_PLACEMENT'),
        'SHUFFLED_DESCRIPTOR': fit_mlp_probe(tr_E, Ytr_c, sh_E, Yho_c, 'SHUFFLE_E'),
        'ZERO_DESCRIPTOR': fit_mlp_probe(tr_E, Ytr_c, z_E, Yho_c, 'ZERO_E'),
    }
    dump(OUT / 'probes/centroid/MLP_PROBE.json', mlp_centroid)

    # rebuild Y from original D (not shuffled / zeroed D)
    tr_Ycad = np.stack([cad_placement_target(x['D_original']) for x in tr_cad], 0)
    ho_Ycad = np.stack([cad_placement_target(x['D_original']) for x in ho_cad], 0)
    dump(OUT / 'probes/cad_level/CAD_TARGET_VARIANCE.json', {
        'target': '12-D centroid mean/std/min/max xyz',
        'train100_std': [float(v) for v in tr_Ycad.std(axis=0)],
        'heldout25_std': [float(v) for v in ho_Ycad.std(axis=0)],
        'train100_mean': [float(v) for v in tr_Ycad.mean(axis=0)],
        'heldout25_mean': [float(v) for v in ho_Ycad.mean(axis=0)],
        'note': 'After CAD-center normalization, CENTROID_MEAN often has small variance; MIN/MAX are the more informative CAD-level placement stats.',
    })
    CAD_GROUPS = [('CENTROID_MEAN', 0, 3), ('CENTROID_STD', 3, 6), ('CENTROID_MIN', 6, 9), ('CENTROID_MAX', 9, 12)]

    def group_metrics(rec):
        r2 = rec['heldout']['R2']
        mae = rec['heldout']['MAE']
        return {name: {'R2_mean': float(np.mean(r2[a:b])), 'MAE_mean': float(np.mean(mae[a:b]))} for name, a, b in CAD_GROUPS}

    tr_Xold = np.stack([x['S_old'].reshape(-1) for x in tr_cad], 0)
    tr_Xpl = np.stack([x['S_place'].reshape(-1) for x in tr_cad], 0)
    ho_Xold = np.stack([x['S_old'].reshape(-1) for x in ho_cad], 0)
    ho_Xpl = np.stack([x['S_place'].reshape(-1) for x in ho_cad], 0)
    ho_Xpl_sh = np.stack([x['S_place'].reshape(-1) for x in ho_shuf_cad], 0)
    ho_Xpl_z = np.stack([x['S_place'].reshape(-1) for x in ho_zero_cad], 0)
    mu, comp = fit_pca(tr_Xpl, 32)
    mu_old, comp_old = fit_pca(tr_Xold, 32)
    cad_probe = {}
    for name, Xtr_raw, Xho_raw, mu_, comp_ in [
        ('OLD_M2_SUMMARY', tr_Xold, ho_Xold, mu_old, comp_old),
        ('M2_PLACEMENT_SUMMARY', tr_Xpl, ho_Xpl, mu, comp),
        ('M2_PLACEMENT_SUMMARY_SHUFFLE', tr_Xpl, ho_Xpl_sh, mu, comp),
        ('M2_PLACEMENT_SUMMARY_ZERO', tr_Xpl, ho_Xpl_z, mu, comp),
    ]:
        rec, _, _ = probe_xyz(apply_pca(Xtr_raw, mu_, comp_), tr_Ycad, apply_pca(Xho_raw, mu_, comp_), ho_Ycad, name)
        rec_mp, _, _ = probe_xyz(
            Xtr_raw.reshape(len(Xtr_raw), 8, 2048).mean(axis=1),
            tr_Ycad,
            Xho_raw.reshape(len(Xho_raw), 8, 2048).mean(axis=1),
            ho_Ycad,
            name + '_MEANPOOL',
        )
        cad_probe[name] = {
            'flatten_pca32': rec,
            'flatten_pca32_groups': group_metrics(rec),
            'meanpool': rec_mp,
            'target': '12-D CAD centroid mean/std/min/max xyz',
        }
    dump(OUT / 'probes/cad_level/SUMMARY_PROBE.json', cad_probe)

    # PHASE I summary delta
    deltas = []
    for a, b in zip(ho_cad, ho_cad):
        s0 = a['S_old'].astype(np.float64)
        s1 = a['S_place'].astype(np.float64)
        l2 = float(np.linalg.norm(s1 - s0))
        rel = l2 / max(float(np.linalg.norm(s0)), 1e-12)
        cos = float(np.dot(s0.reshape(-1), s1.reshape(-1)) / max(np.linalg.norm(s0) * np.linalg.norm(s1), 1e-12))
        deltas.append({'cad_id': a['cad_id'], 'L2': l2, 'relative_L2': rel, 'cosine': cos})
    delta_sum = {
        'L2': stats_1d([d['L2'] for d in deltas]),
        'relative_L2': stats_1d([d['relative_L2'] for d in deltas]),
        'cosine': stats_1d([d['cosine'] for d in deltas]),
        'per_cad': deltas,
    }
    dump(OUT / 'probes/cad_level/OLD_VS_PLACEMENT_SUMMARY_DELTA.json', delta_sum)

    # Outlier
    oid = 'cadfs__00982874'
    outl = next(x for x in ho_cad if x['cad_id'] == oid)
    old_dsl = (OLD_M2_DEC / 'predictions' / oid / 'pred_raw.txt').read_text()
    new_dsl = (M2P_DEC / 'predictions' / oid / 'pred_raw.txt').read_text()
    gt_dsl = (GT_DSL / oid / 'target' / 'cad_target.dsl').read_text()
    s0 = outl['S_old'].astype(np.float64)
    s1 = outl['S_place'].astype(np.float64)
    outlier = {
        'cad_id': oid,
        'n_curves': outl['n_curves'],
        'mean_||C2||': float(outl['c_norm'].mean()),
        'mean_||P||': float(outl['p_norm'].mean()),
        'max_||P||': float(outl['p_norm'].max()),
        'mean_residual_ratio': float(outl['ratio'].mean()),
        'max_residual_ratio': float(outl['ratio'].max()),
        'summary_L2': float(np.linalg.norm(s1 - s0)),
        'summary_relative_L2': float(np.linalg.norm(s1 - s0) / max(np.linalg.norm(s0), 1e-12)),
        'summary_cosine': float(np.dot(s0.reshape(-1), s1.reshape(-1)) / max(np.linalg.norm(s0) * np.linalg.norm(s1), 1e-12)),
        'dsl_text_equal': old_dsl.strip() == new_dsl.strip(),
        'old_ops': [ln.strip() for ln in old_dsl.splitlines() if '=' in ln],
        'placement_ops': [ln.strip() for ln in new_dsl.splitlines() if '=' in ln],
        'gt_ops': [ln.strip() for ln in gt_dsl.splitlines() if '=' in ln],
        'operation_diff': {
            'old_n_ops': sum(1 for ln in old_dsl.splitlines() if 'Extrude' in ln or 'Union' in ln),
            'placement_n_ops': sum(1 for ln in new_dsl.splitlines() if 'Extrude' in ln or 'Union' in ln),
            'gt_has_union': 'Union' in gt_dsl,
            'old_has_union': 'Union' in old_dsl,
            'placement_has_union': 'Union' in new_dsl,
            'same_operation_family': ('ExtrudePolygon' in old_dsl) == ('ExtrudePolygon' in new_dsl),
            'axis_changed': ('axis=(0, 0, 1)' in old_dsl) != ('axis=(0, 0, 1)' in new_dsl) or ('axis=(1, 0, 0)' in old_dsl) != ('axis=(1, 0, 0)' in new_dsl),
        },
        'old_dsl': old_dsl,
        'placement_dsl': new_dsl,
        'gt_dsl': gt_dsl,
        'dsl_change': old_dsl.strip() != new_dsl.strip(),
        'note': 'Do not repair this case. Old M2 already failed GT Union-of-two-polygons; Placement switched to a different ExtrudePolygon, Chamfer 0.039->0.343.',
    }
    dump(OUT / 'outlier_cadfs__00982874/OUTLIER.json', outlier)

    c2_r2 = centroid['C2_ONLY']['heldout_R2_mean']
    p_r2 = centroid['PLACEMENT_RESIDUAL_ONLY']['heldout_R2_mean']
    e_r2 = centroid['C2_PLUS_PLACEMENT']['heldout_R2_mean']
    old_s_r2 = cad_probe['OLD_M2_SUMMARY']['flatten_pca32']['heldout_R2_mean']
    pl_s_r2 = cad_probe['M2_PLACEMENT_SUMMARY']['flatten_pca32']['heldout_R2_mean']
    sh_r2 = centroid['SHUFFLED_DESCRIPTOR']['heldout_R2_mean']
    z_r2 = centroid['ZERO_DESCRIPTOR']['heldout_R2_mean']
    mean_ratio = residual['heldout25']['||P||/||C2||']['mean']
    transfer_e_r2 = transfer['on_enhanced']['R2_mean']
    transfer_sh_r2 = transfer['on_shuffled_enhanced']['R2_mean']
    mlp_e_r2 = mlp_centroid['C2_PLUS_PLACEMENT']['heldout_R2_mean']
    mlp_p_r2 = mlp_centroid['PLACEMENT_RESIDUAL_ONLY']['heldout_R2_mean']
    old_g = cad_probe['OLD_M2_SUMMARY']['flatten_pca32_groups']
    pl_g = cad_probe['M2_PLACEMENT_SUMMARY']['flatten_pca32_groups']
    old_layout_r2 = float(np.mean([old_g['CENTROID_MIN']['R2_mean'], old_g['CENTROID_MAX']['R2_mean']]))
    pl_layout_r2 = float(np.mean([pl_g['CENTROID_MIN']['R2_mean'], pl_g['CENTROID_MAX']['R2_mean']]))

    present_desc = bool(np.mean(variance['centroid_xyz_std']) > 1e-4 and integ['PASS'])
    present_res = p_r2 >= HIGH
    present_add = e_r2 >= HIGH
    present_sum = (pl_layout_r2 - old_layout_r2) >= 0.10 and pl_layout_r2 >= HIGH

    failures = []
    if not present_desc:
        failures.append('DESCRIPTOR')
    if not present_res:
        failures.append('PlacementMLP residual')
    if present_res and (not present_add) and (e_r2 + 0.15 < p_r2):
        failures.append('C2 additive fusion')
    if (present_add or transfer_e_r2 >= HIGH) and not present_sum:
        failures.append('8-token summary')

    if not present_desc:
        first = 'DESCRIPTOR'
        gate = 'PLACEMENT_PIPELINE_MULTIPLE_FAILURES'
    elif not present_res:
        first = 'PlacementMLP residual'
        gate = 'PLACEMENT_ENCODER_NOT_ENCODING_SIGNAL'
    elif present_res and (not present_add) and e_r2 + 0.15 < p_r2:
        first = 'C2 additive fusion'
        gate = 'PLACEMENT_SIGNAL_DROWNED_BY_C2'
        if not present_sum:
            gate = 'PLACEMENT_PIPELINE_MULTIPLE_FAILURES'
            failures = ['C2 additive fusion', '8-token summary']
    elif present_add and not present_sum:
        first = '8-token summary'
        gate = 'PLACEMENT_SIGNAL_LOST_IN_SUMMARY'
    elif present_sum:
        first = 'decoder / DSL supervision (signal still in summary)'
        gate = 'PLACEMENT_SIGNAL_PRESENT_BUT_DECODER_NOT_USING_IT'
    else:
        first = 'multiple'
        gate = 'PLACEMENT_PIPELINE_MULTIPLE_FAILURES'

    extra = []
    if present_res and mean_ratio < 0.01:
        extra.append('RESIDUAL_RATIO_VERY_SMALL')
    if abs(e_r2 - c2_r2) < 0.05 and p_r2 >= HIGH:
        extra.append('ADDITIVE_FUSION_SIGNAL_DOMINATED')
    if abs(sh_r2 - e_r2) < 0.05:
        extra.append('SHUFFLE_CONTROL_NEARLY_IDENTICAL_TO_CORRECT')
    if transfer_e_r2 >= HIGH and (not present_add):
        extra.append('RESIDUAL_READOUT_SURVIVES_ADDITION_BUT_FROM_SCRATCH_E_PROBE_FAILS')
    if abs(pl_layout_r2 - old_layout_r2) < 0.05:
        extra.append('SUMMARY_PLACEMENT_PROBE_NO_GAIN_VS_OLD_M2')
    ratio_stats = residual['heldout25']['||P||/||C2||']
    if ratio_stats['p90'] < 0.01 and ratio_stats['mean'] < 0.01:
        extra.append('RESIDUAL_RATIO_UNIVERSAL_NOT_OUTLIER_DRIVEN')

    report = {
        'CURRENT_GATE': gate,
        'TRAIN_CAD_COUNT': 100,
        'HELDOUT_CAD_COUNT': 25,
        'TRAIN_CURVE_COUNT': len(tr_curve),
        'HELDOUT_CURVE_COUNT': len(ho_curve),
        'DESCRIPTOR_FIELD_INTEGRITY': 'PASS' if integ['PASS'] else 'FAIL',
        'DESCRIPTOR_ZERO_VARIANCE_DIMS': zero_var,
        'CENTROID_DESCRIPTOR_STD': variance['centroid_xyz_std'],
        'C2_ONLY_CENTROID_R2': c2_r2,
        'PLACEMENT_RESIDUAL_CENTROID_R2': p_r2,
        'ENHANCED_TOKEN_CENTROID_R2': e_r2,
        'C2_ONLY_CENTROID_MAE': centroid['C2_ONLY']['heldout_MAE_mean'],
        'PLACEMENT_RESIDUAL_CENTROID_MAE': centroid['PLACEMENT_RESIDUAL_ONLY']['heldout_MAE_mean'],
        'ENHANCED_TOKEN_CENTROID_MAE': centroid['C2_PLUS_PLACEMENT']['heldout_MAE_mean'],
        'centroid_detail': {
            'C2_ONLY': centroid['C2_ONLY']['heldout'],
            'PLACEMENT_RESIDUAL_ONLY': centroid['PLACEMENT_RESIDUAL_ONLY']['heldout'],
            'C2_PLUS_PLACEMENT': centroid['C2_PLUS_PLACEMENT']['heldout'],
        },
        'TRANSFER_RESIDUAL_READOUT_ON_ENHANCED_R2': transfer_e_r2,
        'TRANSFER_RESIDUAL_READOUT_ON_SHUFFLE_R2': transfer_sh_r2,
        'MLP_RESIDUAL_CENTROID_R2': mlp_p_r2,
        'MLP_ENHANCED_CENTROID_R2': mlp_e_r2,
        'OLD_M2_SUMMARY_PLACEMENT_R2': old_s_r2,
        'M2_PLACEMENT_SUMMARY_PLACEMENT_R2': pl_s_r2,
        'OLD_M2_SUMMARY_LAYOUT_R2': old_layout_r2,
        'M2_PLACEMENT_SUMMARY_LAYOUT_R2': pl_layout_r2,
        'OLD_M2_SUMMARY_GROUPS': old_g,
        'M2_PLACEMENT_SUMMARY_GROUPS': pl_g,
        'MEAN_C2_NORM': residual['heldout25']['||C2||']['mean'],
        'MEAN_PLACEMENT_RESIDUAL_NORM': residual['heldout25']['||P||']['mean'],
        'MEAN_RESIDUAL_RATIO': mean_ratio,
        'MEDIAN_RESIDUAL_RATIO': residual['heldout25']['||P||/||C2||']['median'],
        'P90_RESIDUAL_RATIO': residual['heldout25']['||P||/||C2||']['p90'],
        'CORRECT_DESCRIPTOR_PROBE': e_r2,
        'SHUFFLED_DESCRIPTOR_PROBE': sh_r2,
        'ZERO_DESCRIPTOR_PROBE': z_r2,
        'OUTLIER_00982874_RESIDUAL_RATIO': outlier['mean_residual_ratio'],
        'OUTLIER_00982874_SUMMARY_DELTA': outlier['summary_relative_L2'],
        'OUTLIER_00982874_DSL_CHANGE': outlier['dsl_change'],
        'PLACEMENT_SIGNAL_PRESENT_IN_DESCRIPTOR': present_desc,
        'PLACEMENT_SIGNAL_PRESENT_IN_RESIDUAL': present_res,
        'PLACEMENT_SIGNAL_PRESENT_AFTER_ADDITION': present_add,
        'PLACEMENT_SIGNAL_PRESENT_AFTER_8TOKEN_SUMMARY': present_sum,
        'FIRST_FAILURE_STAGE': first,
        'FAILURES': failures,
        'FINAL_GATE': gate,
        'EXTRA_FLAGS': extra,
        'integrity': integ,
        'levels': {
            'C2_ONLY': level(c2_r2),
            'RESIDUAL': level(p_r2),
            'ENHANCED': level(e_r2),
            'OLD_SUMMARY': level(old_s_r2),
            'PLACE_SUMMARY': level(pl_s_r2),
        },
        'V3_TRAIN800_STARTED': False,
        'MODEL_STRUCTURE_CHANGED': False,
        'C2_UNFROZEN': False,
        'PROBE_SOLVER': 'zscore_train_only + ridge=1.0',
    }
    dump(OUT / 'PLACEMENT_SIGNAL_DIAGNOSTIC.json', report)

    md = []
    md.append('# Placement Signal Propagation Diagnostic V1\n')
    md.append(f'FINAL_GATE=`{gate}`\n')
    md.append(f'FIRST_FAILURE_STAGE=`{first}`\n')
    md.append('\n## Frozen cohort\n')
    md.append(f'- train CAD={len(tr_cad)} curves={len(tr_curve)}\n- heldout CAD={len(ho_cad)} curves={len(ho_curve)}\n')
    md.append('\n## Descriptor integrity\n')
    md.append(f'- field integrity `{integ["PASS"]}` maxabs={integ["maxabs_all"]:.3e}\n')
    md.append(f'- centroid std {variance["centroid_xyz_std"]}\n- zero-var dims {zero_var}\n')
    md.append('\n## Curve-level centroid probe (fit train100, eval heldout25; ridge=1.0 z-scored linear)\n')
    md.append('| rep | R2_mean | MAE_mean |\n|---|---:|---:|\n')
    for k in ['C2_ONLY', 'PLACEMENT_RESIDUAL_ONLY', 'C2_PLUS_PLACEMENT']:
        md.append(f'| {k} | {centroid[k]["heldout_R2_mean"]:.4f} | {centroid[k]["heldout_MAE_mean"]:.6f} |\n')
    md.append(f'| SHUFFLE | {sh_r2:.4f} | {centroid["SHUFFLED_DESCRIPTOR"]["heldout_MAE_mean"]:.6f} |\n')
    md.append(f'| ZERO | {z_r2:.4f} | {centroid["ZERO_DESCRIPTOR"]["heldout_MAE_mean"]:.6f} |\n')
    md.append('\n## Other curve-level targets (ridge linear, heldout R2_mean)\n')
    md.append('| target | C2 | residual | enhanced |\n|---|---:|---:|---:|\n')
    md.append(f'| bbox_extent | {bbox["C2_ONLY"]["heldout_R2_mean"]:.4f} | {bbox["PLACEMENT_RESIDUAL_ONLY"]["heldout_R2_mean"]:.4f} | {bbox["C2_PLUS_PLACEMENT"]["heldout_R2_mean"]:.4f} |\n')
    if 'C2_ONLY' in endA:
        md.append(f'| endpoint_A | {endA["C2_ONLY"]["heldout_R2_mean"]:.4f} | {endA["PLACEMENT_RESIDUAL_ONLY"]["heldout_R2_mean"]:.4f} | {endA["C2_PLUS_PLACEMENT"]["heldout_R2_mean"]:.4f} |\n')
        md.append(f'| endpoint_B | {endB["C2_ONLY"]["heldout_R2_mean"]:.4f} | {endB["PLACEMENT_RESIDUAL_ONLY"]["heldout_R2_mean"]:.4f} | {endB["C2_PLUS_PLACEMENT"]["heldout_R2_mean"]:.4f} |\n')
    if isinstance(normal, dict) and 'C2_ONLY' in normal:
        md.append(f'| plane_normal | {normal["C2_ONLY"]["heldout_R2_mean"]:.4f} | {normal["PLACEMENT_RESIDUAL_ONLY"]["heldout_R2_mean"]:.4f} | {normal["C2_PLUS_PLACEMENT"]["heldout_R2_mean"]:.4f} |\n')
    md.append('\nMLP centroid: residual R2=' + f'{mlp_p_r2:.4f}, enhanced R2={mlp_e_r2:.4f}.\n')
    md.append('\n## Residual magnitude (heldout25 curves)\n')
    md.append(f'- mean ||C2||={report["MEAN_C2_NORM"]:.4f}\n- mean ||P||={report["MEAN_PLACEMENT_RESIDUAL_NORM"]:.6f}\n')
    md.append(f'- mean ratio={mean_ratio:.6f} median={report["MEDIAN_RESIDUAL_RATIO"]:.6f} P90={report["P90_RESIDUAL_RATIO"]:.6f}\n')
    md.append('\n## 8-token summary CAD-level probe\n')
    md.append(f'- OLD_M2 12-D R2={old_s_r2:.4f} layout(min/max) R2={old_layout_r2:.4f}\n')
    md.append(f'- M2-Placement 12-D R2={pl_s_r2:.4f} layout(min/max) R2={pl_layout_r2:.4f}\n')
    md.append(f'- summary cosine mean={delta_sum["cosine"]["mean"]:.6f} relative L2 mean={delta_sum["relative_L2"]["mean"]:.6f}\n')
    md.append('\n## Outlier cadfs__00982874\n')
    md.append(f'- residual ratio mean={outlier["mean_residual_ratio"]:.6f}\n- summary rel L2={outlier["summary_relative_L2"]:.6f}\n- DSL changed={outlier["dsl_change"]}\n')
    md.append('\nOld M2 and Placement both fail GT Union; Placement jumped to a different ExtrudePolygon (axis z vs x).\n')
    md.append('\n## Answer\n')
    md.append(f'Placement information first fails at: **{first}**.\n')
    md.append(f'FINAL_GATE=`{gate}` failures={failures}\n')
    (OUT / 'PLACEMENT_SIGNAL_DIAGNOSTIC.md').write_text(''.join(md))
    (OUT / 'FINAL_REPORT.md').write_text(''.join(md))
    print(json.dumps({k: report[k] for k in report if k not in ('centroid_detail', 'integrity')}, indent=2))


if __name__ == '__main__':
    main()
