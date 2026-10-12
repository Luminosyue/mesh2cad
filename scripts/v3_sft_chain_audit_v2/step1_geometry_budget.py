#!/usr/bin/env python3
"""STEP 1: real encode()/one_forward geometry-budget audit for V3-1k train 800.

Does not modify Dora, C2, or official V3 artifacts.
Writes ours3/v3_sft_chain_audit_v2/GEOMETRY_BUDGET_AUDIT.json
"""
from __future__ import annotations

import json
import sys
import traceback
import types
from pathlib import Path

import numpy as np
import torch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_geometry_prefix_v3"))
import train_v3_smoke as core
from spatiallm.model.spatiallm_llama import _splice_labels

OUT = ROOT / "ours3/v3_sft_chain_audit_v2"
DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
CANON = core.CANON
CUTOFF = 4096
DUMMY_PROBE_LEN = 8  # V2 gate dummy input_ids used to fill B1.total_llm_input_length
DUMMY_REPLACED = 2  # point_pad + reserved_8
B1_PHYSICAL = 128  # pack_stream padded_length in the V2 probe
FOCUS = [
    "deepcad__0005_00051866",
    "fusion360__63539_dd7fddaa_0005",
    "fusion360__30400_8824ce97_0007",
    "fusion360__109232_04340d62_0014",
    "fusion360__50409_4a322fbf_0009",
]


class StopAtLlamaEntry(Exception):
    pass


def pct(a, p):
    return float(np.percentile(a, p))


def dist(a):
    a = np.asarray(a, dtype=np.float64)
    if a.size == 0:
        return None
    return {
        "min": int(a.min()),
        "median": float(np.median(a)),
        "p90": pct(a, 90),
        "p95": pct(a, 95),
        "p99": pct(a, 99),
        "max": int(a.max()),
    }


def source_of(cad_id: str) -> str:
    if cad_id.startswith("deepcad__"):
        return "deepcad"
    if cad_id.startswith("fusion360__"):
        return "fusion360"
    return "unknown"


def npy_rows(path) -> int:
    p = Path(path)
    if not p.is_file():
        return -1
    arr = np.load(p, mmap_mode="r")
    if hasattr(arr, "files"):
        for key in ("curve_xyz_normalized", "xyz", "samples", "arr_0"):
            if key in arr.files:
                return int(arr[key].shape[0])
        key = arr.files[0]
        return int(arr[key].shape[0])
    return int(arr.shape[0])


def geometry_extra_formula(row) -> int:
    return int(row["B1"]["total_llm_input_length"]) - int(row["k_valid"]) + core.SUMMARY_TOKENS


def inferred_surface_from_b1_probe(row) -> int:
    """Invert the V2 dummy-8 probe: total = (8-2) + S + 128."""
    return int(row["B1"]["total_llm_input_length"]) - (DUMMY_PROBE_LEN - DUMMY_REPLACED + B1_PHYSICAL)


def encode_parts(tok, row, arm):
    dsl = Path(row["target_dsl"]).read_text()
    user = core.markers(arm) + "\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
    prefix = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    prompt = tok.encode(prefix, add_special_tokens=False)
    target_raw = tok.encode(dsl + "<|eot_id|>", add_special_tokens=False)
    ids, labels, target_n, allowance = core.encode(tok, row, arm)
    return {
        "prompt_tokens": len(prompt),
        "gt_dsl_tokens_raw": len(target_raw),
        "target_tokens_supervised": int(target_n),
        "allowance": int(allowance),
        "ids": ids,
        "labels": labels,
        "target_raw": target_raw,
        "eot_id": tok.convert_tokens_to_ids("<|eot_id|>"),
    }


def install_capturing(model, arm, state, captured):
    original = core.install_precomputed_second(model, arm, state)
    inner = core.module._splice_geometry

    def capturing(cur_embeds, cur_mask, regions):
        captured["n_regions"] = len(regions)
        captured["surface_encoder_output_tokens"] = int(regions[0][1].shape[0])
        captured["surface_start_pos"] = int(regions[0][0])
        captured["surface_end_pos"] = int(regions[0][2])
        captured["m2_summary_token_count"] = 0
        captured["b1_llm_slots"] = 0
        if len(regions) == 2:
            captured["m2_summary_token_count"] = int(regions[1][1].shape[0])
            captured["b1_llm_slots"] = int(regions[1][1].shape[0])
            captured["edge_start_pos"] = int(regions[1][0])
            captured["edge_end_pos"] = int(regions[1][2])
        captured["label_regions"] = [
            (int(s), int(f.shape[0]), int(e)) for s, f, e in regions
        ]
        out_emb, out_mask = inner(cur_embeds, cur_mask, regions)
        captured["spliced_len"] = int(out_emb.shape[0])
        captured["spliced_mask_sum"] = int(out_mask.bool().sum())
        captured["spliced_mask_len"] = int(out_mask.shape[0])
        return out_emb, out_mask

    core.module._splice_geometry = capturing
    return original


def probe(model, plugin, tok, row, arm, device, state):
    parts = encode_parts(tok, row, arm)
    ids = parts["ids"].to(device)
    labels = parts["labels"].to(device)
    att = torch.ones_like(ids)
    surface, edge_cloud = plugin._load_cad_separate_edge(row["surface_input"])
    surface_t = torch.tensor(surface, device=device).unsqueeze(0)
    second, mask = core.second_input(row, arm)
    state["raw_mask"] = mask
    edge = None if second is None else second.to(device).unsqueeze(0)
    captured = {
        "pre_splice_len": int(ids.shape[1]),
        "surface_valid_points": int(surface.shape[0]),
        "b1_valid_points_after_plugin": int(edge_cloud.shape[0]) if edge_cloud is not None else 0,
    }
    original = install_capturing(model, arm, state, captured)

    def hook(mod, args, kwargs):
        captured["inputs_embeds_len"] = int(kwargs["inputs_embeds"].shape[1])
        captured["attention_mask_len"] = int(kwargs["attention_mask"].shape[1])
        captured["attention_mask_sum"] = int(kwargs["attention_mask"].sum())
        raise StopAtLlamaEntry()

    handle = model.model.register_forward_pre_hook(hook, with_kwargs=True)
    try:
        try:
            with torch.no_grad():
                model(
                    input_ids=ids,
                    attention_mask=att,
                    labels=labels,
                    point_clouds=surface_t,
                    edge_clouds=edge,
                )
        except StopAtLlamaEntry:
            pass
    finally:
        handle.remove()
        core.module._splice_geometry = original

    lab_regions = captured.get("label_regions", [])
    if lab_regions:
        spliced_labels = _splice_labels(labels[0], lab_regions, captured["spliced_len"])
        captured["spliced_labels_len"] = int(spliced_labels.shape[0])
        captured["n_supervised_after_splice"] = int((spliced_labels != -100).sum())
        eot = parts["eot_id"]
        captured["eos_in_spliced_labels"] = bool((spliced_labels == eot).any())
        captured["eos_last_supervised"] = bool(
            captured["n_supervised_after_splice"]
            and int(spliced_labels[spliced_labels != -100][-1]) == eot
        )
    captured.pop("surface_np", None)
    captured.pop("parts", None)
    return captured


def static_row(tok, row):
    arm = "m2"
    parts = encode_parts(tok, row, arm)
    geo = geometry_extra_formula(row)
    s_inf = inferred_surface_from_b1_probe(row)
    b1_tokens_path = CANON / row["b1_full_tokens"]
    c2_path = Path(row["m2_full_c2_tokens"])
    edge_path = Path(row["b1_full_input"])
    surf_path = Path(row["surface_input"])
    target_raw = parts["gt_dsl_tokens_raw"]
    eot = parts["eot_id"]
    truncated = target_raw > parts["allowance"]
    target_sup = parts["target_raw"][: parts["allowance"]]
    return {
        "cad_id": row["cad_id"],
        "source_dataset": row.get("source_dataset") or source_of(row["cad_id"]),
        "operation_count": row.get("operation_count"),
        "operation_names": row.get("operation_names"),
        "k_valid": int(row["k_valid"]),
        "k_cap": int(row.get("k_cap", 128)),
        "surface_raw_points": npy_rows(surf_path),
        "b1_raw_edge_points": npy_rows(edge_path),
        "b1_valid_k": int(row["k_valid"]),
        "b1_encoder_output_tokens": int(row.get("b1_post_encoder_count", -1)),
        "b1_full_tokens_rows": npy_rows(b1_tokens_path),
        "m2_raw_curve_count": npy_rows(row["m2_full_curves"]),
        "m2_c2_token_count_before_cap": npy_rows(c2_path),
        "m2_c2_token_count_after_cap": int(row["k_valid"]),
        "m2_available_count": int(row.get("m2_available_count", -1)),
        "prompt_tokens": parts["prompt_tokens"],
        "B1_total_llm_input_length": int(row["B1"]["total_llm_input_length"]),
        "B1_physical_padded_length": int(row["B1"].get("physical_padded_length", 128)),
        "B1_second_stream_active": int(row["B1"].get("second_stream_active", row["k_valid"])),
        "B1_total_active_attention": int(row["B1"].get("total_active_attention", -1)),
        "M2_total_llm_input_length": int(row["M2"]["total_llm_input_length"]),
        "geometry_extra": geo,
        "surface_tokens_inferred_from_b1_probe": s_inf,
        "gt_dsl_tokens_raw": target_raw,
        "target_tokens_supervised": parts["target_tokens_supervised"],
        "total_tokens_before_truncation_encode_budget": parts["prompt_tokens"] + geo + target_raw,
        "total_tokens_after_truncation_encode_budget": parts["prompt_tokens"] + geo + parts["target_tokens_supervised"],
        "truncated_by_encode": truncated,
        "eos_supervised_encode": bool(target_sup and target_sup[-1] == eot),
        "allowance": parts["allowance"],
    }


def attach_forward(rec, cap, arm):
    s = int(cap.get("surface_encoder_output_tokens", -1))
    summary = int(cap.get("m2_summary_token_count", 0 if arm == "b0" else core.SUMMARY_TOKENS))
    prompt = rec["prompt_tokens"]
    target_raw = rec["gt_dsl_tokens_raw"]
    target_sup = rec["target_tokens_supervised"]
    # splice: replace 1 pad with S, and (non-b0) replace 1 reserved_8 with summary
    expansion = (s - 1) + (0 if arm == "b0" else (summary - 1))
    rec[f"{arm}_surface_encoder_output_tokens"] = s
    rec[f"{arm}_surface_llm_slots"] = s
    rec[f"{arm}_surface_valid_points"] = cap["surface_valid_points"]
    rec[f"{arm}_inputs_embeds_len"] = cap.get("inputs_embeds_len")
    rec[f"{arm}_attention_mask_len"] = cap.get("attention_mask_len")
    rec[f"{arm}_attention_mask_sum"] = cap.get("attention_mask_sum")
    rec[f"{arm}_spliced_len"] = cap.get("spliced_len")
    rec[f"{arm}_spliced_labels_len"] = cap.get("spliced_labels_len")
    rec[f"{arm}_len_equal"] = (
        cap.get("inputs_embeds_len") == cap.get("attention_mask_len") == cap.get("spliced_labels_len")
    )
    rec[f"{arm}_predicted_spliced_len_after_trunc"] = prompt + expansion + target_sup
    rec[f"{arm}_predicted_spliced_len_full_target"] = prompt + expansion + target_raw
    rec[f"{arm}_geometry_expansion"] = expansion
    rec[f"{arm}_summary_token_count"] = summary
    rec[f"{arm}_accounting_delta"] = (
        None
        if cap.get("inputs_embeds_len") is None
        else int(cap["inputs_embeds_len"]) - (prompt + expansion + target_sup)
    )
    rec[f"{arm}_geometry_extra_vs_real_expansion"] = rec["geometry_extra"] - expansion
    rec[f"{arm}_eos_in_spliced_labels"] = cap.get("eos_in_spliced_labels")
    rec[f"{arm}_eos_last_supervised"] = cap.get("eos_last_supervised")
    return rec


def make_model(arm, device):
    return core.make_model(arm, device, 1.9414176940917969)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads((DATA / "v3_1k_train.json").read_text())["records"]
    if len(records) != 800:
        raise RuntimeError(f"expected 800, got {len(records)}")
    by_id = {r["cad_id"]: r for r in records}
    tok = core.AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(
        point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True
    )
    rows = [static_row(tok, r) for r in records]
    by_rec = {r["cad_id"]: r for r in rows}

    device = torch.device("cuda:0")
    print("loading M2 model", flush=True)
    model = make_model("m2", device)
    state = {}
    for i, rec in enumerate(records, 1):
        item = by_rec[rec["cad_id"]]
        try:
            cap = probe(model, plugin, tok, rec, "m2", device, state)
            attach_forward(item, cap, "m2")
            item["surface_valid_points"] = cap["surface_valid_points"]
            item["surface_encoder_output_tokens"] = item["m2_surface_encoder_output_tokens"]
            item["surface_llm_slots"] = s = item["m2_surface_encoder_output_tokens"]
            item["b1_llm_slots_v3"] = core.SUMMARY_TOKENS
            item["m2_summary_token_count"] = core.SUMMARY_TOKENS
            item["m2_llm_slots"] = core.SUMMARY_TOKENS
            item["real_inputs_embeds_len"] = item["m2_inputs_embeds_len"]
            item["real_geometry_expansion"] = item["m2_geometry_expansion"]
            item["accounting_bug_geometry_extra_minus_real_expansion"] = (
                item["geometry_extra"] - item["m2_geometry_expansion"]
            )
            item["total_tokens_before_truncation"] = item["m2_predicted_spliced_len_full_target"]
            item["total_tokens_after_truncation"] = item["m2_inputs_embeds_len"]
            item["truncated"] = item["truncated_by_encode"]
            item["eos_supervised"] = item["eos_supervised_encode"]
            item["would_fit_full_target"] = item["m2_predicted_spliced_len_full_target"] <= CUTOFF
            item["inferred_vs_measured_surface"] = s - item["surface_tokens_inferred_from_b1_probe"]
        except Exception as e:
            item["forward_error"] = f"{type(e).__name__}: {e}"[-500:]
            item["forward_traceback"] = traceback.format_exc()[-1500:]
        if i % 20 == 0 or rec["cad_id"] in FOCUS:
            print(
                f"{i}/800 {rec['cad_id']} S={item.get('surface_encoder_output_tokens')} "
                f"embeds={item.get('real_inputs_embeds_len')} extra={item['geometry_extra']} "
                f"delta={item.get('accounting_bug_geometry_extra_minus_real_expansion')}",
                flush=True,
            )
    del model
    torch.cuda.empty_cache()

    focus_arms = {}
    for arm in ("b0", "b1", "m2"):
        print("focus arm", arm, flush=True)
        model = make_model(arm, device)
        state = {}
        focus_arms[arm] = {}
        for cid in FOCUS:
            rec = by_id[cid]
            cap = probe(model, plugin, tok, rec, arm, device, state)
            focus_arms[arm][cid] = {
                "surface_encoder_output_tokens": cap.get("surface_encoder_output_tokens"),
                "summary_or_second_tokens": cap.get("m2_summary_token_count", 0),
                "pre_splice_len": cap["pre_splice_len"],
                "inputs_embeds_len": cap.get("inputs_embeds_len"),
                "attention_mask_len": cap.get("attention_mask_len"),
                "spliced_labels_len": cap.get("spliced_labels_len"),
                "attention_mask_sum": cap.get("attention_mask_sum"),
                "len_equal": cap.get("inputs_embeds_len")
                == cap.get("attention_mask_len")
                == cap.get("spliced_labels_len"),
                "eos_in_spliced_labels": cap.get("eos_in_spliced_labels"),
                "prompt_tokens": encode_parts(tok, rec, arm)["prompt_tokens"],
                "target_supervised": encode_parts(tok, rec, arm)["target_tokens_supervised"],
            }
            print(cid, arm, focus_arms[arm][cid], flush=True)
        del model
        torch.cuda.empty_cache()

    measured = [r for r in rows if r.get("surface_encoder_output_tokens") is not None]
    extras = np.asarray([r["geometry_extra"] for r in rows])
    surf = np.asarray([r["surface_encoder_output_tokens"] for r in measured])
    exp = np.asarray([r["real_geometry_expansion"] for r in measured])
    delta = np.asarray([r["accounting_bug_geometry_extra_minus_real_expansion"] for r in measured])
    k = np.asarray([r["k_valid"] for r in measured])
    max_row = max(measured, key=lambda r: r["geometry_extra"])
    answers = {
        "formula": "geometry_extra = B1.total_llm_input_length - k_valid + SUMMARY_TOKENS(8)",
        "B1.total_llm_input_length": (
            "Measured in V2 gate by splicing a dummy 8-token hook "
            "[BOS, point_start, point_pad, point_end, edge_start, reserved_8, edge_end, extra] "
            "with Sonata surface tokens + 128 physically padded B1 slots. "
            "It is NOT the V3 training sequence length and does NOT include CAD DSL."
        ),
        "k_valid": "Number of selected second-stream tokens (min(B1_post_encoder, M2_c2, 128)).",
        "SUMMARY_TOKENS": "V3 GeometryPrefixAdapter always emits 8 summary tokens.",
        "intended_conversion": (
            "Comment claims the 8-token hook recovers geometry contribution, then "
            "swap k_valid second-stream tokens for 8 summaries. The probe actually "
            "inserted 128 physical slots, so subtracting k_valid (not 128) leaves "
            "(128-k_valid) phantom padding inside geometry_extra."
        ),
        "q1_simple_cad_geometry_extra_140": (
            "Simple CADs have compact voxelized surfaces, so Sonata emits ~90-120 "
            "surface tokens. Plus V3's 8 summaries and marker bookkeeping, "
            "geometry_extra lands near 140-230."
        ),
        "q2_complex_cad_3970": (
            "Sonata token count is occupancy-dependent (sparse encoder). Spread-out "
            "Fusion360 clouds occupy many grid cells, so surface_encoder_output_tokens "
            "can approach the 4096 sampled points. That surface stream dominates 3970."
        ),
        "q3_main_contributor": "surface (Sonata), not B1 edges, not M2 summaries",
        "q4_m2_only_8_why_4k": (
            "M2 only adds 8 LLM slots. The 4k budget is almost entirely variable-length "
            "Sonata surface tokens spliced over <|point_pad|>."
        ),
        "q5_arm_lengths": "see focus_arms; B1-V3 and M2 both splice 8 summaries so sequence lengths match; B0 has no second stream",
        "q6_accounting_bug": (
            "YES. geometry_extra systematically exceeds real M2 expansion by about "
            "(128 - k_valid) plus dummy-hook leftovers. Real length is inputs_embeds.shape[1]."
        ),
    }

    # drop bulky caps from json
    for r in rows:
        r.pop("_cap", None)

    focus_full = {cid: by_rec[cid] for cid in FOCUS}
    summary = {
        "TRAIN_COUNT": 800,
        "measured_forward_count": len(measured),
        "forward_failures": [r["cad_id"] for r in rows if r.get("forward_error")],
        "CUTOFF": CUTOFF,
        "SUMMARY_TOKENS": core.SUMMARY_TOKENS,
        "formula_geometry_extra": answers["formula"],
        "GEOMETRY_EXTRA": dist(extras),
        "SURFACE_ENCODER_OUTPUT_TOKENS": dist(surf),
        "REAL_M2_GEOMETRY_EXPANSION": dist(exp),
        "GEOMETRY_EXTRA_MINUS_REAL_EXPANSION": dist(delta),
        "K_VALID": dist(k),
        "REAL_INPUTS_EMBEDS_LEN": dist([r["real_inputs_embeds_len"] for r in measured]),
        "INFERRED_VS_MEASURED_SURFACE": dist([r["inferred_vs_measured_surface"] for r in measured]),
        "max_geometry_extra_row": {
            "cad_id": max_row["cad_id"],
            "geometry_extra": max_row["geometry_extra"],
            "surface_encoder_output_tokens": max_row.get("surface_encoder_output_tokens"),
            "k_valid": max_row["k_valid"],
            "B1_total_llm_input_length": max_row["B1_total_llm_input_length"],
            "real_geometry_expansion": max_row.get("real_geometry_expansion"),
            "real_inputs_embeds_len": max_row.get("real_inputs_embeds_len"),
        },
        "truncated_by_encode": sum(r["truncated_by_encode"] for r in rows),
        "would_fit_full_target_m2": sum(bool(r.get("would_fit_full_target")) for r in rows),
        "answers": answers,
        "focus_ids": FOCUS,
        "focus_arms": focus_arms,
        "focus_full": focus_full,
        "per_cad": rows,
    }
    (OUT / "GEOMETRY_BUDGET_AUDIT.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    (OUT / "GEOMETRY_BUDGET_per_cad.jsonl").write_text("".join(json.dumps(r, default=str) + "\n" for r in rows))
    print("wrote", OUT / "GEOMETRY_BUDGET_AUDIT.json", "measured", len(measured), flush=True)


if __name__ == "__main__":
    main()
