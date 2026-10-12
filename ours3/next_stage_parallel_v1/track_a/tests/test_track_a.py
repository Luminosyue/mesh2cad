#!/usr/bin/env python3
import csv
import json
import unittest
from pathlib import Path

import numpy as np


OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
TRACK = OURS3 / "next_stage_parallel_v1" / "track_a"
ART = TRACK / "artifacts"
SUMMARY = json.loads((ART / "track_a_summary.json").read_text())
with (ART / "p3_gate1_part_inventory.csv").open(newline="") as f:
    INVENTORY = list(csv.DictReader(f))
with (ART / "p3_gate1_merge_hypotheses.csv").open(newline="") as f:
    PAIRS = list(csv.DictReader(f))
PILOTS = json.loads((ART / "p3_gate1_mac_pilot_candidates.json").read_text())


class TrackATest(unittest.TestCase):
    def test_a0_unique_d_case_auto_selected(self):
        with (OURS3 / "mac_pipeline" / "artifacts" / "mac_gate1_10case_summary.csv").open(newline="") as f:
            expected = [r["CASE"] for r in csv.DictReader(f) if r["CADABILITY_CLASS"] == "D_MULTI_PART_REQUIRES_SEGMENTATION"]
        self.assertEqual(expected, [SUMMARY["D_CASE_ID"]])
    def test_a1_existing_p3_output_reused(self): self.assertTrue(SUMMARY["P3_REUSED_EXISTING_OUTPUT"])
    def test_p3_not_rerun(self): self.assertFalse(SUMMARY["P3_INFERENCE_RERUN"])
    def test_exactly_26_part_objs(self):
        seg = OURS3 / "fusion_pipeline" / "cases" / SUMMARY["D_CASE_ID"] / "segmentation"
        self.assertEqual(len(list(seg.glob("part_[0-9][0-9][0-9].obj"))), 26)
    def test_p3_triangle_mapping(self): self.assertTrue(SUMMARY["TRIANGLE_MAPPING_VALID"])
    def test_mapping_length(self):
        seg = OURS3 / "fusion_pipeline" / "cases" / SUMMARY["D_CASE_ID"] / "segmentation"
        meta = json.loads((seg / "part_metadata.json").read_text())
        self.assertEqual(len(np.load(seg / "triangle_part_id.npy")), meta["source_triangle_count"])
    def test_mapping_ids_valid(self):
        seg = OURS3 / "fusion_pipeline" / "cases" / SUMMARY["D_CASE_ID"] / "segmentation"
        x = np.load(seg / "triangle_part_id.npy")
        self.assertTrue(np.all((x >= 0) & (x < 26)))
    def test_mapping_all_ids_present(self):
        seg = OURS3 / "fusion_pipeline" / "cases" / SUMMARY["D_CASE_ID"] / "segmentation"
        self.assertEqual(set(np.unique(np.load(seg / "triangle_part_id.npy"))), set(range(26)))
    def test_unassigned_triangles_zero(self): self.assertEqual(SUMMARY["UNASSIGNED_TRIANGLES"], 0)
    def test_multi_assigned_triangles_zero(self): self.assertEqual(SUMMARY["MULTI_ASSIGNED_TRIANGLES"], 0)
    def test_all_26_parts_audited(self): self.assertEqual(len(INVENTORY), 26)
    def test_inventory_ids_unique(self): self.assertEqual({int(r["PART_ID"]) for r in INVENTORY}, set(range(26)))
    def test_area_ratio_partition(self): self.assertAlmostEqual(sum(float(r["area_ratio"]) for r in INVENTORY), 1.0, places=8)
    def test_geometry_fields_present(self):
        for r in INVENTORY:
            for k in ("vertices", "triangles", "surface_area", "bbox_min", "bbox_diagonal", "centroid", "connected_components", "watertight", "boundary_edge_count", "geometry_group_count"):
                self.assertIn(k, r)
    def test_tiny_flags_fixed(self):
        for r in INVENTORY:
            a = float(r["area_ratio"])
            self.assertEqual(r["TINY_0001"] == "True", a < .001)
            self.assertEqual(r["TINY_0002"] == "True", a < .002)
            self.assertEqual(r["TINY_0005"] == "True", a < .005)
    def test_fragment_reasons_structured(self):
        for r in INVENTORY: self.assertIsInstance(json.loads(r["FRAGMENT_REASONS"]), list)
    def test_part_cadability_available(self): self.assertEqual(SUMMARY["PART_CADABILITY_AVAILABLE"], 26)
    def test_cadability_fields_present(self):
        for r in INVENTORY:
            for k in ("CADABILITY_CLASS", "CADABILITY_SCORE", "ANALYTIC_COVERAGE", "PLANE_COVERAGE", "CYLINDER_COVERAGE", "SPHERE_COVERAGE", "CONE_COVERAGE", "OTHER_COVERAGE", "EXTRUSION_LIKELIHOOD", "REVOLUTION_LIKELIHOOD", "HOLE_CANDIDATES", "PATTERN_CANDIDATES"):
                self.assertIn(k, r)
    def test_segment_status_enum(self):
        valid = {"GOOD_CAD_PART_CANDIDATE", "OVERSEGMENTATION_SUSPECT", "UNDERSEGMENTATION_SUSPECT", "TINY_FRAGMENT", "FREEFORM_PART", "UNCERTAIN_PART"}
        self.assertTrue(all(r["PART_SEGMENT_STATUS"] in valid for r in INVENTORY))
    def test_segment_status_assigned(self): self.assertEqual(SUMMARY["SEGMENT_STATUS_ASSIGNED"], 26)
    def test_merge_score_range(self): self.assertTrue(all(0 <= float(p["MERGE_SCORE"]) <= 1 for p in PAIRS))
    def test_merge_score_fixed_formula(self):
        for p in PAIRS:
            expected = .30*float(p["shared_boundary_score"]) + .25*float(p["surface_continuity_score"]) + .20*float(p["primitive_compatibility"]) + .15*float(p["normal_continuity"]) + .10*float(p["geometric_proximity"])
            self.assertAlmostEqual(float(p["MERGE_SCORE"]), expected, places=10)
    def test_merge_hypothesis_thresholds(self):
        for p in PAIRS:
            s = float(p["MERGE_SCORE"]); h = p["MERGE_HYPOTHESIS"]
            self.assertEqual(h, "STRONG_MERGE_HYPOTHESIS" if s >= .75 else "WEAK_MERGE_HYPOTHESIS" if s >= .55 else "KEEP_SEPARATE")
    def test_only_adjacent_pairs_scored(self): self.assertTrue(all(float(p["shared_boundary_length"]) > 0 for p in PAIRS))
    def test_no_actual_merge(self): self.assertEqual(SUMMARY["ACTUAL_MERGES"], 0)
    def test_undersegmentation_detection(self):
        d = [r for r in INVENTORY if r["CADABILITY_CLASS"] == "D_MULTI_PART_REQUIRES_SEGMENTATION"]
        self.assertTrue(d and all(r["UNDERSEGMENTATION_SUSPECTED"] == "True" for r in d))
    def test_p3_pilot_selection_max_5(self): self.assertLessEqual(len(PILOTS["candidates"]), 5)
    def test_p3_pilot_selection_nonempty(self): self.assertGreaterEqual(len(PILOTS["candidates"]), 1)
    def test_pilot_a_and_b_caps(self):
        c = PILOTS["candidates"]
        self.assertLessEqual(sum(x["CADABILITY_CLASS"].startswith("A_") for x in c), 1)
        self.assertLessEqual(sum(x["CADABILITY_CLASS"].startswith("B_") for x in c), 4)
    def test_pilot_candidates_good_only(self): self.assertTrue(all(x["PART_SEGMENT_STATUS"] == "GOOD_CAD_PART_CANDIDATE" for x in PILOTS["candidates"]))
    def test_no_mac_runs(self): self.assertEqual(SUMMARY["MULTI_AGENT_CAD_RUNS"], 0)
    def test_no_step_gt(self): self.assertFalse(SUMMARY["STEP_GT_USED"])
    def test_no_abc_gt(self): self.assertFalse(SUMMARY["ABC_DATA_USED"])
    def test_human_review_26_rows(self):
        with (ART / "p3_gate1_human_review.csv").open(newline="") as f: rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 26)
    def test_human_review_fields_blank(self):
        with (ART / "p3_gate1_human_review.csv").open(newline="") as f: rows = list(csv.DictReader(f))
        self.assertTrue(all(not r["HUMAN_IS_REAL_CAD_PART"] and not r["HUMAN_MERGE_WITH"] and not r["HUMAN_KEEP_FOR_CAD"] and not r["NOTES"] for r in rows))
    def test_contact_sheet_exists(self): self.assertGreater((ART / "p3_gate1_segmentation_contact_sheet.png").stat().st_size, 10000)
    def test_merge_visual_exists(self): self.assertGreater((ART / "p3_gate1_merge_hypotheses.png").stat().st_size, 10000)


if __name__ == "__main__": unittest.main(verbosity=2)
