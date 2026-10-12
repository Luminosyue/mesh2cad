#!/usr/bin/env python3
"""Resume rubiks / recordplayer / vase / winerack through CADFit -> STEP -> assembly."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_more_v2"
LOG = LADDER / "logs/continue_four.log"
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
MIN_FREE_MB = 20000
CADFIT_JOBS = 4
INNER = 4

SLUGS = [
    "rubiks_p3_xpart_cadfit_routea_v1",
    "recordplayer_p3_xpart_cadfit_routea_v1",
    "vase_p3_xpart_cadfit_routea_v1",
    "winerack_p3_xpart_cadfit_routea_v1",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def gpu_free_mb() -> list[tuple[int, int]]:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,memory.free", "--format=csv,noheader,nounits"],
        text=True,
    )
    rows = []
    for line in out.strip().splitlines():
        idx, free = [p.strip() for p in line.split(",")]
        rows.append((int(idx), int(float(free))))
    return sorted(rows, key=lambda r: -r[1])


def pick_gpu(min_free_mb: int = MIN_FREE_MB) -> int:
    while True:
        rows = gpu_free_mb()
        idx, free = rows[0]
        log(f"gpu free {rows}")
        if free >= min_free_mb:
            return idx
        log(f"waiting GPU >={min_free_mb} MiB; best gpu{idx}={free}")
        time.sleep(60)


def stl_ready(case: Path) -> bool:
    stl_dir = case / "cadfit_routea/input_stl"
    return bool(stl_dir.is_dir() and list(stl_dir.glob("PART_*.stl")))


def xpart_ok(case: Path) -> bool:
    manifest = case / "xpart/manifest.json"
    if not manifest.is_file():
        return False
    try:
        return int(json.loads(manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0) > 0
    except Exception:
        return False


def run_cmd(cmd: list[str], cwd: Path, log_path: Path) -> int:
    log(f"CMD {' '.join(cmd)}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=str(cwd), stdout=f, stderr=subprocess.STDOUT)
    log(f"RC {proc.returncode}")
    return proc.returncode


def run_xpart(case: Path, gpu: int, octree: int, batch: int) -> int:
    return run_cmd(
        [
            str(HY3D_PY),
            "-u",
            str(case / "scripts/run_xpart.py"),
            "--gpu",
            str(gpu),
            "--octree-resolution",
            str(octree),
            "--batch-size",
            str(batch),
        ],
        case,
        case / "logs/xpart_retry.log",
    )


def run_pipeline(case: Path, args: list[str], log_name: str) -> int:
    return run_cmd(
        [sys.executable, "-u", str(case / "scripts/run_pipeline.py"), *args],
        case,
        case / "logs" / log_name,
    )


def ensure_frontend(case: Path, label: str) -> bool:
    if stl_ready(case):
        log(f"{label} STL ready, skip X-Part")
        return True
    if not (case / "p3/part_metadata.json").is_file():
        log(f"{label} no frozen P3")
        return False
    if xpart_ok(case):
        log(f"{label} X-Part manifest ok")
    else:
        for octree, batch in ((256, 1), (128, 1)):
            gpu = pick_gpu()
            log(f"{label} X-Part octree={octree} batch={batch} gpu={gpu}")
            rc = run_xpart(case, gpu, octree, batch)
            if rc == 0 and xpart_ok(case):
                break
            # clear partial xpart for clean retry
            xp = case / "xpart"
            if xp.is_dir() and not xpart_ok(case):
                for p in xp.glob("PART_*"):
                    if p.is_dir():
                        import shutil
                        shutil.rmtree(p, ignore_errors=True)
                (xp / "manifest.json").unlink(missing_ok=True)
        if not xpart_ok(case):
            log(f"{label} X-Part failed after retries")
            return False
    rc = run_pipeline(case, ["--stage", "stl"], "stl.log")
    return rc == 0 and stl_ready(case)


def run_backend(case: Path, label: str) -> dict:
    row = {"label": label, "case": str(case)}
    if not stl_ready(case):
        row["status"] = "no_stl"
        return row
    # Dora does not feed CADFit; skip blocking dora
    log(f"{label} CADFit -> STEP -> assembly")
    rc = run_pipeline(
        case,
        ["--stage", "cadfit", "--skip-canary", "--jobs", str(CADFIT_JOBS), "--inner-workers", str(INNER)],
        "cadfit.log",
    )
    row["cadfit_rc"] = rc
    rc = run_pipeline(case, ["--stage", "step"], "step.log")
    row["step_rc"] = rc
    rc = run_pipeline(case, ["--stage", "assembly"], "assembly.log")
    row["assembly_rc"] = rc
    row["status"] = "ok" if row.get("step_rc") == 0 and row.get("assembly_rc") == 0 else "partial"
    return row


def main() -> int:
    summary = []
    for slug in SLUGS:
        case = ROOT / "ours3" / slug
        label = slug.split("_p3_")[0]
        log(f"=== {label} ===")
        if not ensure_frontend(case, label):
            summary.append({"label": label, "status": "frontend_fail"})
            continue
        summary.append(run_backend(case, label))
        log(f"{label} done status={summary[-1].get('status')}")
    out = LADDER / "logs/continue_four_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": summary}, indent=2) + "\n")
    log(f"all done {out}")
    return 0 if all(r.get("status") == "ok" for r in summary) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SLUGS = [
            a if a.endswith("_p3_xpart_cadfit_routea_v1") else f"{a}_p3_xpart_cadfit_routea_v1"
            for a in sys.argv[1:]
        ]
    raise SystemExit(main())
