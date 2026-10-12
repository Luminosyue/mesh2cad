# V6 Backend Mainline Integration And Vertical Tail Hybrid

- CURRENT_GATE=V6_BACKEND_MAINLINE_INTEGRATION_AND_VERTICAL_TAIL_HYBRID_PASS
- PASS=True
- V6_GEOMETRY_BACKEND_REGISTERED=True
- V6_GEOMETRY_BACKEND_USED_IN_MAINLINE=True
- V6_MAINLINE_FRESH_EXECUTION_COUNT=6
- V6_BACKEND_CANDIDATE_COUNT=6
- V6_BACKEND_FRESH_BREP_COUNT=6
- V6_BACKEND_RELOAD_VALID_COUNT=6
- V6_BACKEND_SAFETY_PASS_COUNT=6
- V6_BACKEND_SELECTED_PART_COUNT=5
- V6_BACKEND_STRICT_GAIN_PART_COUNT=5
- HYBRID_SELECTED_PART_COUNT=1
- V6_BACKEND_REJECTED_COUNT=0
- V6_BACKEND_SOURCE_MESH_READ_COUNT=6
- V6_BACKEND_MESH_READ_PROVENANCE_COMPLETE=True
- CURRENT_BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT=0
- FUSELAGE_SELECTED_SOURCE=V6_GEOMETRY_BACKEND
- FUSELAGE_CURRENT_IOU=0.0006234876759860825
- FUSELAGE_V6_MAINLINE_IOU=0.06398562897764802
- MAIN_WING_LEFT_SELECTED_SOURCE=V6_GEOMETRY_BACKEND
- MAIN_WING_LEFT_CURRENT_IOU=0.013380560554604765
- MAIN_WING_LEFT_V6_MAINLINE_IOU=0.04021007726317875
- MAIN_WING_RIGHT_SELECTED_SOURCE=V6_GEOMETRY_BACKEND
- MAIN_WING_RIGHT_CURRENT_IOU=0.00040376609694477687
- MAIN_WING_RIGHT_V6_MAINLINE_IOU=0.021631098901872172
- TAILPLANE_LEFT_SELECTED_SOURCE=V6_GEOMETRY_BACKEND
- TAILPLANE_RIGHT_SELECTED_SOURCE=V6_GEOMETRY_BACKEND
- VERTICAL_TAIL_PURE_V6_IOU=0.055137741857529315
- VERTICAL_TAIL_CURRENT_IOU=0.06653902209801142
- VERTICAL_TAIL_HYBRID_IMPLEMENTED=True
- VERTICAL_TAIL_HYBRID_IOU=0.05249772396838187
- VERTICAL_TAIL_HYBRID_SHARED_EDGE=1
- VERTICAL_TAIL_HYBRID_PCURVE=8
- VERTICAL_TAIL_HYBRID_TRIMMED_FACE=2
- VERTICAL_TAIL_HYBRID_PASS=True
- VERTICAL_TAIL_HYBRID_BLOCKER=None
- CASE09_FINAL_SELECTION_COMPLETE=True
- CASE09_WHOLE_OBJECT_CURRENT_IOU=0.7844399837275645
- CASE09_WHOLE_OBJECT_V6_INTEGRATED_IOU=0.924518459652742
- CASE09_WHOLE_OBJECT_CURRENT_CHAMFER=0.024431972691224327
- CASE09_WHOLE_OBJECT_V6_INTEGRATED_CHAMFER=0.01094672072098684
- CASE09_WHOLE_OBJECT_FIDELITY_IMPROVED=True
- V6_MAINLINE_HISTORICAL_STEP_REUSE_COUNT=0
- CURRENT_HISTORICAL_STEP_REUSE_COUNT=0
- V7D3_HISTORICAL_FINAL_STEP_REUSE_COUNT=0
- V6_BACKEND_INVALID_SELECTED_COUNT=0
- DIRECT_PLAN_TO_OCC_BYPASS_COUNT=0
- INVALID_CURRENT_BUILDER_EXECUTED_COUNT=0
- GEOMETRY_EXPLOSION_COUNT=0
- V13_RERUN_STARTED=True
- V13_RERUN_PASS=True
- V13_CONSUMED_SELECTED_ARTIFACT_MATCH=True
- V10_REGRESSION_PASS=True
- V11_REGRESSION_PASS=True
- V11B_REGRESSION_PASS=True
- V11C_REGRESSION_PASS=True
- V12_REGRESSION_PASS=True
- V12R_REGRESSION_PASS=True
- V7D3_REGRESSION_PASS=True
- SELECTED_MANIFEST=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/mainline_selected_artifact_manifest.json
- SELECTION_SUMMARY_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/v6_mainline_selection_summary.csv
- HYBRID_AUDIT_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/vertical_tail_hybrid_audit.csv
- SHADED_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/case09_mainline_v6_integration_shaded.png
- TRUE_EDGE_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/case09_mainline_v6_integration_true_edges.png
- WHOLE_OBJECT_COMPARISON=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/case09_current_vs_v6_integrated_whole_object.png
- REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration/artifacts/V6_BACKEND_MAINLINE_INTEGRATION_REPORT.md
- TESTS_PASSED=8
- TESTS_FAILED=0
- BLOCKERS=[]

## Required answers

1. V6GeometryBackend is registered and used as an audited external mainline candidate source.
2. Every mainline V6 candidate is freshly executed.
3. No old or audit V6 STEP enters final selection.
4. Fuselage selection is metric-driven and reported above.
5. Main Wing Right selection is metric-driven and repairs the Current under-fit when V6 wins.
6. Both tailplanes are evaluated independently against fresh Current replays.
7. Vertical Tail hybrid uses fresh V6 BSpline supports plus the existing V7D3 authoritative shared-edge mechanism.
8. Hybrid geometry and topology gates are both required.
9. V6 source-mesh reads are explicit and provenance-tracked.
10. Current BuilderRegistry runtime source-mesh reads remain zero.
11. Whole-object improvement is measured by four-view IoU and Chamfer.
12. V13 runs only after the mainline, hybrid, and whole-object gates pass.
13. V13 verifies each consumed selected SHA256 before XCAF export.
14. CASE09 main geometry can stop only when the final PASS field is true.
