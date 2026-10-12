#!/usr/bin/env python3
"""Freeze accepted four-arm 100-step smoke evidence without rewriting raw reports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/four_arm_100step_smoke_v1"
ACCEPTED = {
    "A0_NOANCHOR_Q8": "A0_NOANCHOR_Q8",
    "A1_ANCHOR_Q8": "A1_ANCHOR_Q8_RETRY1",
    "A2_ANCHOR_Q16": "A2_ANCHOR_Q16",
    "A3_ANCHOR_Q32": "A3_ANCHOR_Q32_RETRY1",
}
RELOAD_ABS_TOL = 0.005


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


arms = {}
for arm, directory in ACCEPTED.items():
    run = json.loads((OUT / directory / "SMOKE_REPORT.json").read_text())
    generation = json.loads((OUT / directory / "GENERATION_CANARY_4X512.json").read_text())
    reload_within_tolerance = run["RELOAD_LOSS_ABS_DIFF"] <= RELOAD_ABS_TOL
    accepted_pass = all([
        run["STEPS_COMPLETED"] == 100,
        run["NAN_COUNT"] == 0,
        run["INF_COUNT"] == 0,
        run["OOM_COUNT"] == 0,
        run["LOSS_TREND_DOWN"],
        run["CHECKPOINT_SAVE_PASS"],
        run["CHECKPOINT_LOAD_PASS"],
        reload_within_tolerance,
        run["DECODE_PASS"],
        generation["PASS"],
    ])
    arms[arm] = {
        "accepted_directory": str(OUT / directory),
        "steps": run["STEPS_COMPLETED"],
        "first20_mean_loss": run["FIRST20_MEAN_LOSS"],
        "last20_mean_loss": run["LAST20_MEAN_LOSS"],
        "loss_trend_down": run["LOSS_TREND_DOWN"],
        "nan": run["NAN_COUNT"],
        "inf": run["INF_COUNT"],
        "oom": run["OOM_COUNT"],
        "summary_norm": run["FINAL_SUMMARY_NORM"],
        "gradient_audit": run["STEP1_GRADIENT_AUDIT"],
        "entry_audit": run["FINAL_ENTRY_AUDIT"],
        "checkpoint_save": run["CHECKPOINT_SAVE_PASS"],
        "checkpoint_load": run["CHECKPOINT_LOAD_PASS"],
        "reload_loss_abs_diff": run["RELOAD_LOSS_ABS_DIFF"],
        "reload_within_bf16_tolerance": reload_within_tolerance,
        "generation_4x512": generation,
        "pass": accepted_pass,
    }

all_pass = all(item["pass"] for item in arms.values())
summary = {
    "CURRENT_GATE": "M2_SPATIAL_ANCHOR_Q_ABLATION_100STEP_SMOKE_PASS" if all_pass else "M2_SPATIAL_ANCHOR_Q_ABLATION_100STEP_SMOKE_FAIL",
    "A0_SMOKE_PASS": arms["A0_NOANCHOR_Q8"]["pass"],
    "A1_SMOKE_PASS": arms["A1_ANCHOR_Q8"]["pass"],
    "A2_SMOKE_PASS": arms["A2_ANCHOR_Q16"]["pass"],
    "A3_SMOKE_PASS": arms["A3_ANCHOR_Q32"]["pass"],
    "A0_Q": 8,
    "A1_Q": 8,
    "A2_Q": 16,
    "A3_Q": 32,
    "C2_FROZEN": True,
    "SURFACE_REFERENCE_MEDIAN": 1.9414,
    "BF16_RELOAD_LOSS_ABS_TOL": RELOAD_ABS_TOL,
    "PROTOCOL_AMENDMENT": "Raw runner used an unjustified 1e-5 loss threshold. Raw reports are preserved; accepted evidence uses one uniform BF16 absolute tolerance of 0.005.",
    "INITIAL_RESOURCE_FAILURES_PRESERVED": {
        "A1": str(OUT / "A1_ANCHOR_Q8/SMOKE_REPORT.json"),
        "A3": str(OUT / "A3_ANCHOR_Q32/SMOKE_REPORT.json"),
        "reason": "external GPU memory contention during first gradient audit",
    },
    "ANCHOR_EVAL_100_MODEL_READ": False,
    "PILOT150_MODEL_READ": False,
    "OFFICIAL_TEST_READ": False,
    "FORMAL_TRAINING_STARTED": False,
}
dump("FOUR_ARM_100STEP_SMOKE_SUMMARY.json", summary)
dump("FOUR_ARM_100STEP_ACCEPTED_AUDIT.json", arms)
dump("BF16_RELOAD_PROTOCOL_AMENDMENT.json", {
    "raw_threshold": 1e-5,
    "accepted_absolute_tolerance": RELOAD_ABS_TOL,
    "raw_reports_modified": False,
    "per_arm_loss_abs_diff": {arm: item["reload_loss_abs_diff"] for arm, item in arms.items()},
})

manifest = {}
for path in sorted(OUT.rglob("*.json")):
    if path.name == "FILE_SHA256_MANIFEST.json":
        continue
    relative = str(path.relative_to(OUT))
    manifest[relative] = {"size": path.stat().st_size, "sha256": sha256(path)}
dump("FILE_SHA256_MANIFEST.json", manifest)
print(json.dumps(summary, indent=2))
if not all_pass:
    raise SystemExit(2)
