#!/usr/bin/env python3
"""Independent, manifest-locked V4-10K execution canary.

This module deliberately contains no selection code and imports no old V4
selection or gate-policy module.  It consumes rows in their frozen order only.
"""
from __future__ import annotations

import argparse, hashlib, json, shutil, sys, traceback
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

MANIFEST = ROOT / 'ours3/canonical_cad_data_v4_10k/manifests/canary_500_raw_candidates.jsonl'
EXPECTED_MANIFEST_SHA256 = '84e780d036fb0ae199c21177c6e92075da09be0b369f57f6bbebe2c50036b89a'
OUT = ROOT / 'ours3/canonical_cad_data_v4_10k/canary_execution_v1'
OLD = SCRIPTS / 'canonical_cad_data_v4'

# Only these old V4 modules are reused; all are pure conversion/geometry helpers.
REUSED = [
    OLD/'converters/deepcad_to_dsl.py', OLD/'converters/fusion360_to_dsl.py',
    OLD/'converters/fusion_precheck.py', OLD/'converters/cadfs_to_dsl.py',
    OLD/'converters/cad_dsl.py', OLD/'geometry/occ_ops.py',
    OLD/'geometry/c2_export.py', OLD/'hashutil.py',
]

from canonical_cad_data_v4.converters.deepcad_to_dsl import convert_file as deepcad_convert
from canonical_cad_data_v4.converters.fusion360_to_dsl import fusion360_json_to_dsl
from canonical_cad_data_v4.converters.fusion_precheck import require_supported
from canonical_cad_data_v4.converters.cadfs_to_dsl import audit_featurescript, cadfs_to_dsl
from canonical_cad_data_v4.converters.cad_dsl import execute_dsl
from canonical_cad_data_v4.geometry.occ_ops import load_step_shape, geometry_metrics, tessellate, sample_surface_4096, extract_oracle_edges_and_curves
from canonical_cad_data_v4.geometry.c2_export import encode_curves
from canonical_cad_data_v4.hashutil import canonical_dsl_sha256

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def empty(row):
    return {k: row.get(k) for k in ('source','source_id','cad_id')} | {
      'manifest_sha256': EXPECTED_MANIFEST_SHA256, 'source_dataset': row['source'],
      'pool_type': ('advanced' if row['status']=='unsupported_audit_candidate' else 'supported'),
      'source_program_hash': None, 'canonical_program_hash': None,
      'capability_status': 'UNASSESSED', 'unsupported_ops': [], 'fallback_used': False,
      'dsl_parse': False, 'occ_execute': False, 'step_export': False, 'step_reload': False,
      'geometry_gate': False, 'surface_gate': False, 'edge_gate': False,
      'curve_gate': False, 'c2_gate': False, 'failure_stage': None, 'failure_reason': None,
    }

def fail(r, stage, exc):
    r['failure_stage']=stage; r['failure_reason']=f'{type(exc).__name__}:{exc}'[:1000]
    return r

def source_path(row):
    p=Path(row['source_path'])
    if p.exists(): return p
    if row['source']=='FUSION360':
        sid=row['source_id']
        for p in (ROOT/'cad_spatial_dataset/Fusion360/reconstruction'/f'{sid}.json', ROOT/'cad_spatial_dataset/Fusion360/train'/sid/'source.json'):
            if p.exists(): return p
    raise FileNotFoundError(row['source_path'])

def convert(row, r, dsl):
    src=source_path(row); r['source_program_hash']=sha(src)
    if row['source']=='DEEPCAD':
        report=deepcad_convert(src,dsl); text=report.get('dsl_text') or dsl.read_text()
    elif row['source']=='FUSION360':
        data=json.loads(src.read_text()); require_supported(data); text,_=fusion360_json_to_dsl(data); dsl.write_text(text)
    elif row['source']=='CADFS':
        text0=src.read_text(encoding='utf-8',errors='replace'); audit=audit_featurescript(text0)
        r['unsupported_ops']=audit['unsupported']
        if not audit['lossless_candidate']:
            r['capability_status']='UNSUPPORTED'; raise NotImplementedError(','.join(audit['unsupported']) or 'not_lossless_candidate')
        text,_=cadfs_to_dsl(text0); dsl.write_text(text)
    else: raise ValueError('unknown_source')
    r['canonical_program_hash']=canonical_dsl_sha256(text); r['dsl_parse']=True; r['capability_status']='SUPPORTED'
    return text

def execute_one(row):
    r=empty(row); d=OUT/'records'/row['cad_id']; d.mkdir(parents=True,exist_ok=True)
    dsl=d/'program.dsl'; step=d/'model.step'
    try: convert(row,r,dsl)
    except Exception as e: return fail(r,'dsl_parse',e)
    try: execute_dsl(dsl.read_text(),step,d/'model.stl'); r['occ_execute']=True; r['step_export']=step.exists() and step.stat().st_size>0
    except Exception as e: return fail(r,'occ_execute',e)
    try: shape=load_step_shape(step); r['step_reload']=True
    except Exception as e: return fail(r,'step_reload',e)
    try:
        m=geometry_metrics(shape); r['geometry_gate']=bool(m['geometry_metrics_ok']); r['geometry_metrics']=m
        if not r['geometry_gate']: raise RuntimeError('geometry_metrics_failed')
    except Exception as e: return fail(r,'geometry_qa',e)
    try:
        v,f=tessellate(shape); surf=sample_surface_4096(v,f,4096,42)
        if surf.shape!=(4096,6) or not __import__('numpy').isfinite(surf).all(): raise RuntimeError('invalid_surface4096')
        __import__('numpy').save(d/'surface4096.npy',surf); r['surface_gate']=True
    except Exception as e: return fail(r,'surface4096',e)
    try:
        ex=extract_oracle_edges_and_curves(shape,n_sample=32); curves=ex['curves']
        if not curves: raise RuntimeError('no_curves')
        __import__('numpy').save(d/'edge_xyz.npy',__import__('numpy').concatenate([x['xyz'] for x in curves]))
        (d/'curves.json').write_text(json.dumps({'type_counts':ex['type_counts'],'curves':curves}))
        r['edge_gate']=True; r['curve_gate']=True
    except Exception as e: return fail(r,'edge_curve',e)
    try:
        tok,meta=encode_curves(curves); __import__('numpy').save(d/'c2.npy',tok); r['c2_gate']=True; r['c2_meta']=meta
    except Exception as e: return fail(r,'c2',e)
    r['failure_stage']=None; r['failure_reason']=None
    return r

def advanced_audit(rows):
    out=[]
    for row in rows:
        if row['status']!='unsupported_audit_candidate': continue
        r=empty(row); r['capability_status']='UNSUPPORTED'; r['source_program_hash']=sha(source_path(row))
        a=audit_featurescript(source_path(row).read_text(encoding='utf-8',errors='replace'))
        r['unsupported_ops']=a['unsupported']; r['failure_stage']='capability_audit'; r['failure_reason']='UNSUPPORTED_OPERATION:'+','.join(a['unsupported'])
        out.append(r)
    return out

def main():
    if sha(MANIFEST)!=EXPECTED_MANIFEST_SHA256: raise SystemExit('FROZEN_MANIFEST_HASH_MISMATCH')
    rows=[json.loads(x) for x in MANIFEST.read_text().splitlines() if x]
    # frozen order, quotas are a prefix per source: no sorting/shuffling/reselection.
    want={'DEEPCAD':5,'FUSION360':5,'CADFS':10}; seen=Counter(); canary=[]
    for row in rows:
        if row['status']=='unsupported_audit_candidate': continue
        if seen[row['source']]<want[row['source']]: canary.append(row); seen[row['source']]+=1
    if len(canary)!=20 or dict(seen)!=want: raise SystemExit(f'FROZEN_MANIFEST_QUOTA_ERROR:{seen}')
    OUT.mkdir(parents=True,exist_ok=True)
    results=[execute_one(x) for x in canary]; audits=advanced_audit(rows)
    (OUT/'execution_canary.jsonl').write_text(''.join(json.dumps(x,sort_keys=True,default=str)+'\n' for x in results))
    (OUT/'advanced_capability_audit.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in audits))
    fs=Counter(x['failure_stage'] or 'PASS' for x in results); caps=Counter(op for x in audits for op in x['unsupported_ops'])
    all_pass=all(all(x[k] for k in ('dsl_parse','occ_execute','step_export','step_reload','geometry_gate','surface_gate','edge_gate','curve_gate','c2_gate')) and not x['fallback_used'] for x in results)
    report={'manifest_sha256':EXPECTED_MANIFEST_SHA256,'canary_count':20,'canary_by_source':dict(Counter(x['source_dataset'] for x in results)),'stage_outcomes':dict(fs),'advanced_count':len(audits),'advanced_capability_distribution':dict(caps),'silent_fallback_count':sum(bool(x['fallback_used']) for x in results+audits),'unknown_failure_count':sum(x['failure_stage'] is not None and not x['failure_reason'] for x in results+audits),'allow_expand_supported_350':all_pass,'no_training_started':True,'official_test_read':False,'reused_pure_modules':[{'path':str(p),'sha256':sha(p)} for p in REUSED]}
    (OUT/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
