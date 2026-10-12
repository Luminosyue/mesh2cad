#!/usr/bin/env python3
"""STEP 4: GT DSL parse / OCC exec / STEP write / STEP reload for V3-1k train 800.

Read-only. Does not modify GT. Writes ours3/v3_sft_chain_audit_v2/GT_EXEC_AUDIT.json
"""
from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_geometry_prefix_v3"))
from cad_execution_failure_audit import staged_execute

DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
AUDIT_ROWS = ROOT / "cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/reports/AUDITED_ROWS_WITH_IDENTITIES.json"
OUT = ROOT / "ours3/v3_sft_chain_audit_v2"


def by_source(cad_id: str) -> str:
    if cad_id.startswith("deepcad__"):
        return "deepcad"
    if cad_id.startswith("fusion360__"):
        return "fusion360"
    return "unknown"


def rates(rows, keys):
    n = len(rows)
    return {k: {"n": sum(bool(r[k]) for r in rows), "d": n, "rate": (sum(bool(r[k]) for r in rows) / n if n else None)} for k in keys}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads((DATA / "v3_1k_train.json").read_text())["records"]
    if len(records) != 800:
        raise RuntimeError(f"expected 800, got {len(records)}")
    geom = {}
    if AUDIT_ROWS.is_file():
        for r in json.loads(AUDIT_ROWS.read_text()):
            geom[r["cad_id"]] = r

    keys = (
        "dsl_parse_success",
        "dsl_execute_success",
        "occ_shape_non_null",
        "brep_valid",
        "step_write_success",
        "step_reload_success",
    )
    per = []
    work = OUT / "gt_exec_tmp"
    work.mkdir(exist_ok=True)
    for i, rec in enumerate(records, 1):
        dsl_path = Path(rec["target_dsl"])
        text = dsl_path.read_text()
        with tempfile.TemporaryDirectory(dir=work) as d:
            audit = staged_execute(text, Path(d))
        g = geom.get(rec["cad_id"])
        item = {
            "cad_id": rec["cad_id"],
            "source": rec.get("source_dataset") or by_source(rec["cad_id"]),
            "dsl_path": str(dsl_path),
            "operation_count": rec.get("operation_count"),
            "operation_names": rec.get("operation_names"),
            **audit,
            "gt_geometry_pass": None if g is None else bool(g.get("label_gate")),
            "prior_execution_ok": None if g is None else bool(g.get("execution_ok")),
            "prior_step_reload": None if g is None else bool(g.get("step_reload")),
            "prior_chamfer_rel": None if g is None else g.get("chamfer_rel"),
        }
        if not audit["dsl_parse_success"]:
            item["failure_stage"] = "PARSE"
        elif not audit["dsl_execute_success"]:
            item["failure_stage"] = "EXEC"
        elif not audit["step_write_success"]:
            item["failure_stage"] = "STEP_WRITE"
        elif not audit["step_reload_success"]:
            item["failure_stage"] = "STEP_RELOAD"
        else:
            item["failure_stage"] = "SUCCESS"
        per.append(item)
        if i % 50 == 0:
            print(f"gt {i}/800 parse={sum(x['dsl_parse_success'] for x in per)} exec={sum(x['dsl_execute_success'] for x in per)} reload={sum(x['step_reload_success'] for x in per)}", flush=True)

    def split(name):
        return [r for r in per if r["source"] == name]

    groups = {
        "overall": per,
        "deepcad": split("deepcad"),
        "fusion360": split("fusion360"),
    }
    summary_rates = {}
    for gname, grows in groups.items():
        summary_rates[gname] = {
            "n": len(grows),
            "GT_PARSE_PASS": sum(r["dsl_parse_success"] for r in grows),
            "GT_EXEC_PASS": sum(r["dsl_execute_success"] for r in grows),
            "GT_STEP_WRITE_PASS": sum(r["step_write_success"] for r in grows),
            "GT_STEP_RELOAD_PASS": sum(r["step_reload_success"] for r in grows),
            "GT_BREP_VALID": sum(r["brep_valid"] for r in grows),
            "GT_GEOMETRY_PASS": sum(r["gt_geometry_pass"] is True for r in grows),
            "GT_GEOMETRY_KNOWN": sum(r["gt_geometry_pass"] is not None for r in grows),
            "failure_stage": dict(sorted(Counter(r["failure_stage"] for r in grows).items())),
        }

    failures = [r for r in per if r["failure_stage"] != "SUCCESS"]
    out = {
        "TRAIN_COUNT": 800,
        "executor": "scripts/spatiallm_geometry_prefix_v3/cad_execution_failure_audit.py::staged_execute",
        "gt_not_modified": True,
        "by_group": summary_rates,
        "failure_count": len(failures),
        "failures": [
            {
                "cad_id": r["cad_id"],
                "source": r["source"],
                "failure_stage": r["failure_stage"],
                "failure_reason": r.get("failure_reason"),
                "exception": r.get("error"),
                "dsl_path": r["dsl_path"],
            }
            for r in failures
        ],
        "per_cad": per,
    }
    (OUT / "GT_EXEC_AUDIT.json").write_text(json.dumps(out, indent=2) + "\n")
    (OUT / "GT_EXEC_per_cad.jsonl").write_text("".join(json.dumps(r) + "\n" for r in per))

    md = ["# GT_EXEC_AUDIT", "", "GT 未修改。executor = `cad_execution_failure_audit.staged_execute`.", ""]
    md.append("| group | n | PARSE | EXEC | STEP_WRITE | STEP_RELOAD | GEOMETRY |")
    md.append("|---|---:|---:|---:|---:|---:|---:|")
    for gname, s in summary_rates.items():
        md.append(
            f"| {gname} | {s['n']} | {s['GT_PARSE_PASS']} | {s['GT_EXEC_PASS']} | {s['GT_STEP_WRITE_PASS']} | {s['GT_STEP_RELOAD_PASS']} | {s['GT_GEOMETRY_PASS']}/{s['GT_GEOMETRY_KNOWN']} |"
        )
    md += ["", f"failures = {len(failures)}", ""]
    if failures:
        md.append("| cad_id | source | stage | exception |")
        md.append("|---|---|---|---|")
        for r in failures:
            md.append(f"| {r['cad_id']} | {r['source']} | {r['failure_stage']} | `{r.get('exception')}` |")
    (OUT / "GT_EXEC_AUDIT.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary_rates, indent=2))
    print("wrote", OUT / "GT_EXEC_AUDIT.json")


if __name__ == "__main__":
    main()
