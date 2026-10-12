import json, math, runpy, traceback
from pathlib import Path
import cadquery as cq
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; V3=ROOT/'ours3/p3_xpart_20case_compact_ir_v3'; cid='case_014'
gen=(EXP/'eval/generated_02.v3').read_text(); gen=gen[:gen.find('\n<|') if '\n<' in gen else len(gen)]
lines=[x.strip() for x in gen.splitlines() if x.strip()]; qs=[]
for x in lines:
    if x.startswith('Q '): qs += [int(v) for v in x.split()[1:]]
n=int(next(x.split()[1] for x in lines if x.startswith('N ')))
gt=[]
for x in (V3/'compact_ir_v3/case_014.v3').read_text().splitlines():
    if x.startswith('Q '): gt += [int(v) for v in x.split()[1:]]
first=next((i for i,(a,b) in enumerate(zip(gt,qs)) if a!=b),None)
result={'free_generation':{'case_id':cid,'gt_q_n':len(gt),'generated_q_n':len(qs),'free_token_exact':qs==gt,'first_q_divergence':first,'natural_eos':gen.rstrip().endswith('E')}}
v1=V3.parent/'p3_xpart_20case_compact_ir_v1'; qm=json.loads((v1/'quantization'/f'{cid}.json').read_text()); source=next(x for x in json.loads((v1/'CASE_MANIFEST.json').read_text())['cases'] if x['CASE_ID']==cid)['CAD_PATH']; params=runpy.run_path(source)['PARAMETERS']; it=iter(qs)
def walk(x):
    if isinstance(x,dict): return {k:walk(v) for k,v in x.items()}
    if isinstance(x,list): return [walk(v) for v in x]
    if isinstance(x,float) and math.isfinite(x):
        q=next(it); return qm['lo']+(q/16383.0)*(qm['hi']-qm['lo'])
    return x
newp=walk(params); txt=Path(source).read_text(); pos=txt.find('PARAMETERS'); a=txt.find("'''",pos)+3; b=txt.find("'''",a); cp=EXP/'eval/tank_generated_compiler.py'; cp.write_text(txt[:a]+json.dumps(newp,separators=(',',':'))+txt[b:])
try:
    ns=runpy.run_path(str(cp)); shape=ns['build'](); result['brep_valid']=bool(shape.isValid() and len(shape.Solids())>=1); outstep=EXP/'eval/tank_generated.step'; cq.exporters.export(shape,str(outstep)); rb=cq.importers.importStep(str(outstep)).val(); result['step_export']=outstep.exists(); result['step_readback']=bool(rb.isValid()); canon=cq.importers.importStep(str(V3/'step_v3/case_014.step')).val(); result['volume_generated']=float(rb.Volume()); result['volume_canonical']=float(canon.Volume()); result['volume_abs_error']=abs(result['volume_generated']-result['volume_canonical']); result['geometry_equivalence']=result['volume_abs_error'] <= max(1e-12,abs(result['volume_canonical'])*1e-9)
except Exception: result['error']=traceback.format_exc()
(EXP/'eval/TANK_PART029_GATE.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
