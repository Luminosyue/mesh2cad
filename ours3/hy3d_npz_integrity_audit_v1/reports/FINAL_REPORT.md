# HY3D NPZ Integrity Audit V1

## Frozen input

The exact 100 paths from `/data/home/cuiyuehan/project/mesh2cad/ours3/hy3d_part_watertight_audit_v1/manifests/NPZ100_MANIFEST.csv` were inspected. No file was replaced, deleted, repaired, or supplemented.

## Counts

- NPZ_N=100
- VALID_NPZ_N=11
- INVALID_NPZ_N=89
- ZIP_MAGIC_VALID_N=100
- ZIP_TEST_PASS_N=11
- LFS_XET_POINTER_N=0
- HTML_ERROR_N=0
- TRUNCATED_ZIP_N=89
- CRC_ERROR_N=0
- NOT_ZIP_N=0
- NUMPY_FORMAT_ERROR_N=0
- OTHER_N=0

## File-size evidence

- Loadable: {'n': 11, 'min': 675733, 'median': 3207597, 'max': 6110356}
- Failed: {'n': 89, 'min': 7864320, 'median': 7864320, 'max': 7864320}
- Dominant failed size: 7864320 bytes in 89/89 failures

## ZIP and NumPy diagnosis

All classifications are mutually exclusive and recorded per file with 32-byte magic, `file` output, `zipfile.is_zipfile`, `testzip`, and forced NumPy entry reads for both pickle modes. `REQUIRES_PICKLE_N=0`.

## Pointer/error-file diagnosis

Pointer files=0; HTML/XML/error responses=0. Text previews are sanitized and stored only when magic is invalid or files are small.

## Tar archive comparison

Original `00.tar.gz` available: False. Candidates: []. Listing result: NOT_AVAILABLE. Because no source archive is present, the requested 5-valid/5-failed archive-size comparison cannot be performed and no `EXTRACTION_CORRUPTION` or `ARCHIVE_CORRUPTION` label is asserted.

## Primary failure cause

`A. DOWNLOAD_OR_TRANSFER_TRUNCATION`

The 89 failures are primarily transfer/download truncation: they retain the ZIP local-header magic but lack a valid central directory, and most share an exact 7.5 MiB cutoff. The source tar is unavailable, so extraction-vs-download origin cannot be proven from archive comparison.

## Recommended recovery

Re-acquire the same frozen 89 paths (not replacement samples), verify expected size and SHA-256 after transfer, and rerun this integrity audit before repeating the watertight audit. Do not automatically download as part of this stage.

## Gate

`CURRENT_GATE=NPZ_DATA_INTEGRITY_REPAIR_REQUIRED`
