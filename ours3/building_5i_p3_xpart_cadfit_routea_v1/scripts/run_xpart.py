#!/usr/bin/env python3
"""Official X-Part complete parts, conditioned on frozen P3 bboxes.

Does not re-run P3. Chunks of 10 to avoid OOM. octree=512.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import (  # noqa: E402
    CASE,
    HY3DGEN_MODELS,
    P3_DIR,
    P3_ROOT,
    SOURCE,
    XPART_DIR,
    XPART_ROOT,
)

_gpu = "3"
if "--gpu" in sys.argv:
    _gpu = sys.argv[sys.argv.index("--gpu") + 1]
os.environ["CUDA_VISIBLE_DEVICES"] = _gpu
os.environ.setdefault("HY3DGEN_MODELS", str(HY3DGEN_MODELS))

import numpy as np  # noqa: E402
import pytorch_lightning as pl  # noqa: E402
import torch  # noqa: E402
import trimesh  # noqa: E402

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
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--source-mesh", type=Path, default=SOURCE)
    parser.add_argument("--p3-dir", type=Path, default=P3_DIR)
    parser.add_argument("--out-dir", type=Path, default=XPART_DIR)
    parser.add_argument(
        "--only-parts",
        nargs="*",
        default=None,
        help="Optional PART_XXX ids (or integers). If set, only generate these parts.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip parts that already have complete_part_*.obj under out-dir.",
    )
    args = parser.parse_args()

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    (CASE / "artifacts").mkdir(parents=True, exist_ok=True)

    meta = json.loads((args.p3_dir / "part_metadata.json").read_text())
    parts = sorted(meta["parts"], key=lambda p: int(p["part_id"]))
    only_ids = None
    if args.only_parts is not None:
        only_ids = set()
        for tok in args.only_parts:
            s = str(tok).strip().upper().replace("PART_", "")
            only_ids.add(int(s))
        parts = [p for p in parts if int(p["part_id"]) in only_ids]
    if args.skip_existing:
        kept_parts = []
        for p in parts:
            pid = int(p["part_id"])
            complete = out / f"PART_{pid:03d}" / f"complete_part_{pid:03d}.obj"
            if complete.is_file() and complete.stat().st_size > 0:
                continue
            kept_parts.append(p)
        parts = kept_parts
    print(f"[xpart] frozen P3 parts selected={len(parts)} only={sorted(only_ids) if only_ids else 'all'} skip_existing={args.skip_existing}", flush=True)
    if not parts:
        # Refresh manifest from on-disk PART_* dirs.
        by_id = {}
        for part_dir in sorted(out.glob("PART_*")):
            qa_path = part_dir / "qa.json"
            if qa_path.is_file():
                try:
                    by_id[part_dir.name] = json.loads(qa_path.read_text())
                except Exception:
                    continue
        merged = [by_id[k] for k in sorted(by_id.keys())]
        wt = sum(1 for r in merged if r.get("watertight"))
        summary = {
            "P3_REEXECUTED": False,
            "XPART_REEXECUTED": True,
            "condition_source": str(args.p3_dir),
            "XPART_ATTEMPTED_PARTS": 0,
            "XPART_SUCCESSFUL_PARTS": len(merged),
            "XPART_WATERTIGHT_PARTS": wt,
            "XPART_WATERTIGHT_RATE": wt / max(len(merged), 1),
            "PARTS_STILL_OPEN": sum(1 for r in merged if not r.get("watertight")),
            "runtime_seconds": 0.0,
            "octree_resolution": args.octree_resolution,
            "gpu": args.gpu,
            "parts": merged,
            "output_dir": str(out),
            "partial_run": True,
            "generated_this_run": [],
        }
        write_json(out / "manifest.json", summary)
        print("[xpart] nothing to generate", flush=True)
        print(json.dumps({k: v for k, v in summary.items() if k != "parts"}, indent=2))
        return 0

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
    transform = {
        "center": np.asarray(center).tolist(),
        "scale": float(scale),
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": True,
        "condition": f"frozen {args.p3_dir} bbox + part surface samples",
        "part_count_in": len(parts),
    }
    write_json(CASE / "artifacts/coordinate_transform.json", transform)

    aabb_list, surf_list, kept = [], [], []
    for row in parts:
        part_path = Path(row["path"])
        if not part_path.is_file():
            part_path = args.p3_dir / f"part_{int(row['part_id']):03d}.obj"
        part = trimesh.load(part_path, force="mesh", process=False)
        part.vertices = (np.asarray(part.vertices) - center) / scale
        if len(part.faces) < 10 or float(part.area) <= 0:
            continue
        aabb_list.append(np.stack([part.bounds[0], part.bounds[1]], axis=0))
        surf_list.append(sample_part(part, N_PART_POINTS, args.seed + int(row["part_id"])))
        kept.append(int(row["part_id"]))

    aabb = torch.from_numpy(np.stack(aabb_list, axis=0)).float().unsqueeze(0)
    part_surface = torch.stack(surf_list, dim=0).unsqueeze(0)
    write_json(
        CASE / "artifacts/condition_manifest.json",
        {
            "frozen_root": str(args.p3_dir),
            "kept_part_ids": kept,
            "dropped": [int(p["part_id"]) for p in parts if int(p["part_id"]) not in kept],
            "aabb_shape": list(aabb.shape),
            "part_surface_shape": list(part_surface.shape),
        },
    )

    pipeline.to(device="cuda", dtype=torch.float32)
    t0 = time.time()
    chunk = max(1, min(args.batch_size, 10))
    qa_rows, all_geoms = [], []
    for start in range(0, len(kept), chunk):
        sl = slice(start, start + chunk)
        ids = kept[sl]
        print(f"[xpart] chunk parts {ids[0]:03d}-{ids[-1]:03d} ({len(ids)})", flush=True)
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
            part_dir = out / part_id
            part_dir.mkdir(parents=True, exist_ok=True)
            world = geom.copy()
            world.vertices = np.asarray(world.vertices) * scale + center
            geom.export(part_dir / "generated_mesh_norm.obj")
            world.export(part_dir / "generated_mesh.obj")
            world.export(part_dir / f"complete_part_{src_id:03d}.obj")
            row = mesh_qa(world, part_id)
            row.update({"frozen_part_id": src_id, "selected": True, "chunk_start": start})
            write_json(part_dir / "qa.json", row)
            qa_rows.append(row)
            all_geoms.append(world)
        if aux:
            try:
                exploded = aux[2]
                if exploded is not None and getattr(exploded, "geometry", None):
                    exploded.export(CASE / "artifacts" / f"exploded_chunk_{start:03d}.glb")
            except Exception as exc:
                print(f"[xpart] skip exploded export chunk={start}: {exc}", flush=True)
        if not geoms:
            print(f"[xpart] chunk {ids} produced 0 meshes", flush=True)
        del obj_mesh, aux, geoms
        torch.cuda.empty_cache()

    if all_geoms:
        try:
            trimesh.Scene(all_geoms).export(CASE / "artifacts/xpart_assembly.glb")
        except Exception as exc:
            print(f"[xpart] skip assembly glb: {exc}", flush=True)

    # Merge with any previously successful parts when doing partial/skip-existing runs.
    by_id = {}
    old_manifest = out / "manifest.json"
    if old_manifest.is_file():
        try:
            for row in json.loads(old_manifest.read_text()).get("parts") or []:
                by_id[row["part_id"]] = row
        except Exception:
            pass
    for row in qa_rows:
        by_id[row["part_id"]] = row
    merged = [by_id[k] for k in sorted(by_id.keys())]
    # Also pick up on-disk parts that may lack manifest entries.
    for part_dir in sorted(out.glob("PART_*")):
        pid = part_dir.name
        if pid in by_id:
            continue
        qa_path = part_dir / "qa.json"
        if qa_path.is_file():
            try:
                by_id[pid] = json.loads(qa_path.read_text())
            except Exception:
                continue
    merged = [by_id[k] for k in sorted(by_id.keys())]
    wt = sum(1 for r in merged if r.get("watertight"))
    summary = {
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": True,
        "condition_source": str(args.p3_dir),
        "XPART_ATTEMPTED_PARTS": len(kept) if kept else len(merged),
        "XPART_SUCCESSFUL_PARTS": len(merged),
        "XPART_WATERTIGHT_PARTS": wt,
        "XPART_WATERTIGHT_RATE": wt / max(len(merged), 1),
        "PARTS_STILL_OPEN": sum(1 for r in merged if not r.get("watertight")),
        "runtime_seconds": time.time() - t0,
        "octree_resolution": args.octree_resolution,
        "gpu": args.gpu,
        "parts": merged,
        "output_dir": str(out),
        "partial_run": bool(only_ids is not None or args.skip_existing),
        "generated_this_run": [r["part_id"] for r in qa_rows],
    }
    write_json(out / "manifest.json", summary)
    write_json(CASE / "artifacts/xpart_summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "parts"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
