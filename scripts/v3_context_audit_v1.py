#!/usr/bin/env python3
"""V3_CONTEXT_AUDIT: run the real train_v3_smoke.encode() on all 800 train rows.

Reports pre-splice tokenisation (what encode() builds) and the 4096 budget
encode() uses to truncate GT. Does not load Sonata / does not retrain.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_geometry_prefix_v3"))

import train_v3_smoke as core  # real markers/encode/SUMMARY_TOKENS

DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
OUT = ROOT / "ours3/v3_context_audit_v1"
ARM = "m2"
CUTOFF = 4096


def pct(a, p):
    return float(np.percentile(a, p))


def audit_row(tok, row, eot_id):
    dsl = Path(row["target_dsl"]).read_text()
    user = core.markers(ARM) + "\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
    prefix = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    prefix_ids = tok.encode(prefix, add_special_tokens=False)
    instr = "Generate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
    instr_ids = tok.encode(instr, add_special_tokens=False)
    target_raw = tok.encode(dsl + "<|eot_id|>", add_special_tokens=False)
    ids, labels, target_n, allowance = core.encode(tok, row, ARM)
    ids_l = ids[0].tolist()
    labels_l = labels[0].tolist()
    target_sup = target_raw[:allowance]
    geometry_extra = row["B1"]["total_llm_input_length"] - row["k_valid"] + core.SUMMARY_TOKENS
    truncated = len(target_raw) > allowance
    eos_in_raw = eot_id in target_raw
    eos_last_raw = bool(target_raw) and target_raw[-1] == eot_id
    eos_in_sup = eot_id in target_sup
    eos_last_sup = bool(target_sup) and target_sup[-1] == eot_id
    eos_in_labels = eot_id in labels_l
    # geometry tokens are -100 after splice; encode() itself puts DSL+EOS in labels
    surface_markers = 3  # point_start, point_pad, point_end
    curve_markers = 3  # reserved_6, reserved_8, reserved_7
    curve_slots_after_adapter = core.SUMMARY_TOKENS
    # encode() budget: post-splice ≈ prompt + geometry_extra + supervised_target
    total_budget = len(prefix_ids) + geometry_extra + len(target_sup)
    return {
        "cad_id": row["cad_id"],
        "operation_count": row["operation_count"],
        "target_dsl_chars": row["target_dsl_chars"],
        "k_valid": row["k_valid"],
        "surface_slots": surface_markers,
        "surface_slots_note": "3 markers; <|point_pad|> expands to Sonata patches at splice",
        "curve_slots": curve_markers,
        "curve_slots_after_adapter": curve_slots_after_adapter,
        "instruction_tokens": len(instr_ids),
        "prompt_tokens": len(prefix_ids),
        "gt_dsl_tokens_raw": len(target_raw),
        "gt_dsl_tokens": target_n,
        "gt_dsl_allowance": allowance,
        "geometry_extra": int(geometry_extra),
        "total_tokens_presplice": len(ids_l),
        "total_tokens": int(total_budget),
        "cutoff": CUTOFF,
        "truncated": truncated,
        "EOS_present": eos_in_raw and eos_last_raw,
        "EOS_supervised": eos_in_sup and eos_last_sup and eos_in_labels,
        "EOS_id": eot_id,
        "EOS_last_raw": eos_last_raw,
        "EOS_in_labels": eos_in_labels,
        "n_label_supervised": int(sum(x != -100 for x in labels_l)),
        "exceeds_cutoff_budget": total_budget > CUTOFF,
    }, {
        "prefix_text": prefix,
        "prefix_ids": prefix_ids,
        "target_raw_head": target_raw[:20],
        "target_raw_tail": target_raw[-8:],
        "target_sup_tail": target_sup[-8:],
        "dsl_head": dsl[:240],
        "dsl_tail": dsl[-240:],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads((DATA / "v3_1k_train.json").read_text())["records"]
    if len(records) != 800:
        raise RuntimeError(f"expected 800 train rows, got {len(records)}")
    tok = AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    eot_id = tok.convert_tokens_to_ids("<|eot_id|>")
    if eot_id is None or int(eot_id) < 0:
        raise RuntimeError("tokenizer missing <|eot_id|>")
    rows = []
    example_extra = None
    for i, rec in enumerate(records):
        item, extra = audit_row(tok, rec, int(eot_id))
        rows.append(item)
        if rec["cad_id"] == "deepcad__0005_00051866":
            example_extra = extra
            example_extra["audit"] = item
        if (i + 1) % 100 == 0:
            print(f"{i+1}/800", flush=True)

    totals = np.asarray([r["total_tokens"] for r in rows], dtype=np.int64)
    raw = np.asarray([r["gt_dsl_tokens_raw"] for r in rows], dtype=np.int64)
    sup = np.asarray([r["gt_dsl_tokens"] for r in rows], dtype=np.int64)
    prompt = np.asarray([r["prompt_tokens"] for r in rows], dtype=np.int64)
    instr = np.asarray([r["instruction_tokens"] for r in rows], dtype=np.int64)
    geo = np.asarray([r["geometry_extra"] for r in rows], dtype=np.int64)
    trunc = [r for r in rows if r["truncated"]]
    eos_p = [r for r in rows if r["EOS_present"]]
    eos_s = [r for r in rows if r["EOS_supervised"]]
    over = [r for r in rows if r["exceeds_cutoff_budget"]]

    def dist(a):
        return {
            "min": int(a.min()),
            "median": float(np.median(a)),
            "p90": pct(a, 90),
            "p95": pct(a, 95),
            "p99": pct(a, 99),
            "max": int(a.max()),
        }

    summary = {
        "TRAIN_COUNT": 800,
        "arm": ARM,
        "encode": "scripts/spatiallm_geometry_prefix_v3/train_v3_smoke.py::encode",
        "cutoff": CUTOFF,
        "SUMMARY_TOKENS": core.SUMMARY_TOKENS,
        "EOS_token": "<|eot_id|>",
        "EOS_id": int(eot_id),
        "TRUNCATED_COUNT": len(trunc),
        "EOS_PRESENT_COUNT": len(eos_p),
        "EOS_SUPERVISED_COUNT": len(eos_s),
        "EXCEEDS_CUTOFF_BUDGET_COUNT": len(over),
        "TOTAL_TOKEN": dist(totals),
        "PROMPT_TOKENS": dist(prompt),
        "INSTRUCTION_TOKENS": dist(instr),
        "GT_DSL_TOKENS_RAW": dist(raw),
        "GT_DSL_TOKENS_SUPERVISED": dist(sup),
        "GEOMETRY_EXTRA": dist(geo),
        "truncated_cad_ids": [r["cad_id"] for r in trunc],
        "truncated_rows": [
            {
                "cad_id": r["cad_id"],
                "ops": r["operation_count"],
                "dsl_chars": r["target_dsl_chars"],
                "gt_dsl_tokens_raw": r["gt_dsl_tokens_raw"],
                "gt_dsl_tokens": r["gt_dsl_tokens"],
                "allowance": r["gt_dsl_allowance"],
                "total_tokens": r["total_tokens"],
                "EOS_supervised": r["EOS_supervised"],
            }
            for r in sorted(trunc, key=lambda x: -x["gt_dsl_tokens_raw"])
        ],
        "definitions": {
            "surface_slots": "3 marker tokens in encode(); <|point_pad|> is replaced by Sonata patches at splice; encode budgets that via B1.total_llm_input_length - k_valid",
            "curve_slots": "3 marker tokens in encode(); <|reserved_special_token_8|> is replaced by 8 adapter summary tokens",
            "instruction_tokens": "tokenised English instruction only",
            "gt_dsl_tokens": "supervised DSL tokens after encode() truncation (includes EOS if it survived)",
            "total_tokens": "encode() post-splice budget = prompt_tokens + geometry_extra + gt_dsl_tokens; training keeps this <= 4096",
            "truncated": "raw DSL+EOS token count > allowance, so target[:allowance] dropped the tail",
            "EOS_present": "raw target (dsl + <|eot_id|>) ends with EOS",
            "EOS_supervised": "truncated target still ends with EOS and that id is in labels",
        },
    }
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "per_cad.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))

    # one complete sample after encode()
    box = next(r for r in rows if r["cad_id"] == "deepcad__0005_00051866")
    ids, labels, _, _ = core.encode(tok, next(x for x in records if x["cad_id"] == "deepcad__0005_00051866"), ARM)
    decoded = tok.decode(ids[0].tolist(), skip_special_tokens=False)
    example = {
        "cad_id": "deepcad__0005_00051866",
        "audit": box,
        "decoded_encode_ids": decoded,
        "n_ids": int(ids.shape[1]),
        "label_supervised_count": int((labels[0] != -100).sum()),
        "last_8_ids": ids[0, -8:].tolist(),
        "last_8_tokens": tok.convert_ids_to_ids(ids[0, -8:].tolist()) if False else tok.convert_ids_to_tokens(ids[0, -8:].tolist()),
        "prefix_extra": example_extra,
    }
    (OUT / "EXAMPLE_encode_deepcad__0005_00051866.json").write_text(json.dumps(example, indent=2) + "\n")
    (OUT / "EXAMPLE_encode_deepcad__0005_00051866.txt").write_text(decoded)

    print(json.dumps({k: summary[k] for k in (
        "TRAIN_COUNT", "TRUNCATED_COUNT", "EOS_PRESENT_COUNT", "EOS_SUPERVISED_COUNT",
        "EXCEEDS_CUTOFF_BUDGET_COUNT", "TOTAL_TOKEN", "GT_DSL_TOKENS_RAW",
        "GT_DSL_TOKENS_SUPERVISED", "PROMPT_TOKENS", "GEOMETRY_EXTRA", "truncated_cad_ids",
    )}, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
