#!/usr/bin/env python3
"""Resume tank protocol from frozen P3: X-Part -> STL -> CADFit -> STEP -> assembly."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_more_v2"
LOG = LADDER / "logs/continue_from_xpart.log"
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
MIN_FREE_MB = 24000
CADFIT_JOBS = 4
INNER = 4


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
        log(f"waiting for GPU >={min_free_mb} MiB; best gpu{idx}={free}")
        time.sleep(45)


def cadfit_busy() -> bool:
    try:
        out = subprocess.check_output(["ps", "-ef"], text=True)
    except Exception:
        return False
    return "run_cadfit_parallel.py" in out


def xpart_ok(case: Path) -> bool:
    manifest = case / "xpart/manifest.json"
    if not manifest.is_file():
        return False
    try:
        n = int(json.loads(manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0)
    except Exception:
        return False
    return n > 0


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, env: dict | None = None) -> int:
    log(f"CMD {' '.join(cmd)}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=str(cwd), env=env, stdout=f, stderr=subprocess.STDOUT)
    log(f"RC {proc.returncode} {' '.join(cmd[:6])}")
    return proc.returncode


def run_xpart(case: Path, gpu: int, octree: int, batch: int) -> int:
    script = case / "scripts/run_xpart.py"
    return run_cmd(
        [
            str(HY3D_PY),
            "-u",
            str(script),
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


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    summary = []
    for spec in cases:
        case = Path(spec["case_root"])
        row = {"label": spec["label"], "case": str(case)}
        if not (case / "p3/part_metadata.json").is_file():
            row["status"] = "no_p3"
            summary.append(row)
            continue
        if xpart_ok(case):
            log(f"{spec['label']} X-Part already ok")
            row["xpart"] = "skip"
        else:
            gpu = pick_gpu()
            rc = run_xpart(case, gpu, octree=512, batch=1)
            row["xpart_512_rc"] = rc
            row["gpu"] = gpu
            if rc != 0 or not xpart_ok(case):
                gpu = pick_gpu()
                log(f"{spec['label']} X-Part retry octree=256 gpu={gpu}")
                rc = run_xpart(case, gpu, octree=256, batch=1)
                row["xpart_256_rc"] = rc
                row["gpu"] = gpu
            if not xpart_ok(case):
                row["status"] = "xpart_fail"
                summary.append(row)
                continue
        rc = run_pipeline(case, ["--stage", "stl"], "stl.log")
        row["stl_rc"] = rc
        run_pipeline(case, ["--stage", "dora"], "dora.log")
        while cadfit_busy():
            log(f"{spec['label']} waiting for existing CADFit")
            time.sleep(60)
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
        summary.append(row)
        log(f"{spec['label']} status={row['status']}")
    out = LADDER / "logs/continue_from_xpart_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": summary}, indent=2) + "\n")
    log(f"done {out}")
    return 0 if all(r.get("status") == "ok" for r in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
