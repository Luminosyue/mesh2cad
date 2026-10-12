import json
import unittest
from pathlib import Path

OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1/task_b")
ART = OUT / "artifacts"


def load(name):
    return json.loads((ART / name).read_text())


class TaskBTests(unittest.TestCase):
    def test_status_pass(self):
        self.assertEqual(load("task_b_summary.json")["TASK_B_STATUS"], "PASS")

    def test_case09_untouched(self):
        self.assertFalse(load("task_b_summary.json")["CASE09_TOUCHED"])
        self.assertFalse(load("resource_isolation_audit.json")["CASE09_TOUCHED"])

    def test_no_gpu_or_inference(self):
        s = load("task_b_summary.json")
        self.assertFalse(s["GPU_USED"])
        self.assertEqual(s["P3_INFERENCE_RUNS"], 0)
        self.assertEqual(s["PHYSX_INFERENCE_RUNS"], 0)

    def test_no_forbidden_generation(self):
        s = load("task_b_summary.json")
        for key in ["LOFT_RUNS", "BSPLINE_RUNS", "MAC_RUNS", "LLM_CALLS", "STEP_GENERATED"]:
            self.assertEqual(s[key], 0)

    def test_step_not_segmentation_input(self):
        self.assertFalse(load("task_b_summary.json")["STEP_USED_AS_SEGMENTATION_INPUT"])
        for case in ["case06", "case07"]:
            g = load(f"{case}_cad_part_graph.json")
            self.assertEqual(g["segmentation_input_type"], "FROZEN_MANIFEST_SOURCE_OBJ")
            self.assertFalse(g["old_step_used_as_segmentation_input"])
            self.assertTrue(g["source_obj"].endswith(".obj"))

    def test_frozen_source_hashes_verified(self):
        self.assertEqual(load("case06_cad_part_graph.json")["source_sha256"], "4a5a333102288e0aa65da6379200c80da996ba072f777fb182233768cdf0a2ee")
        self.assertEqual(load("case07_cad_part_graph.json")["source_sha256"], "5c44ffd7c72a288dc0cdd940f2a22165c815934b89dcc88be523170645a98b8f")

    def test_case06_complete_assignment(self):
        g = load("case06_cad_part_graph.json")
        self.assertEqual(g["P3_SEGMENTS"], 2)
        self.assertEqual(g["CAD_PARTS"], 2)
        self.assertAlmostEqual(g["PART_GRAPH_COVERAGE"], 1.0, places=12)
        self.assertAlmostEqual(g["UNASSIGNED_AREA_RATIO"], 0.0, places=12)
        self.assertEqual(g["OVERLAP_RATIO"], 0.0)

    def test_case06_rootcause(self):
        r = load("case06_rootcause.json")
        self.assertEqual(r["PRIMARY_ROOT_CAUSE"], "PART_CADABILITY_FAILURE")
        self.assertFalse(r["P3_SEGMENTATION_FAILURE"])
        self.assertFalse(r["PHYSX_PRIOR_FAILURE"])
        self.assertTrue(r["PART_CADABILITY_FAILURE"])

    def test_case07_complete_assignment(self):
        g = load("case07_cad_part_graph.json")
        self.assertEqual(g["P3_SEGMENTS"], 30)
        self.assertGreaterEqual(g["CAD_PARTS"], 30)
        self.assertAlmostEqual(g["PART_GRAPH_COVERAGE"], 1.0, places=12)
        self.assertAlmostEqual(g["UNASSIGNED_AREA_RATIO"], 0.0, places=12)
        self.assertEqual(g["OVERLAP_RATIO"], 0.0)
        self.assertEqual(len(g["split_hypotheses"]), 3)
        self.assertEqual({x["p3_segment_id"] for x in g["split_hypotheses"]}, {12, 13, 16})

    def test_case07_coverage_improved(self):
        s = load("task_b_summary.json")
        self.assertLess(s["CASE07_OLD_COVERAGE"], 0.11)
        self.assertGreater(s["CASE07_PART_GRAPH_COVERAGE"], 0.95)
        self.assertGreater(s["CASE07_PART_GRAPH_COVERAGE"] - s["CASE07_OLD_COVERAGE"], 0.85)

    def test_case07_rootcause(self):
        r = load("case07_rootcause.json")
        self.assertEqual(r["PRIMARY_ROOT_CAUSE"], "ROUTER_FAILURE")
        self.assertEqual(r["ROOT_CAUSE_SUBTYPE"], "AREA_UNAWARE_MAX_READY_PARTS_TRUNCATION")
        self.assertEqual(r["evidence"]["max_ready_parts_per_object"], 6)
        self.assertEqual(r["evidence"]["attempted_parts"], 6)
        self.assertEqual(r["evidence"]["accepted_parts"], 5)

    def test_area_conservation(self):
        for case in ["case06", "case07"]:
            g = load(f"{case}_cad_part_graph.json")
            self.assertAlmostEqual(g["ASSIGNED_AREA"] / g["SOURCE_AREA"] + g["UNASSIGNED_AREA_RATIO"], 1.0, places=10)
            self.assertAlmostEqual(sum(n["source_area"] for n in g["nodes"]), g["ASSIGNED_AREA"], places=8)

    def test_residual_catalog_sorted_and_conserved(self):
        for case in ["case06", "case07"]:
            r = load(f"{case}_residuals.json")
            vals = [x["source_area"] for x in r["residual_regions"]]
            self.assertEqual(vals, sorted(vals, reverse=True))
            self.assertAlmostEqual(sum(vals) / (r["OLD_ACCEPTED_SOURCE_AREA_EXACT"] + sum(vals)), r["OLD_UNASSIGNED_AREA_RATIO_EXACT"], places=10)
            self.assertTrue(all(Path(x["mesh_obj"]).is_file() for x in r["residual_regions"]))

    def test_physx_is_soft_unlocalized_prior(self):
        for case in ["case06", "case07"]:
            g = load(f"{case}_cad_part_graph.json")
            self.assertFalse(g["PHYSX_OBJECT_PRIOR"]["localization_available"])
            self.assertEqual(g["PHYSX_OBJECT_PRIOR"]["use"], "SOFT_COUNT_AND_NAMING_PRIOR_ONLY")
            self.assertTrue(all(n["physx_semantic"] is None for n in g["nodes"]))

    def test_input_reuse_audit(self):
        a = load("input_reuse_audit.json")
        self.assertFalse(a["OLD_STEP_USED"])
        self.assertFalse(a["P3_RERUN"])
        self.assertFalse(a["PHYSX_RERUN"])
        for case in ["CASE_06", "CASE_07"]:
            self.assertEqual(a["cases"][case]["segmentation_input_type"], "OBJ")
            self.assertTrue(Path(a["cases"][case]["p3_triangle_map"]).is_file())

    def test_graph_has_geometry_evidence(self):
        for case in ["case06", "case07"]:
            g = load(f"{case}_cad_part_graph.json")
            self.assertTrue(g["component_groups"])
            self.assertIn("adjacency_edges", g)
            self.assertIn("symmetry_hypotheses", g)
            self.assertIn("merge_hypotheses", g)

    def test_no_step_outputs_in_task_b(self):
        self.assertFalse(any(p.suffix.lower() in {".step", ".stp"} for p in OUT.rglob("*")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
