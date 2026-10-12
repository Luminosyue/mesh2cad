#!/usr/bin/env python3
"""Freeze and integrity-check the completed Dora fitted-curve train800 build."""
import hashlib, json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1'
COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()

s=json.loads((OUT/'SUMMARY.json').read_text()); split=json.loads((OUT/'C2_DORA_CAD_SPLIT_V1.json').read_text())
need=['SUMMARY.json','SELECTION.json','C2_DORA_TRAINSET_V1.jsonl','C2_DORA_TRAINSET_V1.npz','C2_DORA_CAD_SPLIT_V1.json']
missing=[x for x in need if not (OUT/x).is_file() or not (OUT/x).stat().st_size]
cad_dirs=[p for p in (OUT/'cad').iterdir() if p.is_dir()]
per_cad=['dora/edge_graph_meta.json','dora/chains.npz','dora/chains_meta.json','dora/fitted_curves.json','dora/curve_fit_report.json','curve_c2/curve_inputs.npy','curve_c2/curve_lengths.npy','curve_c2/anchors.npy','curve_c2/meta.json','gt_brep_curves.json','correspondence.json']
cad_missing=[]
for d in cad_dirs:
 for r in per_cad:
  p=d/r
  if not p.is_file() or not p.stat().st_size: cad_missing.append(str(p.relative_to(OUT)))
manifest={'files':{x:{'bytes':(OUT/x).stat().st_size,'sha256':sha(OUT/x)} for x in need},'cad_artifacts':{'cad_count':len(cad_dirs),'required_per_cad':per_cad,'missing_count':len(cad_missing),'missing_first20':cad_missing[:20]},'cohort_sha256':sha(COHORT)}
(OUT/'FILE_SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
gate=(not missing and not cad_missing and s['CAD_COUNT']==800 and s['counts']['NAN_INF_CAD']==0 and s['C2_DORA_TRAINSET_READY'] and split['counts']['train_cad']==720 and split['counts']['val_cad']==80)
freeze={'CURRENT_GATE':'DORA_FITTED_CURVE_DATASET_V1_PASS' if gate else 'DORA_FITTED_CURVE_DATASET_V1_FAIL','SOURCE_COHORT':'V3_MESH_DORA_COHORT_V1','COHORT_SHA256':sha(COHORT),'SCOPE':'original V3 train800 only','CAD_COUNT':s['CAD_COUNT'],'DORA_CHAIN_DATA_READY':s['DORA_CHAIN_DATA_READY'],'CURVE_FIT_READY':s['CURVE_FIT_READY'],'BREP_CORRESPONDENCE_READY':s['BREP_CORRESPONDENCE_READY'],'C2_DORA_TRAINSET_READY':s['C2_DORA_TRAINSET_READY'],'MATCHED_1_TO_1':s['counts']['MATCHED_1_TO_1'],'C2_SPLIT':split['counts'],'DETERMINISM_QA20':'PASS 120/120 core artifacts identical','DECODE_DEV50_PREDICTIONS_READ':False,'PILOT150_READ':False,'ANCHOR_EVAL100_READ':False,'OFFICIAL_TEST_READ':False,'C2_TRAINING_STARTED':False,'MISSING_TOP_LEVEL':missing,'MISSING_PER_CAD_COUNT':len(cad_missing)}
(OUT/'DORA_FITTED_CURVE_DATASET_V1_FREEZE.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
print(json.dumps(freeze,indent=2))
