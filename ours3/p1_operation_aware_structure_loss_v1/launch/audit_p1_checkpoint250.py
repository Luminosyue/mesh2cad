#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

import torch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EXP = ROOT / "ours3/p1_operation_aware_structure_loss_v1"
CK = EXP / "runs/p1/checkpoint-250"

sys.path[:0] = [str(ROOT / "SpatialLM"), str(ROOT / "scripts")]
os.environ.update(CAD_SECOND_STREAM="curve_tokens", CAD_USE_SEPARATE_EDGE_TOKENS="1")

from safetensors.torch import load_file
from spatiallm.model.spatiallm_llama import SpatialLMLlamaForCausalLM
from spatiallm_curve_token_v1.curve_projector import build_curve_projector
from transformers import AutoConfig, get_cosine_schedule_with_warmup
from transformers.trainer import ALL_LAYERNORM_LAYERS, get_parameter_names


def main() -> int:
    required = [
        "optimizer.pt",
        "scheduler.pt",
        "trainer_state.json",
        "rng_state.pth",
        "model.safetensors.index.json",
        "config.json",
    ]
    present = {name: (CK / name).is_file() and (CK / name).stat().st_size > 0 for name in required}
    if not all(present.values()):
        report = {"checkpoint": str(CK), "files_present": present, "pass": False}
        (EXP / "audits/P1_CHECKPOINT250_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    config = AutoConfig.from_pretrained(CK, local_files_only=True)
    model = SpatialLMLlamaForCausalLM(config)
    model.edge_proj = build_curve_projector(256, config.hidden_size, getattr(config, "curve_projector_kind", "mlp"))
    model.separate_edge_tokens = True
    model.config.separate_edge_tokens = True
    model.config.curve_token_stream = True
    model.config.curve_token_dim = 256

    weight_map = json.load(open(CK / "model.safetensors.index.json"))["weight_map"]
    state = {}
    for shard in sorted(set(weight_map.values())):
        state.update(load_file(CK / shard, device="cpu"))
    tied_alias_added = False
    if "lm_head.weight" not in state and "model.embed_tokens.weight" in state:
        state["lm_head.weight"] = state["model.embed_tokens.weight"]
        tied_alias_added = True
    model.load_state_dict(state, strict=True)
    model.tie_weights()
    del state

    for p in model.point_backbone.parameters():
        p.requires_grad_(False)
    decay = set(get_parameter_names(model, ALL_LAYERNORM_LAYERS))
    decay = {name for name in decay if "bias" not in name}
    named = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    groups = [
        {"params": [p for name, p in named if name in decay], "weight_decay": 0.0},
        {"params": [p for name, p in named if name not in decay], "weight_decay": 0.0},
    ]
    optimizer = torch.optim.AdamW(groups, lr=2e-5)
    optimizer.load_state_dict(torch.load(CK / "optimizer.pt", map_location="cpu", weights_only=False))
    scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=1200, num_training_steps=39980)
    scheduler.load_state_dict(torch.load(CK / "scheduler.pt", map_location="cpu", weights_only=False))
    trainer_state = json.load(open(CK / "trainer_state.json"))
    rng_state = torch.load(CK / "rng_state.pth", map_location="cpu", weights_only=False)

    edge_keys = sorted(k for k in model.state_dict() if k.startswith("edge_proj."))
    runtime_stats_path = EXP / "audits/P1_RUNTIME_STATS.json"
    runtime_stats = json.load(open(runtime_stats_path)) if runtime_stats_path.is_file() else {}
    effective_path = EXP / "audits/P1_FIRST_EFFECTIVE_UPDATE_AUDIT.json"
    effective = json.load(open(effective_path)) if effective_path.is_file() else {}
    zero_lr_path = EXP / "audits/P1_ZERO_LR_STEP1_AUDIT.json"
    zero_lr = json.load(open(zero_lr_path)) if zero_lr_path.is_file() else {}

    report = {
        "checkpoint": str(CK),
        "GLOBAL_STEP": trainer_state.get("global_step"),
        "files_present": present,
        "MODEL_STRICT_RELOAD": "PASS",
        "tied_lm_head_alias_restored": tied_alias_added,
        "PROJECTOR_RELOAD": "PASS",
        "OPTIMIZER_RELOAD": "PASS",
        "SCHEDULER_RELOAD": "PASS",
        "TRAINER_STATE_RELOAD": "PASS",
        "RNG_RELOAD": "PASS",
        "PROJECTOR_KEYS": len(edge_keys),
        "projector_key_names": edge_keys,
        "PROJECTOR_PARAM_N": sum(p.numel() for p in model.edge_proj.parameters()),
        "MODEL_PARAMETER_COUNT": sum(p.numel() for p in model.parameters()),
        "TRAINABLE_PARAMETER_COUNT": sum(p.numel() for p in model.parameters() if p.requires_grad),
        "optimizer_state_entries": len(optimizer.state),
        "scheduler_last_epoch": scheduler.last_epoch,
        "rng_keys": sorted(rng_state) if isinstance(rng_state, dict) else None,
        "first_effective_update": effective,
        "zero_lr_step1": zero_lr,
        "runtime_stats": runtime_stats,
        "LOSS_RUNTIME_AUDIT": "PASS"
        if runtime_stats.get("means", {}).get("train_op", 0) > 0
        and runtime_stats.get("means", {}).get("train_total", 0) >= runtime_stats.get("means", {}).get("train_base", 0)
        and runtime_stats.get("means", {}).get("eval_total") == runtime_stats.get("means", {}).get("eval_base")
        else "FAIL",
    }
    report["pass"] = (
        all(present.values())
        and report["GLOBAL_STEP"] == 250
        and report["PROJECTOR_KEYS"] == 4
        and report["PROJECTOR_PARAM_N"] == 592128
        and effective.get("FIRST_EFFECTIVE_PROJECTOR_UPDATE") == "PASS"
        and effective.get("C2_HASH_CHANGED") == "NO"
        and report["LOSS_RUNTIME_AUDIT"] == "PASS"
    )
    (EXP / "audits/P1_CHECKPOINT250_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
