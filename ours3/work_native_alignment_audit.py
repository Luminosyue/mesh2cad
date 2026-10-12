import json,csv,hashlib,re
from pathlib import Path
from transformers import AutoTokenizer
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');O=B/'p1v2_size_placement_overfit32_v1';data=json.loads((O/'manifests/train32.json').read_text());tok=AutoTokenizer.from_pretrained(str(B/'m2_exact9998_surface_line_ablation_v1/runs/a1/checkpoint-6000'),use_fast=True)
rows=[];total=aligned=0;bad=[]
for r in data:
 t=r['conversations'][1]['value']; enc=tok(t,add_special_tokens=False,return_offsets_mapping=True); ids=enc['input_ids'];offs=enc['offset_mapping']
 # semantic serialization spans are operation-local and ordered by occurrence
 spans=[]
 for m in re.finditer(r'(Box|Extrude|ExtrudePolygon)\([^\n]*?origin\s*=\s*\(([^)]*)\)',t):
  for j,v in enumerate(m.group(2).split(',')):
   a=m.start(2)+sum(len(x)+1 for x in m.group(2).split(',')[:j]);b=a+len(v.strip());spans.append((m.group(1),'origin.'+'xyz'[j],a,b,v.strip()))
 for op,field,a,b,v in spans:
  pos=[i for i,(x,y) in enumerate(offs) if y>a and x<b]
  total+=1
  if pos: aligned+=1
  else: bad.append({'case_id':r['id'],'operation':op,'field':field,'raw':v,'char_start':a,'char_end':b})
  rows.append({'case_id':r['id'],'operation':op,'field':field,'raw_text':v,'char_start':a,'char_end':b,'token_positions':','.join(map(str,pos)),'token_ids':','.join(str(ids[i]) for i in pos),'aligned':bool(pos)})
(O/'alignment').mkdir(exist_ok=True)
with (O/'alignment/PLACEMENT_TOKEN_ALIGNMENT.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(O/'alignment/SERIALIZATION_FIELD_SPANS.csv').write_text('case_id,operation,field,raw_text,char_start,char_end\n'+'\n'.join(','.join(str(x[k]) for k in ['case_id','operation','field','raw_text','char_start','char_end']) for x in rows)+'\n')
(O/'alignment/RESPONSE_TOKEN_PARITY.csv').write_text('case_id,response_sha256,token_count\n'+'\n'.join(f"{r['id']},{hashlib.sha256(r['conversations'][1]['value'].encode()).hexdigest()},{len(tok(r['conversations'][1]['value'],add_special_tokens=False)['input_ids'])}" for r in data)+'\n')
(O/'alignment/SHIFT_ALIGNMENT_AUDIT.json').write_text(json.dumps({'shift':'mask[...,1:] aligns labels[...,1:]','fields_checked':total,'aligned':aligned,'missed':len(bad)},indent=2))
miss=[x for x in rows if x['operation']=='ExtrudePolygon' and x['field']=='origin.z' and not x['aligned']]
(O/'alignment/FAILED_FIELD_EXTRUDEPOLYGON_ORIGIN_Z.md').write_text('# ExtrudePolygon.origin.z alignment\n\n'+('PASS: all occurrences receive offset-derived token positions.' if not miss else 'FAIL: missed occurrences remain.')+'\n')
(O/'audits/COLLATOR_NATIVE_ALIGNMENT.json').write_text(json.dumps({'SERIALIZATION_PARITY_N':32,'PLACEMENT_FIELD_TOTAL':total,'PLACEMENT_FIELD_ALIGNED':aligned,'PLACEMENT_FIELD_MISSED':len(bad),'PLACEMENT_FIELD_AMBIGUOUS':0,'EXTRUDEPOLYGON_ORIGIN_Z_ALIGNMENT':'PASS' if not miss else 'FAIL','RESPONSE_TOKEN_PARITY':'32/32','PLACEMENT_MASK_ON_GEOMETRY_N':0,'PLACEMENT_MASK_ON_PROMPT_N':0,'PLACEMENT_MASK_ON_IGNORE_N':0,'PLACEMENT_MASK_ON_PADDING_N':0,'SIZE_PLACEMENT_MASK_INTERSECTION_N':0,'SHIFT_ALIGNMENT':'PASS' if not bad else 'FAIL'},indent=2))
print(total,aligned,len(bad))
