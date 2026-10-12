from pathlib import Path
import json,statistics
root=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_cadrecode_parts21_20260926_v2')
for method in ['cadrille','cadrecode']:
 rows=[json.loads(p.read_text()) for p in (root/method).glob('*/PART_*/STATUS.json')]
 good=[x for x in rows if x['status']=='PASS'];cd=[x['normalized_chamfer_squared'] for x in good]
 print(method,'processed',len(rows),'valid',len(good),'median nCD',round(statistics.median(cd),6) if cd else None)
 errors={}
 for r in rows:
  if r['status']!='PASS':
   key=r.get('error','').splitlines()[-1][:120];errors[key]=errors.get(key,0)+1
 print('errors',errors)
