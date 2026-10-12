# LLM Mesh-to-CAD Pilot V1

## Source mesh

- case_id: `CADPART_000`
- path: `/data/home/cuiyuehan/project/mesh2cad/ours3/cad_part_recovery_v1/cases/CADPART_000/source_part.obj`
- vertex count: 9390
- face count: 18776
- connected components: 1
- watertight: true
- bbox size: `[0.17775577, 0.16930450, 0.90513044]`
- surface samples per successful comparison: 50000

The source was copied read-only. It was not remeshed, cropped, repaired, or modified. A reversible `x1000` CAD work-scale transform is recorded in `geometry_report.json`; reconstructed tessellation is transformed back by `x0.001` before comparison.

## Geometry interpretation

- primitive hypothesis: elongated revolved body with reduced-radius neck
- symmetry: strong transverse mirror evidence; PCA main-axis variance ratio 0.921488
- recommended modeling route: `REVOLVE`
- main axis: `[0.02050033, -0.00860652, 0.99975280]`
- principal limitations: mildly non-circular transverse section and asymmetric shoulder detail

## CAD program

- operation sequence: profile -> revolve -> axis rotation -> translation -> STEP/STL export
- operation count: 4 principal modeling/placement operations
- main parameters: total length 0.904943, barrel radius 0.08365, neck radius 0.0505, shoulder bounds -0.382/-0.302
- the CAD program never reads or imports the source mesh

## Round 1

- CAD_PARSE: PASS
- CAD_EXECUTION: PASS
- SOLID_VALID: PASS before export
- STEP_EXPORT: PASS
- STEP_RELOAD: FAIL (kernel-tolerance collapse at source-scale millimetre dimensions)
- Chamfer / Normal / IoU / BBox / Volume: not computed because STEP reload is the mandatory gate

## Round 2

- CAD_PARSE: PASS
- CAD_EXECUTION: PASS
- SOLID_VALID: PASS
- STEP_EXPORT: PASS
- STEP_RELOAD: PASS
- TESSELLATION: PASS
- Chamfer-L1: 0.0189135683
- Chamfer-L2: 0.0005009172
- Normal consistency: 0.9284093680
- IoU: 0.4513708343
- BBox relative error: 0.1331250007
- Surface area ratio: 1.1215517891
- Volume ratio: unavailable because the exported evaluation STL was not considered watertight by trimesh

## Round 3

- CAD_PARSE: PASS
- CAD_EXECUTION: FAIL (`BRepBuilderAPI_DisconnectedWire`)
- SOLID_VALID / STEP / STEP_RELOAD / TESSELLATION: FAIL
- geometry metrics: not computed because STEP reload did not pass

## Best result

BEST_VERSION=v2  
CAD_PARSE=PASS  
CAD_EXECUTION=PASS  
STEP_RELOAD=PASS  
CHAMFER_L1=0.0189135683  
NORMAL_CONSISTENCY=0.9284093680  
IOU=0.4513708343  
BBOX_ERROR=0.1331250007  
VOLUME_RATIO=null

V2 wins deterministically: it passes STEP reload and geometry validity, while V1 and V3 are ineligible. Original V1/V2/V3 artifacts are retained.

## Failure analysis

The long axial body and gross radial scale are recovered well enough to give high normal consistency. The reduced-radius neck and major shoulder transition are represented structurally. The reconstruction misses transverse anisotropy and local non-axisymmetric shoulder details; the unconstrained V2 spline also makes the radial envelope too wide, reflected in bbox and area errors. V1 failed because of STEP tolerance at normalized source scale. V3 failed because the attempted locally constrained profile produced a disconnected CAD wire.

## Conclusion

This single-case pilot demonstrates that the closed loop `single-part mesh -> geometry evidence -> LLM-authored parametric CadQuery -> executable CAD -> STEP -> reload -> tessellation -> quantitative comparison` can run end to end. It does not establish superiority over CAD-Recode and does not justify batch execution. The current result is a valid but approximate parametric reconstruction, with the main remaining error in the radial/shoulder profile.

REFINEMENT_STOP_REASON=three-round cap reached; V2 is the only STEP-reload-valid candidate

