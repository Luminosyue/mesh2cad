# DORA_INPUT_DATA_AUDIT_V1 — data inventory

- frozen V3 cohort: 1000
- fully paired Mesh+Dora+fitted+GT CAD: 800
- paired DeepCAD: 640
- paired Fusion360: 160

Raw Dora is `salient_edges.npz` plus `edge_points.npy`; fitted curves are read-only V1 build artifacts.

Dora-derived `[N,32,7]` inputs exist under `curve_c2/curve_inputs.npy`; no Dora-derived 256-D token is present in this frozen build. GT B-Rep curves are `gt_brep_curves.json`.
