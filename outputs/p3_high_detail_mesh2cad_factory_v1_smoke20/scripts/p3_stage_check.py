import json,argparse,datetime
from pathlib import Path
O=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,choices=[3,5,20],required=True);a=ap.parse_args()
rows=json.loads((O/'manifests/objects_frozen.json').read_text())[:a.limit];parts=[];objects=[];errors=[]
for obj in rows:
 d=O/'objects'/obj['object_id'];seg=json.loads((d/'p3/segmentation.json').read_text());pm=json.loads((d/'p3/parts_manifest.json').read_text());asm=json.loads((d/'assembly/assembly_metrics.json').read_text());objects.append(asm)
 if not seg['success']:errors.append(obj['object_id']+':P3 failure')
 for p in pm['parts']:
  rp=d/'parts'/p['part_id']/'result.json'
  if p['size_class']=='MICRO_PART' or p['part_quality']=='DEGENERATE':continue
  if not rp.exists():errors.append(obj['object_id']+'/'+p['part_id']+':incomplete')
  else:parts.append(json.loads(rp.read_text()))
fixture=json.loads((O/'integrity/assembly_fixture/result.json').read_text())
out={'stage_object_n':a.limit,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_part_attempts_complete':not errors,'part_n':len(parts),'strict_n':sum(p['status']=='STRICT_ACCEPT' for p in parts),'near_n':sum(p['status']=='NEAR_PASS' for p in parts),'reject_n':sum(p['status']=='REJECT' for p in parts),'source_data_nonempty_assembly_n':sum(x['status']!='ASSEMBLY_FAIL' for x in objects),'full_assembly_n':sum(x['status']=='FULL_STRICT_ASSEMBLY' for x in objects),'synthetic_assembly_fixture_pass':fixture['pass'],'errors':errors,'interpretation':'Completion of bounded diagnostic stages is not proof of source-data end-to-end success. No source assembly is claimed without strict parts. Subsequent objects extend the requested Smoke20 quality assessment only; no Scale100.'}
(O/'reports'/f'stage_{a.limit}_checkpoint.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert not errors
