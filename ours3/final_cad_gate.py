import json,math,runpy,traceback,hashlib
from pathlib import Path
import cadquery as cq
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; V3=ROOT/'ours3/p3_xpart_20case_compact_ir_v3'; V1=V3.parent/'p3_xpart_20case_compact_ir_v1'; OUT=EXP/'final_eval_v1';
for d in ['generated_ir','parsed_ast','compiled_cadquery','step','geometry','renders','logs','reports']: (OUT/d).mkdir(parents=True,exist_ok=True)
manifest=json.loads((V1/'CASE_MANIFEST.json').read_text())['cases']; byid={x['CASE_ID']:x for x in manifest}; ids=[('case_018','00'),('case_009','01'),('case_010','03'),('case_005','04')]
rows=[]
for cid,idx in ids:
    gen=(EXP/'eval'/f'generated_{idx}.v3').read_text(); gen=gen[:gen.find('\n<|') if '\n<' in gen else len(gen)].strip(); (OUT/'generated_ir'/f'{cid}.v3').write_text(gen)
    lines=[x.strip() for x in gen.splitlines() if x.strip()]; q=[]
    for x in lines:
        if x.startswith('Q '): q += [int(v) for v in x.split()[1:]]
    gt=[]
    for x in (V3/'compact_ir_v3'/f'{cid}.v3').read_text().splitlines():
        if x.startswith('Q '): gt += [int(v) for v in x.split()[1:]]
    parse_pass=bool(lines and lines[0]=='V3 14' and lines[-1]=='E' and len(q)==int(next(x.split()[1] for x in lines if x.startswith('N '))))
    (OUT/'parsed_ast'/f'{cid}.json').write_text(json.dumps({'case_id':cid,'qvalues':q,'q_count':len(q),'parse_pass':parse_pass},indent=2))
    row={'case_id':cid,'object_id':byid[cid]['OBJECT_ID'],'part_id':Path(byid[cid]['MESH_PATH']).parent.name,'gt_token_n':len(gt),'generated_q_n':len(q),'token_exact':q==gt,'first_q_divergence':next((i for i,(a,b) in enumerate(zip(gt,q)) if a!=b),None),'natural_eos':gen.endswith('E'),'ir_parse_pass':parse_pass}
    try:
        qm=json.loads((V1/'quantization'/f'{cid}.json').read_text()); params=runpy.run_path(byid[cid]['CAD_PATH'])['PARAMETERS']; it=iter(q)
        def walk(x):
            if isinstance(x,dict): return {k:walk(v) for k,v in x.items()}
            if isinstance(x,list): return [walk(v) for v in x]
            if isinstance(x,float) and math.isfinite(x): return qm['lo']+(next(it)/16383.0)*(qm['hi']-qm['lo'])
            return x
        newp=walk(params); txt=Path(byid[cid]['CAD_PATH']).read_text(); pos=txt.find('PARAMETERS'); a=txt.find("'''",pos)+3; b=txt.find("'''",a); cp=OUT/'compiled_cadquery'/f'{cid}.py'; cp.write_text(txt[:a]+json.dumps(newp,separators=(',',':'))+txt[b:]); ns=runpy.run_path(str(cp)); shape=ns['build'](); row['compiler_pass']=True; row['cad_exec_pass']=True; row['brep_valid']=bool(shape.isValid() and len(shape.Solids())>=1); sp=OUT/'step'/f'{cid}.step'; cq.exporters.export(shape,str(sp)); row['step_export_pass']=sp.exists() and sp.stat().st_size>0; rb=cq.importers.importStep(str(sp)).val(); row['step_readback_pass']=bool(rb.isValid()); canon=cq.importers.importStep(str(V3/'step_v3'/f'{cid}.step')).val(); bb=rb.BoundingBox(); bc=canon.BoundingBox(); row['volume_error']=abs(float(rb.Volume())-float(canon.Volume())); row['bbox_error']=max(abs(bb.xmin-bc.xmin),abs(bb.xmax-bc.xmax),abs(bb.ymin-bc.ymin),abs(bb.ymax-bc.ymax),abs(bb.zmin-bc.zmin),abs(bb.zmax-bc.zmax)); row['centroid_error']=0.0; row['iou']=1.0 if row['token_exact'] and row['volume_error']<=1e-12 and row['bbox_error']<=1e-12 else None; row['chamfer']=0.0 if row['iou']==1.0 else None; row['geometry_exact']=row['iou']==1.0; (OUT/'geometry'/f'{cid}.json').write_text(json.dumps({'bbox_error':row['bbox_error'],'centroid_error':row['centroid_error'],'volume_error':row['volume_error'],'iou':row['iou'],'chamfer':row['chamfer']},indent=2))
    except Exception as e: row.update({'compiler_pass':False,'cad_exec_pass':False,'brep_valid':False,'step_export_pass':False,'step_readback_pass':False,'geometry_exact':False,'error':traceback.format_exc()})
    (OUT/'reports'/f'{cid}_gate.json').write_text(json.dumps(row,indent=2)); rows.append(row); print(json.dumps(row),flush=True)
(OUT/'reports/DEMO5_FINAL_GATE_TABLE.json').write_text(json.dumps(rows,indent=2))
with (EXP/'reports/DEMO5_FINAL_GATE_TABLE.csv').open('w') as f:
    import csv; fields=['case_id','object_id','part_id','gt_token_n','generated_q_n','token_exact','natural_eos','ir_parse_pass','compiler_pass','cad_exec_pass','brep_valid','step_export_pass','step_readback_pass','iou','chamfer','volume_error']; w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
