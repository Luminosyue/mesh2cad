# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/canister_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 7054 | 23.331087112426758 | 0.005155514052797174 |
| PART_001 | 15 | 5297 | 27.14950180053711 | 0.00515524528542218 |
| PART_002 | 15 | 17213 | 27.92831039428711 | 0.005381221906994436 |
| PART_000 | 25 | 151 | 30.399314880371094 | 0.00502185381728435 |
| PART_001 | 25 | 638 | 31.189373016357422 | 0.005265999758519522 |
| PART_002 | 25 | 1589 | 48.897682189941406 | 0.005256847119485686 |
| PART_000 | 35 | 0 | n/a | n/a |
| PART_001 | 35 | 1 | 35.163177490234375 | 0.002112894163795245 |
| PART_002 | 35 | 353 | 63.253597259521484 | 0.005388227651413932 |
| PART_000 | 45 | 0 | n/a | n/a |
| PART_001 | 45 | 0 | n/a | n/a |
| PART_002 | 45 | 128 | 67.32750701904297 | 0.005310335814339045 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit does not read these files.
