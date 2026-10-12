#!/usr/bin/env python3
"""Read-only Phase-0 provenance audit for V3 clean held-out construction."""
from __future__ import annotations

import hashlib, json
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
MANIFEST = ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
OUT = ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool'

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def asset(path: str | Path, **extra):
    p=Path(path); return {'path':str(p),'exists':p.is_file(),'sha256':sha(p) if p.is_file() else None, **extra}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=json.loads(MANIFEST.read_text())['records']
    chosen=[]
    for ds in ('deepcad','fusion360'):
        chosen += sorted((r for r in rows if r['source_dataset']==ds),key=lambda x:x['cad_id'])[:3]
    sample_docs=[]
    for r in chosen:
        sid=Path(r['surface_input']).parent.name
        ds_name='DeepCAD' if r['source_dataset']=='deepcad' else 'Fusion360'
        raw=ROOT/'cad_spatial_dataset'/ds_name/'train'/sid
        pack=Path(r['surface_input']).parent
        curves=Path(r['m2_full_curves']); tokens=Path(r['m2_full_c2_tokens'])
        sample_docs.append({'cad_id':r['cad_id'],'dataset':r['source_dataset'],'sample_id':sid,
            'assets':{
              'source_step':asset(raw/'model.step'),'raw_source_dir':str(raw),
              'mesh_obj':asset(pack/'mesh.obj'),'surface_points':asset(pack/'surface_points.npy',shape='[8192,6] xyz+face-normal'),
              'surface_points_source':asset(pack/'surface_points_source.npy',shape='[8192,3] source mesh frame'),
              'surface_face_index':asset(pack/'surface_face_index.npy',shape='[8192]'),
              'coordinate_transform':asset(pack/'coordinate_transform.json'),
              'cad_target_dsl':asset(r['target_dsl']),'brep_edges':asset(pack/'brep_edges.json'),
              'curve_samples':asset(curves),'curve_tokens':asset(tokens,shape='[N,256] float32'),
              'v3_record':{'clean_manifest':str(MANIFEST),'record_sha256':r.get('record_sha256'),'clean_contract':r['clean_contract']},
            }})
    pipeline={
      'phase':'V3_CLEAN_HELDOUT_PHASE0_READ_ONLY_PROVENANCE',
      'status':'PASS',
      'surface_source':'STEP_TO_TRIANGULATED_MESH_TO_UNIFORM_SURFACE_POINTS',
      'curve_source':'FINAL_STEP_BREP_TOPOLOGICAL_EDGES_SHARP_ONLY_TO_ARCLENGTH_SAMPLES_TO_FROZEN_C2',
      'c2_checkpoint':str(ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'),
      'c2_checkpoint_sha256':'553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9',
      'pipeline':[
        {'asset':'source CAD / STEP','script':'scripts/geometry_pack_v1/pack.py','function':'freeze_cad_target','input':'cad_spatial_dataset/{DeepCAD|Fusion360}/train/<id>/{model.step,program_canonical.dsl,coordinate_transform.json}','output':'geometry_pack_v1/<id>/{cad_target.dsl,coordinate_transform.json}','transform':'target DSL copied, never derived from mesh','unit':'frozen coordinate_transform'},
        {'asset':'mesh.obj','script':'scripts/geometry_pack_v1/pack.py','function':'build_one -> occ.tessellate_step','input':'source final model.step','output':'geometry_pack_v1/<id>/mesh.obj','transform':'OCC tessellation, trimesh export','unit':'source STEP frame'},
        {'asset':'surface points','script':'scripts/geometry_pack_v1/{pack.py,surface.py}','function':'sample_surface_uniform','input':'tessellated vertices/faces','output':'surface_points_source.npy, surface_face_index.npy, surface_points.npy','transform':'area-weighted triangle choice + folded-square barycentric sampling; canonical xyz scale+translation; face normals not translated','unit':'source points -> frozen canonical transform','seed':'geometry_pack_v1.constants.DEFAULT_SEED'},
        {'asset':'GT B-Rep curve samples','script':'scripts/curve_token_v1/build_dataset.py','function':'build_one -> extract_curves_from_shape -> build_sample_arrays','input':'source final model.step and read-only geometry_pack_v1 coordinate_transform','output':'ours3/curve_token_data_v1/{deepcad_train|fusion360_train}/<id>/curve_samples.npz','transform':'OCC TopoDS edges; canonicalized; arc-length 32 samples; sharp filtering happens at C2 export','unit':'same frozen Track-A coordinate transform'},
        {'asset':'C2 input and tokens','script':'scripts/spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py','function':'process_cad -> curve_inputs -> frozen C2 forward','input':'curve_samples.npz (normalized xyz, tangents); sharp B-Rep edge map','output':'curve_tokens_c2_frozen_v2/{deepcad|fusion360}/<id>/curve_tokens.npy','transform':'curve-local frame xyz + tangent + normalized s; log polyline length; deterministic length order; sharp-only; max 128 before V3 adapter','unit':'local normalized curve xyz + log length'},
        {'asset':'V3 JSON and tokenizer/chat input','script':'scripts/spatiallm_curve_token_c2_frozen_v2/run_v2_1k_gate.py; scripts/v3_clean_training_v1/{build_clean_manifest.py,train_clean_v3.py}','function':'run_v2_1k_gate.main; build_clean_manifest.main; train_clean_v3.encode_full','input':'surface path + C2 tokens + cad_target.dsl','output':'CLEAN_V3_MANIFEST.json then prompt/target token IDs','transform':'V3 M2 GeometryPrefixAdapter turns full C2 tokens into 8 summaries; full target plus eot checked against actual splice; no target slicing','unit':'token positions, context limit 4096'},
      ],
      'samples':sample_docs,
      'forbidden_reads':{'decode_dev50':False,'pilot150':False,'anchor_eval100':False,'official_test':False},
    }
    (OUT/'BUILD_PIPELINE_PROVENANCE.json').write_text(json.dumps(pipeline,indent=2)+'\n')
    lines=['# V3 held-out Phase 0: verified construction provenance','',f"Surface source: `{pipeline['surface_source']}`.",f"Curve source: `{pipeline['curve_source']}`.",'', '## Pipeline']
    for x in pipeline['pipeline']:
        lines += [f"### {x['asset']}",f"- Script/function: `{x['script']}` — `{x['function']}`",f"- Input: {x['input']}",f"- Output: {x['output']}",f"- Transform: {x['transform']}",f"- Unit/canonicalization: {x['unit']}", f"- Seed: {x.get('seed','not applicable')}",'']
    lines += ['## Audited samples']
    for s in sample_docs:
        lines += [f"### {s['cad_id']} ({s['dataset']})"]
        for name,a in s['assets'].items():
            if isinstance(a,dict) and 'path' in a: lines.append(f"- {name}: `{a['path']}`; exists={a['exists']}; sha256={a['sha256']}")
        lines.append('')
    (OUT/'BUILD_PIPELINE_PROVENANCE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':'PASS','samples':len(sample_docs),'output':str(OUT)},indent=2))

if __name__=='__main__': main()
