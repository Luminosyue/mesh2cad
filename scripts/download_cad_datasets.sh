#!/usr/bin/env bash
# Download CADParser + Fusion360 Gallery Reconstruction datasets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CADPARSER_DIR="${ROOT}/cad_spatial_dataset/CADParser"
FUSION_DIR="${ROOT}/cad_spatial_dataset/Fusion360"
FUSION_ZIP="${FUSION_DIR}/r1.0.1.zip"
FUSION_URL="https://fusion-360-gallery-dataset.s3.us-west-2.amazonaws.com/reconstruction/r1.0.1/r1.0.1.zip"
CADPARSER_GDRIVE="https://drive.google.com/CADParserData"
EXPECTED_BYTES=2103449157

mkdir -p "${CADPARSER_DIR}" "${FUSION_DIR}"

log() { echo "[$(date '+%F %T')] $*"; }

verify_fusion_zip() {
  python3 - <<'PY' "${FUSION_ZIP}"
import sys, zipfile
path = sys.argv[1]
with zipfile.ZipFile(path) as z:
    print(len(z.namelist()))
PY
}

download_fusion_repo() {
  if [[ -d "${FUSION_DIR}/repo/.git" || -f "${FUSION_DIR}/repo/README.md" ]]; then
    log "Fusion360 repo already present"
    return 0
  fi
  log "Cloning Fusion360GalleryDataset repo..."
  if git clone --depth 1 https://github.com/AutodeskAILab/Fusion360GalleryDataset.git "${FUSION_DIR}/repo"; then
    return 0
  fi
  log "git clone failed; trying GitHub archive zip..."
  curl -L --retry 5 --retry-delay 3 \
    -o "${FUSION_DIR}/repo.zip" \
    "https://github.com/AutodeskAILab/Fusion360GalleryDataset/archive/refs/heads/master.zip"
  unzip -q -o "${FUSION_DIR}/repo.zip" -d "${FUSION_DIR}"
  rm -rf "${FUSION_DIR}/repo"
  mv "${FUSION_DIR}/Fusion360GalleryDataset-master" "${FUSION_DIR}/repo"
  rm -f "${FUSION_DIR}/repo.zip"
}

download_fusion_data() {
  if [[ -f "${FUSION_ZIP}" ]] && [[ "$(stat -c%s "${FUSION_ZIP}")" -eq "${EXPECTED_BYTES}" ]]; then
    if verify_fusion_zip >/dev/null 2>&1; then
      log "Fusion360 reconstruction zip already valid"
    else
      log "Fusion360 zip size OK but corrupt; re-downloading"
      rm -f "${FUSION_ZIP}" "${FUSION_ZIP}.aria2"
    fi
  fi

  if [[ ! -f "${FUSION_ZIP}" ]] || [[ "$(stat -c%s "${FUSION_ZIP}" 2>/dev/null || echo 0)" -ne "${EXPECTED_BYTES}" ]]; then
    log "Downloading Fusion360 reconstruction dataset (~2.0 GB)..."
    if command -v aria2c >/dev/null; then
      aria2c -c -x 16 -s 16 --file-allocation=none -d "${FUSION_DIR}" -o r1.0.1.zip "${FUSION_URL}"
    else
      wget -c -O "${FUSION_ZIP}" "${FUSION_URL}"
    fi
  fi

  verify_fusion_zip >/dev/null
  log "Fusion360 zip verified"

  if [[ ! -d "${FUSION_DIR}/reconstruction" ]]; then
    log "Extracting Fusion360 reconstruction dataset..."
    unzip -q "${FUSION_ZIP}" -d "${FUSION_DIR}"
    if [[ -d "${FUSION_DIR}/r1.0.1" ]]; then
      mv "${FUSION_DIR}/r1.0.1" "${FUSION_DIR}/reconstruction"
    fi
  fi
}

download_cadparser() {
  # Official source: Google Drive folder published by CADParser authors (IJCAI 2023).
  if compgen -G "${CADPARSER_DIR}/**/sequence*.json" >/dev/null || \
     compgen -G "${CADPARSER_DIR}/**/*.step" >/dev/null || \
     [[ -d "${CADPARSER_DIR}/CADParserData" ]]; then
    log "CADParser data already present under ${CADPARSER_DIR}"
    return 0
  fi

  python3 -m pip install -q gdown
  log "Downloading CADParser from Google Drive (requires outbound access to drive.google.com)..."
  gdown --folder "${CADPARSER_GDRIVE}" -O "${CADPARSER_DIR}" --remaining-ok
  log "CADParser download finished"
}

main() {
  case "${1:-all}" in
    fusion)
      download_fusion_repo
      download_fusion_data
      ;;
    cadparser)
      download_cadparser
      ;;
    all)
      download_fusion_repo
      download_fusion_data
      download_cadparser
      ;;
    *)
      echo "Usage: $0 [all|fusion|cadparser]" >&2
      exit 1
      ;;
  esac
  log "Done."
}

main "$@"
