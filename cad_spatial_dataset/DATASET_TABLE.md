# Dataset Table (Draft v1)

Last updated: 2026-08-24

This table is for paper writing and experiment tracking.  
Core rule for fair ablation: **different inputs must share the same CAD target sequence**.

| Dataset | Samples | CAD representation | Program available | B-Rep | Mesh | Mesh generation | Edge GT | Split | Usage |
|---|---:|---|---|---|---|---|---|---|---|
| DeepCAD canonical pool (`cad_spatial_dataset/DeepCAD/train`) | 2209 | Parametric CAD DSL (`program.dsl`, `program_canonical.dsl`) | Yes | Yes (`model.step`) | Yes (`model.obj`, `model.stl`) | STEP -> mesh via `scripts/deepcad/step_to_mesh.py` (trimesh / cadquery fallback) | Mesh sharp edge signal from Dora (`edge_score`, `dora/`) | Unsplit pool | Base source for training/eval subsets |
| DeepCAD train100 manifest (`manifest_train100.json`) | 100 requested | Same as above | Yes (99 have frozen canonical DSL) | Yes | Yes | Same as above | Dora sharp-edge derived | Train subset | Fast iteration / overfit-scale ablation |
| DeepCAD train1k v1 (`manifest_train1k_v1.json`) | 1000 | Same as above | Yes | Yes | Yes | Same as above | Dora sharp-edge derived | Complexity split 800/100/100 | Main training/eval (1K round) |
| DeepCAD `separate_edge_tokens_v1` cache | 99 built | Surface cloud + separate edge cloud | Yes (inherited) | Indirect | Yes | Reuses old mesh/surface artifacts | Mesh sharp from Dora segments | Follows train100 ids | Smoke test only; **not** for formal paper ablation |
| DeepCAD `geometry_pack_v1` (**formal overfit pack**) | **99 built / 100 requested** | Frozen CAD target (`cad_target.dsl`, SHA-checked) | Yes | Yes | Yes | **Frozen OCC tessellation**: linear = `max(1e-3 * bbox_diag, 1e-6)`, angular = `20°` | **Dual GT**: `edge_points_gt_all.npy` (all TopoDS_Edge) + `edge_points_gt_sharp.npy` (B-Rep dihedral `>30°`) + `edge_points_detected.npy` (mesh dihedral `>30°`) | train100 overfit (minus 1 incomplete source) | Official fair ablation; Method-1 oracle = **sharp** |
| DeepCAD `geometry_pack_v1` (full) | **2194** | Frozen CAD target | Yes | Yes | Yes | Frozen OCC tessellation | Dual GT sharp/all/detected | `joint_deepcad_fusion360_v1` | Surface J0 / edge ablations |
| Fusion360 `geometry_pack_v1` | **602 surface-valid / 601 edge-valid** | Same DSL family (**no BSpline/Loft/Sweep target**) | Yes | Yes | Yes | Same OCC contract | Dual GT; zero-sharp allowed (`edge_valid=false`) | `joint_deepcad_fusion360_v1` | Joint J0; STEP freeform ≠ DSL target |
| Fusion360 canonical pool (`cad_spatial_dataset/Fusion360/train`) | 635 | Parametric CAD DSL | Yes | Yes | Yes | STEP -> mesh (DeepCAD-style pipeline) | Dora sharp-edge derived | Unsplit pool (+ manifests) | Cross-dataset robustness / transfer |
| Fusion360 `freeform_surface_pack_v1` (**freeform pilot**) | **729 BSpline faces** (+700 Plane +650 Cylinder controls) from **37** freeform parts / 624 source | Face-level NURBS patch (`surface_raw.npz` + canonical 8×8) | No CAD DSL (surface reconstruction) | Yes (per-face BSpline) | Per-face tessellation + `face_mesh.npz` | Same frozen OCC deflection family | Boundary polylines + `boundary_points.npy` (256×6); curve types LINE/BSPLINE | **Part-level** 25/6/6 → 302/222/205 patches | Freeform reconstruction / type classification; **not** Edge Method-1 |

## Method-1 edge semantics (locked)

| File | Meaning | Used by |
|---|---|---|
| `edge_points_gt_all.npy` | All non-degenerate B-Rep `TopoDS_Edge` | Audit only |
| `edge_points_gt_sharp.npy` | B-Rep edges with face-pair dihedral `θ > 30°` | **Method-1 oracle (default)** |
| `edge_points_gt.npy` | Alias of `edge_points_gt_sharp.npy` | Back-compat only |
| `edge_points_detected.npy` | Mesh face-adjacency dihedral `θ > 30°` | Method-1 practical |

Oracle and practical share the **same sharp predicate** (`dihedral_deg > 30`).

## Notes for paper text

- Fair ablation: Baseline / edge-score / method-1 / method-2 must share the same `cad_target.dsl`.
- Surface sampling: area-weighted uniform on triangles; never raw mesh vertices; `surface_points.npy` is `[8192, 6]` with no `edge_score`.
- Dropped sample: `0048_00486244` missing `program_canonical.dsl` / `coordinate_transform.json` in train pool (same gap as the old 99-cache).
- Pack path: `cad_spatial_dataset/DeepCAD/geometry_pack_v1/<sample_id>/`
- Build summary: `cad_spatial_dataset/DeepCAD/geometry_pack_v1/build_summary.json`
