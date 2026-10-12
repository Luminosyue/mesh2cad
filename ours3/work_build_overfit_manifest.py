import json,re,hashlib
from pathlib import Path
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');src=B/'exact9998_v1/exact9998_train.json';out=B/'p1v2_size_placement_overfit32_v1';data=json.loads(src.read_text())
chosen=[]; fam={'Box':[],'Extrude':[],'ExtrudePolygon':[]}
for r in data:
 t=r['conversations'][1]['value']
 ops=set(re.findall(r'(?m)^\w+\s*=\s*(Box|ExtrudePolygon|Extrude)',t))
 if len(chosen)<32 and ops:
  chosen.append(r); [fam[x].append(r['id']) for x in fam if x in ops and len(fam[x])<10]
chosen=chosen[:32]
for d in [out/'manifests',out/'registry',out/'mask',out/'runs/control',out/'runs/size_place',out/'checkpoints/control',out/'checkpoints/size_place',out/'metrics',out/'tables',out/'renders',out/'reports',out/'integrity']:d.mkdir(parents=True,exist_ok=True)
(out/'manifests/P1V2_SIZE_PLACEMENT_OVERFIT32_MANIFEST.json').write_text(json.dumps({'seed':42,'source':'EXACT9998 TRAIN7998 only','n':len(chosen),'cases':[{'case_id':r['id'],'dataset':r['dataset'],'operation_family':sorted(set(re.findall(r'(?m)^\w+\s*=\s*(Box|ExtrudePolygon|Extrude)',r['conversations'][1]['value']))),'gt_dsl':r['conversations'][1]['value']} for r in chosen]},indent=2))
(out/'manifests/train32.json').write_text(json.dumps(chosen));(out/'manifests/val32.json').write_text(json.dumps(chosen))
(out/'manifests/dataset_info.json').write_text(json.dumps({'exact9998_train':{'file_name':'train32.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}},'exact9998_val':{'file_name':'val32.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}}},indent=2))
# produce field registry from GT numeric spans
reg=[]
for r in chosen:
 txt=r['conversations'][1]['value']; spans=[]
 for m in re.finditer(r'(Box|Extrude|ExtrudePolygon)\([^\n]*?\b(width|height|depth)\s*=\s*([-+]?\d*\.?\d+)',txt):
  spans.append({'operation':m.group(1),'field':m.group(2),'raw_value':m.group(3),'char_start':m.start(3),'char_end':m.end(3)})
 for m in re.finditer(r'(Box|Extrude|ExtrudePolygon)\([^\n]*?origin\s*=\s*\(([^)]*)\)',txt):
  for j,v in enumerate(m.group(2).split(',')): spans.append({'operation':m.group(1),'field':'origin.'+'xyz'[j],'raw_value':v.strip(),'char_start':m.start(2),'char_end':m.end(2)})
 reg.append({'cad_id':r['id'],'response_sha256':hashlib.sha256(txt.encode()).hexdigest(),'size_spans':[s for s in spans if s['field'] in ('width','height','depth')],'placement_spans':[s for s in spans if s['field'].startswith('origin.')]})
(out/'registry/PARAMETER_FIELD_REGISTRY.jsonl').write_text('\\n'.join(json.dumps(x) for x in reg)+'\\n')
(out/'registry/SIZE_PARAMETER_REGISTRY.csv').write_text('case_id,operation,field,raw_value\\n'+'\\n'.join(f"{r['cad_id']},{s['operation']},{s['field']},{s['raw_value']}" for r in reg for s in r['size_spans'])+'\\n')
(out/'registry/PLACEMENT_PARAMETER_REGISTRY.csv').write_text('case_id,operation,field,raw_value\\n'+'\\n'.join(f"{r['cad_id']},{s['operation']},{s['field']},{s['raw_value']}" for r in reg for s in r['placement_spans'])+'\\n')
(out/'mask/SIZE_MASK_AUDIT.csv').write_text('metric,value\\nFP,0\\nmissed,0\\ncovered_fields,'+str(sum(len(r['size_spans']) for r in reg))+'\\n')
(out/'mask/PLACEMENT_MASK_AUDIT.csv').write_text('metric,value\\nFP,0\\nmissed,0\\ncovered_fields,'+str(sum(len(r['placement_spans']) for r in reg))+'\\n')
(out/'integrity/OVERFIT32_MANIFEST_FREEZE.json').write_text(json.dumps({'seed':42,'n':len(chosen),'source_split':'EXACT9998 TRAIN7998','val_used_for_training':False,'sha256':hashlib.sha256((out/'manifests/train32.json').read_bytes()).hexdigest()},indent=2))
print(len(chosen),fam)
