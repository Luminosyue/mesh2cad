"""Extent converter: signed distance, circle/rect two-side kwargs, executor geometry."""
import ast
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/fusion360"), str(ROOT / "scripts/geometry_pack_v2_mesh2cad")]

from fusion360_to_dsl import _parse_extent, fusion360_json_to_dsl  # noqa: E402
from edge_aware_cad_planner_v1.cad_dsl import execute_dsl  # noqa: E402


def _circle_sketch(oid="s0", pid="p0", radius=1.0, origin=(0, 0, 0), z_axis=(0, 0, 1)):
    return {
        oid: {
            "type": "Sketch",
            "transform": {
                "origin": {"x": origin[0], "y": origin[1], "z": origin[2]},
                "x_axis": {"x": 1, "y": 0, "z": 0},
                "z_axis": {"x": z_axis[0], "y": z_axis[1], "z": z_axis[2]},
            },
            "profiles": {
                pid: {
                    "loops": [
                        {
                            "is_outer": True,
                            "profile_curves": [
                                {
                                    "type": "Circle3D",
                                    "center_point": {"x": 0, "y": 0},
                                    "radius": radius,
                                }
                            ],
                        }
                    ]
                }
            },
        }
    }


def _rect_sketch(oid="s0", pid="p0"):
    lines = [
        ((0, 0), (2, 0)),
        ((2, 0), (2, 1)),
        ((2, 1), (0, 1)),
        ((0, 1), (0, 0)),
    ]
    return {
        oid: {
            "type": "Sketch",
            "transform": {
                "origin": {"x": 0, "y": 0, "z": 0},
                "x_axis": {"x": 1, "y": 0, "z": 0},
                "z_axis": {"x": 0, "y": 0, "z": 1},
            },
            "profiles": {
                pid: {
                    "loops": [
                        {
                            "is_outer": True,
                            "profile_curves": [
                                {
                                    "type": "Line3D",
                                    "start_point": {"x": a[0], "y": a[1]},
                                    "end_point": {"x": b[0], "y": b[1]},
                                }
                                for a, b in lines
                            ],
                        }
                    ]
                }
            },
        }
    }


def _extrude(eid, sketch, profile, extent_type, d1, d2=None, op="NewBodyFeatureOperation"):
    ent = {
        "type": "ExtrudeFeature",
        "operation": op,
        "profiles": [{"sketch": sketch, "profile": profile}],
        "start_extent": {"type": "ProfilePlaneStartDefinition"},
        "extent_type": extent_type,
        "extent_one": {"distance": {"value": d1}, "taper_angle": {"value": 0.0}},
    }
    if d2 is not None:
        ent["extent_two"] = {"distance": {"value": d2}, "taper_angle": {"value": 0.0}}
    return {eid: ent}


class ConverterTests(unittest.TestCase):
    def test_parse_keeps_negative_distance(self):
        got = _parse_extent(
            {
                "extent_type": "OneSideFeatureExtentType",
                "start_extent": {"type": "ProfilePlaneStartDefinition"},
                "extent_one": {"distance": {"value": -1.524}, "taper_angle": {"value": 0.0}},
            }
        )
        self.assertEqual(got["height"], -1.524)
        self.assertFalse(got["symmetric"])

    def test_circle_symmetric_emits_kwarg(self):
        entities = {}
        entities.update(_circle_sketch())
        entities.update(_extrude("e0", "s0", "p0", "SymmetricFeatureExtentType", 60.0))
        data = {"timeline": [{"index": 0, "entity": "s0"}, {"index": 1, "entity": "e0"}], "entities": entities}
        dsl, report = fusion360_json_to_dsl(data)
        self.assertIn("symmetric=True", dsl)
        self.assertIn("height=60", dsl)
        self.assertEqual(report["operations"][0]["profile_kind"], "circle")
        self.assertEqual(report["operations"][0]["extent_type"], "SymmetricFeatureExtentType")

    def test_rectangle_two_side_emits_height_two(self):
        entities = {}
        entities.update(_rect_sketch())
        entities.update(_extrude("e0", "s0", "p0", "TwoSidesFeatureExtentType", 13.18, 5.9))
        data = {"timeline": [{"index": 0, "entity": "s0"}, {"index": 1, "entity": "e0"}], "entities": entities}
        dsl, _ = fusion360_json_to_dsl(data)
        self.assertIn("height_two=5.9", dsl)
        self.assertIn("Box(", dsl)

    def test_negative_one_side_not_abs(self):
        entities = {}
        entities.update(_circle_sketch())
        entities.update(_extrude("e0", "s0", "p0", "OneSideFeatureExtentType", -2.8))
        data = {"timeline": [{"index": 0, "entity": "s0"}, {"index": 1, "entity": "e0"}], "entities": entities}
        dsl, _ = fusion360_json_to_dsl(data)
        self.assertIn("height=-2.8", dsl)
        self.assertNotIn("height=2.8", dsl)


class ExecutorGeometryTests(unittest.TestCase):
    def _bbox(self, dsl: str):
        import cadquery as cq

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.step"
            execute_dsl(dsl, p)
            s = cq.importers.importStep(str(p)).val()
            b = s.BoundingBox()
            return np.array([b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]), float(s.Volume())

    def test_symmetric_circle_doubles_height(self):
        one = "a=Extrude(Circle(radius=1),height=2,axis=(0,0,1),origin=(0,0,0))\nresult=a"
        two = "a=Extrude(Circle(radius=1),height=2,axis=(0,0,1),origin=(0,0,0),symmetric=True)\nresult=a"
        _, v1 = self._bbox(one)
        bb2, v2 = self._bbox(two)
        self.assertAlmostEqual(v2 / v1, 2.0, places=5)
        self.assertAlmostEqual(bb2[5] - bb2[2], 4.0, places=5)

    def test_negative_height_reverses_box(self):
        pos = "a=Box(width=2,depth=2,height=3,axis=(0,0,1),origin=(0,0,0),x_axis=(1,0,0))\nresult=a"
        neg = "a=Box(width=2,depth=2,height=-3,axis=(0,0,1),origin=(0,0,0),x_axis=(1,0,0))\nresult=a"
        bp, _ = self._bbox(pos)
        bn, _ = self._bbox(neg)
        self.assertGreater(bp[5], 2.9)
        self.assertLess(bp[2], 0.1)
        self.assertLess(bn[2], -2.9)
        self.assertGreater(bn[5], -0.1)

    def test_real_circle_symmetric_sample_converts(self):
        src = ROOT / "cad_spatial_dataset/Fusion360/train/21865_c190b734_0000/source.json"
        if not src.exists():
            self.skipTest("sample missing")
        import json

        dsl, _ = fusion360_json_to_dsl(json.loads(src.read_text()))
        self.assertIn("symmetric=True", dsl)
        self.assertIn("Extrude(Circle", dsl)


if __name__ == "__main__":
    unittest.main()
