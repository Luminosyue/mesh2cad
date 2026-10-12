"""Engineering-only transform/reload test; excluded from dataset and quality counts."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
from pathlib import Path
import numpy as np, cadquery as cq
from p3_assemble import assembly_code, dump
O=Path(__file__).resolve().parents[1]
d=O/'integrity'/'assembly_fixture';d.mkdir(exist_ok=True)
parts=[]
for i,(s,t) in enumerate([(0.7,[.1,-.2,.3]),(.25,[-.6,.4,-.1])]):
 p=d/f'fixture_{i}.py';p.write_text('import cadquery as cq\nresult=cq.Workplane("XY").box(1,0.6,0.4)\n')
 T=np.eye(4);T[:3,:3]*=s;T[:3,3]=t
 parts.append(({'world_transform':T.tolist(),'local_to_original_object':T.tolist()},{'cad_program_path':str(p)}))
code=assembly_code(parts);(d/'assembly.py').write_text(code);scope={};exec(code,scope);s=scope['result'].val();cq.exporters.export(s,str(d/'fixture.step'));r=cq.importers.importStep(str(d/'fixture.step')).val()
expected=sum((scale**3)*.6*.4 for scale in [.7,.25]);volume_error=abs(r.Volume()-expected)
actual=sorted([list(x.Center().toTuple()) for x in r.Solids()]);target=sorted([[.1,-.2,.3],[-.6,.4,-.1]])
center_error=float(np.max(np.abs(np.array(actual)-np.array(target))))
passed=r.isValid() and len(r.Solids())==2 and volume_error<1e-9 and center_error<1e-9
out={'engineering_test_only':True,'included_in_dataset_counts':False,'pass':passed,'solid_count':len(r.Solids()),'volume_error':volume_error,'center_error':center_error,'note':'This verifies assembly code and STEP reload, not success on any source object.'}
dump(d/'result.json',out);print(json.dumps(out));assert passed
