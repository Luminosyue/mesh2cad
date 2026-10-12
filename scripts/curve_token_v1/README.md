# Track B / Method 2 — Parametric Curve Token (data foundation)

Isolated experimental branch. **Track A is a frozen baseline.**

```text
Track A (frozen)                    Track B (this package)
point-level edge representation     curve-level representation

Mesh                                CAD / B-Rep
 ├─ surface sampling                     ↓
 │   → surface point cloud          Exact B-Rep Edge
 │   → Sonata → surface tokens           ↓
 └─ sharp edge sampling             Exact Parametric Curve
     → edge point cloud                  ↓
     → edge tokens                  Canonical Representation
                                         ↓
                                    Curve Sampling + Topology
                                         ↓
                                    Curve Dataset  (this round stops here)
                                         ↓
                                    Curve Encoder → <CURVE> tokens  (future)
```

## Isolation contract

| rule | enforcement |
|---|---|
| Track A is read-only | `track_a_guard.py` sha256-hashes every Track A file before and after each run |
| Track B writes to exactly one root | `assert_write_scope_disjoint()` refuses to run if `OUTPUT_ROOT` overlaps a Track A path |
| No Track A module is imported | Track B carries its own `occ_curve_v1.py` and its own normalization implementation |
| Track A is never re-executed | this package runs no training, no inference, no Sonata, no preprocessing |

Nothing here modifies `brep_edges.json`, `brep_edges.npz`, `edge_score`, Sonata's
`Embedding.stem`, surface/edge sampling, tokenizers, configs, checkpoints or any
existing tensor shape. The single Track A artifact reused is
`coordinate_transform.json`, opened read-only.

A Track A training job may be running concurrently and appending to its own
`.log` files. The guard hashes those too, but attributes a change to the external
process only when it can prove the pre-run bytes are still an exact prefix of the
file (a pure append). Anything else is a hard failure:
`CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION`.

## Data source

Ground truth comes from the CAD kernel, never from re-fitting sampled points:

```text
model.step → STEPControl_Reader → TopoDS_Edge → BRepAdaptor_Curve
           → Geom_Line / gp_Circ / gp_Elips / Geom_BSplineCurve
           → exact parameters
```

Backend is **OCP** (`cadquery-ocp` 7.8.1.1); pythonocc is not installed.

`fit_curves_from_points.py` runs the opposite direction (observed points →
predicted curve) purely as a benchmark. It never contributes to the dataset.

## Layout

```text
scripts/curve_token_v1/
├── config.py                   paths, curve-type ids, tolerances
├── track_a_guard.py            sha256 contamination guard
├── audit_existing_data.py      read-only audit of Track A curve fields
├── occ_curve_v1.py             Track-B private OCC helpers
├── curve_eval.py               OCC-free evaluator (de Boor, analytic)
├── extract_brep_curves.py      exact parameter extraction + self-verification
├── canonicalize_curves.py      world + normalized parameters
├── sample_curves.py            arc-length uniform xyz/tangent sampling
├── extract_topology.py         edge↔vertex, edge↔face, adjacency
├── build_dataset.py            per-CAD driver
├── validate_curve_dataset.py   geometry-level validation
├── curve_statistics.py         dataset-wide statistics
├── fit_curves_from_points.py   fitting baseline (benchmark only)
└── visual_qa.py                3-layer overlay renders

scripts/run_curve_token_data_v1.py   main entry
ours3/curve_token_data_v1/           all output
```

## Output

```text
ours3/curve_token_data_v1/
├── audit_existing_data.md
├── <split>/<cad_id>/
│   ├── curves.json              exact parameters, world + normalized
│   ├── curve_samples.npz        [N_curve, 32, 3] xyz / tangent / mask
│   ├── curve_samples_64.npz     same at 64 samples
│   ├── topology.json            edge↔vertex, edge↔face, adjacency
│   ├── normalization.json       transform actually applied
│   └── metadata.json            provenance + ablation support flags
├── statistics/    validation/    artifacts/visual_qa/
├── curve_fitting_baseline/       track_a_guard/    runs/
```

Splits are `deepcad_train` and `fusion360_train`, restricted to cad_ids that have
both a `model.step` and a Track A pack, so Track B is a valid ablation arm against
A0/A1 rather than a differently-scoped dataset.

`N_curve` is each object's real curve count. There is **no** padding to a
dataset-wide `MAX_CURVES`; batch padding belongs in a future dataloader.

## Curve type ids

Stable — never renumber, downstream embeddings index by these.

```text
LINE 0   CIRCLE 1   ELLIPSE 2   BSPLINE 3   BEZIER 4
HYPERBOLA 5   PARABOLA 6   OFFSET 7   OTHER 8
```

`LINE / CIRCLE / ELLIPSE / BSPLINE` get full analytic parameter blocks. `BEZIER`
is stored as an equivalent clamped B-spline plus its native poles. Remaining types
keep their true OCC type and are counted in the statistics — never silently dropped.

## Verification

Every curve is checked at extraction time and again in validation, by rebuilding
it from the stored parameters and comparing against OCC's evaluation of the
original edge:

- `curve_eval.py` reconstructs without OCC (proves JSON self-sufficiency)
- `rebuild_occ_curve()` reconstructs through the kernel (proves round-trip)
- per-type parameter errors (center, radius, normal, axes, poles, knots)
- endpoint error, tangent angular error, Chamfer distance
- npz samples re-evaluated at their stored parameters
- normalized arrays checked against the stored transform

Periodic B-splines have no numpy path (OCC's knot-wrapping convention), so they
are verified through the kernel rebuild; `recon_backend` records which was used.

## Running

```bash
python3 scripts/run_curve_token_data_v1.py --stage canary10   --workers 48
python3 scripts/run_curve_token_data_v1.py --stage canary100  --workers 64
python3 scripts/run_curve_token_data_v1.py --stage full       --workers 96
```

Canary stages are biased towards curve-type coverage: a uniform sample of DeepCAD
is almost entirely `LINE` and would never exercise the ELLIPSE / BSPLINE paths.

## Gates

```text
CURVE_TOKEN_DATA_V1_PASS                        Track A untouched, extraction /
                                                sampling / topology / geometry
                                                validation all clean
CURVE_TOKEN_DATA_V1_PARTIAL_PASS                some curve types unsupported or
                                                pass rates below threshold
CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION       highest-priority failure; stop
```

## Not in this round

No Qwen integration, no VQ tokenizer, no Curve Encoder training, no changes to the
existing Surface/Edge token pipeline or to Sonata.
