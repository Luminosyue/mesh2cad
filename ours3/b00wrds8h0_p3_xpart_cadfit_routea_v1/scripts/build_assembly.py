#!/usr/bin/env python3
"""Assemble Route A CAD parts back into X-Part source space.

Tank Route A method: uniform scale by max extent + centroid translation.
"""
from __future__ import annotations

import colorsys
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import CASE, CADFIT_DIR, STEP_DIR, XPART_DIR  # noqa: E402

ASSEMBLY_DIR = CASE / "assembly"
RENDER_DIR = CADFIT_DIR / "renders"
LABEL = CASE.name.split("_p3_")[0]


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(str(path), force="mesh", process=False)


def similarity_matrix(source: trimesh.Trimesh, recon: trimesh.Trimesh) -> list[list[float]]:
    """Uniform scale + centroid translation: recon local -> source global."""
    src_c = np.asarray(source.centroid, float)
    rec_c = np.asarray(recon.centroid, float)
    src_ext = float(np.max(source.extents))
    rec_ext = float(np.max(recon.extents))
    scale = src_ext / rec_ext if rec_ext > 1e-12 else 1.0
    t = src_c - scale * rec_c
    return [
        [scale, 0.0, 0.0, float(t[0])],
        [0.0, scale, 0.0, float(t[1])],
        [0.0, 0.0, scale, float(t[2])],
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


def mesh_for_vis(mesh: trimesh.Trimesh, max_faces: int) -> trimesh.Trimesh:
    if len(mesh.faces) <= max_faces:
        return mesh
    idx = np.random.default_rng(42).choice(len(mesh.faces), size=max_faces, replace=False)
    return mesh.submesh([idx], append=True, repair=False)


def part_color(i: int, n: int) -> str:
    hue = (i / max(n, 1)) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.62, 0.88)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def draw_meshes(
    meshes: list[tuple[trimesh.Trimesh, str]],
    out_path: Path,
    title: str,
    elev: float = 22,
    azim: float = 42,
    max_faces: int = 2500,
) -> None:
    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, projection="3d")
    all_verts = []
    for mesh, color in meshes:
        mv = mesh_for_vis(mesh, max_faces)
        tris = mv.vertices[mv.faces]
        coll = Poly3DCollection(tris, linewidths=0.015, alpha=0.92)
        coll.set_facecolor(color)
        coll.set_edgecolor((0, 0, 0, 0.03))
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
    print(f"WROTE {out_path}")


def explode(meshes: list[trimesh.Trimesh], factor: float = 0.35) -> list[trimesh.Trimesh]:
    cents = np.vstack([np.asarray(m.centroid, float) for m in meshes])
    origin = cents.mean(axis=0)
    out = []
    for mesh, c in zip(meshes, cents):
        delta = (c - origin) * factor
        moved = mesh.copy()
        moved.apply_translation(delta)
        out.append(moved)
    return out


def main() -> int:
    part_ids = sorted(p.name for p in STEP_DIR.glob("PART_*") if (p / f"{p.name}.step").is_file())
    if not part_ids:
        raise SystemExit("no STEP parts found")

    entries = []
    placed_shapes = []
    placed_meshes: list[tuple[trimesh.Trimesh, str]] = []
    source_meshes: list[trimesh.Trimesh] = []
    n = len(part_ids)

    for i, pid in enumerate(part_ids):
        idx = int(pid.split("_")[1])
        step_path = STEP_DIR / pid / f"{pid}.step"
        src_path = XPART_DIR / pid / f"complete_part_{idx:03d}.obj"
        recon_path = STEP_DIR / pid / f"{pid}_reconstructed.stl"
        if not recon_path.is_file():
            recon_path = CADFIT_DIR / "cadfit_raw" / pid / "best_greedy_parallel_iterative.stl"
        src = load_mesh(src_path)
        recon = load_mesh(recon_path)
        matrix = similarity_matrix(src, recon)
        placed_shapes.append(transform_shape(load_step_shape(step_path), matrix))
        placed_mesh = recon.copy()
        placed_mesh.apply_transform(np.asarray(matrix, float))
        entries.append(
            {
                "part_id": pid,
                "step_path": str(step_path),
                "source_mesh": str(src_path),
                "recon_mesh": str(recon_path),
                "scale": matrix[0][0],
                "T_cadfit_local_to_source_global": matrix,
                "translation": [matrix[r][3] for r in range(3)],
            }
        )
        placed_meshes.append((placed_mesh, part_color(i, n)))
        source_meshes.append(mesh_for_vis(src, 8000))
        print(f"placed {pid} scale={matrix[0][0]:.4f}")

    step_out = ASSEMBLY_DIR / f"{LABEL}_cad_native.step"
    reload_ok = write_compound_step(placed_shapes, step_out)

    manifest = {
        "CASE": CASE.name,
        "LABEL": LABEL,
        "FINAL_ASSEMBLY_STEP": str(step_out),
        "ASSEMBLY_STEP_RELOAD_VALID": reload_ok,
        "parts_in_assembly": len(entries),
        "transform_method": "uniform_scale_max_extent + centroid_translation",
        "parts": entries,
    }
    dump_json(ASSEMBLY_DIR / "assembly_manifest.json", manifest)

    cad_scene = trimesh.util.concatenate([m for m, _ in placed_meshes])
    src_scene = trimesh.util.concatenate(source_meshes)
    cad_scene.export(ASSEMBLY_DIR / f"{LABEL}_cad_native_assembly.stl")
    src_scene.export(ASSEMBLY_DIR / f"{LABEL}_xpart_source_assembly.stl")

    title = LABEL.replace("_", " ").title()
    draw_meshes(
        placed_meshes,
        RENDER_DIR / "assembly_cadfit_isometric.png",
        f"{title} Route A CAD Assembly ({n} parts)",
    )
    draw_meshes(
        placed_meshes,
        RENDER_DIR / "assembly_cadfit_top.png",
        f"{title} Route A CAD Assembly — Top View",
        elev=90,
        azim=-90,
    )
    draw_meshes(
        [(src_scene, "#4C78A8")],
        RENDER_DIR / "assembly_source_xpart_isometric.png",
        f"{title} X-Part Source Assembly (reference)",
        max_faces=80000,
    )
    draw_meshes(
        [(src_scene, "#4C78A8"), (cad_scene, "#E45756")],
        RENDER_DIR / "assembly_source_vs_cad_overlay.png",
        "Source (blue) vs CADFit Assembly (red)",
        max_faces=60000,
    )
    exploded = explode([m for m, _ in placed_meshes], factor=0.45)
    draw_meshes(
        list(zip(exploded, [c for _, c in placed_meshes])),
        RENDER_DIR / "assembly_cadfit_exploded.png",
        f"{title} Route A CAD Assembly — Exploded",
    )

    print(json.dumps({k: manifest[k] for k in manifest if k != "parts"}, indent=2))
    print(f"WROTE {step_out} reload_ok={reload_ok}")
    return 0 if reload_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
