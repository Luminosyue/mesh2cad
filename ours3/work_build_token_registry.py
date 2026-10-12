import json,re,hashlib
from pathlib import Path
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');O=B/'p1v2_size_placement_overfit32_v1';data=json.loads((O/'manifests/train32.json').read_text())
from transformers import AutoTokenizer
tok=AutoTokenizer.from_pretrained(str(B/'m2_exact9998_surface_line_ablation_v1/runs/a1/checkpoint-6000'),use_fast=False)
lines=[]
for r in data:
 t=r['conversations'][1]['value']; spans=[]
 for m in re.finditer(r'(Box|Extrude|ExtrudePolygon)\([^\n]*?\b(width|height|depth)\s*=\s*([-+]?\d*\.?\d+)',t):
  spans.append({'kind':'size','operation':m.group(1),'field':m.group(2),'raw_value':m.group(3),'token_ids':tok.encode(m.group(3),add_special_tokens=False)})
 for m in re.finditer(r'(Box|Extrude|ExtrudePolygon)\([^\n]*?origin\s*=\s*\(([^)]*)\)',t):
  for j,v in enumerate(m.group(2).split(',')):
   v=v.strip();spans.append({'kind':'placement','operation':m.group(1),'field':'origin.'+'xyz'[j],'raw_value':v,'token_ids':tok.encode(v,add_special_tokens=False)})
 # Regex traversal already preserves operation and field order; retaining it avoids
 # cursor ambiguity when repeated numeric values (for example 0.0) occur.
 lines.append({'cad_id':r['id'],'response_sha256':hashlib.sha256(t.encode()).hexdigest(),'size_spans':[x for x in spans if x['kind']=='size'],'placement_spans':[x for x in spans if x['kind']=='placement']})
(O/'registry/PARAMETER_FIELD_TOKEN_REGISTRY.jsonl').write_text('\n'.join(json.dumps(x) for x in lines)+'\n')
print('cases',len(lines),'size',sum(len(x['size_spans']) for x in lines),'place',sum(len(x['placement_spans']) for x in lines))
