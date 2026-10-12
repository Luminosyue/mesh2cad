#!/usr/bin/env python3
"""Explicit P3-SAM adapter used only for the frozen Gate-1 D case."""

from __future__ import annotations

import argparse
import abc
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


P3_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/Hunyuan3D-Part/P3-SAM")
P3_CHECKPOINT = P3_ROOT / "weights" / "p3sam.safetensors"
SONATA_CHECKPOINT = Path.home() / ".cache" / "sonata" / "sonata.pth"


class PartSegmenter(abc.ABC):
    @abc.abstractmethod
    def segment(self, mesh_path: Path, output_dir: Path) -> dict[str, Any]:
        """Return triangle_part_id, part_confidence, and metadata."""


def _load_source_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(str(path), force="mesh", process=False)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise TypeError(f"P3 source did not resolve to Trimesh: {type(loaded)!r}")
    return trimesh.Trimesh(
        vertices=np.asarray(loaded.vertices).copy(),
        faces=np.asarray(loaded.faces).copy(),
        process=False,
    )


def _contiguous_labels(labels: np.ndarray) -> np.ndarray:
    unique = [int(v) for v in np.unique(labels) if int(v) >= 0]
    mapping = {old: new for new, old in enumerate(unique)}
    result = np.full(labels.shape, -1, dtype=np.int64)
    for old, new in mapping.items():
        result[labels == old] = new
    return result


def _export_part(mesh: trimesh.Trimesh, face_mask: np.ndarray, path: Path) -> dict[str, Any]:
    face_indices = np.flatnonzero(face_mask)
    selected_faces = np.asarray(mesh.faces)[face_indices]
    vertex_ids, inverse = np.unique(selected_faces.reshape(-1), return_inverse=True)
    part = trimesh.Trimesh(
        vertices=np.asarray(mesh.vertices)[vertex_ids],
        faces=inverse.reshape(-1, 3),
        process=False,
    )
    part.export(path)
    return {
        "path": str(path),
        "triangle_count": int(len(part.faces)),
        "vertex_count": int(len(part.vertices)),
        "source_triangle_indices_min": int(face_indices.min()),
        "source_triangle_indices_max": int(face_indices.max()),
        "bbox_min": np.asarray(part.bounds[0]).tolist(),
        "bbox_max": np.asarray(part.bounds[1]).tolist(),
        "surface_area": float(part.area),
        "semantic": None,
    }


def _render_segmentation(mesh: trimesh.Trimesh, labels: np.ndarray, output: Path) -> None:
    face_count = len(mesh.faces)
    sampled = np.linspace(0, face_count - 1, min(face_count, 24000), dtype=np.int64)
    triangles = np.asarray(mesh.vertices)[np.asarray(mesh.faces)[sampled]]
    palette = plt.get_cmap("tab20")
    colors = np.asarray([palette(int(v) % 20) if v >= 0 else (0.2, 0.2, 0.2, 1.0) for v in labels[sampled]])
    fig = plt.figure(figsize=(7, 7), dpi=120, facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    collection = Poly3DCollection(triangles, linewidths=0.02)
    collection.set_facecolor(colors)
    collection.set_edgecolor((0.03, 0.03, 0.03, 0.08))
    ax.add_collection3d(collection)
    bounds = np.asarray(mesh.bounds, dtype=float)
    center = bounds.mean(axis=0)
    half = max(float((bounds[1] - bounds[0]).max()) * 0.58, 1e-9)
    ax.set_xlim(center[0] - half, center[0] + half)
    ax.set_ylim(center[1] - half, center[1] + half)
    ax.set_zlim(center[2] - half, center[2] + half)
    ax.view_init(elev=24, azim=38)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


class P3SAMAdapter(PartSegmenter):
    """Thin adapter over the official local AutoMask API; no fallback exists."""

    def __init__(self, checkpoint: Path = P3_CHECKPOINT, prompt_bs: int = 32):
        self.checkpoint = checkpoint
        self.prompt_bs = prompt_bs

    def availability(self) -> dict[str, Any]:
        return {
            "repo": str(P3_ROOT),
            "checkpoint": str(self.checkpoint),
            "repo_available": (P3_ROOT / "demo" / "auto_mask.py").is_file(),
            "checkpoint_available": self.checkpoint.is_file(),
            "sonata_available": SONATA_CHECKPOINT.is_file(),
            "inference_environment": "hunyuan",
            "official_api": "demo.auto_mask.AutoMask.predict_aabb",
            "connected_components_fallback": False,
        }

    def segment(self, mesh_path: Path, output_dir: Path) -> dict[str, Any]:
        availability = self.availability()
        if not all(availability[k] for k in ("repo_available", "checkpoint_available", "sonata_available")):
            raise RuntimeError(f"P3 assets unavailable: {availability}")
        sys.path.insert(0, str(P3_ROOT))
        sys.path.insert(0, str(P3_ROOT / "demo"))
        from auto_mask import AutoMask, set_seed  # type: ignore

        output_dir.mkdir(parents=True, exist_ok=True)
        mesh = _load_source_mesh(mesh_path)
        original_vertices = np.asarray(mesh.vertices).copy()
        original_faces = np.asarray(mesh.faces).copy()
        set_seed(42)
        started = time.time()
        model = AutoMask(str(self.checkpoint), point_num=100000, prompt_num=400, threshold=0.95, post_process=True)
        _, labels, returned = model.predict_aabb(
            mesh,
            point_num=100000,
            prompt_num=400,
            threshold=0.95,
            post_process=True,
            save_path=None,
            save_mid_res=False,
            show_info=True,
            clean_mesh_flag=False,
            seed=42,
            is_parallel=False,
            prompt_bs=self.prompt_bs,
        )
        labels = _contiguous_labels(np.asarray(labels, dtype=np.int64))
        if labels.shape != (len(original_faces),):
            raise RuntimeError(f"P3 label shape {labels.shape} != source triangle count {len(original_faces)}")
        if not np.array_equal(np.asarray(returned.faces), original_faces):
            raise RuntimeError("P3 changed source face order; triangle mapping is unsafe")
        if not np.array_equal(np.asarray(returned.vertices), original_vertices):
            raise RuntimeError("P3 changed source vertices; triangle mapping is unsafe")
        if np.any(labels < 0):
            raise RuntimeError(f"P3 returned {int(np.sum(labels < 0))} unassigned source triangles")

        np.save(output_dir / "triangle_part_id.npy", labels, allow_pickle=False)
        unique = np.unique(labels)
        part_rows = []
        for part_id in unique:
            path = output_dir / f"part_{int(part_id):03d}.obj"
            row = _export_part(mesh, labels == part_id, path)
            row["part_id"] = int(part_id)
            row["confidence"] = None
            part_rows.append(row)
        _render_segmentation(mesh, labels, output_dir / "p3_part_segmentation.png")
        metadata = {
            "method": "P3-SAM",
            "adapter": "P3SAMAdapter",
            "official_api": "AutoMask.predict_aabb",
            "source_mesh": str(mesh_path),
            "source_triangle_count": int(len(original_faces)),
            "triangle_mapping": "array_index_is_source_triangle_index",
            "num_parts": int(len(unique)),
            "part_confidence": None,
            "parts": sorted(part_rows, key=lambda item: item["part_id"]),
            "runtime_seconds": time.time() - started,
            "seed": 42,
            "point_num": 100000,
            "prompt_num": 400,
            "threshold": 0.95,
            "post_process": True,
            "one_p3_level_only": True,
            "connected_components_used_as_p3": False,
            "provenance": {
                "repo": str(P3_ROOT),
                "checkpoint": str(self.checkpoint),
                "sonata_checkpoint": str(SONATA_CHECKPOINT),
                "environment": "hunyuan",
            },
        }
        (output_dir / "part_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        return {"triangle_part_id": labels, "part_confidence": None, "metadata": metadata}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mesh_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--prompt-bs", type=int, default=32)
    args = parser.parse_args()
    result = P3SAMAdapter(prompt_bs=args.prompt_bs).segment(args.mesh_path, args.output_dir)
    print(f"P3_PARTS={result['metadata']['num_parts']}")
    print("CONNECTED_COMPONENTS_USED_AS_P3=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
