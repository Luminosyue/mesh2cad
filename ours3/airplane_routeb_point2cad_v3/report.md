# Airplane Route B V3 — Dora + Point2CAD Topology Backend

V1 (`routeb_dora_geometry_v1`) and V2 (`airplane_routeb_geometry_v2`) were **not overwritten**.

This round replaces the failed V2 stack:

`custom surface → MASTER_EDGE → DUAL_PCURVE → sewing`

with the official Point2CAD reconstruction backend:

`surface fitting → extension → intersection → clipping → edges/corners → OCC STEP`

---

## Pipeline that actually ran

```text
Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj
→ reused P3 / X-Part (9 watertight parts)
→ reused V2 Dora SES (15/25/35/45°, VAE unused)
→ reused V2 design curves + curve-guided triangle patch_id
→ sampled (x,y,z,s), s = patch_id   [64,365 points, 19 patches]
→ official Point2CAD  (/point2cad + .venv)
     unclipped / clipped / topo
→ OCC import of clipped world mesh → STEP
→ assembly STEP reload
```

- `PARSE_NET_USED=False`, `HPNET_USED=False`
- `s` is **not** GT and **not** manual. It is Route B V2 curve-guided `triangle_labels`.
- Point2CAD official fitting code was used (`process_one_surface` + `save_clipped_meshes` + `save_topology`).

---

## What changed vs V2

| | V2 custom OCC | V3 Point2CAD |
|---|---|---|
| Surface backend | our plane/ruled/bspline hulls | official plane/cylinder/cone/INR |
| Topology | DUAL_PCURVE=0, no MASTER_EDGE | **13 intersection curves** |
| Mean IoU | 0.140 | **0.308** |
| Coverage | 0.900 | **0.971** |
| Fitted surfaces | 19 patches labeled by us | 19 Point2CAD fits: 4 plane, 2 cyl, 4 cone, 9 spline |

Point2CAD did what V2 sewing could not: **pairwise surface intersection produced real curves** (PART_008: 5, PART_002: 3).

---

## Per-part Point2CAD

| Part | Fit types | Topo curves | IoU | Coverage | Note |
|---|---|---:|---:|---:|---|
| PART_000 | plane | 0 | 0.043 | 1.00 | 1 patch → nothing to intersect |
| PART_001 | plane, cylinder | 1 | 0.282 | 1.00 | wing-like; cylinder recovered |
| PART_002 | spline, cone, spline | 3 | 0.352 | 1.00 | strongest small-part topology |
| PART_003 | plane, spline | 1 | 0.372 | 1.00 | |
| PART_004 | cylinder, spline | 1 | 0.347 | 1.00 | |
| PART_005 | plane, spline | 1 | 0.305 | 0.97 | fuselage-like |
| PART_006 | cone, spline | 1 | 0.191 | 0.77 | |
| PART_007 | spline | 0 | 0.632 | 1.00 | 1 patch |
| PART_008 | spline, cone, spline, cone | 5 | 0.252 | 1.00 | most intersection curves |

Single-patch parts (000, 007) cannot emit intersection topology. That is expected.

---

## Solids / STEP — honest reading

`SOLIDS=13` and `CLOSED_SHELLS=13` come from OCC `MakeSolid` on **tessellated clipped-mesh fragments** after STL import. They are **not** clean design solids of a whole airplane part.

- `BREP_VALID_PARTS=1` because `BRepCheck` usually rejects the tessellated STL compound.
- `CAD_NATIVE_PARTS=9`: every part wrote a STEP file and assembly reload succeeded.
- `TOPO_CORNERS=0`: Point2CAD found curve–curve coincidences insufficient for corners.
- `SHELLS=8988` / `FREE_EDGES=88231`: leftover of triangle soups, not compact B-Rep.

The topology win is **`topo/topo.json` intersection curves**, not the OCC analyzer.

---

## Gate

`ROUTE_B_V3_GATE=PASS`

Because: X-Part valid, Dora patches → `(x,y,z,s)`, Point2CAD surface+clipping on **9/9** parts, **13 intersection curves**, **9 CAD STEP**, assembly reload valid.

```text
CURRENT_GATE=AIRPLANE_ROUTE_B_POINT2CAD_TOPOLOGY_V3
SOURCE_CASE=Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj
P3_REEXECUTED=False
XPART_REEXECUTED=False
DORA_SES_REEXECUTED=False
DORA_VAE_USED=False
PARSE_NET_USED=False
HPNET_USED=False
POINT2CAD_USED=True
POINT2CAD_OFFICIAL_MAIN=True
P3_PART_COUNT=9
XPART_WATERTIGHT_PARTS=9
XPART_WATERTIGHT_RATE=1.0
ROUTEB_PARTS_ATTEMPTED=9
RAW_DORA_EDGES=14613
MERGED_DESIGN_CHAINS=112
LINE_CURVES=17
CIRCLE_CURVES=6
ARC_CURVES=64
SURFACE_PATCHES=19
XYZS_POINTS=64365
XYZS_PATCHES=19
POINT2CAD_SURFACE_SUCCESS_PARTS=9
POINT2CAD_TOPOLOGY_SUCCESS_PARTS=9
P2C_FITTED_SURFACES=19
P2C_PLANES=4
P2C_CYLINDERS=2
P2C_SPHERES=0
P2C_CONES=4
P2C_SPLINES=9
TOPO_CURVES=13
TOPO_CORNERS=0
SHELLS=8988
CLOSED_SHELLS=13
SOLIDS=13
TRIMMED_FACES=48766
BREP_VALID_PARTS=1
CAD_NATIVE_PARTS=9
MEAN_IOU=0.3084205184033042
MEAN_CHAMFER=0.026885997131436697
MEAN_HAUSDORFF=0.21714008217102063
MEAN_COVERAGE=0.9712222222222222
MEAN_FP_OCCUPANCY=0.6332429365648399
ASSEMBLY_STEP_RELOAD_VALID=True
ROUTE_B_V3_GATE=PASS
FINAL_ASSEMBLY_STEP=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_routeb_point2cad_v3/assembly/airplane_routeb_v3.step
ARTIFACT_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_routeb_point2cad_v3
NEXT_PRIMARY_BLOCKER=
DUAL_PCURVE_SUCCESS=REPLACED_BY_POINT2CAD_INTERSECTION
MASTER_EDGE=REPLACED_BY_POINT2CAD_TOPOLOGY
```

Artifacts: `ours3/airplane_routeb_point2cad_v3/`  
Contact sheet: `airplane_routeb_v3_contact_sheet.png`
