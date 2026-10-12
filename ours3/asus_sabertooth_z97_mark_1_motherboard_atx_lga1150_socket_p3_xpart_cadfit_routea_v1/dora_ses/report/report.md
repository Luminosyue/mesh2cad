# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asus_sabertooth_z97_mark_1_motherboard_atx_lga1150_socket_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 2356 | 40.524574279785156 | 0.009905916251539915 |
| PART_000 | 25 | 1106 | 44.56084060668945 | 0.009903222123363519 |
| PART_000 | 35 | 301 | 52.30448532104492 | 0.009920409088984195 |
| PART_000 | 45 | 53 | 56.476524353027344 | 0.010105134783009092 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
