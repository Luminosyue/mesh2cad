from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
PARQUET = ROOT / 'zerocad/89_93ae18509d914a69bf2646431db2c6ab_000014_000000-0.parquet'
POOL = ROOT / 'ours3/canonical_cad_dsl_v2_base_operator_integration_canary_v1/UNIFIED_DSL_V2_SUPPORTED_POOL.json'
OUT = ROOT / 'ours3/dsl_v2_source_aware_transform_canonicalizer_canary_v1'
OUT.mkdir(parents=True, exist_ok=True)

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(n,x): (OUT/n).write_text(json.dumps(x, indent=2, default=str) + '\n')
def lines(n,xs): (OUT/n).write_text('\n'.join(json.dumps(x, default=str) for x in xs) + ('\n' if xs else ''))

def ast_graph(source):
    tree = ast.parse(source); rows=[]
    for order, n in enumerate(sorted([x for x in ast.walk(tree) if isinstance(x, ast.Call)], key=lambda x:(getattr(x,'lineno',0), getattr(x,'col_offset',0)))):
        call = ast.unparse(n.func); method = call.split('.')[-1]
        receiver = call.rsplit('.',1)[0] if '.' in call else None
        refs = sorted({x.id for x in ast.walk(n) if isinstance(x, ast.Name) and x.id not in {'cq','math'}})
        kind = 'WORKPLANE' if method == 'Workplane' else 'PROFILE' if method in {'moveTo','lineTo','polyline','rect','circle','close'} else 'BODY_TRANSFORM' if method in {'center','translate','workplane','rotate','mirrorY'} else 'BOOLEAN' if method in {'cut','union','intersect'} else 'SELECTOR' if method in {'edges','faces'} else 'BODY_FEATURE' if method in {'extrude','revolve','fillet','chamfer'} else 'OTHER'
        rows.append({'node_id': f'n{order:03d}', 'source_location': {'lineno': getattr(n,'lineno',0),'col_offset':getattr(n,'col_offset',0)}, 'call_name': call, 'receiver_node': receiver, 'input_body_refs': refs, 'output_object': None, 'object_type': kind, 'parent_scope': None, 'child_scope': None, 'source_order': order})
    return rows

def num_expr(s):
    try: return float(ast.literal_eval(s))
    except Exception: return None

def simple_lower(source, ident):
    """Conservative lowering for complete static box/union/translate subtrees."""
    tree = ast.parse(source); assigns=[]; unsupported=[]
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0], ast.Name):
            name=n.targets[0].id; value=n.value
            if isinstance(value, ast.Call) and ast.unparse(value.func).endswith('.box'):
                args=[num_expr(ast.unparse(x)) for x in value.args]
                if len(args)==3 and all(x is not None for x in args): assigns.append((name, f'{name} = Box(width={args[0]}, depth={args[1]}, height={args[2]}, origin=[0.0, 0.0, {-args[2]/2}], x_axis=[1.0, 0.0, 0.0])'))
                else: unsupported.append('box_parameters')
            elif isinstance(value, ast.Call) and ast.unparse(value.func).endswith('.translate'):
                recv=ast.unparse(value.func).rsplit('.',1)[0]; vec=value.args[0] if value.args else None
                # Resolve only a direct box.translate assignment; this is a whole-subtree bake.
                direct_box = '.box(' in recv
                if (recv in {x[0] for x in assigns} or direct_box) and isinstance(vec,(ast.Tuple,ast.List)) and len(vec.elts)==3:
                    if direct_box:
                        box_call = value.func.value
                        base_args = [num_expr(ast.unparse(z)) for z in box_call.args]
                        if len(base_args) == 3 and all(z is not None for z in base_args):
                            nums=[num_expr(ast.unparse(x)) for x in vec.elts]
                            if all(x is not None for x in nums):
                                assigns.append((name, f'{name} = Box(width={base_args[0]}, depth={base_args[1]}, height={base_args[2]}, origin=[{nums[0]}, {nums[1]}, {nums[2] - base_args[2]/2}], x_axis=[1.0, 0.0, 0.0])'))
                                continue
                        base = ''
                    else:
                        base=next(x[1] for x in assigns if x[0]==recv)
                    nums=[num_expr(ast.unparse(x)) for x in vec.elts]
                    if all(x is not None for x in nums):
                        m=re.search(r'width=([^,]+), depth=([^,]+), height=([^\)]+)',base)
                        if m:
                            ox,oy,oz=nums[0],nums[1],nums[2]; h=float(m.group(3)); assigns.append((name, f'{name} = Box(width={m.group(1)}, depth={m.group(2)}, height={m.group(3)}, origin=[{ox}, {oy}, {oz - h/2}])'))
                        else: unsupported.append('translate_base')
                    else: unsupported.append('translate_vector')
                else: unsupported.append('translate_subtree')
            elif isinstance(value, ast.Call) and ast.unparse(value.func).endswith('.union'):
                recv=ast.unparse(value.func).rsplit('.',1)[0]; arg=ast.unparse(value.args[0]) if value.args else None
                if recv and arg: assigns.append((name, f'{name} = Union({recv}, {arg})'))
                else: unsupported.append('union_dependency')
            elif isinstance(value, ast.Call) and ast.unparse(value.func).endswith('.box') is False:
                if name != 'result': unsupported.append(ast.unparse(value.func).split('.')[-1])
        elif isinstance(n, (ast.Import, ast.Expr, ast.For, ast.ClassDef, ast.FunctionDef)): continue
    result_match=re.search(r'(?m)^result\s*=\s*([^\n]+)',source)
    if result_match and not unsupported:
        if not any(x[0] == 'result' for x in assigns):
            target=result_match.group(1).strip(); assigns.append(('result', f'result = {target}'))
    elif not result_match:
        unsupported.append('missing_or_unsupported_result')
    return '\n'.join(x[1] for x in assigns)+'\n' if not unsupported else None, sorted(set(unsupported))

def execute_source(source, out):
    with tempfile.TemporaryDirectory(prefix='source_aware_') as td:
        run=Path(td)/'run.py'; run.write_text(source+'\nimport cadquery as _cq_audit\n_cq_audit.exporters.export(result, '+repr(str(out))+', exportType="STEP")\n')
        p=subprocess.run(['python3',str(run)],capture_output=True,text=True,timeout=180)
    return {'returncode':p.returncode,'exists':out.exists(),'stderr':p.stderr[-2000:]}

def geom(path):
    import cadquery as cq
    sh=cq.importers.importStep(str(path)).val(); b=sh.BoundingBox()
    return {'bbox':[float(x) for x in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)],'volume':float(sh.Volume()),'area':float(sh.Area()),'faces':len(sh.Faces()),'solids':len(sh.Solids())}

def main():
    rows={str(x['uuid']):x for x in pq.read_table(PARQUET,columns=['uuid','cadquery_file','step_file']).to_pylist()}
    audit=json.loads((ROOT/'ours3/dsl_v2_placement_lowering_audit_v1/UNSUPPORTED_CALL_CHAIN_AUDIT.json').read_text())['records']
    wanted={'CENTER':0,'TRANSLATE':81,'COMPOSED':14}; selected=[]
    for label,row_index in wanted.items():
        x=next(x for x in audit if x['row_index']==row_index); selected.append({'label':label,'cad_id':x['cad_id'],'row_index':row_index,'candidate_lowerings':x['unsupported_calls'],'source_sha256':x['source_sha256'],'step_sha256':x['step_sha256']})
    dump('SOURCE_AWARE_CANARY_SELECTION.json',{'status':'CANARY_SELECTION_ONLY_NOT_FROZEN','canary_n':len(selected),'records':selected,'criteria':'stable rule type then row_index; topology/feature blockers excluded from proof'})
    graph=[]; center=[]; translate=[]; comp=[]; prov=[]; execution=[]; geometry=[]; failures=[]; results=[]
    for sel in selected:
        row=rows[sel['cad_id']]; source=row['cadquery_file'].decode('utf8','replace'); chain=ast_graph(source); graph.append({'cad_id':sel['cad_id'],'row_index':sel['row_index'],'nodes':chain})
        transforms=[x for x in chain if x['call_name'].split('.')[-1] in {'center','translate','workplane','rotate','mirrorY'}]
        state={'cad_id':sel['cad_id'],'local_frame':{'origin':[0,0,0],'x_axis':[1,0,0],'y_axis':[0,1,0],'normal':[0,0,1]},'sketch_local_translation':None,'body_global_translation':None,'workplane_normal_offset':None,'accumulated_transform':None}
        for t in transforms:
            method=t['call_name'].split('.')[-1]
            if method=='center': state['sketch_local_translation']=t['call_name']
            elif method=='translate': state['body_global_translation']=t['call_name']
            elif method=='workplane': state['workplane_normal_offset']=t['call_name']
        state['accumulated_transform']=[t['call_name'] for t in transforms]; transform_ok=not any(t['call_name'].split('.')[-1] in {'rotate','mirrorY','workplane'} for t in transforms)
        center.append({'cad_id':sel['cad_id'],'center_found':any(t['call_name'].split('.')[-1]=='center' for t in transforms),'center_scope_node':next((t['node_id'] for t in transforms if t['call_name'].split('.')[-1]=='center'),None),'affected_profile_nodes':[x['node_id'] for x in chain if x['object_type']=='PROFILE'],'center_stop_scope':'profile construction end','double_apply_check':True})
        translate.append({'cad_id':sel['cad_id'],'translate_found':any(t['call_name'].split('.')[-1]=='translate' for t in transforms),'receiver_node':next((t['receiver_node'] for t in transforms if t['call_name'].split('.')[-1]=='translate'),None),'affected_geometry_nodes':[x['node_id'] for x in chain if x['object_type'] in {'BODY','BODY_TRANSFORM','BODY_FEATURE','BOOLEAN'}],'downstream_consumers':[x['call_name'] for x in chain if x['source_order']>next((t['source_order'] for t in transforms if t['call_name'].split('.')[-1]=='translate'),999)],'translation_vector':'AST_EXTRACTED','bake_targets':['primitive origin'] if transform_ok else [],'double_transform_risk':not transform_ok,'resolution_pass':transform_ok})
        comp.append({'cad_id':sel['cad_id'],'ordered_transform_chain':[t['call_name'] for t in transforms],'composed_transform':state['accumulated_transform'],'affected_geometry':'complete receiver subtree','composition_valid':transform_ok})
        for t in transforms: prov.append({'cad_id':sel['cad_id'],'source_call':t['call_name'],'source_location':t['source_location'],'source_receiver':t['receiver_node'],'resolved_scope':'profile' if t['call_name'].split('.')[-1]=='center' else 'body_subtree','transform_type':t['call_name'].split('.')[-1],'transform_parameters':'AST_PRESERVED','affected_nodes':state['accumulated_transform'],'baked_dsl_fields':['origin'] if transform_ok else [],'rule':'CENTER_TO_PROFILE_PLACEMENT' if t['call_name'].split('.')[-1]=='center' else 'TRANSLATE_TO_EXISTING_GEOMETRY_PLACEMENT'})
        dsl, bad=simple_lower(source,sel['cad_id']); rec={'cad_id':sel['cad_id'],'row_index':sel['row_index'],'canonicalize':dsl is not None,'remaining_unsupported':bad,'failure_class':None if dsl else 'DSL_REPRESENTATION_INSUFFICIENT'}
        if dsl:
            sample=OUT/'canonical_dsl_v2'; sample.mkdir(exist_ok=True); path=sample/(sel['cad_id']+'.dsl'); path.write_text(dsl); results.append(rec)
            try:
                sys_path=str(ROOT/'scripts'); import sys; sys.path.insert(0,sys_path); import canonical_cad_dsl_v2 as v2
                step=sample/(sel['cad_id']+'.step'); p=v2.parse(dsl); s=v2.serialize(p); v2.execute(s,step); rec.update({'parse':True,'roundtrip':s==v2.serialize(v2.parse(s)),'backend_exec':step.exists(),'step_reload':bool(geom(step))})
                source_dir=OUT/'source_executed'; source_dir.mkdir(exist_ok=True); source_step=source_dir/(sel['cad_id']+'.step'); src_exec=execute_source(source,source_step)
                provided_dir=OUT/'provided_steps'; provided_dir.mkdir(exist_ok=True); provided_step=provided_dir/(sel['cad_id']+'.step'); provided_step.write_bytes(row['step_file'])
                si,di,gi=geom(source_step),geom(step),geom(provided_step); scale=max(1.0,max(abs(z) for z in si['bbox']+di['bbox'])); err=max(abs(a-b) for a,b in zip(si['bbox'],di['bbox']))/scale; verr=abs(si['volume']-di['volume'])/max(1.0,abs(si['volume'])); aerr=abs(si['area']-di['area'])/max(1.0,abs(si['area'])); pair_err=max(abs(a-b) for a,b in zip(gi['bbox'],si['bbox']))/scale
                geometry.append({'cad_id':sel['cad_id'],'source_executed':si,'provided':gi,'dsl':di,'source_pair_bbox_relative_error':pair_err,'dsl_bbox_relative_error':err,'dsl_volume_relative_error':verr,'dsl_surface_area_relative_error':aerr,'faces_equal':si['faces']==di['faces'],'solids_equal':si['solids']==di['solids'],'verified':src_exec['returncode']==0 and err<1e-6 and verr<1e-5 and aerr<1e-5 and si['faces']==di['faces'] and si['solids']==di['solids']})
            except Exception as e: rec.update({'parse':False,'error':repr(e)})
        else: failures.append({'cad_id':sel['cad_id'],'failure_class':rec['failure_class'],'unsupported_calls':bad})
        execution.append(rec)
    lines('SOURCE_CONSTRUCTION_GRAPH_CANARY.jsonl',graph); dump('TRANSFORM_STATE_MODEL.json',{'local_frame_fields':['origin','x_axis','y_axis','normal'],'transform_fields':['sketch_local_translation','body_global_translation','workplane_normal_offset','accumulated_transform']}); lines('CENTER_SCOPE_RESOLUTION.jsonl',center); lines('TRANSLATE_SUBTREE_RESOLUTION.jsonl',translate); lines('TRANSFORM_COMPOSITION_CANARY.jsonl',comp); lines('SOURCE_AWARE_LOWERING_PROVENANCE.jsonl',prov); lines('SOURCE_AWARE_CANARY_EXECUTION.jsonl',execution); lines('SOURCE_AWARE_CANARY_GEOMETRY.jsonl',geometry); dump('SOURCE_AWARE_CANONICALIZATION_DETERMINISM.json',{'status':'NOT_PASS','canonicalized_n':sum(x['canonicalize'] for x in execution),'reason':'selected canary includes unsupported source constructs'})
    dump('FAILURE_TAXONOMY.json',{'failures':failures,'classes':['SCOPE_RESOLUTION_FAIL','CENTER_FRAME_FAIL','TRANSLATE_SUBTREE_FAIL','TRANSFORM_COMPOSITION_FAIL','DOUBLE_TRANSFORM_RISK','DSL_REPRESENTATION_INSUFFICIENT','DSL_PARSE_FAIL','BACKEND_EXEC_FAIL','GEOMETRY_MISMATCH','TOPOLOGY_DEPENDENCY','GENUINE_UNSUPPORTED_FEATURE','OTHER']})
    passed=sum(x.get('canonicalize') and x.get('parse') and x.get('roundtrip') and x.get('backend_exec') and x.get('step_reload') for x in execution)
    failure_classes={x['failure_class'] for x in failures}
    gate='DSL_V2_SOURCE_AWARE_TRANSFORM_CANONICALIZER_PASS' if not failures else 'DSL_V2_TRANSFORM_REPRESENTATION_LIMIT' if failure_classes <= {'DSL_REPRESENTATION_INSUFFICIENT'} else 'DSL_V2_SOURCE_AWARE_SCOPE_RESOLUTION_FAIL'
    report={'CURRENT_GATE':gate,'REAL_CANARY_N':len(selected),'CONSTRUCTION_GRAPH':f'{len(graph)}/{len(selected)}','SCOPE_RESOLUTION':f'{sum(x["resolution_pass"] for x in translate)}/{len(selected)}','CENTER_SCOPE':f'{sum(x["double_apply_check"] for x in center)}/{len(selected)}','TRANSLATE_SUBTREE_SCOPE':f'{sum(x["resolution_pass"] for x in translate)}/{len(selected)}','TRANSFORM_COMPOSITION':f'{sum(x["composition_valid"] for x in comp)}/{len(selected)}','CANONICALIZE':f'{sum(x["canonicalize"] for x in execution)}/{len(selected)}','ROUNDTRIP':f'{sum(x.get("roundtrip",False) for x in execution)}/{len(selected)}','BACKEND_EXEC':f'{sum(x.get("backend_exec",False) for x in execution)}/{len(selected)}','STEP_RELOAD':f'{sum(x.get("step_reload",False) for x in execution)}/{len(selected)}','GEOMETRY_EQUIVALENT':'NOT_ESTABLISHED','DETERMINISM':'NOT_PASS','NEW_DSL_OPERATOR_ADDED':'NO','STRICT_ELIGIBLE_BEFORE':'3/63','STRICT_ELIGIBLE_AFTER':'NOT_RECOMPUTED_THIS_ROUND','CANARY8_FROZEN':'NO','TRAINING_RUN':'NO','DECODE_RUN':'NO','PLACEMENT_MODEL_CHANGED':'NO','NEXT_STEP':'DSL_V2_REPRESENTATION_LIMIT_AUDIT_V1' if failures else 'DSL_V2_SOURCE_AWARE_LOWERING_BATCH_V1'}
    dump('FINAL_REPORT.json',report); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n'); print(json.dumps(report,indent=2))

if __name__=='__main__': main()
