#!/usr/bin/env python3
"""Shared plumbing for separate_edge_tokens_v1 probes, training and ablations."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = ROOT / "SpatialLM"
DEFAULT_MODEL_PATH = SPATIALLM_ROOT / "models/SpatialLM1.1-Llama-1B"
CACHE_DIR = ROOT / "cad_spatial_dataset/DeepCAD/separate_edge_tokens_v1"
TRAIN_DIR = ROOT / "cad_spatial_dataset/DeepCAD/train"
OUT_ROOT = ROOT / "ours3/separate_edge_tokens_v1"

EXPERIMENT = "separate_edge_tokens_v1"

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""


def ensure_spatiallm_importable() -> None:
    for p in (str(SPATIALLM_ROOT), str(ROOT / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)


def make_plugin(separate_edge: bool = True, num_bins: int = 1280):
    """A CAD mm_plugin instance usable outside the Trainer."""
    ensure_spatiallm_importable()
    from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin

    return get_cad_mm_plugin(
        point_token="<|point_pad|>",
        use_edge_score=False,
        separate_edge_tokens=separate_edge,
        num_bins=num_bins,
    )


def load_geometry(sample_id: str, plugin=None, cache_dir: Path = CACHE_DIR):
    """Return (surface_tensor, edge_tensor) as (1, N, 9) float32 tensors."""
    plugin = plugin or make_plugin(separate_edge=True)
    surface_npy = Path(cache_dir) / sample_id / "surface_points.npy"
    surface, edge = plugin._load_cad_separate_edge(str(surface_npy))
    return (
        torch.as_tensor(surface[None, ...], dtype=torch.float32),
        torch.as_tensor(edge[None, ...], dtype=torch.float32),
    )


def load_model(
    checkpoint: Path | str = DEFAULT_MODEL_PATH,
    separate_edge: bool = True,
    device: str = "cuda",
    dtype: torch.dtype = torch.float32,
    freeze_sonata: bool = True,
):
    """Load SpatialLM and, if requested, attach the independent edge projector."""
    ensure_spatiallm_importable()
    import spatiallm  # noqa: F401  registers spatiallm_llama
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from spatiallm.tuner.framework.patcher import _attach_edge_projector

    model = AutoModelForCausalLM.from_pretrained(str(checkpoint), torch_dtype=dtype)
    if separate_edge and getattr(model, "edge_proj", None) is None:
        _attach_edge_projector(model)

    stem = model.point_backbone.embedding.stem.linear
    if separate_edge and stem.in_features != 6:
        raise ValueError(
            f"separate_edge_tokens_v1 needs a 6-channel stem, got {stem.in_features}"
        )

    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    if freeze_sonata:
        for p in model.point_backbone.parameters():
            p.requires_grad_(False)
    tokenizer = AutoTokenizer.from_pretrained(str(checkpoint))
    return model, tokenizer


def set_deterministic_serialization(point_backbone) -> None:
    """Freeze Sonata's random space-filling-curve order so A/B runs are comparable."""
    for module in point_backbone.modules():
        if hasattr(module, "shuffle_orders"):
            module.shuffle_orders = False


def build_prompt(separate_edge: bool = True) -> str:
    ensure_spatiallm_importable()
    from spatiallm.tuner.data.mm_plugin import (
        EDGE_E_TOKEN,
        EDGE_PAD_TOKEN,
        EDGE_S_TOKEN,
        POINT_E_TOKEN,
        POINT_S_TOKEN,
    )

    markers = f"{POINT_S_TOKEN}<|point_pad|>{POINT_E_TOKEN}"
    if separate_edge:
        markers += f"{EDGE_S_TOKEN}{EDGE_PAD_TOKEN}{EDGE_E_TOKEN}"
    return f"{markers}\n{CAD_INSTRUCTION.strip()}"


def build_batch(
    tokenizer,
    surface: torch.Tensor,
    edge: torch.Tensor | None,
    target_dsl: str | None,
    device: str,
    separate_edge: bool = True,
):
    """Assemble one training/eval batch of size 1.

    Labels mask the whole prompt; only the CAD target contributes to the loss.
    Geometry regions are additionally masked inside the model.
    """
    prompt = build_prompt(separate_edge=separate_edge)
    conversation = [{"role": "user", "content": prompt}]
    prompt_ids = tokenizer.apply_chat_template(
        conversation, add_generation_prompt=True, return_tensors="pt"
    )[0]

    if target_dsl is None:
        input_ids = prompt_ids
        labels = torch.full_like(input_ids, -100)
    else:
        target_ids = tokenizer(
            target_dsl, add_special_tokens=False, return_tensors="pt"
        ).input_ids[0]
        eos = torch.tensor([tokenizer.eos_token_id], dtype=target_ids.dtype)
        target_ids = torch.cat([target_ids, eos])
        input_ids = torch.cat([prompt_ids, target_ids])
        labels = torch.cat([torch.full_like(prompt_ids, -100), target_ids])

    batch = {
        "input_ids": input_ids[None, :].to(device),
        "attention_mask": torch.ones_like(input_ids)[None, :].to(device),
        "labels": labels[None, :].to(device),
        "point_clouds": surface.to(device),
    }
    if separate_edge and edge is not None:
        batch["edge_clouds"] = edge.to(device)
    return batch


def read_dsl(sample_id: str, train_dir: Path = TRAIN_DIR) -> str:
    path = Path(train_dir) / sample_id / "program_canonical.dsl"
    text = path.read_text(encoding="utf-8").strip()
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    return "\n".join(lines).strip() + "\n"


def cached_sample_ids(cache_dir: Path = CACHE_DIR) -> list[str]:
    return sorted(
        p.name for p in Path(cache_dir).iterdir() if p.is_dir() and (p / "edge_points.npy").is_file()
    )


def zero_edge_like(edge: torch.Tensor) -> torch.Tensor:
    """Zero-control: keep the voxel lattice, remove all edge geometry content.

    grid_coord (cols 0-2) is preserved so the token count stays identical and the
    comparison isolates the geometry features rather than the sequence length.
    """
    out = edge.clone()
    out[..., 3:] = 0.0
    return out


def corrupt_edge(edge: torch.Tensor, seed: int = 0) -> torch.Tensor:
    """Spatially corrupt an edge cloud while preserving its value histogram.

    Sonata is permutation invariant over rows, so shuffling row order alone
    changes nothing. Instead the xyz/grid columns are permuted independently of
    the normals, which destroys the geometric structure while keeping every
    marginal distribution intact.
    """
    g = torch.Generator().manual_seed(seed)
    out = edge.clone()
    n = out.shape[1]
    perm = torch.randperm(n, generator=g)
    # Break the xyz <-> normal correspondence and scramble spatial layout.
    out[0, :, 6:9] = out[0, perm, 6:9]
    perm2 = torch.randperm(n, generator=g)
    out[0, :, 0:6] = out[0, perm2, 0:6]
    return out


def json_dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def pick_gpu(min_free_mb: int = 12000) -> str:
    """Return the CUDA index with most free memory, as a string."""
    import subprocess

    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=index,memory.free", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
    )
    best, best_free = None, -1
    for line in out.stdout.strip().splitlines():
        idx, free = [x.strip() for x in line.split(",")]
        if int(free) > best_free:
            best, best_free = idx, int(free)
    if best is None or best_free < min_free_mb:
        raise RuntimeError(f"no GPU with >= {min_free_mb}MB free (best={best_free}MB)")
    return best
