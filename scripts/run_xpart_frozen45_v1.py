#!/usr/bin/env python3
"""X-Part complete parts conditioned on frozen 45-part P3 bboxes.

Does not re-run P3-SAM. Does not overwrite p3_xpart_dora_frontend_v1.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

_gpu = "3"
if "--gpu" in sys.argv:
    _gpu = sys.argv[sys.argv.index("--gpu") + 1]
os.environ["CUDA_VISIBLE_DEVICES"] = _gpu
os.environ.setdefault(
    "HY3DGEN_MODELS",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart",
)

import numpy as np
import pytorch_lightning as pl
import torch
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
XPART_ROOT = ROOT / "Hunyuan3D-Part/XPart"
P3_ROOT = ROOT / "Hunyuan3D-Part/P3-SAM"
OUT = ROOT / "ours3/p3_xpart_frozen45_v1"
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
    parser.add_argument("--gpu", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--octree-resolution", type=int, default=512)
    args = parser.parse_args()

    out = OUT
    (out / "xpart").mkdir(parents=True, exist_ok=True)
    (out / "artifacts").mkdir(parents=True, exist_ok=True)

    meta = json.loads((FROZEN / "part_metadata.json").read_text())
    parts = sorted(meta["parts"], key=lambda p: int(p["part_id"]))
    assert len(parts) == 45

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

    source = trimesh.load(SOURCE, force="mesh", process=False)
    mesh_norm, center, scale = pipeline.normalize_mesh(source.copy())
    transform = {
        "center": np.asarray(center).tolist(),
        "scale": float(scale),
        "P3_REEXECUTED": False,
        "condition": "frozen_p3_max_367k_4000 bbox + part surface samples",
        "part_count_in": 45,
    }
    write_json(out / "artifacts/coordinate_transform.json", transform)

    aabb_list = []
    surf_list = []
    kept = []
    for row in parts:
        part = trimesh.load(row["path"], force="mesh", process=False)
        part.vertices = (np.asarray(part.vertices) - center) / scale
        if len(part.faces) < 10 or float(part.area) <= 0:
            continue
        aabb_list.append(np.stack([part.bounds[0], part.bounds[1]], axis=0))
        surf_list.append(sample_part(part, N_PART_POINTS, args.seed + int(row["part_id"])))
        kept.append(int(row["part_id"]))

    aabb = torch.from_numpy(np.stack(aabb_list, axis=0)).float().unsqueeze(0)
    part_surface = torch.stack(surf_list, dim=0).unsqueeze(0)
    write_json(
        out / "artifacts/condition_manifest.json",
        {
            "frozen_root": str(FROZEN),
            "kept_part_ids": kept,
            "dropped": [i for i in range(45) if i not in kept],
            "aabb_shape": list(aabb.shape),
            "part_surface_shape": list(part_surface.shape),
        },
    )

    pipeline.to(device="cuda", dtype=torch.float32)
    t0 = time.time()
    chunk = 10
    qa_rows = []
    all_geoms = []
    for start in range(0, len(kept), chunk):
        sl = slice(start, start + chunk)
        ids = kept[sl]
        print(f"[frozen45] X-Part chunk parts {ids[0]:03d}-{ids[-1]:03d} ({len(ids)})", flush=True)
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
        for j, geom in enumerate(geoms):
            src_id = ids[j] if j < len(ids) else ids[-1]
            part_id = f"PART_{src_id:03d}"
            part_dir = out / "xpart" / part_id
            part_dir.mkdir(parents=True, exist_ok=True)
            world = geom.copy()
            world.vertices = np.asarray(world.vertices) * scale + center
            geom.export(part_dir / "generated_mesh_norm.obj")
            world.export(part_dir / "generated_mesh.obj")
            world.export(part_dir / f"complete_part_{src_id:03d}.obj")
            row = mesh_qa(world, part_id)
            row.update({"frozen_part_id": src_id, "selected": True, "chunk_start": start})
            qa_rows.append(row)
            all_geoms.append(world)
        if aux:
            aux[2].export(out / "artifacts" / f"exploded_chunk_{start:03d}.glb")
        del obj_mesh, aux, geoms
        torch.cuda.empty_cache()

    scene = trimesh.Scene(all_geoms)
    scene.export(out / "artifacts/xpart_assembly.glb")
    runtime = time.time() - t0

    wt = sum(1 for r in qa_rows if r["watertight"])
    summary = {
        "P3_REEXECUTED": False,
        "condition_source": str(FROZEN),
        "XPART_ATTEMPTED_PARTS": len(kept),
        "XPART_SUCCESSFUL_PARTS": len(qa_rows),
        "XPART_WATERTIGHT_PARTS": wt,
        "XPART_WATERTIGHT_RATE": wt / max(len(qa_rows), 1),
        "PARTS_STILL_OPEN": sum(1 for r in qa_rows if not r["watertight"]),
        "runtime_seconds": runtime,
        "octree_resolution": args.octree_resolution,
        "gpu": args.gpu,
        "parts": qa_rows,
        "output_dir": str(out),
    }
    write_json(out / "xpart/manifest.json", summary)
    write_json(out / "artifacts/xpart_summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "parts"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
