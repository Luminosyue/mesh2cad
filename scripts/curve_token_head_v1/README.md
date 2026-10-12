# CURVE_TOKEN_HEAD_V1 — frozen C2 backbone + multi-head Curve Token

Track B / Method-2. Reads only `ours3/curve_token_data_v1` (+ the frozen_v1 split and
cache under `ours3/curve_encoder_baseline_v1`). Fully isolated from Track A / Method-1.

## Step 1 — frozen encoder backbone (do not change)

```
curve-local xyz(3) + tangent(3) + s(1)   [32,7] ──► PointNet ──┐
                                                               ├─► concat + MLP ─► Curve Token [256]
log(polyline length + 1e-6)              [1]   ──► MLP(64)  ───┘
```

* `encoder = C2` (from `scripts/curve_encoder_scale_curvature_v1`, exp C2)
* `split = frozen_v1`, `token_dim = 256`, `n_points = 32`
* training setting fixed in `config.py::TRAIN`

The C2 choice comes from the scale/curvature ablation: curve-local normalization removed
the spurious "long line → CIRCLE" shortcut, and re-injecting `log(length)` through a
separate branch keeps scale information without reintroducing the shortcut.

## Steps 2–3 — heads

```
                       Curve Token (256)
        ┌───────────────────┬────────────────────┐
        ▼                   ▼                    ▼
    type head        reconstruction head    parameter heads
  CE over 4 types    32 points → Chamfer    per-type regression
```

Parameter targets live in the **curve-local frame** (same frame as the encoder input):
centers/origins/radii are divided by `curve_scale`, directions are used as-is, angles are
encoded as `(cos, sin)` pairs.

| type | head dim | targets |
|---|---|---|
| LINE | 7 | origin[3], direction[3], length |
| CIRCLE | 12 | center[3], normal[3], radius, cos/sin u0, cos/sin u1, span_frac |
| ELLIPSE | 17 | center[3], major_axis[3], minor_axis[3], normal[3], r_major, r_minor, cos/sin u0, span_frac |
| BSPLINE | 6 + 1 | degree (6-way class over 3..8), log(num_control_points) |

BSPLINE control points are deliberately **not** regressed: variable length (P95 = 34,
max = 95 in this dataset), so geometry is supervised through the 32-point reconstruction
instead.

Loss: `L = CE + 1.0 · L_recon + 0.1 · L_param`, where `L_recon = 0.5·Chamfer +
0.5·ordered MSE` (Chamfer is the reported metric; the ordered term keeps arc-length
order) and `L_param` is averaged over the types present in the batch so LINE does not
drown out the rare types.

## Step 4 — the key experiment

| exp | heads | question |
|---|---|---|
| D0 | type only | classification-only reference on the frozen backbone |
| D1 | type + reconstruction + parameters | does geometric supervision help or hurt classification, and does the token actually store geometry? |

Both runs use the identical backbone, split, sampler, budget and selection rule
(max val Macro F1, tie-break on fewer LINE→CIRCLE FPs).

```bash
bash scripts/curve_token_head_v1/run_all.sh 5             # single seed, GPU id
python3 scripts/curve_token_head_v1/make_table.py         # → runs/TABLE_D0D1_TEST.md

bash scripts/curve_token_head_v1/run_seeds.sh 5 "0 1 2"   # 3 seeds per arm
python3 scripts/curve_token_head_v1/aggregate_seeds.py    # → runs/TABLE_D0D1_SEEDS_TEST.md
```

The D0/D1 Macro F1 gap is smaller than the epoch-to-epoch and seed-to-seed spread, so the
seed-replicated table is the one to read; the single-seed table is only a quick check.

Reported metrics: Macro F1, Balanced Accuracy, per-class F1, LINE→CIRCLE FP,
reconstruction Chamfer, and per-type parameter errors (LINE direction°, CIRCLE normal° /
radius rel. err, ELLIPSE major-axis°, BSPLINE degree accuracy).

## Step 5 — canonical Curve Token data format

```bash
python3 scripts/curve_token_head_v1/export_curve_token_format.py
```

Writes to `ours3/curve_token_head_v1/curve_token_format/`:

* `frozen_v1_{split}_curve_tokens.npz` — bulk float32 arrays (input + supervision)
* `frozen_v1_{split}_preview.jsonl` — the literal nested record form, stratified by type
* `schema.json` — field-by-field contract

Record form:

```json
{
  "curve_token_input": {"xyz_local": [[...]], "tangent": [[...]], "s": [...], "log_length": -2.13},
  "supervision": {"type": "CIRCLE",
                  "params": {"center": [...], "normal": [...], "radius": 0.5, "span_frac": 1.0},
                  "samples": [[...]]},
  "ref": {"dataset": "...", "sample_id": "...", "edge_id": 12, "curve_scale": 0.083}
}
```

Downstream (LLM) consumers should take `curve_token`, not raw `curves.json`.

## Step 6 — real mesh edge → curve (next stage, not implemented here)

Everything above is trained on **GT B-Rep curve samples**, which are clean. The practical
pipeline still has to be built:

```
mesh → sharp-edge detection → edge points → edge grouping → 32 resampled points
     → C2 Curve Encoder → Curve Token → type / params / reconstruction
```

Open items before that stage can start:

1. edge grouping (split detected sharp-edge point clouds into per-curve polylines,
   handle junctions and closed loops);
2. arc-length resampling to exactly 32 ordered points with stable tangents from noisy
   mesh points;
3. domain gap: train/eval the frozen C2 encoder on mesh-derived samples versus GT
   samples, since tangent noise is the main difference;
4. evaluation against the B-Rep GT curve for the matched edge (type accuracy + parameter
   error + Chamfer), reusing this package's metrics.
