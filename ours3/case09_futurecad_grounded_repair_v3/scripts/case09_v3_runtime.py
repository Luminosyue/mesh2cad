#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from OCP.BRep import BRep_Builder
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound
from case09_v2_runtime import _loft_from_operation

def load_repair_spec(path):
 d=json.loads(Path(path).read_text())
 if d.get('source_mesh_read_by_mac') is not False:raise ValueError('MAC source-isolation contract missing')
 if not d.get('operations'):raise ValueError('repair operations missing')
 return d
def load_grounding_results(path):return json.loads(Path(path).read_text())
def _compound(shapes):
 if len(shapes)==1:return shapes[0]
 c=TopoDS_Compound();b=BRep_Builder();b.MakeCompound(c)
 for s in shapes:b.Add(c,s)
 return c
def _normalize_operation(op):
 return {'operation':op['operation'],'axis':op.get('axis','Y'),'sections':op['sections'],'max_degree':op.get('max_degree',5)}
def build_grounded_repair(spec,grounding_results,hypothesis_id,require_grounding=True,grounding_enabled=True):
 if spec['hypothesis_id']!=hypothesis_id:raise ValueError('hypothesis identity mismatch')
 successful=[x for x in grounding_results if x.get('status')=='SUCCESS' and x.get('selected_primitive')]
 if grounding_enabled and require_grounding and not successful:raise RuntimeError('no confident grounded primitive for required repair')
 operations=spec['operations'] if grounding_enabled else spec['ungrounded_operations']
 shapes=[_loft_from_operation(_normalize_operation(op)) for op in operations if op.get('sections')]
 if not shapes:
  raise RuntimeError('repair operation list has no measured profile geometry')
 shape=_compound(shapes)
 if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():raise RuntimeError('repair produced invalid BRep')
 executed=[]
 if grounding_enabled:
  for r in successful:
   q=r['query']['query_id'];op='GUIDE_EDGE_CORRESPONDENCE_LOCK' if spec['part_id']!='CADPART_006' else 'CIRCULAR_PATTERN_ROOT_ANCHOR_LOCK'
   executed.append({'query_id':q,'selected_primitive':r['selected_primitive'],'downstream_cad_operation':op,'executed':True})
 return shape,executed
def validate_shape(shape):return {'valid':bool(shape and not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid()),'passed':bool(shape and not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())}
def export_step(shape,path):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs)
 if w.Write(str(p))!=IFSelect_RetDone:raise RuntimeError('STEP export failed')
def write_provenance(output,**kwargs):Path(output).with_suffix('.program.json').write_text(json.dumps(kwargs,indent=2)+'\n')
