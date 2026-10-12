# Separate Edge Point Tokens V1 — Repository Audit

Read-only audit performed before any code change.

## File map

```text
SURFACE_DATASET_FILE=SpatialLM/spatiallm/tuner/data/mm_plugin.py::SpatialLMPlugin._load_cad_npy
COLLATOR_FILE=SpatialLM/spatiallm/tuner/data/collator.py::MultiModalDataCollatorForSeq2Seq
POINT_FORWARD_FILE=SpatialLM/spatiallm/model/spatiallm_llama.py::forward_point_cloud
PROJECTOR_FILE=SpatialLM/spatiallm/model/spatiallm_llama.py (self.point_proj)
MM_INJECTION_FILE=SpatialLM/spatiallm/model/spatiallm_llama.py::forward
TOKENIZER_SPECIAL_TOKEN_FILE=SpatialLM/models/SpatialLM1.1-Llama-1B/tokenizer_config.json
CURRENT_POINT_INPUT_SHAPE=(B, N_voxel, 10)
CURRENT_SURFACE_CHANNELS=6 baseline / 7 edge_score
CURRENT_POINT_TOKEN_COUNT=variable (~361 for a 8192-pt CAD part)
CURRENT_PROJECTOR_SHAPE=Linear(512,512) -> GELU -> Linear(512,2048)
```

## A. Dataset / preprocessing

`point_cloud` tensor is built in `SpatialLMPlugin._load_cad_npy` (CAD mode).

Column layout of the tensor handed to the model:

| cols | content | consumer |
| --- | --- | --- |
| 0-2 | `grid_coord` (int voxel index) | `coords` -> Sonata `grid_coord` |
| 3-5 | `xyz` (canonical metres) | Sonata `coord` |
| 6-8 | `nx, ny, nz` | Sonata `feat[:, 3:6]` |
| 9 | `edge_score` mapped to `2e-1` | Sonata `feat[:, 6]` (7ch mode only) |

* Surface sampling: offline, `scripts/build_cad_spatial_part.py` (8192 points), stored as
  `features.npy` then canonicalized to `features_canonical.npy`.
* `edge_score` enters at `mm_plugin.py:113-116` and is appended as the last column
  at `mm_plugin.py:140`.
* CAD target: `program_canonical.dsl`, wired into ShareGPT records by
  `scripts/deepcad/create_spatiallm_cad_dataset.py`.
* Canonical transform `p' = s*p + t` lives in `coordinate_transform.json`
  (`scripts/deepcad/cad_canonical.py`). `features_canonical.npy` and
  `program_canonical.dsl` share the same `T`.

## B. Collator

`MultiModalDataCollatorForSeq2Seq.__call__` pops `_point_clouds`, calls
`template.mm_plugin.get_mm_inputs(...)`, then `features.update(mm_inputs)`.
Anything the plugin puts into the returned dict is forwarded verbatim as a model
kwarg. This is the extension point for a second geometry stream: no collator
surgery is needed beyond adding the new key.

## C. Model

```python
coords = point_cloud[:, :3].int()
feats  = point_cloud[:, 3:].float()
input_dict = {"coord": feats[:, :3], "grid_coord": coords, "feat": feats, "batch": zeros}
encoded    = self.point_backbone(input_dict)      # Sonata, (K, 512)
return self.point_proj(encoded.unsqueeze(0))      # (1, K, 2048)
```

No truncation of `feat` occurs; all channels reach the Sonata stem.

## D. Multimodal injection

`forward()` splices per sample:

```python
cat(embeds[:point_start+1], point_features, embeds[point_end:])
```

and records `(point_start_pos, num_patches, point_end_pos)`. Labels are re-spliced
with the identical arithmetic and the geometry region filled with `IGNORE_INDEX`
(`spatiallm_llama.py:335-346`). Batch sequences are right-padded to the longest.

Only one `point_start` / `point_end` pair is allowed (`assert` at line 240).

## E. Tokenizer

`<|point_start|>`=128011, `<|point_end|>`=128012, `<|point_pad|>`=128013.
The checkpoint vocabulary already contains **245 unused
`<|reserved_special_token_N|>` entries**, so edge markers can be introduced with
**zero vocabulary resize**, which keeps every existing checkpoint loadable.

Chosen mapping (aliases, not new vocab entries):

| role | token | id |
| --- | --- | --- |
| `<EDGE_START>` | `<\|reserved_special_token_6\|>` | 128014 |
| `<EDGE_END>` | `<\|reserved_special_token_7\|>` | 128015 |
| `<EDGE_PAD>` | `<\|reserved_special_token_8\|>` | 128016 |

## F. Sharp-edge assets already present

`cad_spatial_dataset/DeepCAD/train/<id>/dora/salient_edges.npz`:

| key | shape | meaning |
| --- | --- | --- |
| `edge_vertex_indices` | (E, 2) int32 | mesh vertex index pair |
| `edge_xyz0` / `edge_xyz1` | (E, 3) f32 | segment endpoints, **source space** |
| `dihedral_deg` | (E,) f32 | face-normal angle |
| `edge_length` | (E,) f32 | segment length |

This is exactly the segment representation required for length-proportional
resampling, so no new edge detector is written.

## G. Correctness issue discovered during audit

`spatiallm/pcd/transform.py::GridSample` performs

```python
grid_coord = floor(coord / grid_size)
grid_coord -= grid_coord.min(0)          # <-- per-cloud re-origin
```

Encoding the edge cloud through the unmodified plugin would therefore give the
edge branch its **own voxel origin**. Sonata feeds `grid_coord` into
`fourier_encode_vector`, so surface tokens and edge tokens would carry
positional codes in two unrelated frames and the LLM could not spatially relate
them.

Mitigation implemented in V1: the edge cloud is voxelized against the **surface
cloud's grid origin**. Both branches then share one integer voxel lattice.
`GRID_ORIGIN_SHARED=True` is asserted and recorded per sample.

## H. Minimum change set

Modified (4 files, all gated so the default path is byte-identical):

1. `SpatialLM/spatiallm/model/spatiallm_llama.py`
2. `SpatialLM/spatiallm/tuner/data/mm_plugin.py`
3. `SpatialLM/spatiallm/tuner/data/template.py`
4. `SpatialLM/spatiallm/tuner/framework/patcher.py`

Added: `scripts/separate_edge_tokens_v1/**`, `SpatialLM/configs/spatiallm_cad_*_sepedge.yaml`.
