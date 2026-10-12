# TEASER_AND_DEMO_EXPORT V1

## Verified cases

| Case | Raw tokens | Compact/generated | Reduction | Free exact | Natural EOS | STEP | Geometry |
|---|---:|---:|---:|---|---|---|---|
| PART_000 (Short) | 5,607 | 2,810 / 2,810 | 49.88% | PASS | PASS | PASS | IoU 1.0, CD 0.0 |
| PART_001 (Medium) | 12,917 | 6,596 / 6,596 | 48.94% | PASS | PASS | PASS | IoU 1.0, CD 0.0 |
| PART_005 (Long) | 25,106 | 12,850 / 12,850 | 48.82% | PASS | PASS | PASS | IoU 1.0, CD 0.0 |

All three teaser cases are deterministic full-sequence free-decoding exact with natural EOS and successful STEP readback. They are training-case memorization results; no held-out or novel-object generalization claim is made.

## Exported assets

- Fixed-camera input mesh, generated CAD, canonical CAD, and exact overlay renders for PART_000, PART_001, and PART_005.
- Teaser overview in PNG, SVG, and PDF.
- Token comparison and quantization validity data in CSV/JSON, reproducible plotting scripts, and SVG/PDF/PNG figures.
- Fusion backend comparison in CSV/JSON. Fusion API generation is deterministic; runtime validation remains PENDING_FUSION360_HOST.
- Seven reusable PART_005 demo stills covering input, generation progress, final IR, compilation, CAD, STEP, and GT overlay.
- SHA256 source provenance and export manifest.

## Quantization statement

14-bit is the first tested precision reaching the observed validity plateau (45/54 at both 14 and 16 bits). This is not a global minimum-safe-bit claim.

TEASER_READY=YES
