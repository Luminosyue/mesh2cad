#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
SRC=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data/pilot_1k_val.json'
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/phase_d_inference_diagnostic_v1/data'
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def main():
 if OUT.exists():raise FileExistsError(OUT)
 rows=json.loads(SRC.read_text())['records'];selected=rows[::4]
 assert len(selected)==50 and len({r['cad_id'] for r in selected})==50
 payload={'protocol':'frozen pilot val order indices 0,4,...,196','source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'official_test_read':False,'count':50,'indices':list(range(0,200,4)),'records':selected};data=canon(payload);payload['content_sha256']=hashlib.sha256(data).hexdigest();OUT.mkdir(parents=True,exist_ok=False);(OUT/'phase_d_50.json').write_bytes(canon(payload));print(json.dumps({'count':50,'sha256':hashlib.sha256((OUT/'phase_d_50.json').read_bytes()).hexdigest(),'content_sha256':payload['content_sha256']},indent=2))
if __name__=='__main__':main()
