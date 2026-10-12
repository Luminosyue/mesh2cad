#!/usr/bin/env bash
# Scheme A fair trio: keep J0 (done); snatch GPUs for J2-O + J2-P until both finish.
# J2-O: CAD_EDGE_SOURCE=gt_sharp   cutoff=4096
# J2-P: CAD_EDGE_SOURCE=detected   cutoff=4096
# Effective batch always 4 (1GPU×accum4 or 2GPU×accum2).
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
TORCHRUN="${TORCHRUN:-/data/miniconda3/envs/spatiallm/bin/torchrun}"
LOG_DIR="$ROOT/cad_spatial_dataset/joint_deepcad_fusion360_v1"
SLOG="$LOG_DIR/scheme_a_j2op_monitor.log"
MIN_FREE="${MIN_FREE:-36000}"
POLL_SEC="${POLL_SEC:-20}"
LOCK=/tmp/scheme_a_j2op_monitor.lock

J2O_CFG_NAME=spatiallm_cad_joint_j2o_oracle.yaml
J2P_CFG_NAME=spatiallm_cad_joint_j2p_detected.yaml
J2O_CFG=configs/$J2O_CFG_NAME
J2P_CFG=configs/$J2P_CFG_NAME
J2O_OUT="$ROOT/SpatialLM/saves/joint_j2o_oracle_v1"
J2P_OUT="$ROOT/SpatialLM/saves/joint_j2p_detected_v1"
J2O_LOG="$LOG_DIR/joint_j2o_oracle_v1.log"
J2P_LOG="$LOG_DIR/joint_j2p_detected_v1.log"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] monitor already running" >>"$SLOG"; exit 0; }

mkdir -p "$LOG_DIR"
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >>"$SLOG"; }

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONPATH="$ROOT/SpatialLM"
export PATH="$(dirname "$PYTHON"):${PATH:-}"
export TORCHRUN_BIN="$TORCHRUN"

done_j2o() { [[ -f "$J2O_OUT/all_results.json" || -f "$J2O_OUT/train_results.json" ]]; }
done_j2p() { [[ -f "$J2P_OUT/all_results.json" || -f "$J2P_OUT/train_results.json" ]]; }

running_cfg() {
  local cfg="$1"
  # Match either the canonical config name or the mktemp launch copy (/tmp/j2o_XXXX.yaml).
  local pat="$cfg"
  case "$cfg" in
    *j2o_oracle*) pat='(/tmp/j2o_|spatiallm_cad_joint_j2o_oracle)' ;;
    *j2p_detected*) pat='(/tmp/j2p_|spatiallm_cad_joint_j2p_detected)' ;;
  esac
  ps -eo pid=,comm=,args= 2>/dev/null | awk -v pat="$pat" '
    ($2 ~ /python/ || $2 == "pt_main_thread") && $0 ~ pat { found=1 }
    END { exit !found }'
}

busy_ours() {
  local pids
  pids=$(pgrep -f '/tmp/j2o_|/tmp/j2p_|spatiallm_cad_joint_j2o_oracle|spatiallm_cad_joint_j2p_detected' 2>/dev/null \
    | tr '\n' '|' | sed 's/|$//')
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

# Prefer single empty 44GB card (J2 cut4096 is memory-sensitive). Fall back to 2-GPU DDP.
launch_one() {
  local name="$1"   # j2o | j2p
  local cfg_name="$2"
  local cfg_src="$3"
  local edge_src="$4"
  local logf="$5"
  local pidf="$6"
  local port="$7"
  local gpus="$8"
  local n; n=$(awk -F, '{print NF}' <<<"$gpus")

  log "LAUNCH $name on GPU=$gpus (n=$n) edge=$edge_src cutoff=4096"
  (
    cd "$ROOT/SpatialLM" || exit 1
    unset CAD_USE_EDGE_SCORE || true
    export CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE="$edge_src"
    CFG=$(mktemp "/tmp/${name}_XXXX.yaml")
    cp "$cfg_src" "$CFG"
    if (( n >= 2 )); then
      export FORCE_TORCHRUN=1 NPROC_PER_NODE=2 MASTER_PORT="$port"
      sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 2/' "$CFG"
    else
      unset FORCE_TORCHRUN NPROC_PER_NODE || true
      sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 4/' "$CFG"
    fi
    CUDA_VISIBLE_DEVICES="$gpus" "$PYTHON" train.py "$CFG"
    rm -f "$CFG"
  ) >>"$logf" 2>&1 &
  echo $! >"$pidf"
}

log "=== scheme-A J2-O/J2-P monitor start MIN_FREE=${MIN_FREE}MB poll=${POLL_SEC}s ==="
log "J0 already complete at saves/joint_j0_surface_v1 (reuse; cutoff=4096)"

while true; do
  if done_j2o && done_j2p; then
    log "J2-O and J2-P BOTH DONE"
    break
  fi

  BUSY=$(busy_ours || true)
  NEED_O=0; NEED_P=0
  done_j2o || running_cfg "$J2O_CFG_NAME" || NEED_O=1
  done_j2p || running_cfg "$J2P_CFG_NAME" || NEED_P=1

  log "status need_j2o=$NEED_O need_j2p=$NEED_P busy=${BUSY:-none} o_run=$(running_cfg "$J2O_CFG_NAME" && echo y || echo n) p_run=$(running_cfg "$J2P_CFG_NAME" && echo y || echo n)"

  if (( NEED_O == 0 && NEED_P == 0 )); then
    sleep "$POLL_SEC"
    continue
  fi

  # Prefer launching the missing job that isn't running; one card each.
  if (( NEED_O == 1 )); then
    GPUS=$(free_gpus 1 "${BUSY:-}")
    if [[ -n "${GPUS:-}" ]]; then
      launch_one j2o "$J2O_CFG_NAME" "$J2O_CFG" gt_sharp "$J2O_LOG" /tmp/joint_j2o.pid 29541 "$GPUS"
      sleep 60
      if running_cfg "$J2O_CFG_NAME"; then log "J2-O running ok"; else log "J2-O died early; will retry"; fi
      BUSY=$(busy_ours || true)
    else
      log "J2-O wait: no GPU >=${MIN_FREE}MB (exclude=${BUSY:-none})"
    fi
  fi

  if (( NEED_P == 1 )); then
    GPUS=$(free_gpus 1 "${BUSY:-}")
    if [[ -n "${GPUS:-}" ]]; then
      launch_one j2p "$J2P_CFG_NAME" "$J2P_CFG" detected "$J2P_LOG" /tmp/joint_j2p.pid 29551 "$GPUS"
      sleep 60
      if running_cfg "$J2P_CFG_NAME"; then log "J2-P running ok"; else log "J2-P died early; will retry"; fi
    else
      log "J2-P wait: no GPU >=${MIN_FREE}MB (exclude=${BUSY:-none})"
    fi
  fi

  sleep "$POLL_SEC"
done

log "=== scheme-A monitor exit ==="
