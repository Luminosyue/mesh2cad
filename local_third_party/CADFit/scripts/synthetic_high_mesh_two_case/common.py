from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
from pathlib import Path


PROTOCOL_NAME = "Synthetic-High-Mesh-Two-Case-Demo-v1"
CASES = [
    ("case_a_flange", "stepped_revolved_flange"),
    ("case_b_bracket", "multi_feature_bracket"),
]


def ensure_dirs(root: Path | None = None) -> None:
    root = root or Path.cwd()
    for rel in [
        "datasets/synthetic_high_mesh_two_case_v1/case_a_flange",
        "datasets/synthetic_high_mesh_two_case_v1/case_b_bracket",
        "outputs/synthetic_high_mesh_two_case_v1/case_a_flange",
        "outputs/synthetic_high_mesh_two_case_v1/case_b_bracket",
        "artifacts/synthetic_high_mesh_two_case_v1/case_a_flange",
        "artifacts/synthetic_high_mesh_two_case_v1/case_b_bracket",
        "scripts/synthetic_high_mesh_two_case",
        "tests/synthetic_high_mesh_two_case",
        "configs",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: str | Path) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def write_csv(path: str | Path, rows: list[dict], fields: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def link_or_copy(src: str | Path, dst: str | Path) -> None:
    src_p = Path(src)
    dst_p = Path(dst)
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    if dst_p.exists() or dst_p.is_symlink():
        dst_p.unlink()
    try:
        os.symlink(src_p.resolve(), dst_p)
    except Exception:
        shutil.copy2(src_p, dst_p)


def count_ops(path: str | Path) -> dict:
    text = Path(path).read_text(encoding="utf-8", errors="ignore") if Path(path).exists() else ""
    return {
        "program_line_count": len(text.splitlines()),
        "sketch_count": len(re.findall(r"\bSketch\b|cq\.Sketch|sketch_", text)),
        "extrude_count": len(re.findall(r"\.extrude\s*\(", text, re.I)),
        "revolve_count": len(re.findall(r"\.revolve\s*\(", text, re.I)),
        "union_count": len(re.findall(r"\.union\s*\(|\.add\s*\(", text, re.I)),
        "cut_count": len(re.findall(r"\.cut\s*\(|cutBlind|hole\s*\(", text, re.I)),
        "fillet_count": len(re.findall(r"\.fillet\s*\(", text, re.I)),
        "chamfer_count": len(re.findall(r"\.chamfer\s*\(", text, re.I)),
        "operation_counts_are_static_approximation": True,
    }


def cadfit_success_dir(case_out: Path, stl_id: str = "input_high_mesh") -> Path:
    return case_out / stl_id


def has_success_outputs(case_out: Path, stl_id: str = "input_high_mesh") -> bool:
    p = cadfit_success_dir(case_out, stl_id)
    return all((p / name).exists() and (p / name).stat().st_size > 0 for name in [
        "best_greedy_parallel_iterative.py",
        "best_greedy_parallel_iterative.stl",
        "final_iou.json",
    ])
