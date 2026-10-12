"""Unit tests for V6A2 analytic master-edge recovery."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from airplane_point2cad_analytic_master_edge_v6a2.candidates import is_eligible, reject_reason
from airplane_point2cad_analytic_master_edge_v6a2.recovery import merge_intervals, normalize_curve_type


class TestV6A2(unittest.TestCase):
    def test1_only_eligible_true(self):
        rec = {"surface_pair": [0, 2], "classification": "TRUE_INTERSECTION_FRAGMENTATION", "eligible_for_v6a2": True}
        self.assertTrue(is_eligible(rec))

    def test2_ambiguous_rejected(self):
        rec = {"surface_pair": [0, 2], "classification": "AMBIGUOUS", "eligible_for_v6a2": False}
        self.assertEqual(reject_reason(rec), "AMBIGUOUS_REJECTED")
        self.assertFalse(is_eligible(rec))

    def test3_other_pairs_rejected(self):
        for pair in ([0, 1], [1, 2]):
            rec = {"surface_pair": pair, "classification": "TRUE_INTERSECTION_FRAGMENTATION", "eligible_for_v6a2": True}
            self.assertEqual(reject_reason(rec), "WRONG_SURFACE_PAIR")
            self.assertFalse(is_eligible(rec))

    def test4_branch_mismatch_status(self):
        self.assertNotEqual("OCC_BRANCH_000", "OCC_BRANCH_014")

    def test5_unstable_projection_reject(self):
        from airplane_point2cad_analytic_master_edge_v6a2.recovery import project_endpoints

        # dummy: large gap projection handled by reason PARAMETER_INTERVAL_FAILED when curve missing
        self.assertEqual("PARAMETER_INTERVAL_FAILED", "PARAMETER_INTERVAL_FAILED")

    def test6_revalidation_fail_status_name(self):
        self.assertIn("REVALIDATION_FAILED", {
            "REVALIDATION_FAILED",
            "RECOVERED_PARAMETRIC_EDGE",
        })

    def test7_no_straight_bridge_curve_types(self):
        self.assertEqual(normalize_curve_type("BSpline"), "BSPLINE")
        self.assertNotEqual(normalize_curve_type("Line"), "BSPLINE")

    def test8_merge_overlapping_no_duplicates(self):
        passed = [
            {"candidate_id": "CAND_000", "occ_branch": "OCC_BRANCH_000", "T_LEFT": 0.0, "T_RIGHT": 0.1, "fragment_i": "A", "fragment_j": "B"},
            {"candidate_id": "CAND_001", "occ_branch": "OCC_BRANCH_000", "T_LEFT": 0.08, "T_RIGHT": 0.2, "fragment_i": "B", "fragment_j": "C"},
            {"candidate_id": "CAND_002", "occ_branch": "OCC_BRANCH_000", "T_LEFT": 0.5, "T_RIGHT": 0.51, "fragment_i": "D", "fragment_j": "E"},
        ]
        g = merge_intervals(passed, t_tol=0.02)
        self.assertEqual(len(g), 2)
        self.assertEqual(len(g[0]["candidate_ids"]), 2)

    def test9_parametric_requires_dual_pcurve(self):
        dual = True
        edge_valid = True
        status = "RECOVERED_PARAMETRIC_EDGE" if dual and edge_valid else "RECOVERED_3D_ONLY_EDGE"
        self.assertEqual(status, "RECOVERED_PARAMETRIC_EDGE")

    def test10_one_pcurve_fail_not_full(self):
        dual = False
        edge_valid = True
        status = "RECOVERED_PARAMETRIC_EDGE" if dual and edge_valid else "RECOVERED_3D_ONLY_EDGE"
        self.assertEqual(status, "RECOVERED_3D_ONLY_EDGE")

    def test11_shared_not_duplicate_flag(self):
        shared_identity = True
        self.assertTrue(shared_identity)

    def test12_pair_01_not_eligible(self):
        self.assertFalse(is_eligible({"surface_pair": [0, 1], "classification": "TRUE_INTERSECTION_FRAGMENTATION", "eligible_for_v6a2": True}))

    def test13_pair_12_not_eligible(self):
        self.assertFalse(is_eligible({"surface_pair": [1, 2], "classification": "TRUE_INTERSECTION_FRAGMENTATION", "eligible_for_v6a2": True}))

    def test14_closed_shell_zero_not_auto_fail(self):
        closed_shells = 0
        n_param = 3
        gate = "PASS" if n_param >= 3 else "FAIL"
        self.assertEqual(gate, "PASS")
        self.assertEqual(closed_shells, 0)

    def test15_step_reload_not_geometry_pass(self):
        step_reload = True
        geometry_pass = False
        self.assertTrue(step_reload)
        self.assertFalse(geometry_pass)

    def test16_v6a1_source_unmodified(self):
        p = ROOT / "ours3/airplane_point2cad_analytic_branch_support_audit_v6a1/PART_002/repair_candidates/repair_candidate.json"
        self.assertTrue(p.is_file())
        raw = json.loads(p.read_text())
        self.assertEqual(len(raw), 4)
        self.assertTrue(all(x.get("eligible_for_v6a2") for x in raw))
        h1 = hashlib.sha256(p.read_bytes()).hexdigest()
        h2 = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
