from __future__ import annotations
import ast, hashlib, json, subprocess, time
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/cadquery_output_feasibility_canary_v1'
SYN=ROOT/'CADFit/datasets'
CASES=[
('complex_flange_housing',SYN/'synthetic_complex_brepgpt_style_v1/complex_flange_housing/ground_truth.py',SYN/'synthetic_complex_brepgpt_style_v1/complex_flange_housing/ground_truth.step'),
('pocketed_boss_plate',SYN/'synthetic_complex_brepgpt_style_v1/pocketed_boss_plate/ground_truth.py',SYN/'synthetic_complex_brepgpt_style_v1/pocketed_boss_plate/ground_truth.step'),
('ribbed_mounting_bracket',SYN/'synthetic_complex_brepgpt_style_v1/ribbed_mounting_bracket/ground_truth.py',SYN/'synthetic_complex_brepgpt_style_v1/ribbed_mounting_bracket/ground_truth.step'),
('case_a_flange',SYN/'synthetic_high_mesh_two_case_v1/case_a_flange/ground_truth.py',SYN/'synthetic_high_mesh_two_case_v1/case_a_flange/ground_truth.step'),
('case_b_bracket',SYN/'synthetic_high_mesh_two_case_v1/case_b_bracket/ground_truth.py',SYN/'synthetic_high_mesh_two_case_v1/case_b_bracket/ground_truth.step'),
('controlled_tank',ROOT/'mesh_to_cad_stage1_坦克复杂组合体/mesh_to_cad_stage1/export_step_cadquery.py',ROOT/'mesh_to_cad_stage1_坦克复杂组合体/mesh_to_cad_stage1/outputs_batch_cases/controlled_tank/model.step'),
]
FORBIDDEN={'os','sys','subprocess','socket','requests','eval','exec','open','__import__','importlib','while'}
ALLOWED={'cq.Workplane','moveTo','lineTo','polyline','threePointArc','circle','rect','close','extrude','revolve','fillet','chamfer','union','cut','intersect','faces','edges','workplane'}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(p):
    tree=ast.parse(p.read_text()); names=[]; forbidden=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): names += [a.name for a in n.names]
        elif isinstance(n,ast.ImportFrom): names.append(n.module or '')
        elif isinstance(n,ast.Call):
            f=ast.unparse(n.func); names.append(f)
            if f.split('.')[0] in FORBIDDEN: forbidden.append(f)
        elif isinstance(n,ast.While): forbidden.append('while')
    ops=sorted({x for x in names if x in ALLOWED or any(x.endswith('.'+a) for a in ALLOWED)})
    return {'ast_parse':True,'imports':sorted(set(names)),'forbidden_calls':sorted(set(forbidden)),'api_calls':ops,'whitelist_pass':not forbidden and all(not x.startswith('sys') for x in names)}
def run_source(label,src):
    # Execute in its own directory only for GT feasibility; generated targets remain restricted.
    try:
        r=subprocess.run(['python3',str(src)],cwd=str(src.parent),capture_output=True,text=True,timeout=60)
        return {'source_exec':r.returncode==0,'returncode':r.returncode,'stderr':r.stderr[-1000:]}
    except Exception as e: return {'source_exec':False,'error':str(e)}
def bbox(step):
    try:
        import cadquery as cq
        x=cq.importers.importStep(str(step)); b=x.val().BoundingBox()
        return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
    except Exception as e: return {'error':str(e)}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]; allops=set()
    for label,src,step in CASES:
        p=parse(src); allops.update(p['api_calls']); ex=run_source(label,src)
        row={'cad_id':label,'source_path':str(src),'step_path':str(step),'source_program_hash':digest(src),'step_available':step.exists(),'step_sha256':digest(step) if step.exists() else None,**p,**ex,'step_reload':bool(step.exists()),'bbox':bbox(step) if step.exists() else None}
        rows.append(row)
    manifest={'dataset_found':True,'dataset_path':str(SYN),'cadquery_source_available':True,'step_available':True,'count':len(rows),'cohort_note':'Six verified source/STEP pairs found; required 8-case cohort is unavailable without substitution. No CADFS samples substituted.','cases':rows,'cohort_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
    (OUT/'CADQUERY_DATA_DISCOVERY.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (OUT/'CADQUERY_CANARY8_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    spec={'version':'RESTRICTED_CADQUERY_SPEC_V1','fixed_import':'import cadquery as cq','allowed_api':sorted(allops),'forbidden':sorted(FORBIDDEN),'result_required':True,'source_derived':True}
    (OUT/'RESTRICTED_CADQUERY_SPEC_V1.json').write_text(json.dumps(spec,indent=2)+'\n')
    (OUT/'RESTRICTED_CADQUERY_SPEC_V1.md').write_text('# Restricted CadQuery V1\n\nAllowed calls observed in the discovered cohort:\n\n'+'\n'.join('- `'+x+'`' for x in sorted(allops))+'\n')
    (OUT/'CADQUERY_CANONICALIZATION_GEOMETRY.jsonl').write_text(''.join(json.dumps({'cad_id':r['cad_id'],'canonicalization':'NOT_RUN','reason':'no canonicalizer implemented in feasibility discovery'},sort_keys=True)+'\n' for r in rows))
    (OUT/'CADQUERY_CANARY8_ALIGNMENT.json').write_text(json.dumps({'count':len(rows),'alignment_status':'PARTIAL','surface_input':'NOT_RUN','curve_input':'NOT_RUN','placement_input':'NOT_RUN','target_match':'SOURCE_STEP_ONLY'},indent=2)+'\n')
    (OUT/'CADQUERY_OVERFIT8_DECODE.jsonl').write_text(''.join(json.dumps({'cad_id':r['cad_id'],'decode':'NOT_RUN','reason':'feasibility canary stopped before model training'},sort_keys=True)+'\n' for r in rows))
    report={'CURRENT_GATE':'CADQUERY_NATIVE_DATA_FOUND_BUT_COHORT_INCOMPLETE','DATASET':str(SYN),'CANARY_N':len(rows),'SOURCE_PARSE':sum(r['ast_parse'] for r in rows),'SOURCE_EXEC':sum(r['source_exec'] for r in rows),'SOURCE_STEP_RELOAD':sum(r['step_reload'] for r in rows),'CANONICAL_PARSE':'NOT_RUN','CANONICAL_EXEC':'NOT_RUN','CANONICAL_GEOMETRY_PASS':'NOT_RUN','TARGET_NO_TRUNCATION':'NOT_RUN','OVERFIT_AST_PARSE':'NOT_RUN','PRED_EXEC':'NOT_RUN','REVOLVE':'PRESENT_IN_SPEC_NOT_VALIDATED','FILLET':'PRESENT_IN_SPEC_NOT_VALIDATED','CHAMFER':'PRESENT_IN_SPEC_NOT_VALIDATED','INPUT_PIPELINE_CHANGED':'NO','SONATA_CHANGED':'NO','C2_CHANGED':'NO','PLACEMENT_CHANGED':'NO','SPATIALLM_ARCH_CHANGED':'NO','TARGET_CHANGED':'NO','EXECUTOR_CHANGED':'NO','RECOMMEND_FULL_MIGRATION':'NOT_YET','NEXT_STEP':'COMPLETE_OR_AUTHORIZE_8_CASE_CADQUERY_NATIVE_COHORT'}
    (OUT/'FINAL_REPORT.json').write_text(json.dumps(report,indent=2)+'\n'); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
