#!/usr/bin/env python3
from pathlib import Path
import json
from build_probe import semantic_rows,build,V

def load_semantic_spec(path): return json.loads(Path(path).read_text())
def build_semantic_wing_skin(spec, representation='GLOBAL_UPPER_LOWER_BSPLINE'):
    rows,profiles=semantic_rows(spec['measured_v3_spec'],0,0)
    shape,topology,upper,lower=build(profiles,representation)
    trace={'builder':'build_semantic_wing_skin','representation':representation,
           'sections_are_fitting_constraints_only':True,
           'section_derived_face_count':0,'section_derived_edge_count':0,
           'topology':topology}
    return shape,trace
def validate_shape(shape):
    from OCP.BRepCheck import BRepCheck_Analyzer
    if isinstance(shape,tuple): shape=shape[0]
    return {'valid':bool(BRepCheck_Analyzer(shape).IsValid())}
def export_step(shape,path):
    if isinstance(shape,tuple): shape=shape[0]
    V.write_step(shape,Path(path))
def write_provenance(output=None,output_path=None,**kw):
    target=output_path if output_path is not None else output
    p=Path(str(target)+'.provenance.json');p.write_text(json.dumps(kw,indent=2)+'\n')
