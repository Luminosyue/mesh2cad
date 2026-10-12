# P1 VAL `gt_sharp` interface audit (toaster mesh-edge ablation)

This ablation must match the **runtime tensor contract** of official P1 VAL, while replacing the **curve source** with X-Part mesh dihedral edges. Historical P1 / CADFit / toaster trees are read-only.

## What VAL actually consumes

Report field `edge_source=gt_sharp` on `ours3/p1_exact9998_val1000_eval_v2` is a CLI leftover from `decode_joint_j0_j2.py`. P1 does **not** ingest raw `edge_points_gt_sharp.npy` `(1024,6)`.

Official P1 VAL path:

1. `CAD_USE_SEPARATE_EDGE_TOKENS=1`
2. `CAD_SECOND_STREAM=curve_tokens`
3. `curve_token_injector.install()` patches `_load_cad_separate_edge`
4. `--variant j2`
5. Second stream payload = frozen C2 tokens **`(K, 256)`**, `K≤128`
6. C2 checkpoint = `ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt`
7. Registry = `ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl`
8. Projector = CurveProjector MLP `256 → 2048` occupying `edge_proj`

VAL **curve geometry source** (forbidden here): GT B-Rep sharp edges (`brep_edges.json` `is_sharp`) → 32-pt polylines → C2.

## What historical toaster P1 consumed

`ours3/toaster_p1_xpart_v1/predictions/full39_j0/report.json`:

- `--variant j0` (surface only)
- `edge_condition=none` for all 39
- `edge_source=gt_sharp` printed but unused
- no `curve_tokens.npy`, no `edge_points_*.npy`
- checkpoint `runs/p1` (= selected best `checkpoint-8000`)

## Ablation mapping

| Arm | Checkpoint | Second stream | Decode variant | Curve source |
|-----|------------|---------------|----------------|--------------|
| A | checkpoint-8000 | none | j0 | — |
| B | checkpoint-8000 | C2 `(K,256)` | j2 + injector | X-Part mesh dihedral θ>30°, chained, resampled 32, C2 |
| C | checkpoint-39980 | none | j0 | — |
| D | checkpoint-39980 | C2 `(K,256)` | j2 + injector | same mesh curves as B |

Surface clouds and `transform.json` are **copied** from toaster P1 inputs (`8192×6`, target diagonal 6.0). No re-canonicalization.

Mesh source: `toaster_p3_xpart_cadfit_routea_v1/xpart/PART_xxx/generated_mesh.obj` (same inventory as toaster P1). Sharp edges are detected on the mesh **after** applying that stored T. No STEP/BRep/GT DSL is read.

If a part has zero retained chains, j2 still needs `K≥1` (injector contract). Ablation injects a single zero token and flags `empty_sharp_fallback=zero_token`.

## Not used

- `CAD_EDGE_SOURCE=detected` / raw `(1024,6)` mesh clouds (B1 Sonata-edge mode; P1 `edge_proj` expects 256-d tokens)
- GT BRep oracle curves
- Training / checkpoint writes
- Historical prediction overwrite
