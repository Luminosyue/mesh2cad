#!/usr/bin/env bash
# Continuously snatch free GPUs for joint J0/J2 until both finish.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
TORCHRUN="${TORCHRUN:-/data/miniconda3/envs/spatiallm/bin/torchrun}"
LOG_DIR="$ROOT/cad_spatial_dataset/joint_deepcad_fusion360_v1"
SLOG="$LOG_DIR/joint_gpu_monitor.log"
MIN_FREE="${MIN_FREE:-36000}"
POLL_SEC="${POLL_SEC:-15}"
LOCK=/tmp/joint_gpu_monitor.lock

J0_CFG_NAME=spatiallm_cad_joint_j0_surface.yaml
J2_CFG_NAME=spatiallm_cad_joint_j2_sepedge.yaml
J0_CFG=configs/$J0_CFG_NAME
J2_CFG=configs/$J2_CFG_NAME
J0_OUT="$ROOT/SpatialLM/saves/joint_j0_surface_v1"
J2_OUT="$ROOT/SpatialLM/saves/joint_j2_sepedge_v1_cut2048"
J0_LOG="$LOG_DIR/joint_j0_surface_v1.log"
J2_LOG="$LOG_DIR/joint_j2_sepedge_v1.log"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] monitor already running" >>"$SLOG"; exit 0; }

mkdir -p "$LOG_DIR"
# Single writer: avoid double lines when stdout is also redirected to SLOG.
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >>"$SLOG"; }

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONPATH="$ROOT/SpatialLM"
export PATH="$(dirname "$PYTHON"):${PATH:-}"
export TORCHRUN_BIN="$TORCHRUN"

done_j0() { [[ -f "$J0_OUT/all_results.json" || -f "$J0_OUT/train_results.json" ]]; }
done_j2() { [[ -f "$J2_OUT/all_results.json" || -f "$J2_OUT/train_results.json" ]]; }
running_j0() {
  ps -eo pid=,comm=,args= 2>/dev/null | awk -v cfg="$J0_CFG_NAME" '
    ($2 ~ /python/ || $2 == "pt_main_thread") && $0 ~ cfg { found=1 }
    END { exit !found }'
}
running_j2() {
  ps -eo pid=,comm=,args= 2>/dev/null | awk -v cfg="$J2_CFG_NAME" '
    ($2 ~ /python/ || $2 == "pt_main_thread") && $0 ~ cfg { found=1 }
    END { exit !found }'
}

# GPUs with our train processes, via nvidia-smi pids only (no hang).
busy_ours() {
  local pids gpus=""
  pids=$(pgrep -f "$J0_CFG_NAME|$J2_CFG_NAME" 2>/dev/null | tr '\n' '|' | sed 's/|$//')
  [[ -z "$pids" ]] && { echo ""; return; }
  nvidia-smi --query-compute-apps=gpu_bus_id,pid --format=csv,noheader,nounits 2>/dev/null \
    | while IFS=',' read -r bus pid; do
        bus=$(echo "$bus" | xargs); pid=$(echo "$pid" | xargs)
        echo "$pids" | grep -qE "(^|\\|)${pid}(\\||$)" || continue
        nvidia-smi --query-gpu=index,gpu_bus_id --format=csv,noheader 2>/dev/null \
          | awk -F', ' -v b="$bus" '{gsub(/ /,"",$1); gsub(/ /,"",$2); if($2==b) print $1}'
      done | sort -nu | paste -sd, -
}

free_gpus() {
  local need="$1"
  local exclude="${2:-}"
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' -v m="$MIN_FREE" -v ex="$exclude" '
        BEGIN{n=split(ex,a,","); for(i=1;i<=n;i++) if(a[i]!="") bad[a[i]+0]=1}
        {gsub(/ /,"",$1); gsub(/ /,"",$2);
         if(!(($1+0) in bad) && $2+0>=m) print $2+0, $1+0}' \
    | sort -nr | head -n "$need" | awk '{print $2}' | paste -sd, -
}

launch_j0() {
  local gpus="$1"
  local n; n=$(awk -F, '{print NF}' <<<"$gpus")
  log "LAUNCH J0 on GPU=$gpus (n=$n)"
  (
    cd "$ROOT/SpatialLM" || exit 1
    unset CAD_USE_EDGE_SCORE CAD_USE_SEPARATE_EDGE_TOKENS CAD_EDGE_SOURCE
    if (( n >= 2 )); then
      export FORCE_TORCHRUN=1 NPROC_PER_NODE=2 MASTER_PORT=29521
      CFG=$(mktemp /tmp/j0_ddp_XXXX.yaml)
      cp "$J0_CFG" "$CFG"
      sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 2/' "$CFG"
      CUDA_VISIBLE_DEVICES="$gpus" "$PYTHON" train.py "$CFG"
      rm -f "$CFG"
    else
      unset FORCE_TORCHRUN NPROC_PER_NODE || true
      CFG=$(mktemp /tmp/j0_s_XXXX.yaml)
      cp "$J0_CFG" "$CFG"
      sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 4/' "$CFG"
      CUDA_VISIBLE_DEVICES="$gpus" "$PYTHON" train.py "$CFG"
      rm -f "$CFG"
    fi
  ) >>"$J0_LOG" 2>&1 &
  echo $! >/tmp/joint_j0.pid
}

launch_j2() {
  local gpus="$1"
  local n; n=$(awk -F, '{print NF}' <<<"$gpus")
  log "LAUNCH J2 on GPU=$gpus (n=$n)"
  (
    cd "$ROOT/SpatialLM" || exit 1
    unset CAD_USE_EDGE_SCORE FORCE_TORCHRUN NPROC_PER_NODE || true
    export CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE=gt_sharp
    if (( n >= 2 )); then
      export FORCE_TORCHRUN=1 NPROC_PER_NODE=2 MASTER_PORT=29531
      CFG=$(mktemp /tmp/j2_ddp_XXXX.yaml)
      cp "$J2_CFG" "$CFG"
      sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 2/' "$CFG"
      CUDA_VISIBLE_DEVICES="$gpus" "$PYTHON" train.py "$CFG"
      rm -f "$CFG"
    else
      CUDA_VISIBLE_DEVICES="$gpus" "$PYTHON" train.py "$J2_CFG"
    fi
  ) >>"$J2_LOG" 2>&1 &
  echo $! >/tmp/joint_j2.pid
}

log "=== joint GPU monitor start MIN_FREE=${MIN_FREE}MB poll=${POLL_SEC}s ==="

while true; do
  if done_j0 && done_j2; then
    log "BOTH DONE"; break
  fi

  BUSY=$(busy_ours || true)
  NEED_J0=0; NEED_J2=0
  done_j0 || running_j0 || NEED_J0=1
  done_j2 || running_j2 || NEED_J2=1

  log "status need_j0=$NEED_J0 need_j2=$NEED_J2 busy_ours=${BUSY:-none} j0_run=$(running_j0 && echo y || echo n) j2_run=$(running_j2 && echo y || echo n)"

  if (( NEED_J0 == 0 && NEED_J2 == 0 )); then
    sleep "$POLL_SEC"
    continue
  fi

  if (( NEED_J2 == 1 )); then
    GPUS=$(free_gpus 1 "${BUSY:-}")
    if [[ -n "${GPUS:-}" ]]; then
      launch_j2 "$GPUS"
      sleep 50
      if running_j2; then log "J2 running ok"; else log "J2 died early; will retry"; fi
      BUSY=$(busy_ours || true)
    else
      log "J2 wait: no GPU >=${MIN_FREE}MB free (exclude=${BUSY:-none})"
    fi
  fi

  if (( NEED_J0 == 1 )); then
    GPUS2=$(free_gpus 2 "${BUSY:-}")
    N2=$(awk -F, '{print NF}' <<<"${GPUS2:-}")
    if [[ -n "${GPUS2:-}" && "${N2:-0}" -ge 2 ]]; then
      launch_j0 "$GPUS2"
    else
      GPUS1=$(free_gpus 1 "${BUSY:-}")
      if [[ -n "${GPUS1:-}" ]]; then
        launch_j0 "$GPUS1"
      else
        log "J0 wait: no GPU >=${MIN_FREE}MB free (exclude=${BUSY:-none})"
      fi
    fi
    sleep 50
    if running_j0; then log "J0 running ok"; else log "J0 died early; will retry"; fi
  fi

  sleep "$POLL_SEC"
done

log "monitor exit"
