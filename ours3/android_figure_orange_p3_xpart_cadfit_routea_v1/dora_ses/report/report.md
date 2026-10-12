# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/android_figure_orange_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002, PART_003, PART_004
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 317 | 30.247844696044922 | 0.007326517502382223 |
| PART_001 | 15 | 848 | 24.11450958251953 | 0.006984401926018053 |
| PART_002 | 15 | 120 | 25.702983856201172 | 0.005622541014201995 |
| PART_003 | 15 | 90 | 32.30828857421875 | 0.005835408302592879 |
| PART_004 | 15 | 6 | 18.263729095458984 | 0.007496709356006485 |
| PART_000 | 25 | 51 | 35.77492141723633 | 0.007208258789650618 |
| PART_001 | 25 | 21 | 33.841617584228516 | 0.006287269932888181 |
| PART_002 | 25 | 8 | 32.756534576416016 | 0.0054682235127134155 |
| PART_003 | 25 | 20 | 39.18433380126953 | 0.0054044191268604975 |
| PART_004 | 25 | 0 | n/a | n/a |
| PART_000 | 35 | 4 | 38.854923248291016 | 0.0049889318196419934 |
| PART_001 | 35 | 1 | 37.19538497924805 | 2.2549944567672384e-06 |
| PART_002 | 35 | 0 | n/a | n/a |
| PART_003 | 35 | 3 | 40.99131774902344 | 0.004985951694960604 |
| PART_004 | 35 | 0 | n/a | n/a |
| PART_000 | 45 | 0 | n/a | n/a |
| PART_001 | 45 | 0 | n/a | n/a |
| PART_002 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 0 | n/a | n/a |
| PART_004 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
