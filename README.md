# mesh2cad

Private source snapshot for the mesh-to-CAD project.

This repository contains project source files (`.py`, `.sh`, `.md`) from the lab working tree. It does not contain meshes, CAD solids, checkpoints, or experiment binaries. Those files are about 898GB and stay on the lab server at:

`/data/home/cuiyuehan/project/mesh2cad`

GitHub rejects files larger than 100MB, so the dataset cannot be pushed here. Hugging Face was unreachable from this server when this snapshot was made.

## Not included

Third-party checkouts are not vendored. Use their upstream repositories:

- CADFit
- DeepCAD
- Dora
- Hunyuan3D-Part
- BGPSeg
- SpatialLM

Downloaded foundation weights in `external_checkpoints/` are also omitted.

## Local data directories

These remain only on the lab server:

- `cad_spatial_dataset/`
- `mesh2cad_stl_00/`, `mesh2cad_stl_03/`, `mesh2cad_stl_04/`
- `partsam/`, `partsam_cad_iou_top1000_v1/`
- `p3_parts_cad_results/`, `p3_xpart_open_cases/`, and other `p3_xpart_*` results
- `ours3/`
- `outputs/`
- `mesh2cad/00/`
