# P3 X-Part 20-case data preparation

## Tank replacement

`case_014` now uses `tank/part_029` and replaces the previous `asus_m5a78lmusb3_motherboard_micro_atx_socket_am3` sample. Tank `PART_029` passed the independent CadQuery rebuild and STEP checks. The supplied Tank source OBJ is retained for conditioning; its surface is marked non-watertight by the mesh audit, while the target CAD rebuild is a valid single solid.

{
  "REQUESTED_CASE_N": 20,
  "RAW_CAD_VALID_N": 20,
  "14BIT_VALID_N": 20,
  "COMPACT_IR_VALID_N": 20,
  "TRAINABLE_CASE_N": 20,
  "failure_categories": {
    "": 20
  }
}

## Per-case token audit

| CASE | Raw | Compact | Reduction | Full sequence |
|---|---:|---:|---:|---:|
| case_000 | 37069 | 29661 | 19.98% | 29684 |
| case_001 | 37122 | 30464 | 17.93% | 30494 |
| case_002 | 37073 | 30952 | 16.51% | 30978 |
| case_003 | 37119 | 30187 | 18.68% | 30210 |
| case_004 | 10293 | 6971 | 32.27% | 7005 |
| case_005 | 19455 | 15434 | 20.67% | 15470 |
| case_006 | 3017 | 1251 | 58.53% | 1276 |
| case_007 | 37126 | 30535 | 17.75% | 30564 |
| case_008 | 8897 | 6220 | 30.09% | 6245 |
| case_009 | 2050 | 896 | 56.29% | 920 |
| case_010 | 12700 | 9270 | 27.01% | 9292 |
| case_011 | 8949 | 6236 | 30.32% | 6264 |
| case_012 | 19495 | 15412 | 20.94% | 15445 |
| case_013 | 37078 | 30953 | 16.52% | 30992 |
| case_014 | 15198 | 11278 | 25.79% | 11300 |
| case_015 | 37175 | 30812 | 17.12% | 30841 |
| case_016 | 4146 | 2513 | 39.39% | 2541 |
| case_017 | 4835 | 3046 | 37.00% | 3081 |
| case_018 | 1190 | 299 | 74.87% | 325 |
| case_019 | 2920 | 1233 | 57.77% | 1256 |
