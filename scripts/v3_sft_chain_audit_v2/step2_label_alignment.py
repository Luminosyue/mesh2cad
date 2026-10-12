#!/usr/bin/env python3
"""STEP 2: label / attention / EOS alignment on real encode() + splice.

Writes LABEL_ALIGNMENT_AUDIT.json and LABEL_ALIGNMENT_EXAMPLE.txt
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_geometry_prefix_v3"))
import train_v3_smoke as core
from spatiallm.model.spatiallm_llama import IGNORE_INDEX, _splice_labels

OUT = ROOT / "ours3/v3_sft_chain_audit_v2"
DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
BUDGET = OUT / "GEOMETRY_BUDGET_AUDIT.json"
EXAMPLE_ID = "deepcad__0005_00051866"
MARKERS = [
    "<|point_start|>",
    "<|point_pad|>",
    "<|point_end|>",
    "<|reserved_special_token_6|>",
    "<|reserved_special_token_8|>",
    "<|reserved_special_token_7|>",
    "<|eot_id|>",
]


class StopAtLlamaEntry(Exception):
    pass


def install_capturing(model, arm, state, captured):
    original = core.install_precomputed_second(model, arm, state)
    inner = core.module._splice_geometry

    def capturing(cur_embeds, cur_mask, regions):
        captured["label_regions"] = [(int(s), int(f.shape[0]), int(e)) for s, f, e in regions]
        captured["surface_n"] = int(regions[0][1].shape[0])
        captured["curve_n"] = int(regions[1][1].shape[0]) if len(regions) == 2 else 0
        out_emb, out_mask = inner(cur_embeds, cur_mask, regions)
        captured["spliced_len"] = int(out_emb.shape[0])
        captured["spliced_mask"] = out_mask.detach().cpu()
        return out_emb, out_mask

    core.module._splice_geometry = capturing
    return original


def reconstruct_positions(tok, ids, labels_pre, spliced_labels, spliced_mask, regions, prompt_len):
    """Rebuild a per-position table after geometry splice."""
    ids = ids.tolist()
    labels_pre = labels_pre.tolist()
    spliced_labels = spliced_labels.tolist()
    mask = spliced_mask.tolist()
    pieces = []
    cursor = 0
    geo_kind = []
    for i, (start, n_feat, end) in enumerate(regions):
        kind = "surface" if i == 0 else "curve"
        pieces.append(("text", ids[cursor : start + 1], labels_pre[cursor : start + 1]))
        geo_kind.append((kind, n_feat))
        pieces.append(("geo", [None] * n_feat, [-100] * n_feat))
        cursor = end
    pieces.append(("text", ids[cursor:], labels_pre[cursor:]))

    flat_ids = []
    src_kind = []
    for kind, tok_ids, _labs in pieces:
        if kind == "text":
            for t in tok_ids:
                flat_ids.append(t)
                src_kind.append("text")
        else:
            name, n = geo_kind.pop(0)
            for j in range(n):
                flat_ids.append(None)
                src_kind.append(f"{kind}:{j}")

    if len(flat_ids) != len(spliced_labels):
        raise RuntimeError(f"reconstruct {len(flat_ids)} vs labels {len(spliced_labels)}")

    # prompt positions in PRE-splice ids are [0, prompt_len)
    # After splice, prompt grows by geometry expansion; assistant starts after spliced prompt.
    expansion = sum(n for _, n, _ in regions) - len(regions)  # each region drops (end-start-1? wait)
    # Safer: first supervised label index in spliced_labels
    sup = [i for i, y in enumerate(spliced_labels) if y != IGNORE_INDEX]
    assistant_start = sup[0] if sup else len(spliced_labels)

    rows = []
    for i in range(len(spliced_labels)):
        tid = flat_ids[i]
        is_geo = src_kind[i] != "text"
        if tid is None:
            decoded = f"<{src_kind[i]}>"
        else:
            decoded = tok.convert_ids_to_tokens([tid])[0]
        is_prompt = i < assistant_start
        is_gt = spliced_labels[i] != IGNORE_INDEX
        rows.append(
            {
                "position": i,
                "input_token_id": tid,
                "decoded_token": decoded,
                "label": int(spliced_labels[i]),
                "attention_mask": int(bool(mask[i])),
                "is_geometry_position": is_geo,
                "is_prompt_position": bool(is_prompt and not is_geo),
                "is_assistant_gt_position": is_gt,
                "source": src_kind[i],
            }
        )
    return rows, assistant_start


def checks(rows, eot_id):
    issues = []
    n = len(rows)
    att = [r["attention_mask"] for r in rows]
    labs = [r["label"] for r in rows]
    if n != len(att):
        issues.append("len mismatch table")
    geo = [r for r in rows if r["is_geometry_position"]]
    prompt = [r for r in rows if r["is_prompt_position"]]
    gt = [r for r in rows if r["is_assistant_gt_position"]]
    if any(r["label"] != -100 for r in geo):
        issues.append("geometry label not -100")
    if any(r["label"] != -100 for r in prompt):
        issues.append("prompt/system/user label not -100")
    if any(r["attention_mask"] != 1 for r in rows):
        # V3 M2 summaries are all attended; surface too. padding would be 0.
        pass
    if not gt:
        issues.append("no assistant GT labels")
    decoded_gt = "".join(
        r["decoded_token"] if r["input_token_id"] is not None else ""
        for r in gt
    )
    result_supervised = any(
        (r["decoded_token"] or "").replace("Ġ", "").replace("▁", "") == "result"
        or "result" in (r["decoded_token"] or "")
        for r in gt
    )
    eos_rows = [r for r in gt if r["input_token_id"] == eot_id or r["label"] == eot_id]
    eos_supervised = bool(eos_rows)
    eos_last = bool(gt) and gt[-1]["label"] == eot_id
    pad_over_eos = False
    if eos_rows:
        for r in eos_rows:
            if r["attention_mask"] == 0:
                pad_over_eos = True
                issues.append("padding covered EOS")
    if n != len(labs):
        issues.append("labels length mismatch")
    return {
        "A_prompt_geometry_label_neg100": all(r["label"] == -100 for r in geo + prompt),
        "B_assistant_gt_starts": bool(gt),
        "C_result_supervised": result_supervised,
        "D_eos_supervised": eos_supervised,
        "D_eos_last_gt": eos_last,
        "E_padding_did_not_cover_eos": not pad_over_eos,
        "F_G_H_len_equal": n == len(att) == len(labs),
        "n_positions": n,
        "n_geometry": len(geo),
        "n_prompt": len(prompt),
        "n_gt": len(gt),
        "issues": issues,
        "PASS": not issues and eos_last and result_supervised and all(r["label"] == -100 for r in geo + prompt),
    }


def pick_ids(budget):
    rows = budget["per_cad"]
    ok = [r for r in rows if r.get("surface_encoder_output_tokens") is not None]
    untrunc = [r for r in ok if not r.get("truncated_by_encode")]
    trunc = [r for r in ok if r.get("truncated_by_encode")]
    untrunc_s = sorted(untrunc, key=lambda r: r.get("m2_predicted_spliced_len_full_target") or r.get("gt_dsl_tokens_raw", 0))
    short = untrunc_s[:5]
    # medium: around median
    mid = len(untrunc_s) // 2
    medium = untrunc_s[max(0, mid - 2) : mid + 3]
    trunc_pref = [
        "fusion360__63539_dd7fddaa_0005",
        "fusion360__30400_8824ce97_0007",
        "fusion360__109232_04340d62_0014",
        "fusion360__50409_4a322fbf_0009",
    ]
    trows = []
    have = set()
    for cid in trunc_pref:
        hit = next((r for r in trunc if r["cad_id"] == cid), None)
        if hit:
            trows.append(hit)
            have.add(cid)
    for r in sorted(trunc, key=lambda r: -r["gt_dsl_tokens_raw"]):
        if r["cad_id"] not in have:
            trows.append(r)
        if len(trows) == 5:
            break
    groups = {"short_untruncated": short, "medium_untruncated": medium, "truncated": trows[:5]}
    # always include the example box
    ids = []
    for g in groups.values():
        for r in g:
            ids.append(r["cad_id"])
    if EXAMPLE_ID not in ids:
        ids = [EXAMPLE_ID] + ids
    return groups, ids


def probe_one(model, plugin, tok, row, device):
    arm = "m2"
    user = core.markers(arm) + "\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
    prefix = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    prompt = tok.encode(prefix, add_special_tokens=False)
    ids, labels, target_n, allowance = core.encode(tok, row, arm)
    ids_t = ids.to(device)
    labels_t = labels.to(device)
    att = torch.ones_like(ids_t)
    surface, _ = plugin._load_cad_separate_edge(row["surface_input"])
    surface_t = torch.tensor(surface, device=device).unsqueeze(0)
    state = {}
    second, mask = core.second_input(row, arm)
    state["raw_mask"] = mask
    edge = None if second is None else second.to(device).unsqueeze(0)
    captured = {}
    original = install_capturing(model, arm, state, captured)

    def hook(mod, args, kwargs):
        captured["inputs_embeds_len"] = int(kwargs["inputs_embeds"].shape[1])
        captured["attention_mask_len"] = int(kwargs["attention_mask"].shape[1])
        raise StopAtLlamaEntry()

    handle = model.model.register_forward_pre_hook(hook, with_kwargs=True)
    try:
        try:
            with torch.no_grad():
                model(
                    input_ids=ids_t,
                    attention_mask=att,
                    labels=labels_t,
                    point_clouds=surface_t,
                    edge_clouds=edge,
                )
        except StopAtLlamaEntry:
            pass
    finally:
        handle.remove()
        core.module._splice_geometry = original

    spliced_labels = _splice_labels(labels_t[0], captured["label_regions"], captured["spliced_len"])
    table, assistant_start = reconstruct_positions(
        tok,
        ids[0],
        labels[0],
        spliced_labels.cpu(),
        captured["spliced_mask"],
        captured["label_regions"],
        len(prompt),
    )
    eot = tok.convert_tokens_to_ids("<|eot_id|>")
    chk = checks(table, eot)
    dsl = Path(row["target_dsl"]).read_text()
    result_in_dsl = "result =" in dsl or "result=" in dsl
    return {
        "cad_id": row["cad_id"],
        "truncated_by_encode": target_n < len(tok.encode(dsl + "<|eot_id|>", add_special_tokens=False)),
        "pre_splice_len": int(ids.shape[1]),
        "prompt_tokens": len(prompt),
        "target_supervised": int(target_n),
        "allowance": int(allowance),
        "surface_n": captured["surface_n"],
        "curve_n": captured["curve_n"],
        "inputs_embeds_len": captured.get("inputs_embeds_len"),
        "attention_mask_len": captured.get("attention_mask_len"),
        "spliced_labels_len": int(spliced_labels.shape[0]),
        "H_len_equal": captured.get("inputs_embeds_len")
        == captured.get("attention_mask_len")
        == int(spliced_labels.shape[0]),
        "assistant_start": assistant_start,
        "result_in_gt_dsl": result_in_dsl,
        "checks": chk,
        "table": table,
    }


def tokenizer_report(tok):
    ids = {m: tok.encode(m, add_special_tokens=False) for m in MARKERS}
    conv = {m: tok.convert_tokens_to_ids(m) for m in MARKERS}
    return {
        "bos_token_id": tok.bos_token_id,
        "eos_token_id": tok.eos_token_id,
        "pad_token_id": tok.pad_token_id,
        "bos_token": tok.bos_token,
        "eos_token": tok.eos_token,
        "pad_token": tok.pad_token,
        "special_tokens_map": {k: str(v) for k, v in tok.special_tokens_map.items()},
        "marker_encode_add_special_tokens_false": ids,
        "marker_convert_tokens_to_ids": conv,
        "note": "Llama-3 encode('token') may add a leading 29871/space; convert_tokens_to_ids is the true single id used as marker.",
    }


def write_example(tok, payload):
    lines = [
        f"LABEL_ALIGNMENT_EXAMPLE cad_id={payload['cad_id']}",
        f"pre_splice_len={payload['pre_splice_len']} spliced={payload['inputs_embeds_len']}",
        f"surface_n={payload['surface_n']} curve_n={payload['curve_n']} assistant_start={payload['assistant_start']}",
        f"checks={json.dumps(payload['checks'])}",
        "",
        f"{'pos':>6} {'id':>10} {'label':>10} {'attn':>4} {'geo':>3} {'prm':>3} {'gt':>3} token",
    ]
    for r in payload["table"]:
        lines.append(
            f"{r['position']:6d} {str(r['input_token_id']):>10} {r['label']:10d} {r['attention_mask']:4d} "
            f"{int(r['is_geometry_position']):3d} {int(r['is_prompt_position']):3d} {int(r['is_assistant_gt_position']):3d} {r['decoded_token']}"
        )
    (OUT / "LABEL_ALIGNMENT_EXAMPLE.txt").write_text("\n".join(lines) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not BUDGET.is_file():
        raise RuntimeError("run STEP 1 first")
    budget = json.loads(BUDGET.read_text())
    groups, ids = pick_ids(budget)
    records = {r["cad_id"]: r for r in json.loads((DATA / "v3_1k_train.json").read_text())["records"]}
    tok = core.AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    tok_rep = tokenizer_report(tok)
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(
        point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True
    )
    device = torch.device("cuda:0")
    model = core.make_model("m2", device, 1.9414176940917969)
    per = []
    example = None
    for cid in ids:
        print("align", cid, flush=True)
        payload = probe_one(model, plugin, tok, records[cid], device)
        compact = dict(payload)
        if cid != EXAMPLE_ID:
            compact.pop("table")
        else:
            example = payload
        per.append(compact)
        print(cid, payload["checks"]["PASS"], payload["H_len_equal"], payload["checks"]["issues"], flush=True)
    if example is None:
        example = probe_one(model, plugin, tok, records[EXAMPLE_ID], device)
        per.append({**example, "table": example["table"]})
    write_example(tok, example)
    summary = {
        "groups": {k: [r["cad_id"] for r in v] for k, v in groups.items()},
        "tokenizer": tok_rep,
        "PASS_count": sum(p["checks"]["PASS"] for p in per),
        "len_equal_count": sum(p["H_len_equal"] for p in per),
        "issues": {p["cad_id"]: p["checks"]["issues"] for p in per},
        "per_sample": per,
        "example_cad_id": EXAMPLE_ID,
    }
    (OUT / "LABEL_ALIGNMENT_AUDIT.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("wrote", OUT / "LABEL_ALIGNMENT_AUDIT.json")


if __name__ == "__main__":
    main()
