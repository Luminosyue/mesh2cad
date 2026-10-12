# FULL20 Blocked Repair Status

Updated 2026-09-25.

## Repaired

- `pressure_cooker`: `PART_003`, `PART_006`, and `PART_012` passed isolated targeted repair. The completion assembly gate passed for all 13/13 model parts, including STEP readback and render. This is a pipeline pass; measured geometry remains CD `0.019580`, surface IoU64 `0.380857`, and volume error `43.50%`.

## In Progress

- `tank`: existing full-object training continues. Its repair launcher is waiting for the base checkpoint; no frozen `PART_029` re-training was started.

## Bounded Repair Attempted

- `airplane`: `PART_000`, `PART_002`, `PART_003`, and `PART_008` have original CAD and q14 metadata, but the isolated OCCT healing / loft fallback attempts did not produce valid BReps. Original artifacts were not modified. The object remains blocked.

## Input-Blocked

- `dvd_player/PART_001` has no original X-Part input.
- `toaster/PART_020` and `PART_035` are not present in the frozen model training provenance.
- Other missing-X-Part entries remain unchanged and are not substituted.

Canonical labels were not counted as model-generated output. q14 and Compact IR V3 were unchanged.
