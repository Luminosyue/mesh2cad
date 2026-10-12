#!/usr/bin/env python3
"""Freeze the four real single-batch audits into reviewable aggregate evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/single_batch_contract_v1"
FILES = {
    "A0_NOANCHOR_Q8": "A0_SINGLE_BATCH_AUDIT.json",
    "A1_ANCHOR_Q8": "A1_SINGLE_BATCH_AUDIT.json",
    "A2_ANCHOR_Q16": "A2_SINGLE_BATCH_AUDIT.json",
    "A3_ANCHOR_Q32": "A3_SINGLE_BATCH_AUDIT.json",
}


def dump(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


audits = {arm: json.loads((OUT / name).read_text()) for arm, name in FILES.items()}
all_pass = all(a["SINGLE_BATCH_PASS"] for a in audits.values())
summary = {
    "CURRENT_GATE": "M2_SPATIAL_ANCHOR_Q_ABLATION_SINGLE_BATCH_PASS" if all_pass else "M2_SPATIAL_ANCHOR_Q_ABLATION_SINGLE_BATCH_FAIL",
    "ARM_PASS": {arm: audit["SINGLE_BATCH_PASS"] for arm, audit in audits.items()},
    "LOSSES": {arm: audit["LOSS"] for arm, audit in audits.items()},
    "FORMAL_TRAINING_STARTED": False,
    "ANCHOR_EVAL_100_MODEL_READ": False,
    "PILOT150_MODEL_READ": False,
    "OFFICIAL_TEST_READ": False,
}
dump("SINGLE_BATCH_CONTRACT_SUMMARY.json", summary)
dump("GRADIENT_OWNERSHIP_AUDIT.json", {arm: a["GRADIENT"] for arm, a in audits.items()})
dump("TENSOR_SHAPE_AUDIT.json", {arm: {
    "raw_curve": a["RAW_CURVE_SHAPE"],
    "c2": a["C2_TOKEN_SHAPE"],
    "anchor": a["ANCHOR_SHAPE"],
    "summary": a["SUMMARY_TOKEN_SHAPE"],
    "llm_input": a["LLM_INPUT_SHAPE"],
} for arm, a in audits.items()})
dump("MASK_CONTRACT_AUDIT.json", {arm: {
    "pass": a["MASK_CONTRACT_PASS"],
    "summary_mask_shape": a["SUMMARY_MASK_SHAPE"],
    "llm_attention_mask_shape": a["LLM_ATTENTION_MASK_SHAPE"],
} for arm, a in audits.items()})
dump("NORM_AUDIT.json", {
    "SURFACE_REFERENCE_MEDIAN": 1.9414,
    "STATUS": "SUMMARY_NORM_DISTRIBUTION_DEFERRED_TO_100STEP_SMOKE",
    "NOTE": "The single-batch gate audited finite tensors and gradient ownership; the 100-step runner records per-step summary norms.",
})

manifest = {}
for path in sorted(OUT.glob("*.json")):
    if path.name == "FILE_SHA256_MANIFEST.json":
        continue
    manifest[path.name] = {"size": path.stat().st_size, "sha256": sha256(path)}
dump("FILE_SHA256_MANIFEST.json", manifest)
print(json.dumps(summary, indent=2))
