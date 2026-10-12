# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gellinksmaster_whitecoffeesand_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_001, PART_002, PART_003
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_001 | 15 | 3 | 17.08414649963379 | 0.009775807744895337 |
| PART_002 | 15 | 16068 | 42.942710876464844 | 0.01429960502409251 |
| PART_003 | 15 | 750 | 81.67398071289062 | 0.014398517439604266 |
| PART_001 | 25 | 0 | n/a | n/a |
| PART_002 | 25 | 5453 | 56.93809509277344 | 0.014265700297594412 |
| PART_003 | 25 | 446 | 90.65631103515625 | 0.014099770922913165 |
| PART_001 | 35 | 0 | n/a | n/a |
| PART_002 | 35 | 1780 | 72.68301391601562 | 0.014496213659044781 |
| PART_003 | 35 | 312 | 92.75173950195312 | 0.013959714009098373 |
| PART_001 | 45 | 0 | n/a | n/a |
| PART_002 | 45 | 676 | 82.91973114013672 | 0.014613396442700403 |
| PART_003 | 45 | 237 | 93.48951721191406 | 0.012194480701351804 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
