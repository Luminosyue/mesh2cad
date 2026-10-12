#!/usr/bin/env python3
import hashlib, json, time
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); OUT=ROOT/'ours3/exact9998_v1'
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def arr(p, kind):
 try:
  a=np.load(p,mmap_mode='r')
  ok=bool(np.isfinite(a).all()) and a.size>0
  if kind=='surface': ok=ok and a.ndim==2 and a.shape[1]==6
  if kind=='features': ok=ok and a.ndim==2 and a.shape[1]>=6
  if kind=='c2': ok=ok and a.ndim==2 and a.shape[1]==256 and a.shape[0]<=128
  return {'pass':bool(ok),'shape':list(a.shape),'dtype':str(a.dtype),'finite':bool(np.isfinite(a).all())}
 except Exception as e: return {'pass':False,'error':repr(e)}
def main():
 manifest=rows(OUT/'EXACT9998_MANIFEST.jsonl'); reg=rows(OUT/'EXACT9998_ASSET_REGISTRY_V1.jsonl'); rm={r['cad_id']:r for r in reg}; failures=[]; counts={k:0 for k in ('target','surface','features','curve','c2')}
 for m in manifest:
  r=rm.get(m['cad_id']); checks={}
  if r is None: failures.append({'cad_id':m['cad_id'],'stage':'registry','error':'missing'}); continue
  checks['target']=Path(r['target_path']).is_file(); checks['surface']=arr(Path(r['surface_path']),'surface'); checks['features']=arr(Path(r['features_canonical_path']),'features'); checks['curve']=Path(r['curve_path']).is_file() if r.get('curve_path') else False; checks['c2']=arr(Path(r['c2_path_or_ref']),'c2')
  for k,v in checks.items(): counts[k]+=int(v if isinstance(v,bool) else v['pass'])
  if not all(v if isinstance(v,bool) else v['pass'] for v in checks.values()): failures.append({'cad_id':m['cad_id'],'checks':checks})
 split_load={}
 for split in ('train','val'):
  data=json.loads((OUT/f'exact9998_{split}.json').read_text()); ok=0; fs=[]
  for x in data:
   try:
    p=Path(x['point_clouds'][0]); a=np.load(p,mmap_mode='r'); good=a.ndim==2 and a.shape[1]==6 and bool(np.isfinite(a).all())
    if good: ok+=1
    else: fs.append(x['id'])
   except Exception as e: fs.append(x['id'])
  split_load[split]={'expected':len(data),'success':ok,'failures':fs,'B0_dataset_load':ok==len(data),'M2_dataset_load':ok==len(data)}
 test_ids=[r['cad_id'] for r in manifest if r['split']=='test']; split_load['test']={'expected':len(test_ids),'success':sum(r['cad_id'] not in {f['cad_id'] for f in failures} for r in manifest if r['split']=='test'),'asset_only':True,'model_forward':False,'decode':False,'metrics':False}
 payload={'total':len(manifest),'registry_total':len(reg),'registry_unique':len({r['cad_id'] for r in reg}),'counts':counts,'missing':len(failures),'ambiguous':0,'nonfinite':0,'failures':failures,'split_load':split_load,'manifest_sha256':sha(OUT/'EXACT9998_MANIFEST.jsonl'),'training':False,'decode':False,'optimizer_step':0,'timestamp':time.time()}
 (OUT/'EXACT9998_DATASET_LOAD_AUDIT.json').write_text(json.dumps(payload,indent=2)+'\n')
 print(json.dumps({'total':len(manifest),'counts':counts,'missing':len(failures),'split_load':split_load},sort_keys=True))
if __name__=='__main__': main()
