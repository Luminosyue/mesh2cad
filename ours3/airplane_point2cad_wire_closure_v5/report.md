# Airplane Point2CAD Wire Closure V5

Frozen: P3 / X-Part / Dora / V3 Point2CAD surface fits + official intersections.
Not overwritten: `ours3/airplane_routeb_point2cad_v3/`, `ours3/airplane_point2cad_brep_closure_v4/`.

This round only reorganized intersection topology and re-intersected **already fitted** surfaces. No surface refit.

## Gate

```text
CURRENT_GATE=AIRPLANE_POINT2CAD_WIRE_CLOSURE_V5
P3_REEXECUTED=False
XPART_REEXECUTED=False
DORA_SES_REEXECUTED=False
DORA_VAE_USED=False
POINT2CAD_SURFACE_FIT_REEXECUTED=False
PARTS_ATTEMPTED=2
SURFACE_PAIR_MAPPING_RATE=1.0
OFFICIAL_CURVES=8
RAW_INTERSECTION_COMPONENTS=39
STITCHED_MASTER_CURVES=29
CORNER_CANDIDATES=40
MERGED_TOPO_CORNERS=10
TRIMMED_MASTER_EDGES=61
CLOSED_WIRES=4
OPEN_WIRES=68
SURFACES_WITH_CLOSED_WIRE=4 / SURFACES_TOTAL=7
MISSING_INTERSECTIONS_ATTEMPTED=1
MISSING_INTERSECTIONS_ACCEPTED=0
VALID_TRIMMED_FACES=4
CLOSED_SHELLS=0
CLEAN_PARAMETRIC_PART_SOLIDS=0
STEP_RELOAD_VALID_PARTS=2
PART_008_RAW_COMPONENTS=16
PART_008_STITCHED_CURVES=11
PART_008_SURFACES_WITH_CLOSED_WIRE=2 / 4
PART_008_CLOSED_SHELL=False
PART_008_CLEAN_SOLID=False
PART_002_RAW_COMPONENTS=23
PART_002_STITCHED_CURVES=18
PART_002_CLOSED_WIRES=2
PART_005_PATCH_UNDERSEGMENTATION=True
ROUTE_B_V5_GATE=PARTIAL_PASS
NEXT_PRIMARY_BLOCKER=WIRE_OPEN
ARTIFACT_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_point2cad_wire_closure_v5
```

Stitching works and closed wires exist, but no closed shell / clean solid. That is PARTIAL_PASS, not FAIL (surface-pair provenance is 1.0; stitching is stable).

---

## Q1 — Did intra-curve stitching fix official-curve fragmentation?

**Partially, and only at the largest allowed official gap (3e-3).**

The fragments of one Point2CAD curve are usually **separate intersection branches**, not 1e-4 cracks. Normalized endpoint gaps on PART_008 C0 are typically 3e-3 … 4e-2. The spec scan stops at 3e-3, so most branches stay separate masters of the **same** `(surface_a, surface_b)`.

| Official curve | raw components | stitched masters | joins at 3e-3 |
|---|---|---|---|
| P2C_CURVE_000 | 5 | 3 | 1 (gap 1.68e-3, tangent dot 1.000) |
| P2C_CURVE_001 | 4 | 3 | 0 (one component already closed; others > 6e-2 apart) |
| P2C_CURVE_002 | 4 | 2 | 0 (tiny tessellation noise dropped; remaining gaps ~1e-2) |
| P2C_CURVE_003 | 2 | 2 | 0 (gap ~0.25 diag) |
| P2C_CURVE_004 | 1 | 1 | n/a |

Forcing 5→1 by jumping 1–2 cm would invent geometry. V5 therefore keeps multiple `STITCHED_MASTER_CURVE`s per official `curve_id` when they fail gap+tangent.

---

## Q2 — PART_008: can all 4 surfaces get a closed wire?

**No. Still 2 / 4**, same as V4 for the closed-wire count, but with authoritative pairs and real stitching QA.

Fitted surfaces: 0 spline, 1 cone, 2 spline, 3 cone.

Official combinations recovered 5/6 pairs:

```text
(0,1) (0,2) (0,3) (1,2) (2,3)
missing: (1,3)  cone ∩ cone
```

Closed wires sit on surfaces **0 and 2** (the two splines that already have a long closed C1 loop). Surfaces **1 and 3** (cones) stay open: almost all boundary vertices have degree 1.

OCC `GeomAPI_IntSS` on cones 1 and 3 **did** produce a 0.75-long analytic curve, then it was **rejected**:

```text
mean_dist_xpart = 1.89
support_frac = 0.0
endpoint_compatible = False
```

That infinite-cone intersection does not lie on the X-Part. Accepting it would be a fake edge. So the missing pair is real in the combination table, but not a valid patch-local intersection of the current fits.

---

## Q3 — Why PART_002 still cannot form a solid cycle set?

V5 **did** recover `PART_002_CLOSED_WIRES=2` (V4 after fake-cycle filter was 0). Those two are closed tessellation loops, not a 3-face outer shell.

Endpoint graph after stitch:

```text
degree1 = 59
degree2 = 5
degree3plus = 5
```

A simple closed wire needs mostly degree-2 vertices. Here the graph is a pile of **open paths**.

Cause ranking:

1. **Fragmentation** — 23 components → 18 masters. Official 3e-3 stitching barely joins (C2: 8→5 mostly by dropping noise).
2. **Wrong / incomplete corner incidence** — 7 merged corners exist, but they do not turn the degree-1 sea into cycles. Many fragment endpoints never snap to a shared-surface corner.
3. **Not missing a surface pair** — all 3 official combinations mapped (`SURFACE_PAIR_MAPPING_RATE=1.0`). There is no empty `(i,j)` to complete.
4. Surface pair mapping is **not** the failure; the 3 curves are the correct pairs.

First concrete open wire:

```text
PART_002 surface 0  WIRE_001  kind=open
v_start = E_P2C_CURVE_000_M00_START  xyz ≈ (-0.319, -0.865, 0.104)
v_end   = E_P2C_CURVE_000_M00_END    xyz ≈ (-0.226, -0.877, 0.095)
incident edges = MASTER_EDGE_000 (+ splits)
candidate pair already exists: (0,1)
```

That gap is an **unstitched / untrimmed branch of an existing intersection**, not a missing pair.

---

## Q4 — First closed shell / clean parametric solid without refitting?

**No.**

```text
CLOSED_SHELLS=0
CLEAN_PARAMETRIC_PART_SOLIDS=0
VALID_TRIMMED_FACES=4   (2 per canary, from closed-loop wires)
STEP reload valid: both parts
```

OCC Face / Shell / Solid path did run (`BRepCheck`, STEP write). Sewing never saw a manifold closed shell: faces that exist already share logical master edges, but two faces cannot make a part solid (V4 2-face lens is rejected: `n_faces >= 4` required).

---

## Q5 — Has the blocker moved from fragmentation to undersegmentation?

**Both, stacked.**

| Part | Topology-backend limit | Need to go upstream? |
|---|---|---|
| PART_008 | Intra-curve branches cannot be stitched at 3e-3; cone–cone analytic intersection misses the part | **Yes for surfaces 1 and 3**: missing patch-local `(1,3)` means the two cones were never given a common clipped boundary. That is patch/fit support, not a corner bug. |
| PART_002 | Fragmentation + open endpoint graph; all surface pairs already present | Still intersection tessellation / corner incidence, **not** a missing pair |
| PART_005 | 1 open curve, 2 surfaces | `PATCH_UNDERSEGMENTATION` — topology backend must not invent caps |

So: V4’s `dists == 0` is fixed; V5’s remaining PART_008 hole is **no valid extra intersection on current fits**. Further closed-shell work on 008/005 requires **curve-guided resegmentation / refit**, which this gate froze.

---

## First FREE / open-wire blocker (concrete)

### PART_008

```text
blocker = WIRE_OPEN
surface = 0
wire    = WIRE_001
v_start = E_P2C_CURVE_000_M00_START   (-0.0605, -0.4458, 0.1568)
v_end   = E_P2C_CURVE_000_M00_END     (-0.0064, -0.6690, 0.1167)
already-has pair (0,1)
```

Surface degree-1 counts: S0=14, S1=10, S2=10, S3=6. Missing pair `(1,3)` was attempted and **rejected** (does not meet X-Part).

### PART_002

```text
blocker = WIRE_OPEN
surface = 0
wire    = WIRE_001
v_start = E_P2C_CURVE_000_M00_START   (-0.3190, -0.8649, 0.1044)
v_end   = E_P2C_CURVE_000_M00_END     (-0.2258, -0.8769, 0.0947)
already-has pair (0,1)
```

No missing-pair completion was even a candidate (all 3 combinations already have curves).

---

## What V5 did implement

- Authoritative `(surface_a, surface_b)` from Point2CAD `itertools.combinations` order (not global KDTree).
- Intra-curve stitch only: same `curve_id` + same pair + gap scan `{1e-4,3e-4,1e-3,3e-3}` + tangent + degree≤1 matching.
- Corners on **stitched masters**, shared-surface only; `MASTER_EDGE` built once.
- Missing-pair OCC intersection with X-Part validation (reject fake cone–cone).
- OCC Face / Sewing / MakeSolid / `BRepCheck` / STEP. No convex-hull caps. No PART_005 synthetic edges.

Run:

```bash
python3 scripts/run_airplane_routeb_v5.py
python3 scripts/run_airplane_routeb_v5.py --parts PART_008 PART_002
```
