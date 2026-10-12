#!/usr/bin/env python3
"""Read-only inventory of CAD outside the frozen V3 800 cohort."""
from __future__ import annotations
import json,pathlib,hashlib
from collections import Counter
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad'); OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/pool'; OUT.mkdir(parents=True,exist_ok=True)
COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'
V3=json.loads((ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json').read_text())['records']
v3ids={r['cad_id'] for r in V3}; v3source={str(r.get('provenance',{}).get('source_id',r['cad_id'])) for r in V3}
SOURCES={'DeepCAD':ROOT/'cad_spatial_dataset/DeepCAD/train','Fusion360':ROOT/'cad_spatial_dataset/Fusion360/train','CADFS':ROOT/'cad_spatial_dataset/CADFS/train'}
def base_ok(p):
 return {'model_step':(p/'model.step').is_file(),'model_obj':(p/'model.obj').is_file(),'dsl':(p/'program_canonical.dsl').is_file(),'transform':(p/'coordinate_transform.json').is_file(),'features_7d':(p/'features_canonical.npy').is_file()}
def main():
 rows=[]; summary={}
 for ds,root in SOURCES.items():
  dirs=sorted(x for x in root.iterdir() if x.is_dir()) if root.is_dir() else []
  for p in dirs:
   cid=(ds.lower()+'__'+p.name) if ds!='DeepCAD' else ('deepcad__'+p.name)
   # V3 Fusion IDs preserve prefix, so also compare terminal source directory.
   in_v3=cid in v3ids or any(x.endswith('__'+p.name) for x in v3ids)
   checks=base_ok(p); rows.append({'dataset':ds,'source_path':str(p),'source_id':p.name,'candidate_id':cid,'in_v3_800':in_v3,'in_train688':in_v3,'base_checks':checks,'base_complete':all(checks.values())})
  z=[r for r in rows if r['dataset']==ds]
  summary[ds]={'total_available':len(z),'already_in_v3_800':sum(r['in_v3_800'] for r in z),'already_in_train688':sum(r['in_train688'] for r in z),'new_candidates':sum(not r['in_v3_800'] for r in z),'new_base_complete':sum((not r['in_v3_800']) and r['base_complete'] for r in z),'missing_asset_counts':dict(Counter(k for r in z if not r['in_v3_800'] for k,v in r['base_checks'].items() if not v))}
 # Deterministic candidate ordering only; no quality gate is claimed here.
 cand=sorted([r for r in rows if not r['in_v3_800'] and r['base_complete']],key=lambda r:hashlib.sha256((r['dataset']+'|'+r['source_id']).encode()).hexdigest())
 (OUT/'EXTERNAL_POOL_INVENTORY.json').write_text(json.dumps({'summary':summary,'v3_train688':len(v3ids),'records':rows,'candidate_ordering':'sha256(dataset|source_id) ascending','new_base_complete_candidates':len(cand)},indent=2)+'\n')
 (OUT/'NEW_BASE_COMPLETE_CANDIDATES.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in cand))
 (OUT/'EXTERNAL_POOL_INVENTORY.md').write_text('# External pool inventory\n\nThis is a read-only asset inventory, not a clean-gate pass. `new_base_complete` means only that STEP, OBJ, DSL, transform, and 7D features exist. Tessellation, real V3 context, GT execution, curve/C2, and leakage/fingerprint gates remain to be run before any candidate is used.\n\n'+json.dumps(summary,indent=2)+'\n')
 print(json.dumps({'summary':summary,'candidate_count':len(cand)},indent=2))
if __name__=='__main__':main()
