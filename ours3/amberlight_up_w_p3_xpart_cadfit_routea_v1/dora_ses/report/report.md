# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/amberlight_up_w_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_006, PART_007, PART_008, PART_009
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_006 | 15 | 2096 | 37.83620071411133 | 0.014195863504573619 |
| PART_007 | 15 | 2018 | 97.22557830810547 | 0.014270550939957808 |
| PART_008 | 15 | 1136 | 45.204078674316406 | 0.01458506548780671 |
| PART_009 | 15 | 92 | 20.77509117126465 | 0.010452933827518423 |
| PART_006 | 25 | 495 | 71.69751739501953 | 0.01434107448422882 |
| PART_007 | 25 | 1214 | 108.61534118652344 | 0.014112498813113477 |
| PART_008 | 25 | 494 | 50.288795471191406 | 0.014546134458680051 |
| PART_009 | 25 | 0 | n/a | n/a |
| PART_006 | 35 | 136 | 86.5555419921875 | 0.012860632683712172 |
| PART_007 | 35 | 748 | 115.16899871826172 | 0.014044582099283678 |
| PART_008 | 35 | 183 | 54.66365432739258 | 0.014596469007731025 |
| PART_009 | 35 | 0 | n/a | n/a |
| PART_006 | 45 | 66 | 93.1993408203125 | 0.012191866034830993 |
| PART_007 | 45 | 512 | 121.16046142578125 | 0.013981724461473796 |
| PART_008 | 45 | 58 | 59.168094635009766 | 0.013837733253969947 |
| PART_009 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
