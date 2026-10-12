# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gelresolution_5_flash_yellowblacksilver_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_002, PART_005
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_002 | 15 | 6888 | 37.164344787597656 | 0.006999833518237454 |
| PART_005 | 15 | 0 | n/a | n/a |
| PART_002 | 25 | 1381 | 56.16277313232422 | 0.006980113046742176 |
| PART_005 | 25 | 0 | n/a | n/a |
| PART_002 | 35 | 413 | 68.65507507324219 | 0.007037491179728907 |
| PART_005 | 35 | 0 | n/a | n/a |
| PART_002 | 45 | 178 | 79.49319458007812 | 0.007031401379131004 |
| PART_005 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
