# SPATIALLM_CURVE_TOKEN_V1 — Curve Token → SpatialLM

Steps 1–5: feed frozen 256-D Curve Tokens to SpatialLM as a second geometry
stream, and check on 100 CADs whether the LLM actually uses them.

Nothing under `SpatialLM/` is modified. Method A configs
(`spatiallm_cad_joint_j0_surface.yaml`, `..._j2_sepedge.yaml`) are untouched;
everything here is applied by runtime monkey-patching.

## Two corrections to the original plan

1. **`hidden_size` is 2048, not 4096.** `SpatialLM1.1-Llama-1B/config.json`
   gives `hidden_size: 2048`, so the adapter is `256 → 2048`.
2. **Baseline 1 already exists.** "sharp edge points → point encoder → edge
   token → LLM" is exactly the shipped J2 `sepedge` recipe (shared Sonata, a
   separate `edge_proj`, its own marker tokens). No new code was needed for it,
   only a 100-CAD config.

Also worth noting: the pipeline is already full-parameter finetuning with a
frozen point encoder (`freeze_point_tower: true`), which is precisely the Step 5
recommendation. LoRA was never in play.

## The key design decision: B1 and M2 share one sequence slot

J2's "separate edge tokens" is really a generic *second geometry stream*: marker
tokens, a splice region in `_splice_geometry`, label masking, and a dedicated
projector. Curve Tokens reuse that slot verbatim and only swap the payload.

```
Instruction
<|point_start|>   [ N surface tokens ]   <|point_end|>          <- Sonata + point_proj
<|reserved_6|>    [ M second-stream tokens ]  <|reserved_7|>    <- B1 or M2
   B1: edge point cloud -> shared Sonata -> edge_proj
   M2: curve tokens (frozen, precomputed) -> CurveProjector
-> LLM
```

Because both arms use the same markers at the same position, the prompt is
byte-identical and the *only* variable is how the same sharp edges are
represented. The cost is that surface + edge points + curve tokens cannot be fed
simultaneously, which the three-arm comparison does not need.

## Components

| file | role |
|---|---|
| `config.py` | paths, `CURVE_TOKEN_DIM=256`, `LLM_HIDDEN_SIZE=2048`, `MAX_CURVE_TOKENS=128` |
| `export_curve_tokens.py` | Step 1 data: frozen C2 tokens per CAD → `[K,256]` npy |
| `make_subset100.py` | Step 4: 80 DeepCAD + 20 Fusion360 overfit subset |
| `curve_projector.py` | Step 1: the adapter, `256 → 2048` |
| `curve_token_injector.py` | Step 2: runtime patches (plugin + projector attach + `forward_geometry`) |
| `train_curve_token_spatiallm.py` | installs patches, hands over to SpatialLM `run_exp` |
| `verify_injection.py` | shape/marker/budget checks before spending GPU hours |
| `run_all.sh` | the three arms |
| `collect_results.py` | loss-curve comparison table |

## The Curve Encoder is frozen by construction

Tokens are computed **offline** by `export_curve_tokens.py` using the C2 backbone
from `curve_token_head_v1/runs/D1_frozen_v1_seed0/best.pt`, then stored on disk.
The training loop only ever sees `[K,256]` float arrays, so no gradient can reach
the encoder — stronger than a `requires_grad=False` flag.

Curves are restricted to **B-Rep sharp** edges so the payload carries the same
geometry as B1's `edge_points_gt_sharp.npy`. Curves are ranked by polyline length
and truncated at 128, since a single CAD can have >1000 curves.

Export stats for the 100-CAD subset: 2 / 24 / 102 / 128 curve tokens per CAD
(min / median / p90 / max), 7 of 100 CADs truncated.

## Sequence budget — an asymmetry to keep in mind

Geometry tokens are spliced in *after* tokenization, so `cutoff_len` bounds the
text only. Measured on six subset CADs:

| stream | tokens per CAD |
|---|---|
| surface (both arms) | 3040 – 7775 (mean 6649) |
| B1 second stream (edge points) | 862 – 1023 (mean 986) |
| M2 second stream (curve tokens) | 2 – 128 (median 24) |

M2 carries the same edges in roughly **40× fewer tokens**. That cuts both ways:
if M2 wins it wins cheaply, and if it loses, capacity is a candidate explanation
rather than representation quality. Report token counts with any result.

## Running

```bash
python3 scripts/spatiallm_curve_token_v1/make_subset100.py
python3 scripts/spatiallm_curve_token_v1/export_curve_tokens.py \
    --ids ours3/spatiallm_curve_token_v1/subset100/curve100_ids.json
python3 scripts/spatiallm_curve_token_v1/verify_injection.py
bash    scripts/spatiallm_curve_token_v1/run_all.sh <gpu> B0 B1 M2
python3 scripts/spatiallm_curve_token_v1/collect_results.py
```

Each arm is launched twice because SpatialLM's loader preprocesses, exits, and
only trains on the second launch; `run_all.sh` handles this.

Arms run **sequentially** on one GPU (`auto` picks the emptiest at launch).

Two concessions to the shared GPUs, both applied identically to every arm so the
comparison is unaffected:

- `optim: adafactor` instead of AdamW. The fp32 Adam moments for 1.24B trainable
  params are ~10 GB on their own, which repeatedly OOM'd next to other tenants.
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, since ~7600 geometry
  tokens per sample make the run fragmentation-sensitive.

100 CADs at batch 4 is only 25 steps per epoch, so `num_train_epochs: 80`
(2000 steps) is what it takes to reach the loss regime where J0/J2 converged;
20 epochs (500 steps) stops while the loss is still falling steeply.

When stopping a run, match on `curve100` — a bare `pkill -f train.py` will also
kill unrelated SpatialLM trainings such as the j2o/j2p runs.

Multi-GPU note: M2 goes through `train_curve_token_spatiallm.py`, which calls
`run_exp` directly and therefore skips `SpatialLM/train.py`'s torchrun path. For
DDP the injector's `install()` would need to be called inside
`spatiallm/tuner/trainer.py`'s entrypoint instead.

## Environment flags

| flag | B0 | B1 | M2 |
|---|---|---|---|
| `CAD_USE_SEPARATE_EDGE_TOKENS` | unset | `1` | `1` |
| `CAD_EDGE_SOURCE` | — | `gt_sharp` | — |
| `CAD_SECOND_STREAM` | — | `edge_points` | `curve_tokens` |
| `CURVE_PROJECTOR` | — | — | `mlp` (default) or `linear` |

## Reading a checkpoint

In curve-token mode the adapter is stored under `edge_proj.*` — deliberately the
same slot as B1's edge projector, which is what makes the two arms comparable.
`config.curve_token_stream`, `curve_token_dim` and `curve_projector_kind` are
written so the checkpoint is self-describing.

## Result: the probe saturates and cannot answer the question

Full table in `ours3/spatiallm_curve_token_v1/runs/TABLE_CURVE100.md`.

| arm | first epoch under loss 1.0 | under 0.1 | under 0.01 | final loss |
|---|---|---|---|---|
| B0 surface only | 14.0 | 24.6 | 39.8 | 0.0002 |
| B1 + edge points | 13.2 | 25.2 | 37.8 | 0.0002 |
| M2 + curve tokens | 14.2 | 25.8 | 37.8 | 0.0002 |

All three arms follow the same trajectory and end at the same loss. The three
curves interleave epoch by epoch, with no ordering that survives more than a
couple of logging steps.

The reason is that the probe has no headroom: **surface tokens alone are enough
to memorize 100 CADs**, so the second stream is never needed and the experiment
cannot distinguish "the LLM ignores curve tokens" from "the LLM does not need
them here". This is a property of the overfit setup, not evidence about Curve
Tokens either way.

What the run *does* establish: curve tokens reach the LLM, training is stable,
and adding the stream costs nothing in optimization behaviour (M2 differs from B0
by exactly the 592,128 CurveProjector parameters).

To make the comparison discriminative, the task has to stop being memorizable.
The options, cheapest first:

1. **Hold out CADs.** Train on a few thousand and evaluate DSL quality on unseen
   CADs. Generalization is where an edge representation should pay off, and the
   J0/J2 runs already provide the baselines at that scale.
2. **Starve the LLM.** `train_proj_only: true` freezes the LLM so the answer must
   come through the geometry streams; the arms then measure representation
   quality directly instead of the LLM's memorization capacity.
3. **Weaken the surface stream.** Subsample surface points (e.g. 8192 → 512) so
   edges carry information the surface no longer has.

Note also the sequence-length asymmetry above: M2 conveys the same edges in ~40×
fewer tokens, so in a regime with real headroom "equal quality" would already be
a win for curve tokens.
