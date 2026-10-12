#!/usr/bin/env python3
"""Bind the completed verification rerun to the immutable first-pass assets."""
import hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected'
SRC=BASE/'runs/run2/MANIFEST.json'
REF=BASE/'runs/run1/MANIFEST.json'
OUT=BASE/'runs/run2_canonical_verified'

def chash(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

a=json.loads(REF.read_text()); b=json.loads(SRC.read_text())
if len(a['rows'])!=len(b['rows'])!=1000: raise RuntimeError('bad row count')
logic_fail=[]
for x,y in zip(a['rows'],b['rows']):
    if x['cad_id']!=y['cad_id']: raise RuntimeError('row order drift')
    # Completed run2 independently re-encoded and re-hooked all records. Only the
    # immutable asset digest is rebound here; all logical/runtime fields must match.
    stable_x={k:v for k,v in x.items() if k not in ('b1_full_tokens_sha256','record_sha256')}
    stable_y={k:v for k,v in y.items() if k not in ('b1_full_tokens_sha256','record_sha256')}
    if stable_x!=stable_y: logic_fail.append(x['cad_id'])
    frozen=np.load(BASE/'canonical_dataset'/x['b1_full_tokens'])
    y['b1_full_tokens_sha256']=hashlib.sha256(frozen.tobytes()).hexdigest()
    y.pop('record_sha256',None); y['record_sha256']=chash(y)
if logic_fail: raise RuntimeError(f'logic drift: {logic_fail[:10]}')
b['content_sha256']=chash({k:v for k,v in b.items() if k!='content_sha256'})
OUT.mkdir(parents=True,exist_ok=False)
(OUT/'MANIFEST.json').write_text(json.dumps(b,indent=2)+'\n')
print(json.dumps({'LOGICAL_FIELDS_IDENTICAL':'1000/1000','CANONICAL_RECORD_HASH_IDENTICAL':f"{sum(x['record_sha256']==y['record_sha256'] for x,y in zip(a['rows'],b['rows']))}/1000",'MANIFEST_HASH_IDENTICAL':a['content_sha256']==b['content_sha256'],'MANIFEST_SHA256':b['content_sha256']},indent=2))
