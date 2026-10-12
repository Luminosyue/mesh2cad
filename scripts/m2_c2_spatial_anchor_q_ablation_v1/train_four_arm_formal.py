#!/usr/bin/env python3
"""Fresh official-base 10-epoch trainer for one frozen Q-ablation arm."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, get_cosine_schedule_with_warmup

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [
    str(ROOT / "scripts/m2_c2_spatial_anchor_q_ablation_v1"),
    str(ROOT / "scripts/spatiallm_geometry_prefix_v3"),
    str(ROOT / "scripts/spatiallm_m2_spatial_anchor_v1"),
    str(ROOT / "scripts"),
    str(ROOT / "SpatialLM"),
    str(ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code"),
]

from run_four_arm_100step_impl import ARMS, BASE, C2, TRAIN, build_model, install_geometry, one_forward, sha256, v3

DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
DEV = DATA / "v3_decode_dev_50.json"
OFFICIAL_LLM_STATE_SHA256 = "996591f4204940b56bd63516a47274ed1eaceb20978149c76cff651c5b248631"


def llm_hash(model) -> str:
    h = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        if name.startswith(("point_backbone.", "point_proj.", "edge_proj.")):
            continue
        value = tensor.detach().cpu().contiguous()
        h.update(name.encode() + b"\0")
        h.update(str(tuple(value.shape)).encode() + b"\0")
        h.update(str(value.dtype).encode() + b"\0")
        h.update(value.view(torch.uint8).numpy().tobytes())
    return h.hexdigest()


def param_audit(params) -> dict:
    params = list(params)
    return {
        "trainable_parameter_count": sum(p.numel() for p in params if p.requires_grad),
        "grad_non_none_tensor_count": sum(p.grad is not None for p in params),
        "grad_non_none_parameter_count": sum(p.numel() for p in params if p.grad is not None),
    }


def validate_ce(model, plugin, tokenizer, rows, q, device, runtime) -> float:
    model.eval()
    losses = []
    with torch.no_grad():
        for row in rows:
            loss, *_ = one_forward(model, plugin, tokenizer, row, q, device, runtime, train=False)
            losses.append(float(loss))
    model.train()
    return float(np.mean(losses))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    use_anchor, q = ARMS[args.arm]
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    device = torch.device(args.device)
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    torch.backends.cuda.matmul.allow_tf32 = True
    train = json.loads(TRAIN.read_text())["records"]
    dev = json.loads(DEV.read_text())["records"]
    if len(train) != 800 or len(dev) != 50:
        raise RuntimeError("frozen split count mismatch")
    if sha256(C2) != "553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9":
        raise RuntimeError("C2 checkpoint hash mismatch")
    v3.heldout_geometry.install()
    plugin = v3.get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True, use_fast=False)
    model, branch, adapter = build_model(use_anchor, q, device)
    initial_llm_hash = llm_hash(model)
    if initial_llm_hash != OFFICIAL_LLM_STATE_SHA256:
        raise RuntimeError(f"official parent LLM hash mismatch: {initial_llm_hash}")
    runtime = {}
    original_splice = install_geometry(model, branch, use_anchor, runtime)
    point = list(model.point_backbone.parameters())
    surface_projector = list(model.point_proj.parameters())
    branch_params = list(branch.parameters())
    excluded = {id(p) for p in point + surface_projector + branch_params}
    llama = [p for p in model.parameters() if id(p) not in excluded]
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(params, lr=2e-5, weight_decay=0.0)
    updates = math.ceil(800 / 4) * args.epochs
    scheduler = get_cosine_schedule_with_warmup(optimizer, int(updates * 0.03), updates)
    report = {
        "CURRENT_GATE": "M2_SPATIAL_ANCHOR_Q_ABLATION_FORMAL_TRAIN800_RUNNING",
        "ARM": args.arm,
        "USE_ANCHOR": use_anchor,
        "NUM_QUERIES": q,
        "FRESH_FROM_OFFICIAL_BASE": True,
        "INITIAL_LLM_HASH": initial_llm_hash,
        "SMOKE_CHECKPOINT_USED_FOR_FORMAL_TRAINING": False,
        "TRAIN_COUNT": 800,
        "DECODE_DEV_COUNT": 50,
        "ANCHOR_EVAL_100_MODEL_READ": False,
        "PILOT150_MODEL_READ": False,
        "OFFICIAL_TEST_READ": False,
        "EPOCHS_REQUESTED": args.epochs,
        "SEED": 42,
        "GRADIENT_ACCUMULATION": 4,
        "PRECISION": "bfloat16",
        "NAN_COUNT": 0,
        "INF_COUNT": 0,
        "OOM_COUNT": 0,
        "EPOCHS": [],
        "STATUS": "RUNNING",
    }
    try:
        for epoch in range(1, args.epochs + 1):
            order = list(range(800))
            random.Random(42 + epoch).shuffle(order)
            optimizer.zero_grad(set_to_none=True)
            losses, update_grad_norms = [], []
            for position, index in enumerate(order, 1):
                row = train[index]
                loss, *_ = one_forward(model, plugin, tokenizer, row, q, device, runtime, train=True)
                if not torch.isfinite(loss):
                    report["NAN_COUNT"] += int(torch.isnan(loss))
                    report["INF_COUNT"] += int(torch.isinf(loss))
                    raise RuntimeError(f"non-finite loss epoch={epoch} position={position}")
                (loss / 4).backward()
                losses.append(float(loss.detach()))
                if epoch == 1 and position == 1:
                    audit = {
                        "SONATA": param_audit(point),
                        "SURFACE_PROJECTOR": param_audit(surface_projector),
                        "C2": {"trainable_parameter_count": 0, "grad_non_none_tensor_count": 0, "grad_non_none_parameter_count": 0},
                        "GEOMETRY_PREFIX_ADAPTER": param_audit(adapter.parameters()),
                        "ANCHOR_MLP": param_audit(branch.anchor_mlp.parameters()) if use_anchor else None,
                        "LLAMA": param_audit(llama),
                    }
                    report["FIRST_BACKWARD_GRADIENT_AUDIT"] = audit
                    if (
                        audit["SONATA"]["trainable_parameter_count"]
                        or audit["SONATA"]["grad_non_none_parameter_count"]
                        or audit["SURFACE_PROJECTOR"]["trainable_parameter_count"]
                        or audit["SURFACE_PROJECTOR"]["grad_non_none_parameter_count"]
                        or audit["C2"]["trainable_parameter_count"]
                        or audit["C2"]["grad_non_none_parameter_count"]
                        or audit["GEOMETRY_PREFIX_ADAPTER"]["grad_non_none_parameter_count"] == 0
                        or audit["LLAMA"]["grad_non_none_parameter_count"] == 0
                        or (use_anchor and audit["ANCHOR_MLP"]["grad_non_none_parameter_count"] == 0)
                    ):
                        raise RuntimeError("gradient ownership hard stop")
                entry = runtime["entry"]
                if entry["summary_active_count"] != q or entry["physical_summary_length"] != q or entry["padding_attention_count"] != 0:
                    raise RuntimeError(f"geometry entry contract hard stop: {entry}")
                if position % 4 == 0 or position == 800:
                    grad_norm = float(torch.nn.utils.clip_grad_norm_(params, 1.0))
                    if not math.isfinite(grad_norm):
                        raise RuntimeError("non-finite gradient norm")
                    update_grad_norms.append(grad_norm)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad(set_to_none=True)
                if position % 100 == 0:
                    print(f"[{args.arm}] epoch={epoch}/{args.epochs} train={position}/800 loss={float(loss):.6f}", flush=True)
            dev_ce = validate_ce(model, plugin, tokenizer, dev, q, device, runtime)
            checkpoint = output / f"checkpoint_epoch_{epoch:02d}"
            checkpoint.mkdir()
            torch.save(branch.state_dict(), checkpoint / "geometry_branch.pt")
            saved_branch = model.edge_proj
            model.edge_proj = None
            model.save_pretrained(checkpoint, safe_serialization=True, max_shard_size="2GB")
            model.edge_proj = saved_branch
            tokenizer.save_pretrained(checkpoint)
            provenance = {
                "arm": args.arm,
                "epoch": epoch,
                "fresh_from_official_base": True,
                "official_initial_llm_hash": initial_llm_hash,
                "smoke_checkpoint_used": False,
                "c2_frozen": True,
                "c2_sha256": sha256(C2),
            }
            (checkpoint / "CHECKPOINT_PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
            epoch_report = {
                "epoch": epoch,
                "train_ce": float(np.mean(losses)),
                "validation_ce": dev_ce,
                "learning_rate": scheduler.get_last_lr()[0],
                "grad_norm_mean": float(np.mean(update_grad_norms)),
                "grad_norm_max": float(np.max(update_grad_norms)),
                "nan_count": 0,
                "inf_count": 0,
                "oom_count": 0,
                "checkpoint": str(checkpoint),
            }
            report["EPOCHS"].append(epoch_report)
            (output / "TRAINING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
            print(f"[{args.arm}] epoch={epoch}/10 train_ce={epoch_report['train_ce']:.6f} dev_ce={dev_ce:.6f}", flush=True)
        report["CURRENT_GATE"] = "FORMAL_TRAIN800_ARM_TRAINING_COMPLETE"
        report["STATUS"] = "PASS"
    except torch.cuda.OutOfMemoryError as error:
        report["OOM_COUNT"] += 1
        report["STATUS"] = "HARD_STOP_OOM"
        report["ERROR"] = repr(error)
        raise
    except Exception as error:
        report["STATUS"] = "HARD_STOP"
        report["ERROR"] = repr(error)
        raise
    finally:
        v3.module._splice_geometry = original_splice
        (output / "TRAINING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "EPOCHS"}, indent=2))


if __name__ == "__main__":
    main()
