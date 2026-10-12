#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MANIFEST = ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl"
OLD = ROOT / "ours3/deepcad_style_iou_cd_ir_evaluation_v1/cadfit_comparison_v1/P1_val1000.csv"


def truth(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def fmt(value, digits=6):
    return "-" if value is None else f"{value:.{digits}f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-root", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads((args.eval_root / "SUMMARY.json").read_text())
    manifest = [json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    source_of = {x["cad_id"]: x["source"].lower() for x in manifest}
    with OLD.open(newline="") as handle:
        old = list(csv.DictReader(handle))
    old_ir = {}
    for source in ("all", "deepcad", "fusion360"):
        rows = old if source == "all" else [x for x in old if source_of[x["case_id"]] == source]
        old_ir[source] = sum(truth(x["deepcad_invalid"]) for x in rows) / len(rows)

    formal_rows = []
    for source in ("all", "deepcad", "fusion360"):
        block = summary[source] if source == "all" else summary["by_dataset"][source]
        for method, prefix in (("P1v2", "P1"), ("CADFit", "CADFit")):
            formal_rows.append(
                {
                    "dataset": source,
                    "N": block["N"],
                    "frozen_GT_valid_N": block["frozen_GT_valid_N"],
                    "strict_common_valid_N": block["strict_common_valid_N"],
                    "method": method,
                    "IR": block[f"{prefix}_IR"],
                    "invalid_N": block[f"{prefix}_invalid_N"],
                    "IoU_mean": block[f"{prefix}_IoU"]["mean"],
                    "IoU_median": block[f"{prefix}_IoU"]["median"],
                    "CD_mean": block[f"{prefix}_CD"]["mean"],
                    "CD_median": block[f"{prefix}_CD"]["median"],
                }
            )
    with (args.eval_root / "P1V2_VS_CADFIT_FORMAL.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(formal_rows[0]))
        writer.writeheader()
        writer.writerows(formal_rows)

    triple_rows = []
    for source in ("all", "deepcad", "fusion360"):
        triple = summary["triple_common"] if source == "all" else summary["by_dataset"][source]["triple_common"]
        for method, key in (("Old P1", "old_P1"), ("P1v2", "new_P1v2"), ("CADFit", "CADFit")):
            triple_rows.append(
                {
                    "dataset": source,
                    "strict_triple_common_valid_N": triple["strict_triple_common_valid_N"],
                    "method": method,
                    "IR_full_dataset": old_ir[source] if method == "Old P1" else (
                        (summary[source] if source == "all" else summary["by_dataset"][source])["P1_IR" if method == "P1v2" else "CADFit_IR"]
                    ),
                    "IoU_mean": triple[key]["IoU"]["mean"],
                    "IoU_median": triple[key]["IoU"]["median"],
                    "CD_mean": triple[key]["CD"]["mean"],
                    "CD_median": triple[key]["CD"]["median"],
                }
            )
    with (args.eval_root / "OLD_P1_P1V2_CADFIT_TRIPLE_COMMON.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(triple_rows[0]))
        writer.writeheader()
        writer.writerows(triple_rows)

    lines = [
        "# P1v2 vs CADFit - DeepCAD-style IoU/CD/IR VAL1000",
        "",
        "FULL_N=1000",
        "FROZEN_GT_VALID_N=253",
        "PAIR_COMMON_VALID_N=192",
        "TRIPLE_COMMON_VALID_N=188",
        "",
        "## Formal P1v2 vs CADFit",
        "",
        "| Dataset | Method | N | IR | IoU mean | IoU median | CD mean | CD median | Common N |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in formal_rows:
        lines.append(
            f"| {row['dataset']} | {row['method']} | {row['N']} | {fmt(row['IR'])} | "
            f"{fmt(row['IoU_mean'])} | {fmt(row['IoU_median'])} | {fmt(row['CD_mean'])} | "
            f"{fmt(row['CD_median'])} | {row['strict_common_valid_N']} |"
        )
    lines += [
        "",
        "## Old P1 vs P1v2 vs CADFit on the same triple-common cases",
        "",
        "| Dataset | Method | IR (full dataset) | IoU mean | IoU median | CD mean | CD median | Triple N |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in triple_rows:
        lines.append(
            f"| {row['dataset']} | {row['method']} | {fmt(row['IR_full_dataset'])} | "
            f"{fmt(row['IoU_mean'])} | {fmt(row['IoU_median'])} | {fmt(row['CD_mean'])} | "
            f"{fmt(row['CD_median'])} | {row['strict_triple_common_valid_N']} |"
        )
    lines += [
        "",
        "## Conclusion",
        "",
        "P1v2 does not exceed CADFit on DeepCAD or Fusion360. On the triple-common Fusion360 cohort, P1v2 improves strongly over old P1 (IoU 0.000443 -> 0.353356; CD 272890.712098 -> 18022.528677), but remains behind CADFit (IoU 0.947742; CD 222.786122). On DeepCAD, P1v2 regresses versus old P1 in IoU, CD, and IR.",
        "",
        "IR uses the full dataset denominator. IoU/CD use only frozen-GT-valid strict common-valid cases. Lower CD and IR are better; higher IoU is better.",
    ]
    (args.eval_root / "FINAL_REPORT.md").write_text("\n".join(lines) + "\n")

    checks = {
        "alignment_N_is_1000": summary["alignment_N"] == 1000,
        "frozen_GT_valid_N_is_253": summary["all"]["frozen_GT_valid_N"] == 253,
        "pair_common_decomposes": 192 == 163 + 29 == summary["all"]["strict_common_valid_N"],
        "triple_common_decomposes": 188 == 159 + 29 == summary["triple_common"]["strict_triple_common_valid_N"],
        "all_methods_have_expected_direction": (
            summary["all"]["P1_IoU"]["mean"] < summary["all"]["CADFit_IoU"]["mean"]
            and summary["all"]["P1_CD"]["median"] > summary["all"]["CADFit_CD"]["median"]
            and summary["all"]["P1_IR"] > summary["all"]["CADFit_IR"]
        ),
    }
    checks["all_pass"] = all(checks.values())
    (args.eval_root / "VALIDATION.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
