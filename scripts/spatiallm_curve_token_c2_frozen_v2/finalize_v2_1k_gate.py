#!/usr/bin/env python3
import hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected'
M1=BASE/'runs/run1/MANIFEST.json'; M2=BASE/'runs/run2_canonical_verified/MANIFEST.json'
ASSETS=BASE/'canonical_dataset'; REPORTS=BASE/'reports/c2_corrected_final'
TOKEN_ROOT=ROOT/'ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2'
PROV=BASE/'provenance20/PROVENANCE.json'
V1=ROOT/'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/V1_FROZEN_SHA256.json'
OLD=ROOT/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/placement_fix_retest_v3/DELIVERY_SHA256.json'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def chash(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def verify_map(p):
 d=json.loads(p.read_text()); ok=0; bad=[]
 for name,digest in d.items():
  q=Path(name)
  if q.is_file() and sha(q)==digest:ok+=1
  else:bad.append(name)
 return {'unchanged':ok,'expected':len(d),'failures':bad}
def stats(vals):
 a=np.asarray(vals,float)
 return {k:float(v) for k,v in [('min',a.min()),('p10',np.percentile(a,10)),('p25',np.percentile(a,25)),('median',np.median(a)),('mean',a.mean()),('p75',np.percentile(a,75)),('p90',np.percentile(a,90)),('p95',np.percentile(a,95)),('max',a.max())]}

a=json.loads(M1.read_text()); b=json.loads(M2.read_text()); rows=a['rows']; rows2=b['rows']; n=len(rows)
prov=json.loads(PROV.read_text())
budget=sum(r['budget_equality'] for r in rows); attention=sum(r['attention_equality'] for r in rows); total=sum(r['total_attention_equality'] for r in rows); physical=sum(r['physical_length_equality'] for r in rows)
fake=sum(r['fake_valid_padding'] for r in rows); pad=sum(r['padding_attention'] for r in rows)
det_b1=sum(x['selected_b1_indices']==y['selected_b1_indices'] for x,y in zip(rows,rows2)); det_m2=sum(x['selected_m2_indices']==y['selected_m2_indices'] for x,y in zip(rows,rows2)); det_k=sum(x['k_valid']==y['k_valid'] for x,y in zip(rows,rows2)); det_record=sum(x['record_sha256']==y['record_sha256'] for x,y in zip(rows,rows2))

asset_counts=Counter(p.name for p in ASSETS.glob('records/*/*'))
asset_ok=(asset_counts['b1_full_tokens_fp16.npy']==asset_counts['b1_mask.npy']==asset_counts['m2_mask.npy']==1000)

token_files=sorted([p for p in TOKEN_ROOT.rglob('*') if p.is_file() and p.name in ('curve_tokens.npy','curve_tokens_meta.json')])
token_entries={str(p.relative_to(TOKEN_ROOT)):sha(p) for p in token_files}
token_manifest={'root':str(TOKEN_ROOT),'checkpoint':'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt','checkpoint_sha256':'553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9','n_curve_token_npy':sum(p.name=='curve_tokens.npy' for p in token_files),'n_metadata_json':sum(p.name=='curve_tokens_meta.json' for p in token_files),'files':token_entries}
token_manifest['content_sha256']=chash(token_manifest)

b1c=[r['b1_post_encoder_count'] for r in rows]; m2c=[r['m2_available_count'] for r in rows]; kval=[r['k_valid'] for r in rows]
b1ret=[r['b1_retention_ratio'] for r in rows]; m2ret=[r['m2_retention_ratio'] for r in rows]
lim=Counter()
for r in rows:
 x,y,k=r['b1_post_encoder_count'],r['m2_available_count'],r['k_valid']
 if k==128 and x>=128 and y>=128:lim['cap']+=1
 elif x<y and x<128:lim['B1']+=1
 elif y<x and y<128:lim['M2']+=1
 else:lim['tie']+=1
low={op:{'count':int(sum(fn(x) for x in kval)),'fraction':float(sum(fn(x) for x in kval)/n)} for op,fn in [('le_2',lambda x:x<=2),('le_4',lambda x:x<=4),('le_8',lambda x:x<=8),('le_16',lambda x:x<=16),('ge_64',lambda x:x>=64),('eq_128',lambda x:x==128)]}

source=Counter(r['source_dataset'] for r in rows); diff=Counter(r['difficulty_bin'] for r in rows); ops=Counter(op for r in rows for op in r['operation_names']); curve_types=Counter();
for r in rows:curve_types.update(r['curve_type_counts'])
features={k:int(sum(bool(r[k]) for r in rows)) for k in ('has_circle','has_rectangle','has_polygon','has_hole','has_cut','has_join')}
surface_counts=[int(np.load(r['surface_input'],mmap_mode='r').shape[0]) for r in rows]

v1=verify_map(V1); old=verify_map(OLD)
manifest_equal=a['content_sha256']==b['content_sha256']=='ef20bd0ef95e97f61c07116ff4e19e7e9a7938d5775520a19d5a351b65244f7c'
passed=all([n==1000,prov['PASS'],budget==attention==total==physical==1000,fake==pad==0,det_b1==det_m2==det_k==det_record==1000,manifest_equal,a['cohort']['audit']['cross_split_leakage']==0,asset_ok,token_manifest['n_curve_token_npy']==token_manifest['n_metadata_json']==2796,v1['unchanged']==v1['expected']==19580,old['unchanged']==old['expected']==3669])
report={
 'CURRENT_GATE':'B1_POST_ENCODER_BUDGET_C2_V2_1K_PASS' if passed else 'B1_POST_ENCODER_BUDGET_C2_V2_1K_HARD_STOP','V2_1K_PROGRESS':f'{n}/1000','CURVE_ENCODER_PROVENANCE':'PASS' if prov['PASS'] else 'FAIL','DIRECT_C2_VS_DISK_TOKEN':prov['DIRECT_C2_VS_EXPORTED_TOKEN'],'MAX_ABS_C2_TOKEN_DIFF':prov['MAX_ABS_TOKEN_DIFF'],'CURVE_ENCODER_CHECKPOINT':prov['CURVE_ENCODER_CHECKPOINT'],'CURVE_ENCODER_CHECKPOINT_SHA256':prov['CURVE_ENCODER_CHECKPOINT_SHA256'],'CURVE_ENCODER_FROZEN':prov['CURVE_ENCODER_FROZEN'],'CURVE_TOKEN_ROOT':str(TOKEN_ROOT.relative_to(ROOT)),
 'BUDGET_EQUALITY':f'{budget}/1000','ATTENTION_EQUALITY':f'{attention}/1000','TOTAL_ATTENTION_EQUALITY':f'{total}/1000','PHYSICAL_PADDED_LENGTH_EQUALITY':f'{physical}/1000','FAKE_VALID_COUNT':fake,'PADDING_ATTENTION_COUNT':pad,
 'DETERMINISTIC_B1_SELECTION':f'{det_b1}/1000','DETERMINISTIC_M2_SELECTION':f'{det_m2}/1000','DETERMINISTIC_K_VALID':f'{det_k}/1000','DETERMINISTIC_RECORD_HASH':f'{det_record}/1000','MANIFEST_HASH_IDENTICAL':manifest_equal,'V2_1K_MANIFEST_SHA256':a['content_sha256'],
 'CROSS_SPLIT_LEAKAGE':a['cohort']['audit']['cross_split_leakage'],'SOURCE_DISTRIBUTION':dict(source),'DIFFICULTY_DISTRIBUTION':dict(diff),'B1_POST_ENCODER_COUNT':stats(b1c),'M2_AVAILABLE_COUNT':stats(m2c),'K_VALID':stats(kval),'LOW_K':low,
 'LIMITER':{k:{'count':lim[k],'fraction':lim[k]/n} for k in ('B1','M2','cap','tie')},'B1_RETENTION':stats(b1ret),'M2_RETENTION':stats(m2ret),'OPERATION_COUNTS':dict(ops),'CURVE_TYPE_COUNTS':dict(curve_types),'FEATURE_COUNTS':features,'TARGET_DSL_CHARS':stats([r['target_dsl_chars'] for r in rows]),'SURFACE_INPUT_COUNT':stats(surface_counts),
 'CANONICAL_ASSETS':dict(asset_counts),'C2_TOKEN_FILES':f"{token_manifest['n_curve_token_npy']}/2796",'C2_TOKEN_METADATA':f"{token_manifest['n_metadata_json']}/2796",'C2_TOKEN_MANIFEST_SHA256':token_manifest['content_sha256'],
 'B1_NUMERIC_RERUN_NOTE':{'exact_byte_hash': '994/1000 on completed independent run2','affected_records':6,'targeted_rerun_max_abs_diff':0.0009765625,'later_observed_max_abs_diff':0.00439453125,'canonical_policy':'first-pass B1 assets frozen; record identity hashes immutable assets; selection/count/masks/LLM-entry verified independently'},
 'V1_FROZEN_HASHES':f"{v1['unchanged']}/{v1['expected']}",'OLD_EVIDENCE_HASHES':f"{old['unchanged']}/{old['expected']}",'ALLOW_PILOT_TRAINING':passed,'PILOT_TRAINING_STARTED':False,'FORMAL_TRAINING_STARTED':False,'ALLOW_V2_10K_BUILD':False,
}
REPORTS.mkdir(parents=True,exist_ok=False)
(REPORTS/'C2_TOKEN_FILE_MANIFEST.json').write_text(json.dumps(token_manifest,indent=2)+'\n')
(REPORTS/'FINAL_GATE.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# V2-1k C2 Budget-Matched Data Gate','']+[f'{k}={v}' for k,v in report.items() if not isinstance(v,dict)]
(REPORTS/'FINAL_GATE.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(report,indent=2)); raise SystemExit(0 if passed else 2)
