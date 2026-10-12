import csv,hashlib,json,unittest
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'batch_part_to_cad_recovery_v2';TARGETS=['CASE_00','CASE_02','CASE_03','CASE_04','CASE_05','CASE_08','CASE_09']
def load(p):return json.loads(Path(p).read_text())
class BatchV2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.inv=load(OUT/'manifest/input_inventory.json');c.new={x:load(OUT/'cases'/x/'case_result.json') for x in TARGETS};c.reg=load(OUT/'artifacts/best_result_registry.json');c.probe=load(OUT/'artifacts/mac_endpoint_probe.json');c.xcaf=load(OUT/'artifacts/xcaf_audit.json')
 def test_source_mapping(self):self.assertTrue(all(Path(x['source_obj']).is_file() for x in self.inv['cases'].values()))
 def test_source_sha(self):self.assertTrue(all(hashlib.sha256(Path(x['source_obj']).read_bytes()).hexdigest()==x['source_sha256'] for x in self.inv['cases'].values()))
 def test_old_outputs_read_only(self):self.assertTrue(all(x['unchanged'] for x in load(OUT/'artifacts/old_outputs_read_only_audit.json').values()))
 def test_remaining_7_cases(self):self.assertEqual(set(self.new),set(TARGETS))
 def test_total_part_count(self):self.assertEqual(sum(x['CAD_PART_COUNT'] for x in self.new.values()),48)
 def test_all_parts_attempted(self):self.assertTrue(all(x['PARTS_ATTEMPTED']==x['CAD_PART_COUNT'] for x in self.new.values()))
 def test_no_ready_only_skip(self):self.assertTrue(all(x['PARTS_ATTEMPTED']==len(x['parts']) for x in self.new.values()))
 def test_all_parts_accepted(self):self.assertTrue(all(x['PARTS_ACCEPTED']==x['CAD_PART_COUNT'] for x in self.new.values()))
 def test_backend_cascade(self):
  expected={'PROGRAMMATIC_MAC','DETERMINISTIC_FEATURE','HYBRID_STRUCTURED_FREEFORM','GLOBAL_FREEFORM','SOURCE_AWARE_SURFACE_BREP_FALLBACK'}
  self.assertTrue(all({c['backend'] for c in p['candidates']}==expected for x in self.new.values() for p in x['parts']))
 def test_mac_403_handled(self):self.assertEqual(self.probe['MAC_HTTP_STATUS'],403)
 def test_mac_not_batch_blocker(self):self.assertTrue(all(x['PARTS_ACCEPTED'] for x in self.new.values()))
 def test_mac_skipped_all(self):self.assertEqual(sum(x['MAC_SKIPPED_PARTS'] for x in self.new.values()),48)
 def test_backend_vs_quality_separated(self):self.assertTrue(any(p['BACKEND_CLASS']=='GEOMETRY_COVERAGE_FALLBACK' and p['FINAL_Q']=='Q1' for x in self.new.values() for p in x['parts']))
 def test_residual_recovery(self):self.assertTrue(all(not x['residual_recovery']['residual_required'] for x in self.new.values()))
 def test_full_coverage(self):self.assertTrue(all(x['CAD_COVERAGE']>=.95 for x in self.new.values()))
 def test_part_level_compact_v1(self):self.assertTrue(all((OUT/'cases'/x['case_id']/'parts'/p['part_id']/'compact_v1/v1_result.json').is_file() for x in self.new.values() for p in x['parts']))
 def test_part_level_compact_v2(self):self.assertTrue(all((OUT/'cases'/x['case_id']/'parts'/p['part_id']/'compact_v2/v2_result.json').is_file() for x in self.new.values() for p in x['parts']))
 def test_no_whole_refit(self):self.assertTrue(all(not load(OUT/'cases'/x['case_id']/'parts'/p['part_id']/'compact_v2/v2_result.json')['whole_assembly_refit'] for x in self.new.values() for p in x['parts']))
 def test_feature_graph_every_part(self):self.assertTrue(all(Path(p['cad_feature_graph']).is_file() for x in self.inv['cases'].values() for p in x['parts']))
 def test_feature_graph_vocabulary(self):
  expected={'PLANE_REGION','CYLINDER_REGION','PROFILE','LOOP','EXTRUSION','REVOLUTION','LOFT','SWEEP','HOLE','SLOT','CUT','PATTERN','FREEFORM_REGION'}
  self.assertTrue(all(set(load(p['cad_feature_graph'])['feature_vocabulary'])==expected for x in self.inv['cases'].values() for p in x['parts']))
 def test_geometry_analyzer_every_part(self):self.assertTrue(all(Path(p['geometry_analysis']).is_file() for x in self.inv['cases'].values() for p in x['parts']))
 def test_mac_inputs_no_raw(self):self.assertTrue(all(not load(p['cad_feature_graph'])['raw_mesh_included'] and not load(p['measured_cad_spec'])['raw_mesh_included'] for x in self.inv['cases'].values() for p in x['parts']))
 def test_geometry_thresholds_frozen(self):
  for x in self.new.values():
   q=x['GEOM_Q'];c=x['CHAMFER'];p=x['P95'];v=x['COVERAGE02']
   if q=='Q1':self.assertTrue(c<=.01 and p<=.02 and v>=.95)
 def test_structural_audit(self):self.assertTrue(all(x['STRUCTURAL_CLASS'] in {'ANALYTIC_FEATURE_BREP','COMPACT_STRUCTURED_BREP','COMPACT_BUT_SPLINE_DERIVED','FRAGMENTED_SPLINE_BREP','SURFACE_BREP_FALLBACK','STRUCTURE_UNKNOWN'} for x in self.new.values()))
 def test_surface_fallback_not_structure_pass(self):self.assertTrue(all(x['CAD_STRUCTURE_Q']=='FAIL' for x in self.new.values() if x['STRUCTURAL_CLASS']=='SURFACE_BREP_FALLBACK'))
 def test_case03_no_regression(self):self.assertEqual(self.reg['cases']['CASE_03']['SELECTED_BEST_PATH'],str(ROOT/'batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step'))
 def test_case03_faces_six(self):
  rows={r['CASE_ID']:r for r in csv.DictReader((OUT/'metrics/batch10_latest_best_summary.csv').open())};self.assertEqual(int(rows['CASE_03']['FACE_COUNT']),6)
 def test_case09_existing_best_preserved(self):self.assertEqual(self.reg['cases']['CASE_09']['SELECTED_BEST_PATH'],str(ROOT/'case09_aircraft_end2end_cad_v1/07_assembly/CASE09_aircraft_final.step'))
 def test_case00_existing_topology_preserved(self):self.assertEqual(self.reg['cases']['CASE_00']['SELECTED_BEST'],'HISTORICAL_BEST')
 def test_xcaf(self):self.assertTrue(all(x['BRep_valid'] and x['XCAF_READ_SUCCESS'] for x in self.xcaf.values()))
 def test_xcaf_component_counts(self):self.assertTrue(all(self.xcaf[c]['ASSEMBLY_COMPONENT_COUNT']==self.new[c]['PARTS_ACCEPTED'] for c in TARGETS))
 def test_best_result_registry(self):self.assertEqual(len(self.reg['cases']),10)
 def test_best_result_no_regression(self):self.assertTrue(all(x['BEST_RESULT_NON_REGRESSION'] for x in self.reg['cases'].values()))
 def test_fixed_cases_not_recomputed(self):self.assertTrue(all(self.reg['cases'][c]['SELECTED_BEST']=='FROZEN_REFERENCE_RESULT' for c in ['CASE_01','CASE_06','CASE_07']))
 def test_batch10_contact_sheet(self):self.assertTrue((OUT/'artifacts/batch10_latest_best_cad_shaded.png').stat().st_size>10000)
 def test_true_edge_contact_sheet(self):self.assertTrue((OUT/'artifacts/batch10_latest_best_true_edges.png').stat().st_size>10000)
 def test_summary_csv_ten_rows(self):self.assertEqual(len(list(csv.DictReader((OUT/'metrics/batch10_latest_best_summary.csv').open()))),10)
 def test_no_step_as_reconstruction_input(self):self.assertTrue(all(Path(p['mesh']).suffix.lower()=='.obj' for x in self.inv['cases'].values() for p in x['parts']))
 def test_identity_no_icp_placement(self):
  for x in self.new.values():
   for p in x['parts']:
    d=load(OUT/'cases'/x['case_id']/'parts'/p['part_id']/'local_to_global_transform.json');self.assertTrue(np.allclose(d['LOCAL_TO_GLOBAL'],np.eye(4)));self.assertFalse(d['ICP_USED']);self.assertFalse(d['guessed_placement'])
if __name__=='__main__':unittest.main(verbosity=2)
