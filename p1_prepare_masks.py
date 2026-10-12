#!/usr/bin/env python3
import ast,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
from transformers import AutoTokenizer
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_operation_aware_structure_loss_v1';DATA=ROOT/'ours3/exact9998_v1';MODEL=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
for d in ('source','configs','masks','audits','logs','runs','tables','reports'):(EXP/d).mkdir(parents=True,exist_ok=True)
tok=AutoTokenizer.from_pretrained(MODEL,use_fast=True)
OPS={'Box','Cylinder','Circle','Sketch','Extrude','ExtrudePolygon','Union','Cut','Revolve','PolygonProfile','Axis','TrueRevolve','Fillet','Chamfer'}
patterns={}
for op in OPS:
 patterns[op]=[]
 for prefix in ('',' '):
  full=tok.encode(prefix+op+'(',add_special_tokens=False);lp=tok.encode(prefix+op,add_special_tokens=False)
  if full[:len(lp)]==lp:patterns[op].append((full, list(range(len(lp)))))
def find(seq,pat):
 n=len(pat);return [i for i in range(len(seq)-n+1) if seq[i:i+n]==pat]
def process(split):
 data=json.loads((DATA/f'exact9998_{split}.json').read_text());out=[];freq=Counter();cases=Counter();alln=0;opn=0;miss=0;false=0
 for row in data:
  text=next(x['value'] for x in row['conversations'] if x['from']=='gpt');tree=ast.parse(text);truth=Counter(n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in OPS);enc=tok(text,add_special_tokens=False,return_offsets_mapping=True);ids=enc['input_ids'];offsets=enc['offset_mapping'];hits=[]
  for op in sorted(OPS,key=len,reverse=True):
   spans=[m.span(1) for m in re.finditer(r'(?<![A-Za-z0-9_])('+re.escape(op)+r')\s*\(',text)]
   if len(spans)!=truth[op]:miss+=max(0,truth[op]-len(spans));false+=max(0,len(spans)-truth[op])
   for cs,ce in spans:
    positions=[j for j,(a,b) in enumerate(offsets) if b>cs and a<ce]
    if not positions:miss+=1;continue
    hits.append({'operation':op,'char_span':[cs,ce],'token_indices':positions,'token_ids':[ids[x] for x in positions]})
   freq[op]+=truth[op];cases[op]+=int(truth[op]>0)
  opn+=sum(len(x['token_indices']) for x in hits);alln+=len(ids)
  out.append({'cad_id':row['id'],'response_sha256':hashlib.sha256(text.encode()).hexdigest(),'response_token_ids':ids,'operations':[x['operation'] for x in sorted(hits,key=lambda z:z['token_indices'][0])],'operation_spans':sorted(hits,key=lambda z:z['token_indices'][0])})
 path=EXP/'masks'/f'{split.upper()}_OPERATION_TOKEN_MASK_REGISTRY.jsonl';path.write_text('\n'.join(json.dumps(x,separators=(',',':')) for x in out)+'\n');sha=hashlib.sha256(path.read_bytes()).hexdigest()
 return {'split':split.upper(),'N':len(data),'registry':str(path),'sha256':sha,'AST_OPERATION_N':sum(freq.values()),'DETECTED_OPERATION_N':sum(len(x['operation_spans']) for x in out),'MISSED_OPERATION_SPAN_N':miss,'FALSE_POSITIVE_OPERATION_TOKEN_N':false,'OP_TOKEN_N':opn,'ALL_SUPERVISED_TARGET_TOKEN_N':alln,'OP_TOKEN_FRACTION':opn/alln,'frequency':{o:{'case_count':cases[o],'occurrence_count':freq[o],'operation_token_count':sum(len(s['token_indices']) for x in out for s in x['operation_spans'] if s['operation']==o)} for o in sorted(freq)}}
audits=[process('train'),process('val')];audit={'status':'PASS' if all(x['MISSED_OPERATION_SPAN_N']==0 and x['FALSE_POSITIVE_OPERATION_TOKEN_N']==0 and x['AST_OPERATION_N']==x['DETECTED_OPERATION_N'] for x in audits) else 'FAIL','splits':audits,'causal_shift':'operation mask is attached to label positions, then shifted identically with shift_labels=labels[...,1:] and shift_mask=mask[...,1:]','geometry_splice':'registry indices are response-relative; runtime locates the exact response token subsequence after all geometry insertion and intersects labels != -100','TEST_TOUCHED':'NO'}
(EXP/'audits/OPERATION_MASK_ALIGNMENT_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');(EXP/'masks/OPERATION_MASK_DISTRIBUTION.json').write_text(json.dumps({'splits':audits},indent=2)+'\n');(EXP/'masks/OPERATION_VOCAB_AUDIT.json').write_text(json.dumps({'operations':sorted(OPS),'token_patterns':{o:[{'ids':p,'operation_relative_indices':r} for p,r in patterns[o]] for o in sorted(OPS)},'source':'actual TRAIN7998 and VAL1000 AST calls plus frozen canonical DSL vocabulary','TEST_TOUCHED':'NO'},indent=2)+'\n')
print(json.dumps(audit,indent=2));raise SystemExit(0 if audit['status']=='PASS' else 2)
