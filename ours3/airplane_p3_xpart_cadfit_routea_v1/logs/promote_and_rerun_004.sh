#!/bin/bash
set -u
export PYTHONUNBUFFERED=1
export CADFIT_INNER_WORKERS=8
ROOT=/data/home/cuiyuehan/project/mesh2cad
RAW=$ROOT/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw
IN=$ROOT/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/_isolated_input
PY=/data/miniconda3/envs/cadfit-env/bin/python
PIPE=$ROOT/CADFit/run_pipeline.py
WAIT_PID=468089

echo "[$(date -Iseconds)] waiting for 001/002 rerun pid=$WAIT_PID"
while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 15; done
echo "[$(date -Iseconds)] 001/002 rerun finished"

python3 - << 'PY'
import json, shutil
from pathlib import Path

raw = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw")

def iou_of(p: Path):
    f = p / "final_iou.json"
    if not f.is_file():
        return None
    return float(json.loads(f.read_text())["final_iou"])

for pid in ["PART_001", "PART_002"]:
    cur = raw / pid
    backups = sorted(raw.glob(f"{pid}_v1_filter_cut_*"), key=lambda p: p.stat().st_mtime)
    if not backups:
        print(f"{pid}: no v1 backup, keep current")
        continue
    old = backups[-1]
    new_iou, old_iou = iou_of(cur), iou_of(old)
    print(f"{pid}: new={new_iou} old={old_iou} backup={old.name}")
    if new_iou is None:
        print(f"{pid}: new missing, restore v1")
        if cur.exists():
            shutil.rmtree(cur)
        shutil.copytree(old, cur)
        continue
    if old_iou is not None and new_iou + 1e-9 < old_iou:
        print(f"{pid}: new worse, restore v1")
        bad = raw / f"{pid}_v2_rejected"
        if bad.exists():
            shutil.rmtree(bad)
        cur.rename(bad)
        shutil.copytree(old, cur)
    else:
        print(f"{pid}: keep new (overwrite official PART dir)")
        (cur / "rerun_choice.json").write_text(json.dumps({
            "kept": "new",
            "new_iou": new_iou,
            "old_iou": old_iou,
            "backup": str(old),
        }, indent=2) + "\n")
PY

ts=$(date +%Y%m%d_%H%M%S)
if [ -d "$RAW/PART_004" ]; then
  mv "$RAW/PART_004" "$RAW/PART_004_v1_filter_cut_$ts"
  echo "[$(date -Iseconds)] backed up PART_004 -> PART_004_v1_filter_cut_$ts"
fi

echo "[$(date -Iseconds)] START PART_004 no-filter-sketches over-threshold=999"
cd $ROOT/CADFit
"$PY" -u "$PIPE" "$IN/PART_004" \
  --output-folder "$RAW" \
  --max-iterations 1 \
  --limit 1 \
  --keep-history \
  --over-threshold 999 \
  --under-threshold 0.01
rc=$?
echo "[$(date -Iseconds)] DONE PART_004 rc=$rc"

python3 - << 'PY'
import json, shutil
from pathlib import Path
raw = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw")
pid = "PART_004"
cur = raw / pid
backups = sorted(raw.glob(f"{pid}_v1_filter_cut_*"), key=lambda p: p.stat().st_mtime)
old = backups[-1] if backups else None

def iou_of(p):
    f = p / "final_iou.json"
    return float(json.loads(f.read_text())["final_iou"]) if p and (p/"final_iou.json").is_file() else None

new_iou, old_iou = iou_of(cur), iou_of(old) if old else None
print(f"PART_004: new={new_iou} old={old_iou}")
if new_iou is None and old is not None:
    if cur.exists():
        shutil.rmtree(cur)
    shutil.copytree(old, cur)
    print("PART_004: restore v1")
elif old_iou is not None and new_iou is not None and new_iou + 1e-9 < old_iou:
    bad = raw / f"{pid}_v2_rejected"
    if bad.exists():
        shutil.rmtree(bad)
    cur.rename(bad)
    shutil.copytree(old, cur)
    print("PART_004: new worse, restore v1")
else:
    print("PART_004: keep new")
    if cur.exists():
        (cur / "rerun_choice.json").write_text(json.dumps({
            "kept": "new", "new_iou": new_iou, "old_iou": old_iou
        }, indent=2) + "\n")
PY
echo "[$(date -Iseconds)] ALL DONE"
