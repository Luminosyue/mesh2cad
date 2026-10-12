"""Immutable paths and gate constants for the V4-10K data build."""
from pathlib import Path

REPO_ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
PIPELINE = 'CANONICAL_CAD_DATA_V4_10K'
DATA_ROOT = REPO_ROOT / 'ours3' / 'canonical_cad_data_v4_10k'
CODE_ROOT = REPO_ROOT / 'scripts' / 'canonical_cad_data_v4_10k'
EXECUTOR = REPO_ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
EXECUTOR_SHA256 = '53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'
C2_CHECKPOINT = REPO_ROOT / 'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
SEED = 42
CANARY_QUOTA = {'DEEPCAD': 100, 'FUSION360': 100, 'CADFS': 300}
OUTPUT_DIRS = ('records', 'manifests', 'reports', 'audit', 'failures', 'hashes', 'canary_500', 'cohort_2k', 'cohort_10k')
DEEPCAD_RAW_JSON = REPO_ROOT / 'cad_spatial_dataset/DeepCAD/raw_json'
FUSION360_PASS = REPO_ROOT / 'cad_spatial_dataset/geometry_pack_v2_mesh2cad/placement_fix_retest_v3/STRICT_LABEL_PASS_CANDIDATES.json'
CADFS_FEATURESCRIPT = REPO_ROOT / 'CADFS/featurescript_rp'
