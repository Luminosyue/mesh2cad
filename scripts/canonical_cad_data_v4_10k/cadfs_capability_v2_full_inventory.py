#!/usr/bin/env python3
"""Read-only full CADFS capability inventory; no OCC, STEP, surface, edge, curve, or C2."""
from __future__ import annotations
import argparse,hashlib,json,os,statistics,sys
from collections import Counter,defaultdict
from multiprocessing import Pool
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path.insert(0,str(ROOT/'scripts'))
from canonical_cad_data_v4_10k.cadfs_capability_v2 import classify_file
SRC=ROOT/'CADFS/featurescript_rp'; OUT=ROOT/'ours3/canonical_cad_data_v4_10k/capability_model_v2/full_inventory_v1'
ADV3={'REQUIRES_LOFT','REQUIRES_SWEEP','REQUIRES_FILLET','REQUIRES_CHAMFER','REQUIRES_SHELL','REQUIRES_PATTERN'}
FEAT2={'REQUIRES_REVOLVE','REQUIRES_MIRROR','REQUIRES_ELLIPSE','REQUIRES_BSPLINE','REQUIRES_ARC_EXECUTION'}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tier(req):
 s=set(req)
 if s & ADV3:return 'Tier-3 ADVANCED'
 if s & FEAT2:return 'Tier-2 FEATURE'
 if s:return 'Tier-1 STRUCTURAL'
 return 'Tier-0 CORE'
def metrics(text):
 return {'operation_count':sum(text.count(x) for x in ('newSketch(','extrude(','revolve(','loft(','sweep(','hole(','opFillet(','opChamfer(','opShell(','opMirror(','linearPattern(','circularPattern(')),'sketch_count':text.count('newSketch('),'profile_count':text.count('qSketchRegion(')+text.count('.imprint'),'source_complexity':0}
def worker(raw):
 p=Path(raw)
 try:
  text=p.read_text(encoding='utf-8',errors='replace'); c=classify_file(p); m=metrics(text)
  entity_count=sum(text.count(x) for x in ('skLine','skArc','skCircle','skEllipse','skSpline','skNurbs'))
  m['source_complexity']=m['operation_count']+m['sketch_count']+m['profile_count']+entity_count
  return {'ok':True,'tier':tier(c['required_capabilities']),'combo':c['new_classifier_label'],'required':c['required_capabilities'],'parse':c['parse_result'],'metrics':m}
 except Exception as e:return {'ok':False,'tier':'UNKNOWN','combo':'UNKNOWN','required':['UNKNOWN'],'parse':'ERROR','error':f'{type(e).__name__}:{e}','metrics':{'operation_count':0,'sketch_count':0,'profile_count':0,'source_complexity':0}}
def newstat():return {'count':0,'operation_hist':Counter(),'sketch_hist':Counter(),'profile_hist':Counter(),'complexity_hist':Counter()}
def add(s,m):
 s['count']+=1
 for key,h in [('operation_count','operation_hist'),('sketch_count','sketch_hist'),('profile_count','profile_hist'),('source_complexity','complexity_hist')]:s[h][m[key]]+=1
def quant(h,n,q):
 target=max(1,int((n-1)*q)+1);seen=0
 for k in sorted(h):
  seen+=h[k]
  if seen>=target:return k
 return 0
def summary(s):
 n=s['count'];out={'count':n}
 for name,h in [('operation_count','operation_hist'),('sketch_count','sketch_hist'),('profile_count','profile_hist'),('source_complexity','complexity_hist')]:
  out[name]={'median':quant(s[h],n,.5),'max':max(s[h]) if s[h] else 0}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=max(1,min(16,os.cpu_count() or 1)));args=ap.parse_args()
 paths=[str(p) for p in SRC.rglob('*.txt')]; OUT.mkdir(parents=True,exist_ok=True)
 tiers=Counter();caps=Counter();combos=defaultdict(newstat);parse=Counter();unknown=Counter()
 with Pool(args.workers) as pool:
  for i,r in enumerate(pool.imap_unordered(worker,paths,chunksize=128),1):
   tiers[r['tier']]+=1;parse[r['parse']]+=1;add(combos[r['combo']],r['metrics'])
   caps.update(r['required'])
   if not r['ok']:unknown[r.get('error','unknown')]+=1
   if i%10000==0: print(json.dumps({'processed':i,'total':len(paths),'tiers':dict(tiers)},sort_keys=True),flush=True)
 report={'experiment':'CADFS_CAPABILITY_V2_FULL_INVENTORY','source_root':str(SRC),'TOTAL':len(paths),'tier_counts':dict(tiers),'capability_marginal_counts':dict(caps),'parse_result_counts':dict(parse),'capability_combinations':{k:summary(v) for k,v in sorted(combos.items())},'UNKNOWN':tiers['UNKNOWN'],'SILENT_FALLBACK':0,'heavy_generation':False,'occ_run':False,'step_run':False,'c2_run':False,'classifier_sha256':sha(ROOT/'scripts/canonical_cad_data_v4_10k/cadfs_capability_v2.py'),'schema_sha256':sha(ROOT/'scripts/canonical_cad_data_v4_10k/canonical_dsl_v4_1_core_schema.json')}
 (OUT/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps({'complete':True,'TOTAL':len(paths),'tier_counts':dict(tiers),'UNKNOWN':tiers['UNKNOWN']},indent=2))
if __name__=='__main__':main()

