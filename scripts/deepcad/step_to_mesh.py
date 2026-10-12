#!/usr/bin/env python3
"""Convert STEP to mesh.obj / mesh.stl for Dora front-end."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import trimesh


def _load_step_with_cadquery(step_path: Path):
    import cadquery as cq

    return cq.importers.importStep(str(step_path))


def _cq_to_trimesh(shape) -> trimesh.Trimesh:
    import cadquery as cq
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        cq.exporters.export(shape, str(tmp_path))
        mesh = trimesh.load(str(tmp_path), force="mesh", process=True)
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
        return trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=True)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def step_to_mesh(step_path: Path, obj_path: Path, stl_path: Path | None = None) -> dict:
    try:
        mesh = trimesh.load(str(step_path), force="mesh", process=True)
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
        mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=True)
        loader = "trimesh"
    except Exception:
        cq_shape = _load_step_with_cadquery(step_path)
        mesh = _cq_to_trimesh(cq_shape)
        loader = "cadquery"

    if len(mesh.faces) == 0:
        raise RuntimeError(f"empty mesh from STEP: {step_path}")

    obj_path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(obj_path)
    out = {
        "step": str(step_path),
        "obj": str(obj_path),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "loader": loader,
    }
    if stl_path is not None:
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        mesh.export(stl_path)
        out["stl"] = str(stl_path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="STEP → OBJ/STL")
    parser.add_argument("--step", type=Path, required=True)
    parser.add_argument("--obj", type=Path, required=True)
    parser.add_argument("--stl", type=Path, default=None)
    args = parser.parse_args()
    result = step_to_mesh(args.step, args.obj, args.stl)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
