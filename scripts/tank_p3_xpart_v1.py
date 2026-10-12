#!/usr/bin/env python3
"""Run official Hunyuan P3-SAM + X-Part on the tank mesh.

Pipeline:
  holistic mesh -> P3-SAM (bbox + semantic features) -> X-Part (complete parts)
  -> per-part OBJ export -> watertight / manifold QA summary
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pytorch_lightning as pl
import torch
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART_ROOT = ROOT / "Hunyuan3D-Part" / "XPart"
DEFAULT_MESH = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
DEFAULT_OUT = ROOT / "ours3/tank_p3_xpart_v1"


def mesh_qa(mesh: trimesh.Trimesh) -> dict:
    bounds = mesh.bounds
    bbox_diag = float(np.linalg.norm(bounds[1] - bounds[0])) if bounds is not None else 0.0
    volume = None
    if mesh.is_watertight:
        try:
            volume = float(mesh.volume)
        except Exception:
            volume = None
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "volume": volume,
        "area": float(mesh.area),
        "bbox_diagonal": bbox_diag,
        "euler_number": int(mesh.euler_number) if hasattr(mesh, "euler_number") else None,
        "is_winding_consistent": bool(mesh.is_winding_consistent),
    }


def export_parts(scene: trimesh.Scene, parts_dir: Path) -> list[dict]:
    parts_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, (name, geom) in enumerate(scene.geometry.items()):
        if not isinstance(geom, trimesh.Trimesh):
            continue
        part_path = parts_dir / f"complete_part_{idx:03d}.obj"
        geom.export(part_path)
        qa = mesh_qa(geom)
        qa.update({"part_index": idx, "geometry_name": str(name), "path": str(part_path)})
        rows.append(qa)
    return rows


def ensure_local_p3_weights(model_cache: Path) -> None:
    p3_target = model_cache / "p3sam" / "p3sam.safetensors"
    p3_source = ROOT / "Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors"
    if p3_target.is_file() or not p3_source.is_file():
        return
    p3_target.parent.mkdir(parents=True, exist_ok=True)
    p3_target.symlink_to(p3_source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh-path", type=Path, default=DEFAULT_MESH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--octree-resolution", type=int, default=512)
    parser.add_argument(
        "--model-path",
        type=str,
        default="tencent/Hunyuan3D-Part",
        help="HF repo id or local model dir under HY3DGEN_MODELS",
    )
    args = parser.parse_args()

    os.environ.setdefault(
        "HY3DGEN_MODELS",
        str(ROOT / "ours3/.cache/xpart"),
    )
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    out = args.output_dir
    parts_dir = out / "01_complete_parts"
    artifacts = out / "artifacts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)

    ensure_local_p3_weights(Path(os.environ["HY3DGEN_MODELS"]) / "tencent/Hunyuan3D-Part")

    sys.path.insert(0, str(XPART_ROOT))
    from partgen.partformer_pipeline import PartFormerPipeline

    started = time.time()
    pl.seed_everything(args.seed, workers=True)

    print(f"[tank_p3_xpart] mesh={args.mesh_path}")
    print(f"[tank_p3_xpart] output={out}")
    print(f"[tank_p3_xpart] HY3DGEN_MODELS={os.environ['HY3DGEN_MODELS']}")

    pipeline = PartFormerPipeline.from_pretrained(
        model_path=args.model_path,
        verbose=True,
    )
    pipeline.to(device="cuda", dtype=torch.float32)

    load_seconds = time.time() - started
    source_mesh = trimesh.load(args.mesh_path, force="mesh")
    source_qa = mesh_qa(source_mesh)
    with (artifacts / "source_mesh_qa.json").open("w", encoding="utf-8") as handle:
        json.dump(source_qa, handle, indent=2)
        handle.write("\n")

    infer_started = time.time()
    obj_mesh, aux = pipeline(
        mesh_path=str(args.mesh_path),
        octree_resolution=args.octree_resolution,
        output_type="trimesh",
        seed=args.seed,
    )
    infer_seconds = time.time() - infer_started

    uid = args.mesh_path.stem
    assembly_glb = artifacts / f"{uid}_xpart_assembly.glb"
    obj_mesh.export(assembly_glb)

    part_rows = export_parts(obj_mesh, parts_dir)
    if aux is not None:
        out_bbox, mesh_gt_bbox, explode_object = aux
        out_bbox.export(artifacts / f"{uid}_xpart_bbox.glb")
        mesh_gt_bbox.export(artifacts / f"{uid}_xpart_input_bbox.glb")
        explode_object.export(artifacts / f"{uid}_xpart_exploded.glb")

    watertight_count = sum(1 for row in part_rows if row["watertight"])
    summary = {
        "mesh_path": str(args.mesh_path),
        "output_dir": str(out),
        "model_path": args.model_path,
        "seed": args.seed,
        "octree_resolution": args.octree_resolution,
        "source_mesh_qa": source_qa,
        "part_count": len(part_rows),
        "watertight_parts": watertight_count,
        "watertight_ratio": watertight_count / max(len(part_rows), 1),
        "parts": part_rows,
        "assembly_glb": str(assembly_glb),
        "runtime_seconds": {
            "pipeline_load": load_seconds,
            "inference": infer_seconds,
            "total": time.time() - started,
        },
        "peak_gpu_memory_mb": float(torch.cuda.max_memory_allocated() / 1024**2)
        if torch.cuda.is_available()
        else None,
    }
    with (artifacts / "xpart_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    print(
        f"[tank_p3_xpart] done parts={len(part_rows)} "
        f"watertight={watertight_count}/{len(part_rows)} "
        f"elapsed={summary['runtime_seconds']['total']:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
