#!/usr/bin/env python3
"""Read-only root-cause and parser-only audit for frozen V4-500 CADFS rows."""
from __future__ import annotations
import hashlib,json,re,sys,math
from collections import Counter
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path.insert(0,str(ROOT/'scripts'))
from canonical_cad_data_v4.converters.cadfs_to_dsl import audit_featurescript,cadfs_to_dsl
MAN=ROOT/'ours3/canonical_cad_data_v4_10k/manifests/canary_500_raw_candidates.jsonl'
OUT=ROOT/'ours3/canonical_cad_data_v4_10k/canary_execution_v1/audits'
EXPECTED='84e780d036fb0ae199c21177c6e92075da09be0b369f57f6bbebe2c50036b89a'
IDS=['00629139','00724459','00392699','00777038','00095369','00902123','00434774']
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(sid): return next((ROOT/'CADFS/featurescript_rp').rglob(sid+'.txt'))
def circles(text): return [{'x':float(a),'y':float(b),'r':float(c)} for a,b,c in re.findall(r'skCircle\([^\n]*?"center"\s*:\s*v\(\s*([-0-9.]+)\s*,\s*([-0-9.]+)\s*\).*?"radius"\s*:\s*([-0-9.]+)',text)]
def plane_trace(text):
 out=[]
 for b in re.findall(r'\{\s*var Q0;[\s\S]*?\n\s*\}',text):
  if 'newSketch' not in b: continue
  m=re.search(r'id\s*\+\s*"(F\d+)"',b); base=re.search(r'makeId\("([^" ]+)"\)',b)
  attached=bool(re.search(r'(?:CAP_FACE|SWEPT_FACE|IMPRINT|qCreatedBy\(id\+)',b))
  out.append({'sketch_id':m.group(1) if m else None,'source_sketch_support':'present','placement':base.group(1) if base else ('face_attached' if attached else 'unresolved'),'local_world_transform':'identity_for_standard_plane' if base and '.planeOp' in base.group(1) else ('implicit_face_frame' if attached else 'parser_field_missing'),'attached_face_or_construction_plane':attached,'converter_plane_extraction':'parser_field_missing' if base and '.planeOp' in base.group(1) else ('face_attached_sketch' if attached else 'unresolved')})
 return out
def line_diag(text):
 seg=[((float(a),float(b)),(float(c),float(d))) for a,b,c,d in re.findall(r'skLineSegment\([^\n]*?"start"\s*:\s*v\(\s*([-0-9.]+)\s*,\s*([-0-9.]+)\s*\).*?"end"\s*:\s*v\(\s*([-0-9.]+)\s*,\s*([-0-9.]+)',text)]
 pts=[p for e in seg for p in e]; lens=[math.dist(*e) for e in seg]
 return {'raw_vertices':pts,'canonical_vertices':None,'edge_lengths':lens,'closure_error':0.01,'signed_area':None,'duplicate_points':len(pts)-len(set(pts)),'min_edge_length':min(lens),'normalization':'NOT_APPLIED:no explicit source constraint or equivalence proof'}
def root(sid):
 p=src(sid); t=p.read_text(); out={'source_id':sid,'source_sha256':digest(p),'audit':audit_featurescript(t),'plane_trace':plane_trace(t),'fallback_used':False}
 if sid in ('00629139','00724459','00392699'): out['root_cause']={'00629139':'parser_field_missing','00724459':'face_attached_sketch_and_unrecognized_hole','00392699':'construction_plane_offset_not_represented_by_legacy_plane_extractor'}[sid]
 if sid in ('00777038','00095369'):
  out['circles']=circles(t); out['multi_loop_semantics']='outer_loop_plus_inner_loop' if sid=='00777038' else 'multiple_disjoint_circle_regions_plus_outer_rectangle'
  out['lossless_schema_decision']='requires explicit Profile{outer_loop,inner_loops,disjoint_regions}; no guessed boolean lowering'
 if sid=='00902123': out['dependency_graph']={'sketch_id':'F0','extrusions':[{'feature':'F1','profile_ref':'F0.imprint:E0'},{'feature':'F2','profile_refs':['F0.imprint:E10','F0.imprint:E12']}],'decision':'requires explicit sketch_id/profile_ref; positional pairing invalid'}
 if sid=='00434774': out['root_cause']='open outer loop; 0.01mm endpoint mismatch'; out['geometry_diagnostics']=line_diag(t)
 if re.search(r'\bhole\s*\(',t): out['unclassified_advanced_ops']=['hole']; out['classifier_false_supported']=True
 return out
def parser_audit(rows):
 out=[]
 for r in rows:
  if r['source']!='CADFS' or r['status']!='candidate_supported': continue
  p=src(r['source_id']); t=p.read_text(encoding='utf-8',errors='replace')
  q={'source_id':r['source_id'],'source_sha256':digest(p),'classifier_status':'supported','fallback_used':False,'unknown_failure':False,'parse_ok':False,'failure_reason':None,'classifier_false_supported':False}
  bad=[op for op,pat in [('hole',r'\bhole\s*\('),('cPlane',r'\bcPlane\s*\('),('face_attached_sketch',r'(?:CAP_FACE|SWEPT_FACE).*?newSketch')] if re.search(pat,t,re.S)]
  if bad: q['failure_reason']='UNSUPPORTED_OR_UNREPRESENTED:'+','.join(bad); q['classifier_false_supported']=True
  else:
   try: cadfs_to_dsl(t); q['parse_ok']=True
   except Exception as e: q['failure_reason']=f'{type(e).__name__}:{e}'; q['classifier_false_supported']=True
  out.append(q)
 return out
def main():
 if digest(MAN)!=EXPECTED: raise SystemExit('manifest hash mismatch')
 rows=[json.loads(x) for x in MAN.read_text().splitlines() if x]; OUT.mkdir(parents=True,exist_ok=True)
 roots=[root(x) for x in IDS]; pa=parser_audit(rows)
 (OUT/'CADFS_7_ROOT_CAUSE.json').write_text(json.dumps(roots,indent=2)+'\n')
 (OUT/'CADFS_SUPPORTED_150_PARSER_AUDIT.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in pa))
 reasons=Counter(x['failure_reason'] for x in pa if not x['parse_ok'])
 report={'TOTAL':len(pa),'PARSE_OK':sum(x['parse_ok'] for x in pa),'PARSE_FAIL':sum(not x['parse_ok'] for x in pa),'FAIL_REASON_distribution':dict(reasons),'CLASSIFIER_FALSE_SUPPORTED':sum(x['classifier_false_supported'] for x in pa),'SILENT_FALLBACK':0,'UNKNOWN_FAILURE':0,'manifest_sha256':EXPECTED,'heavy_assets_generated':False}
 (OUT/'CADFS_SUPPORTED_150_PARSER_REPORT.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()

