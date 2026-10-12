#!/usr/bin/env python3
"""STEP 3: V3_NO_TRUNC_DEBUG manifest. Skip samples whose FULL DSL+EOS cannot fit.

Does not modify official v3_1k_train.json.
Uses REAL M2 splice budget from STEP 1, not the encode() geometry_extra heuristic.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/v3_sft_chain_audit_v2"
DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
BUDGET = OUT / "GEOMETRY_BUDGET_AUDIT.json"
CUTOFF = 4096


def main():
    dest = OUT / "no_trunc_debug"
    dest.mkdir(parents=True, exist_ok=True)
    budget = json.loads(BUDGET.read_text())
    train = json.loads((DATA / "v3_1k_train.json").read_text())
    recs = {r["cad_id"]: r for r in train["records"]}
    kept, removed = [], []
    for r in budget["per_cad"]:
        cid = r["cad_id"]
        src = recs[cid]
        required = r.get("m2_predicted_spliced_len_full_target")
        embeds = r.get("real_inputs_embeds_len")
        if required is None:
            removed.append(
                {
                    "cad_id": cid,
                    "reason": "FORWARD_FAILED_CANNOT_BUDGET",
                    "forward_error": r.get("forward_error"),
                    "full_target_preserved": False,
                    "eos_supervised": False,
                }
            )
            continue
        if required > CUTOFF:
            removed.append(
                {
                    "cad_id": cid,
                    "reason": "FULL_TARGET_EXCEEDS_MAX_CONTEXT",
                    "required_tokens": required,
                    "cutoff": CUTOFF,
                    "surface_encoder_output_tokens": r.get("surface_encoder_output_tokens"),
                    "gt_dsl_tokens_raw": r["gt_dsl_tokens_raw"],
                    "prompt_tokens": r["prompt_tokens"],
                    "geometry_expansion": r.get("real_geometry_expansion"),
                    "truncated_by_old_encode": r["truncated_by_encode"],
                    "full_target_preserved": False,
                    "eos_supervised": False,
                }
            )
            continue
        kept.append(src)
    manifest = {
        "name": "V3_NO_TRUNC_DEBUG",
        "protocol": "skip_if_full_cad_dsl_plus_eos_exceeds_4096",
        "official_v3_train_untouched": True,
        "official_train": str(DATA / "v3_1k_train.json"),
        "original_train_count": 800,
        "kept_count": len(kept),
        "removed_count": len(removed),
        "removed_ids": [x["cad_id"] for x in removed],
        "removed": removed,
        "full_target_preserved": True,
        "eos_supervised": True,
        "silent_truncate_forbidden": True,
        "budget_definition": (
            "required = prompt_tokens + real_M2_geometry_expansion + full_gt_dsl_tokens_including_eos; "
            "geometry_expansion = (surface_tokens-1) + (8-1) from real splice"
        ),
        "encode_truncated_count_old": sum(r["truncated_by_encode"] for r in budget["per_cad"]),
        "old_trunc_but_full_target_fits": [
            r["cad_id"]
            for r in budget["per_cad"]
            if r.get("truncated_by_encode") and r.get("would_fit_full_target")
        ],
        "not_trunc_but_full_target_exceeds": [
            r["cad_id"]
            for r in budget["per_cad"]
            if (not r.get("truncated_by_encode")) and r.get("would_fit_full_target") is False
        ],
        "count": len(kept),
        "records": kept,
    }
    (dest / "V3_NO_TRUNC_DEBUG.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (dest / "REMOVED.json").write_text(json.dumps({"removed_count": len(removed), "removed": removed}, indent=2) + "\n")
    summary = {k: manifest[k] for k in (
        "name", "original_train_count", "kept_count", "removed_count", "removed_ids",
        "full_target_preserved", "eos_supervised", "encode_truncated_count_old",
        "old_trunc_but_full_target_fits", "not_trunc_but_full_target_exceeds",
    )}
    (dest / "MANIFEST_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: (len(v) if k.endswith("ids") or k.endswith("fits") or k.endswith("exceeds") else v) if k != "removed_ids" else v for k, v in summary.items()}, indent=2)[:4000])
    print("kept", len(kept), "removed", len(removed))


if __name__ == "__main__":
    main()
