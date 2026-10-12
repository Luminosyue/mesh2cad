#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np
import trimesh
from PIL import Image, ImageDraw

P3_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/Hunyuan3D-Part/P3-SAM")
P3_CHECKPOINT = P3_ROOT / "weights/p3sam.safetensors"
SONATA_CHECKPOINT = Path.home() / ".cache/sonata/sonata.pth"


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise TypeError(f"Source did not resolve to a mesh: {type(mesh)!r}")
    return trimesh.Trimesh(vertices=np.asarray(mesh.vertices).copy(), faces=np.asarray(mesh.faces).copy(), process=False)


def contiguous(labels: np.ndarray) -> np.ndarray:
    vals = [int(v) for v in np.unique(labels) if int(v) >= 0]
    mapping = {old: new for new, old in enumerate(vals)}
    out = np.full(labels.shape, -1, dtype=np.int64)
    for old, new in mapping.items():
        out[labels == old] = new
    return out


def export_part(mesh: trimesh.Trimesh, mask: np.ndarray, path: Path):
    face_idx = np.flatnonzero(mask)
    faces = np.asarray(mesh.faces)[face_idx]
    vertex_ids, inverse = np.unique(faces.reshape(-1), return_inverse=True)
    part = trimesh.Trimesh(vertices=np.asarray(mesh.vertices)[vertex_ids], faces=inverse.reshape(-1, 3), process=False)
    part.export(path)
    return {
        "path": str(path),
        "triangle_count": int(len(part.faces)),
        "vertex_count": int(len(part.vertices)),
        "source_triangle_indices_min": int(face_idx.min()),
        "source_triangle_indices_max": int(face_idx.max()),
        "bbox_min": np.asarray(part.bounds[0]).tolist(),
        "bbox_max": np.asarray(part.bounds[1]).tolist(),
        "surface_area": float(part.area),
    }


def render_2d(mesh: trimesh.Trimesh, labels: np.ndarray, path: Path):
    image = Image.new("RGB", (900, 900), "white")
    draw = ImageDraw.Draw(image)
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    xy = vertices[:, [0, 1]]
    lo = xy.min(axis=0)
    span = np.maximum(xy.max(axis=0) - lo, 1e-9)
    xy = (xy - lo) / span
    palette = [
        (137, 190, 219), (244, 181, 123), (167, 211, 151), (215, 148, 167),
        (188, 170, 218), (255, 224, 130), (141, 211, 199), (190, 186, 218),
        (220, 160, 160), (160, 205, 180), (200, 200, 200),
    ]
    idx = np.linspace(0, len(faces) - 1, min(len(faces), 30000), dtype=int)
    depth = vertices[faces[idx]].mean(axis=1)[:, 2]
    for _, face_id in sorted(zip(depth, idx)):
        poly = [(int(xy[v, 0] * 820 + 40), int(860 - xy[v, 1] * 820)) for v in faces[face_id]]
        draw.polygon(poly, fill=palette[int(labels[face_id]) % len(palette)])
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mesh_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--prompt-bs", type=int, default=32)
    parser.add_argument("--point-num", type=int, default=100000)
    parser.add_argument("--prompt-num", type=int, default=400)
    args = parser.parse_args()
    availability = {
        "repo": str(P3_ROOT),
        "checkpoint": str(P3_CHECKPOINT),
        "repo_available": (P3_ROOT / "demo/auto_mask.py").is_file(),
        "checkpoint_available": P3_CHECKPOINT.is_file(),
        "sonata_available": SONATA_CHECKPOINT.is_file(),
        "official_api": "demo.auto_mask.AutoMask.predict_aabb",
    }
    if not all(availability[k] for k in ("repo_available", "checkpoint_available", "sonata_available")):
        raise RuntimeError(f"P3 assets unavailable: {availability}")
    sys.path.insert(0, str(P3_ROOT))
    sys.path.insert(0, str(P3_ROOT / "demo"))
    try:
        import numba  # noqa: F401
    except ImportError:
        # P3 uses numba only to JIT one adjacency-array builder. The plain
        # NumPy implementation is functionally identical and keeps official
        # AutoMask/model inference intact when numba is unavailable.
        numba_compat = types.ModuleType("numba")

        def njit(function=None, *args, **kwargs):
            if function is None:
                return lambda wrapped: wrapped
            return function

        numba_compat.njit = njit
        sys.modules["numba"] = numba_compat
    from auto_mask import AutoMask, set_seed  # type: ignore

    args.output_dir.mkdir(parents=True, exist_ok=True)
    mesh = load_mesh(args.mesh_path)
    original_vertices = np.asarray(mesh.vertices).copy()
    original_faces = np.asarray(mesh.faces).copy()
    started = time.time()
    set_seed(42)
    model = AutoMask(
        str(P3_CHECKPOINT),
        point_num=args.point_num,
        prompt_num=args.prompt_num,
        threshold=0.95,
        post_process=True,
    )
    _, labels, returned = model.predict_aabb(
        mesh,
        point_num=args.point_num,
        prompt_num=args.prompt_num,
        threshold=0.95,
        post_process=True,
        save_path=None,
        save_mid_res=False,
        show_info=True,
        clean_mesh_flag=False,
        seed=42,
        is_parallel=False,
        prompt_bs=args.prompt_bs,
    )
    labels = contiguous(np.asarray(labels, dtype=np.int64))
    if labels.shape != (len(original_faces),):
        raise RuntimeError(f"P3 label shape {labels.shape} != source triangle count {len(original_faces)}")
    if not np.array_equal(np.asarray(returned.faces), original_faces):
        raise RuntimeError("P3 changed source face order")
    if not np.array_equal(np.asarray(returned.vertices), original_vertices):
        raise RuntimeError("P3 changed source vertices")
    if np.any(labels < 0):
        raise RuntimeError("P3 returned unassigned triangles")
    np.save(args.output_dir / "triangle_part_id.npy", labels, allow_pickle=False)
    parts = []
    for part_id in np.unique(labels):
        row = export_part(mesh, labels == part_id, args.output_dir / f"part_{int(part_id):03d}.obj")
        row["part_id"] = int(part_id)
        parts.append(row)
    render_2d(mesh, labels, args.output_dir / "p3_part_segmentation.png")
    meta = {
        "method": "P3-SAM",
        "P3_RAN": True,
        "source_mesh": str(args.mesh_path),
        "source_triangle_count": int(len(original_faces)),
        "triangle_mapping": "array_index_is_source_triangle_index",
        "num_parts": int(len(parts)),
        "parts": sorted(parts, key=lambda x: x["part_id"]),
        "runtime_seconds": time.time() - started,
        "seed": 42,
        "point_num": int(args.point_num),
        "prompt_num": int(args.prompt_num),
        "prompt_bs": int(args.prompt_bs),
        "availability": availability,
        "connected_components_used_as_p3": False,
        "numba_jit_available": "numba" in sys.modules and getattr(sys.modules["numba"], "__file__", None) is not None,
        "numba_identity_fallback": getattr(sys.modules.get("numba"), "__file__", None) is None,
        "matplotlib_3d_render_disabled_for_environment": True,
    }
    (args.output_dir / "part_metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({
        "P3_RAN": True,
        "P3_PARTS": meta["num_parts"],
        "point_num": meta["point_num"],
        "prompt_num": meta["prompt_num"],
        "runtime_seconds": meta["runtime_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
