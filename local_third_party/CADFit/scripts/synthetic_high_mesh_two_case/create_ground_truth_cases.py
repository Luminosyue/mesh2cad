#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import CASES, ensure_dirs


CASE_A_CODE = r'''import cadquery as cq


def cyl_y(radius, length, x, y0, z):
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
    return cq.Workplane().newObject([solid])


def build_model():
    # Non-rectangular stepped half-section revolved around Y.
    profile = [
        (10, 0), (50, 0), (50, 8), (43, 8), (43, 16),
        (36, 16), (36, 30), (28, 30), (28, 44), (10, 44)
    ]
    solid = cq.Workplane("XY").polyline(profile).close().revolve(
        360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0)
    )
    # Annular outer groove.
    groove = cq.Workplane("XY").polyline([
        (42, 18), (52, 18), (52, 25), (42, 25)
    ]).close().revolve(360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
    solid = solid.cut(groove)
    # Two large axial relief holes through the flange deck.
    solid = solid.cut(cyl_y(4.75, 58, 28, -6, 0))
    solid = solid.cut(cyl_y(4.75, 58, -28, -6, 0))
    return solid


if __name__ == "__main__":
    result = build_model()
    cq.exporters.export(result, "ground_truth.step")
'''


CASE_B_CODE = r'''import cadquery as cq


def cyl_x(radius, length, x0, y, z):
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))
    return cq.Workplane().newObject([solid])


def build_model():
    base = cq.Workplane("XY").box(92, 52, 10).translate((0, 0, 5))
    plate = cq.Workplane("XY").box(14, 44, 50).translate((-24, 0, 35))
    boss1 = cyl_x(11, 20, -36, -13, 34)
    boss2 = cyl_x(9, 18, -35, 14, 43)
    solid = base.union(plate).union(boss1).union(boss2)
    # Through holes coaxial with the two bosses.
    solid = solid.cut(cyl_x(4.7, 42, -44, -13, 34))
    solid = solid.cut(cyl_x(4.0, 42, -44, 14, 43))
    # Rectangular through slot in the base.
    slot = cq.Workplane("XY").box(32, 9, 16).translate((19, 0, 6))
    solid = solid.cut(slot)
    # Side relief groove at the front bottom edge.
    groove = cq.Workplane("XY").box(36, 10, 6).translate((-8, -25, 8))
    solid = solid.cut(groove)
    return solid


if __name__ == "__main__":
    result = build_model()
    cq.exporters.export(result, "ground_truth.step")
'''


def write_case(case_dir: Path, code: str) -> None:
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "ground_truth.py").write_text(code, encoding="utf-8")
    subprocess.run([sys.executable, "ground_truth.py"], cwd=case_dir, check=True)


def main() -> int:
    argparse.ArgumentParser().parse_args()
    ensure_dirs()
    root = Path("datasets/synthetic_high_mesh_two_case_v1")
    write_case(root / "case_a_flange", CASE_A_CODE)
    write_case(root / "case_b_bracket", CASE_B_CODE)
    print("GROUND_TRUTH_CASES_CREATED=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
