#!/usr/bin/env python3
"""Re-run building_5i: fill missing Dora priors -> CADFit(with Dora) -> STEP -> assembly."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CASE = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1")
LOG = CASE / "logs/rerun_dora_cadfit.log"
PIPE = CASE / "scripts/run_pipeline.py"
DORA_PY = CASE / "scripts/run_dora_ses.py"
DORA = CASE / "dora_ses"
STL = CASE / "cadfit_routea/input_stl"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_cmd(cmd: list[str], cwd: Path | None = None) -> int:
    log("CMD " + " ".join(cmd))
    with LOG.open("a", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=str(cwd or CASE), stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"RC {rc}")
    return rc


def parts_missing_dora() -> list[str]:
    missing = []
    for stl in sorted(STL.glob("PART_*.stl")):
        pid = stl.stem
        found = False
        for th in (25, 35, 15, 45):
            p = DORA / f"threshold_{th}" / pid / "salient_edges_source_space.npz"
            if p.is_file() and p.stat().st_size > 0:
                found = True
                break
        if not found:
            missing.append(pid)
    return missing


def rebuild_dora_summary() -> None:
    """Refresh report/summary.json from all existing threshold part dirs."""
    rows = []
    for th in (15, 25, 35, 45):
        th_sum = DORA / f"threshold_{th}/summary.json"
        if th_sum.is_file():
            try:
                rows.extend(json.loads(th_sum.read_text()))
            except Exception:
                pass
    # also ensure marker exists even if empty-ish
    (DORA / "report").mkdir(parents=True, exist_ok=True)
    (DORA / "report/summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    log(f"rebuilt Dora summary rows={len(rows)}")


def main() -> int:
    log("=== building_5i Dora-prior CADFit rerun start ===")
    missing = parts_missing_dora()
    log(f"Dora missing priors: {missing}")
    if missing:
        rc = run_cmd(
            [
                sys.executable,
                "-u",
                str(DORA_PY),
                "--parts",
                *missing,
                "--skip-edge-json",
            ]
        )
        if rc != 0:
            log(f"Dora fill-in failed rc={rc}; continuing with available priors")
        rebuild_dora_summary()
    else:
        log("All STL parts already have Dora priors")

    # CADFit with Dora wait + edge dir wiring (in updated run_pipeline)
    rc = run_cmd(
        [
            sys.executable,
            "-u",
            str(PIPE),
            "--stage",
            "cadfit",
            "--skip-canary",
            "--jobs",
            "4",
            "--inner-workers",
            "4",
        ]
    )
    log(f"cadfit rc={rc}")

    rc2 = run_cmd([sys.executable, "-u", str(PIPE), "--stage", "step"])
    rc3 = run_cmd([sys.executable, "-u", str(PIPE), "--stage", "assembly"])

    done = list((CASE / "cadfit_routea/cadfit_raw").glob("PART_*/final_iou.json"))
    pm = CASE / "cadfit_routea/parallel_manifest.json"
    dora_flag = None
    if pm.is_file():
        dora_flag = json.loads(pm.read_text()).get("DORA_SES_USED_FOR_CAD")
    n_asm = None
    am = CASE / "assembly/assembly_manifest.json"
    if am.is_file():
        n_asm = json.loads(am.read_text()).get("parts_in_assembly")
    log(
        f"DONE cadfit_iou={len(done)} DORA_SES_USED_FOR_CAD={dora_flag} "
        f"assembly_parts={n_asm} step_rc={rc2} asm_rc={rc3}"
    )
    return 0 if (len(done) > 0 and rc2 == 0 and rc3 == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
