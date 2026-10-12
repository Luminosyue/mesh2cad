#!/usr/bin/env python3
import csv,json,unittest
from pathlib import Path
import numpy as np

R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
S=R/'cad_part_recovery_v1'; A=S/'artifacts'; C=S/'cases'
f1=json.load(open(A/'track_f1_summary.json')); f2=json.load(open(A/'track_f2_summary.json')); summary=json.load(open(A/'cad_part_recovery_v1_summary.json')); manifest=json.load(open(A/'track_f1_manifest.json'))

class StageTests(unittest.TestCase):
 def test_01_exactly_four_ready_parts(self): self.assertEqual(len(manifest['cases']),4)
 def test_02_manifest_ids_frozen(self): self.assertEqual([x['case_id'] for x in manifest['cases']],['CADPART_000','CADPART_001','CADPART_004','CADPART_006'])
 def test_03_review_parts_not_sent_to_mac(self): self.assertEqual({x['case_id'] for x in manifest['cases']},{'CADPART_000','CADPART_001','CADPART_004','CADPART_006'})
 def test_04_existing_mac_result_reuse(self): self.assertEqual([x['case_id'] for x in manifest['cases'] if x['REUSE_EXISTING_MAC_RESULT']],['CADPART_000','CADPART_004'])
 def test_05_mesh_sha_reuse_validation(self):
  for cid in ('CADPART_000','CADPART_004'):
   a=json.load(open(C/cid/'existing_mac_reuse_audit.json')); self.assertTrue(a['p3_id_match'] and a['triangle_ids_match'] and a['mesh_geometry_sha256_match'])
 def test_06_physx_soft_only(self):
  for x in manifest['cases']:
   s=json.load(open(x['fused_spec'])); self.assertEqual(s['PHYSX_CONSTRAINT_PRIORITY'],'SOFT'); self.assertFalse(s['physx_semantic']['hard_constraint'])
 def test_07_geometry_hard_priority(self):
  for x in manifest['cases']: self.assertEqual(json.load(open(x['fused_spec']))['GEOMETRY_CONSTRAINT_PRIORITY'],'HARD')
 def test_08_no_simplest_solid_when_secondary_features(self):
  for x in manifest['cases']:
   p=Path(x['prompt']).read_text(); self.assertNotIn('Construct the simplest solid',p); self.assertNotIn('Make the simplest watertight approximation',p); self.assertNotIn('Ignore secondary geometry',p)
 def test_09_simplification_directive_false(self): self.assertTrue(all(not x['SIMPLIFICATION_DIRECTIVE_USED'] for x in manifest['cases']))
 def test_10_prompt_feature_coverage(self): self.assertTrue(all(x['PROMPT_FEATURE_COVERAGE']>=.9 for x in manifest['cases']))
 def test_11_spec_ready(self): self.assertTrue(all(x['SPEC_READY'] for x in manifest['cases']))
 def test_12_alignment_fix_reused(self):
  for x in manifest['cases']:
   p=Path(x['mac_output_dir'])/'transform_ledger.json'
   if (Path(x['mac_output_dir'])/'generated.step').is_file(): self.assertTrue(json.load(open(p))['MISSING_TRANSLATION_INVERSE_FIX_REUSED'])
 def test_13_transform_roundtrip(self):
  for x in manifest['cases']:
   p=Path(x['mac_output_dir'])/'transform_ledger.json'
   if p.is_file():
    t=json.load(open(p)); self.assertTrue(t['ROUNDTRIP_PASS']); self.assertLess(t['ROUNDTRIP_MAX_ERROR_NORMALIZED'],1e-8)
 def test_14_independent_brepcheck(self): self.assertTrue(all('brep_valid' in x['qa'] for x in f1['CASES']))
 def test_15_fresh_step_tessellation(self): self.assertTrue(all(x['qa']['fresh_step_tessellation'] for x in f1['CASES'] if (Path(x['mac_output_dir'])/'generated.step').is_file()))
 def test_16_no_icp(self): self.assertTrue(all(not x['qa']['icp_used'] for x in f1['CASES']))
 def test_17_quality_thresholds_unchanged(self): self.assertEqual(manifest['quality_thresholds'],{'Q1':{'chamfer_max':.01,'p95_max':.02,'coverage02_min':.95},'Q2':{'chamfer_max':.02,'p95_max':.05,'coverage02_min':.85}})
 def test_18_q_classes_recomputed(self):
  for x in f1['CASES']:
   q=x['qa']; expected='Q1_STRONG_PAIR' if q['brep_valid'] and q['symmetric_chamfer_normalized']<=.01 and q['p95_symmetric']<=.02 and q['coverage_02']>=.95 else ('Q2_USABLE_PAIR' if q['brep_valid'] and q['symmetric_chamfer_normalized']<=.02 and q['p95_symmetric']<=.05 and q['coverage_02']>=.85 else 'Q3_REJECT'); self.assertEqual(q['quality_class'],expected)
 def test_19_q3_not_exported(self):
  for x in f1['CASES']:
   if x['qa']['quality_class']=='Q3_REJECT': self.assertFalse((R/'real03_cad_parts_v1'/x['case_id']).exists())
 def test_20_accepted_exported(self):
  for x in f1['CASES']:
   if x['qa']['quality_class'] in ('Q1_STRONG_PAIR','Q2_USABLE_PAIR'): self.assertTrue((R/'real03_cad_parts_v1'/x['case_id']/'part.step').is_file())
 def test_21_local_global_transform_preserved(self):
  for x in f1['CASES']:
   p=Path(x['mac_output_dir'])/'transform_ledger.json'
   if p.is_file():
    t=json.load(open(p)); self.assertTrue(np.allclose(np.array(t['SOURCE_TO_CANONICAL'])@np.array(t['CANONICAL_TO_SOURCE']),np.eye(4),atol=1e-10))
 def test_22_feature_realization_present(self): self.assertTrue(all(0<=x['qa']['FEATURE_REALIZATION_RATE']<=1 for x in f1['CASES']))
 def test_23_exactly_14_review_edges(self): self.assertEqual(f2['REVIEW_EDGES_PREPARED'],14)
 def test_24_review_csv_schema(self):
  with open(A/'review_merge_edges_14.csv',newline='') as h: rows=list(csv.DictReader(h))
  self.assertEqual(len(rows),14); self.assertEqual(set(rows[0]),{'EDGE_ID','P3_A','P3_B','GEOMETRY_SCORE','PHYSX_SCORE','FINAL_SCORE','SEMANTIC_A','SEMANTIC_B','CURRENT_DECISION','HUMAN_DECISION','NOTES'}); self.assertTrue(all(not r['HUMAN_DECISION'] and not r['NOTES'] for r in rows))
 def test_25_review_packets_complete(self): self.assertTrue(f2['REVIEW_PACKETS_COMPLETE'])
 def test_26_review_parts_20(self): self.assertEqual(f2['REVIEW_PARTS_PREPARED'],20)
 def test_27_no_auto_merge_f2(self): self.assertFalse(f2['HUMAN_DECISIONS_APPLIED'])
 def test_28_no_f2_model_runs(self): self.assertEqual((f2['NEW_MAC_RUNS'],f2['NEW_PHYSX_RUNS'],f2['NEW_P3_RUNS']),(0,0,0))
 def test_29_no_assembly_step(self): self.assertFalse(summary['ASSEMBLY_STEP_GENERATED']); self.assertFalse(any(S.rglob('assembly.step')))
 def test_30_no_ground_truth(self): self.assertFalse(summary['STEP_GT_USED'] or summary['ABC_DATA_USED'])
 def test_31_recovery_rate(self): self.assertAlmostEqual(summary['PART_CAD_RECOVERY_RATE'],(summary['Q1_STRONG_PAIR']+summary['Q2_USABLE_PAIR'])/4)
 def test_32_partial_ready_definition(self): self.assertEqual(summary['PARTIAL_ASSEMBLY_PILOT_READY'],summary['ASSEMBLY_CAD_PARTS_AVAILABLE']>=2)
 def test_33_new_mac_exact(self): self.assertEqual(summary['NEW_MAC_ATTEMPTED'],2)
 def test_34_total_steps(self): self.assertEqual(summary['TOTAL_STEP_AVAILABLE'],3)
 def test_35_blockers(self): self.assertEqual(summary['BLOCKERS_BY_TRACK'],{'F1':['QUOTA'],'F2':[]})
 def test_36_quota_audit(self):
  q=json.load(open(A/'quota_blocker_audit.json')); self.assertEqual((q['blocker_enum'],q['provider_error_code'],q['llm_calls'],q['tokens']),('QUOTA',403,0,0)); self.assertFalse(q['retry_performed'] or q['matching_historical_step_found'])
 def test_37_f1_blocked_precisely(self): self.assertEqual(summary['TRACK_F1_STATUS'],'BLOCKED')

if __name__=='__main__':unittest.main(verbosity=2)
