#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from common import CASES, count_ops, link_or_copy, read_json, write_csv


def copy_if_exists(src: Path, dst: Path, link_mesh: bool = False) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if link_mesh and src.suffix.lower() in {".stl", ".step"}:
        link_or_copy(src, dst)
    else:
        shutil.copy2(src, dst)


def collect_case(case_name: str) -> dict:
    data = Path("datasets/synthetic_high_mesh_two_case_v1") / case_name
    out = Path("outputs/synthetic_high_mesh_two_case_v1") / case_name
    obj = out / "input_high_mesh"
    art = Path("artifacts/synthetic_high_mesh_two_case_v1") / case_name
    art.mkdir(parents=True, exist_ok=True)
    for name in ["ground_truth.py", "ground_truth.step", "input_high_mesh.stl", "mesh_audit.json", "input_render.png"]:
        copy_if_exists(data / name, art / name, link_mesh=True)
    mappings = [
        (obj / "best_greedy_parallel_iterative.py", art / "generated_cad.py"),
        (obj / "best_greedy_parallel_iterative.stl", art / "reconstructed_cad.stl"),
        (obj / "final_iou.json", art / "final_iou.json"),
        (out / "run_status.json", art / "run_status.json"),
        (out / "stdout.log", art / "stdout.log"),
        (out / "stderr.log", art / "stderr.log"),
    ]
    for src, dst in mappings:
        copy_if_exists(src, dst, link_mesh=True)
    audit = read_json(art / "mesh_audit.json")
    status = read_json(art / "run_status.json")
    iou = read_json(art / "final_iou.json")
    ops = count_ops(art / "generated_cad.py")
    step_audit = read_json(Path("artifacts/synthetic_high_mesh_two_case_v1/reconstructed_step_audit.json")).get(case_name, {})
    row = {
        "case_name": case_name,
        "ground_truth_step_faces": audit.get("ground_truth_step_faces", ""),
        "input_vertices": audit.get("vertex_count", ""),
        "input_triangles": audit.get("triangle_count", ""),
        "input_watertight": audit.get("is_watertight", ""),
        "cadfit_status": status.get("status", "not_run"),
        "prior_mode": "no_prior",
        "iou": iou.get("final_iou", ""),
        "runtime_seconds": status.get("runtime_seconds", ""),
        "generated_program_lines": ops["program_line_count"],
        "extrude_count": ops["extrude_count"],
        "revolve_count": ops["revolve_count"],
        "union_count": ops["union_count"],
        "cut_count": ops["cut_count"],
        "fillet_count": ops["fillet_count"],
        "chamfer_count": ops["chamfer_count"],
        "reconstructed_step_success": step_audit.get("step_export_success", False),
        "error": status.get("error", ""),
    }
    case_report = [
        f"# {case_name}",
        "",
        f"- Input triangles: {row['input_triangles']}",
        f"- Input vertices: {row['input_vertices']}",
        f"- Ground-truth STEP faces: {row['ground_truth_step_faces']}",
        f"- Watertight: {row['input_watertight']}",
        f"- CADFit status: {row['cadfit_status']}",
        f"- Prior mode: no_prior",
        f"- IoU: {row['iou']}",
        f"- Runtime seconds: {row['runtime_seconds']}",
        f"- Generated code: `{art / 'generated_cad.py'}`",
        f"- Reconstructed STEP reopen/export success: {row['reconstructed_step_success']}",
        "",
        "## Operation Counts",
        "",
        "These are static approximate counts from the generated program, not guaranteed modeling history.",
        "",
        f"- extrude={row['extrude_count']}, revolve={row['revolve_count']}, union={row['union_count']}, cut={row['cut_count']}, fillet={row['fillet_count']}, chamfer={row['chamfer_count']}",
        "",
        "## Visuals",
        "",
        "![input](input_render.png)",
        "![reconstructed](reconstructed_render.png)",
        "![comparison](comparison.png)",
        "",
        "## Qualitative Notes",
        "",
        "Recovered and simplified structures should be judged from the generated CadQuery program and comparison image. CADFit received only the isolated STL input directory for this run.",
    ]
    (art / "case_report.md").write_text("\n".join(case_report), encoding="utf-8")
    return row


def main() -> int:
    argparse.ArgumentParser().parse_args()
    root = Path("artifacts/synthetic_high_mesh_two_case_v1")
    rows = [collect_case(case) for case, _ in CASES]
    fields = [
        "case_name", "ground_truth_step_faces", "input_vertices", "input_triangles",
        "input_watertight", "cadfit_status", "prior_mode", "iou", "runtime_seconds",
        "generated_program_lines", "extrude_count", "revolve_count", "union_count",
        "cut_count", "fillet_count", "chamfer_count", "reconstructed_step_success", "error",
    ]
    write_csv(root / "demo_summary.csv", rows, fields)
    report = [
        "# Synthetic-High-Mesh-Two-Case-Demo-v1",
        "",
        "两个输入Mesh均由自行构造的参数化机械CAD经过精细三角化得到。CADFit运行时只接收STL Mesh，没有读取ground-truth CadQuery程序或STEP。该实验是功能Demo，不是ABC Hard或论文Table 1复现。",
        "",
        "## Protocol",
        "",
        "- ABC_DOWNLOAD_REQUIRED=false",
        "- STRICT_TABLE1_REPRODUCTION=false",
        "- SKETCH_PRIOR_ENABLED=false",
        "- PRIOR_MODE=no_prior",
        "- max_iterations=1",
        "- fillet_chamfer=false",
        "",
        "## Results",
        "",
        "| case | STEP faces | input triangles | status | IoU | runtime s | STEP export | generated code |",
        "|---|---:|---:|---|---:|---:|---|---|",
    ]
    for row in rows:
        case = row["case_name"]
        report.append(
            f"| {case} | {row['ground_truth_step_faces']} | {row['input_triangles']} | {row['cadfit_status']} | {row['iou']} | {row['runtime_seconds']} | {row['reconstructed_step_success']} | `{case}/generated_cad.py` |"
        )
    for row in rows:
        case = row["case_name"]
        report += [
            "",
            f"## {case}",
            "",
            f"- Original high mesh triangles: {row['input_triangles']}",
            f"- Original STEP faces: {row['ground_truth_step_faces']}",
            f"- IoU: {row['iou']}",
            f"- Runtime seconds: {row['runtime_seconds']}",
            f"- Generated operations: extrude={row['extrude_count']}, revolve={row['revolve_count']}, union={row['union_count']}, cut={row['cut_count']}, fillet={row['fillet_count']}, chamfer={row['chamfer_count']}",
            f"- STEP can reopen: {row['reconstructed_step_success']}",
            "",
            f"![{case} input]({case}/input_render.png)",
            f"![{case} reconstructed]({case}/reconstructed_render.png)",
            f"![{case} comparison]({case}/comparison.png)",
            "",
            "no_prior mode may increase candidate search noise and reduce reconstruction quality versus a working sketch prior. The result is reported only as a functional demonstration.",
        ]
    (root / "demo_report.md").write_text("\n".join(report), encoding="utf-8")
    print("DEMO_SUMMARY=" + str(root / "demo_summary.csv"))
    print("DEMO_REPORT=" + str(root / "demo_report.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
