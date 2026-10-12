# Additional watertight mesh-to-CAD cases

All three inputs were screened as non-empty, single-component, watertight meshes with more than 100 faces and non-degenerate bounding boxes. Each reconstruction is an independent parametric CadQuery program and does not read its source mesh.

| Case | Exact source file | CAD route | Best | STEP reload | IoU | Chamfer-L1 | Normal consistency | BBox relative error |
|---|---|---|---|---:|---:|---:|---:|---:|
| CADPART_004 | `/data/home/cuiyuehan/project/mesh2cad/ours3/cad_part_recovery_v1/cases/CADPART_004/source_part.obj` | Cylindrical body + neck + annular ribs | v3 | PASS | 0.781763 | 0.019415 | 0.832048 | 0.007883 |
| CASE05_PART000 | `/data/home/cuiyuehan/project/mesh2cad/ours3/batch_real_mesh2cad_v1/cases/CASE_05/p3/part_000.obj` | Rounded-rectangle extrusion | v2 | PASS | 0.435610 | 0.012902 | 0.785374 | 0.088817 |
| CASE06_PART000 | `/data/home/cuiyuehan/project/mesh2cad/ours3/batch_real_mesh2cad_v1/cases/CASE_06/p3/part_000.obj` | Seven-section elliptical loft | v1 | PASS | 0.390840 | 0.043615 | 0.797736 | 0.028486 |

## Interpretation

- `CADPART_004` V2 had its body and threaded neck assigned to opposite PCA-axis ends. V3 corrected the axial sign and raised IoU from 0.304282 to 0.781763. It preserves the bottle-like envelope, reduced neck and repeated ribs, while still simplifying the detailed helical thread and lower recessed feature.
- `CASE05_PART000` is the best of these cases by IoU and Chamfer-L1. Its thin elongated envelope is well represented by a rounded plate, although the source includes a stepped/local profile that increases area and bbox errors.
- `CASE06_PART000` is an organic shape. The editable loft captures the overall volume and dimensions, but not the irregular lobes and local depressions.

The reported IoU uses a common source-coordinate voxel grid at `max_bbox_extent / 96`. Successful comparisons use 50,000 surface samples.
