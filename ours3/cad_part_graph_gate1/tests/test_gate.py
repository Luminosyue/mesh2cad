#!/usr/bin/env python3
import csv, json, unittest
from pathlib import Path
import numpy as np
import trimesh

R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
S=R/'cad_part_graph_gate1'; A=S/'artifacts'; C=S/'cases'
summary=json.load(open(A/'cad_part_graph_gate1_summary.json'))
p3=json.load(open(A/'p3_segment_graph.json'))
assoc=json.load(open(A/'physx_p3_association.json'))
cad=json.load(open(A/'cad_part_graph_v1.json'))
assembly=json.load(open(A/'cad_assembly_graph_v1.json'))
manifest=json.load(open(A/'cad_part_mac_manifest_v1.json'))

class GateTests(unittest.TestCase):
 def test_01_source(self): self.assertEqual(summary['SOURCE_OBJECT'],'REAL_03')
 def test_02_raw_count(self): self.assertEqual(p3['node_count'],26)
 def test_03_sparse(self): self.assertLess(p3['edge_count'],p3['possible_undirected_pairs'])
 def test_04_edges_unique(self): self.assertEqual(len({tuple(sorted((e['segment_a'],e['segment_b']))) for e in p3['edges']}),len(p3['edges']))
 def test_05_adjacent(self): self.assertTrue(all(e['source_mesh_adjacent'] for e in p3['edges']))
 def test_06_score_formula(self):
  for e in p3['edges']:
   t=e['score_terms']; expected=.25*t['shared_boundary_score']+.25*t['surface_continuity_score']+.2*t['primitive_relation_score']+.15*t['normal_tangent_continuity']+.15*t['proximity_score']; self.assertAlmostEqual(expected,e['geometry_merge_score'],12)
 def test_07_final_formula(self):
  for e in p3['edges']: self.assertAlmostEqual(.9*e['geometry_merge_score']+.1*e['physx_same_part_score'],e['final_merge_score'],12)
 def test_08_thresholds(self):
  for e in p3['edges']:
   if e['decision']=='AUTO_MERGE': self.assertGreaterEqual(e['final_merge_score'],.8)
   elif e['decision']=='REVIEW_MERGE': self.assertTrue(.6<=e['final_merge_score']<.8)
   elif e['decision']=='KEEP_SEPARATE': self.assertLess(e['final_merge_score'],.6)
 def test_09_physx_reused(self): self.assertTrue(summary['PHYSX_DATA_REUSED'])
 def test_10_no_localization(self): self.assertFalse(assoc['physx_3d_part_localization_available'])
 def test_11_association_count(self): self.assertEqual(len(assoc['associations']),26)
 def test_12_soft_cap(self): self.assertLessEqual(assoc['semantic_soft_prior_max'],.15)
 def test_13_no_kinematic_invention(self): self.assertEqual(assoc['PHYSX_MUST_SEPARATE_PAIRS'],[])
 def test_14_scale_not_graph(self): self.assertFalse(assoc['physical_scale_used_for_part_graph'])
 def test_15_prior_not_executed(self): self.assertTrue(all(not e['GEOMETRY_MERGE_PRIOR']['executed_directly'] for e in p3['edges']))
 def test_16_constraint_grouping(self): self.assertTrue(cad['constraint_aware_grouping'] and not cad['naive_union_find_used'])
 def test_17_group_forbidden(self):
  forb={tuple(x) for x in cad['forbidden_pairs']}
  for n in cad['nodes']:
   g=n['source_p3_segment_ids']; self.assertFalse(any(tuple(sorted((a,b))) in forb for a in g for b in g if a<b))
 def test_18_triangle_coverage(self):
  arrays=[np.load(C/n['cad_part_id']/'source_triangle_ids.npy') for n in cad['nodes']]; allids=np.concatenate(arrays); self.assertEqual(len(allids),385828); self.assertEqual(len(np.unique(allids)),385828); self.assertEqual(allids.min(),0); self.assertEqual(allids.max(),385827)
 def test_19_candidate_count(self): self.assertGreater(len(cad['nodes']),0)
 def test_20_obj_exists(self): self.assertTrue(all(Path(n['global_obj']).is_file() and Path(n['local_obj']).is_file() for n in cad['nodes']))
 def test_21_obj_triangles(self):
  for n in cad['nodes']: self.assertEqual(len(trimesh.load(n['global_obj'],force='mesh',process=False).faces),n['triangle_count'])
 def test_22_transforms_roundtrip(self):
  for n in cad['nodes']:
   t=json.load(open(n['coordinate_transforms'])); self.assertTrue(np.allclose(np.array(t['global_to_local_4x4'])@np.array(t['local_to_global_4x4']),np.eye(4),atol=1e-10))
 def test_23_provenance(self): self.assertTrue(all((C/n['cad_part_id']/'provenance.json').is_file() for n in cad['nodes']))
 def test_24_analyzer_outputs(self): self.assertTrue(all((C/n['cad_part_id']/'geometry_analysis/mesh_stats.json').is_file() for n in cad['nodes']))
 def test_25_router_outputs(self): self.assertTrue(all((C/n['cad_part_id']/'cad_spec/cadability.json').is_file() for n in cad['nodes']))
 def test_26_no_recursive_p3(self): self.assertTrue(all(not n['recursive_p3_allowed'] for n in cad['nodes']))
 def test_27_d_flag(self): self.assertTrue(all(n['requires_further_decomposition']==(n['cadability_class'][0]=='D') for n in cad['nodes']))
 def test_28_ready_manifest(self): self.assertEqual({x['cad_part_id'] for x in manifest['parts']},{n['cad_part_id'] for n in cad['nodes'] if n['reconstruction_state']=='READY_FOR_CAD_RECONSTRUCTION'})
 def test_29_ready_positive(self): self.assertGreater(summary['READY_FOR_CAD_RECONSTRUCTION'],0)
 def test_30_assembly_metadata(self): self.assertTrue(assembly['metadata_only_no_step'] and not assembly['assembly_step_generated'])
 def test_31_no_invented_relations(self): self.assertEqual(assembly['relations'],[])
 def test_32_no_runs(self): self.assertEqual((summary['NEW_P3_RUNS'],summary['NEW_PHYSX_RUNS'],summary['NEW_MAC_RUNS'],summary['NEW_LLM_CAD_CALLS'],summary['NEW_STEP_FILES']),(0,0,0,0,0))
 def test_33_no_gt(self): self.assertFalse(summary['STEP_GT_USED'] or summary['ABC_DATA_USED'])
 def test_34_frame_audit(self): self.assertTrue(json.load(open(A/'coordinate_frame_audit.json'))['coordinate_frame_audit_pass'])
 def test_35_visuals(self): self.assertTrue(all((A/x).is_file() for x in ['raw_p3_vs_cad_parts.png','cad_part_merge_graph.png','cad_part_candidates_contact_sheet.png']))
 def test_36_review_csv_blank(self):
  rows=list(csv.DictReader(open(A/'cad_part_graph_human_review.csv'))); self.assertEqual(len(rows),len(cad['nodes'])); self.assertTrue(all(not r['HUMAN_MERGE_OK'] and not r['HUMAN_SEMANTIC_OK'] and not r['HUMAN_CADABILITY_OK'] for r in rows))
 def test_37_function_zero(self): self.assertEqual(summary['PHYSX_FUNCTION_ZERO_REASON'],'A_ABSENT_FROM_RAW_OUTPUT')
 def test_38_blockers(self): self.assertEqual(summary['BLOCKERS'],[])

if __name__=='__main__': unittest.main(verbosity=2)
