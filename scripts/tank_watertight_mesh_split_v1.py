#!/usr/bin/env python3
"""Split a watertight source mesh into watertight solid parts.

P3 triangle labels are used only as region identity. Each output part is a
closed volume extracted from the source occupancy, not an open surface patch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.ndimage import binary_closing
from trimesh.voxel.ops import matrix_to_marching_cubes


PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad")
DEFAULT_SOURCE = PROJECT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
DEFAULT_P3 = PROJECT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
DEFAULT_OUT = PROJECT / "ours3/tank_watertight_mesh_split_v1"


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n")


def voxelize_filled(mesh: trimesh.Trimesh, pitch: float):
    voxel = mesh.voxelized(pitch)
    filled = voxel.fill()
    matrix = np.asarray(filled.matrix, dtype=bool)
    origin = np.asarray(filled.transform[:3, 3], dtype=float)
    return matrix, origin, float(pitch)


def assign_labels(occupied_ijk: np.ndarray, origin: np.ndarray, pitch: float, centroids: np.ndarray, labels: np.ndarray) -> np.ndarray:
    points = origin + (occupied_ijk.astype(float) + 0.5) * pitch
    _, index = cKDTree(centroids).query(points, workers=-1)
    return labels[index]


def extract_part(volume: np.ndarray, origin: np.ndarray, pitch: float) -> trimesh.Trimesh | None:
    if int(volume.sum()) < 8:
        return None
    padded = np.pad(volume, 1, mode="constant", constant_values=False)
    mesh = matrix_to_marching_cubes(padded, pitch=pitch)
    if mesh is None or len(mesh.faces) == 0:
        return None
    mesh.vertices = mesh.vertices + origin - pitch
    mesh.remove_unreferenced_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def render_preview(parts: list[trimesh.Trimesh], output: Path) -> None:
    helper = PROJECT / "ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/scripts/render_p3_45_assembly.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_p3", helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    colors = mod.palette(len(parts))
    vertices = np.vstack([np.asarray(part.vertices) for part in parts])
    bounds = np.vstack([vertices.min(0), vertices.max(0)]).T
    diag = float(np.linalg.norm(vertices.max(0) - vertices.min(0)))
    iso = mod.camera_matrix(38, 24)
    exploded = []
    center = vertices.mean(0)
    for part in parts:
        mesh = part.copy()
        centroid = np.asarray(mesh.triangles_center).mean(0)
        direction = centroid - center
        norm = np.linalg.norm(direction)
        if norm > 1e-9:
            mesh.vertices = mesh.vertices + direction / norm * diag * 0.18
        exploded.append(mesh)
    exploded_vertices = np.vstack([np.asarray(part.vertices) for part in exploded])
    exploded_bounds = np.vstack([exploded_vertices.min(0), exploded_vertices.max(0)]).T
    cad_color = [(113, 174, 205)] * len(parts)
    counts = np.asarray([len(part.faces) for part in parts], float)
    budgets = np.maximum(400, np.round(counts / counts.sum() * 140000)).astype(int).tolist()
    output.mkdir(parents=True, exist_ok=True)
    shaded = output / "watertight_shaded.png"
    colored = output / "watertight_parts.png"
    exploded_png = output / "watertight_exploded.png"
    sheet = output / "review_sheet.png"
    mod.render_scene(parts, cad_color, bounds, shaded, iso, budgets=budgets)
    mod.render_scene(parts, colors, bounds, colored, iso, budgets=budgets)
    mod.render_scene(exploded, colors, exploded_bounds, exploded_png, iso, budgets=budgets)
    mod.compose(
        [shaded, colored, exploded_png],
        ["Watertight solids shaded", "Watertight parts", "Exploded solids"],
        sheet,
        caption=f"{len(parts)} watertight volume-split parts from source occupancy  |  P3 labels used as identity only",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--p3-root", type=Path, default=DEFAULT_P3)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--grid-size", type=int, default=192)
    parser.add_argument("--close-iters", type=int, default=1)
    args = parser.parse_args()
    out = args.output_root.resolve()
    parts_dir = out / "01_watertight_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    source = trimesh.load(str(args.source), force="mesh", process=False)
    labels = np.asarray(np.load(args.p3_root / "triangle_part_id.npy"), dtype=np.int64).reshape(-1)
    if len(labels) != len(source.faces):
        raise RuntimeError(f"P3_LABEL_COUNT_MISMATCH:{len(labels)}:{len(source.faces)}")
    if not bool(source.is_watertight):
        raise RuntimeError("SOURCE_MESH_NOT_WATERTIGHT_VOLUME_SPLIT_REQUIRES_CLOSED_BODY")

    pitch = float(np.max(source.extents) / max(args.grid_size, 8))
    print(f"voxelizing pitch={pitch:.5f} grid_size={args.grid_size}", flush=True)
    occupied, origin, pitch = voxelize_filled(source, pitch)
    print(f"occupied_voxels={int(occupied.sum())} shape={tuple(occupied.shape)}", flush=True)
    ijk = np.argwhere(occupied)
    assigned = assign_labels(ijk, origin, pitch, np.asarray(source.triangles_center, float), labels)

    unique = sorted(int(v) for v in np.unique(labels))
    rows = []
    meshes = []
    watertight_count = 0
    for part_id in unique:
        volume = np.zeros(occupied.shape, dtype=bool)
        volume[tuple(ijk[assigned == part_id].T)] = True
        if args.close_iters > 0:
            volume = binary_closing(volume, iterations=args.close_iters)
        mesh = extract_part(volume, origin, pitch)
        component_id = f"WT_COMPONENT_{part_id:03d}"
        if mesh is None:
            rows.append(
                {
                    "component_id": component_id,
                    "p3_label": part_id,
                    "extracted": False,
                    "watertight": False,
                    "voxel_count": int(volume.sum()),
                }
            )
            continue
        path = parts_dir / f"part_{part_id:03d}.obj"
        mesh.export(path)
        is_wt = bool(mesh.is_watertight)
        watertight_count += int(is_wt)
        meshes.append(mesh)
        rows.append(
            {
                "component_id": component_id,
                "p3_label": part_id,
                "extracted": True,
                "watertight": is_wt,
                "manifold": bool(mesh.is_winding_consistent),
                "vertex_count": int(len(mesh.vertices)),
                "triangle_count": int(len(mesh.faces)),
                "volume": float(mesh.volume) if is_wt else None,
                "voxel_count": int(volume.sum()),
                "obj_path": str(path),
            }
        )
        print(
            f"[{part_id:03d}] tris={len(mesh.faces)} watertight={is_wt} voxels={int(volume.sum())}",
            flush=True,
        )

    if meshes:
        render_preview(meshes, out / "artifacts/visuals")
    summary = {
        "schema": "TANK_WATERTIGHT_MESH_SPLIT_V1",
        "method": "SOURCE_OCCUPANCY_VOXEL_SPLIT",
        "P3_REEXECUTED": False,
        "p3_used_as": "REGION_IDENTITY_ONLY",
        "source_obj": str(args.source.resolve()),
        "p3_root": str(args.p3_root.resolve()),
        "source_watertight": True,
        "source_volume": float(source.volume),
        "pitch": pitch,
        "grid_shape": list(occupied.shape),
        "occupied_voxels": int(occupied.sum()),
        "component_count": len(rows),
        "extracted_count": sum(row["extracted"] for row in rows),
        "watertight_count": watertight_count,
        "all_extracted_watertight": watertight_count == sum(row["extracted"] for row in rows) and watertight_count > 0,
        "components": rows,
        "note": "Each part is a closed solid from the source volume. This is mesh splitting, not P3 open-surface segmentation.",
    }
    dump(out / "artifacts/watertight_split_summary.json", summary)
    print(json.dumps({k: summary[k] for k in summary if k != "components"}, indent=2))
    return 0 if summary["all_extracted_watertight"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
