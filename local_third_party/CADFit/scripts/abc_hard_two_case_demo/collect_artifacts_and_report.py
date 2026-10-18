#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from pathlib import Path

from common import link_or_copy, read_csv_dicts, write_csv_dicts


def op_stats(script: Path) -> dict:
    text = script.read_text(encoding="utf-8", errors="ignore") if script.exists() else ""
    return {
        "code_lines": len(text.splitlines()),
        "sketch_count": len(re.findall(r"\bSketch\b|cq\.Sketch|sketch_", text)),
        "extrude_count": len(re.findall(r"\.extrude\s*\(", text, re.I)),
        "revolve_count": len(re.findall(r"\.revolve\s*\(", text, re.I)),
        "union_count": len(re.findall(r"\.union\s*\(|\.add\s*\(", text, re.I)),
        "cut_count": len(re.findall(r"\.cut\s*\(", text, re.I)),
        "fillet_count": len(re.findall(r"\.fillet\s*\(", text, re.I)),
        "chamfer_count": len(re.findall(r"\.chamfer\s*\(", text, re.I)),
    }


def collect_case(row: dict, outputs_root: Path, artifacts_root: Path) -> dict:
    case = row["case_name"]
    src_dir = outputs_root / case / row["abc_id"]
    case_dir = artifacts_root / case
    case_dir.mkdir(parents=True, exist_ok=True)
    mappings = [
        (row["source_stl"], case_dir / "input_high_mesh.stl"),
        (src_dir / "best_greedy_parallel_iterative.py", case_dir / "generated_cad.py"),
        (src_dir / "best_greedy_parallel_iterative.stl", case_dir / "reconstructed_cad.stl"),
        (src_dir / "final_iou.json", case_dir / "final_iou.json"),
        (outputs_root / case / "run_status.json", case_dir / "run_status.json"),
        (outputs_root / case / "stdout.log", case_dir / "stdout.log"),
        (outputs_root / case / "stderr.log", case_dir / "stderr.log"),
    ]
    for src, dst in mappings:
        if Path(src).exists():
            if str(src).endswith(".log") or str(src).endswith(".json") or str(src).endswith(".py"):
                shutil.copy2(src, dst)
            else:
                link_or_copy(src, dst)
    status = json.loads((case_dir / "run_status.json").read_text()) if (case_dir / "run_status.json").exists() else {}
    iou_data = json.loads((case_dir / "final_iou.json").read_text()) if (case_dir / "final_iou.json").exists() else {}
    return {"status": status, "iou": iou_data, "stats": op_stats(case_dir / "generated_cad.py")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="datasets/abc_hard_two_case_demo/manifests/selected_two_cases.csv")
    ap.add_argument("--outputs-root", default="outputs/abc_hard_two_case_demo")
    ap.add_argument("--artifacts-root", default="artifacts/abc_hard_two_case_demo")
    args = ap.parse_args()
    rows = read_csv_dicts(args.manifest)
    artifacts_root = Path(args.artifacts_root)
    prior = {}
    prior_file = artifacts_root / "sketch_prior_audit.json"
    if prior_file.exists():
        prior = json.loads(prior_file.read_text())
    export = {}
    exp_file = artifacts_root / "step_export_audit.json"
    if exp_file.exists():
        export = json.loads(exp_file.read_text())
    summary_rows = []
    report = [
        "# ABC-Hard-Two-Case-Demo-v1",
        "",
        "## Task Purpose",
        "Run CADFit on two real ABC Dataset Hard cases selected by the public STEP B-Rep face-count rule, then package executable CadQuery code, reconstructed STL/STEP outputs, metrics, logs, and input/output comparison renders.",
        "",
        "This experiment is a two-case demonstration. It is not a strict reproduction of paper Table 1.",
        "",
        "## CADFit Configuration",
        "- max_iterations: 1",
        "- outer_workers: 1",
        "- fillet_chamfer: false",
        "- mesh repair in wrapper: disabled",
        f"- sketch_prior_mode: {prior.get('prior_mode', 'unknown')}",
        "",
        "## Case Results",
    ]
    for row in rows:
        case = row["case_name"]
        data = collect_case(row, Path(args.outputs_root), artifacts_root)
        status = data["status"]
        iou = data["iou"].get("final_iou", "")
        runtime = status.get("runtime_seconds", "")
        step_export = export.get(case, {})
        case_dir = artifacts_root / case
        summary_rows.append({
            "case_name": case,
            "abc_id": row["abc_id"],
            "step_face_count": row["step_face_count"],
            "input_triangle_count": row["triangle_count"],
            "input_vertex_count": row["vertex_count"],
            "is_watertight": row["is_watertight"],
            "prior_mode": prior.get("prior_mode", "unknown"),
            "iou": iou,
            "runtime_seconds": runtime,
            "generated_code_path": str(case_dir / "generated_cad.py"),
            "generated_stl_path": str(case_dir / "reconstructed_cad.stl"),
            "generated_step_path": str(case_dir / "reconstructed_cad.step"),
            "step_export_success": step_export.get("step_export_success", False),
            "status": status.get("status", ""),
            "error": status.get("error", ""),
        })
        st = data["stats"]
        report += [
            "",
            f"### {case}",
            f"- ABC ID: {row['abc_id']}",
            f"- STEP B-Rep face count: {row['step_face_count']}",
            f"- Input STL triangles: {row['triangle_count']}",
            f"- Input STL vertices: {row['vertex_count']}",
            f"- Watertight: {row['is_watertight']}",
            f"- IoU: {iou}",
            f"- Runtime seconds: {runtime}",
            f"- STEP reopen/export success: {step_export.get('step_export_success', False)}",
            f"- Static code stats: lines={st['code_lines']}, sketches~={st['sketch_count']}, extrude={st['extrude_count']}, revolve={st['revolve_count']}, union={st['union_count']}, cut={st['cut_count']}, fillet={st['fillet_count']}, chamfer={st['chamfer_count']}",
            "",
            "Static operation counts are approximate string counts over generated_cad.py.",
            "",
            f"![{case} input]({case}/input_render.png)",
            f"![{case} reconstructed]({case}/reconstructed_render.png)",
            f"![{case} comparison]({case}/comparison.png)",
            "",
            "Recovered structures and omitted/simplified details should be judged from the comparison image and generated CadQuery program; no manual geometry edits were applied.",
        ]
    report += [
        "",
        "## Statement",
        "本实验为两个依据论文公开STEP face count规则筛选的真实ABC Hard案例演示，不是论文Table 1的严格同样本复现。",
    ]
    fields = [
        "case_name", "abc_id", "step_face_count", "input_triangle_count", "input_vertex_count",
        "is_watertight", "prior_mode", "iou", "runtime_seconds", "generated_code_path",
        "generated_stl_path", "generated_step_path", "step_export_success", "status", "error",
    ]
    write_csv_dicts(artifacts_root / "demo_summary.csv", summary_rows, fields)
    (artifacts_root / "demo_report.md").write_text("\n".join(report), encoding="utf-8")
    print("SUMMARY_PATH=" + str(artifacts_root / "demo_summary.csv"))
    print("REPORT_PATH=" + str(artifacts_root / "demo_report.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
