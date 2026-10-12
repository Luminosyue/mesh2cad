# joint_deepcad_fusion360_v1

- seed = **0**
- ratios = train/val/test = **0.8/0.1/0.1**
- total = **2796**

| split | n | deepcad | fusion360 | freeform-STEP | edge_valid | edge_invalid |
|---|---:|---:|---:|---:|---:|---:|
| train | 2236 | 1756 | 480 | 28 | 2235 | 1 |
| val | 280 | 219 | 61 | 4 | 280 | 0 |
| test | 280 | 219 | 61 | 4 | 280 | 0 |

Part-level: no `part_id` appears in more than one split.
Surface-only J0 should use all `surface_valid` rows (includes edge_invalid).

