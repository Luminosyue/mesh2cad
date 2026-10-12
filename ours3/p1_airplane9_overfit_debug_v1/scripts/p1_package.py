from pathlib import Path
import zipfile,json,hashlib
d=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_overfit_debug_v1')
summary=json.loads((d/'diagnosis_summary.json').read_text())
(d/'status.json').write_text(json.dumps({'state':'COMPLETE','primary_conclusion':summary['PRIMARY_ROOT_CAUSE'],'single_part_exact_overfit':summary['SINGLE_PART_EXACT_OVERFIT'],'single_checkpoint':500,'next_gate':'A2_3_PARTS_NOT_STARTED'},indent=2))
deliver=d/'deliverables';deliver.mkdir(exist_ok=True)
out=deliver/'p1_airplane9_debug_evidence.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(d.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(d)
  if any(x in rel.parts for x in ['cache','deliverables','__pycache__']):continue
  if p.suffix in ['.pt','.pyc']:continue
  z.write(p,str(rel))
sha=hashlib.sha256(out.read_bytes()).hexdigest();(deliver/'sha256.txt').write_text(sha+'  '+out.name+'\n');print(out,out.stat().st_size,sha)
