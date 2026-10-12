"""Semantic CADFS capability classifier V2; no source mutation or fallback."""
from __future__ import annotations
import re
from pathlib import Path
from canonical_cad_data_v4.converters.cadfs_to_dsl import cadfs_to_dsl

ADVANCED = {
 "revolve":"REQUIRES_REVOLVE","mirror":"REQUIRES_MIRROR","loft":"REQUIRES_LOFT",
 "sweep":"REQUIRES_SWEEP","fillet":"REQUIRES_FILLET","chamfer":"REQUIRES_CHAMFER",
 "shell":"REQUIRES_SHELL","pattern":"REQUIRES_PATTERN",
}
OP_PATTERNS = {
 "revolve":r"\brevolve\s*\(","mirror":r"\b(?:opMirror|mirror)\s*\(",
 "loft":r"\bloft\s*\(","sweep":r"\bsweep\s*\(","fillet":r"\b(?:opFillet|fillet)\s*\(",
 "chamfer":r"\b(?:opChamfer|chamfer)\s*\(","shell":r"\b(?:opShell|shell)\s*\(",
 "pattern":r"\b(?:circularPattern|linearPattern|opPattern)\s*\(",
}
def _has(p,t): return bool(re.search(p,t,re.S))
def _line_gap(t):
 # Only recognizes labelled rectangle loops; it does not normalize them.
 rows={}
 for name,x1,y1,x2,y2 in re.findall(r'skLineSegment\(sketch,\s*"([^"]+)",\s*\{"start"\s*:\s*v\(([-.0-9]+),\s*([-.0-9]+)\).*?"end"\s*:\s*v\(([-.0-9]+),\s*([-.0-9]+)',t):
  rows[name]=(float(x1),float(y1),float(x2),float(y2))
 for stem in set(k.rsplit(".",1)[0] for k in rows if "." in k):
  q=[v for k,v in rows.items() if k.startswith(stem+".")]
  pts=[(x,y) for e in q for x,y in ((e[0],e[1]),(e[2],e[3]))]
  if len(pts)==8 and len(set(pts))>4: return True
 return False
def requirements(text):
 req=set()
 for op,pat in OP_PATTERNS.items():
  if _has(pat,text): req.add(ADVANCED[op])
 if _has(r'\bcPlane\s*\(',text): req.add('REQUIRES_CONSTRUCTION_PLANE')
 if _has(r'(?:CAP_FACE|SWEPT_FACE|IMPRINT|qCreatedBy\(id\+)',text) and _has(r'newSketch\s*\(',text): req.add('REQUIRES_FACE_ATTACHED_SKETCH')
 if _has(r'\bhole\s*\(',text): req.add('REQUIRES_HOLE_SEMANTICS')
 if _has(r'\bskEllipse\s*\(',text): req.add('REQUIRES_ELLIPSE')
 if _has(r'\bsk(?:Spline|Nurbs)\s*\(',text): req.add('REQUIRES_BSPLINE')
 if _has(r'\bskArc\s*\(',text): req.add('REQUIRES_ARC_EXECUTION')
 if len(re.findall(r'\bskCircle\s*\(',text))>1 or (_has(r'\bskCircle\s*\(',text) and _has(r'\bskLine(?:Segment)?\s*\(',text)):
  req.add('REQUIRES_PROFILE_TOPOLOGY')
 if len(re.findall(r'\bextrude\s*\(',text)) != len(re.findall(r'newSketch\s*\(',text)) or _has(r'F\d+\.imprint|qSketchRegion|makeQuery\(',text):
  # A plain qSketchRegion immediately paired with an extrusion is ordinary; named/imprint and cardinality patterns are identity requirements.
  if _has(r'F\d+\.imprint|makeQuery\(',text) or len(re.findall(r'\bextrude\s*\(',text)) != len(re.findall(r'newSketch\s*\(',text)):
   req.add('REQUIRES_PROFILE_REFERENCE')
 if _line_gap(text): req.add('REQUIRES_TOLERANCE_NORMALIZATION')
 return sorted(req)
def classify_text(text):
 req=requirements(text)
 if req: return {'new_classifier_label':'+'.join(req),'required_capabilities':req,'lossless_parse_possible':False,'parse_result':'NOT_ATTEMPTED_EXTENSION_REQUIRED','failure_reason':'EXTENSION_REQUIRED:'+','.join(req)}
 try:
  cadfs_to_dsl(text)
  return {'new_classifier_label':'CORE_SUPPORTED','required_capabilities':[],'lossless_parse_possible':True,'parse_result':'PARSE_OK','failure_reason':None}
 except Exception as e:
  # No silent fallback: conservatively mark the specific unexpressed semantic class.
  reason=f'{type(e).__name__}:{e}'
  if 'plane' in reason: cap='REQUIRES_CONSTRUCTION_PLANE'
  elif 'circle' in reason or 'polygon' in reason: cap='REQUIRES_PROFILE_TOPOLOGY'
  elif 'mismatch' in reason: cap='REQUIRES_PROFILE_REFERENCE'
  else: cap='REQUIRES_PROFILE_TOPOLOGY'
  return {'new_classifier_label':cap,'required_capabilities':[cap],'lossless_parse_possible':False,'parse_result':'PARSE_FAIL','failure_reason':reason}
def classify_file(path: Path):
 return classify_text(Path(path).read_text(encoding='utf-8',errors='replace'))
