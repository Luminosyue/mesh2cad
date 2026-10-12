from __future__ import annotations
import ast, hashlib, json, re, subprocess
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OLD=ROOT/'ours3/cadquery_output_feasibility_canary_v1'
OUT=ROOT/'ours3/cadquery_native_cohort_completion_v1'
TANK=ROOT/'mesh_to_cad_stage1_坦克复杂组合体/mesh_to_cad_stage1/export_step_cadquery.py'
FORBIDDEN={'os','sys','subprocess','socket','requests','eval','exec','open','__import__','importlib','while'}
TAX={'extrude':'EXTRUDE','revolve':'REVOLVE','fillet':'FILLET','chamfer':'CHAMFER','union':'BOOLEAN','cut':'BOOLEAN','intersect':'BOOLEAN','loft':'LOFT','sweep':'SWEEP','shell':'SHELL','pattern':'PATTERN','mirror':'MIRROR','hole':'HOLE'}
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
def inspect(p):
    t=ast.parse(p.read_text()); calls=[]; imports=[]
    for n in ast.walk(t):
        if isinstance(n,ast.Import): imports += [a.name for a in n.names]
        elif isinstance(n,ast.ImportFrom): imports.append(n.module or '')
        elif isinstance(n,ast.Call): calls.append(ast.unparse(n.func))
    ops=sorted({TAX[k] for c in calls for k in TAX if c.lower().endswith(k)})
    bad=sorted({c for c in calls if c.split('.')[0] in FORBIDDEN} | ({'while'} if any(isinstance(n,ast.While) for n in ast.walk(t)) else set()))
    return {'ast_parse':True,'imports':sorted(set(imports)),'api_calls':sorted(set(calls)),'operation_list':ops,'whitelist_pass':not bad,'forbidden':bad}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    old=json.loads((OLD/'CADQUERY_DATA_DISCOVERY.json').read_text())
    rows=[]
    for r in old['cases']:
        p=inspect(Path(r['source_path'])); rows.append({'cad_id':r['cad_id'],'python_path':r['source_path'],'step_path':r['step_path'],'source_program_sha256':r['source_program_hash'],'step_sha256':r['step_sha256'],'execution_status':'PASS' if r['source_exec'] else 'FAIL','step_reload':'PASS' if r['step_reload'] else 'FAIL','pairing_evidence':'dataset ground_truth.py/ground_truth.step pair; source execution and STEP reload recorded','geometry_pair_status':'CANDIDATE','operation_list':p['operation_list'],'ast_parse':'PASS','whitelist_pass':p['whitelist_pass'],'imports':p['imports'],'api_calls':p['api_calls']})
    (OUT/'CURRENT_CADQUERY6_AUDIT.json').write_text(json.dumps({'count':len(rows),'rows':rows},indent=2)+'\n')
    tank={"cad_id":"controlled_tank","python_path":str(TANK),"step_path":str(ROOT/'mesh_to_cad_stage1_坦克复杂组合体/mesh_to_cad_stage1/outputs_batch_cases/controlled_tank/model.step'),"ast_parse":"PASS","cadquery_import_present":"cadquery" in TANK.read_text(),'execution_status':'FAIL','failure_type':'EXPORT_ONLY_SCRIPT','failure_detail':'requires --input and --output; wrapper around an existing reconstruction/export pipeline, not a standalone parameter construction program','cadquery_native_program':'NO','recoverable_runtime_mismatch':'NO','counted_in_cohort':False}
    (OUT/'TANK_CADQUERY_SOURCE_AUDIT.json').write_text(json.dumps(tank,indent=2)+'\n')
    (OUT/'LOCAL_CADQUERY_PAIR_DISCOVERY.json').write_text(json.dumps({'root':str(ROOT),'verified_pairs':len(rows),'additional_reliable_pairs':0,'excluded':[tank],'search_policy':'local source/STEP only; no CADFS translation and no synthetic padding'},indent=2)+'\n')
    counts={k:sum(k in r['operation_list'] for r in rows) for k in ['EXTRUDE','BOOLEAN','REVOLVE','FILLET','CHAMFER','LOFT','SWEEP','SHELL','PATTERN','MIRROR','HOLE']}
    (OUT/'LOCAL_CADQUERY_OPERATION_INVENTORY.json').write_text(json.dumps(counts,indent=2)+'\n')
    (OUT/'CADQUERY_PAIR_GEOMETRY_VERIFICATION.jsonl').write_text(''.join(json.dumps({'cad_id':r['cad_id'],'pair_verified':'PENDING_STRICT_GEOMETRY_COMPARISON','source_step':r['step_path'],'provided_step':r['step_path'],'reason':'source wrapper exports to the paired path; no independent generated copy retained'},sort_keys=True)+'\n' for r in rows))
    report={'CURRENT_GATE':'CADQUERY_NATIVE_COHORT_STILL_INCOMPLETE','LOCAL_NATIVE_PAIR_N':len(rows),'EXTERNAL_NATIVE_PAIR_ADDED':0,'FINAL_CANARY_N':len(rows),'SOURCE_PARSE':f'{sum(r["ast_parse"]=="PASS" for r in rows)}/{len(rows)}','SOURCE_EXEC':f'{sum(r["execution_status"]=="PASS" for r in rows)}/{len(rows)}','STEP_RELOAD':f'{sum(r["step_reload"]=="PASS" for r in rows)}/{len(rows)}','PAIR_GEOMETRY_VERIFIED':'NOT_ESTABLISHED','MISSING_CASE_N':8-len(rows),'MISSING_OPERATION_TYPES':['FILLET','CHAMFER','REVOLVE','MIXED'],'TANK_CADQUERY_NATIVE_PROGRAM':'NO','TANK_EXEC_FAILURE_REASON':'EXPORT_ONLY_SCRIPT','COUNTED_IN_COHORT':'NO','TRAINING_RUN':'NO','DECODE_RUN':'NO','SONATA_CHANGED':'NO','C2_CHANGED':'NO','PLACEMENT_CHANGED':'NO','SPATIALLM_CHANGED':'NO','DSL_CHANGED':'NO','CADQUERY_NATIVE_CANARY8_READY':'NO','NEXT_STEP':'MORE_NATIVE_DATA_REQUIRED'}
    (OUT/'CADQUERY_NATIVE_CANARY8_MANIFEST.json').write_text(json.dumps({'count':len(rows),'status':'INCOMPLETE_NOT_CANARY8','records':rows},indent=2)+'\n')
    (OUT/'FINAL_REPORT.json').write_text(json.dumps(report,indent=2)+'\n'); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
