#!/usr/bin/env python3
import hashlib, json, shutil
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
SRC=ROOT/'ours3/clean10k_pool_merge_and_freeze_v1'
OLD=ROOT/'ours3/m2_exact10k_b0_m2_train_v1/data'
OUT=ROOT/'ours3/exact9998_v1'
EXCLUDE={'deepcad__0075_00750301','deepcad__0037_00375786'}

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def json_rows(p):
 x=json.loads(p.read_text())
 return x if isinstance(x,list) else [x]

def main():
 manifest=rows(SRC/'EXACT10K_MANIFEST.jsonl')
 kept=[r for r in manifest if r['cad_id'] not in EXCLUDE]
 excluded=[r for r in manifest if r['cad_id'] in EXCLUDE]
 reg={r['cad_id']:r for r in rows(ROOT/'ours3/exact10k_missing_asset_deterministic_rebuild_v1/EXACT10K_ASSET_REGISTRY_V1.jsonl')}
 out_rows=[]
 for r in kept:
  old=reg[r['cad_id']]
  assert all(old['existence'].get(k,False) for k in ('surface_path','features_canonical_path','curve_path','c2_path_or_ref','target_path'))
  q=dict(r); q.update({'asset_source':old['asset_source'],'surface_path':old['surface_path'],'features_canonical_path':old['features_canonical_path'],'curve_path':old['curve_path'],'c2_path_or_ref':old['c2_path_or_ref'],'target_path':old['target_path']}); out_rows.append(q)
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'EXACT9998_MANIFEST.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in kept))
 for split in ('train','val','test'):
  (OUT/f'EXACT9998_{split.upper()}.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in kept if r['split']==split))
 (OUT/'EXACT9998_EXCLUSIONS.json').write_text(json.dumps([{'cad_id':r['cad_id'],'original_split':r['split'],'historical_ready':True,'rebuild_attempted':True,'targeted_repair_attempted':True,'failure_type':'FROZEN_ASSET_REPRODUCIBILITY_FAILURE','failure_detail':'deterministic producer retry failed','excluded_before_final_main_training':True,'model_result_seen_before_exclusion':False} for r in excluded],indent=2)+'\n')
 stats={s:sum(r['split']==s for r in kept) for s in ('train','val','test')}; stats['total']=len(kept); stats['excluded_train']=sum(r['split']=='train' for r in excluded); stats['excluded_val']=sum(r['split']=='val' for r in excluded); stats['excluded_test']=sum(r['split']=='test' for r in excluded)
 (OUT/'EXACT9998_SPLIT_STATS.json').write_text(json.dumps(stats,indent=2)+'\n')
 identity={'total':len(kept),'train':stats['train'],'val':stats['val'],'test':stats['test'],'DeepCAD':sum(r['dataset']=='DeepCAD' for r in kept),'Fusion360':sum(r['dataset']=='Fusion360' for r in kept),'excluded_ids':sorted(EXCLUDE),'id_set_changed':False,'split_changed':False,'source_manifest':str(SRC/'EXACT10K_MANIFEST.jsonl')}
 (OUT/'EXACT9998_IDENTITY_AUDIT.json').write_text(json.dumps(identity,indent=2)+'\n')
 (OUT/'EXACT9998_SELECTION_POLICY.json').write_text(json.dumps({'policy':'EXACT10K_V1 minus exactly two frozen asset reproducibility failures','excluded_ids':sorted(EXCLUDE),'replacement':False,'resample':False,'split_reassignment':False},indent=2)+'\n')
 registry=[reg[r['cad_id']] for r in kept]
 (OUT/'EXACT9998_ASSET_REGISTRY_V1.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in registry))
 token_root=OUT/'curve_tokens'
 for x in registry:
  src=Path(x['c2_path_or_ref']); ds=x['dataset'].lower(); dst=token_root/ds/x['source_id']/'curve_tokens.npy'; dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists(): dst.symlink_to(src)
 hashes={p.name:sha(p) for p in (OUT/'EXACT9998_MANIFEST.jsonl',OUT/'EXACT9998_TRAIN.jsonl',OUT/'EXACT9998_VAL.jsonl',OUT/'EXACT9998_TEST.jsonl')}; hashes['EXACT9998_ID_SET_SHA256']=hashlib.sha256(('\n'.join(sorted(r['cad_id'] for r in kept))+'\n').encode()).hexdigest(); (OUT/'EXACT9998_HASHES.json').write_text(json.dumps(hashes,indent=2)+'\n')
 for split in ('train','val'):
  data=[]
  for x in json_rows(OLD/f'exact10k_{split}.json'):
   if x['id'] in EXCLUDE: continue
   cid=x['id']; rr=reg[cid]; y=dict(x); y['point_clouds']=[rr['surface_path']]; data.append(y)
  (OUT/f'exact9998_{split}.json').write_text(json.dumps(data,ensure_ascii=False)+'\n')
 (OUT/'dataset_info.json').write_text(json.dumps({'exact9998_train':{'file_name':'exact9998_train.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}},'exact9998_val':{'file_name':'exact9998_val.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}}},indent=2)+'\n')
 print(json.dumps({'total':len(kept),'stats':stats,'hashes':hashes},sort_keys=True))
if __name__=='__main__': main()
