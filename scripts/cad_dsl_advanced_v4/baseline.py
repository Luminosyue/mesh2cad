#!/usr/bin/env python3
"""Freeze V3 executor provenance before advanced-DSL work starts."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OLD = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
EXPECTED = '53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'
OUT = ROOT / 'ours3/canonical_cad_data_v4_10k/reports/ADVANCED_DSL_V4_STATUS.json'
def main():
    if OUT.exists(): raise FileExistsError(f'refusing to overwrite {OUT}')
    actual = hashlib.sha256(OLD.read_bytes()).hexdigest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'canonical_dsl_version':'CAD_DSL_ADVANCED_V4','old_executor_path':str(OLD),'old_executor_sha256_expected':EXPECTED,'old_executor_sha256_actual':actual,'old_executor_modified':actual != EXPECTED,'p0':{'ELLIPSE':'NOT_STARTED','BSPLINE':'NOT_STARTED','REVOLVE':'NOT_STARTED','LOFT':'NOT_STARTED','SWEEP':'NOT_STARTED','TRANSFORM_MIRROR':'NOT_STARTED'},'p1':{'FILLET':'NOT_STARTED','CHAMFER':'NOT_STARTED','SHELL':'NOT_STARTED','PATTERN':'NOT_STARTED'},'training_started':False,'official_test_read':False},indent=2)+'\n')
    print(OUT)
if __name__ == '__main__': main()
