# Airplane Hybrid Geometry Router V1

Generated from frozen P3/X-Part plus existing Route A CADFit and Route B Point2CAD artifacts.

```text
CURRENT_GATE=AIRPLANE_HYBRID_GEOMETRY_ROUTER_V1
SOURCE_CASE=Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj
P3_REEXECUTED=False
XPART_REEXECUTED=False
PARTS_TOTAL=9
CADFIT_ROUTED_PARTS=6
ROUTEB_ROUTED_PARTS=0
DECOMPOSE_ROUTED_PARTS=3
DECOMPOSED_REGIONS=6
CADFIT_ROUTE_REJECTED_BY_QA=1
FINAL_SELECTED_CADFIT_PARTS=8
FINAL_SELECTED_ROUTEB_PARTS=1
PURE_ROUTE_A_MEAN_IOU=0.6594
HYBRID_MEAN_IOU=0.6693
PART_003_SELECTED_ROUTE=MIXED_STRUCTURE
PART_003_REGION_COUNT=2
PART_003_IOU_BEFORE=0.2826
PART_003_IOU_AFTER=0.3717
ASSEMBLY_STEP_RELOAD_VALID=True
FINAL_ASSEMBLY_STEP=ours3/airplane_hybrid_geometry_router_v1/assembly/airplane_hybrid_router_v1.step
ROUTER_GATE=PASS
NEXT_PRIMARY_BLOCKER=Mixed parts were decomposed for routing, but region-level CADFit/Point2CAD was not re-run; whole-part selected STEP is used in assembly.
```

Router input is X-Part watertight geometry plus deterministic measurements only. Part IDs are used in audit, not in scoring.

## Routing table

| Part | Geometry class | CADFit score | RouteB score | Decompose score | Selected |
| --- | --- | ---: | ---: | ---: | --- |
| PART_000 | ROTATIONAL | 0.398 | 0.113 | 0.008 | CADFIT |
| PART_001 | ROTATIONAL | 0.399 | 0.079 | 0.005 | CADFIT |
| PART_002 | ROTATIONAL | 0.324 | 0.182 | 0.748 | DECOMPOSE |
| PART_003 | ROTATIONAL | 0.301 | 0.182 | 0.749 | DECOMPOSE |
| PART_004 | ROTATIONAL | 0.389 | 0.074 | 0.005 | CADFIT |
| PART_005 | ROTATIONAL | 0.566 | 0.000 | 0.004 | CADFIT |
| PART_006 | ROTATIONAL | 0.476 | 0.004 | 0.010 | CADFIT |
| PART_007 | ROTATIONAL | 0.470 | 0.005 | 0.008 | CADFIT |
| PART_008 | ROTATIONAL | 0.156 | 0.406 | 0.746 | DECOMPOSE |

## Q1 — Why pure CADFit is blocky on some parts?

CADFit `max_iterations=1` recovered extrude+union only (`TOTAL_REVOLVES=0`, `TOTAL_CUTS=0`). That matches parts whose measurements are **not** prismatic solids:

| Part | THICKNESS_RATIO | area/volume | SECTION_AREA_CV | FREEFORM_SCORE | Route A IoU |
| --- | ---: | ---: | ---: | ---: | ---: |
| PART_003 | 0.260 | **106.9** | 0.259 | 0.063 | **0.283** |
| PART_002 | 0.249 | **107.2** | — | — | 0.727 |
| PART_008 | 0.140 | **221.5** | — | — | 0.605 |
| PART_000 | 0.136 | 67.0 | — | — | 0.802 |
| PART_005 | 0.149 | **22.6** | 0.229 | 0.174 | 0.786 |

Thin-shell / high area-volume parts (propellers, dorsal) cannot be expressed as a few extrudes. Fuselage (low AV ratio, stronger volumetric evidence) is the CADFit-friendly case.

## Q2 — Where did the router send the 9 parts?

- **REGULAR_CADFIT (6):** PART_000, 001, 004, 005, 006, 007 — extrusion evidence and lower shell ratio.
- **MIXED_STRUCTURE (3):** PART_002, 003, 008 — high area/volume plus rotational evidence, so decompose-first.
- **THIN_FREEFORM (0) at router time.** Route B still won **selection** on PART_003 after CADFit QA reject.

## Q3 — Did it automatically find mixed-structure parts?

Yes. The trigger is geometric, not a part-id rule:

- `area_volume_ratio > 80` (thin shell)
- `REVOLUTION_SCORE > 0.5`
- then `DECOMPOSE_SCORE` wins over CADFit/Route B

That fired on PART_002 / PART_003 / PART_008 only. Fuselage AV=22.6 did **not** mix.

## Q4 — Did decomposition improve region homogeneity?

For PART_003 radial split about the estimated revolution axis:

- REGION_000 / REGION_001 area ≈ 0.49 / 0.51
- HOMOGENEITY_BEFORE = 0.901
- HOMOGENEITY_AFTER = 0.906

Gain is tiny. Both regions re-routed to CADFit under `MAX_DECOMPOSITION_DEPTH`. Split is evidence of mixed regimes, not yet a better CAD construction.

## Q5 — Hybrid vs pure CADFit?

| Metric | Pure Route A | Hybrid |
| --- | ---: | ---: |
| Mean IoU | 0.6594 | **0.6693** |
| Mean FP occupancy | n/a (Route A did not store it) | 0.90 (voxel, not comparable) |

IoU improved because PART_003 switched to Point2CAD (0.28 → 0.37). Other 8 parts kept CADFit when its IoU was higher. Geometry fidelity is first in `SELECTION_SCORE` (`w_geometry=0.60`).

## Q6 — PART_003?

| Field | Value |
| --- | --- |
| Router | MIXED_STRUCTURE (not hardcoded) |
| Reasons | THIN_SHELL_HIGH_AV_RATIO; ROTATIONAL_CORE; MULTIPLE_GEOMETRY_REGIMES |
| Regions | 2 |
| CADFit IoU | 0.283 (QA rejected, 1 extrude) |
| Selected | Route B Point2CAD |
| Hybrid IoU | **0.372** |

Improved, still not a good propeller CAD. Remaining error is Point2CAD surface/topology (high FP occupancy 0.54), not the router.

## Q7 — Remaining blocker layer?

```text
router         — worked: PART_003 is MIXED, not whole-part CADFit
decomposition  — weak: homogeneity barely improved; regions did not get their own CAD
CADFit         — rejected on PART_003 (correct)
Point2CAD fit  — selected; IoU up but still low
Point2CAD topology — primary leftover quality issue on PART_003
```

**NEXT_PRIMARY_BLOCKER:** Mixed parts were decomposed for routing, but region-level CADFit/Point2CAD was not re-run; assembly uses whole-part selected STEP.

## Artifacts

- Features: `geometry_features/PART_XXX.json`
- Routing: `routing/PART_XXX.json`, `router_summary.csv`
- Decomposition: `decomposition/PART_00{2,3,8}/`
- Selected STEP: `selected_parts/PART_XXX/PART_XXX.step`
- Assembly: `assembly/airplane_hybrid_router_v1.step`
- Compare: `pure_routea_vs_hybrid.csv`
