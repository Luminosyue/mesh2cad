# Airplane Route B Geometric CAD V2

Source: `Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj`  
Artifact root: `ours3/airplane_routeb_geometry_v2/`  
Gate: **PARTIAL_PASS**  
Blocker: **NO_SOLID_CLOSURE**

P3/X-Part reused (path + sha256 match). Dora SES 15/25/35/45 run only on these 9 airplane parts. Dora VAE / MAC / VLM / CADFit geometry were not used.

---

## Q1 — Dora fragmentation vs V1?

Yes, compared with Tank Route B V1 (`EDGE_CHAINS=2492` all LINE, PART_042 `EDGE_NOISE_OVERLOAD`).

| | V1 Tank (typical) | V2 Airplane |
|---|---:|---:|
| Raw Dora union edges | tens of thousands on hard parts | 14613 total / 9 parts |
| After hysteresis | (union of 4 thresholds) | 2169 |
| Local chains | 2492 | 172 |
| Merged design chains | (no merge-before-fit) | 112 |

Hysteresis is doing the job: 45°/35° seed (826) absorbs 25° then 15° only as continuation. 15° edges (e.g. PART_000 raw 1719) do not become standalone CAD components (hysteresis 8).

No part hit `EDGE_NOISE_OVERLOAD`.

Caveat: mean `SHORT_CHAIN_RATIO` across parts did **not** drop (0.552 → 0.582) because several parts already had 1–3 long chains. On the actually fragmented parts it did drop:

- PART_005: 0.618 → 0.318
- PART_008: 0.290 → 0.163
- PART_007: 0.333 → 0.000

---

## Q2 — Still thousands of short LINE curves?

**No.** `ALL_LINE_COLLAPSE=False`.

- LINE=17, ARC=64, CIRCLE=6, BSPLINE=8, ELLIPSE=0
- Total parametric curves = 95, not 2492
- `ANALYTIC_CURVE_RATE=0.737`

Short chains are merged or marked noise; they are not auto-classified LINE from tiny residual.

---

## Q3 — Circle / Arc / Ellipse recovered?

**Yes for Circle and Arc. No Ellipse.**

| Part | LINE | CIRCLE | ARC | BSPLINE |
|---|---:|---:|---:|---:|
| PART_000 | 0 | 0 | 1 | 0 |
| PART_001 | 0 | 0 | 0 | 1 |
| PART_002 | 0 | 0 | 11 | 0 |
| PART_003 | 2 | 2 | 12 | 0 |
| PART_004 | 0 | 0 | 2 | 1 |
| PART_005 | 4 | 3 | 5 | 4 |
| PART_006 | 1 | 0 | 3 | 0 |
| PART_007 | 0 | 0 | 2 | 0 |
| PART_008 | 10 | 1 | 28 | 2 |

PART_008 (circular-boundary-rich) and PART_005 (fuselage-like) are the strongest curve recoveries. `COAXIAL_CIRCLE_GROUPS=0`, so there is not yet revolution-axis evidence.

---

## Q4 — Surfaces still mostly BSpline?

**No longer.** After analytic-first + plate split:

- PLANES=13
- RULED=2
- SPHERES=1 (tiny PART_008 patch, radius ~1.06, likely a false positive)
- CYLINDER=0, CONE=0, REVOLUTION=0
- BSPLINE_SURFACES=3 / 19 patches
- `ANALYTIC_SURFACE_RATE=0.842`

Wings/tails become planes or ruled slabs. Cylinder/revolution still missing because coaxial circle groups were not formed, and remaining patches are plate-like rather than cylindrical.

---

## Q5 — SOLIDS > 0?

**No. SOLIDS=0, SHELLS=0, CLOSED_SHELLS=0.**

All 9 parts wrote CAD-native STEP (`BREP_VALID_PARTS=9`, assembly reload valid), but each part is an **open compound of trimmed planar/ruled faces**, not a closed shell.

Real closure blocker:

1. Faces are convex-hull trims of surface patches, **not** wires built from shared design curves.
2. Adjacent patches do not share `MASTER_EDGE`s, so sewing at `0.004 * bbox_diag` leaves `FREE_EDGE_COUNT ≈ EDGE_COUNT`.
3. Spec forbids inflating sewing tolerance until Solid. Gaps are recorded as `TOPOLOGY_GAP`.

`NEXT_PRIMARY_BLOCKER=NO_SOLID_CLOSURE`  
Next work is curve-constrained wires + surface–surface intersection for missing shared edges, not another threshold union.

---

## Q6 — Which parts suit Route B? Overload?

No `EDGE_NOISE_OVERLOAD`.

**Best Route B parts**

- PART_008: 93→49 chains, 1 circle + 28 arcs, 3 planes
- PART_005: 34→22 chains, 3 circles + 5 arcs, 2 ruled
- PART_002 / PART_003: compact arc/circle sets on small watertight parts

**Weak Route B parts**

- PART_000 / PART_007: almost no strong Dora seed (3 seed edges), 1–2 chains, one plane, IoU very low
- PART_001: 1 merged chain, curve gate PARTIAL, 1 plane + 1 BSpline

---

## Q7 — Route A vs Route B?

`AIRPLANE_ROUTE_A_AVAILABLE=False` (CADFit incomplete). Real A IoUs only for PART_000/001/002; other A cells are not fabricated.

| Part | Route A IoU | Route B IoU |
|---|---:|---:|
| PART_000 | 0.8019 | 0.0360 |
| PART_001 | 0.5329 | 0.2137 |
| PART_002 | 0.5599 | 0.1853 |

Where Route A finished, **A wins geometry fidelity**. Route B wins **design-curve compactness** (arcs/circles, 95 curves vs V1's 2492 lines) but current B-Rep is open planar hulls, so IoU/FP occupancy are not competitive.

---

## Geometry vs CAD quality

| Axis | Result |
|---|---|
| Geometry fidelity | Mean IoU 0.140, Chamfer 0.015, Coverage 0.900, FP 0.725 |
| Design curve compactness | 14613 Dora edges → 112 merged chains → 95 curves |
| Analytic surface rate | 0.842 |
| Topology closure | 0 solids; free edges on every face |
| CAD validity | 9/9 STEP reload valid; assembly STEP reload valid |

---

## Required gate block

```text
CURRENT_GATE=AIRPLANE_ROUTE_B_GEOMETRIC_CAD_V2
SOURCE_CASE=Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj
P3_REEXECUTED=False
XPART_REEXECUTED=False
DORA_SES_REEXECUTED=True
DORA_VAE_USED=False
P3_PART_COUNT=9
XPART_WATERTIGHT_PARTS=9
XPART_WATERTIGHT_RATE=1.0
ROUTEB_PARTS_ATTEMPTED=9
RAW_DORA_EDGES=14613
STRONG_SEED_EDGES=826
HYSTERESIS_EDGES=2169
LOCAL_EDGE_CHAINS=172
MERGED_DESIGN_CHAINS=112
SHORT_CHAIN_RATIO_BEFORE=0.5518659076533838
SHORT_CHAIN_RATIO_AFTER=0.5822522948573368
LINE_CURVES=17
CIRCLE_CURVES=6
ARC_CURVES=64
ELLIPSE_CURVES=0
BSPLINE_CURVES=8
COAXIAL_CIRCLE_GROUPS=0
REVOLUTION_EVIDENCE_PARTS=0
CURVE_COMPRESSION_RATIO=130.47321428571428
SURFACE_PATCHES=19
PLANES=13
CYLINDERS=0
CONES=0
SPHERES=1
TORI=0
REVOLUTION_SURFACES=0
RULED_SURFACES=2
BSPLINE_SURFACES=3
ANALYTIC_SURFACE_RATE=0.8421052631578947
SHARED_OCC_EDGES=1085
DUAL_PCURVE_SUCCESS=0
CLOSED_WIRES=18
TRIMMED_FACES=18
SHELLS=0
CLOSED_SHELLS=0
SOLIDS=0
BREP_VALID_PARTS=9
STEP_RELOAD_VALID_PARTS=9
CAD_NATIVE_PARTS=9
MEAN_IOU=0.14012531712260556
MEAN_CHAMFER=0.014582787413646464
MEAN_HAUSDORFF=0.037876356145219246
MEAN_COVERAGE=0.899688888888889
MEAN_FP_OCCUPANCY=0.7245964556697023
ASSEMBLY_STEP_RELOAD_VALID=True
ALL_LINE_COLLAPSE=False
ROUTE_B_V2_GATE=PARTIAL_PASS
FINAL_ASSEMBLY_STEP=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_routeb_geometry_v2/assembly/airplane_routeb_v2.step
ARTIFACT_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_routeb_geometry_v2
NEXT_PRIMARY_BLOCKER=NO_SOLID_CLOSURE
```
