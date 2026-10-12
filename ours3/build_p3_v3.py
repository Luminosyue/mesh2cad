import csv, hashlib, json, math, runpy, statistics, traceback
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
V1 = ROOT / 'ours3/p3_xpart_20case_compact_ir_v1'
OUT = ROOT / 'ours3/p3_xpart_20case_compact_ir_v3'
for name in ['memory_audit','schema','compact_ir_v3','parser_v3','compiler_v3','step_v3','token_audit','context_audit','demo5','training20','renders','reports','logs']:
    (OUT / name).mkdir(parents=True, exist_ok=True)

from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(str(ROOT/'ours3/airplane3_fullseq_14bit_ir_v1/runs/fast_refinement_v2_step80/checkpoint-40'), use_fast=False)
manifest = json.loads((V1/'CASE_MANIFEST.json').read_text())
cases = manifest['cases']
OPCODES = {'loft':'L','extrude':'E','revolve':'R','loft_with_pockets':'LP','base_and_profile_pads':'BP','extruded_body_and_end_features':'XB','unknown':'U'}
FEATURE_CODES = {'loft':'L','extrude':'E','revolve':'R','pocket':'P','unknown':'U'}

def source_params(path):
    return runpy.run_path(str(path))['PARAMETERS']

def dequant(params, qvalues, lo, hi):
    it = iter(qvalues)
    def walk(x):
        if isinstance(x, dict): return {k:walk(v) for k,v in x.items()}
        if isinstance(x, list): return [walk(v) for v in x]
        if isinstance(x, float) and math.isfinite(x):
            q = next(it); return lo + (q/16383.0)*(hi-lo) if hi > lo else lo
        return x
    out = walk(params)
    try: next(it); raise AssertionError('extra q values')
    except StopIteration: return out

def replace_params(source_text, params):
    pos = source_text.find('PARAMETERS'); q = chr(39)*3
    a = source_text.find(q, pos)+3; b = source_text.find(q, a)
    assert pos >= 0 and a >= 3 and b >= 0
    return source_text[:a] + json.dumps(params, separators=(',',':')) + source_text[b:]

def serialize(cid, params, qs):
    op = OPCODES.get(str(params.get('operation','unknown')), 'U')
    feats=[]
    for f in params.get('features',[]):
        typ=FEATURE_CODES.get(str(f.get('type','unknown')),'U'); extra=[]
        for key in ('sections','loops','pockets'):
            if key in f: extra.append(f'{key[0].upper()}{len(f[key])}')
        feats.append(typ+''.join(extra))
    lines=['V3 14',f'C {cid}',f'O {op}',f'F {len(feats)}']
    if feats: lines.append('T '+' '.join(feats))
    lines.append(f'N {len(qs)}')
    vals=[str(int(q)) for q in qs]
    for i in range(0,len(vals),256): lines.append('Q '+' '.join(vals[i:i+256]))
    return '\n'.join(lines+['E'])+'\n'

def parse(text):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    assert lines[0]=='V3 14' and lines[-1]=='E'
    cid=lines[1].split()[1]; n=next(int(x.split()[1]) for x in lines if x.startswith('N '))
    qs=[]
    for x in lines:
        if x.startswith('Q '): qs.extend(int(v) for v in x.split()[1:])
    assert len(qs)==n
    return cid,qs

def toklen(s): return len(tok(s, add_special_tokens=False).input_ids)

schema={'version':'COMPACT_IR_V3','bits':14,'tokenizer_change':False,'operation_codes':OPCODES,'feature_codes':FEATURE_CODES,'q_encoding':'decimal unsigned 0..16383','q_stream_line_width':256,'lossless_contract':['operation sequence','feature sequence','q integer sequence','point order','section/loop/pocket counts','normalization','geometry']}
(OUT/'schema/V3_SCHEMA.json').write_text(json.dumps(schema,indent=2)+'\n')
rows=[]; gates=[]
v1stats={x['CASE_ID']:x for x in csv.DictReader((V1/'token_audit/PER_CASE_TOKEN_STATS.csv').open())}
for c in cases:
    cid=c['CASE_ID']; qm=json.loads((V1/'quantization'/f'{cid}.json').read_text()); qs=[int(x['q14']) for x in qm['parameters']]; params=source_params(c['CAD_PATH'])
    v3=serialize(cid,params,qs); (OUT/'compact_ir_v3'/f'{cid}.v3').write_text(v3)
    pcid,pqs=parse(v3); (OUT/'parser_v3'/f'{cid}.json').write_text(json.dumps({'case_id':pcid,'qvalues':pqs,'q_count':len(pqs),'lo':qm['lo'],'hi':qm['hi']},indent=2)+'\n')
    g={'CASE_ID':cid,'V3_PARSE':pcid==cid,'Q_EXACT':pqs==qs,'Q_COUNT_EXACT':len(pqs)==len(qs),'V3_CAD_EXEC':False,'V3_BREP_VALID':False,'V3_STEP_EXPORT':False,'V3_STEP_READBACK':False,'GEOMETRY_EQUIVALENCE':False,'ERROR':''}
    try:
        cp=OUT/'compiler_v3'/f'{cid}.py'; cp.write_text(replace_params(Path(c['CAD_PATH']).read_text(),dequant(params,qs,qm['lo'],qm['hi'])))
        ns=runpy.run_path(str(cp)); shape=ns['build'](); g['V3_CAD_EXEC']=True; g['V3_BREP_VALID']=bool(shape.isValid() and len(shape.Solids())>=1)
        import cadquery as cq
        sp=OUT/'step_v3'/f'{cid}.step'; cq.exporters.export(shape,str(sp)); g['V3_STEP_EXPORT']=sp.exists() and sp.stat().st_size>0; rb=cq.importers.importStep(str(sp)); g['V3_STEP_READBACK']=bool(rb and rb.val().isValid())
        old=cq.importers.importStep(str(V1/'compiled_cadquery'/f'{cid}.step')).val(); new=rb.val(); g['GEOMETRY_EQUIVALENCE']=abs(float(old.Volume())-float(new.Volume())) <= max(1e-12,abs(float(old.Volume()))*1e-9)
    except Exception: g['ERROR']=traceback.format_exc()[-2500:]
    gates.append(g)
    v1n=toklen((V1/'compact_ir'/f'{cid}.ir').read_text()); v3n=toklen(v3); cond=toklen('<point_cloud>\nGenerate a CAD construction program from the point cloud.\nOutput only valid Compact IR assignments ending with END.\n')
    raw=int(v1stats[cid]['RAW_TOKEN_N']); rows.append({'CASE_ID':cid,'OBJECT_ID':c['OBJECT_ID'],'V1_TOKEN_N':v1n,'V3_TOKEN_N':v3n,'RAW_TOKEN_N':raw,'V1_TO_V3_REDUCTION_PERCENT':round(100*(1-v3n/v1n),3),'RAW_TO_V3_REDUCTION_PERCENT':round(100*(1-v3n/raw),3),'CONDITIONING_TOKEN_N':cond,'V3_FULL_SEQUENCE_TOKEN_N':v3n+cond+1})

with (OUT/'reports/V3_CAD_GATE.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(gates[0])); w.writeheader(); w.writerows(gates)
with (OUT/'token_audit/PER_CASE_V1_V3_TOKEN_STATS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print('generated',len(rows),'cases')

def bucket(n):
    return 'A<=8192' if n<=8192 else 'B<=16384' if n<=16384 else 'C<=24576' if n<=24576 else 'D<=32768' if n<=32768 else 'OVER'

lengths=sorted(rows,key=lambda x:x['V3_FULL_SEQUENCE_TOKEN_N'],reverse=True)
with (OUT/'memory_audit/PER_CASE_FULLSEQ_LENGTHS.csv').open('w',newline='') as f:
    fields=['CASE_ID','TARGET_TOKEN_N','CONDITIONING_TOKEN_N','FULL_SEQUENCE_TOKEN_N','BUCKET']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    w.writerows({'CASE_ID':x['CASE_ID'],'TARGET_TOKEN_N':x['V3_TOKEN_N'],'CONDITIONING_TOKEN_N':x['CONDITIONING_TOKEN_N'],'FULL_SEQUENCE_TOKEN_N':x['V3_FULL_SEQUENCE_TOKEN_N'],'BUCKET':bucket(x['V3_FULL_SEQUENCE_TOKEN_N'])} for x in lengths)

full=[x['V3_FULL_SEQUENCE_TOKEN_N'] for x in rows]; v1=[x['V1_TOKEN_N'] for x in rows]; v3=[x['V3_TOKEN_N'] for x in rows]
import numpy as np
context={'min_full_sequence':min(full),'median_full_sequence':statistics.median(full),'p90_full_sequence':float(np.percentile(full,90)),'p95_full_sequence':float(np.percentile(full,95)),'max_full_sequence':max(full),'candidates':[8192,16384,24576,32768],'recommended_context':next(x for x in [8192,16384,24576,32768] if x>=max(full)*1.05)}
(OUT/'context_audit/context_summary.json').write_text(json.dumps(context,indent=2)+'\n')

cid='case_013'; v1text=(V1/'compact_ir'/f'{cid}.ir').read_text(); v3text=(OUT/'compact_ir_v3'/f'{cid}.v3').read_text(); qm=json.loads((V1/'quantization'/f'{cid}.json').read_text()); qs=[str(x['q14']) for x in qm['parameters']]
cost=[toklen(x) for x in qs]
comp={'case_id':cid,'v1_total_tokens':toklen(v1text),'v3_total_tokens':toklen(v3text),'v1_components':{'parameter_lines':toklen('\n'.join(x for x in v1text.splitlines() if x.startswith('P '))),'structure_lines':toklen('\n'.join(x for x in v1text.splitlines() if not x.startswith('P ')))},'v3_components':{'q_stream':toklen(' '.join(qs)),'metadata':toklen('\n'.join(x for x in v3text.splitlines() if not x.startswith('Q ')))},'q_integer_token_cost':{'mean':statistics.mean(cost),'median':statistics.median(cost),'p90':float(np.percentile(cost,90)),'max':max(cost)}}
(OUT/'token_audit/V1_TOKEN_COMPOSITION.json').write_text(json.dumps(comp,indent=2)+'\n')

demo_ids=['case_018','case_009','case_014','case_010','case_005']
demo=[]
for cid in demo_ids:
    c=next(x for x in cases if x['CASE_ID']==cid); r=next(x for x in rows if x['CASE_ID']==cid)
    demo.append({'CASE_ID':cid,'OBJECT_ID':c['OBJECT_ID'],'MESH_PATH':c['MESH_PATH'],'TARGET_TOKEN_N':r['V3_TOKEN_N'],'FULL_SEQUENCE_TOKEN_N':r['V3_FULL_SEQUENCE_TOKEN_N'],'VISUAL_COMPLEXITY':'short' if cid in ['case_018','case_009'] else 'medium' if cid in ['case_014','case_010'] else 'longer','SELECTION_REASON':'balanced length/object coverage; excludes 30k blocker'})
(OUT/'demo5/DEMO5_MANIFEST.json').write_text(json.dumps({'experiment':'P3_XPART_20CASE_COMPACT_IR_V3_AND_DEMO_OVERFIT','cases':demo},indent=2)+'\n')
maxdemo=max(x['FULL_SEQUENCE_TOKEN_N'] for x in demo); democontext=next(x for x in [8192,16384,24576,32768] if x>=maxdemo*1.05)
(OUT/'demo5/context.json').write_text(json.dumps({'max_full_sequence':maxdemo,'recommended_context':democontext,'demo_ids':demo_ids},indent=2)+'\n')
oldtrain=json.loads((V1/'dataset/train.json').read_text()); train=[]
for x in demo:
    cid=x['CASE_ID']; src=next(y for y in oldtrain if y['id']==cid)
    train.append({'id':cid,'dataset':'p3_xpart_demo5_v3','point_clouds':src['point_clouds'],'conversations':[{'from':'human','value':'<point_cloud>\nGenerate a CAD construction program from the point cloud.\nOutput only valid Compact IR V3 assignments ending with E.\n'},{'from':'gpt','value':(OUT/'compact_ir_v3'/f'{cid}.v3').read_text()}]})
(OUT/'demo5/train.json').write_text(json.dumps(train,indent=2)+'\n'); (OUT/'demo5/val.json').write_text(json.dumps(train,indent=2)+'\n'); (OUT/'demo5/dataset_info.json').write_text(json.dumps({'p3_xpart_demo5_v3':{'file_name':'train.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}}},indent=2)+'\n')

summary={'experiment':'P3_XPART_20CASE_COMPACT_IR_V3_AND_DEMO_OVERFIT','v1_case_manifest_sha256':hashlib.sha256((V1/'CASE_MANIFEST.json').read_bytes()).hexdigest(),'case_n':20,'v3_parse_pass':sum(x['V3_PARSE'] for x in gates),'v3_q_exact_pass':sum(x['Q_EXACT'] for x in gates),'v3_cad_pass':sum(x['V3_CAD_EXEC'] for x in gates),'v3_step_readback_pass':sum(x['V3_STEP_READBACK'] for x in gates),'geometry_equivalence_pass':sum(x['GEOMETRY_EQUIVALENCE'] for x in gates),'v1_max_target':max(v1),'v3_max_target':max(v3),'v1_max_fullseq':max(int(x['FULL_SEQUENCE_TOKEN_N']) for x in csv.DictReader((V1/'token_audit/PER_CASE_TOKEN_STATS.csv').open())),'v3_max_fullseq':max(full),'v3_context':context,'demo5_ids':demo_ids,'demo5_context':democontext,'v3_memory_gate':'PENDING_PROBE','demo5_overfit':'PENDING','twenty_case_overfit':'PENDING'}
(OUT/'reports/experiment_state.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'reports/COMPACT_IR_V3_TOKEN_COMPRESSION.md').write_text('# Compact IR V3 token compression\n\n'+json.dumps(summary,indent=2)+'\n\n'+'\n'.join(f"{x['CASE_ID']}: V1={x['V1_TOKEN_N']} V3={x['V3_TOKEN_N']} reduction={x['V1_TO_V3_REDUCTION_PERCENT']}% full={x['V3_FULL_SEQUENCE_TOKEN_N']}" for x in rows)+'\n')
print(json.dumps(summary,indent=2))
