#!/usr/bin/env python3
"""CADFS_NOISY_OVERFIT100_V1 -- asset-only Noise Canary10.

This script deliberately does not load a model, execute a decoder, or alter
the frozen CADFS converter/screening outputs.  It creates an isolated visual
and numerical qualification of a deterministic mesh-noise protocol.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OLD = ROOT / 'ours3/cadfs_overfit100_v1/geometry_supervision_audit_v1'
OUT = ROOT / 'ours3/cadfs_noisy_overfit100_v1'
ORDER = OLD / 'CADFS_GEOMETRY_VERIFIED_ORDER.json'
SUBSET = OLD / 'CADFS_GEOMETRY_VERIFIED_SUBSET.json'
GLOBAL_SEED = 42
LEVELS = {'N0': 0.0, 'N1': 0.001, 'N2': 0.002, 'N3': 0.005}
SURFACE_N = 8192
VIS_N = 5000
SMOOTHING_ROUNDS = 2

sys.path[:0] = [str(ROOT / 'scripts')]
from geometry_pack_v1.occ import tessellate_step
from geometry_pack_v1.surface import sample_surface_uniform, face_normals
from geometry_pack_v1.pack import apply_canonical
from deepcad.cad_canonical import compute_transform


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + '\n')


def seed_for(cad_id: str, level: str) -> int:
    return int.from_bytes(hashlib.sha256(f'{cad_id}|{level}|{GLOBAL_SEED}'.encode()).digest()[:8], 'little') % (2**63 - 1)


def obj_write(path: Path, v: np.ndarray, f: np.ndarray) -> None:
    with path.open('w') as out:
        out.write('# CADFS_NOISY_OVERFIT100_V1\n')
        for x, y, z in v:
            out.write(f'v {x:.12g} {y:.12g} {z:.12g}\n')
        for a, b, c in f:
            out.write(f'f {int(a)+1} {int(b)+1} {int(c)+1}\n')


def mesh_adjacency(nv: int, f: np.ndarray) -> list[np.ndarray]:
    bags = [set() for _ in range(nv)]
    for a, b, c in f:
        a, b, c = int(a), int(b), int(c)
        bags[a].update((b, c)); bags[b].update((a, c)); bags[c].update((a, b))
    return [np.fromiter(x, dtype=np.int64) for x in bags]


def vertex_normals(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    tri = v[f]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ans = np.zeros_like(v, dtype=np.float64)
    for j in range(3): np.add.at(ans, f[:, j], cross)
    norm = np.linalg.norm(ans, axis=1, keepdims=True)
    return np.divide(ans, norm, out=np.zeros_like(ans), where=norm > 1e-18)


def noisy_vertices(v: np.ndarray, f: np.ndarray, cad_id: str, level: str, diag: float, adjacency: list[np.ndarray]) -> tuple[np.ndarray, dict]:
    sigma = LEVELS[level] * diag
    if sigma == 0:
        return v.copy(), {'seed': seed_for(cad_id, level), 'sigma': 0.0, 'scalar_mean': 0.0, 'scalar_std': 0.0, 'clip': 0.0}
    rng = np.random.default_rng(seed_for(cad_id, level))
    scalar = rng.normal(0.0, 1.0, len(v)); scalar -= scalar.mean()
    for _ in range(SMOOTHING_ROUNDS):
        smooth = scalar.copy()
        for i, nbr in enumerate(adjacency):
            if len(nbr): smooth[i] = (scalar[i] + scalar[nbr].sum()) / (len(nbr) + 1)
        scalar = smooth
    scalar -= scalar.mean(); std = float(scalar.std())
    if std > 1e-18: scalar /= std
    delta = np.clip(scalar * sigma, -3 * sigma, 3 * sigma)
    out = v + delta[:, None] * vertex_normals(v, f)
    return out, {'seed': seed_for(cad_id, level), 'sigma': sigma, 'scalar_mean': float(delta.mean()), 'scalar_std': float(delta.std()), 'clip': 3 * sigma}


def area(v: np.ndarray, f: np.ndarray) -> float:
    t = v[f]; return float(.5 * np.linalg.norm(np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0]), axis=1).sum())


def components(nv: int, adjacency: list[np.ndarray]) -> int:
    seen = np.zeros(nv, bool); count = 0
    for s in range(nv):
        if seen[s]: continue
        count += 1; stack = [s]; seen[s] = True
        while stack:
            i = stack.pop()
            for j in adjacency[i]:
                if not seen[j]: seen[j] = True; stack.append(int(j))
    return count


def geometry_metrics(v0: np.ndarray, v1: np.ndarray, f: np.ndarray, cad_id: str, level: str, diag: float) -> dict:
    # Independent surface samples avoid exploiting identical vertex indices.
    a, na, _ = sample_surface_uniform(v0, f, VIS_N, seed_for(cad_id, 'clean_metric'))
    b, nb, _ = sample_surface_uniform(v1, f, VIS_N, seed_for(cad_id, level + '_metric'))
    da = cKDTree(b).query(a, k=1)[0]; db = cKDTree(a).query(b, k=1)[0]
    mn0, mx0, mn1, mx1 = v0.min(0), v0.max(0), v1.min(0), v1.max(0)
    return {
        'chamfer_rel': float((da.mean()+db.mean())*.5/max(diag, 1e-12)),
        'hausdorff95_rel': float(np.percentile(np.r_[da, db], 95)/max(diag, 1e-12)),
        'bbox_min_delta_rel': float(np.linalg.norm(mn1-mn0)/max(diag, 1e-12)),
        'bbox_max_delta_rel': float(np.linalg.norm(mx1-mx0)/max(diag, 1e-12)),
        'centroid_shift_rel': float(np.linalg.norm(v1.mean(0)-v0.mean(0))/max(diag, 1e-12)),
        'area_ratio': area(v1, f)/max(area(v0, f), 1e-18),
        'normal_angle_deg_median': float(np.degrees(np.arccos(np.clip((na*nb).sum(1), -1, 1))).mean()),
    }


def quantile(rows: list[dict], field: str) -> dict:
    a = [x['levels'][field]['metrics']['chamfer_rel'] for x in rows] if field else []
    return {'median': float(np.median(a)), 'p90': float(np.percentile(a, 90)), 'max': float(np.max(a))} if a else {}


def draw_gallery(rows: list[dict]) -> None:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(16, 3.3 * len(rows)))
    for ri, r in enumerate(rows):
        for ci, level in enumerate(('N0','N1','N2','N3')):
            d = r['levels'][level]; v = np.load(d['vertices_path']); f = np.load(r['faces_path'])
            ax = fig.add_subplot(len(rows), 4, ri*4+ci+1, projection='3d')
            # Same object coordinates and fixed camera for every column in row.
            ax.plot_trisurf(v[:,0],v[:,1],v[:,2],triangles=f, color='#7595b7' if level=='N0' else '#d86944', linewidth=0, alpha=.82, shade=True)
            lim = r['plot_limits']; ax.set_xlim(*lim[0]); ax.set_ylim(*lim[1]); ax.set_zlim(*lim[2]); ax.view_init(22,-52); ax.set_axis_off()
            title = f"{r['cad_id']} | {level} | sigma/D={LEVELS[level]:.3g}" if ci == 0 else f"{level} | sigma/D={LEVELS[level]:.3g}"
            ax.set_title(title, fontsize=7)
    fig.tight_layout(); fig.savefig(OUT/'noise_canary10/figures/GALLERY_10.png', dpi=180); plt.close(fig)
    # Deterministic representative closeups: first five frozen IDs, same fixed camera.
    fig = plt.figure(figsize=(16, 15))
    for ri, r in enumerate(rows[:5]):
        base = np.load(r['levels']['N0']['vertices_path']); f=np.load(r['faces_path'])
        center=(base.min(0)+base.max(0))/2; span=np.max(base.max(0)-base.min(0))*.30
        for ci, level in enumerate(('N0','N1','N2','N3')):
            v=np.load(r['levels'][level]['vertices_path']);ax=fig.add_subplot(5,4,ri*4+ci+1,projection='3d')
            ax.plot_trisurf(v[:,0],v[:,1],v[:,2],triangles=f,color='#7595b7' if level=='N0' else '#d86944',linewidth=0,alpha=.9,shade=True)
            ax.set_xlim(center[0]-span,center[0]+span);ax.set_ylim(center[1]-span,center[1]+span);ax.set_zlim(center[2]-span,center[2]+span);ax.view_init(25,-55);ax.set_axis_off();ax.set_title(f'{r["cad_id"]} {level}',fontsize=7)
    fig.tight_layout();fig.savefig(OUT/'noise_canary10/figures/GALLERY_CLOSEUP.png',dpi=180);plt.close(fig)


def choose(records: list[dict]) -> tuple[list[dict], dict]:
    # Deterministic, manifest-first complexity proxy: operation_count tertiles,
    # with stable source_id ordering; never based on any noisy result or visual.
    ordered = sorted(records, key=lambda r: r['source_id'])
    counts = np.asarray([int(r.get('operation_count', 0)) for r in ordered])
    q1, q2 = np.quantile(counts, [.33, .67])
    groups = {'LOW': [], 'MID': [], 'HIGH': []}
    for r in ordered:
        x = int(r.get('operation_count', 0)); g = 'LOW' if x <= q1 else ('MID' if x <= q2 else 'HIGH'); groups[g].append(r)
    selected=[]
    # Round-robin fully deterministic; duplicate group can occur under degenerate source complexity.
    pos={k:0 for k in groups}
    while len(selected)<10:
        changed=False
        for g in ('LOW','MID','HIGH'):
            if pos[g]<len(groups[g]) and len(selected)<10:
                selected.append(groups[g][pos[g]]);pos[g]+=1;changed=True
        if not changed: break
    return selected, {'algorithm':'source_id lexicographic order; operation_count tertile round-robin; selection occurs before all noise construction', 'q33':float(q1),'q67':float(q2),'group_sizes':{k:len(v) for k,v in groups.items()}}


def main() -> None:
    if OUT.exists(): raise RuntimeError(f'isolated output already exists: {OUT}')
    OUT.mkdir(parents=True)
    for p in ('provenance','noise_canary10/manifests','noise_canary10/clean_mesh','noise_canary10/noisy_mesh','noise_canary10/surface','noise_canary10/figures','noise_canary10/audits','data100','audits','runs'): (OUT/p).mkdir(parents=True, exist_ok=True)
    # No correct old implementation was identified by the focused project search.
    provenance={'EXISTING_NOISE_CODE_FOUND':'NO','search_scope':str(ROOT),'keywords':['noise','mesh_noise','surface_noise','vertex_noise','normal_noise','gaussian_noise','perturb','jitter','noisy_mesh','augmentation','augment_mesh'],'conclusion':'No located script implements the required STEP-to-triangular-mesh normal-displacement noise pipeline; fallback protocol used.','fallback':{'type':'smoothed scalar field along clean vertex normals','levels_sigma_over_bbox_diagonal':LEVELS,'global_seed':GLOBAL_SEED,'per_mesh_seed':'sha256(cad_id|noise_level|42)','clip':'plus_or_minus_3_sigma','smoothing_rounds':SMOOTHING_ROUNDS,'connectivity':'unchanged','surface_sampling':'area-weighted sample from noisy triangles with recomputed noisy face normals','coordinate_frame':'all surface points transformed using N0 clean production transform'}}
    dump(OUT/'provenance/NOISE_IMPLEMENTATION_AUDIT.json', provenance)
    (OUT/'provenance/NOISE_IMPLEMENTATION_AUDIT.md').write_text('# Noise implementation audit\n\n```json\n'+json.dumps(provenance,indent=2)+'\n```\n')
    order=json.loads(ORDER.read_text()); records=order['records']; selected, rule=choose(records)
    manifest={'source_verified_order':str(ORDER),'source_verified_order_sha256':sha(ORDER),'source_verified_subset':str(SUBSET),'source_verified_subset_sha256':sha(SUBSET),'count':10,'selection_rule':rule,'records':[{'cad_id':r['cad_id'],'source_id':r['source_id'],'source_step_sha256':r['source_step_sha256'],'operation_count':r.get('operation_count',0),'operation_types':r.get('operation_types',[]),'face_count':'TO_BE_RECORDED_AFTER_V3_TESSELLATION','bbox_diagonal':'TO_BE_RECORDED_AFTER_V3_TESSELLATION'} for r in selected]}
    dump(OUT/'noise_canary10/manifests/NOISE_CANARY10_MANIFEST.json',manifest)
    rows=[]
    for r in selected:
        cid=r['cad_id']; step=ROOT/'CADFS'/r['source_id']/ 'model.step'
        # authoritative path from prior audit record has no explicit source path; use frozen inventory mapping below if needed.
        if not step.is_file():
            # source path is known from CADFS inventory records, but CADFS files are id/<id>.step in current root.
            candidates=list((ROOT/'CADFS').rglob(r['source_id']+'.step'))
            if len(candidates)!=1: raise RuntimeError(f'cannot resolve source STEP for {cid}: {candidates[:3]}')
            step=candidates[0]
        tess=tessellate_step(step); v=np.asarray(tess['vertices'],np.float64); f=np.asarray(tess['faces'],np.int64)
        if len(v)==0 or len(f)==0 or not np.isfinite(v).all(): raise RuntimeError(f'bad clean tessellation {cid}')
        clean_dir=OUT/'noise_canary10/clean_mesh'/cid; clean_dir.mkdir(); obj_write(clean_dir/'mesh.obj',v,f);np.save(clean_dir/'vertices.npy',v);np.save(clean_dir/'faces.npy',f)
        # Production coordinate contract derives its transform from clean, uniformly sampled source surface.
        raw_clean,n0,_=sample_surface_uniform(v,f,SURFACE_N,GLOBAL_SEED); tf=compute_transform(raw_clean); clean_surface=np.concatenate([apply_canonical(raw_clean,tf.scale,np.asarray(tf.translation)),n0],axis=1).astype(np.float32)
        diag=float(np.linalg.norm(v.max(0)-v.min(0))); adj=mesh_adjacency(len(v),f); chash=hashlib.sha256(f.tobytes()).hexdigest()
        common={'cad_id':cid,'source_id':r['source_id'],'source_step_path':str(step),'source_step_sha256':sha(step),'vertex_count':int(len(v)),'face_count':int(len(f)),'bbox_min':v.min(0).tolist(),'bbox_max':v.max(0).tolist(),'bbox_diagonal':diag,'surface_area':area(v,f),'connected_components':components(len(v),adj),'connectivity_sha256':chash,'faces_path':str(clean_dir/'faces.npy'),'levels':{},'plot_limits':[(float(v[:,j].min()-diag*.06),float(v[:,j].max()+diag*.06)) for j in range(3)]}
        dump(clean_dir/'coordinate_transform.json',{'scale':float(tf.scale),'translation':np.asarray(tf.translation).tolist(),'source':'N0 area-weighted 8192 sample seed42; reused unchanged for all N levels'})
        for level in LEVELS:
            vn,noise_meta=noisy_vertices(v,f,cid,level,diag,adj); level_dir=(OUT/'noise_canary10'/('clean_mesh' if level=='N0' else 'noisy_mesh')/level/cid);level_dir.mkdir(parents=True,exist_ok=True)
            obj_write(level_dir/'mesh.obj',vn,f);np.save(level_dir/'vertices.npy',vn)
            raw,nrm,_=sample_surface_uniform(vn,f,SURFACE_N,seed_for(cid,level+'_surface')); surf=np.concatenate([apply_canonical(raw,tf.scale,np.asarray(tf.translation)),nrm],axis=1).astype(np.float32)
            sp=OUT/'noise_canary10/surface'/level/cid;sp.mkdir(parents=True,exist_ok=True);np.save(sp/'surface_points.npy',surf)
            met=geometry_metrics(v,vn,f,cid,level,diag)
            finite=bool(np.isfinite(vn).all() and np.isfinite(surf).all()); topo=(len(vn)==len(v) and len(f)==len(f) and hashlib.sha256(f.tobytes()).hexdigest()==chash)
            catastrophic=not (finite and topo and .80 <= met['area_ratio'] <= 1.25 and met['bbox_min_delta_rel'] <= .10 and met['bbox_max_delta_rel'] <= .10)
            common['levels'][level]={'sigma_over_D':LEVELS[level],'noise':noise_meta,'vertices_path':str(level_dir/'vertices.npy'),'mesh_path':str(level_dir/'mesh.obj'),'surface_path':str(sp/'surface_points.npy'),'surface_shape':list(surf.shape),'surface_finite':bool(np.isfinite(surf).all()),'normal_unit':bool(np.allclose(np.linalg.norm(surf[:,3:],axis=1),1,atol=1e-5)),'topology_unchanged':topo,'metrics':met,'NOISE_CATASTROPHIC':catastrophic}
        rows.append(common);dump(OUT/'noise_canary10/audits'/f'{cid}.json',common); print(f'CANARY={len(rows)}/10 {cid}',flush=True)
    draw_gallery(rows)
    levels={}
    for lev in ('N1','N2','N3'):
        vals={k:np.asarray([r['levels'][lev]['metrics'][k] for r in rows]) for k in ('chamfer_rel','hausdorff95_rel','bbox_min_delta_rel','bbox_max_delta_rel','centroid_shift_rel','area_ratio','normal_angle_deg_median')}
        levels[lev]={'sigma_over_D':LEVELS[lev],'catastrophic':sum(r['levels'][lev]['NOISE_CATASTROPHIC'] for r in rows),'metrics':{k:{'min':float(a.min()),'median':float(np.median(a)),'p90':float(np.percentile(a,90)),'max':float(a.max())} for k,a in vals.items()}}
    report={'CURRENT_GATE':'CADFS_NOISE_CANARY10_READY_FOR_REVIEW','COUNT':len(rows),'NOISE_PROTOCOL_CANDIDATE':provenance['fallback'],'levels':levels,'RECOMMENDED_MILD_NOISE_LEVEL':None,'WAITING_FOR_VISUAL_CONFIRMATION':'YES','rationale':'No model was run. Selection must be based only on geometry/visual review, not downstream performance.','forbidden_actions_observed':{'training_started':False,'decode_started':False,'dora_used':False,'labels_or_curves_noised':False,'old_roots_modified':False},'gallery':str(OUT/'noise_canary10/figures/GALLERY_10.png'),'closeup_gallery':str(OUT/'noise_canary10/figures/GALLERY_CLOSEUP.png')}
    dump(OUT/'noise_canary10/audits/NOISE_CANARY10_REPORT.json',report); (OUT/'noise_canary10/audits/NOISE_CANARY10_REPORT.md').write_text('# CADFS Noise Canary10\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n')
    dump(OUT/'noise_canary10/audits/NOISE_CANARY10_RECORDS.json',{'records':rows})
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
