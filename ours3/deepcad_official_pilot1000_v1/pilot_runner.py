import argparse
import json
import signal
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/deepcad_official_pilot1000_v1'
FREEZE = OUT / 'DEEPCAD_OFFICIAL_PILOT1000_FREEZE.jsonl'

sys.path[:0] = [str(ROOT / 'scripts/deepcad'), str(ROOT / 'scripts')]
from deepcad_to_dsl import convert_file
from dsl_to_occ import run_dsl_to_occ
from step_to_mesh import step_to_mesh
from cad_canonical import build_sample_canonical
from geometry_pack_v1.pack import build_one


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def run_case(item):
    sid = item['official_id']
    stage = OUT / 'pilot' / 'DeepCAD' / sid
    geom = OUT / 'pilot' / 'geometry_pack_v1' / 'DeepCAD'
    curve = OUT / 'pilot' / 'curve_data' / 'deepcad' / sid
    token = OUT / 'pilot' / 'curve_tokens' / 'deepcad' / sid
    stage.mkdir(parents=True, exist_ok=True)
    r = {'official_id': sid, 'source_json': item['cad_json'], 'dataset': 'DeepCAD',
         'stages': {}, 'errors': []}
    try:
        dsl = stage / 'program.dsl'
        convert_file(Path(item['cad_json']), dsl)
        r['stages']['OFFICIAL_PROGRAM_PARSE'] = True
        r['stages']['CANONICAL_DSL_BUILD'] = dsl.is_file() and dsl.stat().st_size > 0
        r['dsl_sha256'] = __import__('hashlib').sha256(dsl.read_bytes()).hexdigest()
    except Exception as exc:
        r['stages'].update(OFFICIAL_PROGRAM_PARSE=False, CANONICAL_DSL_BUILD=False)
        r['errors'].append({'stage': 'convert', 'error': f'{type(exc).__name__}: {str(exc)[:700]}'})
    if r['stages'].get('CANONICAL_DSL_BUILD'):
        try:
            shutil.copy2(item['cad_json'], stage / 'source.json')
            result = run_dsl_to_occ(dsl, stage / 'model.step', stage / 'model.stl', source_json=None)
            r['stages'].update(DSL_PARSE=True, RESULT_DEFINED=True,
                                DSL_EXEC=True, STEP_EXPORT=(stage / 'model.step').is_file())
            r['occ_report'] = {k: v for k, v in result.items() if k != 'shape'}
        except Exception as exc:
            r['stages'].update(DSL_PARSE=False, RESULT_DEFINED=False, DSL_EXEC=False, STEP_EXPORT=False)
            r['errors'].append({'stage': 'dsl_exec', 'error': f'{type(exc).__name__}: {str(exc)[:700]}'})
    r['PROGRAM_PASS'] = all(r['stages'].get(k, False) for k in
                             ('OFFICIAL_PROGRAM_PARSE', 'CANONICAL_DSL_BUILD', 'DSL_EXEC', 'STEP_EXPORT'))
    r['stages']['PROGRAM_PASS'] = r['PROGRAM_PASS']
    if not r['PROGRAM_PASS']:
        return r
    try:
        obj = stage / 'model.obj'
        step_to_mesh(stage / 'model.step', obj, stl_path=stage / 'model.stl')
        import trimesh
        mesh = trimesh.load(obj, force='mesh', process=False)
        np.save(stage / 'features.npy', np.concatenate((np.asarray(mesh.vertices),
                 np.asarray(mesh.vertex_normals)), axis=1).astype(np.float32))
        canon = build_sample_canonical(stage)
        meta = build_one(stage, geom, overwrite=True)
        r['stages'].update(STEP_RELOAD=True, BREP_VALID=True,
                            SURFACE_PASS=(meta.get('surface_shape') == [8192, 6]))
        r['canonical'] = canon
        r['geometry_pack'] = {k: v for k, v in meta.items()
                              if k in ('sample_id', 'surface_shape', 'mesh', 'brep_gt_edge_all', 'brep_gt_edge_sharp')}
    except Exception as exc:
        r['stages'].update(STEP_RELOAD=False, BREP_VALID=False, SURFACE_PASS=False)
        r['errors'].append({'stage': 'geometry', 'error': f'{type(exc).__name__}: {str(exc)[:700]}'})
    r['PROGRAM_GEOMETRY_PASS'] = bool(r.get('PROGRAM_PASS')) and all(r['stages'].get(k, False) for k in
                                     ('STEP_RELOAD', 'BREP_VALID', 'SURFACE_PASS'))
    r['stages']['PROGRAM_GEOMETRY_PASS'] = r['PROGRAM_GEOMETRY_PASS']
    if not r['PROGRAM_GEOMETRY_PASS']:
        return r
    try:
        from curve_token_v1.extract_brep_curves import extract_curves_from_shape
        from curve_token_v1.occ_curve_v1 import load_step_shape, make_adaptor
        from curve_token_v1.canonicalize_curves import resolve_normalization, canonicalize_curves
        from curve_token_v1.sample_curves import build_sample_arrays
        from curve_token_v1.extract_topology import extract_topology, topology_arrays
        from OCP.TopAbs import TopAbs_EDGE
        from OCP.TopExp import TopExp
        from OCP.TopoDS import TopoDS
        from OCP.TopTools import TopTools_IndexedMapOfShape
        shape = load_step_shape(stage / 'model.step')
        data = extract_curves_from_shape(shape, cad_id=sid)
        nz = resolve_normalization(stage / 'coordinate_transform.json', data['source_bbox_min'], data['source_bbox_max'])
        data = canonicalize_curves(data, nz)
        emap = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape, TopAbs_EDGE, emap)
        adaptors = [make_adaptor(TopoDS.Edge_s(emap.FindKey(e['edge_id'] + 1))) for e in data['curves']]
        arrays = build_sample_arrays(adaptors, data['curves'], 32, nz)
        arrays.update(topology_arrays(extract_topology(shape, data['curves']), data['curves']))
        curve.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(curve / 'curve_samples.npz', **arrays)
        r.update(raw_curve_n=int(data['num_curves']), curve_sample_shape=list(arrays['curve_xyz_normalized'].shape),
                 curve_finite=bool(np.isfinite(arrays['curve_xyz_normalized']).all()), GT_CURVE_PASS=True)
        r['stages']['GT_CURVE_PASS'] = True
    except Exception as exc:
        r['stages']['GT_CURVE_PASS'] = False
        r['errors'].append({'stage': 'gt_curve', 'error': f'{type(exc).__name__}: {str(exc)[:700]}'})
    if not r['stages'].get('GT_CURVE_PASS'):
        return r
    try:
        import torch
        sys.path[:0] = [str(ROOT / 'scripts/spatiallm_curve_token_c2_frozen_v2')]
        from export_curve_tokens import load_backbone, curve_inputs, TYPE_TO_ID, OCC_ID_TO_TYPE, MAX_CURVE_TOKENS, CURVE_TOKEN_DIM
        if not hasattr(run_case, '_c2'):
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            run_case._c2 = load_backbone(ROOT / 'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt', device) + (device,)
        model, meta, device = run_case._c2
        z = np.load(curve / 'curve_samples.npz')
        brep = json.loads((geom / sid / 'brep_edges.json').read_text())
        sharp = {int(e['edge_index']): bool(e.get('is_sharp', False)) for e in brep['edges']}
        feats, scales, kept = [], [], []
        for i in range(int(z['num_curves'][0])):
            ctype = OCC_ID_TO_TYPE.get(int(z['curve_type_id'][i])); eid = int(z['curve_edge_id'][i])
            if ctype not in TYPE_TO_ID or not sharp.get(eid, False): continue
            xyz = np.asarray(z['curve_xyz_normalized'][i], dtype=np.float64)
            tan = np.asarray(z['curve_tangent'][i], dtype=np.float32)
            f, sc = curve_inputs(xyz, tan); feats.append(f); scales.append(sc)
            kept.append({'edge_id': eid, 'type': ctype, 'poly_len': float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())})
        order = np.argsort([-x['poly_len'] for x in kept]); total = len(order); order = order[:MAX_CURVE_TOKENS]
        if not len(order): raise RuntimeError('no sharp supported curves')
        with torch.no_grad():
            tokens = model(torch.from_numpy(np.stack([feats[i] for i in order])).to(device),
                           torch.from_numpy(np.stack([scales[i] for i in order])).to(device))['token'].float().cpu().numpy()
        token.mkdir(parents=True, exist_ok=True); np.save(token / 'curve_tokens.npy', tokens.astype(np.float32))
        r['stages']['GT_CURVE_PASS'] = True
        r['stages']['C2_FORWARD_PASS'] = True
        r.update(retained_k=int(len(order)), cap_triggered=bool(total > len(order)),
                 c2_output_shape=list(tokens.shape), finite=bool(np.isfinite(tokens).all()))
    except Exception as exc:
        r['stages']['C2_FORWARD_PASS'] = False
        r['errors'].append({'stage': 'c2', 'error': f'{type(exc).__name__}: {str(exc)[:700]}'})
    r['GEOMETRY_CLEAN'] = all(r['stages'].get(k, False) for k in
                              ('PROGRAM_GEOMETRY_PASS', 'SURFACE_PASS', 'GT_CURVE_PASS', 'C2_FORWARD_PASS'))
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--shard', type=int, required=True); ap.add_argument('--size', type=int, default=100)
    a = ap.parse_args(); items = rows(FREEZE); lo=a.shard*a.size; hi=min(len(items),(a.shard+1)*a.size); chosen=items[lo:hi]
    sdir=OUT/'pilot'/f'shard_{a.shard:03d}'; sdir.mkdir(parents=True,exist_ok=True)
    (sdir/'SHARD_INPUT.json').write_text(json.dumps({'shard':a.shard,'start':lo,'end':hi,'n':len(chosen),'ids':[x['official_id'] for x in chosen]},indent=2)+'\n')
    out=sdir/'SHARD_RESULTS.jsonl'; done={}
    if out.exists(): done={json.loads(x)['official_id']:json.loads(x) for x in out.read_text().splitlines() if x.strip()}
    with out.open('a') as f:
        for item in chosen:
            if item['official_id'] in done: continue
            def alarm_handler(signum, frame):
                raise TimeoutError('per-case pilot timeout after 300 seconds')
            old_handler = signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(300)
            try:
                r=run_case(item)
            except Exception as exc:
                r={'official_id':item['official_id'],'source_json':item['cad_json'],'dataset':'DeepCAD',
                   'stages':{},'errors':[{'stage':'case_timeout_or_runner','error':f'{type(exc).__name__}: {str(exc)[:700]}'}],
                   'PROGRAM_PASS':False,'GEOMETRY_CLEAN':False}
            finally:
                signal.alarm(0); signal.signal(signal.SIGALRM, old_handler)
            f.write(json.dumps(r,sort_keys=True)+'\n'); f.flush()
            print(item['official_id'],r.get('GEOMETRY_CLEAN'),flush=True)
    final=[json.loads(x) for x in out.read_text().splitlines() if x.strip()]
    summary={'shard':a.shard,'n':len(final),'program_pass':sum(x.get('PROGRAM_PASS',False) for x in final),'geometry_clean':sum(x.get('GEOMETRY_CLEAN',False) for x in final),'c2_pass':sum(x.get('stages',{}).get('C2_FORWARD_PASS',False) for x in final),'errors':sum(bool(x.get('errors')) for x in final)}
    (sdir/'SHARD_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); (sdir/'SHARD_DONE').write_text('done\n'); print(json.dumps(summary))


if __name__ == '__main__': main()
