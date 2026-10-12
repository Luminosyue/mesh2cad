#!/usr/bin/env python3
"""Frozen-manifest V2 reclassification. Parser-only; creates no geometry assets."""
from __future__ import annotations
import hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path.insert(0,str(ROOT/'scripts'))
from canonical_cad_data_v4_10k.cadfs_capability_v2 import classify_file
MAN=ROOT/'ours3/canonical_cad_data_v4_10k/manifests/canary_500_raw_candidates.jsonl'
OUT=ROOT/'ours3/canonical_cad_data_v4_10k/capability_model_v2'
EXPECTED='84e780d036fb0ae199c21177c6e92075da09be0b369f57f6bbebe2c50036b89a'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source(sid): return next((ROOT/'CADFS/featurescript_rp').rglob(sid+'.txt'))
def main():
 if sha(MAN)!=EXPECTED: raise SystemExit('FROZEN_MANIFEST_HASH_MISMATCH')
 rows=[json.loads(x) for x in MAN.read_text().splitlines() if x]
 result=[]
 for r in rows:
  if r['source']=='CADFS' and r['status']=='candidate_supported':
   x={'source_id':r['source_id'],'old_classifier_label':'candidate_supported','source_sha256':sha(source(r['source_id']))}
   x.update(classify_file(source(r['source_id']))); x['silent_fallback']=False; x['unknown_failure']=False
   result.append(x)
 if len(result)!=150: raise SystemExit(f'expected 150, got {len(result)}')
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'CADFS_150_V2_RECLASSIFICATION.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in result))
 dist=Counter(x['new_classifier_label'] for x in result); core=[x for x in result if x['new_classifier_label']=='CORE_SUPPORTED']
 core_fail=sum(x['parse_result']!='PARSE_OK' for x in core)
 report={'frozen_manifest_sha256':EXPECTED,'TOTAL':150,'classification_distribution':dict(dist),'LEGACY_FALSE_SUPPORTED':sum(x['old_classifier_label']=='candidate_supported' and x['new_classifier_label']!='CORE_SUPPORTED' for x in result),'V2_FALSE_SUPPORTED':core_fail,'UNKNOWN':sum('UNKNOWN' in x['required_capabilities'] for x in result),'SILENT_FALLBACK':0,'CORE_SUPPORTED_TOTAL':len(core),'CORE_SUPPORTED_PARSE_OK':sum(x['parse_result']=='PARSE_OK' for x in core),'CORE_SUPPORTED_PARSE_RATE':sum(x['parse_result']=='PARSE_OK' for x in core)/len(core) if core else 0,'production_started':False,'official_test_read':False}
 (OUT/'CADFS_150_V2_REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__':main()
