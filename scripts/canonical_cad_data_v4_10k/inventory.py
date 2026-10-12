"""Read-only source inventory for V4-10K. Never mutates source datasets."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from .config import REPO_ROOT, DATA_ROOT, EXECUTOR, EXECUTOR_SHA256, C2_CHECKPOINT

def _files(root, suffixes):
    if not root.exists(): return 0
    return sum(1 for p in root.rglob('*') if p.is_file() and p.suffix.lower() in suffixes)

def _dirs(root):
    return sum(1 for p in root.iterdir() if p.is_dir()) if root.exists() else 0

def inventory():
    deep_root = REPO_ROOT / 'cad_spatial_dataset/DeepCAD'
    fusion_root = REPO_ROOT / 'cad_spatial_dataset/Fusion360'
    cadfs_root = REPO_ROOT / 'CADFS'
    script = REPO_ROOT / 'scripts'
    result = {
      'pipeline': 'CANONICAL_CAD_DATA_V4_10K', 'read_only_source_inventory': True,
      'DEEPCAD_ROOT': str(deep_root), 'DEEPCAD_TOTAL': _dirs(deep_root / 'train'), 'DEEPCAD_RAW_JSON_COUNT': _files(deep_root / 'raw_json', {'.json'}),
      'FUSION360_ROOT': str(fusion_root), 'FUSION360_TOTAL': _dirs(fusion_root / 'train'), 'FUSION360_RECON_JSON_COUNT': _files(fusion_root / 'reconstruction', {'.json'}),
      'CADFS_ROOT': str(cadfs_root), 'CADFS_TOTAL': _files(cadfs_root / 'featurescript_rp', {'.txt'}),
      'CADFS_STEP_COUNT': _files(cadfs_root / 'step', {'.step','.stp'}), 'CADFS_STL_COUNT': _files(cadfs_root, {'.stl'}), 'CADFS_PROGRAM_COUNT': _files(cadfs_root / 'featurescript_rp', {'.txt'}),
      'EXISTING_DEEPCAD_CONVERTER': str(script / 'deepcad/deepcad_to_dsl.py'),
      'EXISTING_FUSION_CONVERTER': str(script / 'geometry_pack_v2_mesh2cad/placement_v3/fusion360_to_dsl.py'),
      'EXISTING_CADFS_UTILS': str(script / 'canonical_cad_data_v4/converters/cadfs_to_dsl.py'),
      'EXISTING_CURVE_EXTRACTION': str(script / 'curve_token_v1/extract_brep_curves.py'),
      'EXISTING_SURFACE_SAMPLING': str(script / 'geometry_pack_v1/surface.py'),
      'EXISTING_EDGE_EXTRACTION': str(script / 'geometry_pack_v1/mesh_edges.py'),
      'EXISTING_C2_EXPORT': str(script / 'spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py'),
      'FROZEN_DSL_EXECUTOR': str(EXECUTOR), 'FROZEN_DSL_EXECUTOR_SHA256_EXPECTED': EXECUTOR_SHA256,
      'FROZEN_DSL_EXECUTOR_SHA256_ACTUAL': hashlib.sha256(EXECUTOR.read_bytes()).hexdigest() if EXECUTOR.exists() else None,
      'C2_CHECKPOINT': str(C2_CHECKPOINT), 'C2_CHECKPOINT_EXISTS': C2_CHECKPOINT.exists(),
      'LEGACY_CANONICAL_V4_PRESENT': (REPO_ROOT / 'ours3/canonical_cad_data_v4').exists(),
    }
    return result

def write_inventory_once():
    out = DATA_ROOT / 'reports/01_SOURCE_INVENTORY.json'
    if out.exists(): raise FileExistsError(f'refusing to overwrite: {out}')
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(inventory(), indent=2) + '\n')
    return out
