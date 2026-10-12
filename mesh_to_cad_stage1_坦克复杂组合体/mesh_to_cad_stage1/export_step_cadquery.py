"""Export primitives.json to STEP with CadQuery.

Run in an environment with CadQuery installed:
    python export_step_cadquery.py --input outputs/primitives.json --output outputs/03_parametric_reconstruction.step
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq


def make_shape(p: dict) -> cq.Shape:
    if p["type"] == "box":
        x, y, z = p["extents"]
        shape = cq.Workplane("XY").box(x, y, z, centered=(True, True, True)).val()
    elif p["type"] == "cylinder":
        shape = cq.Workplane("XY").cylinder(
            p["height"], p["radius"], centered=(True, True, True)
        ).val()
    else:
        raise ValueError(f"Unsupported primitive: {p['type']}")

    matrix = cq.Matrix(p["transform"])
    return shape.transformShape(matrix)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    primitives = json.loads(args.input.read_text(encoding="utf-8"))
    assembly = cq.Assembly(name="reconstructed")
    for p in primitives:
        assembly.add(make_shape(p), name=f"part_{p['component_id']:02d}_{p['type']}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    assembly.export(str(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
