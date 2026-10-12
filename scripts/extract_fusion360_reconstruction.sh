#!/usr/bin/env bash
# Extract Fusion360 reconstruction zip once download is complete.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FUSION_DIR="${ROOT}/cad_spatial_dataset/Fusion360"
ZIP="${FUSION_DIR}/r1.0.1.zip"
EXPECTED=2103449157

if [[ ! -f "${ZIP}" ]]; then
  echo "Missing ${ZIP}" >&2
  exit 1
fi

ACTUAL=$(stat -c%s "${ZIP}")
if [[ "${ACTUAL}" -ne "${EXPECTED}" ]]; then
  echo "Zip incomplete: ${ACTUAL}/${EXPECTED} bytes" >&2
  exit 1
fi

python3 - <<'PY' "${ZIP}"
import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    print("zip entries:", len(z.namelist()))
PY

if [[ -d "${FUSION_DIR}/reconstruction" ]]; then
  echo "Already extracted: ${FUSION_DIR}/reconstruction"
  exit 0
fi

echo "Extracting to ${FUSION_DIR}/reconstruction ..."
unzip -q "${ZIP}" -d "${FUSION_DIR}"
if [[ -d "${FUSION_DIR}/r1.0.1" ]]; then
  mv "${FUSION_DIR}/r1.0.1" "${FUSION_DIR}/reconstruction"
fi

echo "Sample files:"
find "${FUSION_DIR}/reconstruction" -maxdepth 1 -type f | head -10
