#!/usr/bin/env python3
"""Re-aggregate completed CADFS301 screen using source FeatureScript semantics.

Reads immutable per-CAD geometry results; does not execute geometry, load any
model, or modify the frozen canary.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/cadfs_overfit100_v1/geometry_supervision_audit_v1'
SCREEN=OUT/'CADFS301_GEOMETRY_SCREEN.jsonl'
MAN=OUT/'CADFS301_GEOMETRY_SCREEN_MANIFEST.json'

def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def flags(text):
 l=text.lower()
 return {
  'EXTRUDE': 'extrude(' in l,
  'BOOLEAN': 'opboolean' in l or 'removeoperation' in l or 'addoperation' in l,
  'PROFILE_HOLE': l.count('skcircle')>1 or ('skcircle' in l and 'sklinesegment' in l),
  # `qCreatedBy` and `sketchPlane` are ubiquitous in ordinary principal-plane
  # sketches, so they are not evidence of face attachment.
  'FACE_ATTACHED_SKETCH': any(x in l for x in ('faceattached','evfacetangentplane','faceattachment')),
  'SYMMETRIC_EXTRUDE': 'symmetric' in l or 'twosided' in l or 'seconddirection' in l,
  'EXTRUDE_EXTENT': any(x in l for x in ('startoffset','endoffset','endbound','startbound','oppositedirection','negativedirection')),
  'REVOLVE': 'revolve(' in l,
  'FILLET': 'fillet(' in l or 'opfillet' in l,
  'CHAMFER': 'chamfer(' in l or 'opchamfer' in l,
  'PATTERN': 'pattern(' in l or 'oppattern' in l,
 }
def stat(a):return {'count':len(a),'geometry_pass':sum(r['GEOMETRY_PASS'] for r in a),'pass_rate':sum(r['GEOMETRY_PASS'] for r in a)/len(a) if a else None}
def main():
 rows=[json.loads(x) for x in SCREEN.read_text().splitlines() if x]
 meta={r['source_id']:r for r in json.loads(MAN.read_text())['records']}
 for r in rows:
  fs=Path(meta[r['source_id']]['source_fs_path']);t=fs.read_text(encoding='utf-8',errors='replace');r['source_feature_count']=sum(t.count(x) for x in ('newSketch','extrude(','revolve(','loft(','sweep(','opBoolean','fillet(','chamfer(','opShell'))
  r['source_operation_flags']=flags(t)
  p=OUT/'screen_work'/r['cad_id']/'cad_target.dsl';r['dsl_char_count']=len(p.read_text()) if p.is_file() else None
 ops={k:stat([r for r in rows if r['source_operation_flags'][k]]) for k in next(iter(rows))['source_operation_flags']}
 counts=np.array([r['source_feature_count'] for r in rows]);q1,q2=np.percentile(counts,[100/3,200/3])
 for r in rows:r['complexity_tercile']='SIMPLE' if r['source_feature_count']<=q1 else ('MEDIUM' if r['source_feature_count']<=q2 else 'HARD')
 complexity={k:stat([r for r in rows if r['complexity_tercile']==k]) for k in ('SIMPLE','MEDIUM','HARD')}
 out={'source_operation_definition':'direct FeatureScript lexical operation-semantic flags; a CAD may be counted in multiple buckets','BY_OPERATION':ops,'BY_COMPLEXITY_TERCILES':complexity,'complexity_basis':{'metric':'FeatureScript feature-call count','q1':float(q1),'q2':float(q2),'counts':dict(Counter(r['complexity_tercile'] for r in rows))}}
 dump(OUT/'CADFS301_BY_OPERATION_SEMANTIC_V1.json',out);(OUT/'CADFS301_BY_OPERATION_SEMANTIC_V1.md').write_text('# CADFS301 source-semantic operation and complexity aggregation\n\n```json\n'+json.dumps(out,indent=2)+'\n```\n')
 dump(OUT/'CADFS301_SCREEN_AUGMENTED_V1.jsonl',rows)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
