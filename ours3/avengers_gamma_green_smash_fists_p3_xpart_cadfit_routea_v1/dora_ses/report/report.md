# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/avengers_gamma_green_smash_fists_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 4278 | 47.05398941040039 | 0.014180167763243847 |
| PART_001 | 15 | 4501 | 49.18204116821289 | 0.014350301634321133 |
| PART_000 | 25 | 1431 | 56.683433532714844 | 0.014186478580103428 |
| PART_001 | 25 | 1691 | 63.251426696777344 | 0.014311793799095925 |
| PART_000 | 35 | 565 | 63.61826705932617 | 0.014062672053716302 |
| PART_001 | 35 | 673 | 71.4946060180664 | 0.014335484918145234 |
| PART_000 | 45 | 255 | 70.216552734375 | 0.014055683972889416 |
| PART_001 | 45 | 286 | 76.40835571289062 | 0.014092620816048708 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
