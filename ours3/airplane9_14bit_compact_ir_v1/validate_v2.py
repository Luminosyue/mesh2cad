import csv,runpy,time,traceback
from pathlib import Path
import cadquery as cq
A=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/airplane9_14bit_compact_ir_v1'); out=A/'compiled_cadquery_v2'; step=A/'step_v2'; step.mkdir(exist_ok=True); rows=[]
for p in sorted(out.glob('*.py')):
 pid=p.stem.split('__')[1]; t=time.time(); rec={'PART_ID':pid,'PARSE_PASS':False,'EXEC_PASS':False,'STEP_EXPORT_PASS':False,'STEP_READBACK_PASS':False,'ERROR':''}
 try:
  compile(p.read_text(),str(p),'exec'); rec['PARSE_PASS']=True
  ns=runpy.run_path(str(p)); result=ns['result']; rec['EXEC_PASS']=True
  sp=step/f'airplane__{pid}.step'; cq.exporters.export(result,str(sp)); rec['STEP_EXPORT_PASS']=sp.exists() and sp.stat().st_size>0
  obj=cq.importers.importStep(str(sp)); rec['STEP_READBACK_PASS']=obj is not None and obj.val().isValid()
 except Exception:
  rec['ERROR']=traceback.format_exc()[-2500:]
 rec['SECONDS']=round(time.time()-t,3); rows.append(rec); print(pid,rec['EXEC_PASS'],rec['STEP_READBACK_PASS'],rec['SECONDS'])
with open(A/'reports/alignment_repair/cad_step_v2_validity.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
import json
json.dump({'CAD_EXEC_PASS_N':sum(x['EXEC_PASS'] for x in rows),'STEP_READBACK_PASS_N':sum(x['STEP_READBACK_PASS'] for x in rows),'TOTAL':len(rows)},open(A/'reports/alignment_repair/cad_step_v2_validity.json','w'),indent=2)
