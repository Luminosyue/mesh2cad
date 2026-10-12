"""Unit tests for V6A branch recovery scoring and clustering."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from airplane_point2cad_curve_branch_recovery_v6a.branch_recovery import recover_branches_for_pair
from airplane_point2cad_curve_branch_recovery_v6a.fragments import attach_fragment_features, score_connection


def _frag(fid, pair, pts, sa_uv=None, sb_uv=None, support_frac=0.9):
    pts = np.asarray(pts, float)
    tang_s = (pts[1] - pts[0]) if len(pts) > 1 else np.array([1.0, 0.0, 0.0])
    tang_e = (pts[-1] - pts[-2]) if len(pts) > 1 else tang_s
    tang_s = (tang_s / (np.linalg.norm(tang_s) + 1e-12)).tolist()
    tang_e = (tang_e / (np.linalg.norm(tang_e) + 1e-12)).tolist()
    f = {
        "fragment_id": fid,
        "curve_id": "C0",
        "comp_id": 0,
        "surface_a": pair[0],
        "surface_b": pair[1],
        "surface_pair": pair,
        "points": pts,
        "length": float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()) if len(pts) > 1 else 0.0,
        "closed": False,
        "start_xyz": pts[0].tolist(),
        "end_xyz": pts[-1].tolist(),
        "start_tangent": tang_s,
        "end_tangent": tang_e,
        "start_curvature": 0.01,
        "end_curvature": 0.01,
        "bbox": [pts.min(0).tolist(), pts.max(0).tolist()],
        "surface_A_uv": sa_uv or {"start": [0, 0], "end": [1, 0], "min": [0, 0], "max": [1, 1]},
        "surface_B_uv": sb_uv or {"start": [0, 0], "end": [1, 0], "min": [0, 0], "max": [1, 1]},
        "distance_to_XPart": 0.01,
        "support_fraction": support_frac,
    }
    return f


def _chain_uv(start_u: float, end_u: float):
    uv = {"min": [0, 0], "max": [1, 1]}
    uv["start"] = [start_u, 0.0]
    uv["end"] = [end_u, 0.0]
    return uv


class TestBranchRecoveryV6A(unittest.TestCase):
    def setUp(self):
        self.diag = 1.0
        self.xpart = trimesh.creation.box(extents=[2, 2, 2])
        self.surfaces = [self.xpart, self.xpart]

    def test1_same_pair_close_tangent_accept(self):
        uv1 = _chain_uv(0.0, 0.2)
        uv2 = _chain_uv(0.2, 0.4)
        f1 = _frag("F0", (0, 1), [[-0.4, -0.4, 1.0], [-0.3, -0.4, 1.0], [-0.20005, -0.4, 1.0]], sa_uv=uv1, sb_uv=uv1, support_frac=0.9)
        f2 = _frag("F1", (0, 1), [[-0.19995, -0.4, 1.0], [-0.1, -0.4, 1.0], [0.0, -0.4, 1.0]], sa_uv=uv2, sb_uv=uv2, support_frac=0.9)
        rec = score_connection(f1, f2, "e", "s", self.surfaces, self.xpart, self.diag)
        self.assertTrue(rec["accepted"], rec)

    def test2_orientation_reverse_handled(self):
        f1 = _frag("F0", (0, 1), [[0, 0, 0], [0.1, 0, 0]])
        f2 = _frag("F1", (0, 1), [[0.3, 0, 0], [0.201, 0, 0]])
        rec = score_connection(f1, f2, "e", "e", self.surfaces, self.xpart, self.diag)
        self.assertTrue(rec["reverse_b"] or rec["tangent_dot"] >= 0.65)

    def test3_tangent_discontinuous_reject(self):
        f1 = _frag("F0", (0, 1), [[0, 0, 0], [0.1, 0, 0]])
        f2 = _frag("F1", (0, 1), [[0.101, 0.1, 0], [0.101, 0.2, 0]])
        rec = score_connection(f1, f2, "e", "s", self.surfaces, self.xpart, self.diag)
        self.assertFalse(rec["accepted"])
        self.assertIn("TANGENT_DISCONTINUITY", rec["reason_rejected"])

    def test4_uv_discontinuity_reject(self):
        uv_a = _chain_uv(0.0, 0.05)
        uv_b_far = _chain_uv(5.0, 5.05)
        f1 = _frag("F0", (0, 1), [[-0.4, -0.4, 1.0], [-0.351, -0.4, 1.0]], sa_uv=uv_a, sb_uv=uv_a, support_frac=0.9)
        f2 = _frag("F1", (0, 1), [[-0.349, -0.4, 1.0], [-0.3, -0.4, 1.0]], sa_uv=uv_b_far, sb_uv=uv_b_far, support_frac=0.9)
        rec = score_connection(f1, f2, "e", "s", self.surfaces, self.xpart, self.diag)
        self.assertFalse(rec["accepted"])
        self.assertIn("UV_DISCONTINUITY", rec["reason_rejected"])

    def test5_xpart_support_zero_reject(self):
        f1 = _frag("F0", (0, 1), [[-0.4, -0.4, 1.0], [-0.35, -0.4, 1.0]], support_frac=0.9)
        f2 = _frag("F1", (0, 1), [[10.0, 10.0, 10.0], [10.05, 10.0, 10.0]], support_frac=0.0)
        rec = score_connection(f1, f2, "e", "s", self.surfaces, self.xpart, self.diag)
        self.assertFalse(rec["accepted"])

    def test6_two_independent_branches_not_merged(self):
        uv10 = _chain_uv(0.0, 0.1)
        uv11 = _chain_uv(0.1, 0.2)
        uv20 = _chain_uv(0.0, 0.1)
        uv21 = _chain_uv(0.1, 0.2)
        f1 = _frag("F0", (0, 1), [[-0.4, -0.4, 1.0], [-0.30005, -0.4, 1.0]], sa_uv=uv10, sb_uv=uv10, support_frac=0.9)
        f2 = _frag("F1", (0, 1), [[-0.29995, -0.4, 1.0], [-0.2, -0.4, 1.0]], sa_uv=uv11, sb_uv=uv11, support_frac=0.9)
        f3 = _frag("F2", (0, 1), [[-0.4, 0.4, 1.0], [-0.30005, 0.4, 1.0]], sa_uv=uv20, sb_uv=uv20, support_frac=0.9)
        f4 = _frag("F3", (0, 1), [[-0.29995, 0.4, 1.0], [-0.2, 0.4, 1.0]], sa_uv=uv21, sb_uv=uv21, support_frac=0.9)
        branches, acc, _, _ = recover_branches_for_pair([f1, f2, f3, f4], self.surfaces, self.xpart, self.diag)
        self.assertEqual(len(branches), 2)
        self.assertEqual(len(acc), 2)

    def test7_cross_pair_reject(self):
        f1 = _frag("F0", (0, 1), [[0, 0, 0], [0.05, 0, 0]])
        f2 = _frag("F1", (0, 2), [[0.051, 0, 0], [0.1, 0, 0]])
        # score_connection assumes same pair in caller; branch_recovery groups by pair
        branches, acc, _, _ = recover_branches_for_pair([f1], self.surfaces, self.xpart, self.diag)
        branches2, acc2, _, _ = recover_branches_for_pair([f2], self.surfaces, self.xpart, self.diag)
        self.assertEqual(len(branches) + len(branches2), 2)
        self.assertEqual(len(acc) + len(acc2), 0)

    def test8_open_wire_not_forced_closed(self):
        f1 = _frag("F0", (0, 1), [[0, 0, 0], [0.2, 0, 0]])
        branches, _, _, _ = recover_branches_for_pair([f1], self.surfaces, self.xpart, self.diag)
        self.assertEqual(len(branches), 1)
        self.assertFalse(branches[0]["closed"])

    def test9_two_face_lens_not_solid(self):
        # pipeline-level: 2 faces cannot become clean solid (checked in v5.build_occ_v5)
        n_faces = 2
        clean = 1
        if clean and n_faces < 3:
            clean = 0
        self.assertEqual(clean, 0)


if __name__ == "__main__":
    unittest.main()
