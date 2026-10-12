import json
import unittest
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/next_stage_parallel_v1/track_b")
ART = ROOT / "artifacts"


def load(name):
    return json.loads((ART / name).read_text())


class TrackBEvidenceTests(unittest.TestCase):
    def test_repo_commit_recorded(self):
        self.assertEqual(len(load("physx_repo_audit.json")["commit"]), 40)

    def test_repo_clean(self):
        self.assertFalse(load("physx_repo_audit.json")["dirty"])

    def test_required_official_files_present(self):
        self.assertTrue(all(x["exists"] for x in load("physx_repo_audit.json")["required_files"].values()))

    def test_requirement_has_official_physx_repo(self):
        ids = [x["repo_id"] for x in load("physx_checkpoint_requirement.json")["checkpoints"]]
        self.assertIn("PhysX-Omni/PhysX-Omni", ids)

    def test_requirement_has_trellis_repo(self):
        ids = [x["repo_id"] for x in load("physx_checkpoint_requirement.json")["checkpoints"]]
        self.assertIn("microsoft/TRELLIS-image-large", ids)

    def test_raw_obj_direct_input_false(self):
        self.assertFalse(load("physx_checkpoint_requirement.json")["raw_obj_direct_input_supported"])

    def test_unrelated_checkpoints_rejected(self):
        self.assertTrue(all(not x["accepted"] for x in load("physx_checkpoint_search.json")["unrelated_examples_rejected"]))

    def test_no_valid_checkpoint_found(self):
        self.assertFalse(load("physx_checkpoint_search.json")["valid_physx_checkpoint_found"])

    def test_official_download_attempt_recorded(self):
        self.assertTrue(load("physx_network_audit.json")["official_download_attempted"])

    def test_download_blocker_is_network(self):
        n = load("physx_network_audit.json")
        self.assertEqual(n["error_class"], "NetworkUnavailable")
        self.assertIn(n["direct_https_probe_return_code"], (7, 28))
        self.assertTrue(n["physx_checkpoint_download_blocked"])

    def test_no_unconfigured_mirror_used(self):
        self.assertFalse(load("physx_network_audit.json")["mirror_used"])

    def test_smoke_case_selected_from_gate1_a(self):
        s = load("physx_smoke_gate.json")
        self.assertEqual(s["case"], "REAL_05")
        self.assertEqual(s["selection_class"], "A_PROGRAM_CAD_FRIENDLY")

    def test_smoke_input_has_sha(self):
        self.assertEqual(len(load("physx_smoke_gate.json")["render_sha256"]), 64)

    def test_smoke_not_attempted_without_checkpoint(self):
        s = load("physx_smoke_gate.json")
        self.assertFalse(s["checkpoint_gate_passed"])
        self.assertFalse(s["attempted"])

    def test_batch_not_attempted_before_smoke(self):
        b = load("physx_batch_gate.json")
        self.assertFalse(b["run_permitted"])
        self.assertEqual(b["cases_attempted"], 0)

    def test_checkpoint_load_not_faked(self):
        i = load("physx_checkpoint_integrity.json")
        self.assertFalse(i["load_attempted"])
        self.assertFalse(i["load_success"])

    def test_track_status_blocked_not_fail(self):
        self.assertEqual(load("track_b_summary.json")["PHYSX_GATE_0_RECOVERY"], "BLOCKED")

    def test_no_mac_p3_fusion(self):
        s = load("track_b_summary.json")
        self.assertEqual(s["MAC_RUNS"], 0)
        self.assertFalse(s["P3_TOUCHED"])
        self.assertEqual(s["FUSION_RUNS"], 0)

    # Required names from NEXT_STAGE_PARALLEL_V1.
    def test_physx_checkpoint_not_faked(self):
        s = load("track_b_summary.json")
        self.assertFalse(s["PHYSX_CHECKPOINT_READY"])
        self.assertIsNone(s["PHYSX_CHECKPOINT_PATH"])

    def test_physx_smoke_before_batch(self):
        smoke = load("physx_smoke_gate.json")
        batch = load("physx_batch_gate.json")
        self.assertFalse(smoke["success"])
        self.assertEqual(batch["cases_attempted"], 0)

    def test_physx_raw_output_preserved(self):
        s = load("track_b_summary.json")
        # No inference ran, so zero raw outputs is the only truthful value.
        self.assertEqual(s["PHYSX_RAW_OUTPUTS"], 0)
        self.assertIsNone(load("physx_smoke_gate.json")["raw_output"])

    def test_no_physx_mac_fusion_yet(self):
        s = load("track_b_summary.json")
        self.assertFalse(s["PHYSX_USED_IN_MAC_BASELINE"])
        self.assertEqual(s["MAC_RUNS"], 0)
        self.assertEqual(s["FUSION_RUNS"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
