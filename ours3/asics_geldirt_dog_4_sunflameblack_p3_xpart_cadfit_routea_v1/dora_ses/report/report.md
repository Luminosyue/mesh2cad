# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asics_geldirt_dog_4_sunflameblack_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002, PART_003
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 1278 | 36.89496994018555 | 0.014244135754880195 |
| PART_001 | 15 | 9928 | 37.340049743652344 | 0.014325860557557031 |
| PART_002 | 15 | 6 | 16.83536720275879 | 0.009963304821258416 |
| PART_003 | 15 | 171 | 20.375211715698242 | 0.010994088692679312 |
| PART_000 | 25 | 537 | 40.9717903137207 | 0.013950985045796168 |
| PART_001 | 25 | 2814 | 47.00746536254883 | 0.014401526469188968 |
| PART_002 | 25 | 0 | n/a | n/a |
| PART_003 | 25 | 1 | 25.208892822265625 | 0.010196364316524783 |
| PART_000 | 35 | 106 | 45.83781814575195 | 0.011044530875377271 |
| PART_001 | 35 | 690 | 56.91966247558594 | 0.014372611662004226 |
| PART_002 | 35 | 0 | n/a | n/a |
| PART_003 | 35 | 0 | n/a | n/a |
| PART_000 | 45 | 9 | 47.701210021972656 | 0.012476332660071135 |
| PART_001 | 45 | 174 | 62.964263916015625 | 0.014141004814073814 |
| PART_002 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
