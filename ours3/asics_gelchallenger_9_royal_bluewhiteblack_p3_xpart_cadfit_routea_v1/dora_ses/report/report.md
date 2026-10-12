# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gelchallenger_9_royal_bluewhiteblack_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002, PART_003, PART_004, PART_005, PART_006
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 1119 | 28.149539947509766 | 0.0069220144315635035 |
| PART_001 | 15 | 4 | 22.545555114746094 | 0.006837113072618664 |
| PART_002 | 15 | 4 | 21.07306480407715 | 0.005173605291186023 |
| PART_003 | 15 | 849 | 30.24476432800293 | 0.00721788462360827 |
| PART_004 | 15 | 0 | n/a | n/a |
| PART_005 | 15 | 7720 | 39.91339874267578 | 0.007050804646843893 |
| PART_006 | 15 | 525 | 29.22043228149414 | 0.0072943805665671895 |
| PART_000 | 25 | 115 | 70.96856689453125 | 0.006997601275291313 |
| PART_001 | 25 | 0 | n/a | n/a |
| PART_002 | 25 | 0 | n/a | n/a |
| PART_003 | 25 | 138 | 42.43741989135742 | 0.007251736828059984 |
| PART_004 | 25 | 0 | n/a | n/a |
| PART_005 | 25 | 1841 | 55.006351470947266 | 0.007129519666366028 |
| PART_006 | 25 | 69 | 42.11616897583008 | 0.00765376301205078 |
| PART_000 | 35 | 27 | 101.26226043701172 | 0.006831342911811991 |
| PART_001 | 35 | 0 | n/a | n/a |
| PART_002 | 35 | 0 | n/a | n/a |
| PART_003 | 35 | 18 | 57.434608459472656 | 0.007175784567227403 |
| PART_004 | 35 | 0 | n/a | n/a |
| PART_005 | 35 | 635 | 70.20122528076172 | 0.007287241398093024 |
| PART_006 | 35 | 11 | 45.3178596496582 | 0.007547693352923862 |
| PART_000 | 45 | 16 | 103.5001220703125 | 0.006752343393109419 |
| PART_001 | 45 | 0 | n/a | n/a |
| PART_002 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 3 | 67.06494903564453 | 0.007230769624193484 |
| PART_004 | 45 | 0 | n/a | n/a |
| PART_005 | 45 | 246 | 88.77604675292969 | 0.0074686765838445175 |
| PART_006 | 45 | 1 | 45.80439758300781 | 0.0049329229840024405 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
