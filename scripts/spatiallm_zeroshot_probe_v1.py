#!/usr/bin/env python3
"""Zero-shot probe of a pretrained SpatialLM on mechanical CAD parts.

No training. A cad_spatial_dataset part is pushed through the frozen SpatialLM
point encoder and LLM under several feature variants and several prompts, and
the generated text is scored for CAD vocabulary versus indoor-scene vocabulary.

Feature variants (all share the same xyz, so only the feature channels differ):

    A_rgb_zeros     [xyz | 0,0,0]                6ch, pretrained stem untouched
    A2_normal       [xyz | nx,ny,nz]             6ch, normals in the colour slots
    B_ours          [xyz | nx,ny,nz | edge]      7ch, stem widened for edge_score
    B0_ours_zero    [xyz | nx,ny,nz | -1]        7ch, edge channel carries nothing
    C_shuffled_edge [xyz | nx,ny,nz | perm(edge)] 7ch, right histogram, wrong geometry

A_rgb_zeros is the "SpatialLM as shipped" baseline (xyz + zeros). A2_normal
isolates how much of any gain comes from normals alone. Widening the stem is
itself an untrained perturbation, so B_ours must be read against B0_ours_zero
(same widened stem, no edge information) and C_shuffled_edge (same edge
histogram, scrambled across the surface) rather than against the 6ch variants.

Prompts:

    room        the original SpatialLM task, kept as a domain reference
    structure   describe the mechanical structure (experiment 1 / 2)
    cad_dsl     emit a CAD construction sequence (experiment 3)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SPATIALLM_ROOT = ROOT / "SpatialLM"
MODEL_PATHS = {
    "qwen0.5b": Path("/data/share/zihao_share/models/SpatialLM1.1-Qwen-0.5B"),
    "llama1b": SPATIALLM_ROOT / "models/SpatialLM1.1-Llama-1B",
}
DEFAULT_OUT = ROOT / "ours3/spatiallm_zeroshot_probe_v1"

# SpatialLM voxelizes at 32/num_bins metres for room-scale scans. A CAD part
# spans ~0.3 units, so without rescaling the whole part collapses into a couple
# of voxels and the encoder emits one or two tokens.
TARGET_DIAGONAL = 6.0
PRETRAINED_COLOR_COLUMNS = (3, 4, 5)


# ---------------------------------------------------------------- prompts ----

STRUCTURE_PROMPT = """You are given a 3D point cloud of a mechanical part.
Describe the object structure.
Identify:
- primitive shapes
- symmetry
- circular features
- holes
- sharp boundaries
"""

CAD_DSL_PROMPT = """You are given a 3D point cloud of a mechanical part.
Generate CAD construction sequence.

Allowed operations:
Sketch
Circle
Extrude
Revolve
Cut

Output only DSL.
"""

ROOM_PROMPT_TASK = "Detect walls, doors, windows, boxes."


def build_prompt(kind: str, code_template: str) -> str:
    head = "<|point_start|><|point_pad|><|point_end|>"
    if kind == "room":
        return f"{head}{ROOM_PROMPT_TASK} The reference code is as followed: {code_template}"
    if kind == "structure":
        return head + STRUCTURE_PROMPT
    if kind == "cad_dsl":
        return head + CAD_DSL_PROMPT
    raise ValueError(f"unknown prompt kind: {kind}")


# ---------------------------------------------------------------- scoring ----

CAD_LEXICON = {
    "cylinder": ("cylinder", "cylindrical", "cylindric"),
    "circle": ("circle", "circular", "circumference", "arc", "round", "rim", "disc", "disk"),
    "hole": ("hole", "bore", "bored", "counterbore", "through-hole", "aperture", "opening"),
    "edge": ("edge", "edges", "sharp", "boundary", "boundaries", "fillet", "chamfer"),
    "symmetry": ("symmetry", "symmetric", "symmetrical", "rotational", "axisymmetric", "revolve", "revolution", "axis"),
    "plane": ("planar", "plane", "flat", "face", "faces", "flange"),
    "mech": ("mechanical", "part", "component", "shaft", "hub", "wheel", "gear", "bearing", "ring", "annulus"),
    "cad_op": ("sketch", "extrude", "revolve", "cut", "loft", "fillet", "boolean"),
}
ROOM_LEXICON = (
    "wall", "door", "window", "bbox", "room", "floor", "ceiling", "sofa", "chair",
    "bed", "table", "cabinet", "curtain", "lamp", "toilet", "kitchen",
)


def score_text(text: str) -> dict:
    low = text.lower()
    words = set(re.findall(r"[a-z][a-z\-]+", low))
    cad_hits = {}
    for bucket, terms in CAD_LEXICON.items():
        found = sorted(t for t in terms if t in words or t in low)
        cad_hits[bucket] = found
    room_hits = sorted(t for t in ROOM_LEXICON if t in low)
    return {
        "cad_buckets_hit": sorted(b for b, v in cad_hits.items() if v),
        "cad_bucket_count": sum(1 for v in cad_hits.values() if v),
        "cad_hits": {k: v for k, v in cad_hits.items() if v},
        "room_leak_terms": room_hits,
        "room_leak_count": len(room_hits),
        "chars": len(text),
        "looks_like_room_layout": bool(re.search(r"\b(wall|door|window|bbox)_\d+\s*=", low)),
    }


# ---------------------------------------------------------- preprocessing ----


def _ensure_importable() -> None:
    root = str(SPATIALLM_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


@dataclass
class Variant:
    name: str
    feat_dim: int  # channels handed to Sonata, including xyz
    tensor: torch.Tensor
    num_voxels: int
    note: str
    stats: dict = field(default_factory=dict)


def preprocess(points: np.ndarray, extra: np.ndarray, num_bins: int) -> tuple[torch.Tensor, dict]:
    """Voxelize xyz + K extra channels into the (1, N, 6+K) tensor the encoder reads."""
    _ensure_importable()
    from spatiallm import Layout
    from spatiallm.pcd.transform import Compose

    grid_size = Layout.get_grid_size(num_bins)
    coord = points.astype(np.float64).copy()
    diagonal = float(np.linalg.norm(coord.max(0) - coord.min(0)))
    scale = TARGET_DIAGONAL / diagonal
    coord *= scale

    transform = Compose(
        [
            dict(type="PositiveShift"),
            dict(
                type="GridSample",
                grid_size=grid_size,
                hash_type="fnv",
                mode="test",
                keys=("coord", "extra"),
                return_grid_coord=True,
                max_grid_coord=num_bins,
            ),
        ]
    )
    sampled = transform(
        {"name": "cad_part", "coord": coord, "extra": extra.astype(np.float64).copy()}
    )
    grid_coord = np.asarray(sampled["grid_coord"], dtype=np.float32)
    xyz = np.asarray(sampled["coord"], dtype=np.float32)
    feats = np.asarray(sampled["extra"], dtype=np.float32).reshape(len(xyz), -1)
    stacked = np.concatenate([grid_coord, xyz, feats], axis=1)
    stats = {
        "num_points_in": int(points.shape[0]),
        "num_voxels": int(stacked.shape[0]),
        "grid_size_m": float(grid_size),
        "scale": float(scale),
        "bbox_diagonal_original": diagonal,
    }
    return torch.as_tensor(stacked[None, ...], dtype=torch.float32), stats


def build_variants(part_dir: Path, num_bins: int, only: list[str] | None, seed: int = 0) -> list[Variant]:
    points = np.load(part_dir / "points.npy").astype(np.float64)
    normals = np.load(part_dir / "normals.npy").astype(np.float64)
    edge = np.load(part_dir / "edge_score.npy").astype(np.float64)

    # NormalizeColor maps rgb 0..255 onto [-1, 1], so the pretrained stem expects
    # its non-xyz columns in [-1, 1]. Normals already live there; edge_score is
    # in [0, 1] and is remapped to match.
    edge_signed = 2.0 * edge - 1.0
    zeros3 = np.zeros_like(normals)

    specs = [
        ("A_rgb_zeros", zeros3, "xyz + zeros (SpatialLM as shipped, no colour)"),
        ("A2_normal", normals, "xyz + normal in the colour slots (no edge channel)"),
        ("B_ours", np.concatenate([normals, edge_signed[:, None]], axis=1), "xyz + normal + edge_score"),
        (
            "B0_ours_zero_edge",
            np.concatenate([normals, np.full_like(edge_signed, -1.0)[:, None]], axis=1),
            "xyz + normal + constant edge (negative control for the 7ch path)",
        ),
        (
            "C_shuffled_edge",
            np.concatenate(
                [normals, edge_signed[np.random.default_rng(seed).permutation(edge_signed.shape[0])][:, None]],
                axis=1,
            ),
            "xyz + normal + permuted edge (same histogram, wrong geometry)",
        ),
    ]
    variants = []
    for name, extra, note in specs:
        if only and name not in only:
            continue
        tensor, stats = preprocess(points, extra, num_bins)
        variants.append(
            Variant(
                name=name,
                feat_dim=3 + extra.shape[1],
                tensor=tensor,
                num_voxels=stats["num_voxels"],
                note=note,
                stats=stats,
            )
        )
    return variants


# ------------------------------------------------------------------ model ----


def widen_stem(stem: nn.Linear, out_channels: int) -> nn.Linear:
    """Widen the Sonata embedding stem, seeding new columns from the colour columns.

    The pretrained stem takes [x, y, z, r, g, b]. Extra feature channels get a
    column initialized to the mean of the three colour columns so they enter at
    the magnitude the encoder already expects from a photometric channel; a zero
    column would make the new channel unable to change any token.
    """
    weight = stem.weight.data
    extra = out_channels - stem.in_features
    if extra <= 0:
        raise ValueError(f"stem already has {stem.in_features} inputs, cannot widen to {out_channels}")
    seed = weight[:, list(PRETRAINED_COLOR_COLUMNS)].mean(dim=1, keepdim=True)
    widened = nn.Linear(out_channels, stem.out_features, bias=stem.bias is not None)
    widened = widened.to(device=weight.device, dtype=weight.dtype)
    with torch.no_grad():
        widened.weight.copy_(torch.cat([weight, seed.repeat(1, extra)], dim=1))
        if stem.bias is not None:
            widened.bias.copy_(stem.bias.data)
    return widened


def freeze_serialization(point_backbone: nn.Module) -> None:
    """Sonata picks a space-filling-curve order at random per block; pin it so an
    A/B comparison is not contaminated by encoder nondeterminism."""
    for module in point_backbone.modules():
        if hasattr(module, "shuffle_orders"):
            module.shuffle_orders = False


def load_model(model_path: Path, dtype: torch.dtype, device: str):
    _ensure_importable()
    import spatiallm  # noqa: F401  registers the spatiallm_* architectures
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForCausalLM.from_pretrained(str(model_path), torch_dtype=dtype)
    freeze_serialization(model.point_backbone)
    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    model.eval()
    return model, tokenizer


def set_in_channels(model, feat_dim: int, base_stem_state: dict) -> None:
    """Reset the embedding stem to the pretrained 6ch weights, then widen if needed."""
    stem = model.point_backbone.embedding.stem.linear
    pretrained = nn.Linear(6, base_stem_state["weight"].shape[0], bias="bias" in base_stem_state)
    pretrained = pretrained.to(device=stem.weight.device, dtype=base_stem_state["weight"].dtype)
    with torch.no_grad():
        pretrained.weight.copy_(base_stem_state["weight"])
        if "bias" in base_stem_state:
            pretrained.bias.copy_(base_stem_state["bias"])
    if feat_dim > 6:
        pretrained = widen_stem(pretrained, feat_dim)
    model.point_backbone.embedding.stem.linear = pretrained
    model.point_backbone.embedding.in_channels = feat_dim
    model.config.point_config["in_channels"] = feat_dim
    model.set_point_backbone_dtype(torch.float32)


@torch.inference_mode()
def generate(model, tokenizer, prompt: str, point_cloud: torch.Tensor, max_new_tokens: int,
             temperature: float, seed: int) -> str:
    from transformers import set_seed

    if model.config.model_type == "spatiallm_qwen":
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    else:
        conversation = [{"role": "user", "content": prompt}]

    input_ids = tokenizer.apply_chat_template(
        conversation, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    do_sample = temperature > 0
    if do_sample:
        set_seed(seed)
    kwargs = dict(
        input_ids=input_ids,
        point_clouds=point_cloud.to(model.device),
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        use_cache=True,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
    )
    if do_sample:
        kwargs.update(temperature=temperature, top_p=0.95, top_k=10)
    out = model.generate(**kwargs)
    # generate() returns prompt + completion; the prompt grew by the point tokens
    # so slice by decoding the full sequence minus the known prompt length.
    completion = out[0][input_ids.shape[1]:]
    return tokenizer.decode(completion, skip_special_tokens=True)


# ------------------------------------------------------------------- main ----


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part-dir", type=Path, default=ROOT / "cad_spatial_dataset/PART_005")
    parser.add_argument("--model", default="qwen0.5b", choices=sorted(MODEL_PATHS))
    parser.add_argument("--prompts", nargs="+", default=["structure", "cad_dsl", "room"],
                        choices=["structure", "cad_dsl", "room"])
    parser.add_argument("--variants", nargs="+", default=None,
                        help="subset of A_rgb_zeros A2_normal B_ours B0_ours_zero_edge C_shuffled_edge")
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--temperature", type=float, default=0.0, help="0 = greedy (deterministic)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float32"])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    part_dir = args.part_dir.resolve()
    part_id = part_dir.name
    model_path = MODEL_PATHS[args.model]
    out_dir = args.out / part_id / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(model_path, getattr(torch, args.dtype), "cuda")
    num_bins = model.config.point_config["num_bins"]
    stem = model.point_backbone.embedding.stem.linear
    base_stem_state = {"weight": stem.weight.data.clone()}
    if stem.bias is not None:
        base_stem_state["bias"] = stem.bias.data.clone()

    variants = build_variants(part_dir, num_bins, args.variants)
    code_template = (SPATIALLM_ROOT / "code_template.txt").read_text()

    runs = []
    for variant in variants:
        set_in_channels(model, variant.feat_dim, base_stem_state)
        for kind in args.prompts:
            prompt = build_prompt(kind, code_template)
            text = generate(
                model, tokenizer, prompt, variant.tensor,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                seed=args.seed,
            )
            record = {
                "part_id": part_id,
                "model": args.model,
                "model_path": str(model_path),
                "variant": variant.name,
                "variant_note": variant.note,
                "in_channels": variant.feat_dim,
                "num_voxels": variant.num_voxels,
                "prompt_kind": kind,
                "temperature": args.temperature,
                "max_new_tokens": args.max_new_tokens,
                "output": text,
                "score": score_text(text),
            }
            runs.append(record)
            tag = f"{variant.name}__{kind}"
            (out_dir / f"{tag}.txt").write_text(text, encoding="utf-8")
            print(f"\n=== {args.model} | {variant.name} (in_ch={variant.feat_dim}) | {kind} ===")
            print(f"    voxels={variant.num_voxels}  cad_buckets={record['score']['cad_buckets_hit']}"
                  f"  room_leak={record['score']['room_leak_terms']}")
            print(text[:900] if text.strip() else "<empty>")

    report = {
        "part_id": part_id,
        "part_dir": str(part_dir),
        "model": args.model,
        "model_path": str(model_path),
        "dtype": args.dtype,
        "temperature": args.temperature,
        "target_diagonal": TARGET_DIAGONAL,
        "num_bins": num_bins,
        "prompts": {k: build_prompt(k, code_template).replace(code_template, "<code_template>")
                    for k in args.prompts},
        "runs": runs,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
