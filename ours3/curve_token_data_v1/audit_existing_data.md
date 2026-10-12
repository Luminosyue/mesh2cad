# Track B audit of existing Track A curve data

Read-only audit performed before writing any Track B artifact. Track A files
listed here are **never modified**; `brep_edges.json` and `brep_edges.npz` are
treated as immutable inputs.

## 1. What Track A actually stores

### `deepcad_train` -- `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/geometry_pack_v1`

- sample directories: 250
- `brep_edges.json` present: 250
- `brep_edges.npz` present: 250

`brep_edges.json` top-level keys: `['edges', 'num_segments_all', 'num_segments_sharp', 'num_topo_edges', 'num_topo_edges_sharp', 'sharp_angle_deg', 'sharp_predicate', 'skipped_degenerate']`

`brep_edges.json` per-edge keys: `['curve_type', 'dihedral_deg', 'edge_index', 'is_sharp', 'length', 'n_faces']`

`brep_edges.npz` arrays:

| array | shape | dtype |
|---|---|---|
| `curve_types` | `(42,)` | `<U4` |
| `dihedral_deg` | `(42,)` | `float32` |
| `lengths` | `(42,)` | `float32` |
| `num_topo_edges` | `(1,)` | `int64` |
| `segment_dihedral_deg` | `(1994,)` | `float32` |
| `segment_normals` | `(1994, 3)` | `float32` |
| `sharp_mask` | `(1994,)` | `bool` |
| `v0` | `(1994, 3)` | `float32` |
| `v1` | `(1994, 3)` | `float32` |

curve_type values observed: `{'Line': 19163, 'Circle': 194}`

### `fusion360_train` -- `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/geometry_pack_v1`

- sample directories: 250
- `brep_edges.json` present: 250
- `brep_edges.npz` present: 250

`brep_edges.json` top-level keys: `['edge_valid', 'edges', 'num_segments_all', 'num_segments_sharp', 'num_topo_edges', 'num_topo_edges_sharp', 'sharp_angle_deg', 'sharp_predicate', 'skipped_degenerate']`

`brep_edges.json` per-edge keys: `['curve_type', 'dihedral_deg', 'edge_index', 'is_sharp', 'length', 'n_faces']`

`brep_edges.npz` arrays:

| array | shape | dtype |
|---|---|---|
| `curve_types` | `(98,)` | `<U6` |
| `dihedral_deg` | `(98,)` | `float32` |
| `lengths` | `(98,)` | `float32` |
| `num_topo_edges` | `(1,)` | `int64` |
| `segment_dihedral_deg` | `(3542,)` | `float32` |
| `segment_normals` | `(3542, 3)` | `float32` |
| `sharp_mask` | `(3542,)` | `bool` |
| `v0` | `(3542, 3)` | `float32` |
| `v1` | `(3542, 3)` | `float32` |

curve_type values observed: `{'Line': 7385, 'Circle': 1818, 'BSpline': 1438, 'Ellipse': 111}`

## 2. Source of exact ground truth

| split | STEP source | model.step count | Track A normalization contract |
|---|---|---|---|
| `deepcad_train` | `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/train` | 2199 | `['scale', 'source_bbox_max', 'source_bbox_min', 'source_diagonal', 'target_diagonal', 'translation']` |
| `fusion360_train` | `/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/Fusion360/train` | 624 | `['scale', 'source_bbox_max', 'source_bbox_min', 'source_diagonal', 'target_diagonal', 'translation']` |

Exact parametric ground truth is read directly from the CAD kernel:

```text
model.step -> STEPControl_Reader -> TopoDS_Edge -> BRepAdaptor_Curve
           -> Geom_Line / gp_Circ / gp_Elips / Geom_BSplineCurve
           -> exact parameters
```

Edge-point sampling followed by re-fitting is **not** used to manufacture GT;
`fit_curves_from_points.py` exists only to benchmark the reverse direction.

## 3. Field-by-field reuse analysis

Legend: **reuse** = already present in Track A and directly usable;
**derive** = approximately recoverable from Track A but not exact;
**missing** = absent from Track A, must be read from the B-Rep.

### common

| field | status | notes |
|---|---|---|
| `curve_type` | **reuse** | brep_edges.json:edges[].curve_type (mixed-case names) |
| `length` | **reuse** | brep_edges.json:edges[].length / brep_edges.npz:lengths |
| `edge_id` | **reuse** | brep_edges.json:edges[].edge_index (same OCC map order) |
| `n_faces` | **reuse** | brep_edges.json:edges[].n_faces (count only, no face ids) |
| `dihedral_deg` | **reuse** | brep_edges.json:edges[].dihedral_deg |
| `is_sharp` | **reuse** | brep_edges.json:edges[].is_sharp |
| `start_point / end_point` | **derive** | endpoints of brep_edges.npz polyline (approx only) |
| `face_ids` | **missing** | no face identity stored in Track A |
| `vertex_ids` | **missing** | no vertex identity stored in Track A |
| `u_start / u_end` | **missing** | no parameter range stored in Track A |
| `is_closed` | **missing** | not stored in Track A |
| `tangent` | **missing** | Track A stores face normals, not curve tangents |

### LINE

| field | status | notes |
|---|---|---|
| `origin` | **missing** | must be read from Geom_Line |
| `direction` | **derive** | normalize(v1-v0) of a polyline segment (approximate) |
| `parameter range` | **missing** | must be read from the edge |

### CIRCLE

| field | status | notes |
|---|---|---|
| `center` | **missing** | must be read from gp_Circ |
| `normal` | **missing** | must be read from gp_Circ axis |
| `radius` | **missing** | must be read from gp_Circ |
| `x_axis` | **missing** | must be read from gp_Ax2 XDirection |
| `parameter range` | **missing** | must be read from the edge |

### ELLIPSE

| field | status | notes |
|---|---|---|
| `center` | **missing** | must be read from gp_Elips |
| `major axis` | **missing** | must be read from gp_Ax2 XDirection |
| `major radius` | **missing** | must be read from gp_Elips |
| `minor radius` | **missing** | must be read from gp_Elips |
| `parameter range` | **missing** | must be read from the edge |

### BSPLINE

| field | status | notes |
|---|---|---|
| `degree` | **missing** | must be read from Geom_BSplineCurve |
| `control points` | **missing** | must be read from Geom_BSplineCurve poles |
| `knots` | **missing** | must be read from Geom_BSplineCurve |
| `multiplicities` | **missing** | must be read from Geom_BSplineCurve |
| `weights` | **missing** | must be read from Geom_BSplineCurve |
| `parameter range` | **missing** | must be read from the edge |
| `periodic` | **missing** | must be read from Geom_BSplineCurve |

## 4. Conclusion

- reusable as-is: **6** fields (all metadata, no exact geometry)
- approximately derivable: **2** fields
- must be re-read from the B-Rep: **24** fields

Track A stores a *point-level* edge representation: polyline segments plus
per-edge scalars (`curve_type`, `length`, `dihedral_deg`, `is_sharp`). It contains
**no analytic curve parameters at all** -- no origin/direction, no
center/normal/radius, no control points, knots, multiplicities or weights, and no
parameter ranges. It also stores only the *count* of adjacent faces (`n_faces`),
not face or vertex identity, so topology cannot be reconstructed from it.

Consequently every exact parameter Track B needs is re-read from `model.step`.
The only Track A artifact reused verbatim is `coordinate_transform.json`, so that
Curve Tokens share a coordinate frame with the existing Surface/Edge tokens.
