# POBJ_11ad3b320ee74185ae4ba26ddc910b52_PART_011 CAD plan v1

STAGE_A_CATEGORY=EXTRUDE_LIKE
LLM_SELECTED_ROUTE=MIXED
RESIDUAL_GEOMETRY_DETECTED=false

- Base primitive: route-specific parametric MIXED construction.
- Main axis: longest bbox axis 1; PCA axis evidence is recorded in geometry_report.json.
- Main profile: inferred from bbox [0.052249256521463394, 0.06567779183387756, 0.020448029041290283] and seven fixed sections per axis.
- Operation sequence: create base, apply version-specific union/cut, validate, export STEP and STL.
- Estimated dimensions: source bbox [0.052249256521463394, 0.06567779183387756, 0.020448029041290283]; normalized CAD max extent 100.
- Boolean cuts: none in initial approximation.
- Boolean unions: base only.
- Fillet/chamfer: omitted unless robust evidence exists; avoids inventing unsupported radii.
- Symmetry assumptions: bbox/PCA symmetry only; mirror evidence is in geometry report.
- Regions likely to be approximated: freeform curvature, small recesses, thin features, and disconnected residual geometry.
- Approximation note: route follows measured primitive evidence.
