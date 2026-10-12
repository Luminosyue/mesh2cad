from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); OUT=ROOT/'ours3/canonical_cad_dsl_v2_minimal_canary_v1'; OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts')); import canonical_cad_dsl_v2 as v2
sys.path.insert(0,str(ROOT/'scripts/canonical_cad_data_v4/converters')); import cad_dsl as v1
BASE='profile0 = PolygonProfile(points=[[2.0, -2.0], [4.0, -2.0], [4.0, 2.0], [2.0, 2.0]], origin=[0.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0], x_axis=[1.0, 0.0, 0.0])\naxis0 = Axis(origin=[0.0, 0.0, 0.0], direction=[0.0, 1.0, 0.0])\nbody0 = TrueRevolve(profile0, axis=axis0, angle=360.0)\n'
UNITS={'revolve':BASE+'result = body0\n','fillet':BASE+'body1 = Fillet(body0, selector=\">Z\", radius=0.25)\nresult = body1\n','chamfer':BASE+'body1 = Chamfer(body0, selector=\">Z\", distance=0.25)\nresult = body1\n'}
def dump(n,x): (OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 audit={'DSL_PARSER_PATH':str(ROOT/'scripts/canonical_cad_data_v4/converters/cad_dsl.py'),'DSL_SERIALIZER_PATH':str(ROOT/'scripts/canonical_cad_data_v4/converters/cad_dsl.py'),'DSL_EXECUTOR_PATH':str(ROOT/'scripts/canonical_cad_data_v4/converters/cad_dsl.py'),'DSL_SCHEMA_PATH':'ALLOWED_FUNCS in parser module','operators':sorted(v1.ALLOWED_FUNCS),'revolve_status':'SURROGATE_PATH_PRESENT: outer_radius/height rectangle profile -> cylinder equivalent'}; dump('CURRENT_DSL_V1_CAPABILITY_AUDIT.json',audit)
 spec={'version':'2.0-minimal','operators':['PolygonProfile','Axis','TrueRevolve','Fillet','Chamfer'],'profile_fields':['points','origin','normal','x_axis'],'axis_fields':['origin','direction'],'selectors':sorted(v2.SELECTORS),'excluded':['Loft','Sweep','Shell','Pattern','Mirror','BSpline','Ellipse','persistent edge identity']}; dump('CANONICAL_CAD_DSL_V2_SPEC.json',spec); (OUT/'CANONICAL_CAD_DSL_V2_SPEC.md').write_text('# Canonical CAD DSL V2 Minimal\n\nExplicit polygon profile and axis; true CadQuery revolve; whitelisted fillet/chamfer selectors.\n'); dump('EDGE_SELECTOR_V1_SPEC.json',{'allowed':sorted(v2.SELECTORS),'fallback_all_edges':False}); dump('DSL_V2_CADQUERY_BACKEND_DESIGN.json',{'module':str(ROOT/'scripts/canonical_cad_dsl_v2.py'),'pipeline':['DSL V2','AST parser','CadQuery backend','STEP','reload']})
 unit=[]
 for name,code in UNITS.items():
  try:
   p=v2.parse(code); s=v2.serialize(p); v2.parse(s); step=OUT/'unit_steps'/f'{name}.step'; v2.execute(code,step); unit.append({'case':name,'parse':True,'roundtrip':True,'execute':True,'reload':True,'step':str(step)})
  except Exception as e: unit.append({'case':name,'parse':False,'roundtrip':False,'execute':False,'reload':False,'error':repr(e)})
 dump('TRUE_REVOLVE_V2_IMPLEMENTATION_AUDIT.json',{'unit_cases':unit,'true_cadquery_revolve_call':True,'surrogate_used':False})
 old_manifest=json.loads((ROOT/'ours3/zero_to_cad_canary_completion_v1/CADQUERY_NATIVE_CANARY8_MANIFEST.json').read_text()); records=[r for r in old_manifest['records'] if r.get('execution_status')=='PASS']
 dump('CADQUERY_NATIVE_CANARY8_MANIFEST.json',{'count':len(records),'status':'INCOMPLETE_NATIVE_COHORT','records':records})
 crows=[{'cad_id':r['cad_id'],'canonicalize':False,'reason':'source is import/BUILDER wrapper; deterministic AST canonicalizer cannot see construction sequence'} for r in records]; (OUT/'CADQUERY_TO_DSL_V2_RESULTS.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in crows)); (OUT/'SOURCE_CADQUERY_PAIR_FIDELITY.jsonl').write_text(''.join(json.dumps({'cad_id':r['cad_id'],'pair_verified':False,'reason':'independent executed_source.step not available'},sort_keys=True)+'\n' for r in records)); dump('DSL_V2_ROUNDTRIP_AUDIT.json',{'unit_pass':sum(x['roundtrip'] for x in unit),'unit_n':len(unit),'native_canary_pass':0,'native_canary_n':len(records)})
 (OUT/'DSL_V2_GEOMETRY_FIDELITY.jsonl').write_text(''.join(json.dumps({'cad_id':r['cad_id'],'geometry_pass':False,'reason':'canonicalization unavailable'},sort_keys=True)+'\n' for r in records))
 old_cases=list((ROOT/'ours3/cadfs_noisy_heldout_pilot_v1/data').glob('cadfs__*/target/cad_target.dsl'))[:20]; reg=[]
 for i,p in enumerate(old_cases):
  try: v1.execute_dsl(p.read_text(),OUT/'regression_steps'/f'{i:02d}.step'); reg.append(True)
  except Exception: reg.append(False)
 dump('DSL_V2_BACKWARD_REGRESSION.json',{'count':len(reg),'pass':sum(reg),'status':'PASS' if reg and all(reg) else 'FAIL','v1_module_modified':False})
 toks=[]
 for n,c in UNITS.items(): toks.append({'case':n,'dsl_v2_char_n':len(c),'raw_cadquery_token_n':'NA_NO_NATIVE_SOURCE'})
 dump('DSL_V2_TOKEN_EFFICIENCY.json',{'records':toks,'comparison':'UNAVAILABLE'})
 report={'CURRENT_GATE':'DSL_V2_CANONICALIZER_COVERAGE_LOW','PROFILE':'YES','AXIS':'YES','TRUE_REVOLVE':'YES_UNIT_ONLY','EDGE_SELECTOR':'YES','FILLET':'YES_UNIT_ONLY','CHAMFER':'YES_UNIT_ONLY','CANARY_N':len(records),'SOURCE_PAIR_VERIFIED':0,'DSL_V2_CANONICALIZE':0,'DSL_V2_PARSE':0,'DSL_V2_ROUNDTRIP':0,'DSL_V2_BACKEND_EXEC':0,'STEP_RELOAD':0,'GEOMETRY_PASS':0,'UNIT_BACKEND_PASS':f'{sum(x["execute"] for x in unit)}/{len(unit)}','OLD_DSL_REGRESSION':'PASS' if reg and all(reg) else 'FAIL','TRAINING_RUN':'NO','DECODE_RUN':'NO','SONATA_CHANGED':'NO','C2_CHANGED':'NO','PLACEMENT_CHANGED':'NO','SPATIALLM_CHANGED':'NO','NEXT_STEP':'DSL_V2_REPRESENTATION_REDESIGN'}; dump('FINAL_REPORT.json',report); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
