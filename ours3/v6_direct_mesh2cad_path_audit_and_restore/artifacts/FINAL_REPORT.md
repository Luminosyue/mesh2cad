# V6 Direct Mesh2CAD Path Audit And Restore

## Result

- `CURRENT_GATE=MESH2CAD_STYLE_BRANCH_NO_GAIN_AUDIT_PASS`
- `V6_MESH2CAD_STYLE_PATH_FOUND=True`
- `V6_DIRECT_VLM_CADQUERY_PATH_FOUND=False`
- `V6_MESH_GUIDED_FITTING_PATH_FOUND=True`
- `V6_FIDELITY_ADVANTAGE_ROOT_CAUSE=PROFILE_EXTRACTION|ADAPTIVE_SAMPLING|SEAM_ALIGNMENT|CANDIDATE_SELECTION`
- `V6_PATH_REMOVAL_ROOT_CAUSE=MULTIPLE(SAFETY_GATE_MIGRATION,NO_V11_ADAPTER)`
- `REMOVED_AFTER_VERSION=V7_CONTRACT_CLOSED_RUNTIME`
- `REMOVAL_CODE_PATH=v7_contract_closed_runtime + v10 builder eligibility + v11 structured plan`
- `MESH2CAD_STYLE_BRANCH_IMPLEMENTED=True`
- `MESH2CAD_TO_V11_ADAPTER_IMPLEMENTED=True`
- `MESH2CAD_STYLE_NOT_FULL_PAPER_REPRODUCTION=True`
- `DUAL_MODAL_OBJ_USED_COUNT=5`
- `DUAL_MODAL_RENDER_USED_COUNT=5`
- `MESH2CAD_STYLE_QWEN_CALLS=5`
- `MESH2CAD_STYLE_PROGRAM_COUNT=17`
- `MESH2CAD_STYLE_PARSE_VALID_COUNT=17`
- `MESH2CAD_STYLE_GROUNDED_PLAN_COUNT=7`
- `MESH2CAD_STYLE_EXECUTABLE_COUNT=6`
- `MESH2CAD_STYLE_FRESH_BREP_COUNT=6`
- `MESH2CAD_STYLE_SELECTED_COUNT=4`
- `DUAL_MODAL_BASE_VLM_GAIN_PART_COUNT=0`
- `CASE09_V6_WING_SILHOUETTE_MEAN=0.8982976838337675`
- `CASE09_CURRENT_WING_SILHOUETTE_MEAN=0.8133968795433293`
- `CASE09_GEOMETRY_REFINED_WING_SILHOUETTE_MEAN=0.21080207695077313`
- `CASE09_MESH2CAD_STYLE_WING_SILHOUETTE_MEAN=0.8914044617756535`
- `CASE09_V6_WING_SECTION_ERROR=0.004922976142647608`
- `CASE09_CURRENT_WING_SECTION_ERROR=0.034449342334015`
- `CASE09_GEOMETRY_REFINED_WING_SECTION_ERROR=0.004938996597085355`
- `CASE09_MESH2CAD_STYLE_WING_SECTION_ERROR=0.0071842589998163805`
- `CASE09_CURRENT_TRUE_EDGE_COUNT=156`
- `CASE09_MESH2CAD_STYLE_TRUE_EDGE_COUNT=60`
- `MESH2CAD_RAW_PARAMETER_CONSUMED_FINAL_COUNT=0`
- `MESH2CAD_DIRECT_FINAL_OCC_BYPASS_COUNT=0`
- `INVALID_BUILDER_EXECUTED_COUNT=0`
- `BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT=0`
- `HISTORICAL_STEP_REUSE_COUNT=0`
- `GEOMETRY_EXPLOSION_COUNT=0`
- `CASE09_VERTICAL_TAIL_SELECTED_ARTIFACT_MATCH=True`
- `REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore/artifacts/FINAL_REPORT.md`
- `V6_AUDIT_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore/artifacts/V6_SELECTED_CANDIDATE_SOURCE.csv`
- `AB_COMPARISON_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore/artifacts/AB_COMPARISON.csv`
- `CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore/artifacts/CASE09_AB_SHADED.png`
- `TRUE_EDGE_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore/artifacts/CASE09_AB_TRUE_EDGES.png`
- `TESTS_PASSED=0`
- `TESTS_FAILED=0`

## Required answers

1. V6 had a real dual-modal OBJ-token + render path, but not a direct VLM-to-CadQuery geometry path.
2. It input both canonical OBJ text and rendered pixels.
3. The model output an executable wrapper and structured brief/plan; V6 runtime produced OCC/STEP after rereading the mesh.
4. V6 looked better because runtime profile extraction, adaptive sampling, seam alignment, and candidate selection were stronger.
5. V7 removed runtime mesh remeasurement; V10/V11 retained safety but no adapter retained the dual-modal candidate source.
6. Root cause is multiple: safety migration plus missing V11 adapter, not render/OBJ deletion alone.
7. Restored branch strict A/B gain part count: 0.
8. Any gain is attributable to construction-family diversity; geometry values remain measured-spec grounded.
9. Mesh2CAD-style does not bypass V10/V11: NO.
10. Formal main-pipeline inclusion is justified only if the A/B metrics show repeatable gain on at least two critical parts.

## Safety conclusion

Raw CadQuery programs are retained for diagnostics only. Formal candidates are V11 plans with authoritative refs and execute only through BuilderRegistry. Historical V6 STEP files are comparison-only. Builder runtime source-mesh reads remain zero.
