#!/usr/bin/env python3
"""Correct Canary14 root-cause labels using only semantically explicit FS flags."""
from __future__ import annotations
import ast,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');BASE=ROOT/'ours3/cadfs_overfit100_v1';OUT=BASE/'geometry_supervision_audit_v1';sys.path.insert(0,str(ROOT/'scripts'))
from canonical_cad_data_v4.converters.cadfs_to_dsl import audit_featurescript
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 rows=[json.loads(x) for x in open(BASE/'canary20/retry2/CANARY20_PER_CAD.jsonl') if x.strip()];cases=[]
 for r in rows:
  if r.get('DSL_GEOMETRY_PASS'):continue
  cid=r['cad_id'];base=BASE/'canary20/retry2/cases'/cid;text=(base/'source/source.fs').read_text(encoding='utf-8',errors='replace').lower();audit=audit_featurescript(text)
  # These flags name explicit CADFS semantics. Generic qCreatedBy/sketchPlane
  # occurs in ordinary principal-plane sketches and is intentionally excluded.
  extent=any(x in text for x in ('startoffset','endoffset','startbound','endbound','oppositedirection','negativedirection'))
  symmetric=any(x in text for x in ('symmetric','twosided','seconddirection'))
  face=any(x in text for x in ('faceattached','evfacetangentplane','faceattachment'))
  unsupported=bool(audit.get('unsupported'))
  dsl=(base/'cad_target.dsl').read_text();tree=ast.parse(dsl);bodies=sum(isinstance(x,ast.Assign) and getattr(x.targets[0],'id','').startswith('body_') for x in tree.body if x.targets if isinstance(x,ast.Assign))
  fs_extrude=audit['counts'].get('extrude',0)
  if symmetric:primary='SYMMETRIC_EXTRUDE'
  elif extent:primary='EXTRUDE_EXTENT'
  elif face:primary='FACE_ATTACHED_SKETCH'
  elif unsupported:primary='UNSUPPORTED_SEMANTICS'
  elif fs_extrude!=bodies:primary='SOURCE_DSL_MAPPING_ERROR'
  else:primary='UNKNOWN'
  secondary=[]
  if audit['counts'].get('circle',0)>1 or (audit['counts'].get('circle',0) and audit['counts'].get('line',0)):secondary.append('PROFILE_HOLE')
  cases.append({'cad_id':cid,'source_id':r['source_id'],'prefix_geometry_available':'NO','FIRST_DIVERGENCE_OP':None,'PRIMARY_FAILURE_MODE':primary,'SECONDARY_FAILURE_MODES':secondary,'explicit_semantic_evidence':{'extent':extent,'symmetric_or_two_sided':symmetric,'face_attached':face,'source_extrude_count':fs_extrude,'dsl_body_count':bodies},'chamfer_rel':r.get('chamfer_rel'),'coverage_02':r.get('coverage_02')})
 c=Counter(x['PRIMARY_FAILURE_MODE'] for x in cases);out={'FAILED_CASES':len(cases),'PREFIX_GEOMETRY_AUDIT_AVAILABLE':'NO','classification_policy':'explicit FeatureScript semantic fields only; generic qCreatedBy/sketchPlane excluded','PRIMARY_FAILURE_COUNTS':dict(c),'TOP_5_FAILURE_MODES':c.most_common(5),'MOST_COMMON_FIRST_DIVERGENCE_OPERATION':'UNAVAILABLE_SOURCE_INTERMEDIATE_BODIES','cases':cases}
 dump(OUT/'CANARY14_OPERATION_FAILURE_SUMMARY_V2.json',out);(OUT/'CANARY14_OPERATION_FAILURE_SUMMARY_V2.md').write_text('# Corrected Canary14 semantic audit\n\n```json\n'+json.dumps(out,indent=2)+'\n```\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
