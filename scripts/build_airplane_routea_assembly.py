#!/usr/bin/env python3
"""Build assembled CAD airplane STEP from Route A per-part STEPs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CASE = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
STEP_ROOT = CASE / "cadfit_routea/step"
XPART_ROOT = CASE / "xpart"
ASSEMBLY_DIR = CASE / "assembly"
RENDER_DIR = CASE / "cadfit_routea/renders"


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(str(path), force="mesh", process=False)


def centroid_translation(source: trimesh.Trimesh, recon: trimesh.Trimesh) -> list[list[float]]:
    delta = np.asarray(source.centroid, float) - np.asarray(recon.centroid, float)
    return [
        [1.0, 0.0, 0.0, float(delta[0])],
        [0.0, 1.0, 0.0, float(delta[1])],
        [0.0, 0.0, 1.0, float(delta[2])],
        [0.0, 0.0, 0.0, 1.0],
    ]


def load_step_shape(path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.TransferRoots():
        raise RuntimeError(f"STEP_READ_FAILED:{path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"STEP_NULL_SHAPE:{path}")
    return shape


def transform_shape(shape, matrix: list[list[float]]):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf

    trsf = gp_Trsf()
    trsf.SetValues(*[float(matrix[r][c]) for r in range(3) for c in range(4)])
    out = BRepBuilderAPI_Transform(shape, trsf, True)
    if not out.IsDone():
        raise RuntimeError("BREP_TRANSFORM_FAILED")
    return out.Shape()


def write_compound_step(shapes: list, out_path: Path) -> bool:
    from OCP.BRep import BRep_Builder
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
    from OCP.TopoDS import TopoDS_Compound

    out_path.parent.mkdir(parents=True, exist_ok=True)
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    if writer.Write(str(out_path)) != IFSelect_RetDone:
        return False
    reader = STEPControl_Reader()
    return reader.ReadFile(str(out_path)) == IFSelect_RetDone and reader.TransferRoots()


def mesh_for_vis(mesh: trimesh.Trimesh, max_faces: int = 12000) -> trimesh.Trimesh:
    if len(mesh.faces) <= max_faces:
        return mesh
    idx = np.random.default_rng(42).choice(len(mesh.faces), size=max_faces, replace=False)
    return mesh.submesh([idx], append=True, repair=False)


def draw_meshes(meshes: list[tuple[trimesh.Trimesh, str]], out_path: Path, title: str, elev: float = 22, azim: float = 42) -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    all_verts = []
    for mesh, color in meshes:
        mv = mesh_for_vis(mesh)
        tris = mv.vertices[mv.faces]
        coll = Poly3DCollection(tris, linewidths=0.02, alpha=0.92)
        coll.set_facecolor(color)
        coll.set_edgecolor((0, 0, 0, 0.04))
        ax.add_collection3d(coll)
        all_verts.append(mv.vertices)
    verts = np.vstack(all_verts)
    bmin, bmax = verts.min(0), verts.max(0)
    ctr = 0.5 * (bmin + bmax)
    ext = np.max(bmax - bmin) * 0.55 + 1e-6
    ax.set_xlim(ctr[0] - ext, ctr[0] + ext)
    ax.set_ylim(ctr[1] - ext, ctr[1] + ext)
    ax.set_zlim(ctr[2] - ext, ctr[2] + ext)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=11)
    ax.axis("off")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    part_ids = sorted(p.name for p in STEP_ROOT.glob("PART_*") if (p / f"{p.name}.step").is_file())
    if not part_ids:
        raise SystemExit("no STEP parts found")

    entries = []
    placed_shapes = []
    placed_meshes: list[tuple[trimesh.Trimesh, str]] = []
    source_meshes: list[trimesh.Trimesh] = []
    palette = ["#E45756", "#4C78A8", "#54A24B", "#F58518", "#B279A2", "#72B7B2", "#EECA3B", "#FF9DA6", "#9D755D"]

    for i, pid in enumerate(part_ids):
        idx = int(pid.split("_")[1])
        step_path = STEP_ROOT / pid / f"{pid}.step"
        src_path = XPART_ROOT / pid / f"complete_part_{idx:03d}.obj"
        recon_path = STEP_ROOT / pid / f"{pid}_reconstructed.stl"
        if not recon_path.is_file():
            recon_path = CASE / "cadfit_routea/cadfit_raw" / pid / "best_greedy_parallel_iterative.stl"
        src = load_mesh(src_path)
        recon = load_mesh(recon_path)
        matrix = centroid_translation(src, recon)
        shape = load_step_shape(step_path)
        placed = transform_shape(shape, matrix)
        placed_shapes.append(placed)
        placed_mesh = recon.copy()
        placed_mesh.apply_transform(np.asarray(matrix, float))
        entries.append(
            {
                "part_id": pid,
                "step_path": str(step_path),
                "source_mesh": str(src_path),
                "recon_mesh": str(recon_path),
                "T_cadfit_local_to_source_global": matrix,
                "translation": [matrix[r][3] for r in range(3)],
            }
        )
        placed_meshes.append((placed_mesh, palette[i % len(palette)]))
        source_meshes.append(src)

    step_out = ASSEMBLY_DIR / "airplane_cad_native.step"
    reload_ok = write_compound_step(placed_shapes, step_out)

    manifest = {
        "CASE": "airplane_p3_xpart_cadfit_routea_v1",
        "FINAL_ASSEMBLY_STEP": str(step_out),
        "ASSEMBLY_STEP_RELOAD_VALID": reload_ok,
        "parts_in_assembly": len(entries),
        "transform_method": "centroid_translation(source_complete_part - cadfit_recon_stl)",
        "parts": entries,
    }
    dump_json(ASSEMBLY_DIR / "assembly_manifest.json", manifest)

    cad_scene = trimesh.util.concatenate([m for m, _ in placed_meshes])
    src_scene = trimesh.util.concatenate(source_meshes)
    cad_scene.export(ASSEMBLY_DIR / "airplane_cad_native_assembly.stl")
    src_scene.export(ASSEMBLY_DIR / "airplane_xpart_source_assembly.stl")

    draw_meshes(
        placed_meshes,
        RENDER_DIR / "assembly_cadfit_isometric.png",
        "Airplane Route A CAD Assembly (9 parts)",
    )
    draw_meshes(
        placed_meshes,
        RENDER_DIR / "assembly_cadfit_top.png",
        "Airplane Route A CAD Assembly — Top View",
        elev=90,
        azim=-90,
    )
    draw_meshes(
        [(src_scene, "#4C78A8")],
        RENDER_DIR / "assembly_source_xpart_isometric.png",
        "Airplane X-Part Source Assembly (reference)",
    )
    draw_meshes(
        [(src_scene, "#4C78A8"), (cad_scene, "#E45756")],
        RENDER_DIR / "assembly_source_vs_cad_overlay.png",
        "Source (blue) vs CADFit Assembly (red)",
    )

    gate_path = CASE / "gate.json"
    if gate_path.is_file():
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        gate["FINAL_ASSEMBLY_STEP"] = str(step_out)
        gate["ASSEMBLY_STEP_RELOAD_VALID"] = reload_ok
        gate["NEXT_PRIMARY_BLOCKER"] = (
            "Assembly STEP built. No revolve recovered; PART_003 IoU=0.28 remains Route B candidate."
        )
        dump_json(gate_path, gate)

    print(json.dumps({k: manifest[k] for k in manifest if k != "parts"}, indent=2))
    print(f"WROTE {step_out}")
    print(f"RENDERS {RENDER_DIR}/assembly_*.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
