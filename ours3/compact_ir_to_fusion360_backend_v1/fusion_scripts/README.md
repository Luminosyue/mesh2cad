# Portable Fusion 360 package

Run each script inside a Fusion 360 Script or Add-In host with an active design:

- `airplane__PART_000.py`
- `airplane__PART_001.py`
- `airplane__PART_005.py`

The Linux server performs deterministic source generation and static validation only. Fusion API execution requires a Windows/macOS Fusion 360 host (`FUSION_RUNTIME_GATE=PENDING_HOST`). Each script reads embedded 14-bit q values, dequantizes with the frozen metadata ranges, creates offset sketches and fitted splines, adds loft profiles in exact source order, then applies the located/scale/translate transform.
