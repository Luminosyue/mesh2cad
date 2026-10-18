from __future__ import annotations

import csv
import hashlib
import os
import re
import shutil
from pathlib import Path


PROTOCOL_NAME = "ABC-Hard-Two-Case-Demo-v1"
HARD_MIN = 151
HARD_MAX = 1500


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_demo_dirs(root: Path | None = None) -> None:
    root = root or repo_root()
    for rel in [
        "data/abc_v00_demo/download_lists",
        "data/abc_v00_demo/archives",
        "data/abc_v00_demo/step",
        "data/abc_v00_demo/stl2",
        "datasets/abc_hard_two_case_demo/candidates",
        "datasets/abc_hard_two_case_demo/selected",
        "datasets/abc_hard_two_case_demo/manifests",
        "datasets/abc_hard_two_case_demo/audits",
        "outputs/abc_hard_two_case_demo/case_a",
        "outputs/abc_hard_two_case_demo/case_b",
        "outputs/abc_hard_two_case_demo/failed_attempts",
        "artifacts/abc_hard_two_case_demo/case_a",
        "artifacts/abc_hard_two_case_demo/case_b",
        "scripts/abc_hard_two_case_demo",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def parse_abc_id(path_or_name: str) -> str | None:
    name = Path(path_or_name).name
    m = re.match(r"^(\d{8})(?:[_\-.].*)?$", name)
    if m:
        return m.group(1)
    matches = re.findall(r"(?<!\d)(\d{8})(?!\d)", name)
    return matches[0] if matches else None


def chunk_from_path(path_or_name: str) -> str:
    s = str(path_or_name)
    m = re.search(r"abc_(\d{4})_", s)
    if m:
        return m.group(1)
    parts = Path(s).parts
    for p in parts:
        if re.fullmatch(r"\d{4}", p):
            return p
    return ""


def is_hard_face_count(face_count: int | str | None) -> bool:
    try:
        n = int(face_count)  # type: ignore[arg-type]
    except Exception:
        return False
    return HARD_MIN <= n <= HARD_MAX


def sha256_file(path: str | Path, block_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()


def read_csv_dicts(path: str | Path) -> list[dict[str, str]]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv_dicts(path: str | Path, rows: list[dict], fieldnames: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


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


def successful_outputs(case_dir: str | Path) -> bool:
    p = Path(case_dir)
    return all((p / name).exists() and (p / name).stat().st_size > 0 for name in [
        "best_greedy_parallel_iterative.py",
        "best_greedy_parallel_iterative.stl",
        "final_iou.json",
    ])
