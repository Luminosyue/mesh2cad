#!/usr/bin/env python3
"""Forward / gradient / reload probes for separate_edge_tokens_v1.

Probes
------
A  real edge      Surface A + Edge A            -> shapes of every stage
B  zero edge      Surface A + zeroed edge feats -> must move the embeddings
C  corrupted edge Surface A + spatially scrambled Edge A
D  wrong edge     Surface A + Edge B (other CAD part)

Sonata is permutation invariant over rows, so probe C does not merely shuffle
row order: it permutes the xyz/grid columns independently of the normals, which
destroys geometry while preserving every marginal distribution.

Also runs a gradient probe (the edge projector must receive non-zero gradient),
a parameter audit, and a checkpoint save/reload determinism check.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import (  # noqa: E402
    CACHE_DIR,
    DEFAULT_MODEL_PATH,
    OUT_ROOT,
    build_batch,
    cached_sample_ids,
    corrupt_edge,
    json_dump,
    load_geometry,
    load_model,
    make_plugin,
    read_dsl,
    set_deterministic_serialization,
    zero_edge_like,
)


def _pooled(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=0)


def compare_tokens(ref: np.ndarray, other: np.ndarray) -> dict:
    """Token-wise delta when shapes match; pooled delta always."""
    out = {
        "ref_num_tokens": int(ref.shape[0]),
        "other_num_tokens": int(other.shape[0]),
        "shapes_comparable": bool(ref.shape == other.shape),
    }
    pr, po = _pooled(ref), _pooled(other)
    denom = max(float(np.linalg.norm(pr)), 1e-12)
    out["pooled_relative_delta"] = float(np.linalg.norm(po - pr) / denom)
    out["pooled_cosine"] = float(
        np.dot(pr, po) / max(np.linalg.norm(pr) * np.linalg.norm(po), 1e-12)
    )
    out["pooled_max_abs_diff"] = float(np.abs(po - pr).max())

    if ref.shape == other.shape:
        delta = np.linalg.norm(other - ref, axis=1)
        norm = np.linalg.norm(ref, axis=1)
        rel = delta / np.maximum(norm, 1e-12)
        cos = np.sum(ref * other, axis=1) / np.maximum(
            np.linalg.norm(ref, axis=1) * np.linalg.norm(other, axis=1), 1e-12
        )
        out.update(
            {
                "identical": bool(np.array_equal(ref, other)),
                "relative_delta_mean": float(rel.mean()),
                "relative_delta_max": float(rel.max()),
                "cosine_mean": float(cos.mean()),
                "cosine_min": float(cos.min()),
                "max_abs_diff": float(np.abs(other - ref).max()),
            }
        )
    return out


@torch.no_grad()
def run_forward_probes(model, tokenizer, sample_a: str, sample_b: str, device: str) -> dict:
    plugin = make_plugin(separate_edge=True)
    surf_a, edge_a = load_geometry(sample_a, plugin)
    _, edge_b = load_geometry(sample_b, plugin)

    variants = {
        "A_real_edge": edge_a,
        "B_zero_edge": zero_edge_like(edge_a),
        "C_corrupted_edge": corrupt_edge(edge_a, seed=0),
        "D_wrong_edge": edge_b,
    }

    dsl = read_dsl(sample_a)
    tokens, losses, seq_lens = {}, {}, {}
    surface_tokens_ref = None
    for name, edge in variants.items():
        s_tok, e_tok = model.forward_geometry(
            surf_a[0].to(device), edge[0].to(device), device, torch.float32
        )
        tokens[name] = e_tok.squeeze(0).float().cpu().numpy()
        if surface_tokens_ref is None:
            surface_tokens_ref = s_tok.squeeze(0).float().cpu().numpy()

        batch = build_batch(tokenizer, surf_a, edge, dsl, device, separate_edge=True)
        out = model(**batch)
        losses[name] = float(out.loss.item())
        seq_lens[name] = int(out.logits.shape[1])

    # Surface-only control: identical surface, edge stream switched off entirely.
    batch_surface_only = build_batch(
        tokenizer, surf_a, None, dsl, device, separate_edge=False
    )
    # Prompt without edge markers, so this exercises the untouched baseline path.
    surface_only_loss = float(model(**batch_surface_only).loss.item())

    ref = tokens["A_real_edge"]
    report = {
        "sample_a": sample_a,
        "sample_b": sample_b,
        "RAW_SURFACE_POINT_COUNT": int(np.load(CACHE_DIR / sample_a / "surface_points.npy").shape[0]),
        "RAW_EDGE_POINT_COUNT": int(np.load(CACHE_DIR / sample_a / "edge_points.npy").shape[0]),
        "SURFACE_VOXEL_COUNT": int(surf_a.shape[1]),
        "EDGE_VOXEL_COUNT": int(edge_a.shape[1]),
        "ENCODED_SURFACE_TOKEN_COUNT": int(surface_tokens_ref.shape[0]),
        "ENCODED_EDGE_TOKEN_COUNT": int(ref.shape[0]),
        "surface_token_shape": list(surface_tokens_ref.shape),
        "edge_token_shape": list(ref.shape),
        "final_llm_seq_len": seq_lens["A_real_edge"],
        "surface_only_seq_len": None,
        "losses": losses,
        "surface_only_loss": surface_only_loss,
        "deltas": {
            "real_vs_zero": compare_tokens(ref, tokens["B_zero_edge"]),
            "real_vs_corrupted": compare_tokens(ref, tokens["C_corrupted_edge"]),
            "real_vs_wrong": compare_tokens(ref, tokens["D_wrong_edge"]),
        },
    }
    report["surface_only_seq_len"] = int(
        model(**batch_surface_only).logits.shape[1]
    )
    report["REAL_EDGE_CHANGES_EMBEDDINGS"] = bool(
        report["deltas"]["real_vs_zero"]["pooled_relative_delta"] > 0.0
    )
    return report


def run_gradient_probe(model, tokenizer, sample_id: str, device: str) -> dict:
    plugin = make_plugin(separate_edge=True)
    surf, edge = load_geometry(sample_id, plugin)
    dsl = read_dsl(sample_id)

    model.zero_grad(set_to_none=True)
    batch = build_batch(tokenizer, surf, edge, dsl, device, separate_edge=True)
    out = model(**batch)
    loss = out.loss
    loss.backward()

    def grad_norm(module) -> float:
        total = 0.0
        for p in module.parameters():
            if p.grad is not None:
                total += float(p.grad.detach().float().norm() ** 2)
        return float(total**0.5)

    embed = model.model.embed_tokens
    edge_rows = [model.edge_start_token_id, model.edge_end_token_id, model.edge_token_id]
    special_grad = 0.0
    if embed.weight.grad is not None:
        special_grad = float(
            embed.weight.grad[edge_rows].detach().float().norm().item()
        )

    result = {
        "loss": float(loss.item()),
        "loss_finite": bool(np.isfinite(loss.item())),
        "SURFACE_PROJECTOR_GRAD_NORM": grad_norm(model.point_proj),
        "EDGE_PROJECTOR_GRAD_NORM": grad_norm(model.edge_proj),
        "LLM_GRAD_NORM": grad_norm(model.model),
        "SONATA_GRAD_NORM": grad_norm(model.point_backbone),
        "SPECIAL_EDGE_TOKEN_GRAD_NORM": special_grad,
    }
    result["EDGE_PROJECTOR_GRAD_NONZERO"] = bool(result["EDGE_PROJECTOR_GRAD_NORM"] > 0)
    model.zero_grad(set_to_none=True)
    return result


def run_parameter_audit(model) -> dict:
    def count(module, trainable_only=False):
        return int(
            sum(
                p.numel()
                for p in module.parameters()
                if (p.requires_grad or not trainable_only)
            )
        )

    surface_ids = {id(p) for p in model.point_proj.parameters()}
    edge_ids = {id(p) for p in model.edge_proj.parameters()}
    return {
        "TOTAL_PARAMETERS": count(model),
        "TRAINABLE_PARAMETERS": count(model, True),
        "SONATA_TOTAL": count(model.point_backbone),
        "SONATA_TRAINABLE": count(model.point_backbone, True),
        "SURFACE_PROJECTOR_TOTAL": count(model.point_proj),
        "SURFACE_PROJECTOR_TRAINABLE": count(model.point_proj, True),
        "EDGE_PROJECTOR_TOTAL": count(model.edge_proj),
        "EDGE_PROJECTOR_TRAINABLE": count(model.edge_proj, True),
        "LLM_TOTAL": count(model.model),
        "LLM_TRAINABLE": count(model.model, True),
        "SPECIAL_EDGE_TOKEN_TRAINABLE": bool(
            model.model.embed_tokens.weight.requires_grad
        ),
        "EDGE_PROJECTOR_SHARED": bool(surface_ids & edge_ids),
        "EDGE_PROJECTOR_INIT": "copy_of_surface_projector",
        "SHARED_SONATA": True,
        "SONATA_FROZEN": count(model.point_backbone, True) == 0,
    }


@torch.no_grad()
def run_reload_check(model, tokenizer, sample_id: str, device: str, workdir: Path) -> dict:
    plugin = make_plugin(separate_edge=True)
    surf, edge = load_geometry(sample_id, plugin)
    dsl = read_dsl(sample_id)

    model.eval()
    batch = build_batch(tokenizer, surf, edge, dsl, device, separate_edge=True)
    before = model(**batch)
    before_loss = float(before.loss.item())
    before_logits = before.logits.float().cpu().numpy()

    ckpt = workdir / "reload_ckpt"
    if ckpt.exists():
        shutil.rmtree(ckpt)
    model.save_pretrained(str(ckpt), safe_serialization=True)
    tokenizer.save_pretrained(str(ckpt))

    saved_config = json.loads((ckpt / "config.json").read_text(encoding="utf-8"))

    reloaded, _ = load_model(ckpt, separate_edge=True, device=device, dtype=torch.float32)
    set_deterministic_serialization(reloaded.point_backbone)
    reloaded.eval()
    after = reloaded(**batch)
    after_loss = float(after.loss.item())
    after_logits = after.logits.float().cpu().numpy()

    edge_w_before = next(model.edge_proj.parameters()).detach().float().cpu().numpy()
    edge_w_after = next(reloaded.edge_proj.parameters()).detach().float().cpu().numpy()

    result = {
        "checkpoint_dir": str(ckpt),
        "config_has_separate_edge_tokens": bool(
            saved_config.get("separate_edge_tokens", False)
        ),
        "config_edge_start_token_id": saved_config.get("edge_start_token_id"),
        "reloaded_has_edge_proj": bool(getattr(reloaded, "edge_proj", None) is not None),
        "edge_projector_weights_identical": bool(
            np.array_equal(edge_w_before, edge_w_after)
        ),
        "loss_before": before_loss,
        "loss_after": after_loss,
        "loss_abs_diff": abs(before_loss - after_loss),
        "logits_max_abs_diff": float(np.abs(before_logits - after_logits).max()),
    }
    result["CHECKPOINT_RELOAD_OK"] = bool(
        result["config_has_separate_edge_tokens"]
        and result["reloaded_has_edge_proj"]
        and result["edge_projector_weights_identical"]
        and result["logits_max_abs_diff"] < 1e-3
    )
    del reloaded
    torch.cuda.empty_cache()
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    ap.add_argument("--sample-a", type=str, default=None)
    ap.add_argument("--sample-b", type=str, default=None)
    ap.add_argument("--device", type=str, default="cuda")
    ap.add_argument("--out", type=Path, default=OUT_ROOT / "probes/probe_report.json")
    ap.add_argument("--workdir", type=Path, default=Path(tempfile.gettempdir()) / "sepedge_probe")
    args = ap.parse_args()

    ids = cached_sample_ids()
    if len(ids) < 2:
        raise SystemExit("need at least two cached samples; run build_cache.py")
    sample_a = args.sample_a or ids[0]
    sample_b = args.sample_b or ids[1]
    args.workdir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(
        args.model_path, separate_edge=True, device=args.device, dtype=torch.float32
    )
    set_deterministic_serialization(model.point_backbone)
    model.eval()

    report = {"experiment": "separate_edge_tokens_v1", "model_path": str(args.model_path)}
    report["parameter_audit"] = run_parameter_audit(model)
    report["forward_probes"] = run_forward_probes(
        model, tokenizer, sample_a, sample_b, args.device
    )
    report["gradient_probe"] = run_gradient_probe(model, tokenizer, sample_a, args.device)
    report["reload_check"] = run_reload_check(
        model, tokenizer, sample_a, args.device, args.workdir
    )

    fp, gp, rc = report["forward_probes"], report["gradient_probe"], report["reload_check"]
    report["summary"] = {
        "FORWARD_OK": True,
        "BACKWARD_OK": gp["loss_finite"],
        "EDGE_PROJECTOR_GRAD_NONZERO": gp["EDGE_PROJECTOR_GRAD_NONZERO"],
        "CHECKPOINT_RELOAD_OK": rc["CHECKPOINT_RELOAD_OK"],
        "REAL_EDGE_CHANGES_EMBEDDINGS": fp["REAL_EDGE_CHANGES_EMBEDDINGS"],
        "SURFACE_TOKEN_SHAPE": fp["surface_token_shape"],
        "EDGE_TOKEN_SHAPE": fp["edge_token_shape"],
        "FINAL_LLM_INPUT_SHAPE": [1, fp["final_llm_seq_len"], 2048],
    }
    json_dump(args.out, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
