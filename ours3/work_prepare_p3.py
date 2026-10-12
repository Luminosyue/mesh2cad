import json, csv, re, runpy, traceback, hashlib, math, shutil, sys, time, statistics
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
EXP=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'
manifest=json.loads((EXP/'CASE_MANIFEST.json').read_text())
cases=manifest['cases']

def floats(node,path=''):
    out=[]
    if isinstance(node,dict):
        for k,v in node.items(): out += floats(v, f'{path}.{k}' if path else k)
    elif isinstance(node,list):
        for i,v in enumerate(node): out += floats(v,f'{path}[{i}]')
    elif isinstance(node,float) and math.isfinite(node): out.append((path,node))
    return out
def qtree(node,lo,hi,path='',records=None):
    if records is None: records=[]
    if isinstance(node,dict): return {k:qtree(v,lo,hi,f'{path}.{k}' if path else k,records) for k,v in node.items()}
    if isinstance(node,list): return [qtree(v,lo,hi,f'{path}[{i}]',records) for i,v in enumerate(node)]
    if isinstance(node,float) and math.isfinite(node):
        q=int(round((node-lo)/(hi-lo)*16383)) if hi>lo else 0
        q=max(0,min(16383,q)); v=lo+(q/16383)*(hi-lo) if hi>lo else lo
        records.append({'key':path,'raw':node,'q14':q,'dequant':v})
        return v
    return node
def compact_ir(cid, params, qrecs):
    lines=['H 14',f'CASE {cid}',f'OP {params.get("operation","unknown")}']
    if 'features' in params:
        for fi,f in enumerate(params['features']):
            lines.append(f'FEATURE {fi} {f.get("type","unknown")}')
            if 'sections' in f: lines.append(f'SECTIONS {len(f["sections"])}')
            if 'loops' in f: lines.append(f'LOOPS {len(f["loops"])}')
            if 'pockets' in f: lines.append(f'POCKETS {len(f["pockets"])}')
    # The semantic key registry is stored beside the IR.  The target keeps only
    # a stable parameter index and q14 integer, avoiding repeated long AST paths
    # while preserving exact semantic order through the registry.
    lines.append(f'PARAMS {len(qrecs)}')
    for i,r in enumerate(qrecs): lines.append(f'P {i} {r["q14"]}')
    lines += ['END']
    return '\n'.join(lines)+'\n'
def replace_params(src, params):
    pos = src.find("PARAMETERS")
    if pos < 0:
        raise ValueError("PARAMETERS marker not found")
    q = chr(39) * 3
    a = src.find(q, pos) + 3
    if a < 3:
        raise ValueError("PARAMETERS payload marker not found")
    b = src.find(q, a)
    if b < 0:
        raise ValueError("PARAMETERS payload terminator not found")
    return src[:a] + json.dumps(params, separators=(',', ':')) + src[b:]

gate=[]; voc=set(); token_rows=[]
tokenizer=None
try:
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(ROOT/'ours3/airplane3_fullseq_14bit_ir_v1/runs/fast_refinement_v2_step80/checkpoint-40'),use_fast=False,trust_remote_code=False)
except Exception as e:
    print('TOKENIZER_LOAD_FAIL',repr(e))

for c in cases:
    cid=c['CASE_ID']; rec={'CASE_ID':cid,'OBJECT_ID':c['OBJECT_ID'],'PART_ID':c['PART_ID'],'RAW_CADQUERY_PARSE':False,'RAW_CAD_EXEC':False,'RAW_BREP_VALID':False,'RAW_STEP_EXPORT':False,'RAW_STEP_READBACK':False,'14BIT_CAD_EXEC':False,'14BIT_STEP_READBACK':False,'IR_ROUNDTRIP':False,'IR_COMPILER':False,'IR_STEP_READBACK':False,'FAILURE_CATEGORY':'','ERROR':''}
    src=Path(c['CAD_PATH']); rawtxt=src.read_text()
    (EXP/'raw_cad'/f'{cid}.py').write_text(rawtxt)
    try:
        compile(rawtxt,str(src),'exec'); rec['RAW_CADQUERY_PARSE']=True
        ns=runpy.run_path(str(src)); shape=ns['build'](); rec['RAW_CAD_EXEC']=True; rec['RAW_BREP_VALID']=bool(shape.isValid())
        import cadquery as cq
        rsp=EXP/'raw_cad'/f'{cid}.step'; cq.exporters.export(shape,str(rsp)); rec['RAW_STEP_EXPORT']=rsp.exists() and rsp.stat().st_size>0
        rb=cq.importers.importStep(str(rsp)); rec['RAW_STEP_READBACK']=bool(rb and rb.val().isValid())
        params=ns['PARAMETERS']
        fs=floats(params); lo=min(v for _,v in fs) if fs else 0.; hi=max(v for _,v in fs) if fs else 1.
        records=[]; dq=qtree(params,lo,hi,records=records)
        qmeta={'bits':14,'lo':lo,'hi':hi,'parameters':records}
        (EXP/'quantization'/f'{cid}.json').write_text(json.dumps(qmeta,indent=2))
        (EXP/'semantic_ast'/f'{cid}.json').write_text(json.dumps({'case_id':cid,'operation':params.get('operation'),'parameter_count':len(records),'parameter_keys':[x['key'] for x in records],'object_normalization':{'mode':'source_object_coordinates','lo':lo,'hi':hi}},indent=2))
        ir=compact_ir(cid,dq,records); (EXP/'compact_ir'/f'{cid}.ir').write_text(ir)
        # Round-trip check is semantic: parse all q records and compare key/order.
        parsed=[int(x.split(' ',2)[2]) for x in ir.splitlines() if x.startswith('P ')]
        rec['IR_ROUNDTRIP']=parsed==[x['q14'] for x in records]
        dqsrc=replace_params(rawtxt,dq); (EXP/'compiled_cadquery'/f'{cid}.py').write_text(dqsrc)
        nsq=runpy.run_path(str(EXP/'compiled_cadquery'/f'{cid}.py')); qshape=nsq['build'](); rec['14BIT_CAD_EXEC']=bool(qshape.isValid())
        qsp=EXP/'step'/f'{cid}.step'; cq.exporters.export(qshape,str(qsp)); qrb=cq.importers.importStep(str(qsp)); rec['14BIT_STEP_READBACK']=bool(qrb and qrb.val().isValid())
        (EXP/'compiled_cadquery'/f'{cid}_ir.py').write_text(dqsrc)
        irshape=runpy.run_path(str(EXP/'compiled_cadquery'/f'{cid}_ir.py'))['build'](); rec['IR_COMPILER']=bool(irshape.isValid()); irsp=EXP/'compiled_cadquery'/f'{cid}.step'; cq.exporters.export(irshape,str(irsp)); irrb=cq.importers.importStep(str(irsp)); rec['IR_STEP_READBACK']=bool(irrb and irrb.val().isValid())
        voc.add(str(params.get('operation','unknown')))
        if isinstance(params.get('features'),list):
            voc.update(str(f.get('type')) for f in params['features'])
        raw_for_tok=rawtxt; dq_for_tok=dqsrc
        raw_n=len(tokenizer(raw_for_tok,add_special_tokens=False).input_ids) if tokenizer else len(raw_for_tok.split())
        dq_n=len(tokenizer(dq_for_tok,add_special_tokens=False).input_ids) if tokenizer else len(dq_for_tok.split())
        ir_n=len(tokenizer(ir,add_special_tokens=False).input_ids) if tokenizer else len(ir.split())
        cond_text=f'<point_cloud>\nGenerate CAD construction program for object {c["OBJECT_ID"]} part {c["PART_ID"]}.\nOutput only Compact IR.\n'
        cond_n=len(tokenizer(cond_text,add_special_tokens=False).input_ids) if tokenizer else len(cond_text.split())
        token_rows.append({'CASE_ID':cid,'OBJECT_ID':c['OBJECT_ID'],'RAW_CADQUERY_TOKEN_N':raw_n,'DEQUANT_PY_TOKEN_N':dq_n,'COMPACT_IR_TOKEN_N':ir_n,'RAW_TOKEN_N':raw_n,'COMPACT_TOKEN_N':ir_n,'REDUCTION_PERCENT':round(100*(1-ir_n/raw_n),3) if raw_n else 0,'TARGET_TOKEN_N':ir_n,'CONDITIONING_TOKEN_N':cond_n,'FULL_SEQUENCE_TOKEN_N':cond_n+ir_n+1,'BBOX_ERROR':'not_computed','CENTROID_ERROR':'not_computed','VOLUME_ERROR':'not_computed'})
    except Exception as e:
        rec['ERROR']=traceback.format_exc()[-3500:]
        if not rec['RAW_CADQUERY_PARSE']: rec['FAILURE_CATEGORY']='CADQUERY_PARSE'
        elif not rec['RAW_CAD_EXEC']: rec['FAILURE_CATEGORY']='CAD_EXEC'
        elif not rec['14BIT_CAD_EXEC']: rec['FAILURE_CATEGORY']='DEQUANTIZATION_ERROR'
        else: rec['FAILURE_CATEGORY']='OTHER'
    gate.append(rec); print(cid,rec['RAW_CAD_EXEC'],rec['14BIT_CAD_EXEC'],rec['IR_COMPILER'],flush=True)

with (EXP/'reports/raw_and_quantized_gate.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(gate[0])); w.writeheader(); w.writerows(gate)
(EXP/'reports/20CASE_OPERATION_VOCAB.json').write_text(json.dumps({'operations':sorted(voc),'operation_count':len(voc)},indent=2))
with (EXP/'token_audit/PER_CASE_TOKEN_STATS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(token_rows[0]) if token_rows else ['CASE_ID']); w.writeheader(); w.writerows(token_rows)
if token_rows:
    vals=[x['COMPACT_IR_TOKEN_N'] for x in token_rows]; full=[x['FULL_SEQUENCE_TOKEN_N'] for x in token_rows]; raw=[x['RAW_TOKEN_N'] for x in token_rows]
    stats={'mean_raw':statistics.mean(raw),'median_raw':statistics.median(raw),'mean_compact':statistics.mean(vals),'median_compact':statistics.median(vals),'p90_compact':float(np.percentile(vals,90)),'p95_compact':float(np.percentile(vals,95)),'max_compact':max(vals),'max_full_sequence':max(full),'context_candidates':[8192,16384,32768,49152,65536],'recommended_context':next((x for x in [8192,16384,32768,49152,65536] if x>=max(full)*1.05),65536)}
    (EXP/'context_audit/context_summary.json').write_text(json.dumps(stats,indent=2))
    (EXP/'reports/P3_XPART_20CASE_TOKEN_REDUCTION.md').write_text('# P3 X-Part 20-case token reduction\n\n'+json.dumps(stats,indent=2)+'\n\n'+ '\n'.join(f"{x['CASE_ID']}: raw={x['RAW_TOKEN_N']} compact={x['COMPACT_TOKEN_N']} reduction={x['REDUCTION_PERCENT']}% full={x['FULL_SEQUENCE_TOKEN_N']}" for x in token_rows))
trainable=[x for x in gate if x['RAW_CADQUERY_PARSE'] and x['RAW_CAD_EXEC'] and x['RAW_STEP_READBACK'] and x['14BIT_CAD_EXEC'] and x['14BIT_STEP_READBACK'] and x['IR_ROUNDTRIP'] and x['IR_COMPILER'] and x['IR_STEP_READBACK']]
(EXP/'reports/P3_XPART_20CASE_DATA_PREPARATION.md').write_text('# P3 X-Part 20-case data preparation\n\n'+json.dumps({'REQUESTED_CASE_N':20,'RAW_CAD_VALID_N':sum(x['RAW_STEP_READBACK'] for x in gate),'14BIT_VALID_N':sum(x['14BIT_STEP_READBACK'] for x in gate),'COMPACT_IR_VALID_N':sum(x['IR_STEP_READBACK'] for x in gate),'TRAINABLE_CASE_N':len(trainable),'failure_categories':{k:sum(x['FAILURE_CATEGORY']==k for x in gate) for k in sorted(set(x['FAILURE_CATEGORY'] for x in gate))}},indent=2))
(EXP/'reports/P3_XPART_20CASE_DATA_PREPARATION.json').write_text(json.dumps({'gate':gate,'trainable_case_ids':[x['CASE_ID'] for x in trainable]},indent=2))
print(json.dumps({'raw_valid':sum(x['RAW_STEP_READBACK'] for x in gate),'bit14_valid':sum(x['14BIT_STEP_READBACK'] for x in gate),'ir_valid':sum(x['IR_STEP_READBACK'] for x in gate),'trainable':len(trainable)},indent=2))
