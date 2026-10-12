#!/usr/bin/env python3
"""Read-only V3 held-out raw-source inventory, including CADFS support evidence."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OLD=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/pool/EXTERNAL_POOL_INVENTORY.json'
CADFS=ROOT/'ours3/canonical_cad_data_v4_10k/canary_execution_v1/audits/CADFS_SUPPORTED_150_PARSER_REPORT.json'
OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool'

def main():
    old=json.loads(OLD.read_text()); ca=json.loads(CADFS.read_text()); s=old['summary']
    report={'phase':'RAW_DATASET_INVENTORY_READ_ONLY','priority':'DeepCAD,Fusion360 then CADFS only as separately-labelled OOD if necessary',
      'DeepCAD':{'total_source':s['DeepCAD']['total_available'],'has_step_or_executable_cad':s['DeepCAD']['new_base_complete']+s['DeepCAD']['already_in_train688'],'already_in_v3_800':s['DeepCAD']['already_in_v3_800'],'already_in_train688':s['DeepCAD']['already_in_train688'],'new_source_candidates':s['DeepCAD']['new_candidates'],'new_base_complete':s['DeepCAD']['new_base_complete'],'missing_asset_counts':s['DeepCAD']['missing_asset_counts']},
      'Fusion360':{'total_source':s['Fusion360']['total_available'],'has_step_or_executable_cad':s['Fusion360']['new_base_complete']+s['Fusion360']['already_in_train688'],'already_in_v3_800':s['Fusion360']['already_in_v3_800'],'already_in_train688':s['Fusion360']['already_in_train688'],'new_source_candidates':s['Fusion360']['new_candidates'],'new_base_complete':s['Fusion360']['new_base_complete'],'missing_asset_counts':s['Fusion360']['missing_asset_counts']},
      'CADFS':{'total_source':s['CADFS']['total_available'],'already_used':0,'new_source_candidates':s['CADFS']['new_candidates'],'current_dsl_supported_evidence':'only 41/150 parser-pass in existing V4 canary; not eligible for main ID heldout without a fresh compatible clean gate','current_dsl_supported_observed':ca['PARSE_OK'],'current_dsl_unsupported_or_classifier_false_supported_observed':ca['PARSE_FAIL'],'evidence_path':str(CADFS)},
      'read_only':True,'forbidden_model_reads':{'decode_dev50':False,'pilot150':False,'anchor_eval100':False,'official_test':False}}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'DATASET_INVENTORY.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# V3 held-out raw inventory','', '| Dataset | Total | Used in train688 | New raw candidates | Base complete |', '|---|---:|---:|---:|---:|']
    for name in ('DeepCAD','Fusion360'):
      x=report[name];lines.append(f"| {name} | {x['total_source']} | {x['already_in_train688']} | {x['new_source_candidates']} | {x['new_base_complete']} |")
    lines += ['',f"CADFS: {report['CADFS']['total_source']} source records; existing capability evidence is only {ca['PARSE_OK']}/{ca['TOTAL']} parser-pass, so it is not selected for the ID clean held-out build.",'', 'No raw candidate is treated as clean until the full V3 mesh/surface/DSL/curve/C2/actual-splice/leakage gate passes.']
    (OUT/'DATASET_INVENTORY.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
