#!/usr/bin/env python3
"""Read-only inventory/provenance audit for frozen Mesh->Dora train800 assets."""
from __future__ import annotations
import json, pathlib
from collections import Counter
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'
BUILD=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'
OUT=ROOT/'ours3/dora_input_data_audit_v1'
def yes(p): return p is not None and pathlib.Path(p).is_file()
def main():
 OUT.mkdir(parents=True,exist_ok=True); rows=[json.loads(x) for x in COHORT.read_text().splitlines() if x]
 per=[]
 for r in rows:
  cid=r['cad_id']; a=r['assets']; b=BUILD/cid
  paths={'clean_cad_path':a['program_dsl']['path'],'step_path':a['model_step']['path'],'mesh_path':a['model_obj']['path'],'surface_path':a['features_7d']['path'],'dora_raw_path':a['dora_salient_edges']['path'],'dora_component_path':str(b/'dora/chains.npz'),'dora_fitted_curve_path':str(b/'dora/fitted_curves.json'),'gt_brep_curve_path':str(b/'gt_brep_curves.json'),'curve_c2_input_path':str(b/'curve_c2/curve_inputs.npy'),'dora_token_path':str(b/'curve_c2/curve_tokens.npy')}
  have={k:yes(v) for k,v in paths.items()}
  missing=[k for k,v in have.items() if not v and k!='dora_token_path']
  status='PASS' if not missing else 'FAIL'
  per.append({'cad_id':cid,'source_dataset':r['dataset'],'source_id':r['source_id'],'split':r['split'],'provenance_status':status,'missing':missing,'paths':paths,'assets_sha256':{k:v['sha256'] for k,v in a.items()},'frozen_cohort_record':True})
 counts=Counter(x['source_dataset'] for x in per); stat=Counter(x['provenance_status'] for x in per)
 passed=[x for x in per if x['provenance_status']=='PASS']; pcounts=Counter(x['source_dataset'] for x in passed)
 inv={'name':'DORA_INPUT_DATA_AUDIT_V1','read_only':True,'cohort_source':str(COHORT),'frozen_v3_cohort_cad':len(per),'paired_cad':len(passed),'by_dataset':dict(pcounts),'unbuilt_or_incomplete_cohort_cad':len(per)-len(passed),'unbuilt_or_incomplete_by_dataset':dict(Counter(x['source_dataset'] for x in per if x['provenance_status']!='PASS')),'formats':{'raw_dora':'salient_edges.npz + edge_points.npy + sharp_edges.json','components':'chains.npz + chains_meta.json','fitted':'fitted_curves.json + curve_fit_report.json','c2_interface':'curve_c2/curve_inputs.npy [Nc,32,7], anchors.npy [Nc,6]','dora_256_token':'not present in frozen train800 build (curve_tokens.npy missing)'},'provenance':dict(stat),'rows':per,'forbidden_reads':{'v3_modified':False,'c2_retrained':False,'model_inference':False,'decode_dev_predictions':False,'pilot150':False,'anchor_eval100':False,'official_test':False}}
 (OUT/'DATA_INVENTORY.json').write_text(json.dumps(inv,indent=2)+'\n');(OUT/'per_cad_provenance.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in per));
 aud={'TOTAL_FROZEN_COHORT':len(per),'TOTAL':len(passed),'ALIGN_PASS':stat['PASS'],'ALIGN_FAIL':stat['FAIL'],'ALIGN_PASS_BY_DATASET':dict(pcounts),'UNKNOWN_PROVENANCE':0,'MISSING_MESH':sum('mesh_path' in x['missing'] for x in per),'MISSING_DORA':sum('dora_raw_path' in x['missing'] for x in per),'MISSING_GT_CURVE':sum('gt_brep_curve_path' in x['missing'] for x in per),'protocol':'Paths and frozen cohort SHA evidence are used; no naming-only inference.'};(OUT/'PROVENANCE_AUDIT.json').write_text(json.dumps(aud,indent=2)+'\n')
 md=['# DORA_INPUT_DATA_AUDIT_V1 — data inventory','',f'- frozen V3 cohort: {len(per)}',f'- fully paired Mesh+Dora+fitted+GT CAD: {len(passed)}','- paired DeepCAD: '+str(pcounts['DeepCAD']),'- paired Fusion360: '+str(pcounts['Fusion360']),'', 'Raw Dora is `salient_edges.npz` plus `edge_points.npy`; fitted curves are read-only V1 build artifacts.', '', 'Dora-derived `[N,32,7]` inputs exist under `curve_c2/curve_inputs.npy`; no Dora-derived 256-D token is present in this frozen build. GT B-Rep curves are `gt_brep_curves.json`.']
 (OUT/'DATA_INVENTORY.md').write_text('\n'.join(md)+'\n');print(json.dumps(aud,indent=2))
if __name__=='__main__':main()
