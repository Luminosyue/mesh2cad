#!/usr/bin/env python3
"""STEP 5: select OVERFIT10 then run TEXT-ONLY / SURFACE-ONLY / M2 overfit.

No official V3 checkpoint resume. Fresh from BASE_MODEL. No Dora. No C2 retrain.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
from pathlib import Path

import types

import numpy as np
import torch
from transformers import LlamaForCausalLM

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_geometry_prefix_v3"))
import train_v3_smoke as core
from cad_execution_failure_audit import staged_execute

OUT = ROOT / "ours3/v3_sft_chain_audit_v2"
DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
BUDGET = OUT / "GEOMETRY_BUDGET_AUDIT.json"
GT = OUT / "GT_EXEC_AUDIT.json"
EOS_IDS = (128001, 128008, 128009)
INSTR = "Generate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
SEED = 42
MARGIN = 1024
TARGET_NORM = 1.9414176940917969


def encode_text(tok, row):
    # Identical instruction cannot uniquely greedy-decode 10 different GTs.
    # CAD_ID is the only extra key; no surface/curve.
    user = f"CAD_ID={row['cad_id']}\n{INSTR}"
    prefix = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    prompt = tok.encode(prefix, add_special_tokens=False)
    target = tok.encode(Path(row["target_dsl"]).read_text() + "<|eot_id|>", add_special_tokens=False)
    ids = torch.tensor([prompt + target], dtype=torch.long)
    labels = torch.tensor([[-100] * len(prompt) + target], dtype=torch.long)
    return ids, labels, len(prompt)


def encode_geo_full(tok, row, arm):
    """Official markers/chat template, but NEVER silent-truncate the CAD target."""
    user = core.markers(arm) + "\n" + INSTR
    prefix = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    prompt = tok.encode(prefix, add_special_tokens=False)
    target = tok.encode(Path(row["target_dsl"]).read_text() + "<|eot_id|>", add_special_tokens=False)
    ids = torch.tensor([prompt + target], dtype=torch.long)
    labels = torch.tensor([[-100] * len(prompt) + target], dtype=torch.long)
    return ids, labels, len(prompt)


def classify(ops):
    ops = list(ops or [])
    has = set(ops)
    if ops == ["Box"] or (len(ops) == 1 and ops[0] == "Box"):
        return "box_only"
    if "Box" in has and "Union" in has:
        return "box_union"
    if "Circle" in has and "Cut" in has:
        return "circle_cut"
    if ("ExtrudePolygon" in has or "Polygon" in has) and "Cut" in has:
        return "polygon_cut"
    if len(ops) >= 3:
        return "multi_op"
    return "other"


def select10():
    budget = {r["cad_id"]: r for r in json.loads(BUDGET.read_text())["per_cad"]}
    gt = {r["cad_id"]: r for r in json.loads(GT.read_text())["per_cad"]}
    train = json.loads((DATA / "v3_1k_train.json").read_text())["records"]
    cand = []
    for rec in train:
        b = budget[rec["cad_id"]]
        g = gt[rec["cad_id"]]
        required = b.get("m2_predicted_spliced_len_full_target")
        if required is None or required > MARGIN:
            continue
        if not b.get("eos_supervised_encode"):
            continue
        if b.get("truncated_by_encode"):
            continue
        if g.get("failure_stage") != "SUCCESS":
            continue
        if not g.get("dsl_execute_success") or not g.get("step_reload_success"):
            continue
        cand.append(
            {
                "cad_id": rec["cad_id"],
                "source_dataset": rec.get("source_dataset"),
                "operation_count": rec.get("operation_count"),
                "operation_names": rec.get("operation_names"),
                "recipe": classify(rec.get("operation_names")),
                "required_m2": required,
                "gt_dsl_tokens_raw": b["gt_dsl_tokens_raw"],
                "surface_encoder_output_tokens": b.get("surface_encoder_output_tokens"),
                "dsl_path": rec["target_dsl"],
            }
        )
    rng = random.Random(SEED)
    cand.sort(key=lambda x: (x["required_m2"], x["cad_id"]))
    picked, used = [], set()
    want_order = ["box_only", "box_union", "circle_cut", "polygon_cut", "multi_op"]
    for recipe in want_order:
        pool = [c for c in cand if c["recipe"] == recipe and c["cad_id"] not in used]
        if not pool:
            continue
        # shortest in-recipe, stable
        chosen = pool[0]
        picked.append(chosen)
        used.add(chosen["cad_id"])
    leftover = [c for c in cand if c["cad_id"] not in used]
    leftover.sort(key=lambda x: (x["required_m2"], x["cad_id"]))
    # Prefer the running-example Box if it is in the clean pool.
    for prefer in ("deepcad__0005_00051866",):
        hit = next((c for c in leftover if c["cad_id"] == prefer), None)
        if hit and len(picked) < 10:
            picked.append(hit)
            used.add(hit["cad_id"])
            leftover = [c for c in leftover if c["cad_id"] not in used]
    seen_ops = {tuple(p["operation_names"] or []) for p in picked}
    # Diversify fillers, still preferring short context.
    for c in leftover:
        if len(picked) == 10:
            break
        key = tuple(c["operation_names"] or [])
        if key in seen_ops:
            continue
        picked.append(c)
        used.add(c["cad_id"])
        seen_ops.add(key)
    for c in leftover:
        if len(picked) == 10:
            break
        if c["cad_id"] in used:
            continue
        picked.append(c)
        used.add(c["cad_id"])
    if len(picked) != 10:
        raise RuntimeError(f"could not select 10 clean CADs, got {len(picked)} from {len(cand)} candidates")
    recs = {r["cad_id"]: r for r in train}
    manifest = {
        "name": "OVERFIT10",
        "seed": SEED,
        "margin_max_m2_tokens": MARGIN,
        "n": 10,
        "cad_ids": [p["cad_id"] for p in picked],
        "rows": picked,
        "selection": {
            "not_truncated": True,
            "eos_complete": True,
            "gt_executable_step_reload": True,
            "total_context_margin": f"required_m2 <= {MARGIN}",
        },
        "records": [recs[p["cad_id"]] for p in picked],
        "candidate_pool": len(cand),
        "recipe_counts_selected": {k: sum(p["recipe"] == k for p in picked) for k in want_order + ["other"]},
    }
    dest = OUT / "overfit10"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "OVERFIT10_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def one_step(model, plugin, tok, row, arm, device, state, train=True):
    if arm == "text":
        ids, labels, prompt_n = encode_text(tok, row)
        ids, labels = ids.to(device), labels.to(device)
        att = torch.ones_like(ids)
        ctx = torch.enable_grad() if train else torch.no_grad()
        with ctx:
            out = model(input_ids=ids, attention_mask=att, labels=labels, point_clouds=None, edge_clouds=None)
        return out.loss, prompt_n, ids, labels
    ids, labels, prompt_n = encode_geo_full(tok, row, arm)
    ids, labels = ids.to(device), labels.to(device)
    att = torch.ones_like(ids)
    surface, _ = plugin._load_cad_separate_edge(row["surface_input"])
    surface = torch.tensor(surface, device=device).unsqueeze(0)
    second, mask = core.second_input(row, arm)
    state["raw_mask"] = mask
    edge = None if second is None else second.to(device).unsqueeze(0)
    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        out = model(
            input_ids=ids,
            attention_mask=att,
            labels=labels,
            point_clouds=surface,
            edge_clouds=edge,
        )
    return out.loss, prompt_n, ids, labels


def decode_row(model, plugin, tok, row, arm, device, state, max_new=1024):
    if arm == "text":
        ids, labels, prompt_n = encode_text(tok, row)
        pids = ids[:, :prompt_n].to(device)
        with torch.no_grad():
            gen = model.generate(
                input_ids=pids,
                attention_mask=torch.ones_like(pids),
                point_clouds=None,
                edge_clouds=None,
                max_new_tokens=max_new,
                do_sample=False,
                use_cache=True,
                eos_token_id=list(EOS_IDS),
                pad_token_id=128001,
            )
    else:
        ids, labels, prompt_n = encode_geo_full(tok, row, arm)
        pids = ids[:, :prompt_n].to(device)
        surface, _ = plugin._load_cad_separate_edge(row["surface_input"])
        surface = torch.tensor(surface, device=device).unsqueeze(0)
        second, mask = core.second_input(row, arm)
        state["raw_mask"] = mask
        edge = None if second is None else second.to(device).unsqueeze(0)
        with torch.no_grad():
            gen = model.generate(
                input_ids=pids,
                attention_mask=torch.ones_like(pids),
                point_clouds=surface,
                edge_clouds=edge,
                max_new_tokens=max_new,
                do_sample=False,
                use_cache=True,
                eos_token_id=list(EOS_IDS),
                pad_token_id=128001,
            )
    new = gen[0, prompt_n:].cpu()
    text = tok.decode(new, skip_special_tokens=True)
    target = Path(row["target_dsl"]).read_text()
    with tempfile.TemporaryDirectory() as d:
        st = staged_execute(text, Path(d))
    return {
        "cad_id": row["cad_id"],
        "exact_match": text.strip() == target.strip(),
        "eos_emitted": bool(new.numel() and int(new[-1]) in EOS_IDS),
        "generated_token_length": int(new.numel()),
        "dsl_parse_success": bool(st["dsl_parse_success"]),
        "dsl_execute_success": bool(st["dsl_execute_success"]),
        "step_reload_success": bool(st["step_reload_success"]),
        "failure_reason": st.get("failure_reason"),
        "generated_head": text[:400],
    }


def eval_all(model, plugin, tok, rows, arm, device, state, work):
    model.eval()
    per = [decode_row(model, plugin, tok, r, arm, device, state) for r in rows]
    model.train()
    n = len(per)
    return {
        "exact": sum(x["exact_match"] for x in per) / n,
        "EOS": sum(x["eos_emitted"] for x in per) / n,
        "parse": sum(x["dsl_parse_success"] for x in per) / n,
        "STEP": sum(x["step_reload_success"] for x in per) / n,
        "per_cad": per,
    }


def train_arm(arm, records, epochs, device, eval_every):
    dest_name = "text_cadid" if arm == "text" else arm
    dest = OUT / "overfit10" / dest_name
    dest.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    random.seed(SEED)
    tok = core.AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    plugin = None
    state = {}
    original = None
    if arm == "text":
        model = core.make_model("b0", device, TARGET_NORM)
        model.edge_proj = None
        # SpatialLM.forward(labels=..., point_clouds=None) raises UnboundLocalError
        # because point_start_end_token_pos is only assigned in the splice branch.
        def _text_forward(self, *args, point_clouds=None, edge_clouds=None, **kwargs):
            kwargs.pop("point_clouds", None)
            kwargs.pop("edge_clouds", None)
            return LlamaForCausalLM.forward(self, *args, **kwargs)

        model.forward = types.MethodType(_text_forward, model)
    else:
        core.heldout_geometry.install()
        plugin = core.get_cad_mm_plugin(
            point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True
        )
        model = core.make_model(arm, device, TARGET_NORM)
        original = core.install_precomputed_second(model, arm, state)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=2e-5, weight_decay=0.0)
    report = {
        "arm": arm,
        "n": len(records),
        "epochs": epochs,
        "lr": 2e-5,
        "optimizer": "AdamW",
        "seed": SEED,
        "fresh_from_official_base": True,
        "resume_v3_checkpoint": False,
        "full_ft_llm": True,
        "frozen": ["point_backbone", "point_proj"] if arm != "text" else ["point_backbone", "point_proj"],
        "trainable": "LLM" if arm == "text" else ("LLM" if arm == "b0" else "LLM+GeometryPrefixAdapter"),
        "no_truncation": True,
        "spatiallm_text_forward": (
            "LlamaForCausalLM.forward workaround; SpatialLM.forward crashes without point_clouds"
            if arm == "text"
            else "native SpatialLM splice"
        ),
        "status": "RUNNING",
        "epochs_report": [],
    }
    try:
        for epoch in range(1, epochs + 1):
            order = list(range(len(records)))
            random.Random(SEED + epoch).shuffle(order)
            losses = []
            for ix in order:
                opt.zero_grad(set_to_none=True)
                loss, _, _, _ = one_step(model, plugin, tok, records[ix], arm, device, state, train=True)
                if not torch.isfinite(loss):
                    raise RuntimeError(f"nonfinite {arm} e{epoch}")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step()
                losses.append(float(loss.detach()))
            item = {"epoch": epoch, "train_ce": float(np.mean(losses))}
            if epoch % eval_every == 0 or epoch == epochs:
                ev = eval_all(model, plugin, tok, records, arm, device, state, dest)
                item.update({k: ev[k] for k in ("exact", "EOS", "parse", "STEP")})
                item["per_cad"] = ev["per_cad"]
                print(
                    f"[{arm}] epoch={epoch}/{epochs} ce={item['train_ce']:.4f} "
                    f"exact={item['exact']:.2f} EOS={item['EOS']:.2f} STEP={item['STEP']:.2f}",
                    flush=True,
                )
                if item["exact"] >= 1.0 and item["EOS"] >= 1.0:
                    report["epochs_report"].append(item)
                    report["early_stop_perfect"] = True
                    break
            else:
                print(f"[{arm}] epoch={epoch}/{epochs} ce={item['train_ce']:.4f}", flush=True)
            report["epochs_report"].append(item)
            (dest / "TRAINING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
        report["status"] = "PASS"
        last = report["epochs_report"][-1]
        report["final"] = {k: last.get(k) for k in ("epoch", "train_ce", "exact", "EOS", "parse", "STEP")}
    except Exception as e:
        report["status"] = "HARD_STOP"
        report["error"] = repr(e)
        raise
    finally:
        if original is not None:
            core.module._splice_geometry = original
        ckpt = dest / "checkpoint"
        dest.mkdir(parents=True, exist_ok=True)
        try:
            model.save_pretrained(ckpt, safe_serialization=True, max_shard_size="2GB")
            tok.save_pretrained(ckpt)
            if arm in ("b1", "m2"):
                torch.save(model.edge_proj.state_dict(), ckpt / "geometry_prefix_adapter.pt")
        except Exception:
            pass
        (dest / "TRAINING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["select", "text", "b0", "m2", "all"], default="select")
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--eval-every", type=int, default=5)
    ap.add_argument("--device", default="cuda:0")
    a = ap.parse_args()
    man_path = OUT / "overfit10" / "OVERFIT10_MANIFEST.json"
    if a.mode == "select" or not man_path.is_file():
        man = select10()
        print("selected", man["cad_ids"])
        if a.mode == "select":
            return
    else:
        man = json.loads(man_path.read_text())
    records = man["records"]
    device = torch.device(a.device)
    if a.mode in ("text", "all"):
        rep = train_arm("text", records, a.epochs, device, a.eval_every)
        if a.mode == "all" and not (
            (rep.get("final") or {}).get("exact", 0) >= 0.9
        ):
            print("TEXT-ONLY exact < 0.9; still running geometry arms because EOS/STEP may already pass")
            (OUT / "overfit10" / "TEXT_EXACT_NOTE.json").write_text(
                json.dumps({"reason": "TEXT_ONLY_EXACT_BELOW_0.9", "final": rep.get("final")}, indent=2) + "\n"
            )
    if a.mode in ("b0", "all"):
        train_arm("b0", records, a.epochs, device, a.eval_every)
    if a.mode in ("m2", "all"):
        train_arm("m2", records, a.epochs, device, a.eval_every)


if __name__ == "__main__":
    main()
