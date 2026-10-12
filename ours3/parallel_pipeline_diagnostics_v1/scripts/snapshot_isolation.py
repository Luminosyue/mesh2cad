#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "parallel_pipeline_diagnostics_v1"
EXCLUDE = OUT.resolve()
CODE_SUFFIXES = {".py", ".sh", ".bash", ".yaml", ".yml", ".toml"}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""): h.update(block)
    return h.hexdigest()


def command(args):
    try: return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, timeout=15)
    except Exception as exc: return f"ERROR: {type(exc).__name__}: {exc}"


def main():
    phase = os.environ.get("SNAPSHOT_PHASE", "before")
    files = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES: continue
        try: path.resolve().relative_to(EXCLUDE)
        except ValueError: pass
        else: continue
        try:
            stat = path.stat(); files[str(path)] = {"sha256": sha256(path), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        except (FileNotFoundError, PermissionError): continue
    step_inventory = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".step", ".stp"}: continue
        try: path.resolve().relative_to(EXCLUDE)
        except ValueError: pass
        else: continue
        try:
            stat = path.stat(); step_inventory[str(path)] = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        except (FileNotFoundError, PermissionError): continue
    payload = {
        "phase": phase, "root": str(ROOT), "excluded_output_root": str(EXCLUDE),
        "code_file_count": len(files), "code_files": files,
        "preexisting_step_count": len(step_inventory), "step_inventory_metadata": step_inventory,
        "gpu_compute_processes": command(["nvidia-smi", "--query-compute-apps=pid,gpu_uuid,used_memory,process_name", "--format=csv,noheader,nounits"]),
        "gpu_state": command(["nvidia-smi", "--query-gpu=index,uuid,memory.used,utilization.gpu", "--format=csv,noheader,nounits"]),
        "memory": command(["free", "-b"]), "load": command(["uptime"]),
    }
    dest = OUT / "isolation" / f"{phase}_snapshot.json"; dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"snapshot": str(dest), "code_file_count": len(files), "step_count": len(step_inventory)}))


if __name__ == "__main__": main()
