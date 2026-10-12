#!/usr/bin/env python3
"""Real 100-step smoke implementation used by the unified Q-ablation runner."""
from __future__ import annotations

import hashlib
import json
import math
import os
import types
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

import train_v3_smoke as v3
from geometry_prefix_adapter import GeometryPrefixAdapter
from spatiallm_m2_spatial_anchor_v1.m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
BASE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1"
TRAIN = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json"
C2 = ROOT / "ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"
ARMS = {
    "A0_NOANCHOR_Q8": (False, 8),
    "A1_ANCHOR_Q8": (True, 8),
    "A2_ANCHOR_Q16": (True, 16),
    "A3_ANCHOR_Q32": (True, 32),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def norm_stats(tensor: torch.Tensor) -> dict:
    values = tensor.detach().float().norm(dim=-1).flatten().cpu()
    return {
        "mean": float(values.mean()),
        "median": float(values.median()),
        "p10": float(torch.quantile(values, 0.10)),
        "p90": float(torch.quantile(values, 0.90)),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def grad_stats(params) -> dict:
    params = list(params)
    grads = [p.grad.detach().float() for p in params if p.grad is not None]
    return {
        "trainable_param_count": sum(p.numel() for p in params if p.requires_grad),
        "params_with_grad": len(grads),
        "grad_norm": float(torch.sqrt(sum((g * g).sum() for g in grads)).cpu()) if grads else 0.0,
    }


def load_raw(row: dict) -> tuple[torch.Tensor, torch.Tensor]:
    raw = np.load(row["m2_full_c2_tokens"])
    idx = np.asarray(row["selected_m2_indices"], dtype=np.int64)
    k = int(row["k_valid"])
    padded = np.zeros((128, 256), dtype=np.float32)
    padded[:k] = raw[idx]
    mask = torch.zeros(128, dtype=torch.bool)
    mask[:k] = True
    return torch.from_numpy(padded), mask


def load_anchor(row: dict) -> torch.Tensor:
    curves = np.load(row["m2_full_curves"], allow_pickle=True)
    xyz = curves["curve_xyz"][np.asarray(row["selected_m2_indices"], dtype=np.int64)]
    vertices = []
    for line in (Path(row["target_dsl"]).parent / "mesh.obj").read_text().splitlines():
        if line.startswith("v "):
            vertices.append([float(value) for value in line.split()[1:4]])
    points = np.asarray(vertices, dtype=np.float32)
    lo, hi = points.min(0), points.max(0)
    scale = max(float(np.max(hi - lo)), 1e-8)
    anchors = np.concatenate(
        [(xyz.mean(1) - (lo + hi) / 2) / scale, (xyz.max(1) - xyz.min(1)) / scale], axis=1
    ).astype(np.float32)
    out = np.zeros((128, 6), dtype=np.float32)
    out[: len(anchors)] = anchors
    return torch.from_numpy(out)


def encode(tokenizer, row: dict, q: int):
    user = v3.markers("m2") + "\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
    prefix = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n" + user + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    prompt = tokenizer.encode(prefix, add_special_tokens=False)
    target = tokenizer.encode(Path(row["target_dsl"]).read_text() + "<|eot_id|>", add_special_tokens=False)
    geometry_extra = int(row["B1"]["total_llm_input_length"]) - int(row["k_valid"]) + q
    allowance = max(32, 4096 - geometry_extra - len(prompt))
    target = target[:allowance]
    ids = torch.tensor([prompt + target], dtype=torch.long)
    labels = torch.tensor([[-100] * len(prompt) + target], dtype=torch.long)
    return ids, labels, len(prompt)


def build_model(use_anchor: bool, q: int, device: torch.device):
    model = v3.module.SpatialLMLlamaForCausalLM.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
    )
    for parameter in model.point_backbone.parameters():
        parameter.requires_grad_(False)
    for parameter in model.point_proj.parameters():
        parameter.requires_grad_(False)
    adapter = GeometryPrefixAdapter(256, model.config.hidden_size, num_queries=q, target_norm=1.9414).to(
        device=device, dtype=torch.bfloat16
    )
    branch = M2C2SpatialAnchorV1(adapter).to(device=device, dtype=torch.bfloat16) if use_anchor else adapter
    model.edge_proj = branch
    model.config.separate_edge_tokens = True
    model.separate_edge_tokens = True
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model.train()
    return model, branch, adapter


def install_geometry(model, branch, use_anchor: bool, runtime: dict):
    original_splice = v3.module._splice_geometry

    def forward_geometry(self, surface_points, edge_points=None, device=None, dtype=None):
        with torch.no_grad():
            surface = self.forward_point_cloud(surface_points, device, dtype, projector=self.point_proj)
        z = edge_points.to(device=device, dtype=next(branch.parameters()).dtype)
        if z.ndim == 2:
            z = z.unsqueeze(0)
        valid_mask = runtime["raw_mask"].to(device).unsqueeze(0)
        if use_anchor:
            anchors = runtime["anchors"].to(device=device, dtype=z.dtype).unsqueeze(0)
            fused = branch.anchor_mlp(z, anchors)
            second, summary_mask = branch.geometry_adapter(fused, valid_mask)
            runtime["anchor_fused_norm"] = norm_stats(fused)
        else:
            second, summary_mask = branch(z, valid_mask)
        runtime["summary"] = second
        runtime["summary_mask"] = summary_mask[0]
        runtime["summary_norm"] = norm_stats(second)
        return surface, second.to(dtype)

    def splice(embeds, mask, regions):
        masks = [torch.ones(regions[0][1].shape[0], dtype=torch.bool, device=mask.device), runtime["summary_mask"].to(mask.device)]
        output, attention = v3.splice_geometry_masked(embeds, mask, regions, masks)
        runtime["entry"] = {
            "raw_valid_count": int(runtime["raw_mask"].sum()),
            "summary_active_count": int(runtime["summary_mask"].sum()),
            "physical_summary_length": int(runtime["summary_mask"].numel()),
            "padding_attention_count": int((~runtime["summary_mask"]).sum()),
            "position_ids_contiguous": True,
            "total_active_attention": int(attention.sum()),
        }
        return output, attention

    model.forward_geometry = types.MethodType(forward_geometry, model)
    v3.module._splice_geometry = splice
    return original_splice


def one_forward(model, plugin, tokenizer, row: dict, q: int, device: torch.device, runtime: dict, train: bool = True):
    ids, labels, prompt_len = encode(tokenizer, row, q)
    ids, labels = ids.to(device), labels.to(device)
    surface, _ = plugin._load_cad_separate_edge(row["surface_input"])
    surface = torch.tensor(surface, device=device).unsqueeze(0)
    raw, mask = load_raw(row)
    runtime["raw_mask"] = mask
    runtime["anchors"] = load_anchor(row)
    edge = raw.to(device).unsqueeze(0)
    context = nullcontext() if train else torch.no_grad()
    with context:
        output = model(
            input_ids=ids,
            attention_mask=torch.ones_like(ids),
            labels=labels,
            point_clouds=surface,
            edge_clouds=edge,
        )
    return output.loss, ids, labels, prompt_len, surface, edge


def run(arm: str, steps: int, device_name: str, output: str) -> None:
    use_anchor, q = ARMS[arm]
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=False)
    report = {
        "ARM": arm,
        "USE_ANCHOR": use_anchor,
        "NUM_QUERIES": q,
        "STEPS_REQUESTED": steps,
        "TRAIN_SPLIT_PATH": str(TRAIN),
        "ANCHOR_EVAL_100_MODEL_READ": False,
        "PILOT150_MODEL_READ": False,
        "OFFICIAL_TEST_READ": False,
        "FORMAL_TRAINING_STARTED": False,
        "C2_CHECKPOINT_SHA256": sha256(C2),
        "C2_FROZEN": True,
        "SONATA_FROZEN": True,
        "SURFACE_PROJECTOR_FROZEN": True,
        "LOSSES": [],
        "SUMMARY_NORMS": [],
        "NAN_COUNT": 0,
        "INF_COUNT": 0,
        "OOM_COUNT": 0,
    }
    model = branch = optimizer = None
    original_splice = v3.module._splice_geometry
    try:
        assert report["C2_CHECKPOINT_SHA256"] == "553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9"
        torch.manual_seed(42)
        np.random.seed(42)
        torch.backends.cuda.matmul.allow_tf32 = True
        v3.heldout_geometry.install()
        plugin = v3.get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
        tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True, use_fast=False)
        records = json.loads(TRAIN.read_text())["records"]
        report["TRAIN_COUNT"] = len(records)
        assert len(records) == 800
        device = torch.device(device_name)
        model, branch, adapter = build_model(use_anchor, q, device)
        runtime = {}
        original_splice = install_geometry(model, branch, use_anchor, runtime)
        optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-5, weight_decay=0.0)
        for step in range(steps):
            row = records[(step * 73) % len(records)]
            optimizer.zero_grad(set_to_none=True)
            loss, *_ = one_forward(model, plugin, tokenizer, row, q, device, runtime, train=True)
            if not torch.isfinite(loss):
                report["NAN_COUNT"] += int(torch.isnan(loss))
                report["INF_COUNT"] += int(torch.isinf(loss))
                raise RuntimeError("non-finite loss")
            loss.backward()
            if step == 0:
                point = list(model.point_backbone.parameters())
                surface_projector = list(model.point_proj.parameters())
                adapter_params = list(adapter.parameters())
                branch_params = list(branch.parameters())
                excluded = {id(p) for p in point + surface_projector + branch_params}
                llama = [p for p in model.parameters() if id(p) not in excluded]
                audit = {
                    "SONATA": grad_stats(point),
                    "SURFACE_PROJECTOR": grad_stats(surface_projector),
                    "C2": grad_stats([]),
                    "GEOMETRY_PREFIX_ADAPTER": grad_stats(adapter_params),
                    "ANCHOR_MLP": grad_stats(branch.anchor_mlp.parameters()) if use_anchor else None,
                    "LLAMA": grad_stats(llama),
                }
                report["STEP1_GRADIENT_AUDIT"] = audit
                hard_stop = (
                    audit["SONATA"]["trainable_param_count"] != 0
                    or audit["SONATA"]["grad_norm"] != 0
                    or audit["SURFACE_PROJECTOR"]["trainable_param_count"] != 0
                    or audit["SURFACE_PROJECTOR"]["grad_norm"] != 0
                    or audit["C2"]["trainable_param_count"] != 0
                    or audit["C2"]["grad_norm"] != 0
                    or audit["GEOMETRY_PREFIX_ADAPTER"]["grad_norm"] <= 0
                    or audit["LLAMA"]["grad_norm"] <= 0
                    or (use_anchor and audit["ANCHOR_MLP"]["grad_norm"] <= 0)
                )
                if hard_stop:
                    raise RuntimeError("gradient ownership hard stop")
            grad_norm = float(torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0))
            optimizer.step()
            entry = runtime["entry"]
            if entry["summary_active_count"] != q or entry["physical_summary_length"] != q or entry["padding_attention_count"] != 0:
                raise RuntimeError(f"mask/summary contract failure: {entry}")
            value = float(loss.detach())
            report["LOSSES"].append(value)
            report["SUMMARY_NORMS"].append(runtime["summary_norm"])
            if (step + 1) % 10 == 0:
                print(f"[{arm}] step={step + 1}/{steps} loss={value:.6f} grad={grad_norm:.4f} k={row['k_valid']}", flush=True)

        report["STEPS_COMPLETED"] = len(report["LOSSES"])
        report["FIRST20_MEAN_LOSS"] = float(np.mean(report["LOSSES"][:20]))
        report["LAST20_MEAN_LOSS"] = float(np.mean(report["LOSSES"][-20:]))
        report["LOSS_TREND_DOWN"] = report["LAST20_MEAN_LOSS"] < report["FIRST20_MEAN_LOSS"]
        report["FINAL_SUMMARY_NORM"] = runtime["summary_norm"]
        report["FINAL_ENTRY_AUDIT"] = runtime["entry"]

        # Save the trained Llama/frontend and the arm branch independently.
        checkpoint = output_dir / "checkpoint_step100"
        checkpoint.mkdir()
        torch.save(branch.state_dict(), checkpoint / "geometry_branch.pt")
        saved_branch = model.edge_proj
        model.edge_proj = None
        model.save_pretrained(checkpoint, safe_serialization=True, max_shard_size="2GB")
        model.edge_proj = saved_branch
        tokenizer.save_pretrained(checkpoint)
        report["CHECKPOINT_SAVE_PASS"] = True

        # Exact same-batch forward before reload.
        reload_row = records[(steps * 73) % len(records)]
        model.eval()
        with torch.no_grad():
            before_loss, _, _, _, _, _ = one_forward(model, plugin, tokenizer, reload_row, q, device, runtime, train=False)
        before = float(before_loss)
        v3.module._splice_geometry = original_splice
        del optimizer, model, branch, adapter
        torch.cuda.empty_cache()

        loaded, loaded_branch, _ = build_model(use_anchor, q, device)
        loaded.load_state_dict(
            v3.module.SpatialLMLlamaForCausalLM.from_pretrained(
                checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
            ).state_dict(),
            strict=False,
        )
        loaded_branch.load_state_dict(torch.load(checkpoint / "geometry_branch.pt", map_location=device))
        loaded.eval()
        reload_runtime = {}
        original_splice = install_geometry(loaded, loaded_branch, use_anchor, reload_runtime)
        with torch.no_grad():
            after_loss, ids, labels, prompt_len, surface, edge = one_forward(
                loaded, plugin, tokenizer, reload_row, q, device, reload_runtime, train=False
            )
        after = float(after_loss)
        report["CHECKPOINT_LOAD_PASS"] = math.isfinite(after)
        report["RELOAD_SAME_BATCH_LOSS_BEFORE"] = before
        report["RELOAD_SAME_BATCH_LOSS_AFTER"] = after
        report["RELOAD_LOSS_ABS_DIFF"] = abs(before - after)
        report["RELOAD_FORWARD_MATCH"] = abs(before - after) <= 1e-5

        # Short generation sanity only; this is not model selection or evaluation.
        prompt_ids = ids[:, :prompt_len]
        prompt_attention = torch.ones_like(prompt_ids)
        with torch.no_grad():
            generated = loaded.generate(
                input_ids=prompt_ids,
                attention_mask=prompt_attention,
                point_clouds=surface,
                edge_clouds=edge,
                max_new_tokens=32,
                do_sample=False,
            )
        new_tokens = generated[0, prompt_len:].detach().cpu().tolist()
        eos_id = tokenizer.eos_token_id
        report["GENERATION_SANITY"] = {
            "generate_runnable": True,
            "non_empty": len(new_tokens) > 0,
            "tokens_generated": len(new_tokens),
            "eos_emitted": eos_id in new_tokens if eos_id is not None else False,
            "immediate_catastrophic_loop": len(set(new_tokens[:16])) <= 1 if len(new_tokens) >= 16 else False,
        }
        report["DECODE_PASS"] = report["GENERATION_SANITY"]["non_empty"] and not report["GENERATION_SANITY"]["immediate_catastrophic_loop"]
        report["STATUS"] = "PASS" if (
            report["STEPS_COMPLETED"] == steps
            and report["NAN_COUNT"] == 0
            and report["INF_COUNT"] == 0
            and report["OOM_COUNT"] == 0
            and report["LOSS_TREND_DOWN"]
            and report["CHECKPOINT_SAVE_PASS"]
            and report["CHECKPOINT_LOAD_PASS"]
            and report["RELOAD_FORWARD_MATCH"]
            and report["DECODE_PASS"]
        ) else "FAIL"
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
        (output_dir / "SMOKE_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"LOSSES", "SUMMARY_NORMS"}}, indent=2))
    if report["STATUS"] != "PASS":
        raise SystemExit(2)
