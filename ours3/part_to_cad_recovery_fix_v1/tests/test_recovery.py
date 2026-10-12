import json
import unittest
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/part_to_cad_recovery_fix_v1")


def load(path): return json.loads(Path(path).read_text())


class RecoveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c1 = load(ROOT / "case01/case_result.json")
        cls.c6 = load(ROOT / "case06/case_result.json")
        cls.c7 = load(ROOT / "case07/case_result.json")
        cls.parts = cls.c6["parts"] + cls.c7["parts"]
        cls.mac = load(ROOT / "case07/parts/CADPART_001/candidates/route_a_mac/mac_run_result.json")

    def test_case01_q1(self): self.assertEqual(self.c1["SELECTED_Q"], "Q1")
    def test_case01_feature_priority(self): self.assertEqual(self.c1["SELECTED_CANDIDATE"], "candidate_B_loft")
    def test_case01_final_exists(self): self.assertTrue(Path(self.c1["FINAL_STEP"]).is_file())
    def test_case01_selection_bug_fixed(self): self.assertTrue(self.c1["SELECTION_BUG_FIXED"])
    def test_case01_resource_failure_handled(self): self.assertTrue(self.c1["RESOURCE_FAILURE_HANDLED"])
    def test_case06_attempted(self): self.assertEqual(self.c6["parts_attempted"], 2)
    def test_case06_accepted(self): self.assertEqual(self.c6["parts_accepted"], 2)
    def test_case06_strong_coverage(self): self.assertGreaterEqual(self.c6["final_cad_coverage"], .85)
    def test_case07_attempted(self): self.assertEqual(self.c7["parts_attempted"], 33)
    def test_case07_accepted(self): self.assertEqual(self.c7["parts_accepted"], 33)
    def test_case07_strong_coverage(self): self.assertGreaterEqual(self.c7["final_cad_coverage"], .95)
    def test_all_geometry_accepted(self):
        self.assertTrue(all(p["selected_qa"]["GEOMETRY_Q"] in ("Q1", "Q2", "S1") for p in self.parts))
    def test_all_brep_valid(self): self.assertTrue(all(p["selected_qa"]["BRep_valid"] for p in self.parts))
    def test_all_fresh_reload(self): self.assertTrue(all(p["selected_qa"]["fresh_reload"] for p in self.parts))
    def test_every_part_has_five_routes(self): self.assertTrue(all(len(p["candidates"]) == 5 for p in self.parts))
    def test_route_names_complete(self):
        expected={"PROGRAMMATIC_STRUCTURED","DETERMINISTIC_FEATURE","HYBRID_STRUCTURED_FREEFORM","GLOBAL_FREEFORM_BREP","S1_SURFACE_BREP_FALLBACK"}
        self.assertTrue(all({c["backend"] for c in p["candidates"]} == expected for p in self.parts))
    def test_every_candidate_bookkept(self):
        self.assertTrue(all((ROOT / p["case_id"].lower().replace("_","") / "parts" / p["part_id"] / "candidate_manifest.json").is_file() for p in self.parts))
    def test_all_part_compact_v1(self):
        self.assertTrue(all((ROOT / p["case_id"].lower().replace("_","") / "parts" / p["part_id"] / "compact_v1/v1_result.json").is_file() for p in self.parts))
    def test_all_part_compact_v2(self):
        self.assertTrue(all((ROOT / p["case_id"].lower().replace("_","") / "parts" / p["part_id"] / "compact_v2/v2_result.json").is_file() for p in self.parts))
    def test_no_whole_assembly_refit(self):
        self.assertTrue(all(not load(ROOT / p["case_id"].lower().replace("_","") / "parts" / p["part_id"] / "compact_v2/v2_result.json")["whole_assembly_refit"] for p in self.parts))
    def test_exact_identity_placement(self):
        for p in self.parts:
            d=load(ROOT / p["case_id"].lower().replace("_","") / "parts" / p["part_id"] / "local_to_global_transform.json")
            self.assertTrue(np.allclose(d["LOCAL_TO_GLOBAL"], np.eye(4))); self.assertFalse(d["guessed_placement"])
    def test_strict_mac_feature_input(self):
        d=load(ROOT / "case07/parts/CADPART_001/input/cad_feature_graph.json"); self.assertFalse(d["raw_mesh_included"])
    def test_strict_mac_measured_input(self):
        d=load(ROOT / "case07/parts/CADPART_001/input/measured_cad_spec.json"); self.assertFalse(d["raw_mesh_included"])
    def test_mac_quota_failure_recorded(self):
        log=" ".join(self.mac["final_state"].get("execution_log",[])); self.assertIn("Free quota exhausted",log)
    def test_mac_did_not_fabricate_step(self): self.assertFalse(self.mac["step_exists"])
    def test_no_icp(self):
        self.assertTrue(all(not load(ROOT / p["case_id"].lower().replace("_","") / "parts" / p["part_id"] / "local_to_global_transform.json")["ICP_USED"] for p in self.parts))
    def test_case06_assembly_exists(self): self.assertTrue(Path(self.c6["final_step"]).is_file())
    def test_case07_assembly_exists(self): self.assertTrue(Path(self.c7["final_step"]).is_file())
    def test_area_conservation_case06(self): self.assertAlmostEqual(sum(p["source_area_ratio"] for p in self.c6["parts"]),1.0,places=12)
    def test_area_conservation_case07(self): self.assertAlmostEqual(sum(p["source_area_ratio"] for p in self.c7["parts"]),1.0,places=12)


if __name__ == "__main__": unittest.main(verbosity=2)
