#!/usr/bin/env python3
"""Permanent V4.1 capability regressions for the seven frozen CADFS canaries."""
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path.insert(0,str(ROOT/'scripts'))
from canonical_cad_data_v4_10k.cadfs_capability_v2 import classify_file
CASES={
 '00629139':['REQUIRES_FACE_ATTACHED_SKETCH','REQUIRES_PROFILE_REFERENCE'], # first sketch is principal; a later sketch is cap-face attached
 '00392699':['REQUIRES_CONSTRUCTION_PLANE'],
 '00724459':['REQUIRES_FACE_ATTACHED_SKETCH','REQUIRES_HOLE_SEMANTICS'],
 '00777038':['REQUIRES_PROFILE_TOPOLOGY'],
 '00095369':['REQUIRES_PROFILE_TOPOLOGY'],
 '00902123':['REQUIRES_PROFILE_REFERENCE'],
 '00434774':['REQUIRES_PROFILE_TOPOLOGY'], # closed non-axis-aligned quadrilateral; no normalization is permitted or needed
}
def src(sid): return next((ROOT/'CADFS/featurescript_rp').rglob(sid+'.txt'))
def main():
 rows=[]
 for sid,needed in CASES.items():
  r=classify_file(src(sid)); got=set(r['required_capabilities'])
  ok=set(needed).issubset(got)
  rows.append({'source_id':sid,'expected_capabilities':needed,'actual':r,'status':'PASS' if ok else 'FAIL'})
 out=ROOT/'ours3/canonical_cad_data_v4_10k/capability_model_v2/CADFS_7_REGRESSION.json'
 out.write_text(json.dumps({'suite':'CADFS_CAPABILITY_MODEL_V2','cases':rows,'pass_count':sum(x['status']=='PASS' for x in rows),'total':7},indent=2)+'\n')
 print(json.dumps({'pass_count':sum(x['status']=='PASS' for x in rows),'total':7},indent=2))
 if any(x['status']=='FAIL' for x in rows):raise SystemExit(1)
if __name__=='__main__':main()
