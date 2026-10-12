# Root cause report

## Finding
Both original V1 and current V3 selected 209-part cohorts are independent native CadQuery feature programs. No selected part is a source-triangle wrapper. The original three partial STEP assemblies contain native parts; the current 20 GLB/PLY assembly previews are display meshes derived from those native STEP parts and are not themselves parametric CAD files.

## Three distinct phenomena
1. **BREP_FACET_TOPOLOGY**: one triangle (or a few patches) per source mesh triangle. It would show dense 3-edge planar faces and source-like topology. This was not found in the audited selected cases. The synthetic 320-triangle control demonstrates that the validator detects this while analytic ratio remains 1.0.
2. **Polygonal native feature geometry**: fitted 2D polyline contours are extruded, revolved or lofted. An extrusion of a many-sided contour creates genuine planar side strips. A revolved piecewise linear profile produces real cones/cylinders. These are native parametric features, but they need not be smooth or semantically optimal. Their angular appearance does not disappear merely by refining display tessellation.
3. **RENDER_TESSELLATION and shading**: execute_candidate.py `run` calls `reloaded.tessellate(0.001,0.05)` and writes cad_mesh_from_reloaded_step.ply. V3 assembly renderer `sample` returns `mesh.face_normals[idx]`; `render` shades samples with those constant triangle normals. This can expose display triangles and point-sampling grain on curved B-Rep faces. The new inspection images read original STEP, interpolate OCC surface normals and overlay only genuine B-Rep edges.

## Previous gate
PREVIOUS_NATIVE_CHECK_WAS_INSUFFICIENT = YES, specifically for complete representation evidence. It was NOT merely `.py exists` / STEP reload: execute_candidate.py `validate` already enforced a restrictive AST whitelist, only CadQuery import, approved feature methods, no external paths/payloads and boolean limits; p3_validate.py also checked banned constructors and feature budgets. It lacked direct OCC surface-type and triangular-face auditing and independent source/code/STEP correspondence. This is an evidence/coverage gap, not proof of a previous false acceptance. Its successful prevention of mesh wrappers is consistent with the new audit.

## Action
Adopt the delivered independent representation validator for future admission. No native CAD generator rebuild is justified by these representation results. Improvements to smooth profiles, fitting family choice, detail preservation and assembly completeness remain geometric modeling work; they were not performed in this audit. Existing geometry rejections are unchanged. Never infer high-detail geometric quality from A classification or from a large compression ratio.

Exact original script paths, SHA256 and line references are in `evidence/source_evidence.json`; source snapshots are alongside it. Generator data may legitimately read source meshes to estimate parameters; generated cad.py must and does reconstruct without the mesh.
