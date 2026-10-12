#!/usr/bin/env python3
"""Run official X-Part on P3 part bboxes + surfaces for any case."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

if "--gpu" in sys.argv:
    os.environ["CUDA_VISIBLE_DEVICES"] = sys.argv[sys.argv.index("--gpu") + 1]
os.environ.setdefault("HY3DGEN_MODELS", "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart")

import numpy as np
import pytorch_lightning as pl
import torch
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART_ROOT = ROOT / "Hunyuan3D-Part/XPart"
P3_ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_historical_route_100_20261011/runs/new_object_042/runtime/p3')
N_PART_POINTS = 81920


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def mesh_qa(mesh: trimesh.Trimesh, part_id: str) -> dict:
    counts = np.bincount(mesh.edges_unique_inverse)
    return {
        "part_id": part_id,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "boundary_edges": int(np.sum(counts == 1)),
        "manifold": bool(mesh.is_watertight and int(np.sum(counts > 2)) == 0),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "surface_area": float(mesh.area),
        "volume": float(mesh.volume) if mesh.is_watertight else None,
        "bbox_min": mesh.bounds[0].tolist(),
        "bbox_max": mesh.bounds[1].tolist(),
    }


def sample_part(mesh: trimesh.Trimesh, n: int, seed: int) -> torch.Tensor:
    pts, fid = trimesh.sample.sample_surface(mesh, n, seed=seed)
    nrm = mesh.face_normals[fid]
    sharp = np.zeros((n, 1), dtype=np.float32)
    arr = np.concatenate([pts.astype(np.float32), nrm.astype(np.float32), sharp], axis=-1)
    return torch.from_numpy(arr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-mesh", type=Path, required=True)
    parser.add_argument("--p3-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--gpu", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--octree-resolution", type=int, default=512)
    args = parser.parse_args()

    xpart_root = args.out_dir
    xpart_root.mkdir(parents=True, exist_ok=True)
    meta = json.loads((args.p3_dir / "part_metadata.json").read_text())
    parts = sorted(meta["parts"], key=lambda p: int(p["part_id"]))

    sys.path.insert(0, str(P3_ROOT))
    sys.path.insert(0, str(XPART_ROOT))
    from partgen.partformer_pipeline import PartFormerPipeline

    pl.seed_everything(args.seed, workers=True)
    pipeline = PartFormerPipeline.from_pretrained("tencent/Hunyuan3D-Part", verbose=True)
    try:
        pipeline.bbox_predictor.model.cpu()
        pipeline.bbox_predictor.model_parallel.cpu()
    except Exception:
        pass
    torch.cuda.empty_cache()

    source = trimesh.load(args.source_mesh, force="mesh", process=False)
    mesh_norm, center, scale = pipeline.normalize_mesh(source.copy())
    write_json(xpart_root.parent / "artifacts/xpart_transform.json", {
        "center": np.asarray(center).tolist(),
        "scale": float(scale),
        "XPART_REEXECUTED": True,
    })

    aabb_list, surf_list, kept = [], [], []
    for row in parts:
        p = Path(row["path"])
        part_path = p if p.is_absolute() else args.p3_dir / p.name
        part = trimesh.load(part_path, force="mesh", process=False)
        part.vertices = (np.asarray(part.vertices) - center) / scale
        if len(part.faces) < 10 or float(part.area) <= 0:
            continue
        aabb_list.append(np.stack([part.bounds[0], part.bounds[1]], axis=0))
        surf_list.append(sample_part(part, N_PART_POINTS, args.seed + int(row["part_id"])))
        kept.append(int(row["part_id"]))

    aabb = torch.from_numpy(np.stack(aabb_list, axis=0)).float().unsqueeze(0)
    part_surface = torch.stack(surf_list, dim=0).unsqueeze(0)
    pipeline.to(device="cuda", dtype=torch.float32)

    qa_rows, all_geoms = [], []
    t0 = time.time()
    chunk = max(1, min(args.batch_size, 10))
    for start in range(0, len(kept), chunk):
        sl = slice(start, start + chunk)
        ids = kept[sl]
        print(f"[xpart_from_p3] chunk {ids[0]:03d}-{ids[-1]:03d} n={len(ids)}", flush=True)
        torch.cuda.empty_cache()
        obj_mesh, aux = pipeline(
            mesh=mesh_norm,
            aabb=aabb[:, sl],
            part_surface_inbbox=part_surface[:, sl],
            octree_resolution=args.octree_resolution,
            output_type="trimesh",
            seed=args.seed,
        )
        geoms = [g for g in obj_mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
        assert len(geoms) == len(ids), "XPart output/input count mismatch; do not assign guessed part IDs"
        for j, geom in enumerate(geoms):
            src_id = ids[j] if j < len(ids) else ids[-1]
            part_id = f"PART_{src_id:03d}"
            part_dir = xpart_root / part_id
            part_dir.mkdir(parents=True, exist_ok=True)
            seg = args.p3_dir / f"part_{src_id:03d}.obj"
            if seg.is_file():
                import shutil
                shutil.copy2(seg, part_dir / "source_segment.obj")
            world = geom.copy()
            world.vertices = np.asarray(world.vertices) * scale + center
            geom.export(part_dir / "generated_mesh_norm.obj")
            world.export(part_dir / "generated_mesh.obj")
            world.export(part_dir / f"complete_part_{src_id:03d}.obj")
            write_json(part_dir / "transform.json", {
                "center": np.asarray(center).tolist(),
                "scale": float(scale),
            })
            row = mesh_qa(world, part_id)
            row["success"] = True
            write_json(part_dir / "qa.json", row)
            qa_rows.append(row)
            all_geoms.append(world)
        if aux:
            (xpart_root.parent / "artifacts").mkdir(parents=True, exist_ok=True)
            aux[2].export(xpart_root.parent / "artifacts" / f"exploded_chunk_{start:03d}.glb")
        del obj_mesh, aux, geoms
        torch.cuda.empty_cache()

    if all_geoms:
        trimesh.Scene(all_geoms).export(xpart_root.parent / "artifacts/xpart_assembly.glb")

    wt = sum(1 for r in qa_rows if r["watertight"])
    summary = {
        "XPART_REEXECUTED": True,
        "XPART_ATTEMPTED_PARTS": len(kept),
        "XPART_SUCCESSFUL_PARTS": len(qa_rows),
        "XPART_WATERTIGHT_PARTS": wt,
        "XPART_WATERTIGHT_RATE": wt / max(len(qa_rows), 1),
        "runtime_seconds": time.time() - t0,
        "parts": qa_rows,
    }
    write_json(xpart_root / "manifest.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "parts"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
