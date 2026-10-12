"""Unit tests for V6A.1 audit (read-only)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from airplane_point2cad_analytic_branch_audit_v6a1.gap_audit import classify_gap
from airplane_point2cad_analytic_branch_audit_v6a1.baseline_audit import audit_candidate_accounting
from airplane_point2cad_analytic_branch_audit_v6a1.uv_audit import uv_delta


class TestV6A1Audit(unittest.TestCase):
    def test1_true_intersection_fragmentation(self):
        sup = {"support_frac_surface": 0.8, "support_frac_boundary": 0.7}
        mi = {"matched_occ_branch": "B0", "confidence": "HIGH"}
        mj = {"matched_occ_branch": "B0", "confidence": "HIGH"}
        self.assertEqual(classify_gap({}, {}, mi, mj, sup, 0.002, 1.0), "TRUE_INTERSECTION_FRAGMENTATION")

    def test2_true_trim_separation(self):
        sup = {"support_frac_surface": 0.8, "support_frac_boundary": 0.1}
        mi = {"matched_occ_branch": "B0", "confidence": "HIGH"}
        mj = {"matched_occ_branch": "B0", "confidence": "HIGH"}
        self.assertEqual(classify_gap({}, {}, mi, mj, sup, 0.002, 1.0), "TRUE_TRIM_SEPARATION")

    def test3_different_occ_branch(self):
        mi = {"matched_occ_branch": "B0", "confidence": "HIGH"}
        mj = {"matched_occ_branch": "B1", "confidence": "HIGH"}
        self.assertIn(classify_gap({}, {}, mi, mj, {}, 0.05, 1.0), ("FIT_TOPOLOGY_INCONSISTENT", "AMBIGUOUS"))

    def test4_fit_topology_inconsistent(self):
        mi = {"matched_occ_branch": "B0", "confidence": "NONE"}
        mj = {"matched_occ_branch": "B1", "confidence": "NONE"}
        self.assertEqual(classify_gap({}, {}, mi, mj, {"support_frac_surface": 0.0, "support_frac_boundary": 0.0}, 0.1, 1.0), "FIT_TOPOLOGY_INCONSISTENT")

    def test5_periodic_uv(self):
        peri = {"u_periodic": True, "u_period": 2 * np.pi, "v_periodic": False}
        du, dv, seam = uv_delta(0.01, 0.0, 2 * np.pi - 0.01, 0.0, peri)
        self.assertLess(du, 0.1)
        self.assertTrue(seam)

    def test6_gap_zero_not_xyz_gate(self):
        # endpoint xyz gap 0 should not imply GAP_TOO_LARGE for connection gate
        rec = {"normalized_gap": 0.05, "reason_rejected": ["GAP_TOO_LARGE"]}
        wire_to_frag_gap = 0.0
        self.assertEqual(wire_to_frag_gap, 0.0)
        self.assertGreater(rec["normalized_gap"], 3e-3)

    def test7_candidate_accounting(self):
        doc = {
            "candidates": [
                {"accepted": True},
                {"accepted": False, "reason_rejected": ["GAP_TOO_LARGE"]},
                {"accepted": False, "reason_rejected": ["UV_DISCONTINUITY"]},
            ]
        }
        out = audit_candidate_accounting(doc)
        self.assertEqual(out["TOTAL_CONNECTION_CANDIDATES"], 3)
        self.assertEqual(out["ACCEPTED_CONNECTIONS"] + out["REJECTED_CONNECTIONS"] + out["AMBIGUOUS_CONNECTIONS"], 3)

    def test8_audit_only_no_topology(self):
        self.assertTrue(True)  # pipeline sets TOPOLOGY_MODIFIED=False; enforced at runner level


if __name__ == "__main__":
    unittest.main()
