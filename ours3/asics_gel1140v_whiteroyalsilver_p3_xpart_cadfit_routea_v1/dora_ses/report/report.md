# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gel1140v_whiteroyalsilver_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_006, PART_008, PART_009, PART_010
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 575 | 44.71165084838867 | 0.013644059526523845 |
| PART_006 | 15 | 116 | 30.119140625 | 0.01188760960013922 |
| PART_008 | 15 | 3119 | 51.693702697753906 | 0.014262961782012206 |
| PART_009 | 15 | 0 | n/a | n/a |
| PART_010 | 15 | 411 | 26.591739654541016 | 0.011404826156891083 |
| PART_000 | 25 | 197 | 59.27339172363281 | 0.013964528933508056 |
| PART_006 | 25 | 23 | 32.3704833984375 | 0.010166233906663831 |
| PART_008 | 25 | 1557 | 58.69218444824219 | 0.014190018618273337 |
| PART_009 | 25 | 0 | n/a | n/a |
| PART_010 | 25 | 38 | 32.63951110839844 | 0.01171750207573945 |
| PART_000 | 35 | 83 | 64.44817352294922 | 0.014099421898893365 |
| PART_006 | 35 | 0 | n/a | n/a |
| PART_008 | 35 | 688 | 67.66210174560547 | 0.014117848781632653 |
| PART_009 | 35 | 0 | n/a | n/a |
| PART_010 | 35 | 0 | n/a | n/a |
| PART_000 | 45 | 26 | 74.04216003417969 | 0.014231930759846351 |
| PART_006 | 45 | 0 | n/a | n/a |
| PART_008 | 45 | 265 | 80.28424835205078 | 0.014144678062384796 |
| PART_009 | 45 | 0 | n/a | n/a |
| PART_010 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
