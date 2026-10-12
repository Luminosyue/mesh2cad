# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/3d_dollhouse_happy_brother_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 1590 | 42.090824127197266 | 0.014314670913282219 |
| PART_001 | 15 | 2858 | 41.9913215637207 | 0.01410935544295433 |
| PART_002 | 15 | 2505 | 39.690345764160156 | 0.014003445179630952 |
| PART_000 | 25 | 501 | 57.30210494995117 | 0.013986072942602549 |
| PART_001 | 25 | 750 | 55.250667572021484 | 0.013988905267972727 |
| PART_002 | 25 | 540 | 48.71416091918945 | 0.013007346721210906 |
| PART_000 | 35 | 156 | 74.64611053466797 | 0.013309366403602193 |
| PART_001 | 35 | 265 | 67.47457122802734 | 0.014180194178512174 |
| PART_002 | 35 | 205 | 58.78828811645508 | 0.01179023022992324 |
| PART_000 | 45 | 62 | 81.66031646728516 | 0.011581989196118862 |
| PART_001 | 45 | 110 | 73.87305450439453 | 0.014229201306845329 |
| PART_002 | 45 | 65 | 66.68193054199219 | 0.011807329080446894 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
