#!/usr/bin/env python3
"""Formal 10-epoch B0/B1-BM/M2-C2-BM pilot on the frozen 800/200 split."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
import shutil
import sys
import time

import numpy as np
import torch
from transformers import AutoTokenizer, get_cosine_schedule_with_warmup
from safetensors import safe_open

ROOT = pathlib.Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_curve_token_c2_frozen_v2"))
import train_canonical_smoke as core

DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data"
BASE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1"
SPATIAL_MODULE_BASE = core.BASE_MODEL
TOKENIZER_BASE = BASE
SEED = 42


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def llm_state_hash(model) -> str:
    h = hashlib.sha256()
    for key, tensor in sorted(model.state_dict().items()):
        if key.startswith(("point_backbone.", "point_proj.", "edge_proj.")):
            continue
        value = tensor.detach().cpu().contiguous()
        h.update(key.encode() + b"\0")
        h.update(str(tuple(value.shape)).encode() + b"\0")
        h.update(str(value.dtype).encode() + b"\0")
        h.update(value.view(torch.uint8).numpy().tobytes())
    return h.hexdigest()


def load_records(split: str) -> list[dict]:
    return json.loads((DATA / f"pilot_1k_{split}.json").read_text())["records"]


def make_official_model(arm: str, device: torch.device):
    """Load the one frozen parent checkpoint, then add only the arm projector."""
    contract = json.loads((BASE / "BASE_CONTRACT.json").read_text())
    model = core.module.SpatialLMLlamaForCausalLM.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
    )
    for parameter in model.point_backbone.parameters():
        parameter.requires_grad_(False)
    for parameter in model.point_proj.parameters():
        parameter.requires_grad_(False)
    if arm == "b1":
        projector = torch.nn.Linear(model.config.hidden_size, model.config.hidden_size, bias=False, dtype=torch.bfloat16, device=device)
        with torch.no_grad():
            projector.weight.copy_(torch.eye(model.config.hidden_size, dtype=torch.bfloat16, device=device))
        model.edge_proj = projector
    elif arm == "m2":
        model.edge_proj = core.build_curve_projector(256, model.config.hidden_size).to(device=device, dtype=torch.bfloat16)
    else:
        model.edge_proj = None
    if arm != "b0":
        model.config.separate_edge_tokens = True
        model.separate_edge_tokens = True
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model.train()
    provenance = {
        "parent_contract": contract["contract"],
        "parent_llm_state_sha256": contract["llm"]["state_sha256"],
        "official_model_sha256": contract["llm"]["source_sha256"],
        "spatial_llm_tensors_loaded": contract["spatiallm_llm_tensors_loaded"],
        "loaded_directly_from_frozen_parent": True,
    }
    return model, provenance


def save_checkpoint(model, tokenizer, arm: str, directory: pathlib.Path, metadata: dict) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    model.save_pretrained(directory, safe_serialization=True, max_shard_size="2GB")
    tokenizer.save_pretrained(directory)
    if arm != "b0":
        torch.save(model.edge_proj.state_dict(), directory / "arm_projector.pt")
    (directory / "pilot_checkpoint.json").write_text(json.dumps(metadata, indent=2) + "\n")


def validate(model, plugin, tokenizer, records, arm, device, state) -> tuple[float, list[float], int]:
    model.eval()
    losses, failures = [], 0
    for row in records:
        loss, _, _ = core.one_forward(model, plugin, tokenizer, row, arm, device, state, train=False)
        value = float(loss)
        if not math.isfinite(value):
            raise RuntimeError(f"non-finite validation loss for {row['cad_id']}")
        losses.append(value)
        if arm != "b0" and (state["entry"]["second_stream_active"] != row["k_valid"] or state["entry"]["padding_attention"] != 0):
            failures += 1
    model.train()
    return float(np.mean(losses)), losses, failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=["b0", "b1", "m2"], required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--warmup-ratio", type=float, default=0.03)
    args = parser.parse_args()

    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    train, val = load_records("train"), load_records("val")
    if len(train) != 800 or len(val) != 200:
        raise RuntimeError("formal split count mismatch")
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    random.seed(SEED)
    torch.backends.cuda.matmul.allow_tf32 = True
    device = torch.device(args.device)
    torch.cuda.set_device(device)
    torch.cuda.reset_peak_memory_stats(device)

    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_BASE, local_files_only=True, use_fast=False)
    marker_contract = {
        "vocab_size": len(tokenizer),
        "point_start_token_id": tokenizer.convert_tokens_to_ids("<|point_start|>"),
        "point_end_token_id": tokenizer.convert_tokens_to_ids("<|point_end|>"),
        "point_pad_token_id": tokenizer.convert_tokens_to_ids("<|point_pad|>"),
        "llm_embedding_rows_added": 0,
        "official_embedding_ids_reused": [128011, 128012, 128013],
    }
    if marker_contract != {
        "vocab_size": 128256,
        "point_start_token_id": 128011,
        "point_end_token_id": 128012,
        "point_pad_token_id": 128013,
        "llm_embedding_rows_added": 0,
        "official_embedding_ids_reused": [128011, 128012, 128013],
    }:
        raise RuntimeError(f"geometry marker contract mismatch: {marker_contract}")
    model, initialization_provenance = make_official_model(args.arm, device)
    initial_llm_hash = llm_state_hash(model)
    expected_llm_hash = initialization_provenance["parent_llm_state_sha256"]
    if initial_llm_hash != expected_llm_hash:
        raise RuntimeError(f"pre-optimizer LLM hash mismatch: {initial_llm_hash} != {expected_llm_hash}")
    state = {}
    original_splice = core.install_precomputed_second(model, args.arm, state)
    point, edge, llm = core.groups(model, args.arm)
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
    updates_per_epoch = math.ceil(len(train) / args.grad_accum)
    total_updates = updates_per_epoch * args.epochs
    warmup = int(total_updates * args.warmup_ratio)
    scheduler = get_cosine_schedule_with_warmup(optimizer, warmup, total_updates)

    report = {
        "protocol": "pilot_1k_formal_v1",
        "arm": args.arm,
        "base_checkpoint": str(BASE),
        "base_checkpoint_kind": "official_original_Llama-3.2-1B-Instruct",
        "initialization_provenance": initialization_provenance,
        "pre_optimizer_llm_state_sha256": initial_llm_hash,
        "pre_optimizer_llm_hash_match": True,
        "tokenizer_marker_contract": marker_contract,
        "fresh_from_base": True,
        "smoke_checkpoint_used": False,
        "official_test_read": False,
        "seed": SEED,
        "epochs_requested": args.epochs,
        "train_count": len(train),
        "val_count": len(val),
        "batch_size": 1,
        "gradient_accumulation": args.grad_accum,
        "precision": "bfloat16",
        "max_sequence_length": 4096,
        "optimizer": "AdamW",
        "lr": args.lr,
        "scheduler": "cosine",
        "warmup_updates": warmup,
        "total_updates": total_updates,
        "split_hashes": {
            "train": sha(DATA / "pilot_1k_train.json"),
            "val": sha(DATA / "pilot_1k_val.json"),
        },
        "epochs": [],
        "status": "RUNNING",
    }
    best_val = float("inf")
    best_epoch = None
    global_update = 0
    first_audit = None
    try:
        for epoch in range(1, args.epochs + 1):
            epoch_start = time.time()
            order = list(range(len(train)))
            random.Random(SEED + epoch).shuffle(order)
            optimizer.zero_grad(set_to_none=True)
            sample_losses, grad_norms = [], []
            entry_failures = 0
            for position, index in enumerate(order, 1):
                row = train[index]
                loss, _, _ = core.one_forward(model, plugin, tokenizer, row, args.arm, device, state, train=True)
                if not torch.isfinite(loss):
                    raise RuntimeError(f"non-finite train loss epoch={epoch} cad={row['cad_id']}")
                sample_losses.append(float(loss.detach()))
                (loss / args.grad_accum).backward()
                if first_audit is None:
                    first_audit = {
                        "SONATA_AND_SURFACE_PROJECTOR": core.audit_group(point),
                        "ARM_PROJECTOR": core.audit_group(edge),
                        "LLM": core.audit_group(llm),
                        "C2": {"parameter_count": 0, "trainable_parameter_count": 0, "grad_non_none_parameter_count": 0, "grad_non_none_tensor_count": 0},
                        "B1_ENCODER": {"parameter_count": 0, "trainable_parameter_count": 0, "grad_non_none_parameter_count": 0, "grad_non_none_tensor_count": 0},
                    }
                    hard = (
                        first_audit["SONATA_AND_SURFACE_PROJECTOR"]["trainable_parameter_count"]
                        or first_audit["SONATA_AND_SURFACE_PROJECTOR"]["grad_non_none_parameter_count"]
                        or first_audit["C2"]["trainable_parameter_count"]
                        or first_audit["C2"]["grad_non_none_parameter_count"]
                        or first_audit["B1_ENCODER"]["trainable_parameter_count"]
                        or first_audit["B1_ENCODER"]["grad_non_none_parameter_count"]
                        or first_audit["LLM"]["grad_non_none_parameter_count"] == 0
                        or (args.arm != "b0" and first_audit["ARM_PROJECTOR"]["grad_non_none_parameter_count"] == 0)
                    )
                    if hard:
                        raise RuntimeError("first-backward gradient audit hard stop")
                    report["first_backward_gradient_audit"] = first_audit
                    (out / "FIRST_BACKWARD_AUDIT.json").write_text(json.dumps(first_audit, indent=2) + "\n")
                if args.arm != "b0" and (state["entry"]["second_stream_active"] != row["k_valid"] or state["entry"]["padding_attention"] != 0):
                    entry_failures += 1
                    raise RuntimeError(f"training entry mismatch for {row['cad_id']}")
                if position % args.grad_accum == 0 or position == len(order):
                    norm = torch.nn.utils.clip_grad_norm_(trainable, 1.0)
                    grad_norms.append(float(norm))
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad(set_to_none=True)
                    global_update += 1
                if position % 100 == 0:
                    print(f"[{args.arm}] epoch={epoch}/{args.epochs} sample={position}/800 loss={sample_losses[-1]:.6f} lr={scheduler.get_last_lr()[0]:.3e}", flush=True)

            val_ce, val_losses, val_entry_failures = validate(model, plugin, tokenizer, val, args.arm, device, state)
            if entry_failures or val_entry_failures:
                raise RuntimeError(f"entry gate failure train={entry_failures} val={val_entry_failures}")
            epoch_record = {
                "epoch": epoch,
                "train_ce": float(np.mean(sample_losses)),
                "val_ce": val_ce,
                "lr": scheduler.get_last_lr()[0],
                "gradient_norm_mean": float(np.mean(grad_norms)),
                "gradient_norm_max": float(np.max(grad_norms)),
                "gpu_peak_memory_bytes": int(torch.cuda.max_memory_allocated(device)),
                "train_entry_failures": entry_failures,
                "val_entry_failures": val_entry_failures,
                "elapsed_seconds": time.time() - epoch_start,
            }
            report["epochs"].append(epoch_record)
            ckpt = out / f"checkpoint-epoch-{epoch:02d}"
            save_checkpoint(model, tokenizer, args.arm, ckpt, {**epoch_record, "arm": args.arm, "base_checkpoint": str(BASE)})
            if val_ce < best_val:
                best_val, best_epoch = val_ce, epoch
                (out / "BEST_CHECKPOINT.json").write_text(json.dumps({"epoch": epoch, "val_ce": val_ce, "path": str(ckpt)}, indent=2) + "\n")
            report.update(best_epoch=best_epoch, best_val_ce=best_val, global_updates=global_update)
            (out / "TRAINING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(epoch_record), flush=True)
        report["status"] = "PASS"
    except torch.cuda.OutOfMemoryError as exc:
        report["status"] = "HARD_STOP_OOM"
        report["error"] = repr(exc)
        raise
    except Exception as exc:
        report["status"] = "HARD_STOP"
        report["error"] = repr(exc)
        raise
    finally:
        core.module._splice_geometry = original_splice
        report["best_epoch"] = best_epoch
        report["best_val_ce"] = None if best_epoch is None else best_val
        report["global_updates"] = global_update
        (out / "TRAINING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
