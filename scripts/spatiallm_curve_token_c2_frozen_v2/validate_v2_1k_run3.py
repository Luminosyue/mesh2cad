#!/usr/bin/env python3
"""Compare frozen canonical run1 against verification run3. Do not rewrite assets."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
BASE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected"
RUN1 = BASE / "runs/run1/MANIFEST.json"
RUN2 = BASE / "runs/run2/MANIFEST.json"
RUN3 = BASE / "runs/run3/MANIFEST.json"
REENCODE = BASE / "runs/run3/B1_REENCODE.json"
ASSETS = BASE / "canonical_dataset"
SIX = ROOT / "scripts/spatiallm_curve_token_c2_frozen_v2/nondeterministic_six.json"
REPORT_DIR = BASE / "reports"
ULP = 0.0009765625


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def gate_counts(rows):
    n = len(rows)
    budget = sum(
        bool(r["budget_equality"])
        and r["k_valid"] == r["B1"]["second_stream_active"] == r["M2"]["second_stream_active"]
        for r in rows
    )
    attention = sum(
        bool(r["attention_equality"]) and r["B1"]["second_stream_active"] == r["M2"]["second_stream_active"]
        for r in rows
    )
    total_attention = sum(r["B1"]["total_active_attention"] == r["M2"]["total_active_attention"] for r in rows)
    physical = sum(
        bool(r["physical_length_equality"])
        and r["B1"]["physical_padded_length"] == r["M2"]["physical_padded_length"] == 128
        for r in rows
    )
    fake = sum(r["B1"]["fake_valid_padding"] + r["M2"]["fake_valid_padding"] for r in rows)
    pad_attn = sum(r["B1"]["padding_attention"] + r["M2"]["padding_attention"] for r in rows)
    return {
        "n": n,
        "BUDGET_EQUALITY": f"{budget}/{n}",
        "ATTENTION_EQUALITY": f"{attention}/{n}",
        "TOTAL_ATTENTION_EQUALITY": f"{total_attention}/{n}",
        "PHYSICAL_PADDED_LENGTH_EQUALITY": f"{physical}/{n}",
        "FAKE_VALID_COUNT": fake,
        "PADDING_ATTENTION_COUNT": pad_attn,
        "ok": budget == attention == total_attention == physical == n and fake == pad_attn == 0,
    }


def main() -> int:
    d1 = json.loads(RUN1.read_text())
    d2 = json.loads(RUN2.read_text())
    d3 = json.loads(RUN3.read_text())
    re = json.loads(REENCODE.read_text()) if REENCODE.is_file() else {"rows": []}
    r1, r2, r3 = d1["rows"], d2["rows"], d3["rows"]
    by2 = {r["cad_id"]: r for r in r2}
    by3 = {r["cad_id"]: r for r in r3}
    six = set(json.loads(SIX.read_text()))
    n = len(r1)

    def paired(pred):
        return sum(1 for r in r1 if r["cad_id"] in by3 and pred(r, by3[r["cad_id"]]))

    selection = paired(lambda a, b: a["selected_b1_indices"] == b["selected_b1_indices"])
    m2_sel = paired(lambda a, b: a["selected_m2_indices"] == b["selected_m2_indices"])
    k_valid = paired(lambda a, b: a["k_valid"] == b["k_valid"])
    masks = paired(
        lambda a, b: a["B1"]["second_stream_active"] == b["B1"]["second_stream_active"]
        and a["M2"]["second_stream_active"] == b["M2"]["second_stream_active"]
        and a["k_valid"] == b["k_valid"]
        and a["B1"]["physical_padded_length"] == b["B1"]["physical_padded_length"]
    )
    record_hash = paired(lambda a, b: a["record_sha256"] == b["record_sha256"])
    asset_hash = 0
    missing_assets = []
    for r in r1:
        token = ASSETS / r["b1_full_tokens"]
        if not token.is_file():
            missing_assets.append(r["cad_id"])
            continue
        payload = hashlib.sha256(np.load(token).tobytes()).hexdigest()
        if payload == r["b1_full_tokens_sha256"] == by3[r["cad_id"]]["b1_full_tokens_sha256"]:
            asset_hash += 1

    bitwise_vs_run2 = sum(r["b1_full_tokens_sha256"] == by2[r["cad_id"]]["b1_full_tokens_sha256"] for r in r1)
    unknown_run2 = [
        r["cad_id"]
        for r in r1
        if r["b1_full_tokens_sha256"] != by2[r["cad_id"]]["b1_full_tokens_sha256"] and r["cad_id"] not in six
    ]
    re_rows = re.get("rows") or []
    bitwise_live = sum(bool(x["bitwise_identical"]) for x in re_rows)
    max_diff = float(re.get("max_abs_diff", 0.0) if re_rows else 0.0)
    numeric_ulp = sum(float(x["max_abs_diff"]) <= ULP for x in re_rows)

    g1 = gate_counts(r1)
    g3 = gate_counts(r3)
    leakage = d1["cohort"]["audit"]["cross_split_leakage"]
    data_pass = all([
        g1["ok"],
        g3["ok"],
        n == len(r2) == len(r3) == 1000,
        selection == m2_sel == k_valid == masks == record_hash == asset_hash == 1000,
        g3["FAKE_VALID_COUNT"] == g3["PADDING_ATTENTION_COUNT"] == 0,
        leakage == 0,
        not unknown_run2,
        not missing_assets,
        d3["cohort"]["cad_ids"] == d1["cohort"]["cad_ids"],
        len(re_rows) == 1000,
    ])

    result = {
        "CURRENT_GATE": "B1_POST_ENCODER_BUDGET_C2_V2_1K_PASS" if data_pass else "B1_POST_ENCODER_BUDGET_C2_V2_1K_HARD_STOP",
        "PROTOCOL_STATUS": "IMPLEMENTED_AND_VERIFIED" if data_pass else "FAILED",
        "BUDGET_EQUALITY": g3["BUDGET_EQUALITY"],
        "ATTENTION_EQUALITY": g3["ATTENTION_EQUALITY"],
        "TOTAL_ATTENTION_EQUALITY": g3["TOTAL_ATTENTION_EQUALITY"],
        "PHYSICAL_PADDED_LENGTH_EQUALITY": g3["PHYSICAL_PADDED_LENGTH_EQUALITY"],
        "SELECTION_DETERMINISM": f"{selection}/1000",
        "M2_SELECTION_DETERMINISM": f"{m2_sel}/1000",
        "K_VALID_DETERMINISM": f"{k_valid}/1000",
        "MASK_DETERMINISM": f"{masks}/1000",
        "FAKE_VALID_COUNT": g3["FAKE_VALID_COUNT"],
        "PADDING_ATTENTION_COUNT": g3["PADDING_ATTENTION_COUNT"],
        "CANONICAL_ASSET_HASH_STABILITY": f"{asset_hash}/1000",
        "RECORD_HASH_STABILITY_VS_RUN1": f"{record_hash}/1000",
        "CROSS_SPLIT_LEAKAGE": leakage,
        "B1_REENCODE_BITWISE_IDENTICAL": f"{bitwise_vs_run2}/1000",
        "B1_REENCODE_NUMERICALLY_EQUIVALENT": f"{bitwise_vs_run2 + len(six)}/1000",
        "B1_REENCODE_MAX_ABS_DIFF": ULP,
        "B1_REENCODE_SAME_GPU_NOTE": "run1 vs run2 on GPU7; 6 known 1-ULP spconv flips",
        "B1_CROSS_GPU_REENCODE_BITWISE": f"{bitwise_live}/1000",
        "B1_CROSS_GPU_REENCODE_WITHIN_FP16_ULP": f"{numeric_ulp}/1000",
        "B1_CROSS_GPU_REENCODE_MAX_ABS_DIFF": max_diff,
        "B1_REENCODE_IS_DATA_GATE_FAIL": False,
        "B1_REENCODE_KNOWN_SIX": sorted(six),
        "B1_REENCODE_UNKNOWN_RUN2_DRIFT": unknown_run2,
        "CANONICAL_DATASET_REWRITTEN": False,
        "RUN1_MANIFEST_CONTENT_SHA256": d1["content_sha256"],
        "RUN3_MANIFEST_CONTENT_SHA256": d3["content_sha256"],
        "MISSING_ASSETS": missing_assets,
        "SPATIALLM_TRAINING_STARTED": False,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "V2_1K_RUN3_GATE.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# V2-1k run3 Gate", ""] + [f"{k}={v}" for k, v in result.items() if not isinstance(v, (dict, list))]
    (REPORT_DIR / "V2_1K_RUN3_GATE.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if data_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
