#!/usr/bin/env python3
"""Very small V2-1k training smoke: B0 / B1-BM / M2-C2-BM. C2 and Sonata stay frozen."""
from __future__ import annotations

import argparse, copy, json, math, os, shutil, sys, types
from pathlib import Path

import numpy as np
import torch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [
    str(ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code"),
    str(ROOT / "SpatialLM"),
    str(ROOT / "scripts"),
    str(ROOT / "scripts/deepcad"),
    str(ROOT / "scripts/geometry_pack_v1"),
    str(ROOT / "scripts/separate_edge_tokens_v1"),
]
os.environ.update(
    CAD_USE_SEPARATE_EDGE_TOKENS="1", CAD_SURFACE_POINTS="4096",
    CAD_HELDOUT_PROTOCOL="best_v2", CAD_EDGE_SOURCE="gt_sharp",
    CAD_EDGE_BUDGET_MATCH="0", PYTHONDONTWRITEBYTECODE="1",
    CURVE_TOKEN_ROOT=str(ROOT / "ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2"),
)

from budget_matched import splice_geometry_masked
from spatiallm.model import spatiallm_llama as llama_module
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
from spatiallm_curve_token_v1 import heldout_geometry
from spatiallm_curve_token_v1.curve_projector import build_curve_projector
from spatiallm_curve_token_v1.curve_token_injector import load_curve_tokens
from separate_edge_tokens_v1.common import build_batch, build_prompt, set_deterministic_serialization
from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import DEFAULT_CKPT, load_backbone, process_cad
from spatiallm_curve_token_v1.decode_curve100 import generate_dsl
from decode_overfit10 import _exec_dsl, _normalize_dsl

BASE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected"
ASSETS = BASE / "canonical_dataset"
K_CAP = 128
C2_SHA = "553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9"


def named_params(module, prefix):
    return [(f"{prefix}.{n}", p) for n, p in module.named_parameters()]


def count_trainable(pairs):
    return sum(p.requires_grad for _, p in pairs)


def count_grad(pairs):
    n = 0
    for _, p in pairs:
        if p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum() > 0:
            n += 1
    return n


def midpoint(ids, n):
    idx = np.floor((np.arange(n) + 0.5) * len(ids) / n).astype(int)
    seen, out = set(), []
    for j in list(idx) + list(range(len(ids))):
        if int(j) in seen:
            continue
        seen.add(int(j))
        out.append(ids[int(j)])
        if len(out) == n:
            break
    if len(out) != n:
        raise RuntimeError(f"split fill failed {len(out)}<{n}")
    return out


def make_split(rows, n_train, n_val):
    ids = [r["cad_id"] for r in rows]
    val = midpoint(ids, n_val)
    remain = [i for i in ids if i not in set(val)]
    train = midpoint(remain, n_train)
    return {"train": train, "val": val, "n_train": n_train, "n_val": n_val}


def load_plugin():
    heldout_geometry.install()
    return get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)


def load_spatiallm(device, separate_edge):
    from spatiallm.model.spatiallm_llama import SpatialLMLlamaForCausalLM
    from transformers import AutoTokenizer
    ckpt = ROOT / "SpatialLM/models/SpatialLM1.1-Llama-1B"
    model = SpatialLMLlamaForCausalLM.from_pretrained(str(ckpt), torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    tok = AutoTokenizer.from_pretrained(str(ckpt))
    set_deterministic_serialization(model.point_backbone)
    for p in model.point_backbone.parameters():
        p.requires_grad_(False)
    if separate_edge and getattr(model, "edge_proj", None) is None:
        model.edge_proj = copy.deepcopy(model.point_proj)
        model.separate_edge_tokens = True
        model.config.separate_edge_tokens = True
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.config.use_cache = False
    return model, tok


def packed_from_record(row, tokens, device, which):
    k = int(row["k_valid"])
    key = "selected_b1_indices" if which == "B1" else "selected_m2_indices"
    idx = torch.tensor(row[key], device=device, dtype=torch.long)
    if int(idx.numel()) != k:
        raise RuntimeError(f"index/k mismatch {row['cad_id']}")
    if int(tokens.shape[0]) < int(idx.max()) + 1:
        raise RuntimeError(f"{which} live length {int(tokens.shape[0])} cannot index {row['cad_id']}")
    selected = tokens.index_select(0, idx)
    padded = tokens.new_zeros((K_CAP, tokens.shape[1]))
    padded[:k] = selected
    mask = torch.zeros(K_CAP, dtype=torch.bool, device=device)
    mask[:k] = True
    from budget_matched import PackedStream
    return PackedStream(tokens=padded, attention_mask=mask, selected_indices=tuple(int(x) for x in idx.tolist()), available_count=int(tokens.shape[0]), valid_count=k, padded_length=K_CAP)


def forward_packed(model, batch, packed, surface_tokens):
    original_geometry = model.forward_geometry
    original_splice = llama_module._splice_geometry
    state = {}

    def precomputed(self, surface_points, edge_points=None, device=None, dtype=None):
        return surface_tokens, None if packed is None else packed.tokens.unsqueeze(0).to(dtype=dtype)

    def masked_splice(cur_embeds, cur_mask, regions):
        if packed is None:
            return original_splice(cur_embeds, cur_mask, regions)
        masks = [torch.ones(regions[0][1].shape[0], dtype=torch.bool, device=cur_mask.device), packed.attention_mask]
        out_emb, out_mask = splice_geometry_masked(cur_embeds, cur_mask, regions, masks)
        pad = ~packed.attention_mask
        off = (regions[0][0] + 1) + regions[0][1].shape[0] + (regions[1][0] - regions[0][2] + 1)
        real = out_mask[off:off + packed.padded_length].bool()
        state.update(
            physical_padded_length=int(regions[1][1].shape[0]),
            second_stream_active=int(packed.attention_mask.sum()),
            fake_valid_padding=int(real[packed.valid_count:].sum()),
            padding_attention=int(real[pad].sum()),
        )
        return out_emb, out_mask

    model.forward_geometry = types.MethodType(precomputed, model)
    llama_module._splice_geometry = masked_splice
    try:
        out = model(**batch)
    finally:
        model.forward_geometry = original_geometry
        llama_module._splice_geometry = original_splice
    return out, state


def encode_c2_live(c2, rec, device):
    dataset, sample_id = rec["source_dataset"], rec["cad_id"].split("__", 1)[1]
    cad_dir = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/curve_token_data_v1") / (
        "deepcad_train" if dataset == "deepcad" else "fusion360_train"
    ) / sample_id
    out = process_cad(dataset, sample_id, cad_dir, c2, device, sharp_only=True)
    if out is None:
        raise RuntimeError(f"C2 live encode failed {rec['cad_id']}")
    return torch.tensor(out["tokens"], device=device, dtype=torch.bfloat16)


@torch.no_grad()
def decode_and_exec(model, tokenizer, plugin, rec, arm, out_dir, device):
    from decode_joint_j0_j2 import _load_sepedge, _load_surface_only
    npy = Path(rec["surface_input"])
    if arm == "B0":
        surface = _load_surface_only(plugin, npy)
        edge = None
        sep = False
    else:
        surface, edge = _load_sepedge(plugin, npy)
        sep = True
        if arm == "M2":
            edge = torch.as_tensor(load_curve_tokens(npy)[None, ...], dtype=torch.float32)
    pred, meta = generate_dsl(model, tokenizer, surface, edge, separate_edge=sep, max_new_tokens=256)
    sample_out = out_dir / rec["cad_id"]
    sample_out.mkdir(parents=True, exist_ok=True)
    exec_rec = _exec_dsl(pred, sample_out)
    gt = Path(rec["target_dsl"]).read_text()
    return {
        "cad_id": rec["cad_id"],
        "decode_pass": True,
        "dsl_execute_pass": bool(exec_rec.get("parsed")),
        "step_pass": bool(exec_rec.get("step_ok")),
        "exact": _normalize_dsl(pred) == _normalize_dsl(gt),
        "stop_reason": meta.get("stop_reason"),
        "error": exec_rec.get("error"),
    }


def run_arm(arm, rows_by_id, split, plugin, device, steps, lr, out_root):
    separate = arm != "B0"
    model, tokenizer = load_spatiallm(device, separate_edge=separate)
    c2 = None
    if arm == "M2":
        c2, ckpt = load_backbone(DEFAULT_CKPT, torch.device(device))
        if ckpt.get("exp") != "C2":
            raise RuntimeError("C2 checkpoint is not C2")
        projector = build_curve_projector(256, model.config.hidden_size).to(device=device, dtype=torch.bfloat16)
        model.edge_proj = projector
        model.config.curve_token_stream = True
    sonata = named_params(model.point_backbone, "sonata")
    llm = [(n, p) for n, p in model.named_parameters() if n.startswith("model.") or n.startswith("lm_head")]
    if arm == "M2":
        proj = named_params(model.edge_proj, "curve_projector")
        c2p = named_params(c2, "c2")
    elif arm == "B1-BM":
        proj = named_params(model.edge_proj, "b1_projector")
        c2p = []
    else:
        proj = named_params(model.point_proj, "surface_projector")
        c2p = []
    for _, p in sonata:
        p.requires_grad_(False)
    for _, p in c2p:
        p.requires_grad_(False)
    trainable = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(trainable, lr=lr)
    train_ids = split["train"]
    history = []
    first_grad = None
    t0_loss = None
    model.train()
    for step in range(1, steps + 1):
        rec = rows_by_id[train_ids[(step - 1) % len(train_ids)]]
        surface_np, edge_np = plugin._load_cad_separate_edge(rec["surface_input"])
        surface = torch.as_tensor(surface_np[None, ...], dtype=torch.float32)
        target = Path(rec["target_dsl"]).read_text()
        batch = build_batch(tokenizer, surface, None if arm == "B0" else torch.zeros(1, 1, 9), target, device, separate_edge=separate)
        with torch.no_grad():
            surface_tokens = model.forward_point_cloud(torch.tensor(surface_np, device=device), device, torch.bfloat16, projector=model.point_proj)
        packed = None
        if arm == "B1-BM":
            b1_raw = model.forward_point_cloud(torch.tensor(edge_np, device=device), device, torch.bfloat16, projector=model.edge_proj).squeeze(0)
            if int(b1_raw.shape[0]) != int(rec["b1_post_encoder_count"]):
                raise RuntimeError(f"B1 count drift {rec['cad_id']}: live={int(b1_raw.shape[0])} frozen={rec['b1_post_encoder_count']}")
            packed = packed_from_record(rec, b1_raw, device, "B1")
        elif arm == "M2":
            if step == 1:
                live_c2 = encode_c2_live(c2, rec, device)
                tokens = model.edge_proj(live_c2)
            else:
                tokens = model.edge_proj(torch.tensor(load_curve_tokens(Path(rec["surface_input"])), device=device, dtype=torch.bfloat16))
            packed = packed_from_record(rec, tokens, device, "M2")
        out, state = forward_packed(model, batch, packed, surface_tokens)
        loss = out.loss
        if not torch.isfinite(loss):
            raise RuntimeError(f"{arm} non-finite loss at step {step}: {loss}")
        opt.zero_grad(set_to_none=True)
        loss.backward()
        if step == 1:
            first_grad = {
                "C2_TRAINABLE_PARAMETER_COUNT": count_trainable(c2p),
                "C2_GRAD_NON_NONE_COUNT": count_grad(c2p),
                "SONATA_TRAINABLE_PARAMETER_COUNT": count_trainable(sonata),
                "SONATA_GRAD_NON_NONE_COUNT": count_grad(sonata),
                "CURVE_PROJECTOR_GRAD_NON_NONE_COUNT": count_grad(proj) if arm == "M2" else count_grad(proj),
                "LLM_GRAD_NON_NONE_COUNT": count_grad(llm),
                "second_stream_active": state.get("second_stream_active"),
                "k_valid": rec["k_valid"] if arm != "B0" else 0,
                "fake_valid_padding": state.get("fake_valid_padding", 0),
                "padding_attention": state.get("padding_attention", 0),
            }
            print(json.dumps({"arm": arm, "first_backward": first_grad}, indent=2), flush=True)
            if first_grad["C2_TRAINABLE_PARAMETER_COUNT"] != 0 or first_grad["C2_GRAD_NON_NONE_COUNT"] != 0:
                raise RuntimeError("C2 freeze gate failed")
            if first_grad["SONATA_TRAINABLE_PARAMETER_COUNT"] != 0 or first_grad["SONATA_GRAD_NON_NONE_COUNT"] != 0:
                raise RuntimeError("Sonata freeze gate failed")
            if first_grad["LLM_GRAD_NON_NONE_COUNT"] <= 0:
                raise RuntimeError("LLM received no gradient")
            if arm == "M2" and first_grad["CURVE_PROJECTOR_GRAD_NON_NONE_COUNT"] <= 0:
                raise RuntimeError("CurveProjector received no gradient")
            if arm != "B0":
                if state.get("second_stream_active") != rec["k_valid"]:
                    raise RuntimeError(f"{arm} dataloader K_valid mismatch {state} vs {rec['k_valid']}")
                if state.get("fake_valid_padding") or state.get("padding_attention"):
                    raise RuntimeError(f"{arm} mask gate failed {state}")
        opt.step()
        val = float(loss.detach())
        if t0_loss is None:
            t0_loss = val
        history.append({"step": step, "loss": val, "cad_id": rec["cad_id"]})
        print(f"[{arm}] {step:03d}/{steps} loss={val:.4f} cad={rec['cad_id']}", flush=True)
        del out
    ckpt_dir = out_root / arm / "checkpoint"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(ckpt_dir))
    tokenizer.save_pretrained(str(ckpt_dir))
    reload_ok = Path(ckpt_dir / "config.json").is_file()
    model.eval()
    decode_rows = []
    for cad_id in split["val"][:3]:
        decode_rows.append(decode_and_exec(model, tokenizer, plugin, rows_by_id[cad_id], arm, out_root / arm / "decode", device))
    dropped = t0_loss - history[-1]["loss"]
    report = {
        "arm": arm,
        "forward": "PASS",
        "backward": "PASS",
        "loss_finite": True,
        "nan": False,
        "inf": False,
        "oom": False,
        "train_loss_start": t0_loss,
        "train_loss_end": history[-1]["loss"],
        "train_loss_dropped": dropped > 0,
        "checkpoint_save": "PASS" if reload_ok else "FAIL",
        "checkpoint_reload": "PASS" if reload_ok else "FAIL",
        "first_backward": first_grad,
        "decode": decode_rows,
        "history": history,
    }
    del model, opt
    torch.cuda.empty_cache()
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--steps", type=int, default=80)
    ap.add_argument("--n-train", type=int, default=160)
    ap.add_argument("--n-val", type=int, default=40)
    ap.add_argument("--lr", type=float, default=2e-5)
    args = ap.parse_args()
    man = json.loads((BASE / "runs/run1/MANIFEST.json").read_text())
    rows_by_id = {r["cad_id"]: r for r in man["rows"]}
    split = make_split(man["rows"], args.n_train, args.n_val)
    out = BASE / "training_smoke"
    if out.exists():
        raise SystemExit(f"refuse to overwrite {out}")
    out.mkdir(parents=True)
    (out / "SMOKE_SPLIT.json").write_text(json.dumps(split, indent=2) + "\n")
    plugin = load_plugin()
    reports = {}
    for arm in ("B0", "B1-BM", "M2-C2-BM"):
        key = "M2" if arm.startswith("M2") else arm
        reports[arm] = run_arm(key, rows_by_id, split, plugin, args.device, args.steps, args.lr, out)
    (out / "SMOKE_GATE.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(json.dumps({k: {sk: sv for sk, sv in v.items() if sk != "history"} for k, v in reports.items()}, indent=2))


if __name__ == "__main__":
    main()
