# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/aroma_stainless_steel_milk_frother_2_cup_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002, PART_003
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 260 | 23.749897003173828 | 0.006700559421705612 |
| PART_001 | 15 | 7511 | 28.560665130615234 | 0.007012161946619336 |
| PART_002 | 15 | 3872 | 30.705612182617188 | 0.0069903479096816165 |
| PART_003 | 15 | 11622 | 52.90765380859375 | 0.007232085352237596 |
| PART_000 | 25 | 7 | 27.559473037719727 | 0.00621522990147911 |
| PART_001 | 25 | 780 | 40.568206787109375 | 0.007002628743365907 |
| PART_002 | 25 | 686 | 35.57773208618164 | 0.006732072468375602 |
| PART_003 | 25 | 3666 | 71.86006164550781 | 0.007270238180709848 |
| PART_000 | 35 | 0 | n/a | n/a |
| PART_001 | 35 | 117 | 50.76346206665039 | 0.0069792316696888155 |
| PART_002 | 35 | 45 | 38.59671401977539 | 0.005982395827071234 |
| PART_003 | 35 | 1724 | 83.34800720214844 | 0.007307137772898684 |
| PART_000 | 45 | 0 | n/a | n/a |
| PART_001 | 45 | 18 | 52.759666442871094 | 0.00499525194433921 |
| PART_002 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 964 | 92.49610137939453 | 0.007307137772898684 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
