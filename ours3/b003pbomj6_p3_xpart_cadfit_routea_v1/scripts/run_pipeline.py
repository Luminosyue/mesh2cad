#!/usr/bin/env python3
"""Route A orchestrator: P3 freeze -> X-Part -> Dora SES | CADFit Route A -> STEP.

Tank protocol. Independent case directory. Does not import tank/airplane/robot scripts.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import (  # noqa: E402
    BLENDER_PY,
    CADFIT_DIR,
    CADFIT_PY,
    CADFIT_RAW,
    CADFIT_REPO,
    CASE,
    DORA_DIR,
    HUNYUAN_PY,
    HY3D_PY,
    LOGS,
    P3_DIR,
    SOURCE,
    SOURCE_ORIG,
    STL_DIR,
    XPART_DIR,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def log(msg: str, log_path: Path) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, env: dict | None = None) -> int:
    log(f"CMD {' '.join(str(c) for c in cmd)}", log_path)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=str(cwd), env=env, stdout=f, stderr=subprocess.STDOUT)
    return proc.returncode


def select_canaries(n: int = 5) -> list[str]:
    summary_path = CASE / "artifacts/xpart_summary.json"
    if summary_path.is_file():
        parts = json.loads(summary_path.read_text())["parts"]
        scored = sorted(parts, key=lambda r: -float(r.get("surface_area") or 0))
        ids = [r["part_id"] for r in scored]
    else:
        ids = [p.stem for p in sorted(STL_DIR.glob("PART_*.stl"))]
    if len(ids) <= n:
        return ids
    picks = [ids[0], ids[len(ids) // 4], ids[len(ids) // 2], ids[(3 * len(ids)) // 4], ids[-1]]
    out, seen = [], set()
    for pid in picks:
        if pid not in seen:
            seen.add(pid)
            out.append(pid)
    for pid in ids:
        if len(out) >= n:
            break
        if pid not in seen:
            seen.add(pid)
            out.append(pid)
    return out[:n]


def stage_source(log_path: Path) -> None:
    CASE.mkdir(parents=True, exist_ok=True)
    (CASE / "source").mkdir(parents=True, exist_ok=True)
    if not SOURCE.is_file():
        shutil.copy2(SOURCE_ORIG, SOURCE)
    write_json(
        CASE / "pipeline_manifest.json",
        {
            "case_root": str(CASE),
            "source_mesh": str(SOURCE),
            "created_at": utc_now(),
            "stages": ["source", "p3", "xpart", "dora_ses", "cadfit_routea"],
            "note": "Fresh cube run. Tank protocol. Independent directory.",
        },
    )
    log(f"source ready {SOURCE}", log_path)


def stage_p3(gpu: int, log_path: Path) -> dict:
    meta_path = P3_DIR / "part_metadata.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        log(f"P3 skip existing parts={meta.get('num_parts')}", log_path)
        return meta
    n_faces = 0
    with SOURCE.open() as f:
        for line in f:
            if line.startswith("f "):
                n_faces += 1
    # Tank recipe: point_num = face count, prompt_num=4000, prompt_bs=4.
    # Cap at 400k (tank was 367k) so 0.8M-1.3M high-poly scans do not OOM.
    point_num = min(n_faces, 400000)
    prompt_num = 4000
    prompt_bs = 4
    log(f"P3 start faces={n_faces} point_num={point_num} prompt_num={prompt_num} gpu={gpu}", log_path)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    rc = run_cmd(
        [
            str(HUNYUAN_PY),
            "-u",
            str(_HERE / "run_p3.py"),
            str(SOURCE),
            str(P3_DIR),
            "--prompt-bs",
            str(prompt_bs),
            "--point-num",
            str(point_num),
            "--prompt-num",
            str(prompt_num),
        ],
        CASE,
        log_path,
        env,
    )
    if rc != 0 or not meta_path.is_file():
        raise RuntimeError(f"P3 failed rc={rc}")
    meta = json.loads(meta_path.read_text())
    meta["P3_REEXECUTED"] = True
    meta["frozen"] = True
    write_json(P3_DIR / "manifest.json", meta)
    log(f"P3 freeze parts={meta.get('num_parts')} runtime={meta.get('runtime_seconds')}", log_path)
    return meta


def stage_xpart(gpu: int, log_path: Path, batch_size: int = 10) -> dict:
    manifest = XPART_DIR / "manifest.json"
    if manifest.is_file():
        summary = json.loads(manifest.read_text())
        if int(summary.get("XPART_SUCCESSFUL_PARTS") or 0) > 0:
            log(f"X-Part skip existing successful={summary.get('XPART_SUCCESSFUL_PARTS')}", log_path)
            return summary
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HY3DGEN_MODELS"] = "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart"
    env.setdefault("MPLCONFIGDIR", str(LOGS / "mpl"))
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    rc = run_cmd(
        [
            str(HY3D_PY),
            "-u",
            str(_HERE / "run_xpart.py"),
            "--gpu",
            str(gpu),
            "--octree-resolution",
            "512",
            "--batch-size",
            str(batch_size),
            "--source-mesh",
            str(SOURCE),
            "--p3-dir",
            str(P3_DIR),
            "--out-dir",
            str(XPART_DIR),
        ],
        CASE,
        log_path,
        env,
    )
    if rc != 0 or not manifest.is_file():
        raise RuntimeError(f"X-Part failed rc={rc}")
    summary = json.loads(manifest.read_text())
    if int(summary.get("XPART_SUCCESSFUL_PARTS") or 0) <= 0:
        raise RuntimeError("X-Part produced 0 parts")
    log(
        f"X-Part done successful={summary.get('XPART_SUCCESSFUL_PARTS')} "
        f"watertight={summary.get('XPART_WATERTIGHT_PARTS')} batch={batch_size}",
        log_path,
    )
    return summary


def stage_stl(log_path: Path) -> None:
    stls = list(STL_DIR.glob("PART_*.stl"))
    xparts = list(XPART_DIR.glob("PART_*"))
    if stls and len(stls) >= len(xparts) > 0:
        log(f"STL skip existing {len(stls)}", log_path)
        return
    rc = run_cmd([sys.executable, "-u", str(_HERE / "obj_to_stl.py")], CASE, log_path)
    if rc != 0:
        raise RuntimeError(f"OBJ->STL failed rc={rc}")
    log(f"STL ready {len(list(STL_DIR.glob('PART_*.stl')))}", log_path)


def _dora_pid_alive() -> bool:
    pid_file = DORA_DIR / "logs/dora_run.pid"
    if not pid_file.is_file():
        return False
    try:
        pid = int(pid_file.read_text().strip().split()[0])
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def stage_dora(log_path: Path, background: bool = False) -> None:
    done = DORA_DIR / "report/summary.json"
    if done.is_file():
        log("Dora SES skip existing report", log_path)
        return
    if _dora_pid_alive():
        log("Dora SES already running; skip spawn", log_path)
        return
    if not BLENDER_PY.is_file():
        raise FileNotFoundError(BLENDER_PY)
    cmd = [sys.executable, "-u", str(_HERE / "run_dora_ses.py"), "--all-parts", "--skip-edge-json"]
    if not background:
        rc = run_cmd(cmd, CASE, log_path)
        if rc != 0:
            raise RuntimeError(f"Dora SES failed rc={rc}")
        log("Dora SES done (priors will feed CADFit)", log_path)
        return
    dora_log = DORA_DIR / "logs/dora_run.log"
    dora_log.parent.mkdir(parents=True, exist_ok=True)
    with dora_log.open("a", encoding="utf-8") as f:
        proc = subprocess.Popen(cmd, cwd=str(CASE), stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
    (DORA_DIR / "logs/dora_run.pid").write_text(str(proc.pid) + "\n")
    log(f"Dora SES forked pid={proc.pid} (CADFit will wait and consume edge priors)", log_path)


def wait_for_dora(log_path: Path, timeout_s: int = 7200, poll_s: float = 15.0) -> None:
    """Block until Dora SES report exists so CADFit can load edge priors."""
    done = DORA_DIR / "report/summary.json"
    if done.is_file():
        log("Dora SES ready for CADFit", log_path)
        return
    if not _dora_pid_alive():
        log("Dora SES missing; running foreground before CADFit", log_path)
        stage_dora(log_path, background=False)
        if not done.is_file():
            raise RuntimeError("Dora SES did not produce report/summary.json")
        return
    log(f"waiting Dora SES report (timeout={timeout_s}s)", log_path)
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if done.is_file():
            log(f"Dora SES ready after {time.time()-t0:.1f}s", log_path)
            return
        time.sleep(poll_s)
    raise TimeoutError(f"Dora SES not ready after {timeout_s}s: {done}")


def stage_cadfit_canary(canaries: list[str], log_path: Path) -> None:
    canary_in = CADFIT_DIR / "_canary_input"
    canary_in.mkdir(parents=True, exist_ok=True)
    for p in canary_in.glob("*.stl"):
        p.unlink()
    pending = []
    for pid in canaries:
        if (CADFIT_RAW / pid / "final_iou.json").is_file():
            log(f"canary skip {pid}", log_path)
            continue
        src = STL_DIR / f"{pid}.stl"
        if src.is_file():
            shutil.copy2(src, canary_in / f"{pid}.stl")
            pending.append(pid)
    if not pending:
        log("canary CADFit nothing pending", log_path)
        return
    write_json(CADFIT_DIR / "canary_parts.json", {"canaries": canaries, "pending": pending})
    log(f"canary CADFit official single-thread {pending}", log_path)
    env = os.environ.copy()
    rc = run_cmd(
        [
            str(CADFIT_PY),
            "-u",
            str(CADFIT_REPO / "run_pipeline.py"),
            str(canary_in.resolve()),
            "--output-folder",
            str(CADFIT_RAW.resolve()),
            "--max-iterations",
            "1",
            "--keep-history",
            "--skip-existing",
            "--dora-edge-dir",
            str(DORA_DIR.resolve()),
            "--dora-threshold",
            "25",
        ],
        CADFIT_REPO,
        log_path,
        env,
    )
    if rc != 0:
        log(f"canary CADFit rc={rc} (continue to remaining)", log_path)


def stage_cadfit_parallel(
    jobs: int,
    inner_workers: int,
    log_path: Path,
    wait: bool = True,
) -> None:
    stls = sorted(p.stem for p in STL_DIR.glob("PART_*.stl"))
    remaining = [pid for pid in stls if not (CADFIT_RAW / pid / "final_iou.json").is_file()]
    if not remaining:
        log("parallel CADFit nothing pending", log_path)
        return
    cmd = [
        str(sys.executable),
        "-u",
        str(_HERE / "run_cadfit_parallel.py"),
        "--jobs",
        str(jobs),
        "--inner-workers",
        str(inner_workers),
        "--max-iterations",
        "1",
        "--output-dir",
        str(CADFIT_DIR),
        "--input-stl-dir",
        str(STL_DIR),
        "--raw-dir",
        str(CADFIT_RAW),
        "--dora-edge-dir",
        str(DORA_DIR.resolve()),
        "--dora-threshold",
        "25",
        "--parts",
        *remaining,
    ]
    log(f"parallel CADFit jobs={jobs} remaining={remaining} wait={wait}", log_path)
    if wait:
        rc = run_cmd(cmd, CASE, log_path)
        log(f"parallel CADFit rc={rc}", log_path)
        return
    parallel_log = CADFIT_DIR / "logs/parallel_run.log"
    parallel_log.parent.mkdir(parents=True, exist_ok=True)
    with parallel_log.open("a", encoding="utf-8") as f:
        proc = subprocess.Popen(cmd, cwd=str(CASE), stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
    (CADFIT_DIR / "logs/parallel_run.pid").write_text(str(proc.pid) + "\n")
    log(f"parallel CADFit pid={proc.pid}", log_path)


def stage_step(log_path: Path) -> None:
    rc = run_cmd([sys.executable, "-u", str(_HERE / "export_step.py")], CASE, log_path)
    log(f"STEP export rc={rc}", log_path)



def stage_assembly(log_path: Path) -> None:
    rc = run_cmd(
        [str(CADFIT_PY), "-u", str(_HERE / "build_assembly.py")],
        CASE,
        log_path,
    )
    if rc != 0:
        raise RuntimeError(f"assembly failed rc={rc}")
    log("assembly done", log_path)

def write_progress(stage: str, extra: dict | None = None) -> None:
    row = {"stage": stage, "time": utc_now()}
    if extra:
        row.update(extra)
    path = LOGS / "progress.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, default=3)
    parser.add_argument(
        "--stage",
        default="all",
        choices=["all", "source", "p3", "xpart", "stl", "dora", "cadfit", "step", "frontend", "assembly"],
    )
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--inner-workers", type=int, default=4)
    parser.add_argument("--xpart-batch-size", type=int, default=10)
    parser.add_argument("--skip-canary", action="store_true")
    args = parser.parse_args()

    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / "pipeline.log"
    stages = {
        "all": ["source", "p3", "xpart", "stl", "dora", "cadfit", "step", "assembly"],
        "frontend": ["source", "p3", "xpart", "stl", "dora"],
        "source": ["source"],
        "p3": ["source", "p3"],
        "xpart": ["xpart"],
        "stl": ["stl"],
        "dora": ["dora"],
        "cadfit": ["stl", "dora", "cadfit"],
        "step": ["step"],
        "assembly": ["assembly"],
    }[args.stage]

    t0 = time.time()
    try:
        if "source" in stages:
            stage_source(log_path)
            write_progress("source")
        if "p3" in stages:
            meta = stage_p3(args.gpu, log_path)
            write_progress("p3", {"num_parts": meta.get("num_parts")})
        if "xpart" in stages:
            summary = stage_xpart(args.gpu, log_path, batch_size=args.xpart_batch_size)
            write_progress("xpart", {"successful": summary.get("XPART_SUCCESSFUL_PARTS")})
        if "stl" in stages:
            stage_stl(log_path)
            write_progress("stl")
        if "dora" in stages:
            # Frontend may fork Dora; CADFit always waits and consumes priors.
            stage_dora(log_path, background=(args.stage in ("all", "frontend")))
            write_progress("dora")
        if "cadfit" in stages:
            wait_for_dora(log_path)
            write_progress("dora_ready_for_cadfit")
            canaries = [] if args.skip_canary else select_canaries(5)
            write_json(CADFIT_DIR / "canary_parts.json", {"canaries": canaries})
            if canaries and not args.skip_canary:
                stage_cadfit_canary(canaries, log_path)
                write_progress("cadfit_canary", {"parts": canaries})
            stage_cadfit_parallel(args.jobs, args.inner_workers, log_path, wait=True)
            write_progress("cadfit_parallel")
        if "step" in stages:
            stage_step(log_path)
            write_progress("step")
        if "assembly" in stages:
            stage_assembly(log_path)
            write_progress("assembly")
    except Exception as exc:
        log(f"FAILED {exc!r}", log_path)
        write_progress("failed", {"error": repr(exc)})
        raise
    log(f"orchestrator stage={args.stage} elapsed={time.time()-t0:.1f}s", log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
