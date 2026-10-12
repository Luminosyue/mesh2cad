# MESH_EDGE_TO_CURVE_V1 — Step 6: mesh sharp edge → Curve Token

Reads only `geometry_pack_v1` (mesh side), `ours3/curve_token_data_v1` (B-Rep GT),
the `frozen_v1` split, and the frozen `D1` checkpoints. Writes only under
`ours3/mesh_edge_to_curve_v1/`.

## Why the packed edge point clouds could not be used

`geometry_pack_v1/<sample>/edge_points_detected.npy` is `[1024, 6]` **per CAD**, i.e. one
global cloud for the whole model, and it carries no per-point edge identity — only
`edge_segment_index_*.npy`, which indexes polyline *segments*, not topological edges. For a
CAD with 494 edges that is ~2 points per edge, far too few to resample 32 points per curve.

This package therefore works from `mesh_sharp_edges.npz` (`v0`, `v1`, `vertex_indices`,
`dihedral_deg`, `face_pairs`), the full-density set of mesh triangle edges whose dihedral
exceeds 30°, in world coordinates. Points are mapped into the canonical frame with the same
`metadata.json::canonical` transform (`p' = s·p + t`) that the curve data uses, so mesh
points and `curve_xyz_normalized` live in one frame.

## Step 6.1A — oracle grouping

```bash
python3 scripts/mesh_edge_to_curve_v1/build_oracle_dataset.py --split test
CUDA_VISIBLE_DEVICES=0 python3 scripts/mesh_edge_to_curve_v1/eval_domain_gap.py --exp D1
python3 scripts/mesh_edge_to_curve_v1/make_report.py     # → runs/REPORT_STEP61A_D1_test.md
```

Oracle (must be replaced in 6.1B):

* **grouping** — each mesh sharp segment is attached to the B-Rep curve it lies on, by
  exact point-to-segment distance against the GT 64-point polyline, accepted only when the
  whole segment is within 1% of the canonical diagonal;
* **ordering** — points inside a group are sorted by their projected arc-length position on
  the GT polyline. This deliberately removes chaining as a confound.

Purely mesh-derived, and therefore what the experiment actually measures: point positions,
point spacing, and tangents (finite differences on the resampled polyline).

The evaluation is paired over three arms on the same curves with the same checkpoints:

| arm | xyz | tangent |
|---|---|---|
| `brep` | exact B-Rep samples | exact OCC tangent (training distribution) |
| `brep_fd` | exact B-Rep samples | finite differences (isolates tangent estimation) |
| `mesh` | mesh sharp-edge samples | finite differences (full mesh path) |

Parameter targets are rebuilt in each arm's own curve-local frame, so centers, radii and
lengths stay comparable across arms.

## Step 6.1B — real grouping (not implemented)

Replace both oracle components with GT-free algorithms:

1. build a graph over mesh sharp-edge vertices and split it at junctions (vertex degree ≠ 2)
   and at tangent discontinuities, giving candidate chains;
2. order each chain by graph traversal instead of GT projection, and pick a deterministic
   orientation (the frozen C2 input contains `s` and tangents, so a flipped traversal is a
   different input — this is the main new risk that oracle ordering hides);
3. handle closed loops (no degree-1 endpoint) and chains that merge several B-Rep edges of
   the same type into one candidate.

Evaluation against 6.1A: how much of the recovered set survives, and how much
over/under-segmentation costs relative to the oracle numbers already measured.
