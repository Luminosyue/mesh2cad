#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/m2_deepcad_fusion360_clean10k_real_pipeline_v1'

FILES = {
    'step_to_occ_pack': 'scripts/geometry_pack_v1/pack.py',
    'occ_tessellation': 'scripts/geometry_pack_v1/occ.py',
    'surface_sampling': 'scripts/geometry_pack_v1/surface.py',
    'gt_curve_extractor': 'scripts/curve_token_v1/build_dataset.py',
    'c2_exporter': 'scripts/spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py',
    'm2_k8_interface': 'scripts/spatiallm_geometry_prefix_v3/train_v3_smoke.py',
    'original_m2_loader': 'scripts/v3_clean_training_v1/train_clean_v3.py',
    'canonical_builder': 'scripts/deepcad/cad_canonical.py',
    'fusion_sample_builder': 'scripts/fusion360/build_fusion360_sample.py',
    'fusion_converter_original': 'scripts/fusion360/fusion360_to_dsl.py',
    'fusion_converter_fixed': 'scripts/geometry_pack_v2_mesh2cad/placement_v3/fusion360_to_dsl.py',
    'fusion_unit_contract': 'scripts/geometry_pack_v2_mesh2cad/placement_v3/fusion_unit_contract.py',
    'executor': 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py',
    'geometry_evaluator': 'scripts/geometry_pack_v2_mesh2cad/placement_v3/retest.py',
    'c2_checkpoint': 'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt',
}

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def write(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def staged(root: Path, dataset: str) -> list[dict]:
    rows = []
    if not root.is_dir():
        return rows
    for d in sorted(x for x in root.iterdir() if x.is_dir()):
        required = ['model.step', 'program_canonical.dsl', 'coordinate_transform.json', 'source.json']
        ok = all((d / n).is_file() for n in required)
        rows.append({'dataset': dataset, 'source_id': d.name, 'cad_id': f'{dataset.lower()}__{d.name}',
                     'group_id': f'{dataset.lower()}__{d.name}', 'source_path': str(d),
                     'exact_original_m2_source_ready': ok,
                     'required_assets': {n: (d/n).is_file() for n in required}})
    return rows

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {}
    missing = []
    for key, rel in FILES.items():
        p = ROOT / rel
        if p.is_file(): hashes[key] = {'path': str(p), 'sha256': sha(p), 'size': p.stat().st_size}
        else: missing.append(str(p))

    deep_root = ROOT / 'cad_spatial_dataset/DeepCAD/train'
    fusion_stage_root = ROOT / 'cad_spatial_dataset/Fusion360/train'
    rows = staged(deep_root, 'DeepCAD') + staged(fusion_stage_root, 'Fusion360')
    ready = [r for r in rows if r['exact_original_m2_source_ready']]
    registry = OUT / 'CAD_ID_REGISTRY.jsonl'
    registry.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))

    recon = ROOT / 'cad_spatial_dataset/Fusion360/reconstruction/reconstruction'
    split_path = ROOT / 'cad_spatial_dataset/Fusion360/reconstruction/train_test.json'
    split = json.loads(split_path.read_text()) if split_path.is_file() else {}
    fusion_native_ids = sorted(set(split.get('train', [])) | set(split.get('test', [])))
    fusion_native_complete = 0
    for sid in fusion_native_ids:
        if (recon/f'{sid}.json').is_file() and (recon/f'{sid}.step').is_file() and (recon/f'{sid}.obj').is_file():
            fusion_native_complete += 1

    deep_ready = sum(r['dataset']=='DeepCAD' for r in ready)
    fusion_ready = sum(r['dataset']=='Fusion360' for r in ready)
    inventory = {
        'DEEPCAD_DIRECTORY_COUNT': sum(r['dataset']=='DeepCAD' for r in rows),
        'DEEPCAD_EXACT_ORIGINAL_M2_READY': deep_ready,
        'FUSION360_STAGED_DIRECTORY_COUNT': sum(r['dataset']=='Fusion360' for r in rows),
        'FUSION360_EXACT_ORIGINAL_M2_READY': fusion_ready,
        'FUSION360_NATIVE_IDENTITIES': len(fusion_native_ids),
        'FUSION360_NATIVE_JSON_STEP_OBJ_COMPLETE': fusion_native_complete,
        'TOTAL_EXACT_ORIGINAL_M2_READY_UPPER_BOUND': deep_ready + fusion_ready,
        'SHORTAGE_TO_10000_BEFORE_CLEANING': max(0, 10000 - deep_ready - fusion_ready),
        'native_fusion_not_counted_as_exact_ready_reason': 'missing frozen old program_canonical.dsl and coordinate_transform.json; old builder obtains transform from features.npy produced by Dora stage',
        'registry': {'path': str(registry), 'sha256': sha(registry), 'count': len(rows)},
    }
    write('SOURCE_POOL_INVENTORY.json', inventory)

    provenance = {
        'CURRENT_GATE': 'M2_10K_REAL_PIPELINE_PROVENANCE_FAIL',
        'REAL_ORIGINAL_M2': True,
        'SURFACE_PIPELINE': 'STEP_TO_CLEAN_MESH_TO_8192X6',
        'SURFACE_SOURCE': 'CLEAN_SURFACE',
        'NOISE_STAGE': 'NONE',
        'CURVE_PIPELINE': 'FINAL_STEP_BREP_SHARP_EDGES_TO_32X7_TO_FROZEN_C2_TO_NX256_TO_EXISTING_K8_SUMMARY',
        'TARGET': 'ORIGINAL_CANONICAL_CAD_DSL_PLUS_EOS',
        'C2_FROZEN': True,
        'C2_CKPT_SHA256': hashes.get('c2_checkpoint', {}).get('sha256'),
        'CURVE_INPUT': '32x7', 'CURVE_FEATURE_DIM': 256, 'CURVE_SUMMARY_K': 8,
        'PLACEMENT_USED': False, 'DORA_CURVES_USED': False, 'DSL_V2_USED': False,
        'files': hashes, 'missing_files': missing,
        'blocking_conflict': {
            'code_evidence': [
                'scripts/fusion360/build_fusion360_sample.py runs dora_spatial before cad_canonical.build_sample_canonical',
                'scripts/deepcad/cad_canonical.py build_sample_canonical loads features.npy and computes coordinate transform from features[:, :3]',
                'scripts/geometry_pack_v1/pack.py requires pre-existing program_canonical.dsl and coordinate_transform.json',
            ],
            'contract_requirement': 'expand raw Fusion360 with exact original canonical target while Dora execution and pipeline modification are forbidden',
            'result': 'no frozen numerically-equivalent Dora-free canonical target builder was found; native raw Fusion360 cannot be promoted to exact original-M2-ready candidates',
        },
        'CANARY40_STARTED': False, 'PILOT1000_STARTED': False, 'FULL_SCAN_STARTED': False,
        'TRAINING_RUN': False, 'DECODE_RUN': False, 'OFFICIAL_TEST_READ': False,
    }
    write('REAL_M2_PIPELINE_PROVENANCE.json', provenance)
    final = {
        'CURRENT_GATE': provenance['CURRENT_GATE'], 'TRAINING_APPROVED': 'NO',
        'reason': 'EXACT_ORIGINAL_M2_SOURCE_POOL_BELOW_10000_AND_RAW_FUSION_CANONICALIZATION_CONFLICT',
        **inventory,
        'CANARY40_STARTED': False, 'PILOT1000_STARTED': False,
        'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO',
        'NEXT_STEP': 'M2_10K_SOURCE_POOL_EXPANSION_V1_OR_EXPLICIT_CANONICALIZATION_PROTOCOL_AMENDMENT',
    }
    write('FINAL_REPORT.json', final)
    (OUT/'FINAL_REPORT.md').write_text(
        '# M2 DeepCAD + Fusion360 clean10k real-pipeline phase-0\n\n'
        f"**Gate:** `{final['CURRENT_GATE']}`\n\n"
        'The frozen original M2 source-preparation chain cannot currently produce 10,000 exact-compatible candidates '
        'without violating the no-Dora/no-pipeline-change contract. Canary and training were not started.\n')
    print(json.dumps(final, indent=2))

if __name__ == '__main__':
    main()
