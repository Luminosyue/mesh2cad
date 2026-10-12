# Curve Encoder Baseline V1 — Geometry-only

Isolated Track B training package. **Track A is frozen. curve_token_data_v1 is read-only.**

## Question this baseline answers

> Looking only at one curve's noisy sampled points, can a network learn a stable Curve Token?

```text
32 sampled points (xyz_normalized [+ tangent])
        ↓
 Curve Encoder (PointNet or 1D Transformer)
        ↓
 256D Curve Token
        ↓
  ├─ Curve Type Head
  ├─ Geometry Reconstruction Head
  └─ Parameter Regression Head
```

No Qwen / LLM. No `curve_type` as input (Geometry-only).

## Isolation

| rule | enforcement |
|---|---|
| Track A read-only | `guard.py` sha256 snapshot before/after |
| `curve_token_data_v1` read-only | write-scope assert refuses overlap |
| Writes only here | `ours3/curve_encoder_baseline_v1/` |

## Ablations (input)

| id | input | notes |
|---|---|---|
| B0 | xyz | sanity |
| B1 | xyz + tangent | primary |
| B2 | xyz + tangent + length/closed | optional |

`curve_type` is a **prediction target**, never an input in this package.

## Models

- **PointNet**: `32×C → MLP  C→64→128→256 → max-pool → 256D`
- **Transformer**: `32×C → Linear + arc-pos → 2–4 blocks → CLS → 256D`

## Splits

CAD-level (Fusion360: family = `project_hash`). Curves never cross splits.

**Before training:** run `python3 -m curve_encoder_v1.training_data_audit`  
→ `ours3/curve_encoder_baseline_v1/reports/training_data_audit_v1/TRAINING_DATA_AUDIT_V1.md`

Known risks (audit WARN, not data bugs):
- ~95% LINE → majority baseline ~95% type-acc; use class weights / oversample rare types on **train only**
- Ellipse n=366; BSpline long-tail Ncp≤95 — keep 32/64 sample-point representation
- World length spans ~12 decades — use `length_normalized` or `log(length+eps)`, never raw world length as primary feat
- Input must stay Geometry-only (`xyz[+tangent][+curve_u]`); GT type/params are supervision / oracle only

## Eval axes

- Noise σ ∈ {0, 1e-4, 1e-3, 5e-3} (relative to target_diagonal=6)
- Partial observation ∈ {100%, 75%, 50%, 25%}
- Arc-coverage buckets for CIRCLE/ELLIPSE
- Classical fitting comparison on the same conditions

## Run

```bash
# canary (fast)
python scripts/run_curve_encoder_baseline_v1.py --stage canary

# full
python scripts/run_curve_encoder_baseline_v1.py --stage full
```

## Gate

`CURRENT_GATE=CURVE_ENCODER_BASELINE_V1_PASS` requires Track A unmodified and both
baselines + clean/noise/partial/classical/embedding reports finished.
